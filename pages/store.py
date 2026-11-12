from factory.base_pages_store import BasePagesStore
from factory.context import Context
from pages.analytics_page import AnalyticsPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.my_jobs_page import MyJobsPage
from pages.people_page import PeoplePage
from pages.sales_page import SalesPage
from pages.schedule_page import SchedulePage


class HorillaStorePages(BasePagesStore):
    """Каталог страниц Horilla"""

    def __init__(self, context: Context, store='Магазин страниц Horilla'):
        super().__init__(context, store=store)

        self.page_registry([
            {'Страница Авторизации': LoginPage},
            {'Главная страница': HomePage},
            {'Страница вкладки Sales': SalesPage},
            {'Страница вкладки People': PeoplePage},
            {'Страница вкладки Analytics': AnalyticsPage},
            {'Страница вкладки Schedule': SchedulePage},
            {'Страница вкладки My Jobs': MyJobsPage}
        ])
