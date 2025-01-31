import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import psycopg2
from PIL import Image, ImageTk

# Конфигурация подключения к базе данных (оставляется без изменений)
def connect_db():
    return psycopg2.connect(
        dbname="prac_2025",
        user="postgres",  # Укажите имя пользователя
        password="1234",  # Укажите пароль
        host="localhost",  # Укажите хост (по умолчанию localhost)
        port="5432"  # Укажите порт (по умолчанию 5432)
    )

def execute_query(query, parameters=()):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query, parameters)
        conn.commit()
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
    finally:
        cursor.close()
        conn.close()

def fetch_query(query, parameters=()):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query, parameters)
        result = cursor.fetchall()
        return result
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Главное окно приложения
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Учебное заведение")
        self.geometry("800x600")

        # Логотип учебного заведения
        try:
            original_image = Image.open('logo2.jpg')
            resized_image = original_image.resize((200, 100), Image.Resampling.LANCZOS)
            logo_img = ImageTk.PhotoImage(resized_image)
            logo_label = tk.Label(self, image=logo_img)
            logo_label.image = logo_img
            logo_label.pack(pady=10)
        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Не удалось загрузить логотип: {e}")

        # Вкладки
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Вкладки для таблиц
        self.create_table_tab("Преподаватели", "преподаватели", ["id", "фио", "дисциплина", "группа_id", "лекции_в_неделю", "практики_в_неделю", "лабораторные_в_неделю", "кабинет_id"])
        self.create_table_tab("Группы", "группы", ["id", "название", "количество_студентов"])
        self.create_table_tab("Кабинеты", "кабинеты", ["id", "номер", "описание", "вместимость", "примечания"])
        self.create_table_tab("Расписание", "расписание", ["id", "день", "пара", "группа_id", "дисциплина", "преподаватель_id", "аудитория_id"])


    def create_table_tab(self, tab_name, table_name, columns):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=tab_name)

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        tree.pack(fill="both", expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Заполнение данных из базы
        self.populate_table(tree, table_name, columns)

        # Добавление кнопок для операций с записями
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)

        # Кнопка добавления
        add_button = tk.Button(button_frame, text="Добавить запись", command=lambda: self.add_record(tree, table_name, columns))
        add_button.grid(row=0, column=0, padx=10)

        # Кнопка удаления
        delete_button = tk.Button(button_frame, text="Удалить запись", command=lambda: self.delete_record(tree, table_name))
        delete_button.grid(row=0, column=1, padx=10)

        # Кнопка редактирования
        edit_button = tk.Button(button_frame, text="Редактировать запись", command=lambda: self.edit_record(tree, table_name, columns))
        edit_button.grid(row=0, column=2, padx=10)

        # Кнопка выполнения встроенного запроса
        query_button = tk.Button(button_frame, text="Вывести данные", command=lambda: self.show_related_data(tree, table_name))
        query_button.grid(row=0, column=3, padx=10)

    def show_related_data(self, tree, table_name):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Не выбрана запись для вывода данных.")
            return

        # Получаем ID выбранной записи
        item_id = tree.item(selected_item)["values"][0]

        # Определяем запрос и названия колонок в зависимости от таблицы
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
        else:
            messagebox.showerror("Ошибка", "Для этой таблицы запросы не поддерживаются.")
            return

        # Выполняем запрос и отображаем результаты
        results = fetch_query(query, (item_id,))
        if results:
            result_window = tk.Toplevel(self)
            result_window.title("Результаты запроса")
            result_window.geometry("600x400")

            # Выводим результаты в Treeview
            result_tree = ttk.Treeview(result_window, columns=column_names, show="headings")
            result_tree.pack(fill="both", expand=True)

            # Устанавливаем заголовки колонок
            for col in column_names:
                result_tree.heading(col, text=col)
                result_tree.column(col, width=150)

            # Добавляем данные в Treeview
            for result in results:
                result_tree.insert("", "end", values=result)

            close_button = tk.Button(result_window, text="Закрыть", command=result_window.destroy)
            close_button.pack(pady=10)
        else:
            messagebox.showinfo("Результаты запроса", "Данные не найдены.")


    def populate_table(self, tree, table_name, columns):
        # Очищаем текущие данные в таблице
        for item in tree.get_children():
            tree.delete(item)
        
        # Заполняем таблицу данными из базы
        query = f"SELECT * FROM {table_name};"
        records = fetch_query(query)
        for record in records:
            tree.insert("", "end", values=record)

    def add_record(self, tree, table_name, columns):
        # Диалоговое окно для ввода ID
        id_value = simpledialog.askinteger("Добавить запись", f"Введите ID для {table_name}:")
        if not id_value:
            messagebox.showwarning("Ошибка", "Не введен ID!")
            return
        
        # Диалоговое окно для ввода других значений
        values = [id_value]  # Вставляем ID в начало списка значений
        for col in columns[1:]:  # Пропускаем ID, потому что оно уже введено
            value = simpledialog.askstring("Добавить запись", f"Введите {col}:")
            if value:
                values.append(value)
            else:
                messagebox.showwarning("Ошибка", f"Не введено значение для {col}")
                return

        # Добавляем запись в базу данных
        if self.add_record_to_db(table_name, columns, values):
            # Очищаем текущие данные в таблице
            for item in tree.get_children():
                tree.delete(item)
            # Заполняем таблицу заново
            self.populate_table(tree, table_name, columns)
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить запись в базу данных.")

    def add_record_to_db(self, table_name, columns, values):
        try:
            # Приводим имена столбцов к правильному формату
            columns_str = ", ".join([f'"{col}"' for col in columns])
            placeholders = ", ".join(["%s"] * len(values))
            
            # Строим SQL запрос
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            
            # Выводим запрос в консоль для отладки
            print(f"SQL запрос: {query}")
            
            # Выполняем запрос
            execute_query(query, values)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при добавлении записи: {e}")
            return False
        
    def add_schedule_record(self, tree, table_name, columns):
        # Получаем данные
        day = simpledialog.askstring("Добавить запись", "Введите день (например, Понедельник):")
        pair = simpledialog.askinteger("Добавить запись", "Введите номер пары (1-5):")
        group_id = simpledialog.askinteger("Добавить запись", "Введите ID группы:")
        discipline = simpledialog.askstring("Добавить запись", "Введите дисциплину:")
        teacher_id = simpledialog.askinteger("Добавить запись", "Введите ID преподавателя:")
        room_id = simpledialog.askinteger("Добавить запись", "Введите ID аудитории:")

        # Проверки
        conflict_query = """
        SELECT * FROM расписание
        WHERE день = %s AND пара = %s AND (аудитория_id = %s OR преподаватель_id = %s);
        """
        conflicts = fetch_query(conflict_query, (day, pair, room_id, teacher_id))
        if conflicts:
            messagebox.showerror("Ошибка", "Конфликт: аудитория или преподаватель заняты.")
            return

        # Добавляем запись
        values = [day, pair, group_id, discipline, teacher_id, room_id]
        columns_str = ", ".join(columns[1:])  # Пропускаем ID
        placeholders = ", ".join(["%s"] * len(values))
        query = f"INSERT INTO расписание ({columns_str}) VALUES ({placeholders})"
        execute_query(query, values)
        self.populate_table(tree, table_name, columns)

    def delete_record(self, tree, table_name):
        selected_item = tree.selection()
        if selected_item:
            item_id = tree.item(selected_item)["values"][0]
            self.delete_record_from_db(table_name, item_id)
            
            # Очищаем текущие данные в таблице
            for item in tree.get_children():
                tree.delete(item)
            
            # Заполняем таблицу заново
            self.populate_table(tree, table_name, tree["columns"])
        else:
            messagebox.showwarning("Предупреждение", "Не выбрана запись для удаления.")

    def delete_record_from_db(self, table_name, record_id):
        query = f"DELETE FROM {table_name} WHERE id = %s"
        execute_query(query, (record_id,))

    def edit_record(self, tree, table_name, columns):
        selected_item = tree.selection()
        if selected_item:
            item_id = tree.item(selected_item)["values"][0]
            values = []
            for col in columns[1:]:
                new_value = simpledialog.askstring("Редактировать запись", f"Введите новое значение для {col}:")
                values.append(new_value)

            self.edit_record_in_db(table_name, item_id, columns[1:], values)
            self.populate_table(tree, table_name, columns)
        else:
            messagebox.showwarning("Предупреждение", "Не выбрана запись для редактирования.")

    def edit_record_in_db(self, table_name, record_id, columns, values):
        set_clause = ", ".join([f"{col} = %s" for col in columns])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s"
        execute_query(query, values + (record_id,))

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
