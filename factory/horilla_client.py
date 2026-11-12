from faker import Faker
from utils.allure_utils import attach, step
from utils.logger import get_logger
from utils.data_generator import generate_new_fio, create_email

loger = get_logger(__name__)
_new = Faker('ru_RU')


class HorillaClient:
    """Класс пользователя Horilla CRM"""
    def __init__(
            self,
            first_name: str = None,
            last_name: str = None,
            birth_date=None,
            email: str = None,
            phone_number: str = None,
            company: str = None):
        """
        Инициализация класса пользователя Horilla CRM
        :param first_name: имя
        :param last_name: фамилия
        :param birth_date: дата рождения
        :param email: адрес электронной почты
        :param phone_number: номер телефона
        :param company: компания клиента
        """
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.email = email
        self.phone_number = phone_number
        self.company = company

    def __call__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self

    def __str__(self, *args, **kwargs):
        """Строковое представление класса HorillaClient"""
        return f"""
            Имя: {self.first_name}
            Фамилия: {self.last_name}
            Дата рождения: {self.birth_date}
            Электронная почта: {self.email}
            Номер телефона: {self.phone_number}
            Компания: {self.company}
            """


class HorillaClientProvider:
    def __init__(self, context):
        self.context = context

    @step('Создать нового пользователя/клиента Horilla CRM')
    def get_new_client(self):
        client = HorillaClient()
        fio = generate_new_fio(split=True)
        client.first_name = fio[1]
        client.last_name = fio[0]
        client.birth_date = _new.date_between(start_date='-65y', end_date='-18y')
        client.email = create_email()
        client.company = _new.company()
        attach('Получены данные клиента', body=str(client))
        return client
