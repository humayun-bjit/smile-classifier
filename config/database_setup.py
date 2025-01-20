from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database_model import Base

# SQLite database URL
DATABASE_URL = "mysql+pymysql://root:123456@mysql_container/mini_project_fastapi"
 
# Create engine
engine = create_engine(DATABASE_URL)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency that creates a new database session for each request
    and closes it after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()