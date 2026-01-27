from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "lupa_politica_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.services.ai_worker"]
)

celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_serializer="json",
    accept_content=["json"],
    task_routes={
        "src.services.ai_worker.*": {"queue": "ai_queue"}
    },
    task_annotations={
        "*": {"rate_limit": "50/m"} 
    }
)
