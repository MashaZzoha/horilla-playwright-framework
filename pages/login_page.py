from config.settings import settings
from factory.context import Context
from pages.base_page import BasePage
from utils.allure_utils import step
from utils.logger import get_logger

logger = get_logger(__name__)


class LoginPage(BasePage):
    """Класс страницы авторизации"""

    def __init__(self, context: Context, page_name: str):
        super().__init__(context, page_name, page_file_name="login_page.yaml")
        self.yaml_locator_loader.locator_registry(self.page_file_name)
        self.add_elements_to_check("Форма авторизации", "Текст приветствия")
        self.check_page()

    @step('Авторизация')
    def auth(
            self,
            alias: str = None,
            username: str = None,
            password: str = None,
            success: bool = True,
            delay: int = 200):
        """
        Авторизация в приложении
        :param alias: алиас пользователя для получения пары username/password из конфига
        :param username: логин
        :param password: пароль
        :param success: True - успешная авторизация
        :param delay: интервал между повторными попытками ввода логина/пароля
        """
        if alias:
            record = settings.users.get(alias)
            if record is None:
                raise ValueError(f'Не удалось найти пользователя: "{alias}" в конфиг settings.yaml!')
            username = record["username"]
            password = record["password"]
        self.input_verified('Поле ввода Логин', username, delay=delay)
        self.input_verified('Поле ввода Пароль', password, delay=delay)
        self.click('Кнопка Войти')
        if success:
            self.page('Главная страница')
            assert self.has_element('Алерт Успешная авторизация'), (
                "Алерт об успешной авторизации не отобразился на странице")
        self.page('Страница Авторизации')
