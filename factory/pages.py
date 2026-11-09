from factory.web_context import WebContext
from utils.logger import get_logger

logger = get_logger(__name__)


class Pages:
    """Класс управления текущей страницей"""

    def __init__(self, web_context: WebContext):
        self.context = web_context
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

    def open_page(self, page_name: str, url_name: str = None, **kwargs):
        """Открыть страницу. Возвращает Page Object."""
        target_url = url_name or page_name
        page = self.page(page_name)
        self.context.goto(target_url, **kwargs)
        return page

    def __getattr__(self, name):
        """Передаёт методы BasePage на текущую страницу"""
        if name.startswith('_'):
            raise AttributeError(name)
        return getattr(self.current, name)
