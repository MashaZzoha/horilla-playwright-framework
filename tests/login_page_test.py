import allure
import pytest

from config.settings import settings
from utils.allure_utils import step
from utils.test_data import get_random_word

wrong_username = get_random_word(min_size=5)
wrong_password = get_random_word(min_size=7)


@allure.story('Проверка страницы авторизации')
@pytest.mark.login_page_test
class TestLoginPage:

    datasets = [
        ('Авторизация с валидными логином и паролем', settings.admin['username'], settings.admin['password'], True),
        ('Попытка авторизации с невалидным логином и невалидным паролем', wrong_username, wrong_password, False),
        ('Попытка авторизации без логина и пароля', '', '', False),
    ]

    @pytest.mark.parametrize('title, username, password, auth_success', datasets, ids=[t[0] for t in datasets])
    @allure.title('{title}')
    def test_verify_login(self, context, title, username, password, auth_success):
        ctx = context
        with step("Открыть страницу авторизации"):
            login_page = context.open_page("Страница Авторизации")
            login_page.auth(username, password, success=auth_success)
            ctx.check.check_user_exists('Department')
