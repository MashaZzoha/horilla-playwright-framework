import os
import shutil
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright

from config.settings import settings
from factory.pages import Pages
from factory.url_manager import URLManager
from factory.web_context import WebContext
from pages.store import NalogStorePages
from utils.allure_utils import build_environment_xml, copy_environment_to
from utils.logger import get_logger

logger = get_logger(__name__)

SUPPORTED_BROWSERS = ("chromium", "firefox", "webkit")

VIDEO_DIR = Path("tmp/videos")
TRACES_DIR = Path("tmp/traces")


def pytest_addoption(parser):
    """Добавляет флаг --all-browsers для запуска во всех браузерах"""
    parser.addoption(
        "--all-browsers",
        action="store_true",
        default=False,
        help=f"Прогнать тесты во всех браузерах ({str(SUPPORTED_BROWSERS)})")


def _get_browser_from_env():
    """Браузер из BROWSER или chromium по умолчанию"""
    env_browser = os.environ.get('BROWSER', '').strip().lower()
    if env_browser in SUPPORTED_BROWSERS:
        return env_browser
    if env_browser:
        logger.warning(f"Браузер '{env_browser}' не поддерживается. "
                       f"Допустимые браузеры: {SUPPORTED_BROWSERS}. Будет использован 'chromium'.")
    return "chromium"


# def pytest_configure(config):
#     """
#     Определить браузер по приоритету:
#     1. --all-browsers → параметризация в pytest_generate_tests
#     2. --browser → явный выбор
#     3. BROWSER (env) → из переменной
#     4. По умолчанию → chromium
#     """
#     shutil.rmtree(VIDEO_DIR, ignore_errors=True)
#     VIDEO_DIR.mkdir(parents=True, exist_ok=True)
#     shutil.rmtree(TRACES_DIR, ignore_errors=True)
#     TRACES_DIR.mkdir(parents=True, exist_ok=True)
#
#     if config.getoption("--all-browsers"):
#         return
#     if getattr(config.option, 'browser', None):
#         return
#     config.option.browser = _get_browser_from_env()


# def pytest_generate_tests(metafunc):
#     """--all-browsers - параметризация browser_name"""
#     if 'browser_name' not in metafunc.fixturenames:
#         return
#     if metafunc.config.getoption('--all-browsers'):
#         metafunc.parametrize('browser_name', list(SUPPORTED_BROWSERS))
#     else:
#         browser = getattr(metafunc.config.option, 'browser', None) or _get_browser_from_env()
#         metafunc.parametrize('browser_name', [browser])


def pytest_make_parametrize_id(config, val):
    """Читаемый формат ID параметризованных тестов"""
    return repr(val)

# -------------------------------- Фикстуры ---------------------------------------------------------------------------


@pytest.fixture(scope='session')
def playwright_instance():
    """Единый sync_playwright на сессию"""
    pw = sync_playwright().start()
    try:
        yield pw
    finally:
        pw.stop()


@pytest.fixture(scope='session')
def browser(playwright_instance, browser_name: str):
    """Запуск браузера. Пересоздаётся на каждый браузер(browser_name) при --all-browsers"""
    if browser_name not in SUPPORTED_BROWSERS:
        raise ValueError(f"Неподдерживаемый браузер '{browser_name}'. Допустимые: {SUPPORTED_BROWSERS}")

    launch_args = []
    if not settings.headless and browser_name == 'chromium':
        launch_args.append('--start-maximized')

    browser_type = getattr(playwright_instance, browser_name)
    browser = browser_type.launch(headless=settings.headless, args=launch_args)
    try:
        yield browser
    finally:
        browser.close()


