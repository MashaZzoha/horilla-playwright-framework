import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from utils.logger import get_logger

logger = get_logger(__name__)


class PostgreSQLProvider:
    """Провайдер для работы с БД PostgreSQL"""

    def __init__(self, host: str, port: int, dbname: str, user: str, password: str):
        self.connection_str = f"host={host} port={port} dbname={dbname} user={user} password={password}"
        logger.debug(f"Connection string: {self.connection_str}")
        self.conn = None
        self.cursor = None

    @property
    def get_cursor(self):
        if not self.cursor or self.cursor.closed:
            self.connect()
        return self.cursor

    def connect(self):
        if self.conn:
            self.close()
        self.conn = psycopg2.connect(self.connection_str)
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.conn.cursor()
        logger.debug("Установлено соединение с PostgreSQL")
        return self

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
        except Exception as e:
            logger.error(f"Ошибка закрытия cursor: {e}")
        finally:
            self.cursor = None
        try:
            if self.conn:
                self.conn.close()
        except Exception as e:
            logger.error(f"Ошибка закрытия connection: {e}")
        finally:
            self.conn = None
        logger.debug("Соединение с PostgreSQL остановлено")

    def _row_to_dict_list(self):
        if not self.get_cursor.description:
            return []
        columns = [i[0].upper() for i in self.get_cursor.description]
        return [dict(zip(columns, row)) for row in self.get_cursor]

    def execute(self, query: str, params: tuple = None):
        """Выполнить SQL и вернуть список словарей (результат SELECT)"""
        logger.debug(f"SQL: {query} | params: {params}")
        self.get_cursor.execute(query, params)
        result = self._row_to_dict_list()
        logger.debug(f"Количество записей от БД: {result}")
        return result

    def fetch_one(self):
        """Вернуть одну строку или {}"""
        row = self.get_cursor.fetchone()
        if row and self.get_cursor.description:
            columns = [i[0].upper() for i in self.get_cursor.description]
            return dict(zip(columns, row))
        return {}

    def fetch_many(self, limit: int = 1000):
        """Вернуть количество строк до указанного ограничения (limit)"""
        rows = self.get_cursor.fetchmany()
        if rows and self.get_cursor.description:
            columns = [i[0].upper() for i in self.get_cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []

    def commit(self):
        """Зафиксировать изменения (если ISOLATION_LEVEL_AUTOCOMMIT не нужен)"""
        self.conn.commit()
        logger.debug("Transaction committed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self
