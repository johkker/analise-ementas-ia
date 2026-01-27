# Implementation Plan - Lupa Política (Analise Ementas IA)

## Goal Description
Build a robust political data analysis system that ingests data from the Câmara dos Deputados, stores it in a structured PostgreSQL database, and uses Generative AI (Gemini) to analyze legislative proposals for clarity, financial impact, and potential corruption risks.

## User Review Required
No immediate user review required for proceed with initial file creation.

## Proposed Changes

### Core Infrastructure
#### [NEW] [pyproject.toml](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/pyproject.toml)
- Define dependencies: FastAPI, SQLAlchemy, Alembic, Pydantic, Celery, Redis, Google Generative AI.

#### [NEW] [docker-compose.yml](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/docker-compose.yml)
- Services: Postgres (db), Redis (broker), Web App (api), Celery Worker (worker), Flower (monitor).

### Database Schema
#### [NEW] [src/core/database.py](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/src/core/database.py)
- Async SQLAlchemy engine and session factory.

#### [NEW] [src/models/](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/src/models/)
- `politico.py`: Politician data.
- `gasto.py`: Expenses data.
- `dlq.py`: Dead Letter Queue for ingestion errors.
- `analise.py`: AI analysis results.

### Ingestion Logic
#### [NEW] [src/schemas/camara_api.py](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/src/schemas/camara_api.py)
- Pydantic models for API responses.

#### [NEW] [src/services/resilience_ingestor.py](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/src/services/resilience_ingestor.py)
- Implement `ResilienceIngestor` class with Strict Mode validation and DLQ fallback.

### Intelligence Layer
#### [NEW] [src/services/llm_service.py](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/src/services/llm_service.py)
- Implement `GeminiClient` with structured output using `response_schema`.

#### [NEW] [src/services/ai_worker.py](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/src/services/ai_worker.py)
- Celery task for asynchronous AI analysis with retry logic.

## Verification Plan

### Automated Tests
- Run `pytest` for unit tests of schemas and extractor logic.
- Verify database migrations with `alembic upgrade head`.

### Manual Verification
- Start services via `docker-compose up`.
- Trigger ingestion endpoint via Swagger UI.
- Verify data in Postgres using a client.
- Check Celery worker logs for AI task execution.
