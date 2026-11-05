import allure
import pytest
from utils.allure_utils import step


@allure.story('Проверка главной страницы')
@pytest.mark.main_page
class TestMainPage:

    def test_verify_main(self):
        with step("Открыть главную страницу"):
