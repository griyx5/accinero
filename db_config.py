
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# SQLite — файл базы данных в текущей папке
DATABASE_URL = "sqlite:///vaccinepro.db"

engine = create_engine(DATABASE_URL, echo=False)  # echo=True для отладки SQL
SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()