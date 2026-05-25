import logging
import logging.handlers
from pathlib import Path

import structlog
from structlog.processors import (
    JSONRenderer,
    TimeStamper,
    add_log_level,
    format_exc_info,
)

from src.core.config import settings


def setup_logger() -> structlog.BoundLogger:
    log_file = settings.logs_dir / "app.log"

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter("%(message)s"))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(message)s",
        handlers=[file_handler, console_handler],
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            TimeStamper(fmt="iso"),
            add_log_level,
            format_exc_info,
            structlog.processors.UnicodeDecoder(),
            JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    return structlog.get_logger()


logger = setup_logger()
