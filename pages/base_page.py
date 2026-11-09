from playwright.sync_api import Locator
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from utils.allure_utils import attach_screenshot, step
from utils.exceptions import ElementsNotFound, LocatorNotFound
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    """Базовый класс страниц проекта"""

    def __init__(self, context, page_name: str, page_file_name: str = None):
        """

        :param context: WebContext
        :param page_name: название страницы из каталога страниц
        :param page_file_name: название .yaml-файла страницы
        """
        self.context = context
        self.browser_page = context.browser_page
        self.yaml_locator_loader = context.yaml_locator_loader
        self.url_manager = self.context.url_manager
        self.page_file_name = page_file_name
        self.page_name = page_name
        self._elements_to_check = []

    @staticmethod
    def time_sec(timeout: int = None):
        return f"{timeout / 1000:.1f} сек." if timeout else 'время ожидания по умолчанию'

    def _get(self, locator: str, **kwargs) -> Locator:
        """
        Возвращает Locator по названию из YAML
        :param locator: YAML-локатор
        :param kwargs: значение для динамического локатора
        :return: Locator
        """
        return self.yaml_locator_loader.get_locator_by_name(self.page_file_name, locator, **kwargs)

    def get_element(self, locator_name: str, timeout: int = None, **kwargs) -> Locator:
        """
        Поиск элемента, ожидание его отображения на странице
        :param locator_name: YAML-локатор
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        locator = self._get(locator_name, **kwargs)
        try:
            locator.wait_for(state='visible', timeout=timeout)
            logger.debug(f"[{self.page_name}]: найден элемент '{locator_name.upper()}'")
            return locator
        except PlaywrightTimeoutError:
            msg = (f"Не найден элемент '{locator_name.upper()}' на странице '{self.page_name}' "
                   f"(за {self.time_sec(timeout)})")
            logger.error(msg)
            attach_screenshot(self.browser_page, f"Не найден элемент: '{locator_name}'")
            raise

    @step("Проверка отображения элемента '{}' на странице")
    def has_element(self, locator: str, timeout: int = None, **kwargs) -> bool:
        """
        Проверка наличия или отсутствия элемента на странице
        :param locator: YAML-локатор
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        try:
            self.get_element(locator, timeout=timeout, **kwargs)
            return True
        except PlaywrightTimeoutError:
            return False

    @step("Добавить элементы для проверки на странице: {elements}")
    def add_elements_to_check(self, *elements):
        """
        Добавляет уникальные элементы для проверки на странице для проверки страницы
        :param elements: элементы для проверки
        """
        for element in elements:
            try:
                self.yaml_locator_loader.get_locator_by_name(
                    page_file_name=self.page_file_name,
                    locator_name=element)
                self._elements_to_check.append(element)
                logger.debug(f"[{self.page_name}]: Добавлен элемент для проверки {element.upper()}")
            except KeyError:
                msg = (f"[{self.page_name}]: Локатор '{element.upper()}' не найден "
                       f"в {self.page_file_name}. Невозможно добавить в проверку страницы.")
                logger.error(msg)
                raise LocatorNotFound(msg)

    def check_page(self, timeout: int = None):
        """
        Базовый метод для проверки нахождения на странице
        Проверка осуществляется путем поиска ключевых элементов,
        присущих только проверяемой странице
        :param timeout: время ожидания
        """
        if not self._elements_to_check:
            return self
        elements_not_found = []
        with step(f"Проверка перехода на {self.page_name}"):
            with step(f"Проверка отображения {len(self._elements_to_check)} элементов на странице "
                      f"{self.page_name}"):
                for element in self._elements_to_check:
                    if not self.has_element(element, timeout):
                        elements_not_found.append(element)
                if elements_not_found:
                    msg = (f"Элементы: {', '.join(elements_not_found).upper()} не найдены.\n"
                           f"Возможно не открылась страница {self.page_name.upper()}")
                    logger.error(msg)
                    raise ElementsNotFound(msg)
        return self

    def page(self, page_name: str):
        """Получить объект новой страницы по названию из каталога страниц"""
        return self.context.get_page(page_name)

    def open_page(self, url: str):
        """
        Открывает страницу по указанному адресу
        :param url: имя URL из менеджера URL
        """
        self.browser_page.goto(url)
        return self

    def click(self, locator: str, timeout: int = None, **kwargs):
        """
        Нажимает на заданный элемент
        :param locator: YAML-локатор
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        self.get_element(locator, timeout=timeout, **kwargs).click()
        return self

    @step("Ввести текст '{text}' в поле ввода '{locator}'")
    def input(self, locator: str, text, timeout: int = None, **kwargs):
        """
        Вводит текст в поле ввода
        :param locator: YAML-локатор
        :param text: текст для ввода
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        self.get_element(locator, timeout=timeout, **kwargs).fill(str(text))
        return self

    @step("Получить текст из элемента '{locator}'")
    def get_text(self, locator: str, timeout: int = None, **kwargs) -> str:
        """
        Получить текст из элемента
        :param locator: YAML-локатор
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        return self.get_element(locator, timeout=timeout, **kwargs).inner_text()

    @step("Проверка отображения элемента '{locator}' на странице")
    def is_visible(self, locator: str, timeout: int = None, **kwargs) -> bool:
        """
        Проверка отображения элемента на экране
        :param locator: YAML-локатор
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        return self.get_element(locator, timeout=timeout, **kwargs).is_visible()

    @step("Очистить поле ввода '{locator}'")
    def clear(self, locator: str, timeout: int = None, **kwargs):
        """
        Очистка поля ввода
        :param locator: YAML-локатор
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        self.get_element(locator, timeout=timeout, **kwargs).clear()
        return self

    @step("Пролистать страницу до элемента '{locator}'")
    def scroll_to(self, locator: str, timeout: int = None, **kwargs):
        """
        Пролистать до элемента
        :param locator: YAML-локатор
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        self.get_element(locator, timeout=timeout, **kwargs).scroll_into_view_if_needed()
        return self

    @step("Ввести текст '{text}' посимвольно в элемент '{locator}'")
    def type_text(self, locator: str, text: str, delay: int = 0, timeout: int = None, **kwargs):
        """
        Ввод текста посимвольно
        :param locator: YAML-локатор
        :param text: текст для ввода
        :param delay: задержка между вводом символов
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора

        """
        self.get_element(locator, timeout=timeout, **kwargs).press_sequentially(text, delay=delay)
        return self

    @step("Нажать клавишу '{key}', находясь на элементе '{locator}'")
    def press_key(self, locator: str, key: str, timeout: int = None, **kwargs):
        """
        Нажать клавишу на клавиатуре (Enter, Tab, Escape... и т.д.), находясь на элементе
        :param locator: YAML-локатор
        :param key: название клавиши
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        self.get_element(locator, timeout=timeout, **kwargs).press(key)
        return self

    def refresh_page(self, timeout=None):
        """Обновить страницу (по умолчанию 30 сек)"""
        with step(f"Обновить страницу {self.browser_page}"):
            self.browser_page.reload(timeout=timeout)
        return self
