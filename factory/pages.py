from factory.context import Context
from utils.logger import get_logger

logger = get_logger(__name__)


class Pages:
    """Класс управления текущей страницей"""

    def __init__(self, context: Context):
        """
        Инициализация класса управления страницами Pages
        :param context: вэб-контекст
        """
        self.context = context
        self._current_page = None

    @property
    def current(self):
        """Текущая страница (Page Object)"""
        if self._current_page is None:
            raise RuntimeError("Сначала надо получить страницу: page()/open_page()")
        return self._current_page

    def page(self, page_name: str):
        """Получить объект страницы по названию из каталога страниц"""
        self._current_page = self.context.get_page(page_name)
        return self._current_page

    def open_page(self, page_name: str, **kwargs):
        """
        Открыть страницу по названию из каталога
        :param page_name: название страницы
        :param kwargs: **kwargs
        """
        self.context.goto(page_name, **kwargs)
        return self.page(page_name)

    def __getattr__(self, name):
        """Передаёт методы BasePage на текущую страницу"""
        if name.startswith('_'):
            raise AttributeError(name)
        return getattr(self.current, name)
