# Repository Structure & Component Boundaries

## Overview

The Football AI Intelligence & Machine-Learning Platform is organized as a monorepo establishing clean physical and logical boundaries between the Next.js web application, the Python FastAPI ML service, shared data contracts, and infrastructure/deployment configurations.

## Folder Hierarchy

```
/
├── apps/
│   └── web/                   # Next.js App Router (TypeScript) Web App & API Gateway
│       ├── src/
│       │   ├── app/           # App Router pages and API routes (/api/v1/health, /api/v1/readiness)
│       │   └── lib/           # Environment validation, structured logging, API helpers
│       ├── next.config.mjs    # Next.js configuration and security headers
│       └── tsconfig.json      # Strict TypeScript configuration
├── services/
│   └── ml/                    # FastAPI (Python 3.12) ML & Feature Service Boundary
│       ├── app/
│       │   ├── main.py        # FastAPI app entry point & CORS
│       │   ├── config.py      # Pydantic BaseSettings configuration
│       │   ├── logging_config.py # JSON structured logging with correlation ID tracking
│       │   ├── errors.py      # Platform exception handlers and error codes
│       │   ├── data/          # Data ingestion boundary (Stub)
│       │   ├── features/      # Feature engineering boundary (Stub)
│       │   ├── models/        # Forecasting model boundary (Stub)
│       │   ├── evaluation/    # Evaluation & calibration boundary (Stub)
│       │   └── jobs/          # Background worker tasks boundary (Stub)
│       └── tests/             # Unit and integration tests for Python ML service
├── packages/
│   └── contracts/             # Shared Contracts & Type Definitions
│       ├── src/               # TypeScript schemas and enums
│       └── python/            # Python Pydantic models (football_contracts)
├── infrastructure/            # Deployment & Infrastructure Configuration Boundaries
│   ├── database/              # PostgreSQL connection boundary and health checks
│   ├── jobs/                  # Modal.com / QStash background worker boundary
│   └── README.md              # Infrastructure responsibilities documentation
├── docs/                      # Master Specifications, Architecture Docs, and Guides
├── tests/                     # Architecture Guard & Specification Compliance Tests
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI/CD Pipeline
├── .env.example               # Safe environment variable placeholders
├── vercel.json                # Vercel deployment configuration
├── package.json               # Monorepo root npm workspaces config
└── pyproject.toml             # Python root dependencies and tool configs (Ruff/pytest/mypy)
```

## Architectural Rationale

1. **`apps/web`**: Uses Next.js (TypeScript) for optimal web frontend performance, server-rendered analytics pages, and serverless edge API routing deployed to Vercel.
2. **`services/ml`**: Uses FastAPI (Python) for native integration with Python ML packages (`pandas`, `scikit-learn`, `XGBoost`). Runs on async Python worker infrastructure (Modal.com) to bypass serverless HTTP timeouts.
3. **`packages/contracts`**: Centralized, typed contracts (TypeScript & Python Pydantic) ensuring strict contract alignment between web gateway and ML services.
4. **`infrastructure`**: Clear boundary separating Vercel frontend hosting from PostgreSQL database storage and Modal.com async workers.
