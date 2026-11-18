import allure
import pytest


@allure.story('Проверка страницы People')
@pytest.mark.people_page_test
class TestPeoplePage:
    @pytest.mark.parametrize('login_to_crm', [dict(Пользователь='admin')], indirect=True)
    def test_create_account_singe_step_form(self, get_new_client, login_to_crm):
        ctx = get_new_client
        client = ctx.horilla_client
        home_page = login_to_crm
        people_page = home_page.open_tab('People', 'Страница вкладки People')
        people_page.single_step_create_account()
        ctx.check.check_account_created(client.phone)

    @pytest.mark.parametrize('login_to_crm', [dict(Пользователь='admin')], indirect=True)
    def test_create_account_multiple_step_form(self, get_new_client, login_to_crm):
        ctx = get_new_client
        client = ctx.horilla_client
        home_page = login_to_crm
        people_page = home_page.open_tab('People', 'Страница вкладки People')
        people_page.multi_step_create_account()
        ctx.check.check_account_created(client.phone)
