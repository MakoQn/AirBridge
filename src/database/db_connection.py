from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.utils.config import Config
from src.database.models.base import Base

config = Config()

engine = create_engine(
    config.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()