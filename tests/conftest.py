import pytest

from utils.allure_utils import step
from utils.logger import get_logger

logger = get_logger(__name__)


@pytest.fixture(scope='function')
def login_to_crm(request, context):
    """Авторизоваться в приложении"""
    user = request.param['Пользователь']
    with step("Открыть страницу авторизации"):
        login_page = context.open_page("Страница Авторизации")
        page = login_page.auth(alias=user, success=True)
        yield page


@pytest.fixture(scope='function')
def get_new_client(context):
    """Получить нового клиента"""
    context.horilla_client_provider.create_new_client()
    return context


@pytest.fixture(scope='function')
def get_new_lead(context):
    """Получить потенциального клиента-лида"""
    context.horilla_client_provider.create_new_client(lead=True)
    return context
