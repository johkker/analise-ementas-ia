from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
# Import models to ensure they are registered with Base
from src.models.gasto import Gasto, Empresa
from src.models.politico import Politico
from src.models.proposicao import Proposicao
from src.models.votacao import Votacao
from src.models.voto import Voto
from src.core.config import settings

from sqlalchemy.pool import NullPool

# Garante que o driver asyncpg seja usado mesmo que o usuário esqueça no .env
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    db_url, 
    echo=True,
    poolclass=NullPool
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Integragem com Celery para evitar erros de fork (InterfaceError)
def setup_worker_db():
    from celery.signals import worker_process_init
    @worker_process_init.connect
    def init_worker(**kwargs):
        import asyncio
        # No worker, queremos que o engine limpe qualquer conexão herdada do pai
        # e crie novas sob demanda no novo processo
        asyncio.run(engine.dispose())

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
