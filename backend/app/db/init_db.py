from .models import Base
from .session import engine
from sqlalchemy import text

def init_db():
    Base.metadata.create_all(bind=engine)

def clear_db():
    from .session import SessionLocal
    db = SessionLocal()
    db.execute(text('DELETE FROM traffic_flow;'))
    db.execute(text('DELETE FROM traffic_incident;'))
    db.commit()
    db.close()
    print("✅ Tables cleared successfully.")

if __name__ == "__main__":
    clear_db()
    init_db()
    print("✅ Tables created successfully.")
