"""
Repository pattern для работы с SQLite
"""
from sqlalchemy.orm import Session
from models import Patient, Vaccine, Procedure, Vaccination, MedicalRecord
from datetime import date, timedelta

class PatientRepository:
    @staticmethod
    def get_all(session: Session):
        return session.query(Patient).all()

    @staticmethod
    def get_by_id(session: Session, patient_id: int):
        return session.query(Patient).get(patient_id)

    @staticmethod
    def add(session: Session, full_name, birth_date, phone, snils):
        patient = Patient(full_name=full_name, birth_date=birth_date, phone=phone, snils=snils)
        session.add(patient)
        session.commit()
        return patient

    @staticmethod
    def update(session: Session, patient_id, **kwargs):
        patient = session.query(Patient).get(patient_id)
        if patient:
            for key, value in kwargs.items():
                if hasattr(patient, key):
                    setattr(patient, key, value)
            session.commit()
            return True
        return False

    @staticmethod
    def delete(session: Session, patient_id):
        patient = session.query(Patient).get(patient_id)
        if patient:
            session.delete(patient)
            session.commit()
            return True
        return False

class VaccineRepository:
    @staticmethod
    def get_all(session: Session):
        return session.query(Vaccine).all()

    @staticmethod
    def get_by_id(session: Session, vaccine_id):
        return session.query(Vaccine).get(vaccine_id)

class ProcedureRepository:
    @staticmethod
    def get_all(session: Session):
        return session.query(Procedure).all()

    @staticmethod
    def get_by_id(session: Session, proc_id):
        return session.query(Procedure).get(proc_id)

class VaccinationRepository:
    @staticmethod
    def add(session: Session, patient_id, vaccine_id, dose, series, date_val):
        vacc = Vaccination(patient_id=patient_id, vaccine_id=vaccine_id,
                           dose=dose, series=series, date=date_val)
        session.add(vacc)
        session.commit()
        return vacc

    @staticmethod
    def get_by_patient(session: Session, patient_id):
        return session.query(Vaccination).filter(Vaccination.patient_id == patient_id).all()

    @staticmethod
    def get_next_due_date(vaccine, last_date):
        return last_date + timedelta(days=vaccine.min_interval_days)

class MedicalRecordRepository:
    @staticmethod
    def add(session: Session, patient_id, procedure_id, doctor_name, diagnosis, date_val):
        rec = MedicalRecord(patient_id=patient_id, procedure_id=procedure_id,
                            doctor_name=doctor_name, diagnosis=diagnosis, date=date_val)
        session.add(rec)
        session.commit()
        return rec

    @staticmethod
    def get_by_patient(session: Session, patient_id):
        return session.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).all()