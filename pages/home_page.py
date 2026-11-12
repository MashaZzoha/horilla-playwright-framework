from factory.context import Context
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class HomePage(BasePage):
    """Класс главной страницы приложения"""

    def __init__(self, context: Context, page_name: str):
        super().__init__(context, page_name, page_file_name="home_page.yaml")
        self.yaml_locator_loader.locator_registry(self.page_file_name)
        self.add_elements_to_check("Приветствие", "Home активна")
        self.check_page()

    def open_tab(self, button: str, page_name: str, timeout: int = None):
        """
        Открыть вкладку через меню навигации
        :param button: кнопка на меню навигации
        :param page_name: имя страницы
        :param timeout: время ожидания элемента
        """
        if not self.has_element('Активная вкладка меню', link_name=button, timeout=timeout):
            self.click('Неактивная вкладка меню', link_name=button)
        assert self.has_element('Активная вкладка меню', link_name=button, timeout=timeout), (
            f'Плашка вкладки {page_name} не отображается активной')
        return self.page(page_name)
