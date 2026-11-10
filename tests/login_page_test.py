import allure
import pytest

from utils.allure_utils import step


@allure.story('Проверка страницы авторизации')
@pytest.mark.login_page_test
class TestMainPage:

    def test_verify_login(self, pages, browser_page):
        with step("Открыть страницу авторизации"):
            pages.open_page("Страница Авторизации")
