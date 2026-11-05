from factory.base_pages_store import BasePagesStore
from factory.web_context import WebContext
from pages.main_page import MainPage


class ProjectStorePages(BasePagesStore):
    """Каталог страниц Project"""
    def __init__(self, context: WebContext, store='Магазин страниц Project'):
        super().__init__(context, store=store)

        self.page_registry([
            {'Главная страница': MainPage},
        ])
