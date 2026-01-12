from celery import Celery
import os
from config import settings
from db.models.tasks import Task
from db.database import engine

celery_client = Celery(
    "celery_app",
    broker=settings.REDIS_CELERY_BROKER,
    backend=settings.REDIS_URL,
    timezone="Asia/Kolkata",
    enable_utc=False,
)

celery_client.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    include=["tasks.process_file"],
)
celery_client.autodiscover_tasks()
import redis
redis_client = redis.Redis.from_url(settings.REDIS_URL)
redis_client.ping()