import datetime
import os
import sys

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Add python contracts path
contracts_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../packages/contracts/python")
)
if contracts_path not in sys.path:
    sys.path.insert(0, contracts_path)

from football_contracts import ErrorCode  # noqa: E402


class PlatformException(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 400,
        details: list = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []


async def platform_exception_handler(request: Request, exc: PlatformException) -> JSONResponse:
    correlation_id = request.headers.get("x-correlation-id", "N/A")
    return JSONResponse(
        status_code=exc.status_code,
        headers={"x-correlation-id": correlation_id},
        content={
            "success": False,
            "error": {
                "code": exc.code.value,
                "message": exc.message,
                "details": exc.details,
            },
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "correlation_id": correlation_id,
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    correlation_id = request.headers.get("x-correlation-id", "N/A")
    details = []
    for err in exc.errors():
        details.append(
            {
                "field": ".".join([str(loc) for loc in err.get("loc", [])]),
                "message": err.get("msg", ""),
                "location": err.get("type", ""),
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        headers={"x-correlation-id": correlation_id},
        content={
            "success": False,
            "error": {
                "code": ErrorCode.VALIDATION_ERROR.value,
                "message": "Request payload validation failed",
                "details": details,
            },
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "correlation_id": correlation_id,
        },
    )
