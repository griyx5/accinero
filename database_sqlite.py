import sqlalchemy as sa
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date
from typing import List, Optional

# -------- ПОДКЛЮЧЕНИЕ К SQLITE (файл в папке проекта) --------
engine = create_engine("sqlite:///sevilia.db", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -------- МОДЕЛИ (ТЕ ЖЕ САМЫЕ) --------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(200), nullable=True)
    role = Column(String(50), default="user")

class Release(Base):
    __tablename__ = "releases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(20), unique=True, nullable=False)
    status = Column(String(50), nullable=False)
    first_released = Column(Date, nullable=False)

class DownloadStat(Base):
    __tablename__ = "download_stats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    release_id = Column(Integer, ForeignKey("releases.id", ondelete="CASCADE"), nullable=False)
    download_date = Column(Date, nullable=False, default=date.today)
    count = Column(BigInteger, nullable=False, default=0)

# -------- ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ (СОЗДАЁТ ФАЙЛ sevilia.db) --------
def init_db():
    Base.metadata.create_all(engine)
    print("✅ База данных SQLite создана (файл sevilia.db)")

# -------- ТЕСТОВЫЕ ДАННЫЕ (ТЕ ЖЕ) --------
def seed_test_data():
    with SessionLocal() as session:
        if session.query(User).count() == 0:
            session.add(User(username="admin", password_hash="admin123", email="admin@example.com", role="admin"))
        if session.query(Release).count() == 0:
            releases = [
                ("3.14", "pre-release", date(2025,10,1)),
                ("3.13", "bugfix", date(2024,10,7)),
                ("3.12", "security", date(2023,10,2)),
                ("3.11", "security", date(2022,10,24)),
                ("3.10", "security", date(2021,10,4)),
                ("3.9", "security", date(2020,10,5)),
                ("3.8", "end of line", date(2019,10,14)),
            ]
            for ver, stat, d in releases:
                session.add(Release(version=ver, status=stat, first_released=d))
        if session.query(DownloadStat).count() == 0:
            rel = session.query(Release).filter_by(version="3.13").first()
            if rel:
                session.add(DownloadStat(release_id=rel.id, count=10_000_000))
        session.commit()
        print("✅ Тестовые данные добавлены")

# -------- CRUD (ТЕ ЖЕ МЕТОДЫ) --------
class ReleaseCRUD:
    @staticmethod
    def get_all(session):
        return session.query(Release).order_by(Release.first_released.desc()).all()
    @staticmethod
    def create(session, version, status, first_released):
        r = Release(version=version, status=status, first_released=first_released)
        session.add(r)
        session.commit()
        return r
    @staticmethod
    def delete(session, release_id):
        r = session.query(Release).get(release_id)
        if r:
            session.delete(r)
            session.commit()
            return True
        return False

# -------- ЗАПУСК ПРИ ОДИНОЧНОМ ВЫПОЛНЕНИИ --------
if __name__ == "__main__":
    init_db()
    seed_test_data()
    with SessionLocal() as sess:
        print("\n--- Релизы в базе данных ---")
        for r in ReleaseCRUD.get_all(sess):
            print(f"{r.version} | {r.status} | {r.first_released}")