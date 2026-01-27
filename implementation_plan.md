# Implementation Plan - Lupa Política (Analise Ementas IA)

## Goal Description
Build a robust political data analysis system that ingests data from the Câmara dos Deputados, stores it in a structured PostgreSQL database, and uses Generative AI (Gemini) to analyze legislative proposals for clarity, financial impact, and potential corruption risks.

# Advanced Exploration & Deputy Insights

Expand the analysis capabilities with advanced time filters, better data performance (caching), and a unified deputy profile view.

## Proposed Changes

### Backend: Advanced Queries
---
#### [MODIFY] [gastos.py](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/src/api/routes/gastos.py)
- [DONE] Added `data_inicio` and `data_fim` to `/gastos/exploration`.

#### [MODIFY] [deputados.py](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/src/api/routes/deputados.py)
- Ensure a `GET /deputados/{id}/details` endpoint exists to aggregate:
    - Recent Expenses.
    - Voting History.
    - Authorship of Propositions.

### Frontend: Performance & UX
---
#### [MODIFY] [layout.tsx](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/frontend/app/layout.tsx)
- Install and wrap the app in `@tanstack/react-query` provider for global caching.

#### [MODIFY] [gastos/page.tsx](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/frontend/app/gastos/page.tsx)
- Add a "Period" selector (Last 30 days, Specific month, Custom range).
- Integrate a DateRangePicker component.

#### [NEW] [DeputyDetails.tsx](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/frontend/components/deputados/DeputyDetailsModal.tsx)
- A high-tech shadcn Dialog showing the full profile of a deputy.
- Tabs for "Gastos", "Proposições" and "Frequência".

## Verification Plan

### Automated Tests
- Test API throughput with caching headers.
- Build test after adding react-query.

### Manual Verification
- Filter expenses by a specific week in 2026.
- Navigate to a deputy profile and open the modal from the dashboard.

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
-## Deployment Plan (Vercel)

### Pre-requisites
- Backend deploy at Railway with fixed CORS regex.
- Frontend `.env.local` set to production API.

### Steps
1. Push latest changes to GitHub (Manual or via Agent).
2. Connect Vercel to the repository.
3. Configure `NEXT_PUBLIC_API_URL` as a Production/Preview environment variable.
4. Set the Root Directory to `frontend/`.
5. Trigger initial deployment.

### Production Verification
- Verify that statistics fetch correctly from the Railway API.
- Test deputy filters on the newly deployed Vercel domain.
