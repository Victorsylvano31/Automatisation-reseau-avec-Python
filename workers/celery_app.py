from celery import Celery
from core.config import settings

celery_app = Celery(
    "nre_platform",
    broker="memory://", # Pas de Redis nécessaire
    backend="cache+memory://",
    include=["workers.tasks"]
)

celery_app.conf.update(
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,  # Exécute tout en synchrone pour le test local sans Redis
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
