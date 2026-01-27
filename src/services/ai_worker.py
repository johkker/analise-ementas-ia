from decimal import Decimal
from src.core.celery_app import celery_app
from src.services.llm_service import GeminiClient
from src.core.database import AsyncSessionLocal
from src.models.analise import AnaliseIA
import asyncio

from google.api_core.exceptions import ResourceExhausted

# Celery task
@celery_app.task(
    bind=True, 
    max_retries=1, 
    autoretry_for=(ResourceExhausted, Exception),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    rate_limit='4/m'  # Safe under the 5 RPM limit for Gemini 3/2.5 Flash
)
def processar_analise_ia(self, entidade_tipo: str, entidade_id: int, texto_para_analise: str):
    # Nota: Celery worker é síncrono por padrão, mas podemos rodar async dentro
    return asyncio.run(_async_processar_analise_ia(entidade_tipo, entidade_id, texto_para_analise))

@celery_app.task(bind=True)
def mass_analyze_pending_gastos(self, batch_size: int = 20):
    """
    Cron-ready task to find Gasto records without AnaliseIA and process them.
    Rate limit is handled by the processar_analise_ia task itself.
    """
    return asyncio.run(_async_mass_analyze(batch_size))

async def _async_mass_analyze(batch_size: int):
    from src.models.gasto import Gasto
    from src.models.analise import AnaliseIA
    from sqlalchemy import select, and_
    
    async with AsyncSessionLocal() as db:
        # Find Gastos that don't have an AnaliseIA
        # Using a subquery for NOT EXISTS
        subq = select(AnaliseIA.entidade_id).where(AnaliseIA.entidade_tipo == 'GASTO')
        stmt = select(Gasto).where(and_(
            Gasto.ext_id.not_in(subq),
            Gasto.valor > 1000 # Prioritize larger expenses (optional heuristic)
        )).limit(batch_size)
        
        result = await db.execute(stmt)
        pending_gastos = result.scalars().all()
        
        print(f"Feeding {len(pending_gastos)} pending gastos info to the AI queue.")
        
        for gasto in pending_gastos:
            processar_analise_ia.delay(
                entidade_tipo="GASTO",
                entidade_id=gasto.ext_id,
                texto_para_analise=f"Gasto de R$ {gasto.valor} com {gasto.empresa_cnpj} p/ {gasto.tipo_despesa} em {gasto.data_emissao}"
            )
        
    return {"queued": len(pending_gastos)}

async def _async_processar_analise_ia(entidade_tipo: str, entidade_id: int, texto_para_analise: str):
    from src.core.database import engine, AsyncSessionLocal
    
    if entidade_id is None:
        return {"status": "skipped", "reason": "null_id"}

    llm = GeminiClient()
    try:
        resultado = llm.analisar_gasto(texto_para_analise)
        
        async with AsyncSessionLocal() as db:
            nova_analise = AnaliseIA(
                entidade_tipo=entidade_tipo,
                entidade_id=entidade_id,
                resumo_critico=resultado.get('resumo_executivo'),
                impacto_financeiro=resultado.get('impacto_financeiro'),
                grupos_beneficiados=resultado.get('grupos_beneficiados'),
                riscos_corrupcao=resultado.get('riscos_corrupcao'),
                raw_response=resultado
            )
            # Safe score conversion
            score = resultado.get('sentimento_politico', 0)
            nova_analise.score_anomalia = Decimal(str(score)) if score is not None else Decimal('0')
            
            db.add(nova_analise)
            await db.commit()
            
        print(f"✅ AI Analysis completed for {entidade_tipo} {entidade_id}")
        return {"status": "success", "entidade_id": entidade_id}
    except Exception as e:
        print(f"❌ AI Worker Error for {entidade_id}: {e}")
        raise
    finally:
        await engine.dispose()
