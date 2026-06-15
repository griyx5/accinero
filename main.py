import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from database_sqlite import SessionLocal, ReleaseCRUD, Release, User, DownloadStat
from database_sqlite import init_db, seed_test_data
init_db()
seed_test_data()
# ------------------------- ОКНО ЛОГИНА -------------------------
class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Sevilia - Login")
        self.window.geometry("400x500")
        self.window.configure(bg="#2b2b2b")

        tk.Label(self.window, text="LOG IN", font=("Arial", 24, "bold"), fg="white", bg="#2b2b2b").pack(pady=40)

        tk.Label(self.window, text="Enter email or username", font=("Arial", 10), fg="gray", bg="#2b2b2b").pack(anchor="w", padx=50)
        self.entry_user = tk.Entry(self.window, font=("Arial", 14), bd=0, relief="flat")
        self.entry_user.pack(fill="x", padx=50, pady=5)
        self.entry_user.insert(0, "admin")

        tk.Label(self.window, text="Enter password", font=("Arial", 10), fg="gray", bg="#2b2b2b").pack(anchor="w", padx=50, pady=(20,0))
        self.entry_pass = tk.Entry(self.window, font=("Arial", 14), show="*", bd=0, relief="flat")
        self.entry_pass.pack(fill="x", padx=50, pady=5)
        self.entry_pass.insert(0, "admin123")

        tk.Button(self.window, text="Enter", command=self.check_login, font=("Arial", 12), bg="#4c9aff", fg="white", bd=0, padx=20, pady=8).pack(pady=30)

        create_lbl = tk.Label(self.window, text="Create Account", font=("Arial", 10), fg="#4c9aff", bg="#2b2b2b", cursor="hand2")
        create_lbl.pack()
        create_lbl.bind("<Button-1>", lambda e: messagebox.showinfo("Info", "Demo: используйте admin/admin123"))

        tk.Button(self.window, text="Google", font=("Arial", 10), bg="#dd4b39", fg="white", bd=0, padx=20, pady=5).pack(pady=10)

        self.window.mainloop()

    def check_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()
        with SessionLocal() as session:
            user = session.query(User).filter_by(username=username).first()
            if user and user.password_hash == password:
                messagebox.showinfo("Успех", f"Добро пожаловать, {username}!")
                self.window.destroy()
                MainWindow()
            else:
                messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")

# ------------------------- ГЛАВНОЕ ОКНО -------------------------
class MainWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Sevilia - Python Community Stats")
        self.window.geometry("800x600")
        self.window.configure(bg="#f0f0f0")

        tk.Label(self.window, text="python™", font=("Arial", 48, "bold"), fg="#4c9aff", bg="#f0f0f0").pack(pady=20)
        slogan = tk.Label(self.window, text="Billions of users around the world start using it right now\nby becoming part of the community",
                          font=("Arial", 12), justify="center", bg="#f0f0f0")
        slogan.pack(pady=10)

        tk.Button(self.window, text="Start using it right now!", command=self.go_to_releases, font=("Arial", 12),
                  bg="#4c9aff", fg="white", bd=0, padx=20, pady=8).pack(pady=20)

        self.frame_stats = tk.Frame(self.window, bg="#f0f0f0")
        self.frame_stats.pack(pady=30)
        self.update_stats()

        tk.Button(self.window, text="Manage Python Releases", command=self.go_to_releases, font=("Arial", 10),
                  bg="#333", fg="white", bd=0, padx=15, pady=5).pack()

        self.window.mainloop()

    def update_stats(self):
        for widget in self.frame_stats.winfo_children():
            widget.destroy()

        with SessionLocal() as session:
            releases_count = session.query(Release).count()
            total_downloads = session.query(DownloadStat).with_entities(DownloadStat.count).all()
            total_downloads = sum(d[0] for d in total_downloads) if total_downloads else 10000000
            import random
            online = random.randint(200000, 300000)

        stats = [
            ("Users online", f"{online:,}", "#4c9aff"),
            ("Downloaded", f"{total_downloads:,} mln+", "#4c9aff"),
            ("Files created", f"{releases_count * 200:,}", "#4c9aff")
        ]
        for title, value, color in stats:
            frame = tk.Frame(self.frame_stats, bg="#ffffff", relief="ridge", bd=1)
            frame.pack(side="left", padx=20, ipadx=20, ipady=10)
            tk.Label(frame, text=title, font=("Arial", 10), fg="gray", bg="#ffffff").pack()
            tk.Label(frame, text=value, font=("Arial", 24, "bold"), fg=color, bg="#ffffff").pack()

    def go_to_releases(self):
        self.window.destroy()
        ReleasesWindow()

