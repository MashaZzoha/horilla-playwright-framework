from playwright.sync_api import Locator
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import expect

from utils.allure_utils import attach, attach_screenshot, step
from config.settings import settings
from utils.exceptions import ElementsNotFound, LocatorNotFound
from utils.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    """Базовый класс страниц проекта"""

    def __init__(self, context, page_name: str, page_file_name: str = 'base_page_yaml'):
        """
        :param context: Context
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
        self.yaml_locator_loader.locator_registry(self.page_file_name)

    @staticmethod
    def time_sec(timeout: int = None):
        """
        Перевести время из миллисекунд в секунды (для удобочитаемости в отчётах и логах)
        :param timeout: время ожидания в миллисекундах
        """
        return f"{timeout / 1000:.1f} сек." if timeout else 'время ожидания по умолчанию'

    def _get(self, locator: str, **kwargs) -> Locator:
        """
        Возвращает Locator по названию из YAML
        :param locator: YAML-локатор
        :param kwargs: значение для динамического локатора
        :return: Locator
        """
        return self.yaml_locator_loader.get_locator_by_name(self.page_file_name, locator, **kwargs)

    def get_element(self, locator_name: str, timeout: int = 10000, **kwargs) -> Locator:
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

    @step("Проверка отображения элемента {locator} на странице")
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

    @step('Проверить наличие атрибута {attribute} со значением {value} у элемента {locator}')
    def expect_attribute(self, locator: str, attribute: str, value, timeout: int = None, **kwargs):
        """
        Проверяет у элемента наличие атрибута с определённым значением
        :param locator: YAML-локатор
        :param attribute: атрибут
        :param value: значение атрибута
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        expect(self._get(locator, **kwargs)).to_have_attribute(attribute, value, timeout)
        return self

    @step("Проверить наличие видимого текста '{text}' в элементе '{locator}'")
    def expect_text(
            self,
            locator: str,
            text: str,
            exact: bool = True,
            timeout: int = 5000,
            **kwargs):
        """
        Проверяет, что элемент или поле ввода содержит видимый текст
        :param locator: имя локатора
        :param text: ожидаемый текст
        :param exact: True — точное совпадение, False — подстрока
        :param timeout: время ожидания
        :param kwargs: параметры динамического локатора
        """
        element = self._get(locator, **kwargs)
        if exact:
            expect(element).to_have_text(text, timeout=timeout)
        else:
            expect(element).to_contain_text(text, timeout=timeout)
        return self

    @step("Проверить отсутствие видимого текста '{text}' в элементе '{locator}'")
    def expect_not_text(
            self,
            locator: str,
            text: str,
            exact: bool = True,
            timeout: int = 5000,
            **kwargs):
        """
        Проверяет, что элемент или поле ввода НЕ содержит видимый текст
        :param locator: имя локатора
        :param text: ожидаемый текст
        :param exact: True — точное совпадение, False — подстрока
        :param timeout: время ожидания
        :param kwargs: параметры динамического локатора
        """
        element = self._get(locator, **kwargs)
        element.wait_for(state="visible", timeout=timeout)
        tag = element.evaluate("el => el.tagName.toLowerCase()")
        if tag in ("input", "textarea"):
            actual_text = element.input_value()
        else:
            actual_text = element.inner_text()
        attach('Фактический тест элемента', actual_text)
        if exact:
            assert actual_text != text, f"Видимый текст элемента '{locator}' соответствует '{text}'"
        else:
            assert text not in actual_text, f"Видимый текст '{locator}' содержит '{text}'"
        return self

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
                           f"Возможно не открылась {self.page_name.upper()}")
                    logger.error(msg)
                    raise ElementsNotFound(msg)
        return self

    @step('Проверить отображение активной плашки {tab}')
    def check_active_tab(self, tab: str):
        """
        Проверить отображение активной плашки при открытии соответствующей страницы
        :param tab: название плашки (Home, Sales, People, Analytics, Schedule, My Jobs)
        """
        if not self.has_element('Активная кнопка меню', link_name=tab):
            msg = (f"Активная плашка страницы: {tab} не отобразилась.\n"
                   f"Возможно не открылась {self.page_name.upper()}")
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
    def input_text(self, locator: str, text, timeout: int = None, **kwargs):
        """
        Вводит текст в поле ввода
        :param locator: YAML-локатор
        :param text: текст для ввода
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        self.get_element(locator, timeout=timeout, **kwargs).fill(str(text))
        return self

    @step("")
    def input_verified(self, locator: str, text: str, retries: int = 3, delay: int = 150,
                       timeout: int = None, **kwargs):
        """Вводит значение в поле и проверяет, что оно 'закрепилось' (HTMX может перерисовать DOM)
        :param locator: имя локатора
        :param text: значение
        :param retries: число попыток
        :param delay: пауза после ввода перед проверкой (мс)
        :param timeout: время ожидания элемента
        :param kwargs: параметры динамического локатора
        """
        attempts = 0
        text = str(text)

        while attempts < retries:
            mismatched = []
            self.input_text(locator, text, timeout=timeout, **kwargs)
            self.browser_page.wait_for_timeout(delay)
            element = self.get_element(locator, timeout=timeout, **kwargs)
            if element.input_value() != text:
                mismatched.append(locator)
            if not mismatched:
                return self
            attempts += 1
            logger.debug(
                f"[{self.page_name}] Не закрепилось поле: {mismatched} на попытке {attempts}")

        raise AssertionError(
            f"Не удалось зафиксировать значение '{text}' в поле '{locator}' за {attempts} попыток")

    @step("Заполнить поля ввода значениями: {fields}")
    def input_verify_batch(
            self,
            fields: dict[str, str],
            retries: int = 3,
            delay: int = 150,
            timeout: int = None,
            **kwargs):
        """
        Заполнить поля ввода fields.keys значениями fields.values
        :param fields: словарь {имя локатора: значение}
        :param retries: количество попыток ввода
        :param delay: интервал между попытками ввода
        :param timeout: время ожидания элемента
        :param kwargs: параметры динамического локатора
        """
        fields = {key: str(value) for key, value in fields.items()}
        attempts = 0
        mismatched = []
        while attempts < retries:
            mismatched = []
            for locator, text in fields.items():
                self.input_text(locator, text, timeout=timeout, **kwargs)
                self.browser_page.wait_for_timeout(delay)
                element = self.get_element(locator, **kwargs)
                if element.input_value() != text:
                    mismatched.append(locator)
            if not mismatched:
                return self
            retries += 1
            logger.debug(f"[{self.page_name}] Не закрепились поля: {mismatched}, попытка {attempts}")
        raise AssertionError(f"Не удалось зафиксировать значения в полях: {mismatched} за {attempts} попыток")

    @step("Получить текст из элемента '{locator}'")
    def get_text(self, locator: str, timeout: int = None, **kwargs) -> str:
        """
        Получить текст из элемента
        :param locator: YAML-локатор
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        return self.get_element(locator, timeout=timeout, **kwargs).inner_text()

    @step("Проверка отображения элемента {locator} на странице")
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

    @step("Выбрать значение '{option}' в выпадающем меню селектора {locator}")
    def select_option(self, locator: str, option: str = None, timeout: int = None, **kwargs):
        """
        Выбрать опцию в выпадающем меню селектора
        :param locator: локатор выпадающего меню (select)
        :param option: значение выбора
        :param timeout: время ожидания
        :param kwargs: значение для динамического локатора
        """
        self.get_element(locator, timeout, **kwargs).select_option(label=option)
        return self

    @step("Выбрать опцию {option} в селекторе Select2 {selector_name}")
    def select2_option(self, selector_name: str, option: str, timeout: int = 5000):
        """
        Выбрать опцию в селекторе Select2
        :param selector_name: название селектора (частичное значение атрибута name/id)
        :param option: вариант выбора
        :param timeout: время ожидания элемента на странице
        """
        self.click("Селектор select2", selector_name=selector_name, timeout=timeout)
        self.click("Опция select2", selector_name=selector_name, option=option, timeout=timeout)
        return self

    @step("Выбрать значения в селекторах Select2 : {selections}")
    def select2_option_batch(
            self,
            selections: dict[str, str],
            timeout: int = 5000):
        """
        Заполнить поля ввода fields.keys значениями fields.values
        :param selections: словарь {локатор селектора: значение}
        :param timeout: время ожидания элемента
        """
        selections = {key: str(value) for key, value in selections.items()}
        for selector2, option in selections.items():
            self.select2_option(selector2, option, timeout=timeout)
        return self

    @step('Открыть форму Create Lead или Create Account')
    def open_form_new(self, form: str):
        """
        Открыть форму для внесения данных по новому лиду или профилю
        :param form: форма внесения данных Create Lead или Create Account
        """
        if self.has_element('Кнопка Add New'):
            self.click('Кнопка Add New')
        else:
            self.click('Кнопка New')
        assert self.has_element(form), f"Не открылась форма '{form}'"
        return self

    @staticmethod
    def get_owner():
        """Получить данные: имя и фамилию админа из settings.yaml"""
        first_name = settings.users['admin'].get('first_name')  # "Зинаида"
        last_name = settings.users['admin'].get('last_name')
        return f"{first_name} {last_name}"

    def refresh_page(self, timeout=None):
        """Обновить страницу (по умолчанию 30 сек)"""
        with step(f"Обновить страницу {self.browser_page}"):
            self.browser_page.reload(timeout=timeout)
        return self
