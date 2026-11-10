from factory.web_context import WebContext
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    """Класс страницы авторизации"""

    def __init__(self, context: WebContext, page_name: str):
        super().__init__(context, page_name, page_file_name="login_page.yaml")
        self.yaml_locator_loader.locator_registry(self.page_file_name)
        self.add_elements_to_check("Форма авторизации", "Текст приветствия")
        self.check_page()
