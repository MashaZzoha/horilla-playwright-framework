from factory.base_pages_store import BasePagesStore
from factory.context import Context
from pages.login_page import LoginPage
from pages.main_page import MainPage


class HorillaStorePages(BasePagesStore):
    """Каталог страниц Horilla"""
    def __init__(self, context: Context, store='Магазин страниц Horilla'):
        super().__init__(context, store=store)

        self.page_registry([
            {'Страница Авторизации': LoginPage},
            {'Главная страница': MainPage},
        ])
