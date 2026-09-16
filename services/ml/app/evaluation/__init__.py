"""
Evaluation & Calibration Boundary Placeholder
Stage 3 Architecture: Interfaces defined. Probability calibration strictly NOT IMPLEMENTED.
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


def calibrate_probabilities(*args, **kwargs):
    raise PlatformException(
        code=ErrorCode.NOT_IMPLEMENTED,
        message="Probability calibration engine is not implemented in Stage 3.",
        status_code=501,
    )
