# Docubank

Multi-tenat agentic RAG platform for banking documents.
Users upload per-year policy PDFs, an agentic workflow answers questions with exact numeric accuracy and strict tenant isolation.

## Architecture

React (SSE) → API Gateway (Cognito + WAF) → ALB → ECS Fargate (FastAPI) → LangGraph: guardrail → year-resolve → hybrid retrieval (pgvector + tsvector, RRF) → rerank → answer → evaluator loop ingest: S3 → SQS → worker (pymupdf) → chunks → embeddings → Postgres

## Local setup

Requires: Docker, uv.

    docker compose up -d
    cd api && uv sync
    cd ../worker && uv sync
    python scripts/generate_fake_data.py