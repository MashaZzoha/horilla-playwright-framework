import allure
import pytest

from utils.data_generator import get_random_word

wrong_username = get_random_word(min_size=5)
wrong_password = get_random_word(min_size=7)


@allure.story('Проверка страницы Sales')
@pytest.mark.sales_page_test
class TestSalesPage:
    @pytest.mark.parametrize('login_to_crm', [dict(Пользователь='admin')], indirect=True)
    def test_add_lead_singe_step_form(self, get_new_lead, login_to_crm):
        ctx = get_new_lead
        client = ctx.horilla_client
        home_page = login_to_crm
        sales_page = home_page.open_tab('Sales', 'Страница вкладки Sales')
        sales_page.single_step_add_new_lead()
        ctx.check.check_lead_created(client.email)

    @pytest.mark.parametrize('login_to_crm', [dict(Пользователь='admin')], indirect=True)
    def test_add_lead_multi_step_form(self, get_new_lead, login_to_crm):
        ctx = get_new_lead
        client = ctx.horilla_client
        home_page = login_to_crm
        sales_page = home_page.open_tab('Sales', 'Страница вкладки Sales')
        sales_page.multi_step_add_new_lead()
        ctx.check.check_lead_created(client.email)
