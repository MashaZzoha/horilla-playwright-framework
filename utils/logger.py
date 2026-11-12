import logging
import logging.handlers
import os
import sys


class Logger:
    """Класс единожды настраивает логирование. Возвращает логи по названию."""

    def __init__(
            self,
            log_format: str = "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s",
            log_level: str = 'INFO',
            log_file: str = 'horilla.log'):
        """
        __init__
        :param log_format: формат логов
        :param log_level: уровень логирования
        :param log_file: файл для хранения логов
        """

        self.log_level = logging.getLevelName(os.environ.get('LOG_LEVEL', log_level).upper().strip())
        self.formatter = logging.Formatter(log_format)

        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        self.log_file = os.path.join(logs_dir, log_file)

        # xdist workers
        worker_id = os.environ.get('PYTEST_XDIST_WORKER')
        if worker_id:
            name, ext = os.path.splitext(log_file)
            log_file = f"{name}_{worker_id}{ext}"
        self.log_file = os.path.join(logs_dir, log_file)

        self._stream_handler = self._stream_handler(self.log_level, self.formatter)
        self._file_handler = self._rotating_file_handler(self.log_file, self.log_level, self.formatter)

    @staticmethod
    def _rotating_file_handler(file, log_level, formatter, max_bytes=5 * 1024 * 1024, backup_count=3):
        h = logging.handlers.RotatingFileHandler(
            file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
        )
        h.setLevel(log_level)
        h.setFormatter(formatter)
        return h

    @staticmethod
    def _stream_handler(log_level, formatter):
        h = logging.StreamHandler(sys.stdout)
        h.setLevel(log_level)
        h.setFormatter(formatter)
        return h

    def __call__(self, name: str = None) -> logging.Logger:
        """Единожды настраивает логирование. Возвращает логи по названию."""
        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)

        if not logger.handlers:
            logger.addHandler(self._stream_handler)
            logger.addHandler(self._file_handler)

        return logger


get_logger = Logger()
