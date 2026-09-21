# Football AI Intelligence Platform — File Structure

This document provides a comprehensive mapping of the repository layout, directories, key source files, contracts, and deployment artifacts across the monorepo architecture.

```
football-ai-platform/
├── .env.example                               # Environment variable template with secret placeholders
├── .gitignore                                  # Git exclusion patterns
├── README.md                                   # Root project documentation
├── package.json                                # Monorepo root npm workspace manifest
├── package-lock.json                           # Locked npm dependency tree
├── pyproject.toml                              # Root Python tool configuration
├── requirements.txt                            # Root Python service requirements
├── vercel.json                                 # Vercel deployment configuration & URL rewrites
├── file-structure.md                           # Master repository directory & file manifest
├── stage26handoff.md                           # Stage 26 handoff summary report
│
├── api/                                        # Vercel Serverless Function Entry Points
│   └── index.py                                # Vercel Python entry point importing FastAPI app
│
├── apps/                                       # Frontend Applications
│   └── web/                                    # Next.js 15 App Router Frontend Console
│       ├── src/
│       │   ├── app/
│       │   │   ├── layout.tsx                  # Global navigation header & footer shell
│       │   │   ├── page.tsx                    # Private Beta Operational Dashboard
│       │   │   ├── predict/page.tsx            # Match Prediction Generator & Auto-Inference UI
│       │   │   ├── history/page.tsx            # Auditable Prediction History Viewer
│       │   │   └── status/page.tsx             # Real-time System Health & Telemetry Monitor
│       │   └── lib/                            # Frontend utility functions
│       ├── next.config.mjs                     # Next.js configuration
│       ├── tsconfig.json                       # TypeScript compiler settings
│       └── package.json                        # Frontend web package manifest
│
├── packages/                                   # Shared Monorepo Packages
│   └── contracts/                              # Shared Type Contracts & Schemas
│       ├── src/                                # TypeScript type definitions (enums, predictions)
│       ├── python/                             # Python Pydantic contract bindings
│       └── package.json                        # Contracts package manifest
│
├── services/                                   # Backend Microservices & ML Pipelines
│   └── ml/                                     # FastAPI Service & ML Intelligence Boundary
│       ├── app/
│       │   ├── main.py                         # FastAPI application entry point & CORS configuration
│       │   ├── config.py                       # Pydantic Settings configuration loader
│       │   ├── errors.py                       # Exception handling & 500 error masking
│       │   ├── logging_config.py               # Structured JSON log formatter & secret redaction
│       │   ├── backtesting/                    # Stage 12 time-aware walk-forward backtest engine
│       │   ├── calibration/                    # Stage 13 probability calibration (Platt/Isotonic)
│       │   ├── db/                             # Database models, SQLAlchemy sessions & pooling
│       │   │   ├── models.py                   # SQLAlchemy ORM models (prediction_reports, etc.)
│       │   │   └── session.py                  # Database connection pooling & transaction manager
│       │   ├── evidence/                       # Stage 15 research evidence validator & SSRF checks
│       │   ├── features/                       # Stage 9 feature registry & calculation engine
│       │   ├── integration/                    # Stage 20 end-to-end prediction pipeline orchestrator
│       │   │   ├── pipeline.py                 # 9-step EndToEndPredictionPipeline implementation
│       │   │   └── schemas.py                  # Pipeline request/response Pydantic schemas
│       │   ├── markets/                        # Stage 17 controlled market mapper (8 supported markets)
│       │   ├── models/                         # ML models (Logistic Regression, RandomForest, XGBoost)
│       │   ├── pipeline/                       # Stage 16 current match feature update & forecaster
│       │   ├── reporting/                      # Stage 19 auditable report generator & repository
│       │   ├── research/                       # Stage 14 web research fact collection & verification
│       │   ├── risk/                           # Stage 18 risk engine & NO-BET decision boundary
│       │   ├── selection/                      # Stage 13 production forecaster selector (xgboost_platt)
│       │   └── validation/                     # Stage 22 historical shadow testing & validation
│       ├── tests/                              # Unit & integration test suites
│       │   ├── test_main.py                    # Test suite for FastAPI endpoints (/health, /predict, /history)
│       │   ├── test_migration_execution.py     # Alembic DATABASE_URL override tests
│       │   ├── test_stage24_security_observability.py # SSRF & secret redaction tests
│       │   ├── test_stage25_beta_integration.py# End-to-end beta pipeline tests
│       │   └── test_vercel_entrypoint.py       # Vercel api/index.py entry point tests
│       └── pyproject.toml                      # ML service Python dependencies & build config
│
├── infrastructure/                             # Relational Storage & Database Migrations
│   └── database/
│       ├── alembic.ini                         # Alembic database migration configuration
│       ├── schema.sql                          # Raw PostgreSQL SQL DDL definition
│       └── migrations/
│           ├── env.py                          # Alembic migration environment runner (DATABASE_URL override)
│           └── versions/
│               ├── 001_stage4_core_football_schema.py
│               ├── 002_stage20_prediction_history_schema.py
│               └── 003_stage23_production_indexes.py
│
├── docs/                                       # Platform Documentation & Engineering Artifacts
│   ├── DEPLOYMENT_GUIDE.md                     # Step-by-step human deployment manual (35 topics)
│   ├── FRONTEND_VERIFICATION.md                # Page-by-page visual & functional audit report
│   ├── PRODUCTION_TROUBLESHOOTING.md           # Incident response guide for 16 failure scenarios
│   ├── STAGE26_PUBLIC_LAUNCH_CONTINUOUS_MONITORING.md # Primary Stage 26 public launch report
│   ├── STAGE26_API_WIRING_CORRECTION.md        # API route mounting correction report
│   ├── VERCEL_FASTAPI_DEPLOYMENT.md            # Vercel serverless FastAPI deployment guide
│   └── screenshots/stage26/                    # Playwright visual verification screenshot artifacts
│       ├── dashboard.png
│       ├── prediction.png
│       ├── history.png
│       └── status.png
```
