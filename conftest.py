import allure
import pytest
from pytest import fixture
from playwright.sync_api import sync_playwright, Browser, Page


@fixture(scope='session')
def browser_setup(context):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=False,
        args=["--start-maximized"])
    yield browser
    browser.close()
    playwright.stop()


@fixture(scope='function')
def context(browser: Browser):
    context = browser.new_context(no_viewport=True)
    yield context
    context.close()


@fixture()
def page(browser: Browser):
    page = browser.new_page()
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
