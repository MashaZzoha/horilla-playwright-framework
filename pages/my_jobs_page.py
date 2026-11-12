from factory.context import Context
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger(__name__)


class MyJobsPage(BasePage):
    """Класс страницы задач (My Jobs)"""

    def __init__(self, context: Context, page_name: str):
        super().__init__(context, page_name, page_file_name="my_jobs_page.yaml")
        self.yaml_locator_loader.locator_registry(self.page_file_name)
        self.add_elements_to_check('Заголовок My Review Jobs', 'Меню Review Jobs')
        self.check_page()
