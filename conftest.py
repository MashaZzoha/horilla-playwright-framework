import os
import allure
import pytest
from typing import Type
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from config.settings import settings
from factory.url_manager import URLManager
from factory.web_context import WebContext
from pages.store import ProjectStorePages
from utils.logger import get_logger

logger = get_logger(__name__)

SUPPORTED_BROWSERS = ("chromium", "firefox", "webkit")


def pytest_addoption(parser):
    """Добавляет флаг --all-browsers для запуска браузеров"""
    parser.addoption(
        "--all-browsers",
        action="store_true",
        default=False,
        help=f"Прогнать тесты во всех браузерах ({str(SUPPORTED_BROWSERS)})")


def pytest_configure(config):
    """
    Определить список браузеров по приоритету:
    1. --all-browsers → все три
    2. --browser → явный выбор
    3. BROWSER (env) → из переменной
    4. По умолчанию → chromium
    """
    # --all-browsers
    if config.getoption("--all-browsers"):
        config.option.browser = ["chromium", "firefox", "webkit"]
        return
    if config.option.browser:
        return
    env_browser = os.environ.get("BROWSER", "").strip().lower()
    if env_browser in ("chromium", "firefox", "webkit"):
        config.option.browser = [env_browser]
        return
    # chromium по умолчанию
    config.option.browser = ["chromium"]


@pytest.fixture(scope='session')
def browser(browser_name: str):
    """Запуск браузера (--browser/BROWSER/по умолчанию)"""
    playwright = sync_playwright().start()
    try:
        browser_type = getattr(playwright, browser_name)
        args = [] if settings.headless else ["--start-maximized"]
        browser = browser_type.launch(headless=settings.headless, args=args)
        yield browser
        browser.close()
    finally:
        playwright.stop()


@pytest.fixture(scope='function')
def context(browser: Browser):
    """Новый контекст для каждого теста"""
    if settings.headless:
        context = browser.new_context()
    else:
        context = browser.new_context(no_viewport=True)
    yield context
    context.close()


@pytest.fixture(scope='function')
def page(context: BrowserContext):
    """Новая страница для каждого теста"""
    page = context.new_page()
    yield page
    page.close()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'call' and rep.failed:
        page = item.funcargs.get('page')
        if page:
            screenshot = page.screenshot()
            allure.attach(
                screenshot,
                name='Скриншот на падении теста',
                attachment_type=allure.attachment_type.PNG
            )


@pytest.fixture(scope="function")
def url_manager() -> URLManager:
    """URL-менеджер с зарегистрированными адресами"""
    manager = URLManager(base_url=settings.base_url)
    manager.registry_urls([{}])
    return manager


@pytest.fixture(scope='function')
def web_context(page: Page, url_manager: Type[URLManager]) -> WebContext:
    """Вэб-контекст: page + создаётся locator_loader + url_manager + store_pages"""
    return WebContext(page=page, store_pages=ProjectStorePages, url_manager=url_manager)
