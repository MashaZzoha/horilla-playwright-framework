import time

from config.settings import settings
from factory.context import Context
from pages.base_page import BasePage
from utils.allure_utils import step
from utils.logger import get_logger

logger = get_logger(__name__)


class SalesPage(BasePage):
    """Класс страницы продаж (Sales)"""

    def __init__(self, context: Context, page_name: str):
        """
        Инициализация класса страницы продаж SalesPage
        :param context: вэб-контекст
        :param page_name: название страницы
        """
        super().__init__(context, page_name, page_file_name="sales_page.yaml")
        self.yaml_locator_loader.locator_registry(self.page_file_name)
        self.add_elements_to_check('Заголовок Leads', 'Меню Leads')
        self.check_page()

    @staticmethod
    def lead_owner():
        """Получить данные: имя и фамилию админа из settings.yaml"""
        first_name = settings.users['admin'].get('first_name')  # "Зинаида"
        last_name = settings.users['admin'].get('last_name')
        return f"{first_name} {last_name}"

    @step("Заполнить окно Lead Stage данными: '{status_name}', '{status_order}', '{probability}'")
    def _add_lead_stage(self, status_name: str = None, status_order: int = None, probability: int = None):
        """
        Заполнить окно Lead Stage
        :param status_name: Status Name
        :param status_order: Status Order
        :param probability: Probability
        """
        self.click('Кнопка Add Lead Stage')
        assert self.has_element('Окно Create Lead Stage'), 'Окно Create Lead Stage не открылось!'
        self.input_verify_batch({
            'Поле Status Name': status_name,
            'Поле Status Order': status_order,
            'Поле Probability': probability
        })
        self.click('Кнопка Save Lead Stage')
        return self

    @step('Заполнение одностраничной формы ')
    def single_step_add_new_lead(self):
        """Заполнить одностраничную форму Create Lead"""
        client = self.context.horilla_client
        self.open_form_new()
        assert self.has_element('Одностраничная форма'), 'Одностраничная форма не открылась!'
        self.select2_option_batch({
            'contact_number': '+7',
            'lead_source': client.lead_source,
            'lead_owner': self.lead_owner(),
            'industry': client.industry,
            'country': client.country})
        self.input_verify_batch({
            'Поле First Name': client.first_name,
            'Поле Last Name': client.last_name,
            'Поле Email': client.email,
            'Поле Number of Employees': client.employee_number,
            'Поле City': client.city,
            'Поле Zip': client.postal,
            'Поле Annual Revenue': client.annual_revenue,
            'Поле Lead Company': client.company,
            'Поле Contact Number': client.phone[2:],
            'Поле Requirements': self.context.test_data.requirements
        })
        self._add_lead_stage(
            status_name=client.status_name, status_order=client.status_order, probability=client.status_order)
        time.sleep(5)
        self.click('Кнопка Save')
        assert self.has_element('Алерт Успех Lead created'), 'Возможно, не произошло создание нового лида!'
        return self

    def multi_step_add_new_lead(self):
        """Заполнить многостраничную форму Create Lead"""
        client = self.context.horilla_client
        self.open_form_new()
        assert self.has_element('Одностраничная форма'), 'Одностраничная форма не открылась!'
        self.click('Кнопка Многостраничная форма')
        assert self.has_element('Многостраничная форма'), 'Многостраничная форма не открылась!'
        assert self.has_element('Прогресс-бар'), 'Не отобразился прогресс-бар шагов многостраничной формы!'
        assert self.has_element('Активная стадия прогресса', active_stage='Basic Information'), (
            "Не отобразилась активная стадия прогресса 'Basic Information'")
        self.select2_option_batch({
            'contact_number': '+7',
            'lead_source': client.lead_source,
            'lead_owner': self.lead_owner()})
        self.input_verify_batch({
            'Поле First Name': client.first_name,
            'Поле Last Name': client.last_name,
            'Поле Email': client.email,
            'Поле Contact Number': client.phone[2:]})
        self._add_lead_stage(
            status_name=client.status_name, status_order=client.status_order, probability=client.status_order)
        self.click('Кнопка Next')
        assert self.has_element('Активная стадия прогресса', active_stage='Company Details'), (
            "Не отобразилась активная стадия прогресса 'Company Details'")
        self.select2_option(selector_name='industry', option=client.industry)
        self.input_verify_batch({
            'Поле Number of Employees': client.employee_number,
            'Поле Annual Revenue': client.annual_revenue,
            'Поле Lead Company': client.company})
        assert self.has_element('Кнопка Previous'), 'Не отобразилась кнопка Previous!'
        self.click('Кнопка Next')
        assert self.has_element('Активная стадия прогресса', active_stage='Location'), (
            "Не отобразилась активная стадия прогресса 'Location'")
        self.select2_option(selector_name='country', option=client.country)
        self.input_verify_batch({'Поле City': client.city, 'Поле Zip': client.postal})
        assert self.has_element('Кнопка Previous'), 'Не отобразилась кнопка Previous!'
        self.click('Кнопка Next')
        assert self.has_element('Активная стадия прогресса', active_stage='Requirements'), (
            "Не отобразилась активная стадия прогресса 'Requirements'")
        self.input_text('Поле Requirements', self.context.test_data.requirements)
        assert self.has_element('Кнопка Previous'), 'Не отобразилась кнопка Previous!'
        assert self.has_element('Кнопка Save & New'), 'Не отобразилась кнопка Save & New!'
        assert self.has_element('Кнопка Save'), 'Не отобразилась кнопка Save!'
        time.sleep(5)
        self.click('Кнопка Save')
        assert self.has_element('Алерт Успех Lead created'), 'Возможно, не произошло создание нового лида!'
        return self
