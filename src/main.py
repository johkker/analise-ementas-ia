from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.services.extractor.camara import CamaraExtractor
from src.services.resilience_ingestor import ResilienceIngestor
from src.services.ai_worker import processar_analise_ia

app = FastAPI(title="Lupa Política API")

@app.get("/")
async def root():
    return {"message": "Lupa Política is running"}

@app.post("/ingest/gastos/{deputado_id}")
async def ingest_gastos(deputado_id: int, db: AsyncSession = Depends(get_db)):
    extractor = CamaraExtractor()
    ingestor = ResilienceIngestor(db)
    
    # Busca dados da API
    raw_gastos = await extractor.get_gastos(deputado_id)
    
    # Processa e salva no banco (com DLQ se falhar)
    await ingestor.process_gastos_batch(deputado_id, raw_gastos)
    
    # Trigger AI analysis for the first few (demo)
    for gasto in raw_gastos[:3]: # Só os 3 primeiros para não gastar tokens à toa no teste
        processar_analise_ia.delay(
            entidade_tipo="GASTO",
            entidade_id=gasto.get('idDocumento'),
            texto_para_analise=f"Gasto de {gasto.get('valorLiquido')} com {gasto.get('nomeFornecedor')} para {gasto.get('tipoDespesa')}"
        )
        
    return {"status": "Ingestion started", "count": len(raw_gastos)}
