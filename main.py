"""
Главный модуль приложения VaccinePro (SQLite)
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date
from db_config import get_session
from repository import (
    PatientRepository, VaccineRepository, ProcedureRepository,
    VaccinationRepository, MedicalRecordRepository
)

# ---------- Окно авторизации (упрощённая) ----------
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Авторизация - VaccinePro")
        self.root.geometry("300x200")
        self.root.resizable(False, False)

        tk.Label(root, text="Логин:").pack(pady=5)
        self.entry_login = tk.Entry(root)
        self.entry_login.pack(pady=5)

        tk.Label(root, text="Пароль:").pack(pady=5)
        self.entry_password = tk.Entry(root, show="*")
        self.entry_password.pack(pady=5)

        tk.Button(root, text="Войти", command=self.login).pack(pady=20)

    def login(self):
        login = self.entry_login.get()
        password = self.entry_password.get()
        # Фиксированные роли для демонстрации
        if login == "admin" and password == "admin123":
            role = "admin"
        elif login == "nurse" and password == "nurse123":
            role = "nurse"
        elif login == "doctor" and password == "doctor123":
            role = "doctor"
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")
            return

        self.root.destroy()
        root_main = tk.Tk()
        app = MainApp(root_main, role)
        root_main.mainloop()

# ---------- Главное приложение ----------
class MainApp:
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.root.title(f"VaccinePro - {role.capitalize()}")
        self.root.geometry("900x600")

        # Меню
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        patient_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Пациенты", menu=patient_menu)
        patient_menu.add_command(label="Список пациентов", command=self.show_patients)
        patient_menu.add_command(label="Добавить пациента", command=self.add_patient)

        vacc_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вакцинация", menu=vacc_menu)
        vacc_menu.add_command(label="Зарегистрировать вакцинацию", command=self.add_vaccination)
        vacc_menu.add_command(label="История вакцинаций", command=self.show_vaccinations)

        proc_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Медпроцедуры", menu=proc_menu)
        proc_menu.add_command(label="Добавить запись о процедуре", command=self.add_medical_record)
        proc_menu.add_command(label="История процедур", command=self.show_medical_records)

        report_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Отчёты", menu=report_menu)
        report_menu.add_command(label="Пациенты, требующие ревакцинации", command=self.show_revaccination_report)

        self.status = tk.Label(root, text="Готов", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(self.main_frame, text=f"Добро пожаловать, {role}!", font=("Arial", 16)).pack(pady=50)
        tk.Label(self.main_frame, text="Используйте меню для работы с системой.").pack()

    def set_status(self, msg):
        self.status.config(text=msg)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ---------- Пациенты ----------
    def show_patients(self):
        self.clear_frame()
        session = get_session()
        patients = PatientRepository.get_all(session)
        session.close()

        frame = self.main_frame
        tk.Label(frame, text="Список пациентов", font=("Arial", 14)).pack(pady=5)

        columns = ('ID', 'ФИО', 'Дата рождения', 'Телефон', 'СНИЛС')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
        for p in patients:
            tree.insert('', tk.END, values=(p.id, p.full_name, p.birth_date, p.phone, p.snils))
        tree.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=5)

        def edit_patient():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Внимание", "Выберите пациента")
                return
            patient_id = tree.item(selected[0])['values'][0]
            self.edit_patient_form(patient_id)

        def delete_patient():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Внимание", "Выберите пациента")
                return
            patient_id = tree.item(selected[0])['values'][0]
            if messagebox.askyesno("Удаление", "Удалить пациента и все его записи?"):
                session = get_session()
                PatientRepository.delete(session, patient_id)
                session.close()
                self.show_patients()
                self.set_status("Пациент удалён")

        tk.Button(btn_frame, text="Редактировать", command=edit_patient).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=delete_patient).pack(side=tk.LEFT, padx=5)

    def add_patient(self):
        self.clear_frame()
        frame = self.main_frame
        tk.Label(frame, text="Добавление пациента", font=("Arial", 14)).pack(pady=5)

        tk.Label(frame, text="ФИО:").pack()
        entry_name = tk.Entry(frame, width=50)
        entry_name.pack(pady=2)

        tk.Label(frame, text="Дата рождения (ГГГГ-ММ-ДД):").pack()
        entry_birth = tk.Entry(frame, width=20)
        entry_birth.pack(pady=2)

        tk.Label(frame, text="Телефон:").pack()
        entry_phone = tk.Entry(frame, width=30)
        entry_phone.pack(pady=2)

        tk.Label(frame, text="СНИЛС:").pack()
        entry_snils = tk.Entry(frame, width=20)
        entry_snils.pack(pady=2)

        def save():
            name = entry_name.get().strip()
            birth_str = entry_birth.get().strip()
            phone = entry_phone.get().strip()
            snils = entry_snils.get().strip()
            if not name or not birth_str:
                messagebox.showerror("Ошибка", "ФИО и дата рождения обязательны")
                return
            try:
                birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            except:
                messagebox.showerror("Ошибка", "Неверный формат даты")
                return
            session = get_session()
            PatientRepository.add(session, name, birth_date, phone, snils)
            session.close()
            self.set_status("Пациент добавлен")
            self.show_patients()

        tk.Button(frame, text="Сохранить", command=save).pack(pady=10)

    def edit_patient_form(self, patient_id):
        session = get_session()
        patient = PatientRepository.get_by_id(session, patient_id)
        session.close()
        if not patient:
            messagebox.showerror("Ошибка", "Пациент не найден")
            return

        self.clear_frame()
        frame = self.main_frame
        tk.Label(frame, text=f"Редактирование пациента ID {patient_id}", font=("Arial", 14)).pack(pady=5)

        tk.Label(frame, text="ФИО:").pack()
        entry_name = tk.Entry(frame, width=50)
        entry_name.insert(0, patient.full_name)
        entry_name.pack(pady=2)

        tk.Label(frame, text="Дата рождения (ГГГГ-ММ-ДД):").pack()
        entry_birth = tk.Entry(frame, width=20)
        entry_birth.insert(0, patient.birth_date.isoformat())
        entry_birth.pack(pady=2)

        tk.Label(frame, text="Телефон:").pack()
        entry_phone = tk.Entry(frame, width=30)
        entry_phone.insert(0, patient.phone or "")
        entry_phone.pack(pady=2)

        tk.Label(frame, text="СНИЛС:").pack()
        entry_snils = tk.Entry(frame, width=20)
        entry_snils.insert(0, patient.snils or "")
        entry_snils.pack(pady=2)

        def save():
            name = entry_name.get().strip()
            birth_str = entry_birth.get().strip()
            phone = entry_phone.get().strip()
            snils = entry_snils.get().strip()
            if not name or not birth_str:
                messagebox.showerror("Ошибка", "ФИО и дата рождения обязательны")
                return
            try:
                birth_date = datetime.strptime(birth_str, "%Y-%m-%d").date()
            except:
                messagebox.showerror("Ошибка", "Неверный формат даты")
                return
            session = get_session()
            PatientRepository.update(session, patient_id,
                                      full_name=name, birth_date=birth_date,
                                      phone=phone, snils=snils)
            session.close()
            self.set_status("Данные обновлены")
            self.show_patients()

        tk.Button(frame, text="Сохранить", command=save).pack(pady=10)

    # ---------- Вакцинация ----------
    def add_vaccination(self):
        self.clear_frame()
        frame = self.main_frame
        tk.Label(frame, text="Регистрация вакцинации", font=("Arial", 14)).pack(pady=5)

        session = get_session()
        patients = PatientRepository.get_all(session)
        vaccines = VaccineRepository.get_all(session)
        session.close()

        if not patients:
            messagebox.showerror("Ошибка", "Нет пациентов. Сначала добавьте пациента.")
            return
        if not vaccines:
            messagebox.showerror("Ошибка", "Нет вакцин. Запустите init_db.py для создания справочников.")
            return

        patient_names = {f"{p.id} - {p.full_name}": p.id for p in patients}
        vaccine_names = {f"{v.id} - {v.name}": v.id for v in vaccines}

        tk.Label(frame, text="Пациент:").pack()
        combo_patient = ttk.Combobox(frame, values=list(patient_names.keys()), width=50)
        combo_patient.pack(pady=2)

        tk.Label(frame, text="Вакцина:").pack()
        combo_vaccine = ttk.Combobox(frame, values=list(vaccine_names.keys()), width=50)
        combo_vaccine.pack(pady=2)

        tk.Label(frame, text="Доза (мл):").pack()
        entry_dose = tk.Entry(frame)
        entry_dose.pack(pady=2)

        tk.Label(frame, text="Серия:").pack()
        entry_series = tk.Entry(frame, width=30)
        entry_series.pack(pady=2)

        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").pack()
        entry_date = tk.Entry(frame, width=20)
        entry_date.insert(0, date.today().isoformat())
        entry_date.pack(pady=2)

        def save():
            patient_key = combo_patient.get()
            vaccine_key = combo_vaccine.get()
            dose_str = entry_dose.get().strip()
            series = entry_series.get().strip()
            date_str = entry_date.get().strip()
            if not patient_key or not vaccine_key or not dose_str or not date_str:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            try:
                dose = float(dose_str)
                if dose <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Ошибка", "Доза должна быть положительным числом")
                return
            try:
                date_val = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                messagebox.showerror("Ошибка", "Неверный формат даты")
                return
            patient_id = patient_names[patient_key]
            vaccine_id = vaccine_names[vaccine_key]
            session = get_session()
            VaccinationRepository.add(session, patient_id, vaccine_id, dose, series, date_val)
            session.close()
            self.set_status("Вакцинация добавлена")
            messagebox.showinfo("Успех", "Вакцинация зарегистрирована")

        tk.Button(frame, text="Сохранить", command=save).pack(pady=10)

    def show_vaccinations(self):
        patient_id = self.select_patient()
        if patient_id is None:
            return
        session = get_session()
        vaccinations = VaccinationRepository.get_by_patient(session, patient_id)
        session.close()

        self.clear_frame()
        frame = self.main_frame
        tk.Label(frame, text=f"История вакцинаций пациента ID {patient_id}", font=("Arial", 14)).pack(pady=5)

        if not vaccinations:
            tk.Label(frame, text="Нет записей о вакцинации").pack()
            return

        columns = ('ID', 'Вакцина', 'Доза', 'Серия', 'Дата')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
        for v in vaccinations:
            tree.insert('', tk.END, values=(v.id, v.vaccine.name, v.dose, v.series, v.date))
        tree.pack(fill=tk.BOTH, expand=True, pady=5)

    # ---------- Медицинские процедуры ----------
    def add_medical_record(self):
        self.clear_frame()
        frame = self.main_frame
        tk.Label(frame, text="Добавление медицинской процедуры", font=("Arial", 14)).pack(pady=5)

        session = get_session()
        patients = PatientRepository.get_all(session)
        procedures = ProcedureRepository.get_all(session)
        session.close()

        if not patients or not procedures:
            messagebox.showerror("Ошибка", "Нет пациентов или процедур. Добавьте их сначала.")
            return

        patient_names = {f"{p.id} - {p.full_name}": p.id for p in patients}
        procedure_names = {f"{pr.id} - {pr.name}": pr.id for pr in procedures}

        tk.Label(frame, text="Пациент:").pack()
        combo_patient = ttk.Combobox(frame, values=list(patient_names.keys()), width=50)
        combo_patient.pack(pady=2)

        tk.Label(frame, text="Процедура:").pack()
        combo_proc = ttk.Combobox(frame, values=list(procedure_names.keys()), width=50)
        combo_proc.pack(pady=2)

        tk.Label(frame, text="Врач:").pack()
        entry_doctor = tk.Entry(frame, width=50)
        entry_doctor.pack(pady=2)

        tk.Label(frame, text="Диагноз:").pack()
        entry_diagnosis = tk.Entry(frame, width=50)
        entry_diagnosis.pack(pady=2)

        tk.Label(frame, text="Дата (ГГГГ-ММ-ДД):").pack()
        entry_date = tk.Entry(frame, width=20)
        entry_date.insert(0, date.today().isoformat())
        entry_date.pack(pady=2)

        def save():
            patient_key = combo_patient.get()
            proc_key = combo_proc.get()
            doctor = entry_doctor.get().strip()
            diagnosis = entry_diagnosis.get().strip()
            date_str = entry_date.get().strip()
            if not patient_key or not proc_key or not doctor or not date_str:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return
            try:
                date_val = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                messagebox.showerror("Ошибка", "Неверный формат даты")
                return
            patient_id = patient_names[patient_key]
            proc_id = procedure_names[proc_key]
            session = get_session()
            MedicalRecordRepository.add(session, patient_id, proc_id, doctor, diagnosis, date_val)
            session.close()
            self.set_status("Запись добавлена")
            messagebox.showinfo("Успех", "Медицинская процедура добавлена")

        tk.Button(frame, text="Сохранить", command=save).pack(pady=10)

    def show_medical_records(self):
        patient_id = self.select_patient()
        if patient_id is None:
            return
        session = get_session()
        records = MedicalRecordRepository.get_by_patient(session, patient_id)
        session.close()

        self.clear_frame()
        frame = self.main_frame
        tk.Label(frame, text=f"История процедур пациента ID {patient_id}", font=("Arial", 14)).pack(pady=5)

        if not records:
            tk.Label(frame, text="Нет записей о процедурах").pack()
            return

        columns = ('ID', 'Процедура', 'Врач', 'Диагноз', 'Дата')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
        for r in records:
            tree.insert('', tk.END, values=(r.id, r.procedure.name, r.doctor_name, r.diagnosis, r.date))
        tree.pack(fill=tk.BOTH, expand=True, pady=5)

    # ---------- Вспомогательные ----------
    def select_patient(self):
        session = get_session()
        patients = PatientRepository.get_all(session)
        session.close()
        if not patients:
            messagebox.showerror("Ошибка", "Нет пациентов")
            return None
        patient_names = {f"{p.id} - {p.full_name}": p.id for p in patients}
        choice = simpledialog.askstring("Выбор пациента", "Введите ID или имя пациента (из списка):\n" + "\n".join(patient_names.keys()))
        if not choice:
            return None
        for key, pid in patient_names.items():
            if choice.strip() in key:
                return pid
        messagebox.showerror("Ошибка", "Пациент не найден")
        return None

    # ---------- Отчёт "Ревакцинация" ----------
    def show_revaccination_report(self):
        self.clear_frame()
        frame = self.main_frame
        tk.Label(frame, text="Пациенты, которым нужна ревакцинация", font=("Arial", 14)).pack(pady=5)

        session = get_session()
        today = date.today()
        patients = PatientRepository.get_all(session)
        results = []
        for p in patients:
            vaccs = VaccinationRepository.get_by_patient(session, p.id)
            if vaccs:
                last = max(vaccs, key=lambda v: v.date)
                vaccine = last.vaccine
                next_date = last.date + timedelta(days=vaccine.min_interval_days)
                if next_date <= today:
                    results.append((p.full_name, last.vaccine.name, last.date, next_date))
        session.close()

        if not results:
            tk.Label(frame, text="Все пациенты вакцинированы в срок, ревакцинация не требуется.").pack()
            return

        columns = ('Пациент', 'Последняя вакцина', 'Дата', 'Рекомендуемая дата')
        tree = ttk.Treeview(frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
        for row in results:
            tree.insert('', tk.END, values=row)
        tree.pack(fill=tk.BOTH, expand=True, pady=5)

# ---------- Запуск ----------
if __name__ == "__main__":
    root = tk.Tk()
    login = LoginWindow(root)
    root.mainloop()