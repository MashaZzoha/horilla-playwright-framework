import allure
import json
from typing import Union
from contextlib import contextmanager
from allure_commons.types import AttachmentType
from playwright.sync_api import Page, Error as PlaywrightError
from utils.logger import get_logger

logger = get_logger(__name__)


def attach(name: str, body: Union[str, bytes] = '', attachment_type=AttachmentType.TEXT):
    """Прикрепляет и логирует шаги и вложения к Аллюр-отчёту"""
    if attachment_type != AttachmentType.TEXT:
        logger.debug(f"Allure attachment: {name} -> {attachment_type}")
    else:
        logger.debug(f"Allure attachment: {name}: {body}")
    allure.attach(name=name, body=body, attachment_type=attachment_type)


def attach_screenshot(page: Page, name: str = 'screenshot'):
    """Делает скриншот и прикрепляет его к Аллюр-отчёту"""
    screenshot = page.screenshot()
    attach(name, screenshot, AttachmentType.PNG)


def attach_json(data: dict, name: str = 'JSON'):
    """Прикрепляет JSON к Аллюр-отчёту"""
    body = json.dumps(data, ensure_ascii=False, indent=2)
    attach(name, body, AttachmentType.JSON)


@contextmanager
def step(title: str, page: Page = None):
    """Шаг с логированием начала и конца для Аллюр-отчёта"""
    logger.info(f"START STEP: {title}")
    try:
        with allure.step(title):
            yield
    except Exception as e:
        logger.error(f"STEP FAILED: {e}")
        if page:
            try:
                attach_screenshot(page, f"STEP FAILED: {title}")
            except PlaywrightError as err:
                logger.error(f"Не удалось сделать скриншот для шага {title}: {err}")
        raise
    finally:
        logger.info(f"END STEP: {title}")
