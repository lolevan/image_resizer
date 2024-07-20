from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# Получение URL базы данных из переменных окружения, если не установлено, используется SQLite по умолчанию
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Создание движка базы данных
engine = create_engine(DATABASE_URL)

# Создание сессии базы данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей базы данных
Base = declarative_base()


# Определение модели APIKey для хранения API-ключей
class APIKey(Base):
    __tablename__ = "api_keys"  # Имя таблицы в базе данных
    key = Column(String, primary_key=True, index=True)  # Столбец для хранения API-ключа
    user = Column(String, index=True)  # Столбец для хранения имени пользователя

# Создание всех таблиц в базе данных
Base.metadata.create_all(bind=engine)
