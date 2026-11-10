import json
import os.path
import shutil
from datetime import datetime
from functools import wraps
from typing import Union

import allure
from allure_commons._allure import StepContext
from allure_commons import plugin_manager
from allure_commons.types import AttachmentType
from allure_commons.utils import func_parameters, represent
from lxml import etree
from playwright.sync_api import Page

from utils.logger import get_logger

logger = get_logger(__name__)


# ----------------------------- Вложения -----------------------------

def attach(name: str, body: Union[str, bytes] = '', attachment_type=AttachmentType.TEXT):
    """Прикрепляет и логирует вложения к Allure-отчёту."""
    if attachment_type != AttachmentType.TEXT:
        logger.debug(f"Allure attachment: {name} -> {attachment_type}")
    else:
        logger.debug(f"Allure attachment: {name}: {body}")
    allure.attach(name=name, body=body, attachment_type=attachment_type)


def attach_screenshot(page: Page, name: str = 'screenshot'):
    """Делает скриншот и прикрепляет его к Allure-отчёту."""
    screenshot = page.screenshot()
    attach(name, screenshot, AttachmentType.PNG)


def attach_json(data: dict, name: str = 'JSON'):
    """Прикрепляет JSON к Allure-отчёту."""
    body = json.dumps(data, ensure_ascii=False, indent=2)
    attach(name, body, AttachmentType.JSON)


# ----------------------------- Шаги -----------------------------

def step(title):
    """Шаг Allure: работает и как декоратор, и как контекст-менеджер.
    Декоратор: подставляет аргументы функции в {placeholders};
    Контекст: логирует начало/конец шага.
    """
    if callable(title):
        return StepContextWrap(title.__name__, {}, True)(title)
    return StepContextWrap(title, {})


class StepContextWrap(StepContext):

    def __init__(self, title, params, is_callable=False):
        super().__init__(title, params)
        self.is_callable = is_callable
        self.start_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S.%f")

    def log_step(self, action, title=None):
        if title is None:
            title = self.title
        logger.info('{} step: {}'.format(action, title))

    def _allure_step(self, title=None):
        if title is None:
            title = self.title
        return "[{}] {}".format(self.start_time, title)

    def __enter__(self):
        plugin_manager.hook.start_step(
            uuid=self.uuid,
            title=self._allure_step(),
            params=self.params,
        )
        if self.is_callable is False:
            self.log_step('Start')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            logger.error('STEP FAILED! Reason:\n{}'.format(exc_val))
        if self.is_callable is False:
            self.log_step('End')

        plugin_manager.hook.stop_step(
            uuid=self.uuid,
            title=self._allure_step(),
            exc_type=exc_type,
            exc_val=exc_val,
            exc_tb=exc_tb,
        )

    def __call__(self, func):
        @wraps(func)
        def impl(*a, **kw):
            __tracebackhide__ = True
            params = func_parameters(func, *a, **kw)
            args = list(map(lambda x: represent(x), a))
            title = self.title.format(*args, **params)     # ← подстановка {locator}
            with StepContextWrap(title, params):
                return func(*a, **kw)
        return impl


# ----------------------------- Окружение -----------------------------

def build_environment_xml(path: str, params: dict):
    """Создать environment.xml с параметрами окружения."""
    root = etree.Element('environment')
    for key, value in params.items():
        param = etree.SubElement(root, 'parameter')
        etree.SubElement(param, 'key').text = str(key)
        etree.SubElement(param, 'value').text = str(value)
    with open(path, 'wb') as f:
        f.write(etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='utf-8'))
    logger.debug(f"environment.xml создан: {path}")
    return path


def copy_environment_to(allure_dir: str, env_path: str):
    """Копирует environment.xml в папку Allure-отчёта."""
    if not allure_dir or not os.path.isdir(allure_dir):
        logger.warning(f"alluredir не найден: {allure_dir}. environment.xml не скопирован")
        return
    if not os.path.exists(env_path):
        logger.warning(f"environment.xml не найден: {env_path}")
        return
    shutil.copy(env_path, os.path.join(allure_dir, 'environment.xml'))
    logger.debug(f"environment.xml скопирован в {allure_dir}")
