from time import sleep, time

from utils.allure_utils import attach, step
from utils.logger import get_logger

logger = get_logger(__name__)


class Checker:
    """Класс для проверок ответов от БД и сервисов"""

    def __init__(self, context):
        """
        Инициализатор класса
        :param context: Context
        """
        self.ctx = context

    @step("Проверить создание лида по адресу электронной почты: {email}")
    def check_lead_created(self, email: str, timeout: int = 30, interval: int = 2):
        """
        Проверка, что лид (потенциальный клиент) был успешно создан
        :param email: электронная почта
        :param timeout: максимальное время ожидания ответа от БД
        :param interval: интервал между повторными запросами
        """
        response = []
        start_time = time()
        while time() - start_time < timeout:
            response = self.ctx.horilla_provider.get_lead_by_email(email)
            if response:
                break
            sleep(interval)
        attach('Получен ответ от БД', body=str(response))
        assert response, f"Не найдено записи в БД по клиенту c адресом электронной почты: {email}"
        return self

    @step("Проверить создание профиля по номеру телефона: {phone}")
    def check_account_created(self, phone: str, timeout: int = 30, interval: int = 2):
        """
        Проверка, что профиль был успешно создан
        :param phone: номер телефона в формате +7 9847701216
        :param timeout: максимальное время ожидания ответа от БД
        :param interval: интервал между повторными запросами
        """
        response = []
        start_time = time()
        while time() - start_time < timeout:
            response = self.ctx.horilla_provider.get_account_by_phone(phone)
            if response:
                break
            sleep(interval)
        attach('Получен ответ от БД', body=str(response))
        assert response, f"Не найдено записи в БД по клиенту c номером телефона: {phone}"
        return self
