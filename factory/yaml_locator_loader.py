import os

import yaml
from playwright.sync_api import Page
from yaml.nodes import MappingNode

from utils.exceptions import RegistrationLocatorsException
from utils.logger import get_logger

logger = get_logger(__name__)

SUPPORTED_TYPES = ("role", "label", "placeholder", "text", "alt", "title", "test_id", "css", "xpath", "frame")
FILTER_KEYS = ('filter_text', 'filter_not_text')


class YamlLocatorsLoader:
    """Класс для проверки, регистрации, преобразования и загрузки локаторов из .yaml"""

    def __init__(self, page: Page, project_root: str, *locator_root_path: str):
        """
        Инициализация
        :param page: для загрузки семантических локаторов
        :param project_root: путь до корня проекта
        :param locator_root_path: путь до папки с локаторами
        """
        self.page = page
        self.project_root = project_root
        self.locator_root_path = os.path.join(self.project_root, *locator_root_path)
        self.check_exists(self.locator_root_path)
        self._locators = {}
        logger.info(f"Загрузчик локаторов инициализирован: {self.locator_root_path}")

    @staticmethod
    def check_exists(file_path):
        """Проверка существования папки или файла с локаторами"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл с локаторами не найден {file_path}")

    @staticmethod
    def _find_yaml_duplicates(file_path):
        """Поиск повторяющихся названий локаторов в .yaml"""
        warnings = []
        with open(file_path, 'rt', encoding='utf-8') as f:
            node = yaml.compose(f)

        if not isinstance(node, MappingNode):
            return warnings

        known = {}

        for key_node, _ in node.value:
            key = key_node.value.upper()
            line = key_node.start_mark.line + 1
            if key in known:
                warnings.append(f"{os.path.basename(file_path)}: дублирует локатор: '{key}'\n"
                                f"строка: {known[key]}, {line}")
            else:
                known[key] = line
        return warnings

    def locator_registry(self, page_file_name: str):
        """Регистрация локаторов для страницы из .yaml или из кода"""
        if page_file_name in self._locators:
            return self._locators[page_file_name]

        warnings = []

        file_path = os.path.join(self.locator_root_path, page_file_name)
        self.check_exists(file_path)

        # Поиск дубликатов по имени
        warnings.extend(self._find_yaml_duplicates(file_path))

        with open(file_path, 'rt', encoding='utf-8') as f:
            raw = yaml.safe_load(f) or {}
        all_locators = {k.upper(): v for k, v in raw.items()}

        # Поиск дубликатов по значению
        validated = {}
        known_values = {}

        for name, value in all_locators.items():
            if not isinstance(value, dict):
                warnings.append(f"Локатор '{name}': ожидаемый тип dict, получен: {type(value).__name__}")
                continue

            # регистрация локаторов для iframe
            if "frame" in value:
                result = self._validate_frame(name, value, warnings)
                if result is None:
                    continue
                locator_type, locator_value = result
            else:
                base_keys = [key for key in value if key not in FILTER_KEYS]
                if not base_keys:
                    warnings.append(f"Локатор '{name}': отсутствует базовый тип локатора (только filter_*)")
                    continue
                locator_type = base_keys[0]
                if locator_type not in SUPPORTED_TYPES:
                    warnings.append(f"Локатор '{name}': неподдерживаемый тип '{locator_type}'.\n"
                                    f"Поддерживаемые типы: {SUPPORTED_TYPES}")
                    continue

                locator_value = str(value[locator_type])
            fingerprint = tuple(sorted((k, str(v)) for k, v in value.items()))

            if fingerprint in known_values:
                warnings.append(
                    f"Локатор: {name} дублирует {known_values[fingerprint]} по значению:\n"
                    f"{locator_type}={locator_value}")
            else:
                known_values[fingerprint] = name

            validated[name] = value
            logger.debug(f"Добавлен локатор: {name} {locator_type}")

        if warnings:
            logger.error(f"{page_file_name}.yaml: Ошибка регистрации локаторов! "
                         f"Требуется проверка на разрешённые типы локаторов и наличие дублей.")
            raise RegistrationLocatorsException("\n".join(warnings))

        self._locators[page_file_name] = validated
        logger.info(f"{page_file_name}: зарегистрировано {len(validated)} локаторов")
        return validated

    @staticmethod
    def _build_locator(container, locator_data: dict, **kwargs):
        """Составляет локатор Locator внутри контейнера page или frame"""
        def _format(value: str) -> str:
            """Безопасно подставляет kwargs в шаблон."""
            try:
                return value.format(**kwargs)
            except KeyError as e:
                raise KeyError(
                    f"В шаблоне локатора не хватает параметра {e}. "
                    f"Шаблон: {value}. Переданы: {list(kwargs.keys())}"
                )

        get_locator_by = {
            "role": lambda c, loc: c.get_by_role(loc["role"], name=loc.get("name")),
            "label": lambda c, loc: c.get_by_label(loc["label"]),
            "placeholder": lambda c, loc: c.get_by_placeholder(loc["placeholder"]),
            "text": lambda c, loc: c.get_by_text(loc["text"], exact=loc.get("exact", False)),
            "alt": lambda c, loc: c.get_by_alt_text(loc["alt"]),
            "title": lambda c, loc: c.get_by_title(loc["title"]),
            "test_id": lambda c, loc: c.get_by_test_id(_format(loc["test_id"])),
            "css": lambda c, loc: c.locator(f"css={_format(loc['css'])}"),
            "xpath": lambda c, loc: c.locator(f"xpath={_format(loc['xpath'])}"),
        }

        base_locator = None
        for key, handler in get_locator_by.items():
            if key in locator_data:
                base_locator = handler(container, locator_data)
                break
        if base_locator is None:
            raise ValueError(
                f"Неизвестный тип локатора: {locator_data}\n"
                f"Поддерживаемые типы: {SUPPORTED_TYPES}")

        if 'filter_text' in locator_data:
            base_locator = base_locator.filter(has_text=_format(locator_data['filter_text']))
        if 'filter_not_text' in locator_data:
            base_locator = base_locator.filter(has_not_text=_format(locator_data['filter_not_text']))
        return base_locator

    @staticmethod
    def _validate_frame(name: str, value: dict, warnings: list):
        """Проверяет локатор для фрейма для последующей обработки из .yaml"""
        frame_data = value['frame']
        if not isinstance(frame_data, dict):
            warnings.append(f"Локатор '{name}' должен быть словарём")
            return
        if 'selector' not in frame_data or 'inner' not in frame_data:
            warnings.append(f"Локатор '{name}': 'frame' должен содержать 'selector' и 'inner'")
            return
        if not isinstance(frame_data['inner'], dict):
            warnings.append(f"Локатор '{name}': 'inner' должен быть словарём")
            return
        if not frame_data['inner']:
            warnings.append(f"Локатор '{name}': 'inner' не может быть пустым")
            return
        inner_keys = [key for key in frame_data['inner'] if key not in FILTER_KEYS]
        if not inner_keys:
            warnings.append(f"Локатор '{name}': во frame нет базового типа (только filter_*)")
        inner_type = inner_keys[0]
        if inner_type == 'frame':
            warnings.append(f"Локатор '{name}': вложенные frame не поддерживаются")
            return
        if inner_type not in SUPPORTED_TYPES:
            warnings.append(f"Локатор '{name}': неподдерживаемый тип внутри frame: '{inner_type}'")
            return
        return 'frame', frame_data['selector']

    def get_locator_by_name(self, page_file_name: str, locator_name: str, **kwargs):
        """Возвращает локатор по имени из YAML"""
        locators = self.locator_registry(page_file_name)
        locator_name = locator_name.upper().strip()

        if locator_name not in locators:
            raise KeyError(
                f"Локатор {locator_name} не найден в списке локаторов для страницы {page_file_name}")

        locator_data = locators[locator_name]

        if 'frame' in locator_data:
            frame_data = locator_data['frame']
            frame = self.page.frame_locator(frame_data['selector'])
            return self._build_locator(frame, frame_data['inner'], **kwargs)
        return self._build_locator(self.page, locator_data, **kwargs)
