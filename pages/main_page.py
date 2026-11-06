from factory.web_context import WebContext
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class MainPage(BasePage):
    """Класс главной страницы приложения"""

    def __init__(self, context: WebContext, page_name: str):
        super().__init__(context, page_name, page_file_name="main_page.yaml")
        self.yaml_locator_loader.locator_registry(self.page_file_name)
        self.add_elements_to_check("ЛОГОТИП", "ПОЛЕ ПОИСКА")
        self.check_page()
