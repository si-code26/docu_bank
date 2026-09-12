# Docubank

Mult-tenat agentic RAG platform for banking document.
Users upload per-year policy PDFs, an agentic workflow answers questions with excat numeric accuracy and strict tenant isolation.

## Architecture

React (SSE) → API Gateway (Congnito + WAF) → ALB → ECS Fargate (FastAPI) → LangGraph: guardrail → year-resolve → hybrid retrieval (pgvector + tsvector, RRF) → rerank → answer → evaluator loop ingest: S3 → SQS → worker (pymupdf) → chunks → embeddings → Postgre

## Local setup

Requires: Docker, uv.

    docker compose up -d
    cd api && uv sync
    cd ../worker && uv sync
    python scripts/generate_fake_data.py