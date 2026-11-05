import exceptions
from typing import Dict, List, Type
from playwright.sync_api import Page
from pages.base_page import BasePage
from utils.logger import get_logger
from utils.yaml_locators_loader import YamlLocatorsLoader

logger = get_logger(__name__)


class BasePageStore:
    """Базовый класс каталога страниц.
    Реализует поиск в каталоге страниц по названию страницы"""

    def __init__(self, page: Page, locator_loader: YamlLocatorsLoader, store="Магазин страниц"):
        self.page = page
        self.locator_loader = locator_loader
        self._store = store
        self._registry: Dict[str, Type[BasePage]] = {}
        self._pages: Dict[str, BasePage] = {}
        self._current_page = None

    def __call__(self, title: str, check: bool = True):
        title = title.upper()
        try:
            page_class = self._registry[title]
        except KeyError:
            msg = f"[{self._store}] Не найдена страница по имени '{title}'"
            logger.error(msg)
            raise exceptions.NotFoundPageInStore(msg)

        if title not in self._pages:
            self._pages[title] = page_class(
                page=self.page,
                title=title,
                check=check,
                locator_loader=self.locator_loader)
            logger.debug(f"{self._store}: создана страница '{title}' ({page_class.__name__})")

        self._current_page = self._pages[title]
        return self

    def page_registry(self, pages: List[Dict[str, Type[BasePage]]]):
        """Регистрация страниц в каталоге страниц списком словарей:
        [{'название страницы N': класс страницы N}, ...]"""
        logger.debug(f"[{self._store}] Идёт регистрация {len(pages)} страниц")
        for row in pages:
            for title, page_class in row.items():
                title = title.upper()
                if isinstance(page_class, type) and issubclass(page_class, BasePage):
                    self._registry[title] = page_class
                    logger.debug(f"{self._store}: зарегистрирована страница: {title} -> {page_class.__name__}")
                else:
                    logger.warning(f"Не удалось зарегистрировать страницу: {title}")
        logger.info(f"{self._store}: зарегистрировано {len(self._registry)} страниц")
        return self

    @property
    def current_page(self):
        """Возвращает текущую страницу"""
        return self._current_page
