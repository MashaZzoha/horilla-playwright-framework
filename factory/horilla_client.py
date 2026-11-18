import random

from faker import Faker

from utils.allure_utils import attach, step
from utils.data_generator import (city_postal, create_email,
                                  generate_business_data, generate_new_fio,
                                  generate_requirements, mobile_provider_codes)
from utils.logger import get_logger

loger = get_logger(__name__)
_new = Faker('ru_RU')
_new.text(max_nb_chars=50)


class HorillaClient:
    """Класс личных и деловых данных пользователя/клиента Horilla CRM"""

    def __init__(
            self,
            first_name: str = None,
            last_name: str = None,
            birth_date=None,
            email: str = None,
            phone: str = None,
            country: str = None,
            city: str = None,
            postal: int = None,
            company: str = None,
            industry: str = None,
            ownership: str = None,
            employee_number: int = None,
            annual_revenue: int = None):
        """
        Инициализация класса пользователя Horilla CRM
        :param first_name: имя
        :param last_name: фамилия
        :param birth_date: дата рождения
        :param email: адрес электронной почты
        :param phone: номер телефона
        :param country: страна
        :param city: адрес клиента
        :param postal: почтовый индекс клиента
        :param company: компания
        :param industry: отрасль
        :param ownership: юридическая форма собственности
        :param employee_number: количество работников
        :param annual_revenue: годовая выручка
        """
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.email = email
        self.phone = phone
        self.country = country
        self.city = city
        self.postal = postal
        self.company = company
        self.industry = industry
        self.ownership = ownership
        self.employee_number = employee_number
        self.annual_revenue = annual_revenue

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
            Номер телефона: {self.phone}
            Страна: {self.country}
            Город: {self.city}
            Почтовый индекс: {self.postal}
            Компания: {self.company}
            Отрасль: {self.industry}
            Форма собственности: {self.ownership}
            Количество работников: {self.employee_number}
            Годовая выручка: {self.annual_revenue}
            """


class HorillaClientProvider:
    """Провайдер работы с объектом HorillaClient"""

    def __init__(self, context):
        """
        Инициализация класса-провайдера работы с объектами HorillaClient
        :param context: вэб-контекст
        """
        self.context = context

    @step('Создать нового пользователя/клиента Horilla CRM')
    def create_new_client(
            self,
            industry: str = None,
            lead_source: str = None,
            country: str = None,
            status_name: str = None,
            status_order: int = None,
            probability: int = None,
            lead: bool = False):
        """
        Создать нового клиента
        :param industry: отрасль
        :param lead_source: источник потенциального клиента
        :param country: страна
        :param status_name: название статуса
        :param status_order: очередь
        :param probability: % возможного исхода
        :param lead: True-добавить данные для создания лида
        :return: HorillaClient
        """
        client = HorillaClient()
        fio = generate_new_fio(split=True)
        client.first_name = fio[1]
        client.last_name = fio[0]
        client.birth_date = _new.date_between(start_date='-65y', end_date='-18y')
        client.email = create_email()
        client.company = _new.company()
        self.__set_phone_number(client)
        self.__set_country(client, country=country)
        self.__set_city_postal(client)
        self.__set_additional_data(client)
        self.__set_employee_number(client)
        self.__set_annual_revenue(client)
        self.context.horilla_client = client
        if lead:
            self.__set_new_lead_data(
                industry=industry,
                lead_source=lead_source,
                status_name=status_name,
                status_order=status_order,
                probability=probability)
        attach('Получены данные клиента', body=str(client))
        return client

    @step('Установить страну клиента {country}')
    def __set_country(self, client: HorillaClient, country: str = None):
        client.country = 'Russia' if not country else country
        return client

    @step('Установить клиенту дополнительные параметры: acc_source, ownership, industry, acc_type')
    def __set_additional_data(self, client: HorillaClient):
        client.acc_source, client.ownership, client.industry, client.acc_type = generate_business_data()
        return client

    @step('Установить клиенту количество работников')
    def __set_employee_number(self, client: HorillaClient):
        client.employee_number = random.randint(5, 1000)
        return client

    @step('Установить компании клиента размер годовой выручки')
    def __set_annual_revenue(self, client: HorillaClient):
        client.annual_revenue = random.randint(10000000, 1000000001)
        return client

    @step('Установить клиенту номер мобильного телефона')
    def __set_phone_number(self, client: HorillaClient):
        operator_code = random.choice(mobile_provider_codes)
        client.phone = f'+7{operator_code}{random.randrange(1000000, 9999999)}'
        return client

    @step('Установить клиенту город и почтовый индекс')
    def __set_city_postal(self, client: HorillaClient):
        city, postal = random.choice(list(city_postal.items()))
        client.city = city
        client.postal = str(postal)
        return client

    @step('Установить данные для нового лида')
    def __set_new_lead_data(
            self,
            industry: str = None,
            lead_source: str = None,
            status_name: str = None,
            status_order: int = None,
            probability: int = None):
        """
        Установить данные для нового лида
        :param industry: отрасль
        :param lead_source: источник лида
        :param status_name: название статуса
        :param status_order: очередь
        :param probability: % благоприятного исхода
        """
        client = self.context.horilla_client
        client.industry = client.industry if not industry else industry
        client.lead_source = client.acc_source if not lead_source else lead_source
        client.status_name = random.choice(['New', 'Contacted', 'Qualified']) if not status_name else status_name
        client.status_order = random.choice([1, 2, 3]) if not status_order else status_order
        client.probability = random.randint(10, 100) if not probability else probability
        self.context.test_data.requirements = generate_requirements()
        lead_status = [client.status_name, client.status_order, client.probability]
        attach('Статус лида: ', body=str(lead_status))
        return client
