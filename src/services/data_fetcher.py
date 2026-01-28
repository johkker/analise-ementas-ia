from datetime import datetime, timedelta
import asyncio
from src.core.celery_app import celery_app
from src.core.database import AsyncSessionLocal
from src.services.extractor.camara import CamaraExtractor
from src.services.resilience_ingestor import ResilienceIngestor

from sqlalchemy import select
from src.models.politico import Politico

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
def fetch_gastos_task(self, ano: int = None):
    if ano is None:
        ano = datetime.now().year
    asyncio.run(_async_fetch_all_gastos(ano))

async def _async_fetch_all_gastos(ano: int):
    extractor = CamaraExtractor()
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Politico.id))
        politico_ids = [row[0] for row in result.all()]
    
    print(f"Starting expense fetching for {len(politico_ids)} deputies for year {ano}")
    
    async def fetch_for_deputy(pid):
        try:
            pagina = 1
            total_ingested = 0
            while True:
                raw_gastos = await extractor.get_gastos(pid, ano, pagina=pagina, itens=100)
                if not raw_gastos:
                    break
                    
                async with AsyncSessionLocal() as db:
                    ingestor = ResilienceIngestor(db)
                    await ingestor.process_gastos_batch(pid, raw_gastos)
                
                total_ingested += len(raw_gastos)
                pagina += 1
                if pagina > 50: # Safety break
                    break
            
            if total_ingested > 0:
                print(f"  - Ingested {total_ingested} expenses for deputy {pid}")
        except Exception as e:
            print(f"Error fetching expenses for deputy {pid}: {e}")

    # Use a semaphore to control concurrency and avoid hitting rate limits or DB connection limits too hard
    sem = asyncio.Semaphore(10)

    async def throttled_fetch(pid):
        async with sem:
            await fetch_for_deputy(pid)

    tasks = [throttled_fetch(pid) for pid in politico_ids]
    await asyncio.gather(*tasks)

@celery_app.task(bind=True, max_retries=3)
def fetch_gastos_rescan_task(self):
    """
    Rescanning task: busca gastos dos últimos 90 dias.
    
    Executa: Todos os dias
    Justificativa:
    - Câmara tem defasagem até 30 dias
    - Deputados podem demorar até 3 meses para lançar um gasto
    - Rescanning garante que gastos atrasados sejam capturados
    
    Estratégia:
    - Busca 90 dias atrás
    - Roda diariamente
    - Deduplicação no banco garante que não insere duplicatas
    """
    asyncio.run(_async_fetch_gastos_rescan())

async def _async_fetch_gastos_rescan():
    """Busca gastos dos últimos 90 dias para pegar dados atrasados."""
    extractor = CamaraExtractor()
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Politico.id))
        politico_ids = [row[0] for row in result.all()]
    
    days_back = 90
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    print(f"🔄 RESCAN: Starting rescan for {len(politico_ids)} deputies")
    print(f"   Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} (90 dias)")
    
    async def fetch_for_deputy(pid):
        try:
            total_found = 0
            # Câmara API usa ano como parâmetro, então fazemos request por ano
            for year in [start_date.year, datetime.now().year]:
                pagina = 1
                while True:
                    raw_gastos = await extractor.get_gastos(pid, year, pagina=pagina, itens=100)
                    if not raw_gastos:
                        break
                    
                    # Filtra apenas gastos dentro da janela de 90 dias
                    filtered_gastos = []
                    for gasto in raw_gastos:
                        try:
                            # Parse data do gasto
                            gasto_date_str = gasto.get('dataDocumento') or gasto.get('dataPagamento')
                            if gasto_date_str:
                                gasto_date = datetime.strptime(gasto_date_str[:10], "%Y-%m-%d")
                                if start_date <= gasto_date <= end_date:
                                    filtered_gastos.append(gasto)
                                    total_found += 1
                        except Exception:
                            # Se não conseguir parsear data, inclui mesmo assim
                            filtered_gastos.append(gasto)
                    
                    if filtered_gastos:
                        async with AsyncSessionLocal() as db:
                            ingestor = ResilienceIngestor(db)
                            await ingestor.process_gastos_batch(pid, filtered_gastos)
                    
                    pagina += 1
                    if pagina > 50:
                        break
            
            if total_found > 0:
                print(f"  ✓ Deputy {pid}: Found {total_found} expenses in 90-day window")
        except Exception as e:
            print(f"  ✗ Deputy {pid}: Error - {e}")

    # Semaphore para controlar concorrência
    sem = asyncio.Semaphore(10)

    async def throttled_fetch(pid):
        async with sem:
            await fetch_for_deputy(pid)

    tasks = [throttled_fetch(pid) for pid in politico_ids]
    await asyncio.gather(*tasks)
    
    print(f"✅ RESCAN: Completed for all {len(politico_ids)} deputies")

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
                if pagina > 50:
                    print("Reached page limit (50).")
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
                if pagina > 50: 
                    print("Reached page limit (50).")
                    break

        except Exception as e:
            print(f"Error in votacoes chunk {data_inicio}-{data_fim}: {e}")
            
        current_start = current_end + timedelta(days=1)
