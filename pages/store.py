from utils.base_page_store import BasePageStore
from playwright.sync_api import Page
from pages.main_page import MainPage


class LivemastersStorePages(BasePageStore):
    """Каталог страниц Livemasters"""
    def __init__(self, page: Page, store='Магазин страниц Livemasters'):
        super().__init__(page, store)

        self.page_registry([
            {'Главная страница': MainPage},
        ])
