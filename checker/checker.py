from time import sleep, time

from utils.allure_utils import attach, step
from utils.logger import get_logger

logger = get_logger(__name__)


class Checker:
    """Класс для проверок ответов от БД и сервисов"""

    def __init__(self, web_context):
        """
        Инициализатор класса
        :param web_context: WebContext
        """
        self.ctx = web_context

    # TODO Ничего полезного для нас этот метод не обрабатывает - проверка логики

    @step("Проверить {logentry}")
    def check_user_exists(self, logentry: str, timeout: int = 10, interval: int = 2):
        """
        Проверка данных пользователя в БД
        :param logentry: logentry
        :param timeout: максимальное время ожидания ответа от БД
        :param interval: интервал между повторными запросами
        """
        response = []
        start_time = time()
        while time() - start_time < timeout:
            response = self.ctx.horilla_provider.get_changes_by_logentry(logentry)
            if response:
                break
            sleep(interval)
        attach('Получен ответ от БД', body=str(response))
        assert response, f"Не найдено записи в БД по клиенту {logentry}"
