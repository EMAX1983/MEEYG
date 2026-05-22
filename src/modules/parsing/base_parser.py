"""
Базовые классы и структуры данных для парсеров.
"""

import asyncio
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from playwright.async_api import Page
from sqlalchemy.orm import Session

from src.core.logger import logger


@dataclass
class ParsedProduct:
    """Унифицированная структура данных для хранения результата парсинга продукта."""

    url: str
    title: str = ""
    description: str = ""
    price: Optional[float] = None
    currency: Optional[str] = None
    is_available: bool = True
    sku: Optional[str] = None
    category_id: Optional[int] = None
    category_path_str: str = ""
    image_urls: List[str] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)
    molding_items: List[Dict[str, Any]] = field(default_factory=list)
    variations: List[Dict[str, Any]] = field(default_factory=list)
    compatible_collections: List[str] = field(default_factory=list)


class BaseParser(ABC):
    """Абстрактный базовый класс для всех парсеров."""

    def __init__(
        self,
        supplier_id: int,
        headless: bool = True,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        **kwargs: Any,
    ):
        self.supplier_id = supplier_id
        self.headless = headless
        self.log_callback = log_callback or (lambda m: logger.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)

        self._cancelled = False
        self._paused = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # Изначально не на паузе

        self.stats: Dict[str, Any] = {
            "products_parsed": 0,
            "variations_created": 0,
            "errors": [],
        }

    def _log(self, msg: str):
        """Централизованный вызов логгирования."""
        self.log_callback(msg)

    # --- Методы управления состоянием ---
    def cancel(self):
        self._cancelled = True
        self._pause_event.set()  # Снимаем паузу при отмене

    def pause(self):
        self._paused = True
        self._pause_event.clear()

    def resume(self):
        self._paused = False
        self._pause_event.set()

    # --- Вспомогательные утилиты ---
    @staticmethod
    def _clean_text(text: Optional[str]) -> str:
        """Очищает текст от лишних пробелов и переносов строк."""
        return re.sub(r'\s+', ' ', text).strip() if text else ''

    @staticmethod
    def normalize_price(text: str) -> Optional[float]:
        """Извлекает числовое значение цены из строки."""
        if not text:
            return None
        # Удаляем пробелы, заменяем запятую на точку
        text = text.strip().replace(' ', '')
        match = re.search(r"([\d\s.,]+)", text)
        if not match:
            return None
        num_str = match.group(1).replace(',', '.')
        try:
            return float(num_str)
        except (ValueError, TypeError):
            return None

    # --- Абстрактные методы, которые должны реализовать наследники ---
    @abstractmethod
    async def _parse_product_page(self, page: Page, url: str, **kwargs) -> Optional[List[ParsedProduct]]:
        """Парсит страницу одного продукта. Возвращает список: [родитель, ребёнок1, ребёнок2, ...]."""
        raise NotImplementedError

    @abstractmethod
    async def run(self, session: Session, **kwargs: Any) -> Dict[str, Any]:
        """Основной метод, запускающий процесс парсинга."""
        raise NotImplementedError
