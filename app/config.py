import os
from celery import Celery

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

# Настройки API-ключей
API_KEYS = {
    "testkey": "user1",
    "examplekey": "user2",
}


# Функция для проверки API-ключа
def validate_api_key(api_key: str) -> bool:
    return api_key in API_KEYS
