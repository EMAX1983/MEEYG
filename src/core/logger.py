import logging
import logging.handlers
import sys
from pathlib import Path

import structlog
from structlog.processors import JSONRenderer, TimeStamper

from src.core.config import settings


def setup_logger() -> structlog.BoundLogger:
    """Настраивает structlog для вывода в консоль и в файл."""
    log_file = settings.logs_dir / "app.log"
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Общие обработчики для всех логов
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=False),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=shared_processors
        + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Форматтер для консоли: цветной и читаемый
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(colors=True),
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)

    # Форматтер для файла: JSON для машинной обработки
    file_formatter = structlog.stdlib.ProcessorFormatter(
        processor=JSONRenderer(),
    )
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)

    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Очищаем предыдущие обработчики
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(log_level)

    # Приглушаем слишком "болтливые" библиотеки
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.WARNING)

    return structlog.get_logger()


# Инициализируем и экспортируем логгер
logger = setup_logger()
