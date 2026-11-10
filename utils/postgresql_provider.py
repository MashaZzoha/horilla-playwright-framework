from functools import partial, wraps

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from utils.allure_utils import attach
from utils.logger import get_logger

logger = get_logger(__name__)


def attach_source_query(func):
    """
    Декоратор для методов HorillaQueries
    Добавляет в Allure attach с SQL-запросом
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        query = func(*args, **kwargs)
        attach('Текст запроса к БД', body=query)
        return query

    return wrapper


class PostgreSQLProvider:
    """Провайдер для работы с БД PostgreSQL"""

    def __init__(self, host: str, port: int, dbname: str, user: str, password: str):
        self.connection_str = f"host={host} port={port} dbname={dbname} user={user} password={password}"
        logger.debug(f"Connection string: {self.connection_str}")
        self.conn = None
        self.cursor = None
        self.query_storage = None

    def __getattr__(self, item):
        """Передаёт методы хранилища запросов (HorillaQueries)"""
        if item.startswith('_'):
            raise AttributeError(item)
        if self.query_storage:
            query_method = getattr(self.query_storage, item, None)
            if query_method:
                return partial(self._make_execute, query_method)
            raise AttributeError(f"Не найден метод запроса '{item}' в хранилище {self.query_storage}")
        raise TypeError("Не определено хранилище запросов. Установите provider.query_storage (HorillaQueries)")

    def _make_execute(self, query, *args, **kwargs):
        """Собрать SQL из метода хранилища и выполнить через execute"""
        params = kwargs.pop('params', None)
        q = query(*args, **kwargs)
        if isinstance(q, tuple):
            return self.execute(*q, params=params)
        return self.execute(q, params=params)

    @property
    def get_cursor(self):
        """Вернуть активный курсор (создаёт соединение, если его нет)"""
        if not self.cursor or self.cursor.closed:
            self.connect()
        return self.cursor

    def connect(self):
        """Установить соединение с PostgreSQL и создать курсор"""
        if self.conn:
            self.close()
        self.conn = psycopg2.connect(self.connection_str)
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.conn.cursor()
        logger.debug("Установлено соединение с PostgreSQL")
        return self

    def close(self):
        """Закрыть курсор и соединение с PostgreSQL"""
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
        """Преобразовать текущий результат курсора в список словарей (ключи — имена колонок)"""
        if not self.get_cursor.description:
            return []
        columns = [i[0].upper() for i in self.get_cursor.description]
        return [dict(zip(columns, row)) for row in self.get_cursor]

    def execute(self, query: str, params: tuple = None):
        """
        Выполнить SQL и вернуть список словарей (результат SELECT)
        :param query: SQL-запрос
        :param params: параметры запроса (для передачи значений в запрос)
        :return: строки результата в формате списка словарей
        """
        logger.debug(f"SQL: {query} | params: {params}")
        self.get_cursor.execute(query, params)
        result = self._row_to_dict_list()
        logger.debug(f"Количество записей от БД: {len(result)}")
        return result

    def fetch_one(self):
        """Вернуть одну строку результата или {} если БД не вернула результат"""
        row = self.get_cursor.fetchone()
        if row and self.get_cursor.description:
            columns = [i[0].upper() for i in self.get_cursor.description]
            return dict(zip(columns, row))
        return {}

    def fetch_many(self, limit: int = 1000):
        """
        Вернуть количество строк до указанного ограничения (limit)
        :param limit: максимальное количество строк
        :return: строки результата в формате списка словарей
        """
        rows = self.get_cursor.fetchmany(limit)
        if rows and self.get_cursor.description:
            columns = [i[0].upper() for i in self.get_cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []

    def commit(self):
        """Зафиксировать изменения (если ISOLATION_LEVEL_AUTOCOMMIT не нужен)"""
        self.conn.commit()
        logger.debug("Transaction committed")

    def __enter__(self):
        """Контекстный менеджер: вход (возвращает провайдер)"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер: выход (закрывает соединение)"""
        return self
