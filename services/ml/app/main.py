import datetime
import logging
import os
import sys
import uuid
from typing import Optional

from fastapi import FastAPI, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure contracts are in path
contracts_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../packages/contracts/python")
)
if contracts_path not in sys.path:
    sys.path.insert(0, contracts_path)

from services.ml.app.config import settings  # noqa: E402
from services.ml.app.db.session import check_database_health  # noqa: E402
from services.ml.app.errors import (  # noqa: E402
    PlatformException,
    platform_exception_handler,
    validation_exception_handler,
)
from services.ml.app.integration.pipeline import EndToEndPredictionPipeline  # noqa: E402
from services.ml.app.integration.schemas import (  # noqa: E402
    EndToEndPredictionResponse,
    PredictionPipelineRequest,
)
from services.ml.app.reporting.repository import PredictionHistoryRepository  # noqa: E402
from services.ml.app.reporting.schemas import PredictionHistoryFilter  # noqa: E402

logger = logging.getLogger("football_ml.api")

app = FastAPI(
    title="Football AI Platform — Python ML Service",
    description="FastAPI operational boundary for forecasting, risk evaluation, and prediction history.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration supporting environment-driven allowed origins
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")] if allowed_origins_env else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers
app.add_exception_handler(PlatformException, platform_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Global catch-all exception handler masking internal stack traces, DB URLs, and SQL queries from clients.
    """
    correlation_id = getattr(request.state, "correlation_id", "N/A")
    logger.error(
        f"Unhandled exception on endpoint {request.url.path}: {exc}",
        extra={"correlation_id": correlation_id, "event_type": "INFRASTRUCTURE_FAILURE"},
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        headers={"x-correlation-id": correlation_id},
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_INFRASTRUCTURE_FAILURE",
                "message": "An internal operational error occurred. The incident has been logged with correlation ID.",
            },
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "correlation_id": correlation_id,
        },
    )


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("x-correlation-id") or f"ml-{uuid.uuid4()}"
    request.state.correlation_id = correlation_id
    response: Response = await call_next(request)
    response.headers["x-correlation-id"] = correlation_id
    return response


@app.get("/health", tags=["System"])
@app.get("/api/v1/health", tags=["System"])
async def health(request: Request):
    correlation_id = getattr(request.state, "correlation_id", "N/A")
    db_status = check_database_health()
    is_db_healthy = db_status.get("status") == "HEALTHY"

    return {
        "success": True,
        "data": {
            "status": "HEALTHY" if is_db_healthy else "DEGRADED",
            "service": settings.service_name,
            "environment": settings.environment,
            "version": "0.1.0",
            "database": db_status.get("status", "UNKNOWN"),
        },
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "correlation_id": correlation_id,
    }


@app.get("/readiness", tags=["System"])
@app.get("/api/v1/readiness", tags=["System"])
async def readiness(request: Request):
    correlation_id = getattr(request.state, "correlation_id", "N/A")
    db_status = check_database_health()
    is_ready = db_status.get("status") == "HEALTHY"

    return JSONResponse(
        status_code=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        headers={"x-correlation-id": correlation_id},
        content={
            "success": is_ready,
            "data": {
                "status": "READY" if is_ready else "NOT_READY",
                "service": settings.service_name,
                "checks": {
                    "environment": "OK",
                    "database": db_status.get("status", "UNHEALTHY"),
                },
            },
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "correlation_id": correlation_id,
        },
    )


@app.post("/api/v1/predict", tags=["Prediction"])
async def predict_match(request: Request, payload: PredictionPipelineRequest):
    """
    Executes the 9-stage prediction pipeline over current fixture research facts and base features.
    Outputs an immutable, auditable prediction report and persists it to the prediction history repository.
    """
    correlation_id = getattr(request.state, "correlation_id", "N/A")
    logger.info(
        f"Received prediction request for fixture {payload.fixture_id} ({payload.home_team} vs {payload.away_team})",
        extra={"correlation_id": correlation_id, "event_type": "PREDICTION_PIPELINE_START"},
    )

    pipeline = EndToEndPredictionPipeline()
    response_data: EndToEndPredictionResponse = pipeline.execute_prediction_pipeline(payload)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        headers={"x-correlation-id": correlation_id},
        content=response_data.model_dump(),
    )


@app.get("/api/v1/history", tags=["Prediction"])
async def get_prediction_history(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    decision_status: Optional[str] = Query(default=None, alias="status"),
    fixture_id: Optional[str] = Query(default=None),
):
    """
    Retrieves auditable historical prediction reports matching multi-criteria filters.
    """
    correlation_id = getattr(request.state, "correlation_id", "N/A")
    logger.info(
        f"Querying prediction history (limit={limit}, offset={offset}, status={decision_status}, fixture_id={fixture_id})",
        extra={"correlation_id": correlation_id, "event_type": "PREDICTION_HISTORY_QUERY"},
    )

    query_filter = PredictionHistoryFilter(
        limit=limit,
        offset=offset,
        status=decision_status,
        fixture_id=fixture_id,
    )

    repository = PredictionHistoryRepository()
    reports = repository.query_history(query_filter)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        headers={"x-correlation-id": correlation_id},
        content=[report.model_dump() for report in reports],
    )
