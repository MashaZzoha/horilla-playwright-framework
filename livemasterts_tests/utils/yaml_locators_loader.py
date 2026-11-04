import os
import yaml
from playwright.sync_api import Page


class YamlLocatorsLoader:
    """Класс для преобразования и загрузки локаторов из .yaml"""
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
        self._cache = {}

    @staticmethod
    def check_exists(file_path):
        """Проверка существования папки или файла с локаторами"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл с локаторами не найден {file_path}")

    def _load_file(self, page_name: str):
        """Читает и кэширует локатор из YAML"""
        if page_name not in self._cache:
            file_path = os.path.join(self.locator_root_path, f"{page_name}.yaml")
            self.check_exists(file_path)
            with open(file_path, 'rt', encoding='utf-8') as f:
                self._cache[page_name] = yaml.safe_load(f) or {}
        return self._cache[page_name]

    def get_locator_by_name(self, page_name: str, locator_name: str, **kwargs):
        """Возвращает локатор по имени из YAML"""
        locators = self._load_file(page_name)
        locator_name = locator_name.upper()
        if locator_name not in locators:
            raise KeyError(f"Локатор {locator_name} не найден в списке локаторов для страницы {page_name}.yaml")

        locator_data = locators[locator_name]

        def _format(value: str) -> str:
            """Безопасно подставляет kwargs в шаблон."""
            try:
                return value.format(**kwargs)
            except KeyError as e:
                raise KeyError(
                    f"В шаблоне локатора '{locator_name}' не хватает параметра {e}. "
                    f"Шаблон: {value}. Переданы: {list(kwargs.keys())}"
                )

        get_locator_by = {
            "role": lambda l: self.page.get_by_role(l["role"], name=l.get("name")),
            "label": lambda l: self.page.get_by_label(l["label"]),
            "placeholder": lambda l: self.page.get_by_placeholder(l["placeholder"]),
            "text": lambda l: self.page.get_by_text(l["text"], exact=l.get("exact", False)),
            "alt": lambda l: self.page.get_by_alt_text(l["alt"]),
            "title": lambda l: self.page.get_by_title(l["title"]),
            "test_id": lambda l: self.page.get_by_test_id(_format(l["test_id"])),
            "css": lambda l: self.page.locator(f"css={_format(l['css'])}"),
            "xpath": lambda l: self.page.locator(f"xpath={_format(l['xpath'])}"),
        }

        for key, handler in get_locator_by.items():
            if key in locator_data:
                return handler(locator_data)

        raise ValueError(
            f"Неизвестный тип локатора '{locator_name}': {locator_data}\n"
            "Поддерживаемые типы: ['role', 'label', 'placeholder', 'text', 'alt', "
            "'title', 'test_id', 'css', 'xpath']")
