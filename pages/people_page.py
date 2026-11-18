import random
import time

from factory.context import Context
from pages.base_page import BasePage
from utils.allure_utils import attach, step
from utils.logger import get_logger

logger = get_logger(__name__)


class PeoplePage(BasePage):
    """Класс страницы пользователей (People)"""

    def __init__(self, context: Context, page_name: str):
        """
        Инициализация класса страницы пользователей PeoplePage
        :param context: вэб-контекст
        :param page_name: название страницы
        """
        super().__init__(context, page_name, page_file_name="people_page.yaml")
        self.yaml_locator_loader.locator_registry(self.page_file_name)
        self.add_elements_to_check('Заголовок Accounts', 'Меню Accounts')
        self.check_page()
        self.check_active_tab(tab='People')

    @step('Является ли партнёром: {partner}')
    def is_partner(self, partner: bool = None):
        """
        Включить переключатель Is Partner
        :param partner: True - включить Is Partner
        """
        partner_ = random.choice([True, False])
        partner = partner_ if not partner else partner
        if partner:
            self.click('Переключатель Is Partner')
        attach('Партнёр: ', str(partner))
        return self

    @step('Заполнение одностраничной формы Create Account')
    def single_step_create_account(self):
        """Заполнить одностраничную форму Create Account"""
        client = self.context.horilla_client
        self.open_form_new('Форма Create Account')
        assert self.has_element('Одностраничная форма account'), 'Одностраничная форма Create Account не открылась!'
        self.select2_option_batch({
            'contact_number': '+7',
            'account_source': client.acc_source,
            'account_owner': self.get_owner(),
            'account_type': client.acc_type,
            'industry': client.industry,
            'ownership': client.ownership})
        self.is_partner(partner=False)
        self.input_verify_batch({
            'Поле Account Name': client.acc_name,
            'Поле Rating': client.rating,
            'Поле Contact Number': client.phone[2:],
            'Поле Account Number': client.acc_number,
            'Поле Website': client.website,
            'Поле Account Site': client.website,
            'Поле Billing City': client.city,
            'Поле Billing Zip': client.postal,
            'Поле Shipping City': client.shipping_city,
            'Поле Shipping Zip': client.shipping_postal,
            'Поле Annual Revenue': client.annual_revenue,
            'Поле Number of Employees': client.employee_number,
            'Поле Description': self.context.test_data.description})
        self.click('Кнопка Save', timeout=10000)
        assert self.has_element('Алерт Успех Account created'), 'Возможно, не произошло создание нового профиля!'
        return self

    def multi_step_create_account(self):
        """Заполнить многостраничную форму Create Lead"""
        client = self.context.horilla_client
        self.open_form_new('Форма Create Account')
        assert self.has_element('Одностраничная форма account'), 'Одностраничная форма Create Account не открылась!'
        self.click('Кнопка Многостраничная форма')
        assert self.has_element('Многостраничная форма account'), 'Многостраничная форма Create Account не открылась!'
        assert self.has_element('Прогресс-бар'), 'Не отобразился прогресс-бар шагов многостраничной формы!'
        assert self.has_element('Активная стадия прогресса', active_stage='Account Information'), (
            "Не отобразилась активная стадия прогресса 'Account Information'")
        self.select2_option_batch({
            'contact_number': '+7',
            'account_source': client.acc_source,
            'account_owner': self.get_owner(),
            'account_type': client.acc_type})
        self.input_verify_batch({
            'Поле Account Name': client.acc_name,
            'Поле Rating': client.rating,
            'Поле Contact Number': client.phone[2:],
            'Поле Account Number': client.acc_number,
            'Поле Website': client.website,
            'Поле Account Site': client.website})
        self.click('Кнопка Next')
        assert self.has_element('Активная стадия прогресса', active_stage='Address Information'), (
            "Не отобразилась активная стадия прогресса 'Address Information'")
        self.input_verify_batch({
            'Поле Billing City': client.city,
            'Поле Billing Zip': client.postal,
            'Поле Shipping City': client.shipping_city,
            'Поле Shipping Zip': client.shipping_postal})
        assert self.has_element('Кнопка Previous', timeout=10000), 'Не отобразилась кнопка Previous!'
        self.click('Кнопка Next')
        self.input_verify_batch({
            'Поле Number of Employees': client.employee_number,
            'Поле Annual Revenue': client.annual_revenue})
        self.is_partner(partner=True)
        self.select2_option_batch({'industry': client.industry, 'ownership': client.ownership})
        assert self.has_element('Активная стадия прогресса', active_stage='Additional Information'), (
            "Не отобразилась активная стадия прогресса 'Additional Information'")
        assert self.has_element('Кнопка Previous'), 'Не отобразилась кнопка Previous!'
        self.click('Кнопка Next')
        assert self.has_element('Активная стадия прогресса', active_stage='Description'), (
            "Не отобразилась активная стадия прогресса 'Description'")
        self.input_text('Поле Description', self.context.test_data.description)
        assert self.has_element('Кнопка Previous'), 'Не отобразилась кнопка Previous!'
        assert self.has_element('Кнопка Save & New'), 'Не отобразилась кнопка Save & New!'
        self.click('Кнопка Save', timeout=10000)
        assert self.has_element('Алерт Успех Account was created'), 'Возможно, не произошло создание нового профиля!'
        return self
