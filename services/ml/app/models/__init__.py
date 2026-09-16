"""
Forecasting Models & Inference Engine Boundary Placeholder
Stage 3 Architecture: Interfaces defined. Model training/inference strictly NOT IMPLEMENTED.
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


def run_model_inference(*args, **kwargs):
    raise PlatformException(
        code=ErrorCode.NOT_IMPLEMENTED,
        message="Model training and inference engines are not implemented in Stage 3.",
        status_code=501,
    )
