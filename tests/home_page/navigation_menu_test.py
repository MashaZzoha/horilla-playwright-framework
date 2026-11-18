import allure
import pytest

from utils.allure_utils import step


@allure.story('Проверка функциональности меню навигации на главной странице')
@pytest.mark.navigation_menu_test
class TestNavigationMenu:

    datasets = [
        ('Переход на вкладку Sales', 'Sales', 'Страница вкладки Sales'),
        ('Переход на вкладку People', 'People', 'Страница вкладки People'),
        ('Переход на вкладку Analytics', 'Analytics', 'Страница вкладки Analytics'),
        ('Переход на вкладку Schedule', 'Schedule', 'Страница вкладки Schedule'),
        ('Переход на вкладку My Jobs', 'My Jobs', 'Страница вкладки My Jobs')
    ]

    @allure.story('{title}')
    @pytest.mark.parametrize('title, button, tab_name', datasets, ids=[t[0] for t in datasets])
    @pytest.mark.parametrize('login_to_crm', [dict(Пользователь='admin')], indirect=True)
    def test_navigation_menu(self, context, login_to_crm, title, button, tab_name):
        with step("Открыть главную страницу"):
            home_page = login_to_crm
            home_page.open_tab(button, tab_name)
