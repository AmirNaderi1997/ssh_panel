from celery import Celery
from backend.app.config import settings

celery_app = Celery(
    "ssh_manager_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Optional configuration overrides
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour maximum limit
)

# Automatically find tasks under app.tasks package
celery_app.autodiscover_tasks(
    [
        "backend.app.tasks.ssh_tasks",
        "backend.app.tasks.ssl_tasks",
        "backend.app.tasks.backup_tasks",
        "backend.app.tasks.monitor_tasks",
        "backend.app.tasks.traffic_tasks",
    ],
    force=True,
)
