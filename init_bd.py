"""
Инициализация базы данных SQLite: создание таблиц и тестовых данных
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Patient, Vaccine, Procedure, Vaccination, MedicalRecord
from datetime import date, timedelta
from db_config import DATABASE_URL

# Создаём все таблицы
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Проверяем, есть ли уже данные
if session.query(Patient).count() == 0:
    # Тестовые пациенты
    p1 = Patient(full_name="Иванов Иван Иванович", birth_date=date(1980, 5, 15),
                 phone="+7-999-123-45-67", snils="123-456-789 00")
    p2 = Patient(full_name="Петрова Мария Сергеевна", birth_date=date(1995, 10, 20),
                 phone="+7-888-234-56-78", snils="987-654-321 00")
    session.add_all([p1, p2])
    session.commit()

    # Справочники вакцин
    v1 = Vaccine(name="Корь-краснуха-паротит", manufacturer="Фармстандарт", min_interval_days=30)
    v2 = Vaccine(name="Гепатит B", manufacturer="Биофарм", min_interval_days=180)
    v3 = Vaccine(name="COVID-19 (Спутник V)", manufacturer="Гам-Казак", min_interval_days=21)
    session.add_all([v1, v2, v3])
    session.commit()

    # Справочник процедур
    pr1 = Procedure(name="Осмотр терапевта", procedure_type="осмотр")
    pr2 = Procedure(name="Прививка", procedure_type="инъекция")
    pr3 = Procedure(name="Флюорография", procedure_type="диагностика")
    session.add_all([pr1, pr2, pr3])
    session.commit()

    # Вакцинации
    vacc1 = Vaccination(patient_id=p1.id, vaccine_id=v1.id, dose=0.5,
                        series="A123", date=date.today() - timedelta(days=20))
    vacc2 = Vaccination(patient_id=p1.id, vaccine_id=v2.id, dose=1.0,
                        series="B456", date=date.today() - timedelta(days=10))
    vacc3 = Vaccination(patient_id=p2.id, vaccine_id=v3.id, dose=0.5,
                        series="C789", date=date.today() - timedelta(days=5))
    session.add_all([vacc1, vacc2, vacc3])
    session.commit()

    # Медицинские записи
    rec1 = MedicalRecord(patient_id=p1.id, procedure_id=pr1.id,
                         doctor_name="Доктор Смирнов", diagnosis="Острые респираторные инфекции",
                         date=date.today() - timedelta(days=15))
    rec2 = MedicalRecord(patient_id=p2.id, procedure_id=pr3.id,
                         doctor_name="Доктор Иванова", diagnosis="В норме",
                         date=date.today() - timedelta(days=3))
    session.add_all([rec1, rec2])
    session.commit()

    print("Тестовые данные добавлены.")
else:
    print("Данные уже существуют, пропускаем инициализацию.")

session.close()
print("Инициализация БД завершена. Файл vaccinepro.db создан.")