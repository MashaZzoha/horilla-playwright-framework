import json
from json import JSONEncoder

from utils.logger import get_logger

logger = get_logger(__name__)


class TestDataJSONEncoder(JSONEncoder):
    def default(self, obj):
        return obj.to_json()


class TestDataKeeper(object):
    """Класс-хранитель тестовых данных"""
    def __init__(self):
        self._data = {}
        logger.info(f'Инициализирован хранитель тестовых данных: {self}')

    @classmethod
    def create(cls, **test_data):
        """
        Создание хранителя тестовых данных с начальным набором тестовых данных
        :param test_data: тестовые данные
        :return: TestDataKeeper
        """
        test_data_keeper = cls()
        test_data_keeper._data = test_data
        return test_data_keeper

    def __getattr__(self, key):
        """
        Получить тестовые данные
        :param key: имя атрибута для получения тестовых данных
        :return: тестовые данные
        """
        logger.debug(f'Получить значение атрибута тестовых данных: {key}')
        return self._data.get(key, None)

    def __setattr__(self, key, value):
        """
        Записать тестовые данные
        :param key: имя атрибута
        :param value: значение
        """
        if key == '_data':
            self.__dict__[key] = value
        elif key in self._data:
            self._data[key] = value
            logger.debug(f'Обновлено значение атрибута тестовых данных: {key}')
        else:
            self._data[key] = value
            logger.debug(f'Добавлен новый атрибут тестовых данных: {key}')

    def __delattr__(self, key):
        """
        Удалить атрибут
        :param key: имя атрибута
        """
        if key in self._data:
            del self._data[key]
            logger.debug(f'Удален атрибут тестовых данных: {key}')
        else:
            logger.debug(f'Не найден атрибут тестовых данных: {key} - нечего удалять!')

    def __str__(self):
        """Строковое представление TestDataKeeper"""
        return json.dumps(self._data, ensure_ascii=False, cls=TestDataJSONEncoder, default=str, indent=4)

    def remove(self):
        """Удалить тестовые данные"""
        self._data = {}
        logger.debug('Все тестовые данные удалены')
