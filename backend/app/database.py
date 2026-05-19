from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
import logging
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://pitchiq:pitchiq_secret@localhost:5432/pitchiq")

# Safely handle standard Render/Heroku 'postgres://' URLs
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Fallback to SQLite if PostgreSQL fails
logger = logging.getLogger(__name__)
db_type = "PostgreSQL"

try:
    if DATABASE_URL.startswith("postgresql"):
        # Attempt to create PostgreSQL engine
        engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 3})
        # Test connection
        conn = engine.connect()
        conn.close()
        logger.info("Connected to PostgreSQL successfully.")
    else:
        engine = create_engine(DATABASE_URL)
        db_type = "Unknown/Custom"
except Exception as e:
    logger.warning(f"PostgreSQL connection failed: {e}. Falling back to SQLite local file.")
    SQLITE_URL = "sqlite:///./pitchiq.db"
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    db_type = "SQLite"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
