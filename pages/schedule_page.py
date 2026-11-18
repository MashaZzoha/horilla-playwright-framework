from factory.context import Context
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class SchedulePage(BasePage):
    """Класс страницы календаря (Schedule)"""

    def __init__(self, context: Context, page_name: str):
        """
        Инициализация класса страницы календаря SchedulePage
        :param context: вэб-контекст
        :param page_name: название страницы
        """
        super().__init__(context, page_name, page_file_name="schedule_page.yaml")
        self.yaml_locator_loader.locator_registry(self.page_file_name)
        self.add_elements_to_check('Заголовок Calendar', 'Заголовок Calendar')
        self.check_page()
