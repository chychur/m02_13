from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config_file import settings


engine = create_engine(settings.db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
