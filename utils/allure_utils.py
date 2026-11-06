import json
import os.path
import shutil
from contextlib import contextmanager
from typing import Union

import allure
from allure_commons.types import AttachmentType
from lxml import etree
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page

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


def build_environment_xml(path: str, params: dict):
    """
    Создать environment.xml с параметрами окружения
    :param path: путь до environment.xml
    :param params: словарь параметров
    :return: путь до созданного файла
    """
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
    """Копирует environment.xml в папку Allure-отчёта"""
    if not allure_dir or not os.path.isdir(allure_dir):
        logger.warning(f"alluredir не найден: {allure_dir}. environment.xml не скопирован")
        return
    if not os.path.exists(env_path):
        logger.warning(f"environment.xml не найден: {env_path}")
        return
    shutil.copy(env_path, os.path.join(allure_dir, 'environment.xml'))
    logger.debug(f"environment.xml скопирован в {allure_dir}")
