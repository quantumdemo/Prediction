"""
Calibration Metrics Module: ECE & MCE

Computes Expected Calibration Error (ECE) and Maximum Calibration Error (MCE)
over probabilistic forecasts (binary or multi-class outcomes).
"""

from typing import List, Union
import numpy as np


def calculate_ece(
    probs: Union[List[float], np.ndarray],
    targets: Union[List[int], np.ndarray],
    n_bins: int = 10,
) -> float:
    """
    Calculates Expected Calibration Error (ECE) over binary predictions.
    probs: predicted probabilities for positive outcome in [0, 1]
    targets: ground-truth binary targets in {0, 1}
    """
    probs = np.array(probs, dtype=float)
    targets = np.array(targets, dtype=int)

    if len(probs) == 0:
        return 0.0

    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    total_samples = len(probs)

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]

        if i == n_bins - 1:
            in_bin = (probs >= bin_lower) & (probs <= bin_upper)
        else:
            in_bin = (probs >= bin_lower) & (probs < bin_upper)

        bin_size = np.sum(in_bin)
        if bin_size > 0:
            bin_acc = np.mean(targets[in_bin])
            bin_conf = np.mean(probs[in_bin])
            ece += (bin_size / total_samples) * abs(bin_acc - bin_conf)

    return float(ece)


def calculate_mce(
    probs: Union[List[float], np.ndarray],
    targets: Union[List[int], np.ndarray],
    n_bins: int = 10,
) -> float:
    """
    Calculates Maximum Calibration Error (MCE) over binary predictions.
    """
    probs = np.array(probs, dtype=float)
    targets = np.array(targets, dtype=int)

    if len(probs) == 0:
        return 0.0

    bin_boundaries = np.linspace(0.0, 1.0, n_bins + 1)
    max_error = 0.0

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]

        if i == n_bins - 1:
            in_bin = (probs >= bin_lower) & (probs <= bin_upper)
        else:
            in_bin = (probs >= bin_lower) & (probs < bin_upper)

        bin_size = np.sum(in_bin)
        if bin_size > 0:
            bin_acc = np.mean(targets[in_bin])
            bin_conf = np.mean(probs[in_bin])
            err = abs(bin_acc - bin_conf)
            if err > max_error:
                max_error = err

    return float(max_error)


def calculate_multiclass_ece(
    probs_matrix: Union[List[List[float]], np.ndarray],
    target_indices: Union[List[int], np.ndarray],
    n_bins: int = 10,
) -> float:
    """
    Calculates multi-class top-label ECE.
    """
    probs_matrix = np.array(probs_matrix, dtype=float)
    target_indices = np.array(target_indices, dtype=int)

    if len(probs_matrix) == 0:
        return 0.0

    confidences = np.max(probs_matrix, axis=1)
    predictions = np.argmax(probs_matrix, axis=1)
    accuracies = (predictions == target_indices).astype(int)

    return calculate_ece(confidences, accuracies, n_bins=n_bins)
