"""
Модуль парсинга товаров для MEEYG 1.0

Отвечает за:
- Извлечение характеристик товаров из HTML
- Парсинг сопутствующих товаров (погонаж) как НЕЗАВИСИМЫХ записей
- Сохранение данных в БД с поддержкой иерархии (Родитель → Дети)
- Обработку дубликатов и транзакционность
"""

import asyncio
import json
import logging
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup, Tag
from sqlalchemy import select
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.logger import logger
from src.database.models import Category, Product, ProductAttribute, Supplier

logger_parser = logging.getLogger("meeyg.parser")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/124.0.0.0 Safari/537.36",
]

PRICE_RE = re.compile(r"([\d\s.,]+)")
CURRENCY_RE = re.compile(r"([A-Z]{3}|[$€£¥₽])")
SIZE_RE = re.compile(r"([\d.,]+\s*[xх]\s*[\d.,]+(?:\s*[xх]\s*[\d.,]+)?)")


@dataclass
class ParsedProduct:
    """Структура данных для распарсенного товара"""
    url: str
    title: str = ""
    description: str = ""
    price: Optional[float] = None
    currency: Optional[str] = None
    is_available: bool = True
    sku: Optional[str] = None
    image_urls: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    category_id: Optional[int] = None
    raw_html_length: int = 0
    molding_items: list[dict] = field(default_factory=list)
    # 🔥 ДОБАВЛЕНО: Список вариаций товара (размеры, типы и т.д.)
    variations: list[dict] = field(default_factory=list)


