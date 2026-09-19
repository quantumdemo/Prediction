"""
Stage 13 Probability Calibration & Model Selection Runner Script

Runs Platt Scaling and Isotonic Regression calibrators across all Stage 10 & Stage 11 candidates,
evaluates out-of-sample calibration metrics (Log Loss, Brier Score, ECE, MCE), selects the optimal
production forecaster, and exports STAGE13_CALIBRATION_ARTIFACT_v1.0.0.
"""

import os
import sys
import time
import json
from services.ml.app.selection.selector import ModelSelector

def main():
    print("=========================================================================", flush=True)
    print("STAGE 13: PROBABILITY CALIBRATION & PRODUCTION MODEL SELECTION", flush=True)
    print("=========================================================================", flush=True)

    t0 = time.time()
    selector = ModelSelector(artifacts_dir="/tmp/stage12_artifacts")
    artifact_payload = selector.run_calibration_and_selection(output_dir="/tmp/stage13_artifacts")
    duration = time.time() - t0

    report = artifact_payload["report"]

    print(f"\nExecution completed in {duration:.2f} seconds!", flush=True)
    print(f"Canonical artifact exported to: /tmp/stage13_artifacts/stage13_calibration_report.json", flush=True)

    selected = report["selected_production_model"]
    print("\n=========================================================================", flush=True)
    print("SELECTED PRODUCTION FORECASTER", flush=True)
    print("=========================================================================", flush=True)
    print(f"Candidate ID:        {selected['candidate_id']}")
    print(f"Model Key:           {selected['model_key']}")
    print(f"Calibration Method:  {selected['calibration_method']}")
    print(f"1X2 Log Loss:        {selected['1x2_log_loss']:.5f}")
    print(f"1X2 Brier Score:     {selected['1x2_brier_score']:.5f}")
    print(f"1X2 RPS:             {selected['1x2_rps']:.5f}")
    print(f"1X2 ECE:             {selected['1x2_ece']:.5f}")
    print(f"Selection Criteria:  {selected['selection_criteria']}")

    print("\n==========================================================================================", flush=True)
    print("CANDIDATE RANKINGS (OUT-OF-SAMPLE HOLDOUT EVALUATION)", flush=True)
    print("==========================================================================================", flush=True)
    print(f"{'Rank':<4} | {'Candidate ID':<25} | {'Calibration Method':<20} | {'1X2 LogLoss':<11} | {'1X2 ECE':<8} | {'1X2 Brier':<10}")
    print("-" * 90)
    for idx, c in enumerate(report["candidate_rankings"], 1):
        print(f"{idx:<4} | {c['candidate_id']:<25} | {c['calibration_method']:<20} | {c['1x2_log_loss']:<11.5f} | {c['1x2_ece']:<8.5f} | {c['1x2_brier_score']:<10.5f}")

if __name__ == "__main__":
    main()
