import datetime
import os
import sys
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

# Ensure contracts are in path
contracts_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../packages/contracts/python")
)
if contracts_path not in sys.path:
    sys.path.insert(0, contracts_path)

from services.ml.app.config import settings  # noqa: E402
from services.ml.app.errors import (  # noqa: E402
    PlatformException,
    platform_exception_handler,
    validation_exception_handler,
)

app = FastAPI(
    title="Football AI Platform — Python ML Service",
    description="FastAPI service boundary for feature engineering, forecasting, calibration.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(PlatformException, platform_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)


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
    return {
        "success": True,
        "data": {
            "status": "HEALTHY",
            "service": settings.service_name,
            "environment": settings.environment,
            "version": "0.1.0",
        },
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "correlation_id": correlation_id,
    }


@app.get("/readiness", tags=["System"])
@app.get("/api/v1/readiness", tags=["System"])
async def readiness(request: Request):
    correlation_id = getattr(request.state, "correlation_id", "N/A")
    return {
        "success": True,
        "data": {
            "status": "READY",
            "service": settings.service_name,
            "checks": {
                "environment": "OK",
                "database_boundary": "OK",
            },
        },
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "correlation_id": correlation_id,
    }
