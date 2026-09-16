"""
Data Processing & Ingestion Boundary Placeholder
Stage 3 Architecture: Interfaces defined. Ingestion logic strictly NOT IMPLEMENTED.
"""

import os
import sys

from services.ml.app.errors import PlatformException

contracts_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../../packages/contracts/python")
)
if contracts_path not in sys.path:
    sys.path.insert(0, contracts_path)

from football_contracts import ErrorCode  # noqa: E402


def process_raw_match_data(*args, **kwargs):
    raise PlatformException(
        code=ErrorCode.NOT_IMPLEMENTED,
        message="Production match data processing is not implemented in Stage 3.",
        status_code=501,
    )
