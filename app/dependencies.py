from .models import SessionLocal


def get_db():
    """
    Создает сессию базы данных для запроса и автоматически закрывает ее после использования.
    Используется как зависимость в маршрутах FastAPI для получения сессии базы данных.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
