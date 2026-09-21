# Football AI Intelligence & Machine-Learning Platform

[![Stage 26: Public Launch & Deployment](https://img.shields.io/badge/Stage-26%20Complete-green)](#development-stages)
[![Live Vercel Production](https://img.shields.io/badge/Live-https%3A%2F%2Fprediction--web--zeta.vercel.app%2F-blue)](https://prediction-web-zeta.vercel.app/)

A production-quality Football AI Intelligence & Machine-Learning Platform built for real-world football match data ingestion, validation, feature engineering, statistical/ML forecasting, risk evaluation, probability calibration, and auditable prediction reporting.

---

## 📌 Project Overview

This platform is **NOT** a gambling or sportsbook website. It is an end-to-end data engineering, statistical modeling, machine learning forecasting, research, and risk audit system.

The core objective is to calculate scientifically sound football event probabilities using verified data, reproducible feature pipelines, time-aware backtesting, probability calibration, and rigorous abstention logic (`NO BET / INSUFFICIENT EVIDENCE`).

---

## 🏗 System Architecture

```
                                +---------------------------+
                                |  Real Football Data       |
                                |  (Public APIs / Historical)|
                                +-------------+-------------+
                                              |
                                              v
+------------------------+      +-------------+-------------+      +------------------------+
|  Current Match         |      | Data Cleaning,            |      | Football Entity        |
|  Web Research Engine   | ---> | Validation & Provenance   | <--- | System & Canonical IDs |
+------------------------+      +-------------+-------------+      +------------------------+
                                              |
                                              v
                                +-------------+-------------+
                                | Feature Engineering Engine|
                                | (No Future Data Leakage)  |
                                +-------------+-------------+
                                              |
                                              v
                                +-------------+-------------+
                                | Statistical & ML          |
                                | Forecasting Engine        |
                                +-------------+-------------+
                                              |
                                              v
                                +-------------+-------------+
                                | Probability Calibration   |
                                | & Market Mapping          |
                                +-------------+-------------+
                                              |
                                              v
                                +-------------+-------------+
                                | Risk, Confidence &        |
                                | NO-BET Engine             |
                                +-------------+-------------+
                                              |
                                              v
                                +-------------+-------------+
                                | Auditable Reporting       |
                                | & Prediction History      |
                                +---------------------------+
```

---

## 📜 Core Directives & Principles

1. **Real Data Only**: No fake football values, fabricated xG, synthetic match results, or fake probabilities in production.
2. **First-Class Abstention**: `NO BET / INSUFFICIENT EVIDENCE` is a primary system output whenever data or model confidence is inadequate.
3. **Time-Aware Validation**: Strictly chronological training/testing splits with 0 future-data leakage.
4. **Full Provenance & Auditability**: Every prediction logs feature versions, model versions, source URLs, timestamps, and confidence scores.

---

## 🚀 Development Stages

- [x] **STAGE 1 — Master Specification & Engineering Constitution**
- [x] **STAGE 2 — Architecture & Technology Research**
- [x] **STAGE 3 — Repository, Application Skeleton & Vercel Foundation**
- [x] **STAGE 4 — Database Schema & Data Contracts**
- [x] **STAGE 5 — Football Data Source Research & Acquisition Strategy**
- [x] **STAGE 6 — Historical Dataset Acquisition & Ingestion**
- [x] **STAGE 7 — Data Cleaning, Normalization & Validation**
- [x] **STAGE 8 — Football Entity & Fixture Identification**
- [x] **STAGE 9 — Feature Engineering Engine**
- [x] **STAGE 10 — Statistical Baseline Forecasting**
- [x] **STAGE 11 — Machine-Learning Forecasting**
- [x] **STAGE 12 — Time-Aware Historical Backtesting**
- [x] **STAGE 13 — Probability Calibration & Model Selection**
- [x] **STAGE 14 — Current-Match Web Research Engine**
- [x] **STAGE 15 — Evidence, Provenance & Current-Data Validation**
- [x] **STAGE 16 — Current Feature Update & Forecast Pipeline**
- [x] **STAGE 17 — Market Catalogue & Market Mapping**
- [x] **STAGE 18 — Risk, Confidence & NO-BET Engine**
- [x] **STAGE 19 — Auditable Reporting & Prediction History**
- [x] **STAGE 20 — Complete Prediction Pipeline Integration**
- [x] **STAGE 21 — Full System Audit**
- [x] **STAGE 22 — Historical Validation & Shadow Testing**
- [x] **STAGE 23 — Production Infrastructure & Database Hardening**
- [x] **STAGE 24 — Security, Monitoring, Logging & Failure Handling**
- [x] **STAGE 25 — Private Beta & Controlled Live Testing**
- [x] **STAGE 26 — Public Launch & Continuous Monitoring**

---

## 💻 Local Development & Verification

### Install Dependencies

```bash
npm install
pip install -r requirements.txt
```

### Run Historical Data Acquisition

```bash
python3 scripts/ingest_historical_data.py
```

### Run Verification Tests & Linter

```bash
npm run build --workspace=packages/contracts
npm test
ruff check .
```

### Build Web Application

```bash
npm run build --workspace=apps/web
```

For detailed setup instructions, refer to [`docs/LOCAL_DEVELOPMENT.md`](docs/LOCAL_DEVELOPMENT.md), [`docs/DATA_ACQUISITION_RUNBOOK.md`](docs/DATA_ACQUISITION_RUNBOOK.md), and [`docs/DATA_QUALITY_REPORT.md`](docs/DATA_QUALITY_REPORT.md).
