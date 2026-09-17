# Stage 6A Data Leakage Audit & Control Matrix

## Overview

Data leakage occurs when information from the match itself, or from future matches after kickoff, is incorporated into feature variables used for prediction. Under **Engineering Constitution Article III** and the **Master Control Specification**, strict temporal isolation must be maintained.

This document classifies every derived, rated, and engineered feature in the candidate dataset (`Matches.csv`).

---

## 1. Feature Isolation & Classification Matrix

| Feature Name | Column Type | Temporal Source | Leakage Risk Level | Production Classification | Approved Action / Mandatory Control |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `HomeElo` | Pre-match Rating | Sourced Snapshot | SAFE_PRE_MATCH | **APPROVED_REFERENCE_FIELD** | Import as reference value. |
| `AwayElo` | Pre-match Rating | Sourced Snapshot | SAFE_PRE_MATCH | **APPROVED_REFERENCE_FIELD** | Import as reference value. |
| `HomeElo_Diff` | Differential | Sourced Arithmetic | SAFE_PRE_MATCH | **REQUIRES_RECALCULATION** | Recalculate as `HomeElo - AwayElo` in Stage 9. |
| `Form3Home` | Rolling Form | Past Matches | SAFE_PRE_MATCH | **REQUIRES_RECALCULATION** | **DO NOT IMPORT**. Recompute deterministically from raw historical results in Stage 9. |
| `Form5Home` | Rolling Form | Past Matches | SAFE_PRE_MATCH | **REQUIRES_RECALCULATION** | **DO NOT IMPORT**. Recompute deterministically from raw historical results in Stage 9. |
| `Form3Away` | Rolling Form | Past Matches | SAFE_PRE_MATCH | **REQUIRES_RECALCULATION** | **DO NOT IMPORT**. Recompute deterministically from raw historical results in Stage 9. |
| `Form5Away` | Rolling Form | Past Matches | SAFE_PRE_MATCH | **REQUIRES_RECALCULATION** | **DO NOT IMPORT**. Recompute deterministically from raw historical results in Stage 9. |
| `Form3_Diff` | Form Differential | Past Matches | SAFE_PRE_MATCH | **REQUIRES_RECALCULATION** | Recompute in Stage 9. |
| `Form5_Diff` | Form Differential | Past Matches | SAFE_PRE_MATCH | **REQUIRES_RECALCULATION** | Recompute in Stage 9. |
| `HomeRating` | Composite Strength | Author Model | UNKNOWN_METHODOLOGY | **REQUIRES_RECALCULATION** | **REJECT**. Author proprietary formula unknown. |
| `AwayRating` | Composite Strength | Author Model | UNKNOWN_METHODOLOGY | **REQUIRES_RECALCULATION** | **REJECT**. Author proprietary formula unknown. |
| `ClusterLabel` | Clustering | Full Dataset | CONFIRMED_LEAKAGE | **REJECTED_LEAKAGE** | **STRICTLY REJECT**. Dataset-wide K-Means clustering incorporates post-kickoff future distribution knowledge. |
| `ClusterProb` | Clustering | Full Dataset | CONFIRMED_LEAKAGE | **REJECTED_LEAKAGE** | **STRICTLY REJECT**. Contains dataset-wide cluster membership probabilities. |
| `ExpectedGoalsHome` | Linear Estimate | Odds & Shots | POTENTIAL_LEAKAGE | **REJECTED_UNVERIFIED** | **REJECT**. Synthetic linear estimate incorporating odds. |
| `ExpectedGoalsAway` | Linear Estimate | Odds & Shots | POTENTIAL_LEAKAGE | **REJECTED_UNVERIFIED** | **REJECT**. Synthetic linear estimate incorporating odds. |
| `ShotAccuracyHome` | Post-match Stat | Same Match | POTENTIAL_LEAKAGE | **REQUIRES_RECALCULATION** | Compute post-match in Stage 9 if needed for evaluation. |
| `DefensivePressureHome` | Post-match Stat | Same Match | POTENTIAL_LEAKAGE | **REQUIRES_RECALCULATION** | Compute post-match in Stage 9 if needed for evaluation. |

---

## 2. Leakage Isolation Protocol

1. **Rejection of Pre-calculated Feature Columns**:
   * Pre-calculated form, momentum, rating, and cluster columns (`Form3Home`, `Form5Home`, `ClusterLabel`, `HomeRating`) will **NOT** be populated into production feature tables during ingestion.
2. **Deterministic Stage 9 Feature Pipeline**:
   * In Stage 9, rolling form and team strength features will be constructed chronologically using strictly past match records where `match_date < current_match_date`.
3. **Auditing Verification**:
   * Automated unit tests in `tests/test_stage6a_dataset_audit.py` enforce that no `CONFIRMED_LEAKAGE` or `REJECTED_LEAKAGE` columns can be mapped into ML training pipelines.
