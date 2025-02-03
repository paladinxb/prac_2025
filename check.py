import unittest
import main  # Убеждаемся, что импортируем реальный модуль

class TestDatabaseFunctions(unittest.TestCase):
    def test_insert_data_real_db(self):
        """Тестируем реальную вставку данных в PostgreSQL"""
        main.insert_data('группы', {'id': 10, 'название': 'test', 'количество_студентов': '20'})
        print("Данные успешно добавлены. Проверьте таблицу 'группы' в БД.")
        # Удаление данных (временно отключено)
        main.delete_data('группы', 10)
        print("Удаление выполнено")

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestDatabaseFunctions("test_insert_data_real_db"))
    runner = unittest.TextTestRunner()
    runner.run(suite)