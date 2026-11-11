import allure
import pytest

from utils.allure_utils import step


@allure.story('Проверка главной страницы')
@pytest.mark.main_page_test
class TestMainPage:
    @pytest.mark.parametrize('login_to_crm', [dict(Пользователь='admin')], indirect=True)
    def test_verify_main(self, context, login_to_crm):
        with step("Открыть главную страницу"):
            main_page = login_to_crm
