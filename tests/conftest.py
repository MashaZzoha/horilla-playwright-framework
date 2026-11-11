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