# ------------------------- ОКНО ТАБЛИЦЫ РЕЛИЗОВ (CRUD) -------------------------
class ReleasesWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Sevilia - Active Python Releases")
        self.window.geometry("800x500")
        self.window.configure(bg="#f0f0f0")

        tk.Label(self.window, text="Active Python Releases", font=("Arial", 18, "bold"), bg="#f0f0f0").pack(pady=10)
        tk.Label(self.window, text="For more information visit the Python Developer's Guide.", font=("Arial", 10), bg="#f0f0f0").pack()

        columns = ("version", "status", "first_released")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings", height=12)
        self.tree.heading("version", text="Python version")
        self.tree.heading("status", text="Maintenance status")
        self.tree.heading("first_released", text="First released")
        self.tree.column("version", width=120)
        self.tree.column("status", width=180)
        self.tree.column("first_released", width=120)
        self.tree.pack(pady=10, fill="both", expand=True)

        frame_btns = tk.Frame(self.window, bg="#f0f0f0")
        frame_btns.pack(pady=10)
        tk.Button(frame_btns, text="Добавить", command=self.add_release, bg="#4c9aff", fg="white", padx=10).pack(side="left", padx=10)
        tk.Button(frame_btns, text="Редактировать", command=self.edit_release, bg="#ffa500", fg="white", padx=10).pack(side="left", padx=10)
        tk.Button(frame_btns, text="Удалить", command=self.delete_release, bg="#dc3545", fg="white", padx=10).pack(side="left", padx=10)
        tk.Button(frame_btns, text="Обновить", command=self.load_data, bg="#28a745", fg="white", padx=10).pack(side="left", padx=10)
        tk.Button(frame_btns, text="На главную", command=self.back_to_main, bg="#333", fg="white", padx=10).pack(side="left", padx=10)

        self.load_data()
        self.window.mainloop()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        with SessionLocal() as session:
            releases = ReleaseCRUD.get_all(session)
            for rel in releases:
                self.tree.insert("", "end", values=(rel.version, rel.status, rel.first_released))

    def add_release(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Добавить релиз")
        dialog.geometry("300x250")
        dialog.grab_set()

        tk.Label(dialog, text="Версия (например, 3.15)").pack(pady=5)
        version_entry = tk.Entry(dialog)
        version_entry.pack()

        tk.Label(dialog, text="Статус (pre-release/bugfix/security)").pack(pady=5)
        status_entry = tk.Entry(dialog)
        status_entry.pack()

        tk.Label(dialog, text="Дата (ГГГГ-ММ-ДД)").pack(pady=5)
        date_entry = tk.Entry(dialog)
        date_entry.pack()

        def save():
            try:
                with SessionLocal() as session:
                    ReleaseCRUD.create(session, version_entry.get(), status_entry.get(), date.fromisoformat(date_entry.get()))
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        tk.Button(dialog, text="Сохранить", command=save).pack(pady=15)

    def edit_release(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для редактирования")
            return
        item = self.tree.item(selected[0])
        old_version = item['values'][0]
        old_status = item['values'][1]
        old_date = item['values'][2]

        dialog = tk.Toplevel(self.window)
        dialog.title("Редактировать релиз")
        dialog.geometry("300x250")
        dialog.grab_set()

        tk.Label(dialog, text="Версия").pack()
        version_entry = tk.Entry(dialog)
        version_entry.insert(0, old_version)
        version_entry.pack()

        tk.Label(dialog, text="Статус").pack()
        status_entry = tk.Entry(dialog)
        status_entry.insert(0, old_status)
        status_entry.pack()

        tk.Label(dialog, text="Дата (ГГГГ-ММ-ДД)").pack()
        date_entry = tk.Entry(dialog)
        date_entry.insert(0, str(old_date))
        date_entry.pack()

        def update():
            try:
                with SessionLocal() as session:
                    rel = session.query(Release).filter_by(version=old_version).first()
                    if rel:
                        rel.version = version_entry.get()
                        rel.status = status_entry.get()
                        rel.first_released = date.fromisoformat(date_entry.get())
                        session.commit()
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        tk.Button(dialog, text="Обновить", command=update).pack(pady=15)

    def delete_release(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите запись для удаления")
            return
        if messagebox.askyesno("Подтверждение", "Удалить выбранную версию?"):
            version = self.tree.item(selected[0])['values'][0]
            with SessionLocal() as session:
                rel = session.query(Release).filter_by(version=version).first()
                if rel:
                    session.delete(rel)
                    session.commit()
            self.load_data()

    def back_to_main(self):
        self.window.destroy()
        MainWindow()

# ------------------------- ЗАПУСК -------------------------
if __name__ == "__main__":
    LoginWindow()