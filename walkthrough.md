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

### 1. Set Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_google_ai_key_here
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/lupa_politica
REDIS_URL=redis://redis:6379/0
```

### 2. Start Infrastructure
Run the following command to start the database, redis, api, worker, and flower (monitor):
```bash
docker-compose up --build
```

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
