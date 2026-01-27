from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.services.extractor.camara import CamaraExtractor
from src.services.resilience_ingestor import ResilienceIngestor
from src.services.ai_worker import processar_analise_ia

from src.api.routes import deputados, proposicoes, stats, gastos
from src.core.security import rate_limiter

from google import genai
from src.core.config import settings

app = FastAPI(title="Lupa Política API")

@app.on_event("startup")
async def startup_event():
    print("--- Checking Available Gemini Models ---")
    if settings.GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            for m in client.models.list():
                # The new SDK model object has 'name' attribute
                print(f"  - Model: {m.name}")
        except Exception as e:
            print(f"  - Error listing models: {e}")
    else:
        print("  - GEMINI_API_KEY not configured.")
    print("----------------------------------------")

# Register Routers with Rate Limiting
app.include_router(deputados.router, dependencies=[Depends(rate_limiter)])
app.include_router(proposicoes.router, dependencies=[Depends(rate_limiter)])
app.include_router(stats.router, dependencies=[Depends(rate_limiter)])
app.include_router(gastos.router, dependencies=[Depends(rate_limiter)])

@app.get("/")
async def root():
    return {"message": "Lupa Política is running"}

@app.post("/ingest/deputados")
async def ingest_deputados(db: AsyncSession = Depends(get_db)):
    extractor = CamaraExtractor()
    ingestor = ResilienceIngestor(db)
    
    # Busca todos os deputados (resumo)
    raw_deputados = await extractor.get_deputados()
    
    # Processa e salva no banco
    await ingestor.process_deputados_batch(raw_deputados)
    
    return {"status": "Deputados population finished", "count": len(raw_deputados)}

@app.post("/ingest/gastos/{deputado_id}")
async def ingest_gastos(deputado_id: int, db: AsyncSession = Depends(get_db)):
    extractor = CamaraExtractor()
    ingestor = ResilienceIngestor(db)
    
    # Busca dados da API
    raw_gastos = await extractor.get_gastos(deputado_id)
    
    # Processa e salva no banco (com DLQ se falhar)
    await ingestor.process_gastos_batch(deputado_id, raw_gastos)
    
    return {"status": "Ingestion completed", "count": len(raw_gastos)}