@dataclass
class ParsingStats:
    """Статистика парсинга"""
    total_products: int = 0
    total_pages: int = 0
    successful_pages: int = 0
    failed_pages: int = 0
    total_attributes: int = 0
    errors: list[str] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    @property
    def elapsed(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        if self.start_time:
            return time.time() - self.start_time
        return 0.0


class ParserEngine:
    """
    Движок парсинга товаров с поддержкой:
    - Асинхронных запросов
    - Обработки иерархии товаров (Родитель → Дети)
    - Погонаж как НЕЗАВИСИМЫЕ товары с compatible_collections
    - Транзакционности при сохранении в БД
    - Обработки дубликатов
    """

    def __init__(
        self,
        supplier_id: int,
        base_url: str,
        concurrency: int = 5,
        delay_range: tuple[float, float] = (0.5, 2.0),
        timeout: int = 30,
        batch_size: int = 500,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        self.supplier_id = supplier_id
        self.base_url = base_url.rstrip("/")
        self.concurrency = concurrency
        self.delay_range = delay_range
        self.timeout = timeout
        self.batch_size = batch_size
        self.log_callback = log_callback or (lambda m: logger_parser.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        
        self._cancelled = False
        self._paused = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        
        self.stats = ParsingStats()
        self._seen_urls: set[str] = set()
        self._session: Optional[aiohttp.ClientSession] = None
        self._category_cache: dict[str, int] = {}

    # =========================================================================
    # Управление выполнением
    # =========================================================================

    def cancel(self) -> None:
        self._cancelled = True
        self._pause_event.set()

    def pause(self) -> None:
        self._paused = True
        self._pause_event.clear()

    def resume(self) -> None:
        self._paused = False
        self._pause_event.set()

    def _log(self, msg: str) -> None:
        self.log_callback(msg)

    def _progress(self, processed: int, total: int, msg: str) -> None:
        pct = int((processed / max(total, 1)) * 100)
        self.progress_callback(pct, total, msg)

    def _random_delay(self) -> None:
        time.sleep(random.uniform(*self.delay_range))

    def _get_headers(self) -> dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "identity",
            "Connection": "keep-alive",
        }

    # =========================================================================
    # Утилиты нормализации данных
    # =========================================================================

    @staticmethod
    def normalize_title(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def normalize_price(text: str) -> Optional[float]:
        if not text:
            return None
        text = text.strip().replace("\xa0", " ").replace("  ", " ")
        match = PRICE_RE.search(text)
        if not match:
            return None
        num_str = match.group(1).replace(",", ".")
        parts = num_str.split(".")
        if len(parts) > 2:
            num_str = " ".join(parts[:-1]) + "." + parts[-1]
        try:
            val = float(num_str)
            return val if val > 0 else None
        except ValueError:
            return None

    @staticmethod
    def normalize_currency(text: str) -> Optional[str]:
        if not text:
            return None
        match = CURRENCY_RE.search(text)
        if not match:
            return None
        val = match.group(1)
        currency_map = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY", "₽": "RUB"}
        return currency_map.get(val, val.upper())

    @staticmethod
    def is_valid_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False

    def _clean_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    # =========================================================================
    # Парсинг HTML-элементов
    # =========================================================================

    def _parse_molding_items(self, soup: BeautifulSoup) -> list[dict]:
        molding_items = []
        for item in soup.select("li.Product-description__molding-item"):
            data_id = item.get("data-id", "")
            data_price = item.get("data-price", "")
            title_el = item.select_one(".Checkbox__text")
            title = self._clean_text(title_el.get_text()) if title_el else ""
            color_el = item.select_one(".Checkbox__out-text")
            color = self._clean_text(color_el.get_text()) if color_el else ""
            item_type = self._detect_molding_type(title)
            if title:
                molding_items.append({
                    "title": title,
                    "price": self.normalize_price(data_price),
                    "color": color,
                    "external_id": data_id,
                    "type": item_type,
                })
        logger_parser.info(f"  Найдено {len(molding_items)} изделий погонажа")
        return molding_items

    def _detect_molding_type(self, title: str) -> str:
        if not title:
            return "Прочее"
        title_lower = title.lower()
        if "добор" in title_lower:
            return "Добор"
        elif "короб" in title_lower:
            return "Короб"
        elif "наличник" in title_lower:
            return "Наличник"
        elif "плинтус" in title_lower:
            return "Плинтус"
        elif "планка" in title_lower:
            return "Притворная планка"
        elif "порог" in title_lower:
            return "Порог"
        return "Прочее"

    def _parse_description_list(self, soup: BeautifulSoup) -> dict[str, str]:
        attributes = {}
        desc_lists = soup.select(".Description__list")
        for dl in desc_lists:
            terms = dl.select("dt.Description__list-term")
            descs = dl.select("dd.Description__list-desc")
            for dt, dd in zip(terms, descs):
                name = self._clean_text(dt.get_text())
                value = self._clean_text(dd.get_text())
                if name and value:
                    attributes[name] = value
        logger_parser.info(f"  Извлечено {len(attributes)} характеристик из блока описания")
        return attributes

    def _extract_variations(self, soup: BeautifulSoup, base_url: str) -> list[dict]:
        """
        Извлечь вариации товара (размеры, типы) из HTML.
        Возвращает список словарей с данными вариаций.
        """
        variations = []
        
        # === Извлечение размеров ===
        sizes = []
        size_inputs = soup.select("input.sizer[name='size'], input.sizer")
        for el in size_inputs:
            value = el.get("value", "").strip()
            # Если value содержит путь — извлекаем только последнюю часть
            if value and '/' in value:
                value = value.split('/')[-1].rstrip('/')
            # Проверяем, похоже ли на размер (700, 700x2000, 700x2000x40)
            if value and (re.match(r'^[\d.,]+[xх][\d.,]+$', value) or re.match(r'^\d+$', value)):
                sizes.append(value)
            # Пробуем data-атрибуты
            elif el.get("data-size"):
                sizes.append(el.get("data-size"))
            # Или из текста родителя (label)
            else:
                label = el.find_parent("label")
                if label:
                    text = self._clean_text(label.get_text())
                    size_match = re.search(r'([\d.,]+\s*[xх]\s*[\d.,]+)', text)
                    if size_match:
                        sizes.append(size_match.group(1).replace(' ', ''))
        
        # === Извлечение типов ===
        types = []
        type_inputs = soup.select("input.typer[name='type'], input.typer")
        for el in type_inputs:
            value = el.get("value", "").strip()
            if value:
                types.append(value)
        
        # === Создаём комбинации ===
        if sizes and types:
            for size in sizes:
                for type_val in types:
                    variations.append({
                        "title": "",
                        "price": None,
                        "attributes": {"Размер": size, "Тип": type_val}
                    })
        elif sizes:
            for size in sizes:
                variations.append({
                    "title": "",
                    "price": None,
                    "attributes": {"Размер": size}
                })
        elif types:
            for type_val in types:
                variations.append({
                    "title": "",
                    "price": None,
                    "attributes": {"Тип": type_val}
                })
        
        logger_parser.info(f"  Найдено {len(variations)} вариаций")
        return variations

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True,
    )
    async def fetch_page(self, url: str) -> Optional[str]:
        if not self._session:
            return None
        try:
            async with self._session.get(
                url, 
                headers=self._get_headers(), 
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status != 200:
                    self._log(f"  HTTP {resp.status}: {url}")
                    return None
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type and "application/xhtml" not in content_type:
                    return None
                return await resp.text(errors="replace")
        except asyncio.TimeoutError:
            self._log(f"  Timeout: {url}")
            raise
        except aiohttp.ClientError as exc:
            self._log(f"  Network error: {url} ({exc})")
            raise

    def _extract_product_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        links = []
        seen = set()
        selectors = [
            "a.product-link", "a.product-card", "a.item", "a.product",
            "div.product a[href]", "div.item a[href]",
            "a[href*='/product/']", "a[href*='/item/']", 
            "a[href*='/p/']", "a[href*='/catalog/']",
        ]
        for selector in selectors:
            for a_tag in soup.select(selector):
                href = a_tag.get("href", "")
                if href and not href.startswith(("javascript:", "mailto:", "tel:", "#")):
                    full_url = urljoin(base_url, href).split("#")[0]
                    clean_url = self._clean_url(full_url)
                    if clean_url not in seen and self._is_product_url(clean_url):
                        links.append(clean_url)
                        seen.add(clean_url)
        if not links:
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                if href and not href.startswith(("javascript:", "mailto:")):
                    full_url = urljoin(base_url, href).split("#")[0]
                    clean_url = self._clean_url(full_url)
                    if clean_url not in seen and self._is_product_url(clean_url):
                        links.append(clean_url)
                        seen.add(clean_url)
        return links

    def _clean_url(self, url: str) -> str:
        url = url.split("#")[0]
        url = url.split("?")[0]
        return url.rstrip("/")

    def _is_product_url(self, url: str) -> bool:
        path = urlparse(url).path.lower()
        keywords = ["/product/", "/item/", "/p/", "/goods/", "/товар/", "/product-", "/item-", "/p-", "product_id", "item_id"]
        return any(kw in path for kw in keywords)

    def _parse_product_page(self, soup: BeautifulSoup, url: str) -> ParsedProduct:
        product = ParsedProduct(url=url)
        product.raw_html_length = len(str(soup))

        # === Извлечение заголовка ===
        title_el = (
            soup.select_one("h1") 
            or soup.select_one("h1.product-title") 
            or soup.select_one("h1.item-title")
            or soup.select_one("[itemprop='name']")
            or soup.select_one("meta[name='title']")
        )
        if title_el:
            product.title = self.normalize_title(
                title_el.get("content") if title_el.name == "meta" else title_el.get_text()
            )

        # === Извлечение цены и валюты ===
        price_el = (
            soup.select_one(".Product-description__item-price-value")
            or soup.select_one("[itemprop='price']")
            or soup.select_one(".price")
            or soup.select_one(".product-price")
            or soup.select_one(".current-price")
        )
        if price_el:
            price_text = price_el.get_text()
            product.price = self.normalize_price(price_text)
            product.currency = self.normalize_currency(price_text)

        # === Извлечение наличия ===
        avail_el = (
            soup.select_one("[itemprop='availability']")
            or soup.select_one(".availability")
            or soup.select_one(".stock-status")
            or soup.select_one(".in-stock")
        )
        if avail_el:
            avail_text = avail_el.get_text().lower()
            positive = ["in stock", "в наличии", "available", "есть", "yes", "да"]
            negative = ["out of stock", "нет в наличии", "sold out", "нет", "no"]
            if any(kw in avail_text for kw in positive):
                product.is_available = True
            elif any(kw in avail_text for kw in negative):
                product.is_available = False

        # === Извлечение артикула (SKU) ===
        sku_el = (
            soup.select_one("[itemprop='sku']")
            or soup.select_one(".sku")
            or soup.select_one(".product-sku")
            or soup.select_one(".article")
            or soup.select_one(".artikul")
        )
        if sku_el:
            product.sku = self._clean_text(sku_el.get_text())

        # === Извлечение описания ===
        desc_el = (
            soup.select_one("[itemprop='description']")
            or soup.select_one(".product-description")
            or soup.select_one("#description")
            or soup.select_one(".description")
        )
        if desc_el:
            product.description = self._clean_text(desc_el.get_text())

        # === Извлечение изображений ===
        for img in soup.select("img"):
            src = (
                img.get("src") 
                or img.get("data-src") 
                or img.get("data-lazy-src") 
                or img.get("data-original")
            )
            if src:
                full_src = urljoin(url, src)
                if self.is_valid_url(full_src) and not any(
                    ext in full_src.lower() for ext in [".svg", ".gif", ".ico", "placeholder", "blank"]
                ):
                    if full_src not in product.image_urls:
                        product.image_urls.append(full_src)

        # === Извлечение характеристик из блока описания ===
        dl_attrs = self._parse_description_list(soup)
        if dl_attrs:
            product.attributes.update(dl_attrs)

        # === Дополнительный парсинг таблиц характеристик ===
        attr_tables = soup.select(
            ".attributes, .specs, .specifications, .characteristics, .params, .properties"
        )
        for table in attr_tables:
            for row in table.select("tr"):
                cells = row.select("td, th")
                if len(cells) >= 2:
                    name = self._clean_text(cells[0].get_text())
                    value = self._clean_text(cells[1].get_text())
                    if name and value and len(name) > 1 and len(value) > 1:
                        product.attributes[name] = value

        # === Парсинг списка характеристик (dl/dt/dd) ===
        for dl in soup.select("dl.attributes, dl.specs, dl.characteristics"):
            terms = dl.select("dt")
            defs = dl.select("dd")
            for dt, dd in zip(terms, defs):
                name = self._clean_text(dt.get_text())
                value = self._clean_text(dd.get_text())
                if name and value:
                    product.attributes[name] = value

        # === Парсинг сопутствующих товаров (погонаж) ===
        molding_items = self._parse_molding_items(soup)
        if molding_items:
            product.molding_items = molding_items
            logger_parser.info(f"Найдено {len(molding_items)} сопутствующих товаров для {url}")

        # === Парсинг вариаций товара ===
        variations = self._extract_variations(soup, url)
        if variations:
            product.variations = variations

        return product

    # =========================================================================
    # Работа с категориями в БД
    # =========================================================================

    def _get_or_create_category(
        self, 
        db_session, 
        supplier_id: int, 
        parent_category_id: Optional[int], 
        name: str,
        url: str = ""
    ) -> int:
        cache_key = f"{supplier_id}:{parent_category_id}:{name}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]
        
        existing = db_session.execute(
            select(Category).where(
                Category.supplier_id == supplier_id,
                Category.parent_id == parent_category_id,
                Category.name == name,
            )
        ).scalar_one_or_none()
        
        if existing:
            self._category_cache[cache_key] = existing.id
            return existing.id
        
        new_category = Category(
            supplier_id=supplier_id,
            parent_id=parent_category_id,
            name=name,
            url=url,
            xpath_selector="",
            sort_order=0,
            product_count=0,
        )
        db_session.add(new_category)
        db_session.flush()
        self._category_cache[cache_key] = new_category.id
        self._log(f"  Создана категория: {name} (parent_id={parent_category_id})")
        return new_category.id

    def _get_full_category_path(self, db_session, category_id: int) -> str:
        """
        Рекурсивно собрать полный путь категории от корня до листа.
        Пример: "Межкомнатные двери > Бона > Покрытие"
        """
        if not category_id:
            return ""
        path_parts = []
        current_id = category_id
        while current_id:
            category = db_session.execute(
                select(Category).where(Category.id == current_id)
            ).scalar_one_or_none()
            if not category:
                break
            path_parts.insert(0, category.name)
            current_id = category.parent_id
        return " > ".join(path_parts) if path_parts else ""

    def _get_or_create_molding_root_category(self, db_session) -> int:
        """
        Получить или создать корневую категорию "Погонаж"
        """
        cache_key = f"{self.supplier_id}:molding_root"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]
        
        root = db_session.execute(
            select(Category).where(
                Category.supplier_id == self.supplier_id,
                Category.name == "Погонаж",
                Category.parent_id.is_(None)
            )
        ).scalar_one_or_none()
        
        if not root:
            root = Category(
                supplier_id=self.supplier_id,
                name="Погонаж",
                url="",
                parent_id=None,
                xpath_selector="",
                sort_order=0,
                product_count=0,
            )
            db_session.add(root)
            db_session.flush()
            self._log(f"  Создана корневая категория погонажа (id={root.id})")
        
        self._category_cache[cache_key] = root.id
        return root.id

    def _get_or_create_molding_subcategory(self, db_session, molding_type: str) -> int:
        """
        Получить или создать подкатегорию погонажа под корнем "Погонаж"
        """
        root_id = self._get_or_create_molding_root_category(db_session)
        cache_key = f"{self.supplier_id}:molding:{molding_type}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]
        
        subcat = db_session.execute(
            select(Category).where(
                Category.supplier_id == self.supplier_id,
                Category.parent_id == root_id,
                Category.name == molding_type,
            )
        ).scalar_one_or_none()
        
        if not subcat:
            subcat = Category(
                supplier_id=self.supplier_id,
                parent_id=root_id,
                name=molding_type,
                url="",
                xpath_selector="",
                sort_order=0,
                product_count=0,
            )
            db_session.add(subcat)
            db_session.flush()
            self._log(f"  Создана подкатегория погонажа: {molding_type} (id={subcat.id})")
        
        self._category_cache[cache_key] = subcat.id
        return subcat.id

    def _upsert_molding_item(self, item: dict, door_category_path: str, db_session) -> None:
        """
        Создать или обновить погонажный товар как НЕЗАВИСИМУЮ запись.
        
        Логика UPSERT:
        1. Поиск по external_sku или title в категории погонажа
        2. Если найден → обновить compatible_collections (добавить путь категории двери)
        3. Если не найден → создать новую запись с parent_product_id=None
        """
        molding_type = item.get("type", "Прочее")
        molding_title = item.get("title", "")
        molding_sku = item.get("external_id")
        molding_color = item.get("color", "")
        molding_price = item.get("price")
        
        if not molding_title:
            return
        
        # Получить/создать категорию погонажа
        molding_category_id = self._get_or_create_molding_subcategory(db_session, molding_type)
        
        # Поиск существующего погонажа (НЕЗАВИСИМОГО!)
        existing_molding = None
        if molding_sku:
            existing_molding = db_session.execute(
                select(Product).where(
                    Product.supplier_id == self.supplier_id,
                    Product.category_id == molding_category_id,
                    Product.external_sku == molding_sku,
                    Product.parent_product_id.is_(None),  # 🔥 Ищем только независимые!
                )
            ).scalar_one_or_none()
        
        if not existing_molding and molding_title:
            existing_molding = db_session.execute(
                select(Product).where(
                    Product.supplier_id == self.supplier_id,
                    Product.category_id == molding_category_id,
                    Product.title == molding_title,
                    Product.parent_product_id.is_(None),  # 🔥 Ищем только независимые!
                )
            ).scalar_one_or_none()
        
        if existing_molding:
            # Обновление существующего погонажа
            existing_molding.title = molding_title
            existing_molding.price = molding_price
            existing_molding.currency = "RUB"
            existing_molding.is_available = True
            existing_molding.updated_at = datetime.utcnow()
            
            # 🔥 КЛЮЧЕВОЙ МОМЕНТ: обновить compatible_collections без дублей
            current_collections = existing_molding.get_compatible_collections()
            if door_category_path and door_category_path not in current_collections:
                current_collections.append(door_category_path)
                existing_molding.set_compatible_collections(current_collections)
            
            db_session.flush()
            self._log(f"  Обновлен погонаж: {molding_title} | Collections: {len(current_collections)}")
        else:
            # Создание НОВОГО независимого погонажа
            molding_product = Product(
                supplier_id=self.supplier_id,
                category_id=molding_category_id,
                parent_product_id=None,  # 🔥 НЕЗАВИСИМЫЙ товар!
                external_sku=molding_sku,
                title=molding_title,
                description=f"Комплектующий: {molding_type}",
                price=molding_price,
                currency="RUB",
                is_available=True,
                image_urls="[]",
            )
            
            # Инициализация compatible_collections
            if door_category_path:
                molding_product.set_compatible_collections([door_category_path])
            
            db_session.add(molding_product)
            db_session.flush()
            
            # Добавить атрибут цвета если есть
            if molding_color:
                safe_color = molding_color[:65535]
                if safe_color:
                    color_attr = ProductAttribute(
                        product_id=molding_product.id,
                        name="Цвет",
                        value=safe_color,
                    )
                    db_session.add(color_attr)
            
            self._log(f"  Создан погонаж: {molding_title} | Collections: {[door_category_path]}")

    # =========================================================================
    # Сохранение данных в БД
    # =========================================================================

    def _save_batch(self, products: list[ParsedProduct], db_session) -> None:
        """
        Сохранить пакет товаров в БД с поддержкой иерархии:
        
        ЛОГИКА:
        1. РОДИТЕЛЬ (дверь):
           - Поиск/создание с parent_product_id=None
           - Очистка заголовка от конкретного размера/цвета
           - Атрибут "Доступные размеры" = "600|700|800"
        
        2. ДЕТИ (вариации):
           - Создать с parent_product_id=ID_родителя
           - Атрибут "Размер" = одно конкретное значение
        
        3. ПОГОНАЖ:
           - Создать/обновить как НЕЗАВИСИМЫЙ товар (parent_product_id=None)
           - Категория: "Погонаж > Добор/Наличник/..."
           - compatible_collections: массив путей категорий дверей
        
        Транзакция: всё в одном try/except, при ошибке → rollback.
        """
        from sqlalchemy.exc import IntegrityError
        
        try:
            # 🔥 ОТЛАДКА: выводим информацию о пакете
            print(f"\n🔥 [DEBUG] _save_batch: {len(products)} товаров в пакете")
            if products:
                p = products[0]
                print(f"   🔹 title: {p.title[:50]}")
                print(f"   🔹 attributes: {len(p.attributes)} шт.")
                print(f"   🔹 molding_items: {len(p.molding_items)} шт.")
                print(f"   🔹 variations: {len(p.variations)} шт.")
                if p.molding_items:
                    print(f"   🔹 Пример погонажа: {p.molding_items[0].get('title')} ({p.molding_items[0].get('type')})")
            
            self._log(f"  Начало транзакции для пакета из {len(products)} товаров")
            
            for parsed_product in products:
                try:
                    # =====================================================
                    # 1. ОБРАБОТКА РОДИТЕЛЬСКОГО ТОВАРА (ДВЕРЬ)
                    # =====================================================
                    
                    # Очистка заголовка от конкретного размера/цвета
                    cleaned_title = re.sub(r'\s*\d+[xх]\d+\s*.*$', '', parsed_product.title or "Без названия").strip()
                    
                    # Поиск дубликата по SKU (для основных товаров parent_product_id IS NULL)
                    existing_product = None
                    if parsed_product.sku:
                        existing_product = db_session.execute(
                            select(Product).where(
                                Product.supplier_id == self.supplier_id,
                                Product.external_sku == parsed_product.sku,
                                Product.parent_product_id.is_(None),
                            )
                        ).scalar_one_or_none()
                    
                    # Поиск по названию если нет SKU
                    if not existing_product and not parsed_product.sku:
                        existing_product = db_session.execute(
                            select(Product).where(
                                Product.supplier_id == self.supplier_id,
                                Product.title == cleaned_title,
                                Product.parent_product_id.is_(None),
                            )
                        ).scalar_one_or_none()
                    
                    if existing_product:
                        # Обновление существующего товара
                        main_product_id = existing_product.id
                        existing_product.title = cleaned_title
                        existing_product.description = parsed_product.description
                        existing_product.price = parsed_product.price
                        existing_product.currency = parsed_product.currency
                        existing_product.is_available = parsed_product.is_available
                        existing_product.image_urls = json.dumps(
                            parsed_product.image_urls, ensure_ascii=False
                        )
                        existing_product.updated_at = datetime.utcnow()
                        db_session.flush()
                        self._log(f"  Обновлен родитель: {cleaned_title} (id={main_product_id})")
                    else:
                        # Создание нового родителя
                        main_product = Product(
                            supplier_id=self.supplier_id,
                            category_id=parsed_product.category_id,
                            parent_product_id=None,  # 🔥 РОДИТЕЛЬ НЕЗАВИСИМЫЙ
                            external_sku=parsed_product.sku,
                            title=cleaned_title,
                            description=parsed_product.description,
                            price=parsed_product.price,
                            currency=parsed_product.currency,
                            is_available=parsed_product.is_available,
                            image_urls=json.dumps(
                                parsed_product.image_urls, ensure_ascii=False
                            ),
                        )
                        db_session.add(main_product)
                        db_session.flush()
                        main_product_id = main_product.id
                        self._log(f"  Создан родитель: {cleaned_title} (id={main_product_id})")
                    
                    # Сохранение атрибутов родителя
                    for attr_name, attr_value in parsed_product.attributes.items():
                        safe_name = attr_name[:255] if attr_name else ""
                        safe_value = attr_value[:65535] if attr_value else ""
                        if safe_name and safe_value:
                            attr = ProductAttribute(
                                product_id=main_product_id,
                                name=safe_name,
                                value=safe_value,
                            )
                            db_session.add(attr)
                    
                    # =====================================================
                    # 2. СБОР РАЗМЕРОВ И СОЗДАНИЕ ВАРИАЦИЙ (ДЕТЕЙ)
                    # =====================================================
                    
                    # Сначала собираем все размеры для родителя
                    all_sizes = []
                    variations = getattr(parsed_product, 'variations', [])
                    if variations:
                        for variation in variations:
                            if isinstance(variation, dict):
                                size_attr = variation.get("attributes", {}).get("Размер")
                            else:
                                size_attr = getattr(variation, 'attributes', {}).get("Размер")
                            if size_attr and size_attr not in all_sizes:
                                all_sizes.append(size_attr)
                        
                        # 🔥 Записываем СКЛЕЕННЫЕ размеры у родителя
                        if all_sizes:
                            sizes_string = "|".join(all_sizes)
                            existing_size_attr = db_session.execute(
                                select(ProductAttribute).where(
                                    ProductAttribute.product_id == main_product_id,
                                    ProductAttribute.name == "Доступные размеры"
                                )
                            ).scalar_one_or_none()
                            
                            if existing_size_attr:
                                existing_size_attr.value = sizes_string
                            else:
                                size_attr_obj = ProductAttribute(
                                    product_id=main_product_id,
                                    name="Доступные размеры",  # 🔥 Имя атрибута для родителя
                                    value=sizes_string
                                )
                                db_session.add(size_attr_obj)
                            self._log(f"  Родитель: размеры = {sizes_string}")
                    
                    # Создаем вариации как дочерние товары
                    for variation in variations:
                        if isinstance(variation, dict):
                            var_title = variation.get("title", cleaned_title)
                            var_desc = variation.get("description", parsed_product.description)
                            var_price = variation.get("price", parsed_product.price)
                            var_currency = variation.get("currency", parsed_product.currency)
                            var_available = variation.get("is_available", parsed_product.is_available)
                            var_images = variation.get("image_urls", parsed_product.image_urls)
                            var_attrs = variation.get("attributes", {})
                        else:
                            var_title = getattr(variation, 'title', cleaned_title)
                            var_desc = getattr(variation, 'description', parsed_product.description)
                            var_price = getattr(variation, 'price', parsed_product.price)
                            var_currency = getattr(variation, 'currency', parsed_product.currency)
                            var_available = getattr(variation, 'is_available', parsed_product.is_available)
                            var_images = getattr(variation, 'image_urls', parsed_product.image_urls)
                            var_attrs = getattr(variation, 'attributes', {})
                        
                        variation_product = Product(
                            supplier_id=self.supplier_id,
                            category_id=parsed_product.category_id,
                            parent_product_id=main_product_id,  # 🔥 Связь с родителем
                            external_sku=parsed_product.sku,
                            title=var_title,
                            description=var_desc,
                            price=var_price,
                            currency=var_currency,
                            is_available=var_available,
                            image_urls=json.dumps(var_images, ensure_ascii=False),
                        )
                        db_session.add(variation_product)
                        db_session.flush()
                        variation_id = variation_product.id
                        self._log(f"  Создана вариация: {var_title} (parent={main_product_id})")
                        
                        # Сохранение атрибутов вариации
                        for attr_name, attr_value in var_attrs.items():
                            safe_name = attr_name[:255] if attr_name else ""
                            safe_value = attr_value[:65535] if attr_value else ""
                            if safe_name and safe_value:
                                attr = ProductAttribute(
                                    product_id=variation_id,
                                    name=safe_name,
                                    value=safe_value,
                                )
                                db_session.add(attr)
                    
                    # =====================================================
                    # 3. ОБРАБОТКА ПОГОНАЖА (НЕЗАВИСИМЫЕ ТОВАРЫ!)
                    # =====================================================
                    
                    if parsed_product.molding_items:
                        # 🔥 Получаем ПОЛНЫЙ путь категории двери
                        door_category_path = self._get_full_category_path(
                            db_session, parsed_product.category_id
                        )
                        self._log(f"  Путь категории двери: {door_category_path}")
                        
                        # Обрабатываем каждый погонаж через UPSERT
                        for molding_item in parsed_product.molding_items:
                            try:
                                self._upsert_molding_item(
                                    molding_item, 
                                    door_category_path, 
                                    db_session
                                )
                            except Exception as e:
                                self._log(f"  Ошибка обработки погонажа {molding_item.get('title')}: {e}")
                                continue
                                    
                except IntegrityError as e:
                    self._log(f"  Ошибка уникальности при обработке {parsed_product.title}: {e}")
                    db_session.rollback()
                    raise
                except Exception as e:
                    self._log(f"  Ошибка обработки товара {parsed_product.title}: {e}")
                    raise
            
            # 🔥 ФИНАЛЬНЫЙ COMMIT после успешной обработки всех товаров
            self._log(f"  Пакет успешно сохранён: {len(products)} товаров обработано")
            
        except Exception as e:
            self._log(f"  Ошибка транзакции: {e}")
            logger_parser.exception("Ошибка сохранения пакета товаров")
            raise

    # =========================================================================
    # Парсинг категории (основной метод)
    # =========================================================================

    async def _parse_category(self, category_id: int, url: str, db_session) -> int:
        if self._cancelled:
            return 0

        await self._pause_event.wait()

        html = await self.fetch_page(url)
        if not html:
            self.stats.failed_pages += 1
            return 0

        self.stats.successful_pages += 1
        self._random_delay()

        soup = BeautifulSoup(html, "lxml")
        product_links = self._extract_product_links(soup, url)
        self._log(f"  Категория: найдено {len(product_links)} ссылок на товары")

        parsed_products = []
        for i, p_url in enumerate(product_links):
            if self._cancelled:
                break
            await self._pause_event.wait()
            if p_url in self._seen_urls:
                continue
            self._seen_urls.add(p_url)

            p_html = await self.fetch_page(p_url)
            if not p_html:
                self.stats.failed_pages += 1
                continue

            self.stats.successful_pages += 1
            self.stats.total_pages += 1
            self._random_delay()

            try:
                p_soup = BeautifulSoup(p_html, "lxml")
                product = self._parse_product_page(p_soup, p_url)
                product.category_id = category_id
                parsed_products.append(product)
                self.stats.total_products += 1
                self.stats.total_attributes += len(product.attributes)
                self._progress(
                    self.stats.total_products,
                    max(len(product_links), 1),
                    f"Распаршено {self.stats.total_products} товаров",
                )
            except Exception as exc:
                self._log(f"  Ошибка парсинга товара {p_url}: {exc}")
                self.stats.errors.append(f"Product parse error: {p_url} - {exc}")

        if parsed_products:
            self._save_batch(parsed_products, db_session)

        next_page = self._find_next_page(soup, url)
        if next_page and not self._cancelled:
            await self._parse_category(category_id, next_page, db_session)

        return len(parsed_products)

    def _find_next_page(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        selectors = [
            "a.next", "a.next-page", "a.pagination-next",
            "a[rel='next']", ".next a", ".pagination .next a",
            "a[href*='page=']", "a[href*='p=']",
        ]
        for selector in selectors:
            el = soup.select_one(selector)
            if el and el.get("href"):
                return urljoin(base_url, el["href"])
        return None

    # =========================================================================
    # Основной метод запуска
    # =========================================================================

    async def run(self, category_ids: list[int], db_session) -> dict[str, Any]:
        self._cancelled = False
        self._paused = False
        self._pause_event.set()
        self.stats = ParsingStats()
        self.stats.start_time = time.time()
        self._seen_urls.clear()
        self._category_cache.clear()

        self._log(f"Запуск парсера для поставщика {self.supplier_id}")
        self._log(f"Категорий для парсинга: {len(category_ids)}")

        connector = aiohttp.TCPConnector(
            ssl=False,
            limit=self.concurrency,
            limit_per_host=self.concurrency,
            ttl_dns_cache=300,
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            self._session = session
            categories = db_session.execute(
                select(Category).where(Category.id.in_(category_ids))
            ).scalars().all()

            if not categories:
                self._log("Не найдено категорий для указанных ID")
                return {"success": False, "error": "No categories found", "stats": self.stats}

            self._log(f"Загружено {len(categories)} категорий из БД")

            semaphore = asyncio.Semaphore(self.concurrency)

            async def _parse_with_semaphore(cat):
                async with semaphore:
                    return await self._parse_category(cat.id, cat.url, db_session)

            tasks = [_parse_with_semaphore(cat) for cat in categories]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            total_parsed = 0
            for r in results:
                if isinstance(r, int):
                    total_parsed += r
                elif isinstance(r, Exception):
                    self._log(f"Ошибка парсинга категории: {r}")
                    self.stats.errors.append(str(r))

        self._update_supplier_timestamp(db_session)
        self.stats.end_time = time.time()

        self._log(f"Парсинг завершён: {total_parsed} товаров, {self.stats.total_pages} страниц")
        self._log(f"Затрачено времени: {self.stats.elapsed:.1f}с")

        return {
            "success": True,
            "products_parsed": total_parsed,
            "stats": self.stats,
        }

    def _update_supplier_timestamp(self, db_session) -> None:
        supplier = db_session.execute(
            select(Supplier).where(Supplier.id == self.supplier_id)
        ).scalar_one_or_none()
        if supplier:
            supplier.last_scrape_run = datetime.utcnow()
            db_session.flush()