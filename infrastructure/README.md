# Infrastructure & Deployment Architecture

## Overview

This directory documents the infrastructure boundaries established in Stage 3 according to **ADR-001 through ADR-009**.

## Component Responsibilities

| Component | Technology | Responsibilities | Deployment Host |
| :--- | :--- | :--- | :--- |
| **Web Frontend & API Gateway** | Next.js (TypeScript) App Router | UI presentation, user requests, edge API routing, health/readiness endpoints | Vercel |
| **Relational Database Boundary** | PostgreSQL (psycopg3) | Transactional storage, audit logs, feature snapshots | Supabase / Managed PostgreSQL |
| **ML & Data Service Boundary** | FastAPI (Python 3.12) | Typed feature computation, model inference, calibration | Async Python Worker (Modal.com / Fargate) |
| **Background Job Scheduler** | Modal.com / Upstash QStash | Scheduled data ingestion, web research scraping | Serverless Worker Pool |

## Environment Variables Configuration

Refer to `.env.example` in the root directory for all required variable names.
Never commit secrets or actual credentials to source control.
