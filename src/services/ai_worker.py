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
    rate_limit='8/m'  # Conservador para o limite de 10 RPM do Free Tier
)
def processar_analise_ia(self, entidade_tipo: str, entidade_id: int, texto_para_analise: str):
    # Nota: Celery worker é síncrono por padrão, mas podemos rodar async dentro
    return asyncio.run(_async_processar_analise_ia(entidade_tipo, entidade_id, texto_para_analise))

async def _async_processar_analise_ia(entidade_tipo: str, entidade_id: int, texto_para_analise: str):
    from src.core.database import engine, AsyncSessionLocal
    
    # Se entidade_id ainda for None por algum motivo, não tentamos salvar (prevenção extra)
    if entidade_id is None:
        print(f"Aviso: entidade_id é None para {entidade_tipo}. Ignorando.")
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
            nova_analise.score_anomalia = Decimal(str(resultado.get('sentimento_politico', 0)))
            
            db.add(nova_analise)
            await db.commit()
            
        return {"status": "success", "entidade_id": entidade_id}
    except Exception as e:
        print(f"Erro no worker: {e}")
        raise
    finally:
        # Crucial: Como estamos usando asyncio.run(), o loop vai fechar.
        # Precisamos limpar as conexões do pool que estão presas a este loop.
        await engine.dispose()
