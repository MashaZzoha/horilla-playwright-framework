from typing import Type

from playwright.sync_api import Page

from config.settings import PROJECT_ROOT
from factory.base_pages_store import BasePagesStore
from factory.url_manager import URLManager
from factory.yaml_locator_loader import YamlLocatorsLoader
from utils.allure_utils import attach_screenshot, step
from utils.exceptions import UnsupportedStorePages, UnsupportedUrlManager
from utils.logger import get_logger

logger = get_logger(__name__)


class WebContext:
    """Класс web-контекст. Реализует контекст для работы с браузером."""

    def __init__(self, page: Page, store_pages: Type[BasePagesStore], url_manager: URLManager):
        self.page = page
        self.yaml_locator_loader = YamlLocatorsLoader(self.page, PROJECT_ROOT, 'locators')
        self._store_pages = None
        self._url_manager = None
        if store_pages:
            self.set_store_pages(store_pages)
        if url_manager:
            self.set_url_manager(url_manager)

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

    def goto(self, url_name: str, **kwargs):
        """
        Открывает страницу по URL
        :param url_name: название URL-адреса
        :param kwargs: параметры для динамического URL
        """
        url = self.url_manager.get(url_name, **kwargs)
        with step(f"Открыть по URL страницу: {url_name} - {url}"):
            self.page.goto(url)
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
        if not issubclass(url_manager, URLManager):
            raise UnsupportedUrlManager(f"Неподдерживаемый URL-менеджер: {url_manager}")
        self._url_manager = url_manager

    def get_page(self, page_name, check=True):
        """
        Получить объект страницы по названию
        :param check: выполнять проверку ключевых элементов на странице
        :param page_name: название страницы
        :return: объект страницы
        """
        return self.store_pages(page_name, check).current_page

    def open_new_tab(self) -> Page:
        """Открыть и перейти на новую вкладку"""
        new_page = self.page.context.new_page()
        self.page = new_page
        self.yaml_locator_loader.page = new_page
        logger.info("Открыта новая вкладка")
        return new_page

    def close_tab(self):
        """Закрыть текущую вкладку и переключиться на оставшуюся"""
        current = self.page
        ctx = current.context
        current.close()
        logger.info("Вкладка закрыта")
        remaining = ctx.pages
        if not remaining:
            raise RuntimeError("Все вкладки закрыты")
        self.page = remaining[-1]
        self.yaml_locator_loader.page = self.page
        logger.info(f"Переключено на вкладку: {self.page.url}")
        return self

    def switch_to_tab(self, index: int) -> Page:
        """Переключиться на вкладку по индексу self.page — выбранная вкладка"""
        pages = self.page.context.pages
        if index >= len(pages):
            raise IndexError(f"Вкладки с индексом {index} нет. Общее число вкладок: {len(pages)}")
        self.page = pages[index]
        logger.info(f"Переключено на вкладку {index}")
        return self.page

    def close_all_tabs(self):
        """Закрыть все вкладки"""
        ctx = self.page.context
        for page in ctx.pages:
            page.close()
        logger.info("Все вкладки закрыты")
        return self

    def screenshot(self, name: str = 'screenshot'):
        """Делает и прикрепляет скриншот в Allure."""
        attach_screenshot(self.page, name)
        return self
