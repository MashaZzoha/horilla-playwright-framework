from playwright.sync_api import Page


class BasePage:
    """Базовый класс страниц проекта"""

    def __init__(self, page: Page):
        self.page = page

    def check_page(self, *locators: str):
        """Базовый метод для проверки нахождения на странице.
         Проверка осуществляется путем поиска ключевых элементов,
        присущих только проверяемой странице."""
        for locator in locators:
            if not self.is_visible(locator)

    def open_page(self, url: str):
        """Открывает страницу по указанному адресу"""
        self.page.goto(url)
        return self

    def click(self, locator: str):
        """Нажимает на заданный элемент"""
        self.page.locator(locator).click()
        return self

    def input(self, locator: str, text):
        """Вводит значение в поле ввода"""
        self.page.locator(locator).fill(str(text))
        return self

    def get_text(self, locator: str) -> str:
        """Получает текст из элемента"""
        return self.page.locator(locator).inner_text()

    def is_visible(self, locator: str) -> bool:
        """Проверка отображения элемента на экране"""
        return self.page.locator(locator).is_visible()

    def wait_for_element(self, locator: str, state: str = 'visible', timeout: int = None):
        """Ждёт, пока элемент достигнет указанного состояния (visible, attached, hidden)."""
        self.page.locator(locator).wait_for(state=state, timeout=timeout)
        return self

    def clear(self, locator: str):
        self.page.locator(locator).clear()
        return self

    def refresh_page(self, timeout=None):
        """Обновить страницу (по умолчанию 30 сек)"""
        self.page.reload(timeout=timeout)
        return self


