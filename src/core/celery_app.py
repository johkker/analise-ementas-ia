from celery import Celery
from src.core.config import settings
from src.core.database import setup_worker_db

setup_worker_db()

celery_app = Celery(
    "lupa_politica_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.services.ai_worker", "src.services.data_fetcher"]
)

celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_serializer="json",
    accept_content=["json"],
    task_routes={
        "src.services.ai_worker.*": {"queue": "ai_queue"},
        "src.services.data_fetcher.*": {"queue": "ai_queue"}
    },
    task_annotations={
        "*": {"rate_limit": "50/m"} 
    }
)

from celery.schedules import crontab
celery_app.conf.beat_schedule = {
    'fetch-deputados-weekly': {
        'task': 'src.services.data_fetcher.fetch_deputados_task',
        'schedule': crontab(day_of_week='sun', hour=1, minute=0),
    },
    'fetch-proposicoes-daily': {
        'task': 'src.services.data_fetcher.fetch_proposicoes_task',
        'schedule': crontab(hour=2, minute=0),
        'args': (7,) 
    },
    'fetch-votacoes-daily': {
        'task': 'src.services.data_fetcher.fetch_votacoes_task',
        'schedule': crontab(hour=3, minute=0),
        'args': (7,) 
    },
    'analyze-gastos-periodic': {
        'task': 'src.services.ai_worker.mass_analyze_pending_gastos',
        'schedule': crontab(minute='*/15'), # Run every 15 mins
        'args': (2,) # Analyze 2 items per run (total 192/day max if 1.5 flash, or respects 20 RPD better)
    }
}
