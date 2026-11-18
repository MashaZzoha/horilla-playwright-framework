from typing import Dict, List, Type

from pages.base_page import BasePage
from utils.exceptions import NotFoundPageInStore
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePagesStore:
    """
    Базовый класс каталога страниц.
    Реализует поиск в каталоге страниц по названию страницы
    """

    def __init__(self, context, store="Каталог страниц"):
        """
        Инициализация базового класса
        :param context: вэб-контекст
        :param store: каталог страниц
        """
        self.context = context
        self._store = store
        self._registry: Dict[str, Type[BasePage]] = {}
        self._pages: Dict[str, BasePage] = {}
        self._current_page = None

    def __call__(self, page_name: str):
        page_name = page_name.upper()
        try:
            page_class = self._registry[page_name]
        except KeyError:
            msg = f"[{self._store}] Не найдена страница по имени '{page_name}'"
            logger.error(msg)
            raise NotFoundPageInStore(msg)

        if page_name not in self._pages:
            self._pages[page_name] = page_class(
                context=self.context,
                page_name=page_name)
            logger.debug(f"{self._store}: создана страница '{page_name}' ({page_class.__name__})")

        self._current_page = self._pages[page_name]
        return self

    def page_registry(self, pages: List[Dict[str, Type[BasePage]]]):
        """
        Регистрация страниц в каталоге страниц списком словарей:
        [{'название страницы N': класс страницы N}, ...]
        :param pages: страницы каталога
        """
        logger.debug(f"[{self._store}] Идёт регистрация {len(pages)} страниц")
        for row in pages:
            for page_name, page_class in row.items():
                page_name = page_name.upper()
                if isinstance(page_class, type) and issubclass(page_class, BasePage):
                    self._registry[page_name] = page_class
                    logger.debug(f"{self._store}: зарегистрирована страница: {page_name} -> {page_class.__name__}")
                else:
                    logger.warning(f"Не удалось зарегистрировать страницу: {page_name}")
        logger.info(f"{self._store}: зарегистрировано {len(self._registry)} страниц")
        return self

    @property
    def current_page(self):
        """Возвращает текущую страницу"""
        return self._current_page
