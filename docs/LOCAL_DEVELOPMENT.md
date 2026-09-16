# Local Development Guide

## Prerequisites

- **Node.js**: v22.0.0 or higher
- **npm**: v11.0.0 or higher
- **Python**: v3.11 or v3.12
- **Git**

## 1. Environment Setup

Clone the repository and copy the example environment file:

```bash
cp .env.example .env
```

Review `.env` to configure optional local database or service variables.

## 2. Installation

### Install Node.js Dependencies

```bash
npm install
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## 3. Running Services Locally

### Build Shared Contracts Package

```bash
npm run build --workspace=packages/contracts
```

### Start Next.js Web Application

```bash
npm run dev --workspace=apps/web
```

The web application will be accessible at [http://localhost:3000](http://localhost:3000).

- Health endpoint: `http://localhost:3000/api/v1/health`
- Readiness endpoint: `http://localhost:3000/api/v1/readiness`

### Start FastAPI Python ML Service

```bash
uvicorn services.ml.app.main:app --reload --port 8000
```

The FastAPI service will be accessible at [http://localhost:8000](http://localhost:8000).

- Interactive API Docs: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/health`
- Readiness endpoint: `http://localhost:8000/readiness`

## 4. Running Tests & Quality Checks

### Run All Tests

```bash
npm test
```

Or run Python tests directly:

```bash
PYTHONPATH=. python3 -m unittest discover -s tests
PYTHONPATH=. python3 -m unittest discover -s services/ml/tests
```

### Run Python Linting (Ruff)

```bash
ruff check .
```

### Run Next.js Type Check & Build Validation

```bash
npm run build --workspace=apps/web
```
