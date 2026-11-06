import os
from pathlib import Path
from types import SimpleNamespace

import yaml

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
TRACE_DIR = Path("tmp/traces")

_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
_SETTINGS_PATH = os.path.join(_CONFIG_DIR, "settings.yaml")

_settings_cache = None


def load_settings():
    """Читает и кэширует результат из config/settings.yaml и кэширует результат"""
    global _settings_cache
    if _settings_cache is None:
        if not os.path.exists(_SETTINGS_PATH):
            raise FileNotFoundError(f"Файл настроек не найден: {_SETTINGS_PATH}")
        with open(_SETTINGS_PATH, 'rt', encoding='utf-8') as f:
            _settings_cache = yaml.safe_load(f) or {}
    return _settings_cache


def get_settings(key: str, default=None):
    """Возвращает значение настройки по ключу"""
    return load_settings().get(key, default)


settings = SimpleNamespace(**load_settings())
