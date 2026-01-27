from datetime import datetime, timedelta
import asyncio
from src.core.celery_app import celery_app
from src.core.database import AsyncSessionLocal
from src.services.extractor.camara import CamaraExtractor
from src.services.resilience_ingestor import ResilienceIngestor

@celery_app.task(bind=True, max_retries=3)
def fetch_proposicoes_task(self, days_back: int = 7):
    asyncio.run(_async_fetch_proposicoes(days_back))

async def _async_fetch_proposicoes(days_back: int):
    # Setup dependencies
    extractor = CamaraExtractor()
    
    data_fim = datetime.now().strftime("%Y-%m-%d")
    data_inicio = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    print(f"Fetching proposicoes from {data_inicio} to {data_fim}")
    
    try:
        # Fetch data (pages handling could be added here or in extractor, 
        # for now extracting page 1 with 100 items as a start/demo)
        # Ideally we loop through pages until mapping is empty.
        
        # Simple pagination loop
        pagina = 1
        while True:
            raw_data = await extractor.get_proposicoes(data_inicio, data_fim, pagina=pagina)
            if not raw_data:
                break
                
            # Enrich with authors
            enriched_data = []
            for item in raw_data:
                try:
                    autores = await extractor.get_proposicao_autores(item['id'])
                    item['autores'] = autores
                    enriched_data.append(item)
                except Exception as e:
                    print(f"Error fetching authors for {item['id']}: {e}")
                    enriched_data.append(item)

            async with AsyncSessionLocal() as db:
                ingestor = ResilienceIngestor(db)
                await ingestor.process_proposicoes_batch(enriched_data)
            
            print(f"Processed page {pagina} with {len(raw_data)} propositions")
            pagina += 1
            if pagina > 10: # Safety break for now
                break
                
    except Exception as e:
        print(f"Error fetching proposicoes: {e}")
        raise

@celery_app.task(bind=True, max_retries=3)
def fetch_votacoes_task(self, days_back: int = 7):
    asyncio.run(_async_fetch_votacoes(days_back))

async def _async_fetch_votacoes(days_back: int):
    extractor = CamaraExtractor()
    
    data_fim = datetime.now().strftime("%Y-%m-%d")
    
    # API restriction: dataInicio and dataFim must be in same year if provided.
    # Handling cross-year fetching requires logic, for now assume current year or short window.
    start_date = datetime.now() - timedelta(days=days_back)
    if start_date.year != datetime.now().year:
         start_date = datetime(datetime.now().year, 1, 1)
         
    data_inicio = start_date.strftime("%Y-%m-%d")
    
    print(f"Fetching votacoes from {data_inicio} to {data_fim}")
    
    try:
        pagina = 1
        while True:
            raw_data = await extractor.get_votacoes(data_inicio, data_fim, pagina=pagina)
            if not raw_data:
                break
                
            # Enrich with individual votes
            enriched_data = []
            for item in raw_data:
                try:
                    votos = await extractor.get_votacao_votos(item['id'])
                    item['votos'] = votos
                    enriched_data.append(item)
                except Exception as e:
                    print(f"Error fetching votes for {item['id']}: {e}")
                    # Still ingest the votacao without votes
                    enriched_data.append(item)
            
            async with AsyncSessionLocal() as db:
                ingestor = ResilienceIngestor(db)
                await ingestor.process_votacoes_batch(enriched_data)
                
            print(f"Processed page {pagina} with {len(raw_data)} votes")
            pagina += 1
            if pagina > 10:
                break

    except Exception as e:
        print(f"Error fetching votacoes: {e}")
        raise
