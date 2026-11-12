from typing import Dict, List

from utils.exceptions import NotFoundUrlInStorage, RegistryUrlException
from utils.logger import get_logger

logger = get_logger(__name__)


class URLManager:
    """Класс для хранения и обработки URL-адресов. Позволяет получать адрес по имени и пробрасывать параметры"""

    def __init__(self, base_url: str, name: str = "URLManager"):
        self.base_url = base_url.rstrip("/")
        self.name = name
        self._url_storage: Dict[str, str] = {}
        self._registry_errors: List[str] = []

    def _add_error(self, error: str):
        logger.warning(error)
        self._registry_errors.append(error)

    def add_url(self, url_title: str, path: str = None, url: str = None):
        """
        Добавление URL-адреса в хранилище
        :param url_title: название URL
        :param path: путь от базового URL-адреса
        :param url: абсолютный URL
        """
        url_title = url_title.upper()
        if not url and path:
            url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}" if path else self.base_url
        if not url:
            self._add_error(f"Невозможно добавить URL с именем <{url_title}>: "
                            f"отсутствуют обязательные параметры url или path")
            return
        if url_title in self._url_storage:
            self._add_error("Название URL должно быть уникальным!\n"
                            f"Найден URL с названием: {url_title} -> {self._url_storage[url_title]}")
            return
        self._url_storage[url_title] = url
        logger.debug(f"[{self.name}] Добавлен URL: {url_title} -> {url}")

    def get(self, url_title: str, **kwargs):
        """Возвращает URL по имени с подстановкой параметров"""
        url_title = url_title.upper()
        if url_title not in self._url_storage:
            raise NotFoundUrlInStorage(f"URL-адрес не найден в каталоге по имени '{url_title}'")
        try:
            return self._url_storage[url_title].format(**kwargs)
        except KeyError as e:
            raise KeyError(f"В шаблоне URL '{url_title}' отсутствует параметр {e}. "
                           f"Шаблон: {self._url_storage[url_title]}. Переданы: {list(kwargs.keys())}")

    def registry_urls(self, urls: List[Dict]):
        """Регистрация список URL-адресов в формате словарей [{'ИМЯ': {'path': '/login'}}, ...]"""
        self._registry_errors = []
        logger.debug(f"[{self.name}] Идёт регистрация URL-адресов: кол-во {len(urls)}")
        for row in urls:
            for url_title, item in row.items():
                if isinstance(item, dict):
                    self.add_url(url_title=url_title, **item)
                else:
                    self._add_error(
                        f"Невозможно добавить URL с именем <{url_title}>: "
                        f"некорректные параметры URL - {item}")
        if self._registry_errors:
            raise RegistryUrlException("\n".join(self._registry_errors))
