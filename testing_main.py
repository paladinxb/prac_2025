import unittest
from unittest.mock import patch, MagicMock
import main
import psycopg2

class TestDatabaseFunctions(unittest.TestCase):
    @patch('main.psycopg2.connect')
    def test_connect_to_db_success(self, mock_connect):
        mock_connect.return_value = MagicMock()
        conn = main.connect_to_db()
        self.assertIsNotNone(conn)

    @patch('main.psycopg2.connect', side_effect=psycopg2.OperationalError)
    def test_connect_to_db_failure(self, mock_connect):
        conn = main.connect_to_db(show_error=False)  # Отключаем показ ошибки
        self.assertIsNone(conn)
    
    @patch('main.connect_to_db')
    def test_fetch_data(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1, 'John Doe')]
        mock_cursor.description = [('id',), ('name',)]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        columns, rows = main.fetch_data('users')
        self.assertEqual(columns, ['id', 'name'])
        self.assertEqual(rows, [(1, 'John Doe')])

    @patch('main.connect_to_db')
    def test_insert_and_delete_data(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Добавление данных
        main.insert_data('группы', {'id': 10, 'название': 'test'})
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
        print("Добавление выполнено")

        # Удаление данных (временно отключено)
        # main.delete_data('users', 1)
        # mock_cursor.execute.assert_called()
        # mock_conn.commit.assert_called()
        # print("Удаление выполнено")


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestDatabaseFunctions("test_insert_and_delete_data"))
    runner = unittest.TextTestRunner()
    runner.run(suite)