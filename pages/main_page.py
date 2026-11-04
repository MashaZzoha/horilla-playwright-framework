from playwright.sync_api import Page
from base_page import BasePage


class MainPage(BasePage):
    """Класс главной страницы приложения"""

    def __init__(self, page: Page, locators: dict):
        super().__init__(page)
