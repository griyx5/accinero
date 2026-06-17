"""
Модели базы данных для системы VaccinePro (SQLite)
"""
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Text, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'Patients'
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    birth_date = Column(Date, nullable=False)
    phone = Column(String(20))
    snils = Column(String(14), unique=True)

    vaccinations = relationship("Vaccination", back_populates="patient", cascade="all, delete-orphan")
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")

class Vaccine(Base):
    __tablename__ = 'Vaccines'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    manufacturer = Column(String(100))
    min_interval_days = Column(Integer, nullable=False)

    vaccinations = relationship("Vaccination", back_populates="vaccine")

class Procedure(Base):
    __tablename__ = 'Procedures'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    procedure_type = Column(String(50))

    medical_records = relationship("MedicalRecord", back_populates="procedure")

class Vaccination(Base):
    __tablename__ = 'Vaccinations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('Patients.id', ondelete='CASCADE'), nullable=False)
    vaccine_id = Column(Integer, ForeignKey('Vaccines.id'), nullable=False)
    dose = Column(Float, nullable=False)
    series = Column(String(50))
    date = Column(Date, nullable=False)

    patient = relationship("Patient", back_populates="vaccinations")
    vaccine = relationship("Vaccine", back_populates="vaccinations")

    __table_args__ = (
        CheckConstraint('dose > 0', name='check_dose_positive'),
    )

class MedicalRecord(Base):
    __tablename__ = 'MedicalRecords'
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('Patients.id', ondelete='CASCADE'), nullable=False)
    procedure_id = Column(Integer, ForeignKey('Procedures.id'), nullable=False)
    doctor_name = Column(String(100), nullable=False)
    diagnosis = Column(Text)
    date = Column(Date, nullable=False)

    patient = relationship("Patient", back_populates="medical_records")
    procedure = relationship("Procedure", back_populates="medical_records")