# Implementation Plan - Lupa Política (Analise Ementas IA)

## Goal Description
Build a robust political data analysis system that ingests data from the Câmara dos Deputados, stores it in a structured PostgreSQL database, and uses Generative AI (Gemini) to analyze legislative proposals for clarity, financial impact, and potential corruption risks.

# Dashboard & Expense Exploration

Implement a more powerful dashboard focused on the current year and a dedicated exploration page for deep-diving into deputy spending.

## Proposed Changes

### Backend: Statistics & Exploration
---
#### [MODIFY] [stats.py](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/src/api/routes/stats.py)
Update `/stats/dashboard` to:
- Filter `total_gastos` by current year (2026).
- Add `top_spenders` (top 5 deputies by total spending).
- Add `expense_by_category` (aggregation by `tipo_despesa`).

#### [NEW] [gastos.py](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/src/api/routes/gastos.py)
Create a new router for exploration:
- `GET /gastos/exploration`: Paginated list of expenses with filters:
    - `politico_id`
    - `ano`
    - `mes`
    - `tipo_despesa`
    - `min_valor` / `max_valor`

### Frontend: UI/UX Improvements
---
#### [MODIFY] [page.tsx](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/frontend/app/page.tsx)
- **Stats Integration**: Update `DashboardStats` to fetch from `/stats/dashboard`.
- **Top Spenders Widget**: Create a new component `TopSpendersList` with horizontal scrolling or a glassmorphic list.
- **Spending By Category**: Implement a `CategoryMetric` component showing the top categories with progress bars (Emerald Green).
- **Navigation**: Add a "Explorar Gastos" CTA card leading to the new exploration page.

#### [NEW] [exploration/page.tsx](file:///wsl.localhost/Ubuntu/home/johkker/analise-ementas-ia/frontend/app/gastos/page.tsx)
- **Filter Management**: Use URL state for persistent filtering.
- **Expense Grid**: Cards showing `Suppliers`, `Date`, and `Value`.
- **AI Ribbon**: A subtle emerald glow on cards that have `ai_resumo`.
- **Modal View**: Clicking a card opens a modal with the receipt link and the full technical `AnaliseIA`.
- **Infinite Scroll / Pagination**: Use the `total` and `page` parameters from the API.

## Verification Plan

### Automated Tests
- `npm run build` to ensure no regression in Next.js.
- Verify API response for `/gastos/exploration` manually with various query params.

### Manual Verification
- **Dashboard**: Confirm Top Spenders show photos and accurate 2026 totals.
- **Exploration**: Verify filters (Party/Name) narrow down the list instantly.
- **Aesthetics**: Ensure glassmorphism blur and Emerald accents match `MASTER.md`.

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
