# MACHINE LEARNING ARCHITECTURE & MODEL GOVERNANCE
## FOOTBALL AI INTELLIGENCE & MACHINE-LEARNING PLATFORM

### 1. FORECASTING MODEL HIERARCHY

The platform uses a two-tiered model hierarchy to generate raw match probabilities:

```
                          ┌───────────────────────────┐
                          │   Engineered Features     │
                          │   (Cutoff: t < Kickoff)   │
                          └─────────────┬─────────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    ▼                                       ▼
    ┌───────────────────────────────┐       ┌───────────────────────────────┐
    │ Tier 1: Statistical Baseline  │       │   Tier 2: ML Ensemble         │
    │  - Bivariate Poisson          │       │  - XGBoost Classifier         │
    │  - Dixon-Coles Low-Score Mod  │       │  - LightGBM Classifier        │
    └───────────────┬───────────────┘       └───────────────┬───────────────┘
                    │                                       │
                    └───────────────────┬───────────────────┘
                                        ▼
                            [Raw Probability Vectors]
                                        │
                                        ▼
                            [Probability Calibration]
                             (Isotonic / Platt)
                                        │
                                        ▼
                            [Calibrated Probabilities]
```

---

### 2. STRICT ZERO FUTURE-DATA LEAKAGE GUARANTEE

#### 2.1 Cutoff Enforcement Mechanism
For match $M_k$ occurring at kickoff timestamp $T_k$, all feature engineering queries MUST enforce a strict temporal filter:
$$\text{event\_timestamp} \le T_k - \Delta_{\text{lead\_time}}$$

#### 2.2 Ingestion & Leakage Checks
- Post-kickoff statistics (final score, yellow cards, late lineup changes announced post-kickoff) are IMPOSSIBLE to query during feature calculation.
- Automated data leakage unit tests verify that attempting to compute features for historical matches with future data injected throws an explicit `DataLeakageException`.

---

### 3. PROBABILITY CALIBRATION & EVALUATION

#### 3.1 Calibration Methods
- **Platt Scaling (Logistic Calibration)**: Applied to parametric statistical models (Poisson/Dixon-Coles) on small validation samples.
- **Isotonic Regression**: Non-parametric calibration applied to gradient boosted decision trees (XGBoost/LightGBM) when validation sample size $N \ge 1000$.

#### 3.2 Model Evaluation Metrics
All models are evaluated chronologically using:
1. **Log Loss (Cross-Entropy Loss)**: Measures probability accuracy with heavy penalties for overconfident errors.
2. **Brier Score**: Mean squared difference between predicted probability and binary outcome.
3. **Expected Calibration Error (ECE)**: Bin-weighted absolute difference between predicted probability and empirical accuracy.

---

### 4. MODEL REGISTRY & AUDITABILITY

Every trained model artifact stored in the Registry includes:
- `model_id`: Immutable UUID.
- `algorithm_name`: E.g., `dixon_coles`, `xgboost_classifier`.
- `dataset_version_id`: FK to exact training dataset split.
- `feature_version_id`: FK to feature schema definition.
- `hyperparameters`: Immutable JSON blob of training hyperparameters.
- `calibration_version_id`: FK to calibrated scalar parameters.
- `evaluation_metrics`: Log Loss, Brier Score, and ECE logged on out-of-time test set.
