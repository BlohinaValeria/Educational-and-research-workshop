import sqlite3
from contextlib import contextmanager


class Database:
    """Класс для управления подключением к SQLite и выполнения запросов."""

    def __init__(self, db_name="students.db"):
        self.db_name = db_name

    @contextmanager
    def connection(self):
        """Контекстный менеджер для автоматического закрытия соединения."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Доступ по имени колонки
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def execute_query(self, query, params=()):
        """Выполнение одного запроса без возврата данных (INSERT, UPDATE, DELETE)."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid

    def execute_multiple(self, queries):
        """Выполнение нескольких SQL-запросов."""
        with self.connection() as conn:
            cursor = conn.cursor()
            for query in queries:
                if query.strip():
                    cursor.execute(query)

    def fetch_all(self, query, params=()):
        """Получение всех строк результата запроса."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetch_one(self, query, params=()):
        """Получение одной строки."""
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()