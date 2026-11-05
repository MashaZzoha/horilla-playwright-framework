from playwright.sync_api import Page
from base_page import BasePage
from utils.yaml_locators_loader import YamlLocatorsLoader


class MainPage(BasePage):
    """Класс главной страницы приложения"""

    def __init__(self, page: Page, title: str, locator_loader: YamlLocatorsLoader, check: bool = True):
        super().__init__(page, title, locator_loader, page_file_name="main_page.yaml", check=check)
        self.locator_loader.locator_registry(self.page_file_name)

