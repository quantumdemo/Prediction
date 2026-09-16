# TECHNOLOGY RESEARCH & EVALUATION
## FOOTBALL AI INTELLIGENCE & MACHINE-LEARNING PLATFORM

### 1. FRONTEND TECHNOLOGY EVALUATION

| Technology | Status | Advantages | Disadvantages | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Next.js (TypeScript)** | **SELECTED** | Native React App Router, Server-Side Rendering (SSR) for SEO, seamless Vercel integration, strong TypeScript typing. | Vercel serverless function execution limits. | **CHOSEN** |
| **React SPA (Vite)** | Rejected | Fast local dev, simple deployment. | Client-side bundle heavy, poor SEO for match analysis pages. | Rejected |
| **SvelteKit** | Rejected | Lightweight, excellent performance. | Smaller ecosystem for complex data visualization libraries. | Rejected |

---

### 2. BACKEND & API EVALUATION

| Technology | Status | Advantages | Disadvantages | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **FastAPI (Python 3.11+)** | **SELECTED** | Native Python ML ecosystem integration (scikit-learn, XGBoost), Pydantic data validation, async support, auto OpenAPI docs. | Requires separate hosting container for heavy jobs. | **CHOSEN (ML/Core API)** |
| **Next.js API Routes** | **SELECTED** | Zero latency for frontend requests, easy Vercel deployment. | Unsuitable for long-running ML or pandas tasks (>10s limit). | **CHOSEN (Gateway)** |
| **Node.js Express** | Rejected | Fast I/O. | Requires JS re-implementations of ML feature extractors or IPC overhead. | Rejected |

---

### 3. DATABASE EVALUATION

| Database Option | Status | Advantages | Disadvantages | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Managed PostgreSQL (Supabase / RDS)** | **SELECTED** | Strict relational schema, ACID compliance, native JSONB support, PgBouncer pooling, Python `psycopg3` compatibility. | Requires migration management. | **CHOSEN** |
| **MongoDB / NoSQL** | Rejected | Flexible document storage. | Lacks relational integrity for Club -> Match -> Player entities; risk of inconsistent stats. | Rejected |
| **SQLite** | Rejected | Simple file-based DB. | Poor concurrent write performance for background jobs and web APIs. | Rejected |

---

### 4. MACHINE LEARNING STACK EVALUATION

| Library / Tool | Category | Justification |
| :--- | :--- | :--- |
| **statsmodels** | Baseline Statistical Model | Implementation of Poisson & Dixon-Coles goal-distribution models. |
| **scikit-learn** | ML Baseline & Calibration | Feature preprocessing, Logistic Regression, Isotonic Regression, Platt Scaling. |
| **XGBoost / LightGBM** | Advanced ML Models | Gradient boosted decision trees optimized for tabular match feature datasets. |
| **pandas / NumPy** | Data Processing | Vectorized numerical processing and feature matrix construction. |
| **Joblib / Cloudpickle** | Serialization | Versioned serialization of trained model artifacts and calibration scalars. |

---

### 5. BACKGROUND JOBS & WORKER EVALUATION

| Option | Status | Advantages | Disadvantages | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Modal.com** | **SELECTED** | Serverless Python worker pool, instant cold starts, GPU/CPU scaling, zero infra management. | Pay-per-second cloud cost. | **CHOSEN (ML Compute)** |
| **Celery + Redis** | Alternative | Industry standard, flexible. | Requires running persistent EC2/Redis infrastructure. | Backup Option |
| **Upstash QStash** | **SELECTED** | Serverless HTTP queue, ideal for Vercel scheduled cron triggers. | Limited to HTTP webhooks. | **CHOSEN (Cron triggers)** |
