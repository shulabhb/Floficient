from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Read the DB URL from config.py (which reads from .env)
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Set echo=True to see generated SQL queries (for debugging)
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
print(f"[DEBUG] session.py loaded. engine: {engine}")

# SessionLocal is the class you'll use to create DB sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
