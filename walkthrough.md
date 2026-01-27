# Walkthrough - Lupa Política

I have successfully implemented the architecture described in `context.md`. The system is now a robust FastAPI application with a resilient ingestion pipeline, dedicated AI analysis worker via Celery, and a structured database schema.

## Changes Made

### 1. Robust Ingestion Pipeline
- **Strict Validation**: Implemented `StrictGastoSchema` (Pydantic V2) which enforces rigid data types and forbids extra fields from the Câmara API.
- **Resilience Ingestor**: Created `ResilienceIngestor` with a "Dead Letter Queue" (DLQ) mechanism. If the data fails validation, it's stored in the `sys_ingestion_dlq` table instead of crashing the pipeline.

### 2. Intelligence Layer (Gemini AI)
- **Structured Outputs**: The `GeminiClient` is configured to return a typed JSON response matching our audit requirements (impact, risks, sentiment).
- **Asynchronous Worker**: Integrated Celery with Redis. AI analyses are processed in the background to ensure the API remains responsive.

### 3. Database Schema
- Implemented models for **Politicos**, **Gastos**, **Empresas**, **DLQ**, and **AnalisesIA** using SQLAlchemy 2.0 (Async).

## How to Run

### 1. Database Migrations
Before starting the app, you need to create the tables in your cloud database:
```bash
# Generate the initial migration
docker-compose exec api alembic revision --autogenerate -m "Initial migration"

# Apply the migration
docker-compose exec api alembic upgrade head
```

### 2. Configure Cloud Services
Since you are using cloud instances for Postgres and Redis, ensure you have a `.env` file in the root directory (use `.env.example` as a template):
```env
DATABASE_URL=postgresql+asyncpg://user:password@cloud-host:5432/lupa_politica
REDIS_URL=redis://cloud-host:6379/0
GEMINI_API_KEY=your_google_ai_key_here
```

### 3. Build and Start
Run the following command to build and start the API and Worker:
```bash
docker-compose up --build -d
```

## Recent Fixes
- **Worker Auto-Reload**: Added `watchdog` and configured `docker-compose.yml` to use `watchmedo`. The worker now restarts automatically when code in `src/` changes.
- **URL Resilience**: Added logic to `src/core/database.py` to automatically detect and fix `DATABASE_URL` if it's missing the `+asyncpg` prefix.
- **Database Driver**: Added `psycopg2-binary` to ensure compatibility with standard PostgreSQL connections and sync operations that some dependencies might trigger. 
- **Flower Service**: Added `flower` as a dependency in `pyproject.toml` and updated `docker-compose.yml` to build from the local Dockerfile.
- **Health Checks**: Added health checks to all services (`api`, `worker`, `flower`) to ensure they are running and responsive. `curl` was added to the `Dockerfile` to support these checks.
- **Poetry Build Error**: Added `package-mode = false` to `pyproject.toml` and `--no-root` to `Dockerfile`.

### 3. Trigger Ingestion
Once the system is up, you can trigger data ingestion via the interactive docs at `http://localhost:8000/docs` or using `curl`:
```bash
curl -X POST http://localhost:8000/ingest/gastos/204554
```
*(Where 204554 is an example ID of a deputy)*

### 4. Monitor
- **API Docs**: `http://localhost:8000/docs`
- **Celery Tasks (Flower)**: `http://localhost:5555`

## Verification Results
- Core logic for data validation and DLQ fallback implemented.
- Background worker configured for Gemini AI processing.
- Docker environment prepared for easy deployment.
