import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from tkinter import *
from PIL import Image, ImageTk
from art import text2art 

# Подключение к базе данных PostgreSQL
def connect_to_db(show_error=True):
    try:
        conn = psycopg2.connect(
            dbname="prac_2025",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        if show_error:
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных: {e}")
        return None


def fetch_data(table_name, condition=None):
    if not table_name.isidentifier():  # Проверка, что имя таблицы безопасно
        messagebox.showerror("Ошибка", "Недопустимое имя таблицы")
        return [], []

    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                if condition:
                    query = f"SELECT * FROM {table_name} WHERE {condition};"
                else:
                    query = f"SELECT * FROM {table_name};"
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return columns, rows
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при получении данных: {e}")
            return [], []
        finally:
            conn.close()
    return [], []

def insert_data(table_name, data):
    if not data:
        messagebox.showwarning("Предупреждение", "Нет данных для вставки")
        return

    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                columns = ", ".join(data.keys())
                values = ", ".join(["%s"] * len(data))
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
                cursor.execute(query, list(data.values()))
                conn.commit()
                messagebox.showinfo("Успех", "Данные успешно добавлены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при вставке данных: {e}")
        finally:
            conn.close()

def delete_data(table_name, id):
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                query = f"DELETE FROM {table_name} WHERE id = %s;"
                cursor.execute(query, (id,))
                conn.commit()
                messagebox.showinfo("Успех", "Данные успешно удалены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении данных: {e}")
        finally:
            conn.close()

def fetch_query(query, parameters=()):
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, parameters)
                result = cursor.fetchall()
                return result
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
            return []
        finally:
            conn.close()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Управление базой данных")
        self.geometry("1024x450")
        try:
            header_frame = tk.Frame(self)
            header_frame.pack(pady=10)

            original_image = Image.open('logo2.jpg')
            resized_image = original_image.resize((100, 100), Image.Resampling.LANCZOS)
            logo_img = ImageTk.PhotoImage(resized_image)

            logo_label = tk.Label(header_frame, image=logo_img)
            logo_label.image = logo_img
            logo_label.grid(row=0, column=1, padx=10)

            ascii_art = text2art("Practice_2025", font="standard")
            label_title = tk.Label(header_frame, text=ascii_art, font='Courier 9')
            label_title.grid(row=0, column=0, sticky="nsew")
            header_frame.columnconfigure(1, weight=1)

        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Не удалось загрузить логотип: {e}")

        self.tab_control = ttk.Notebook(self)
        self.tabs = {}
        for table in ["преподаватели", "кабинеты", "группы", "расписание"]:
            tab = ttk.Frame(self.tab_control)
            self.tabs[table] = tab
            self.tab_control.add(tab, text=table.capitalize())
            self.setup_tab(tab, table)
        self.tab_control.pack(expand=1, fill="both")

    def setup_tab(self, tab, table_name):
        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True)

        columns, rows = fetch_data(table_name)
        if not columns:
            return

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        tree.grid(row=0, column=0, sticky="nsew")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')

        for row in rows:
            tree.insert("", "end", values=row)

        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=x_scroll.set)
        x_scroll.grid(row=1, column=0, sticky="ew")

        frame_buttons = ttk.Frame(tab)
        frame_buttons.pack(pady=10)

        ttk.Button(frame_buttons, text="Добавить", command=lambda: self.show_insert_dialog(table_name, tree)).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Удалить", command=lambda: self.show_delete_dialog(table_name, tree)).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Вывести данные", command=lambda: self.show_related_data(tree, table_name)).pack(side="left", padx=5)

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        tab.tree = tree

    def show_insert_dialog(self, table_name, tree):
        dialog = tk.Toplevel(self)
        dialog.title(f"Добавить данные в {table_name}")
        entries = {}

        columns, _ = fetch_data(table_name)
        for col in columns:
            ttk.Label(dialog, text=col).pack()
            entry = ttk.Entry(dialog)
            entry.pack()
            entries[col] = entry

        ttk.Button(dialog, text="Добавить", command=lambda: self.insert_and_refresh(dialog, table_name, entries, tree)).pack(pady=10)

    def show_delete_dialog(self, table_name, tree):
        dialog = tk.Toplevel(self)
        dialog.title(f"Удалить данные из {table_name}")

        ttk.Label(dialog, text="Введите ID для удаления:").pack()
        id_entry = ttk.Entry(dialog)
        id_entry.pack()

        ttk.Button(dialog, text="Удалить", command=lambda: self.delete_and_refresh(dialog, table_name, id_entry.get(), tree)).pack(pady=10)

    def insert_and_refresh(self, dialog, table_name, entries, tree):
        data = {col: entry.get() for col, entry in entries.items()}
        insert_data(table_name, data)
        self.refresh_table(tree, table_name)
        dialog.destroy()

    def show_related_data(self, tree, table_name):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Не выбрана запись для вывода данных.")
            return

        # Вместо ID получаем название дисциплины (например, из столбца с индексом 5)
        item_id = tree.item(selected_item)["values"][4]  # Замените 4 на индекс столбца с названием дисциплины

        if table_name == "преподаватели":
            query = """
            SELECT преподаватели.фио, группы.название, кабинеты.номер
            FROM преподаватели
            JOIN группы ON преподаватели.группа_id = группы.id
            JOIN кабинеты ON преподаватели.кабинет_id = кабинеты.id
            WHERE преподаватели.id = %s;
            """
            column_names = ["ФИО", "Группа", "Кабинет"]

        elif table_name == "группы":
            query = """
            SELECT группы.название, преподаватели.фио, кабинеты.номер
            FROM группы
            JOIN преподаватели ON преподаватели.группа_id = группы.id
            JOIN кабинеты ON преподаватели.кабинет_id = кабинеты.id
            WHERE группы.id = %s;
            """
            column_names = ["Группа", "Преподаватель", "Кабинет"]

        elif table_name == "расписание":
            query = """
            SELECT 
                расписание.день, 
                расписание.пара, 
                группы.название AS группа, 
                группы.количество_студентов, 
                расписание.дисциплина, 
                преподаватели.фио AS преподаватель, 
                SUM(преподаватели.лекции_в_неделю + преподаватели.практики_в_неделю + преподаватели.лабораторные_в_неделю) AS сумма_пар, 
                кабинеты.номер AS аудитория, 
                кабинеты.описание, 
                кабинеты.вместимость, 
                кабинеты.примечания
            FROM расписание
            JOIN группы ON расписание.группа_id = группы.id
            JOIN преподаватели ON расписание.преподаватель_id = преподаватели.id
            JOIN кабинеты ON расписание.аудитория_id = кабинеты.id
            WHERE расписание.дисциплина = %s  -- Смотрим по дисциплине
            GROUP BY 
                расписание.день, 
                расписание.пара, 
                группы.название, 
                группы.количество_студентов, 
                расписание.дисциплина, 
                преподаватели.фио, 
                кабинеты.номер, 
                кабинеты.описание, 
                кабинеты.вместимость, 
                кабинеты.примечания;
            """
            column_names = ["День", "Пара", "Группа", "Студенты", "Дисциплина", "Преподаватель", "Сумма", "Аудитория", "Описание", "Вместимость", "Примечания"]

        else:
            messagebox.showerror("Ошибка", "Для этой таблицы запросы не поддерживаются.")
            return

        # Запрашиваем данные по выбранной дисциплине
        results = fetch_query(query, (item_id,))  # Передаем название дисциплины, а не ID
        if results:
            result_window = tk.Toplevel(self)
            result_window.title("Результаты запроса")
            result_window.geometry("1000x600")  # Увеличен размер окна для скроллов

            # Создаем Treeview
            result_tree = ttk.Treeview(result_window, columns=column_names, show="headings")
            result_tree.grid(row=0, column=0, sticky="nsew")

            # Горизонтальный скролл
            x_scroll = ttk.Scrollbar(result_window, orient="horizontal", command=result_tree.xview)
            x_scroll.grid(row=1, column=0, sticky="ew")

            # Вертикальный скролл
            y_scroll = ttk.Scrollbar(result_window, orient="vertical", command=result_tree.yview)
            y_scroll.grid(row=0, column=1, sticky="ns")

            # Настроим скроллы для Treeview
            result_tree.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

            for col in column_names:
                result_tree.heading(col, text=col)
                result_tree.column(col, width=150)

            for result in results:
                result_tree.insert("", "end", values=result)

            # Кнопка "Закрыть", которая будет по центру
            close_button = tk.Button(result_window, text="Закрыть", command=result_window.destroy)
            close_button.grid(row=2, column=0, pady=10, sticky="nsew")

            # Разрешим растягивать строки и колонки
            result_window.grid_rowconfigure(0, weight=1)  # Растягиваем первую строку (Treeview)
            result_window.grid_columnconfigure(0, weight=1)  # Растягиваем первую колонку (Treeview)
            result_window.grid_columnconfigure(1, weight=0)  # Для вертикального скролла
            result_window.grid_rowconfigure(1, weight=0)  # Для горизонтального скролла

        else:
            messagebox.showinfo("Результаты запроса", "Данные не найдены.")


    def delete_and_refresh(self, dialog, table_name, id, tree):
        delete_data(table_name, id)
        self.refresh_table(tree, table_name)
        dialog.destroy()

    def refresh_table(self, tree, table_name, condition=None):
        tree.delete(*tree.get_children())
        _, rows = fetch_data(table_name, condition)
        for row in rows:
            tree.insert("", "end", values=row)

if __name__ == "__main__":
    app = App()
    app.mainloop()