from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=getattr(settings, "DB_POOL_SIZE", 20),
    max_overflow=getattr(settings, "DB_MAX_OVERFLOW", 40),
    pool_timeout=getattr(settings, "DB_POOL_TIMEOUT", 30),
    pool_recycle=getattr(settings, "DB_POOL_RECYCLE", 1800),
)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)

def check_db_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