@pytest.fixture(scope='function')
def browser_context(browser: Browser, request):
    """Новый контекст для каждого теста: viewport + видео + трассировка"""
    ctx = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=str(VIDEO_DIR),
        record_video_size={"width": 1280, "height": 720},
    )
    ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    try:
        yield ctx
    finally:
        page = ctx.pages[0] if ctx.pages else None
        video_path = None
        if page and page.video:
            try:
                video_path = page.video.path()
            except PlaywrightError as e:
                logger.warning(f"Не удалось получить путь к видео: {e}")
                video_path = None

        rep = getattr(request.node, 'rep_call', None)
        failed = rep is not None and rep.failed
        if failed:
            safe_name = request.node.name.replace('/', '_').replace('::', '_')
            trace_path = TRACES_DIR / f'{safe_name}.zip'
            try:
                ctx.tracing.stop(path=str(trace_path))
                allure.attach.file(
                    str(trace_path), name=f'trace_{safe_name}.zip', attachment_type=allure.attachment_type.ZIP)
            except PlaywrightError as e:
                logger.warning(f"Не удалось сохранить trace: {e}")
        else:
            try:
                ctx.tracing.stop()
            except PlaywrightError as e:
                logger.warning(f"Не удалось остановить tracing: {e}")

        ctx.close()

        if video_path and os.path.exists(video_path):
            if failed:
                allure.attach.file(
                    video_path, name='video_failed.webm',
                    attachment_type=allure.attachment_type.WEBM)
            else:
                try:
                    os.remove(video_path)
                except OSError as e:
                    logger.warning(f"Не удалось удалить видео: {e}")


@pytest.fixture(scope='function')
def browser_page(browser_context: BrowserContext):
    """Новая страница для каждого теста"""
    page = browser_context.new_page()
    try:
        yield page
    finally:
        page.close()

# ------------------------------ environment.xml и скриншоты для Allure -----------------------------------------------


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f'rep_{rep.when}', rep)

    if rep.when not in ('call', 'setup') or not rep.failed:
        return

    browser_page = item.funcargs.get('page')
    if browser_page is None:
        return
    try:
        screenshot = browser_page.screenshot()
        allure.attach(
            screenshot,
            name=f'Скриншот на падении ({rep.when})',
            attachment_type=allure.attachment_type.PNG
        )
    except PlaywrightError as e:
        logger.warning(f"Не удалось сделать скриншот '{item.name}': {e}")


@pytest.fixture(scope='function')
def allure_env(tmpdir_factory):
    """Путь до environment.xml"""
    return tmpdir_factory.mktemp('allure').join('environment.xml').strpath


@pytest.fixture(scope='function')
def write_allure_env(request, allure_env):
    """Заполняет environment.xml и копирует в alluredir после тестов"""
    build_environment_xml(allure_env, {
        "Browser": getattr(settings, "browser", "chromium"),
        "Headless": getattr(settings, "headless", True),
        "Environment": getattr(settings, "env", "local"),
        "Base URL": getattr(settings, "base_url", "n/a")
    })

    yield

    allure_dir = request.config.getoption("--alluredir", default="", skip=True)
    copy_environment_to(allure_dir, allure_env)

# ------------------------------ URL / WebContext ---------------------------------------------------------------------


@pytest.fixture(scope="function")
def url_manager() -> URLManager:
    """URL-менеджер с зарегистрированными адресами"""
    manager = URLManager(base_url=settings.base_url)
    manager.registry_urls([
        {"Главная страница": {"path": "/"}},
    ])
    return manager


@pytest.fixture(scope='function')
def web_context(browser_page: Page, url_manager: URLManager) -> WebContext:
    """Вэб-контекст: page + создаётся locator_loader + url_manager + store_pages"""
    return WebContext(browser_page=browser_page, store_pages=NalogStorePages, url_manager=url_manager)


@pytest.fixture(scope='function')
def pages(web_context: WebContext):
    """Точка входа в управление текущей страницей"""
    return Pages(web_context)


@pytest.fixture(scope='function')
def store_pages(web_context: WebContext):
    """Экземпляр каталога страниц, созданный внутри WebContext."""
    return web_context.store_pages
