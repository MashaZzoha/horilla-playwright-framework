from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from utils import logger
from utils.yaml_locators_loader import YamlLocatorsLoader
from utils.exceptions import LocatorNotFound, ElementsNotFound
from utils.allure_utils import step, attach_screenshot

logger = logger.get_logger(__name__)


class BasePage:
    """Базовый класс страниц проекта"""

    def __init__(
            self,
            page: Page,
            title: str,
            locator_loader: YamlLocatorsLoader,
            page_file_name: str = None,
            check: bool = True):

        self.page = page
        self.title = title
        self.locator_loader = locator_loader
        self.page_file_name = page_file_name
        self._elements_to_check = []
        self.check = check

    @staticmethod
    def time_sec(timeout: int = None):
        return f"{timeout / 1000:.1f} сек." if timeout else 'время ожидания по умолчанию'

    def _get(self, locator_name: str, **kwargs) -> Locator:
        """Возвращает Locator по названию из YAML"""
        return self.locator_loader.get_locator_by_name(self.page_file_name, locator_name, **kwargs)

    def get_element(self, locator_name: str, timeout: int = None, **kwargs) -> Locator:
        """Поиск элемента, ожидание его отображения на странице"""
        locator = self._get(locator_name, **kwargs)
        try:
            locator.wait_for(state='visible', timeout=timeout)
            logger.debug(f"[{self.title}]: найден элемент '{locator_name.upper()}'")
            return locator
        except PlaywrightTimeoutError:
            msg = (f"Не найден элемент '{locator_name.upper()}' на странице '{self.title}' "
                   f"(за {self.time_sec(timeout)})")
            logger.error(msg)
            attach_screenshot(self.page, f"Не найден элемент: '{locator_name}'")
            raise

    def has_element(self, locator_name: str, timeout: int = None, **kwargs) -> bool:
        """Проверка наличия или отсутствия элемента на странице"""
        try:
            self.get_element(locator_name, timeout=timeout, **kwargs)
            return True
        except PlaywrightTimeoutError:
            return False

    def add_elements_to_check(self, *elements):
        """
        Добавляет уникальные элементы для проверки на странице для проверки страницы
        :param elements: элементы для проверки
        """
        for element in elements:
            try:
                self.locator_loader.get_locator_by_name(
                    page_file_name=self.page_file_name,
                    locator_name=element)
                self._elements_to_check.append(element)
                logger.debug(f"[{self.title}]: Добавлен элемент для проверки {element.upper()}")
            except KeyError:
                msg = (f"[{self.title}]: Локатор '{element.upper()}' не найден "
                       f"в {self.page_file_name}.yaml. Невозможно добавить в проверку страницы.")
                logger.error(msg)
                raise LocatorNotFound(msg)

    def check_page(self, timeout: int = None):
        """Базовый метод для проверки нахождения на странице.
         Проверка осуществляется путем поиска ключевых элементов,
        присущих только проверяемой странице."""
        if self._elements_to_check:
            elements_not_found = []
            with step(f"Проверка перехода на {self.title}"):
                with step(f"Проверка отображения {len(self._elements_to_check)} элементов на странице {self.title}"):
                    for idx, element in enumerate(self._elements_to_check):
                        if not self.has_element(element, timeout):
                            elements_not_found.append(element)
                    if elements_not_found:
                        msg = (f"Элементы: {', '.join(elements_not_found).upper()} не найдены.\n"
                               f"Возможно не открылась страница {self.title.upper()}")
                        logger.error(msg)
                        raise ElementsNotFound(msg)
        return self

    def open_page(self, url: str):
        """Открывает страницу по указанному адресу"""
        self.page.goto(url)
        return self

    def click(self, locator: str):
        """Нажимает на заданный элемент"""
        self.get_element(locator).click()
        return self

    def input(self, locator: str, text):
        """Вводит значение в поле ввода"""
        self.get_element(locator).fill(str(text))
        return self

    def get_text(self, locator: str) -> str:
        """Получает текст из элемента"""
        return self.get_element(locator).inner_text()

    def is_visible(self, locator: str) -> bool:
        """Проверка отображения элемента на экране"""
        return self.get_element(locator).is_visible()

    def clear(self, locator: str):
        self.get_element(locator).clear()
        return self

    def refresh_page(self, timeout=None):
        """Обновить страницу (по умолчанию 30 сек)"""
        self.page.reload(timeout=timeout)
        return self
