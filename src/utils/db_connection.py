from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.config import Config

config = Config()

engine = create_engine(
    config.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def init_db():
    from src.models import 
    
    Base.metadata.create_all(bind=engine)