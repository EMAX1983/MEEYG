"""
Playwright-парсер для tandoor.ru
Финальная версия с поддержкой:
1. Иерархии Родитель -> Дети (Вариации)
2. Независимого погонажа с compatible_collections
3. Склеивания размеров у родителя
"""

import asyncio
import json
import logging
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser
from sqlalchemy import select

from src.core.logger import logger
from src.database.models import Product, ProductAttribute, Category, Supplier

logger_parser = logging.getLogger("meeyg.tandoor_parser")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

PRICE_RE = re.compile(r"([\d\s.,]+)")
CURRENCY_RE = re.compile(r"([A-Z]{3}|[$€£¥₽])")


@dataclass
class ParsedProduct:
    """Структура данных распарсенного товара"""
    url: str
    title: str = ""
    description: str = ""
    price: Optional[float] = None
    currency: Optional[str] = None
    is_available: bool = True
    sku: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)
    category_id: Optional[int] = None
    raw_html_length: int = 0
    molding_items: List[Dict[str, Any]] = field(default_factory=list)
    variations: List[Dict[str, Any]] = field(default_factory=list)


class TandoorPlaywrightParser:
    def __init__(
        self,
        supplier_id: int,
        db_session,
        headless: bool = True,
        delay_range: Tuple[float, float] = (1.0, 3.0),
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        self.supplier_id = supplier_id
        self.db_session = db_session
        self.headless = headless
        self.delay_range = delay_range
        self.log_callback = log_callback or (lambda m: logger_parser.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self._cancelled = False
        self._paused = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        self.stats = {
            "products_parsed": 0,
            "variations_parsed": 0,
            "molding_items_parsed": 0,
            "errors": [],
            "start_time": None,
            "end_time": None,
        }
        self._seen_urls: set[str] = set()
        self.browser: Optional[Browser] = None
        self._category_cache: Dict[str, int] = {}

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

    async def _extract_variations(self, page: Page, base_url: str) -> List[Dict[str, Any]]:
        """
        Извлекает вариации товара через Playwright.
        Возвращает список словарей с данными вариаций.
        """
        variations = []
        
        # === Извлечение размеров ===
        sizes = []
        size_selectors = [
            "input.sizer[name='size']",
            "input.sizer",
            "button[data-size]",
            ".Product-description__size-item input[type='radio']",
        ]
        
        for selector in size_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for el in elements:
                    value = await el.get_attribute("value")
                    if value:
                        value = value.strip()
                        # Если значение содержит путь — извлекаем только последнюю часть
                        if "/" in value:
                            value = value.split("/")[-1].rstrip("/")
                        # Проверяем формат размера (700, 700x2000, 700x2000x40)
                        if re.match(r"^[\d.,]+[xх][\d.,]+$", value) or re.match(r"^\d+$", value):
                            if value not in sizes:
                                sizes.append(value)
                        # Или извлекаем из data-атрибута
                        elif await el.get_attribute("data-size"):
                            size_val = (await el.get_attribute("data-size")).strip()
                            if size_val and size_val not in sizes:
                                sizes.append(size_val)
                        # Или из текста родителя (label)
                        else:
                            label = await el.query_selector("xpath=..")
                            if label:
                                text = await label.inner_text()
                                size_match = re.search(r"([\d.,]+\s*[xх]\s*[\d.,]+)", text)
                                if size_match:
                                    size_val = size_match.group(1).replace(" ", "")
                                    if size_val not in sizes:
                                        sizes.append(size_val)
            except Exception:
                continue
        
        # === Извлечение типов ===
        types = []
        type_selectors = [
            "input.typer[name='type']",
            "input.typer",
            "button[data-type]",
            ".Product-description__type-item input[type='radio']",
        ]
        
        for selector in type_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for el in elements:
                    value = await el.get_attribute("value")
                    if value:
                        value = value.strip()
                        if value and value not in types:
                            types.append(value)
            except Exception:
                continue
        
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

    async def _parse_molding_items(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        molding_items = []
        for item in soup.select("li.Product-description__molding-item"):
            try:
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
            except Exception as e:
                logger_parser.warning(f"Ошибка парсинга погонажа: {e}")
        
        logger_parser.info(f"  Найдено {len(molding_items)} изделий погонажа")
        return molding_items

    async def _parse_product_page(self, page: Page, url: str) -> ParsedProduct:
        product = ParsedProduct(url=url)
        
        try:
            # Переход на страницу и ожидание загрузки
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(1500)  # Доп. ожидание для динамического контента
            
            html = await page.content()
            soup = BeautifulSoup(html, "lxml")
            product.raw_html_length = len(html)
            
            # === Заголовок ===
            title_el = (
                soup.select_one("h1") 
                or soup.select_one("h1.Product-description__title")
                or soup.select_one("[itemprop='name']")
                or soup.select_one("meta[name='title']")
            )
            if title_el:
                product.title = self.normalize_title(
                    title_el.get("content") if title_el.name == "meta" else title_el.get_text()
                )
            
            # === Цена ===
            price_el = soup.select_one(".Product-description__item-price-value")
            if price_el:
                price_text = price_el.get_text()
                product.price = self.normalize_price(price_text)
                product.currency = self.normalize_currency(price_text)
            
            # === SKU ===
            sku_el = soup.select_one("[itemprop='sku'], .sku")
            if sku_el:
                product.sku = self._clean_text(sku_el.get_text())
            
            # === Описание ===
            desc_el = soup.select_one("[itemprop='description'], .product-description")
            if desc_el:
                product.description = self._clean_text(desc_el.get_text())
            
            # === Изображения ===
            for img in soup.select("img[itemprop='image'], .Thumbnail-slide__swiper-image img"):
                src = img.get("data-src") or img.get("src")
                if src:
                    full_src = urljoin(url, src)
                    if self.is_valid_url(full_src) and not any(
                        ext in full_src.lower() for ext in [".svg", ".gif", ".ico", "placeholder"]
                    ):
                        if full_src not in product.image_urls:
                            product.image_urls.append(full_src)
            
            # === Атрибуты из dl/dt/dd ===
            for dt in soup.select(".Description__list dt.Description__list-term"):
                dd = dt.find_next_sibling("dd", class_="Description__list-desc")
                if dd:
                    name = self._clean_text(dt.get_text())
                    value = self._clean_text(dd.get_text())
                    if name and value:
                        product.attributes[name] = value
            
            # === Погонаж ===
            molding_items = await self._parse_molding_items(soup)
            if molding_items:
                product.molding_items = molding_items
                self.stats["molding_items_parsed"] += len(molding_items)
            
            # === Вариации ===
            has_sizer = await page.query_selector("input.sizer")
            has_typer = await page.query_selector("input.typer")
            if has_sizer or has_typer:
                variations = await self._extract_variations(page, url)
                if variations:
                    product.variations = variations
                    self.stats["variations_parsed"] += len(variations)
                    
        except Exception as e:
            logger_parser.error(f"Ошибка парсинга {url}: {e}")
            self.stats["errors"].append(f"Parse error: {url} - {e}")
            raise
        
        return product

    def _get_full_category_path(self, category_id: int) -> str:
        """Рекурсивно собирает полный путь категории."""
        if not category_id:
            return ""
        path_parts = []
        current_id = category_id
        while current_id:
            category = self.db_session.execute(
                select(Category).where(Category.id == current_id)
            ).scalar_one_or_none()
            if not category:
                break
            path_parts.insert(0, category.name)
            current_id = category.parent_id
        return " > ".join(path_parts) if path_parts else ""

    def _get_or_create_molding_root_category(self) -> int:
        """Получает или создаёт корневую категорию 'Погонаж'."""
        cache_key = f"{self.supplier_id}:molding_root"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]
        
        root = self.db_session.execute(
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
            self.db_session.add(root)
            self.db_session.flush()
            self._log(f"  Создан корень погонажа (id={root.id})")
        
        self._category_cache[cache_key] = root.id
        return root.id

    def _get_or_create_molding_subcategory(self, molding_type: str) -> int:
        """Получает или создаёт подкатегорию погонажа."""
        root_id = self._get_or_create_molding_root_category()
        cache_key = f"{self.supplier_id}:molding:{molding_type}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]
        
        subcat = self.db_session.execute(
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
            self.db_session.add(subcat)
            self.db_session.flush()
            self._log(f"  Создана подкатегория погонажа: {molding_type} (id={subcat.id})")
        
        self._category_cache[cache_key] = subcat.id
        return subcat.id

    def _upsert_molding_item(self, item: Dict[str, Any], door_category_path: str) -> None:
        """UPSERT погонажа как НЕЗАВИСИМОГО товара."""
        molding_type = item.get("type", "Прочее")
        molding_title = item.get("title", "")
        molding_sku = item.get("external_id")
        molding_color = item.get("color", "")
        molding_price = item.get("price")
        
        if not molding_title:
            return
        
        # 🔥 Получаем категорию погонажа ПОД корнем "Погонаж"
        molding_category_id = self._get_or_create_molding_subcategory(molding_type)
        
        # 🔥 Поиск существующего НЕЗАВИСИМОГО погонажа (parent_product_id=None!)
        existing_molding = None
        if molding_sku:
            existing_molding = self.db_session.execute(
                select(Product).where(
                    Product.supplier_id == self.supplier_id,
                    Product.category_id == molding_category_id,
                    Product.external_sku == molding_sku,
                    Product.parent_product_id.is_(None),  # 🔥 Только независимые!
                )
            ).scalar_one_or_none()
        
        if not existing_molding and molding_title:
            existing_molding = self.db_session.execute(
                select(Product).where(
                    Product.supplier_id == self.supplier_id,
                    Product.category_id == molding_category_id,
                    Product.title == molding_title,
                    Product.parent_product_id.is_(None),  # 🔥 Только независимые!
                )
            ).scalar_one_or_none()
        
        if existing_molding:
            # Обновление
            existing_molding.title = molding_title
            existing_molding.price = molding_price
            existing_molding.currency = "RUB"
            existing_molding.is_available = True
            existing_molding.updated_at = datetime.utcnow()
            
            # 🔥 Обновление compatible_collections без дублей
            current = existing_molding.get_compatible_collections()
            if door_category_path and door_category_path not in current:
                current.append(door_category_path)
                existing_molding.set_compatible_collections(current)
            
            self.db_session.flush()
            self._log(f"  Обновлен погонаж: {molding_title} | Collections: {len(current)}")
        else:
            # 🔥 Создание НОВОГО независимого погонажа
            molding_product = Product(
                supplier_id=self.supplier_id,
                category_id=molding_category_id,
                parent_product_id=None,  # 🔥 НЕЗАВИСИМЫЙ!
                external_sku=molding_sku,
                title=molding_title,
                description=f"Комплектующий: {molding_type}",
                price=molding_price,
                currency="RUB",
                is_available=True,
                image_urls="[]",
            )
            
            # 🔥 Инициализация compatible_collections
            if door_category_path:
                molding_product.set_compatible_collections([door_category_path])
            
            self.db_session.add(molding_product)
            self.db_session.flush()
            
            if molding_color:
                safe_color = molding_color[:65535]
                if safe_color:
                    color_attr = ProductAttribute(
                        product_id=molding_product.id,
                        name="Цвет",
                        value=safe_color,
                    )
                    self.db_session.add(color_attr)
            
            self._log(f"  Создан погонаж: {molding_title} | Collections: {[door_category_path]}")

    async def _save_product(self, product: ParsedProduct) -> int:
        """Сохраняет товар с поддержкой иерархии."""
        try:
            # === 1. РОДИТЕЛЬ ===
            cleaned_title = re.sub(r'\s*\d+[xх]\d+\s*.*$', '', product.title or "Без названия").strip()
            
            existing = None
            if product.sku:
                existing = self.db_session.execute(
                    select(Product).where(
                        Product.supplier_id == self.supplier_id,
                        Product.external_sku == product.sku,
                        Product.parent_product_id.is_(None),
                    )
                ).scalar_one_or_none()
            elif cleaned_title and cleaned_title != "Без названия":
                existing = self.db_session.execute(
                    select(Product).where(
                        Product.supplier_id == self.supplier_id,
                        Product.title == cleaned_title,
                        Product.parent_product_id.is_(None),
                    )
                ).scalar_one_or_none()

            if existing:
                main_id = existing.id
                existing.title = cleaned_title
                existing.description = product.description
                existing.price = product.price
                existing.currency = product.currency
                existing.is_available = product.is_available
                existing.image_urls = json.dumps(product.image_urls, ensure_ascii=False)
                existing.updated_at = datetime.utcnow()
                self.db_session.flush()
                self._log(f"  Обновлен родитель: {cleaned_title} (id={main_id})")
            else:
                main = Product(
                    supplier_id=self.supplier_id,
                    category_id=product.category_id,
                    parent_product_id=None,
                    external_sku=product.sku,
                    title=cleaned_title if cleaned_title != "Без названия" else (product.title or "Без названия"),
                    description=product.description,
                    price=product.price,
                    currency=product.currency,
                    is_available=product.is_available,
                    image_urls=json.dumps(product.image_urls, ensure_ascii=False),
                )
                self.db_session.add(main)
                self.db_session.flush()
                main_id = main.id
                self._log(f"  Создан родитель: {cleaned_title} (id={main_id})")

            # Атрибуты родителя
            for attr_name, attr_value in product.attributes.items():
                safe_name = attr_name[:255] if attr_name else ""
                safe_value = attr_value[:65535] if attr_value else ""
                if safe_name and safe_value:
                    attr = ProductAttribute(
                        product_id=main_id,
                        name=safe_name,
                        value=safe_value,
                    )
                    self.db_session.add(attr)

            # === 2. ВАРИАЦИИ (ДЕТИ) + СБОР РАЗМЕРОВ ===
            all_sizes = []
            for var in product.variations:
                size = var.get("attributes", {}).get("Размер")
                if size and size not in all_sizes:
                    all_sizes.append(size)
            
            if all_sizes:
                sizes_str = "|".join(all_sizes)
                existing_attr = self.db_session.execute(
                    select(ProductAttribute).where(
                        ProductAttribute.product_id == main_id,
                        ProductAttribute.name == "Доступные размеры"
                    )
                ).scalar_one_or_none()
                
                if existing_attr:
                    existing_attr.value = sizes_str
                else:
                    self.db_session.add(ProductAttribute(
                        product_id=main_id,
                        name="Доступные размеры",
                        value=sizes_str,
                    ))
                self._log(f"  Родитель: размеры = {sizes_str}")
            
            # Создание детей
            for var in product.variations:
                var_title = var.get("title", cleaned_title)
                var_attrs = var.get("attributes", {})
                var_product = Product(
                    supplier_id=self.supplier_id,
                    category_id=product.category_id,
                    parent_product_id=main_id,
                    external_sku=product.sku,
                    title=var_title if var_title else f"{cleaned_title} ({var_attrs.get('Размер', '')})",
                    description=var.get("description", product.description),
                    price=var.get("price", product.price),
                    currency=var.get("currency", product.currency),
                    is_available=var.get("is_available", product.is_available),
                    image_urls=json.dumps(var.get("image_urls", product.image_urls), ensure_ascii=False),
                )
                self.db_session.add(var_product)
                self.db_session.flush()
                var_id = var_product.id
                self._log(f"  Создана вариация: {var_product.title} (parent={main_id})")
                
                for attr_name, attr_value in var_attrs.items():
                    safe_name = attr_name[:255] if attr_name else ""
                    safe_value = attr_value[:65535] if attr_value else ""
                    if safe_name and safe_value:
                        self.db_session.add(ProductAttribute(
                            product_id=var_id,
                            name=safe_name,
                            value=safe_value,
                        ))

            # === 3. ПОГОНАЖ (НЕЗАВИСИМЫЕ!) ===
            if product.molding_items:
                # 🔥 Получаем ПОЛНЫЙ путь категории двери
                door_category_path = self._get_full_category_path(product.category_id)
                self._log(f"  Путь категории двери: '{door_category_path}'")
                
                for molding in product.molding_items:
                    try:
                        self._upsert_molding_item(molding, door_category_path)
                    except Exception as e:
                        self._log(f"  Ошибка погонажа {molding.get('title')}: {e}")
                        continue

            return main_id
            
        except Exception as e:
            logger_parser.error(f"Ошибка сохранения товара: {e}")
            self.stats["errors"].append(f"Database save error: {e}")
            raise

    async def run(self, urls: List[str], is_category: bool = True) -> Dict[str, Any]:
        """Запускает парсинг."""
        self._cancelled = False
        self._paused = False
        self._pause_event.set()
        self.stats = {
            "products_parsed": 0,
            "variations_parsed": 0,
            "molding_items_parsed": 0,
            "errors": [],
            "start_time": time.time(),
            "end_time": None,
        }
        self._seen_urls.clear()
        self._category_cache.clear()

        self._log(f"Запуск Playwright-парсера для поставщика {self.supplier_id}")
        self._log(f"URL для парсинга: {len(urls)} (категории={is_category})")

        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=self.headless)
            
            try:
                if is_category:
                    for category_url in urls:
                        if self._cancelled:
                            break
                        await self._parse_category(category_url)
                else:
                    # 🔥 Парсинг отдельных товаров
                    for product_url in urls:
                        if self._cancelled:
                            break
                        await self._pause_event.wait()
                        page = None
                        try:
                            page = await self.browser.new_page()
                            product = await self._parse_product_page(page, product_url)
                            await self._save_product(product)
                            self.stats["products_parsed"] += 1
                            self._progress(
                                self.stats["products_parsed"],
                                len(urls),
                                f"Обработано {self.stats['products_parsed']} товаров"
                            )
                            self._random_delay()
                        except Exception as e:
                            self._log(f"  Ошибка товара {product_url}: {e}")
                            self.stats["errors"].append(f"Product error: {product_url} - {e}")
                        finally:
                            if page and not page.is_closed():
                                await page.close()
                    
                # Обновление метаданных поставщика
                supplier = self.db_session.execute(
                    select(Supplier).where(Supplier.id == self.supplier_id)
                ).scalar_one_or_none()
                if supplier:
                    supplier.last_scrape_run = datetime.utcnow()
                    self.db_session.flush()
                     
            finally:
                await self.browser.close()
                self.browser = None
                
        self.stats["end_time"] = time.time()
        elapsed = self.stats["end_time"] - self.stats["start_time"]
        
        self._log(f"Парсинг завершён: {self.stats['products_parsed']} товаров, {elapsed:.1f}с")
        
        return {
            "success": True,
            "products_parsed": self.stats["products_parsed"],
            "variations_parsed": self.stats["variations_parsed"],
            "molding_items_parsed": self.stats["molding_items_parsed"],
            "errors": self.stats["errors"],
            "elapsed": elapsed,
        }

    async def _parse_category(self, category_url: str) -> Dict[str, Any]:
        if self._cancelled:
            return self.stats

        await self._pause_event.wait()

        if not self.browser:
            raise RuntimeError("Browser not initialized")
            
        page = await self.browser.new_page()
        
        try:
            await page.goto(category_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(1000)
            
            product_links = []
            link_elements = await page.query_selector_all("a[href*='/catalog/']")
            
            for link_el in link_elements:
                href = await link_el.get_attribute("href")
                if href:
                    full_url = urljoin(category_url, href.split("#")[0])
                    # 🔥 КЛЮЧЕВОЙ ФИЛЬТР: только домен tandoor.ru и только /product/
                    if (
                        "/product/" in full_url 
                        and full_url.startswith("https://tandoor.ru")
                        and full_url not in self._seen_urls
                    ):
                        product_links.append(full_url)
                        self._seen_urls.add(full_url)
            
            self._log(f"  Категория: найдено {len(product_links)} товаров")
            
            parsed_products = []
            total_links = len(product_links)
            
            for i, product_url in enumerate(product_links):
                if self._cancelled:
                    break
                    
                await self._pause_event.wait()
                
                try:
                    product = await self._parse_product_page(page, product_url)
                    parsed_products.append(product)
                    self.stats["products_parsed"] += 1
                    
                    self._progress(
                        self.stats["products_parsed"],
                        total_links,
                        f"Распаршено {self.stats['products_parsed']} товаров"
                    )
                    
                    self._random_delay()
                except Exception as e:
                    self._log(f"  Ошибка товара {product_url}: {e}")
                    self.stats["errors"].append(f"Product parse error: {product_url} - {e}")
                    continue
            
            for product in parsed_products:
                try:
                    await self._save_product(product)
                except Exception as e:
                    self._log(f"  Ошибка сохранения {product.title}: {e}")
                    self.stats["errors"].append(f"Product save error: {product.title} - {e}")
                    continue
                    
        except Exception as e:
            logger_parser.error(f"Ошибка парсинга категории {category_url}: {e}")
            self.stats["errors"].append(f"Category parse error: {category_url} - {e}")
        final                                                                            