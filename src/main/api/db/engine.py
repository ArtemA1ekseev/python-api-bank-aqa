from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main.api.configs.config import Config


"""
Движок который управялет соединениями с БД
"""
engine = create_engine(Config.fetch('dataBaseUrl'), echo=False) # убрали логи SQL
SessionLocal = sessionmaker(bind=engine) # sessionmaker - Фабрика сессий