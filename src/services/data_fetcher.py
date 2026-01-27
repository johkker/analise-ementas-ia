from datetime import datetime, timedelta
import asyncio
from src.core.celery_app import celery_app
from src.core.database import AsyncSessionLocal
from src.services.extractor.camara import CamaraExtractor
from src.services.resilience_ingestor import ResilienceIngestor

@celery_app.task(bind=True, max_retries=3)
def fetch_deputados_task(self):
    asyncio.run(_async_fetch_deputados())

async def _async_fetch_deputados():
    extractor = CamaraExtractor()
    try:
        raw_data = await extractor.get_deputados()
        if not raw_data:
            return
            
        async with AsyncSessionLocal() as db:
            ingestor = ResilienceIngestor(db)
            await ingestor.process_deputados_batch(raw_data)
        
        print(f"Processed {len(raw_data)} deputies.")
    except Exception as e:
        print(f"Error fetching deputados: {e}")
        raise

@celery_app.task(bind=True, max_retries=3)
def fetch_proposicoes_task(self, days_back: int = 7):
    asyncio.run(_async_fetch_proposicoes(days_back))

async def _async_fetch_proposicoes(days_back: int):
    extractor = CamaraExtractor()
    
    # Target dates
    end_date_absolute = datetime.now()
    start_date_absolute = end_date_absolute - timedelta(days=days_back)
    
    # Split the range into 90-day chunks (API limit is approx 3 months)
    current_start = start_date_absolute
    while current_start < end_date_absolute:
        current_end = min(current_start + timedelta(days=90), end_date_absolute)
        
        data_inicio = current_start.strftime("%Y-%m-%d")
        data_fim = current_end.strftime("%Y-%m-%d")
        
        print(f"--- Fetching proposicoes from {data_inicio} to {data_fim} ---")
        
        try:
            pagina = 1
            while True:
                raw_data = await extractor.get_proposicoes(data_inicio, data_fim, pagina=pagina)
                if not raw_data:
                    print(f"No more proposicoes for range {data_inicio} to {data_fim}")
                    break
                    
                enriched_data = []
                print(f"Enriching {len(raw_data)} propositions with authors...")
                for i, item in enumerate(raw_data):
                    try:
                        autores = await extractor.get_proposicao_autores(item['id'])
                        item['autores'] = autores
                        enriched_data.append(item)
                        if (i+1) % 20 == 0:
                            print(f"  - Progress: {i+1}/{len(raw_data)} enriched")
                    except Exception as e:
                        print(f"Error fetching authors for {item['id']}: {e}")
                        enriched_data.append(item)

                print(f"Ingesting batch of {len(enriched_data)} propositions...")
                async with AsyncSessionLocal() as db:
                    ingestor = ResilienceIngestor(db)
                    await ingestor.process_proposicoes_batch(enriched_data)
                
                print(f"✅ Processed page {pagina} with {len(raw_data)} propositions")
                pagina += 1
                if pagina > 5:
                    print("Reached page limit (5).")
                    break
                
        except Exception as e:
            print(f"Error in proposicoes chunk {data_inicio}-{data_fim}: {e}")
            
        current_start = current_end + timedelta(days=1)

@celery_app.task(bind=True, max_retries=3)
def fetch_votacoes_task(self, days_back: int = 7):
    asyncio.run(_async_fetch_votacoes(days_back))

async def _async_fetch_votacoes(days_back: int):
    extractor = CamaraExtractor()
    
    end_date_absolute = datetime.now()
    start_date_absolute = end_date_absolute - timedelta(days=days_back)
    
    current_start = start_date_absolute
    while current_start < end_date_absolute:
        current_end = min(current_start + timedelta(days=90), end_date_absolute)
        
        data_inicio = current_start.strftime("%Y-%m-%d")
        data_fim = current_end.strftime("%Y-%m-%d")
        
        print(f"--- Fetching votacoes from {data_inicio} to {data_fim} ---")
        
        try:
            pagina = 1
            while True:
                raw_data = await extractor.get_votacoes(data_inicio, data_fim, pagina=pagina)
                if not raw_data:
                    print(f"No more votacoes for range {data_inicio} to {data_fim}")
                    break
                    
                enriched_data = []
                print(f"Enriching {len(raw_data)} votacoes with individual votes...")
                for i, item in enumerate(raw_data):
                    try:
                        votos = await extractor.get_votacao_votos(item['id'])
                        item['votos'] = votos
                        enriched_data.append(item)
                        if (i+1) % 10 == 0:
                            print(f"  - Progress: {i+1}/{len(raw_data)} enriched")
                    except Exception as e:
                        print(f"Error fetching votes for {item['id']}: {e}")
                        enriched_data.append(item)
                
                print(f"Ingesting batch of {len(enriched_data)} votacoes...")
                async with AsyncSessionLocal() as db:
                    ingestor = ResilienceIngestor(db)
                    await ingestor.process_votacoes_batch(enriched_data)
                    
                print(f"✅ Processed page {pagina} with {len(raw_data)} votacoes")
                pagina += 1
                if pagina > 5: 
                    print("Reached page limit (5).")
                    break

        except Exception as e:
            print(f"Error in votacoes chunk {data_inicio}-{data_fim}: {e}")
            
        current_start = current_end + timedelta(days=1)
