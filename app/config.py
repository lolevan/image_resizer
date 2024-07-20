import os

from celery import Celery

from sqlalchemy.orm import Session

from .models import APIKey

from .dependencies import get_db


# Настройки Redis и Celery
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    'tasks',
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


# Функция для проверки API-ключа
def validate_api_key(api_key: str, db: Session) -> bool:
    db_key = db.query(APIKey).filter(APIKey.key == api_key).first()
    return db_key is not None
