from typing import Dict, List
from exceptions import RegistryUrlException, NotFoundUrlInStorage
from utils.logger import get_logger

logger = get_logger(__name__)


class URLManager:
    """Класс для хранения и обработки URL-адресов. Позволяет получать адрес по имени и пробрасывать параметры"""
    def __init__(self, base_url: str, name: str = "URLManager"):
        self.base_url = base_url
        self.name = name
        self._url_storage: Dict[str, str] = {}
        self._registry_errors: List[str] = []

    def _add_error(self, error: str):
        logger.warning(error)
        self._registry_errors.append(error)

    def add_url(self, title: str, path: str = None, url: str = None):
        """
        Добавление URL-адреса в хранилище
        :param title: название URL
        :param path: путь от базового URL-адреса
        :param url: абсолютный URL
        """
        title = title.upper()
        if not url and path:
            url = f"{self.base_url}{path.lstrip('/')}" if path else self.base_url
        if not url:
            self._add_error(f"Невозможно добавить URL с именем <{title}>: "
                            f"отсутствуют обязательные параметры url или path")
            return
        if title in self._url_storage:
            self._add_error("Название URL должно быть уникальным!\n"
                            f"Найден URL с названием: {title} -> {self._url_storage[title]}")
            return
        self._url_storage[title] = url
        logger.debug(f"Добавлен URL: {title} -> {url}")

    def get(self, title: str, **kwargs):
        """Возвращает URL по имени с подстановкой параметров"""
        title = title.upper()
        if title not in self._url_storage:
            raise NotFoundUrlInStorage(f"URL-адрес не найден в каталоге по имени '{title}'")
        try:
            return self._url_storage[title].format(**kwargs)
        except KeyError as e:
            raise KeyError(f"В шаблоне URL '{title}' отсутствует параметр {e}. "
                           f"Шаблон: {self._url_storage[title]}. Переданы: {list(kwargs.keys())}")

    def registry_urls(self, urls: List[Dict]):
        """Регистрация список URL-адресов в формате словарей [{'ИМЯ': {'path': '/login'}}, ...]"""
        self._registry_errors = []
        logger.debug(f"[{self.name}] Идёт регистрация URL-адресов: кол-во {len(urls)}")
        for row in urls:
            for title, item in row.items():
                if isinstance(item, dict):
                    self.add_url(title=title, **item)
                else:
                    self._add_error(
                        f"Невозможно добавить URL с именем <{title}>: "
                        f"некорректные параметры URL - {item}")
        if self._registry_errors:
            raise RegistryUrlException("\n".join(self._registry_errors))
