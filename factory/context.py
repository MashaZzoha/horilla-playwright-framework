from time import sleep
from typing import Type

from playwright.sync_api import Page

from config.settings import PROJECT_ROOT, settings
from factory.base_pages_store import BasePagesStore
from factory.queries.horilla_db import HorillaQueries
from factory.url_manager import URLManager
from factory.yaml_locator_loader import YamlLocatorsLoader
from utils.allure_utils import attach_screenshot, step
from utils.exceptions import (UnknownConfigException, UnknownDbException,
                              UnsupportedStorePages, UnsupportedUrlManager)
from utils.logger import get_logger
from utils.postgresql_provider import PostgreSQLProvider

logger = get_logger(__name__)


def retry(func):
    """Повторный вызов метода при ошибках подключения к БД (3 попытки)"""

    def decorator(*args, **kwargs):
        attempts = 3
        delay = 5
        while attempts > 0:
            attempts -= 1
            try:
                return func(*args, **kwargs)
            except UnknownDbException as e:
                if attempts == 0:
                    raise e
                sleep(delay)

    return decorator


class Context:
    """Класс web-контекст. Реализует контекст для работы с браузером."""

    def __init__(self, browser_page: Page, store_pages: Type[BasePagesStore], url_manager: URLManager):
        self.browser_page = browser_page
        self.yaml_locator_loader = YamlLocatorsLoader(self.browser_page, PROJECT_ROOT, 'locators')
        self._store_pages = None
        self._url_manager = None
        if store_pages:
            self.set_store_pages(store_pages)
        if url_manager:
            self.set_url_manager(url_manager)
        self._db_registry = {}
        self._check = None
        self._pages = None

    def __getattr__(self, name):
        """Передаёт методы Pages, не ломая property pages."""
        if name.startswith("_"):
            raise AttributeError(name)
        # обход рекурсии
        pages = object.__getattribute__(self, "_pages")
        if pages is None:
            from factory.pages import Pages
            pages = Pages(self)
            object.__setattr__(self, "_pages", pages)

        return getattr(pages, name)

    @property
    def store_pages(self):
        """
        Вернуть магазин страниц
        :return: магазин страниц
        """
        return self._store_pages

    @property
    def url_manager(self):
        """
        Вернуть URL-менеджер
        :return: URL-менеджер
        """
        return self._url_manager

    @property
    def horilla_provider(self):
        """Провайдер для работы с БД PostgreSQL horilla_db"""
        return self.get_db_provider(
            'db', db_name='horilla', provider=PostgreSQLProvider, query_storage=HorillaQueries)

    @property
    def check(self):
        """Класс проверок ответов от БД и сервисов"""
        if self._check is None:
            from checker.checker import Checker
            self._check = Checker(self)
        return self._check

    def goto(self, url_name: str, **kwargs):
        """
        Открывает страницу по URL
        :param url_name: название URL-адреса
        :param kwargs: параметры для динамического URL
        """
        url = self.url_manager.get(url_name, **kwargs)
        with step(f"Открыть по URL страницу: {url_name} - {url}"):
            self.browser_page.goto(url)
            self.browser_page.locator(".htmx-request, .htmx-settling, .htmx-swapping"
                                      ).wait_for(state="detached", timeout=5000)
        return self

    def set_store_pages(self, store_pages):
        """
        Установить новый магазин страниц для вэб-контекста
        :param store_pages: магазин страниц
        """
        if not issubclass(store_pages, BasePagesStore):
            raise UnsupportedStorePages(f"Неподдерживаемый тип магазина страниц: {store_pages}")
        self._store_pages = store_pages(self)

    def set_url_manager(self, url_manager):
        """
        Установить новый URL-менеджер для контекста
        :param url_manager: URL-менеджер
        """
        if not isinstance(url_manager, URLManager):
            raise UnsupportedUrlManager(f"Неподдерживаемый URL-менеджер: {url_manager}")
        self._url_manager = url_manager

    def get_page(self, page_name: str):
        """
        Получить объект страницы по названию
        :param page_name: название страницы
        :return: объект страницы
        """
        return self.store_pages(page_name).current_page

    def open_new_tab(self) -> Page:
        """Открыть и перейти на новую вкладку"""
        new_page = self.browser_page.context.new_page()
        self.browser_page = new_page
        self.yaml_locator_loader.page = new_page
        logger.info("Открыта новая вкладка")
        return new_page

    def close_tab(self):
        """Закрыть текущую вкладку и переключиться на оставшуюся"""
        current = self.browser_page
        ctx = current.context
        current.close()
        logger.info("Вкладка закрыта")
        remaining = ctx.pages
        if not remaining:
            raise RuntimeError("Все вкладки закрыты")
        self.browser_page = remaining[-1]
        self.yaml_locator_loader.page = self.browser_page
        logger.info(f"Переключено на вкладку: {self.browser_page.url}")
        return self

    def switch_to_tab(self, index: int) -> Page:
        """Переключиться на вкладку по индексу self.page — выбранная вкладка"""
        pages = self.browser_page.context.pages
        if index >= len(pages):
            raise IndexError(f"Вкладки с индексом {index} нет. Общее число вкладок: {len(pages)}")
        self.browser_page = pages[index]
        logger.info(f"Переключено на вкладку {index}")
        return self.browser_page

    def close_all_tabs(self):
        """Закрыть все вкладки"""
        ctx = self.browser_page.context
        for page in ctx.pages:
            page.close()
        logger.info("Все вкладки закрыты")
        return self

    def screenshot(self, name: str = 'screenshot'):
        """Делает и прикрепляет скриншот в Allure."""
        attach_screenshot(self.browser_page, name)
        return self

    @staticmethod
    def _get_item_from_config(*path, name):
        """
        Получить объект из конфига (settings)
        :param path: путь до объекта (например, "db")
        :param name: ключ объекта (например, "horilla")
        :return: объект конфига (словарь)
        """
        env = settings
        item = None
        for item in path:
            env = getattr(env, item, None) if hasattr(env, item) else env.get(item) if isinstance(env, dict) else None
        if not env:
            raise UnknownConfigException(f"Не найден конфиг: {item}")
        return env.get(name) if isinstance(env, dict) else getattr(env, name, None)

    @retry
    def get_db_provider(self, *path, db_name: str, provider, query_storage=None, **kwargs):
        """
        Получить провайдер БД по имени (кэшируется)
        :param path: путь до БД в конфиге (например, "db")
        :param db_name: имя БД
        :param provider: класс провайдера
        :param query_storage: класс запросов в БД
        :param kwargs: параметры подключения
        :return: объект провайдера
        """
        if db_name not in self._db_registry:
            env = self._get_item_from_config(*path, name=db_name)
            if not env:
                raise UnknownDbException(f"Не найден конфиг БД: {db_name}")
            self._db_registry[db_name] = provider(**dict(env)).connect()
            if query_storage:
                self._db_registry[db_name].query_storage = query_storage
        return self._db_registry[db_name]

    def close_db(self):
        """Закрыть все соединения с БД"""
        for provider in self._db_registry.values():
            provider.close()
        self._db_registry.clear()
