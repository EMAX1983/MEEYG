import asyncio
import logging
import random
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp
from bs4 import BeautifulSoup, Tag
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.logger import logger

logger_discovery = logging.getLogger("meeyg.discovery")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/124.0.0.0 Safari/537.36",
]

CMS_PATTERNS = {
    "bitrix": [r"bitrix/", r"BX\.setForm", r"/bitrix/js/", r"bitrix:catalog", r"bitrix\.template"],
    "woocommerce": [r"woocommerce", r"wc-ajax", r"wp-content/plugins/woocommerce"],
    "opencart": [r"route=product/category", r"index\.php\?route=", r"opencart"],
    "prestashop": [r"prestashop", r"themes/prestashop"],
    "magento": [r"mage/", r"static/frontend/", r"Magento"],
}

EXCLUDE_PATTERNS = re.compile(
    r"(\?|filter|sort|clear|back|login|cart|korzina|checkout|order|zakaz|"
    r"search|poisk|ajax|api|upload|bitrix|include|component|local/|"
    r"\.html$|\.php$|\.pdf$|\.jpg$|\.png$|\.jpeg$|\.gif$|\.svg$|\.ico$)",
    re.IGNORECASE,
)

EXCLUDE_KEYWORDS = [
    "about", "o-kompanii", "o_kompanii", "contacts", "kontakty",
    "delivery", "dostavka", "oplata", "payment",
    "news", "novosti", "blog", "articles",
    "reviews", "otzyvy", "feedback",
    "login", "auth", "register", "personal", "profile",
    "search", "poisk", "ajax", "api", "upload",
    "wishlist", "favorites", "izbrannoe", "compare", "sravnenie",
    "vacancies", "vakansii", "partners", "partneram",
    "sitemap", "map", "privacy", "policy",
    "3d-tur", "3d_tur", "action", "sale",
]

EXCLUDE_KEYWORDS_RE = re.compile(
    r"/(" + "|".join(EXCLUDE_KEYWORDS) + r")(/|$|\?)",
    re.IGNORECASE,
)


@dataclass
class DiscoveredCategory:
    name: str
    url: str
    xpath_selector: str = ""
    product_count: int = 0
    children: list["DiscoveredCategory"] = field(default_factory=list)
    depth: int = 0
    external_id: Optional[str] = None


class BaseDiscovery(ABC):
    def __init__(
        self,
        base_url: str,
        session: aiohttp.ClientSession,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        max_depth: int = 3,
        delay_range: tuple[float, float] = (0.5, 2.0),
        check_robots: bool = True,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.log_callback = log_callback or (lambda m: logger_discovery.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self.max_depth = max_depth
        self.delay_range = delay_range
        self.check_robots = check_robots
        self.timeout = timeout
        self.robots_allowed = True
        self.visited_urls: set[str] = set()
        self._total_pages = 0
        self._pages_scanned = 0

    def _log(self, msg: str) -> None:
        self.log_callback(msg)

    def _progress(self, msg: str) -> None:
        self._pages_scanned += 1
        pct = int((self._pages_scanned / max(self._total_pages, 1)) * 100)
        self.progress_callback(pct, self._total_pages, msg)

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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True,
    )
    async def fetch_page(self, url: str) -> Optional[str]:
        if url in self.visited_urls:
            return None
        self.visited_urls.add(url)

        try:
            async with self.session.get(
                url, headers=self._get_headers(), timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status == 404:
                    self._log(f"  404: {url}")
                    return None
                if resp.status == 403:
                    self._log(f"  403: {url}")
                    return None
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

    def _check_robots(self) -> None:
        if not self.check_robots:
            return
        robots_url = urljoin(self.base_url, "/robots.txt")
        try:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            self.robots_allowed = rp.can_fetch(random.choice(USER_AGENTS), self.base_url)
            if not self.robots_allowed:
                self._log(f"WARNING: robots.txt блокирует доступ к {self.base_url}")
        except Exception:
            self._log("WARNING: Не удалось загрузить robots.txt, продолжаем без проверки")

    def _is_internal_url(self, url: str) -> bool:
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)
        return parsed.netloc == base_parsed.netloc

    def _clean_url(self, url: str) -> str:
        url = url.split("#")[0]
        url = url.split("?")[0]
        url = url.rstrip("/")
        return url

    def _build_xpath(self, element: Tag) -> str:
        parts = []
        current: Tag | None = element
        while current and current.name:
            selector = current.name
            if current.get("id"):
                selector += f"[@id='{current['id']}']"
                parts.append(selector)
                break
            if current.get("class"):
                cls = " ".join(str(c) for c in current["class"])
                selector += f"[contains(concat(' ', normalize-space(@class), ' '), ' {cls} ')]"
            parts.append(selector)
            current = current.parent
        parts.reverse()
        return "/" + "/".join(parts)

    def detect_cms(self, html: str) -> Optional[str]:
        for cms, patterns in CMS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, html, re.IGNORECASE):
                    return cms
        return None

    @abstractmethod
    async def discover_categories(self) -> list[DiscoveredCategory]:
        pass

    async def run(self) -> list[DiscoveredCategory]:
        self._log(f"Начало разведки: {self.base_url}")
        self._check_robots()
        if not self.robots_allowed:
            self._log("Прервано: robots.txt запрещает доступ")
            return []
        result = await self.discover_categories()
        self._log(f"Разведка завершена: найдено {len(result)} категорий верхнего уровня")
        return result


class CatalogDiscovery(BaseDiscovery):
    """Универсальная стратегия: ищет все ссылки с /catalog/ и строит иерархию из URL."""

    def _is_excluded_url(self, url: str) -> bool:
        if EXCLUDE_PATTERNS.search(url):
            return True
        path = urlparse(url).path.lower()
        if EXCLUDE_KEYWORDS_RE.search(path):
            return True
        return False

    def _is_catalog_link(self, url: str) -> bool:
        path = urlparse(url).path.lower()
        return "/catalog/" in path

    def _get_url_segments(self, url: str) -> list[str]:
        path = urlparse(url).path
        return [s for s in path.split("/") if s]

    def _get_parent_url(self, url: str) -> Optional[str]:
        segments = self._get_url_segments(url)
        if len(segments) <= 1:
            return None
        parent_path = "/" + "/".join(segments[:-1]) + "/"
        return urljoin(self.base_url, parent_path).rstrip("/")

    def _extract_all_catalog_links(self, soup: BeautifulSoup, page_url: str) -> list[DiscoveredCategory]:
        categories = []
        seen_urls: set[str] = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue

            full_url = urljoin(page_url, href)

            if not self._is_internal_url(full_url):
                continue
            if not self._is_catalog_link(full_url):
                continue
            if self._is_excluded_url(full_url):
                continue

            clean_url = self._clean_url(full_url)
            if clean_url in seen_urls:
                continue
            if clean_url in self.visited_urls:
                continue

            name = a_tag.get_text(strip=True)
            if not name or len(name) < 2:
                continue

            xpath = self._build_xpath(a_tag)
            cat = DiscoveredCategory(
                name=name,
                url=clean_url,
                xpath_selector=xpath,
            )
            categories.append(cat)
            seen_urls.add(clean_url)

        return categories

    def _build_tree_from_urls(self, all_cats: list[DiscoveredCategory]) -> list[DiscoveredCategory]:
        url_map: dict[str, DiscoveredCategory] = {}
        for cat in all_cats:
            url_map[cat.url] = cat

        url_list = sorted(url_map.keys(), key=lambda u: len(self._get_url_segments(u)))

        roots: list[DiscoveredCategory] = []

        for url in url_list:
            cat = url_map[url]
            parent_url = self._get_parent_url(url)

            if parent_url and parent_url in url_map:
                parent = url_map[parent_url]
                parent.children.append(cat)
                cat.depth = parent.depth + 1
            else:
                roots.append(cat)
                cat.depth = 0

        return roots

    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log("Универсальный поиск каталога (метод грубой силы)")

        catalog_url = urljoin(self.base_url, "/catalog/")

        html = await self.fetch_page(catalog_url)
        if not html:
            self._log(f"Не удалось загрузить {catalog_url}, пробую главную")
            html = await self.fetch_page(self.base_url)
            if not html:
                self._log("Не удалось загрузить главную страницу")
                return []
            page_url = self.base_url
        else:
            page_url = catalog_url

        self._random_delay()
        self._progress(f"Анализ: {page_url}")

        soup = BeautifulSoup(html, "lxml")
        cats = self._extract_all_catalog_links(soup, page_url)
        self._log(f"Найдено {len(cats)} уникальных ссылок с /catalog/ на странице {page_url}")

        if not cats:
            self._log("Ссылки с /catalog/ не найдены, сканирую вложенные страницы...")
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                if not href or href.startswith(("javascript:", "mailto:")):
                    continue
                raw_url = urljoin(page_url, href)
                if not self._is_internal_url(raw_url):
                    continue
                if "/catalog/" not in raw_url.lower():
                    continue
                if self._is_excluded_url(raw_url):
                    continue
                link_url = self._clean_url(raw_url)
                if link_url not in self.visited_urls:
                    sub_html = await self.fetch_page(raw_url)
                    if sub_html:
                        self._random_delay()
                        sub_soup = BeautifulSoup(sub_html, "lxml")
                        sub_cats = self._extract_all_catalog_links(sub_soup, raw_url)
                        for sc in sub_cats:
                            if sc.url not in [c.url for c in cats]:
                                cats.append(sc)
                            self._log(f"  +{len(sub_cats)} ссылок со страницы {link_url}")

        if not cats:
            self._log("Категории не найдены")
            return []

        roots = self._build_tree_from_urls(cats)
        self._log(f"Построено дерево из {len(cats)} категорий ({len(roots)} корней)")

        return roots


class GenericDiscovery(BaseDiscovery):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _looks_like_category_page(self, url: str, text: str) -> bool:
        path = urlparse(url).path.lower()
        keywords = [
            "catalog", "category", "cat", "section", "department", "shop",
            "каталог", "категория", "раздел",
        ]
        combined = f"{path} {text}".lower()
        return any(kw in combined for kw in keywords)

    async def _scan_page_for_categories(self, url: str, depth: int = 0) -> list[DiscoveredCategory]:
        if depth > self.max_depth:
            return []

        html = await self.fetch_page(url)
        if not html:
            return []

        self._random_delay()
        self._progress(f"Сканирование: {url}")

        soup = BeautifulSoup(html, "lxml")
        categories = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue
            full_url = self._clean_url(urljoin(url, href))
            if not self._is_internal_url(full_url):
                continue
            name = a_tag.get_text(strip=True)
            if not name or len(name) < 2:
                continue
            if self._looks_like_category_page(full_url, name):
                xpath = self._build_xpath(a_tag)
                cat = DiscoveredCategory(name=name, url=full_url, xpath_selector=xpath, depth=depth + 1)
                categories.append(cat)

        if depth < self.max_depth:
            for cat in categories[:10]:
                if cat.url not in self.visited_urls:
                    children = await self._scan_page_for_categories(cat.url, depth + 1)
                    cat.children = children
                    if children:
                        self._log(f"  Найдено {len(children)} подкатегорий в '{cat.name}'")

        return categories

    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log(f"Сканирование главной: {self.base_url}")
        html = await self.fetch_page(self.base_url)
        if not html:
            self._log("Не удалось загрузить главную страницу")
            return []

        self._random_delay()
        soup = BeautifulSoup(html, "lxml")
        cms = self.detect_cms(html)
        if cms:
            self._log(f"Обнаружена CMS: {cms}")

        categories = await self._scan_page_for_categories(self.base_url, depth=0)

        seen_urls = set()
        unique = []
        for cat in categories:
            if cat.url not in seen_urls:
                seen_urls.add(cat.url)
                unique.append(cat)

        return unique


class BitrixDiscovery(CatalogDiscovery):
    """Стратегия для 1С-Битрикс: использует CatalogDiscovery с fallback на общий поиск."""

    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log("Использование стратегии для 1С-Битрикс")
        return await super().discover_categories()


class WooCommerceDiscovery(GenericDiscovery):
    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log("Использование стратегии для WooCommerce")
        shop_urls = [
            urljoin(self.base_url, "/shop/"),
            urljoin(self.base_url, "/product-category/"),
        ]
        all_cats = []
        for url in shop_urls:
            cats = await self._scan_page_for_categories(url, depth=0)
            all_cats.extend(cats)
        return all_cats


class OpenCartDiscovery(GenericDiscovery):
    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log("Использование стратегии для OpenCart")
        catalog_url = urljoin(self.base_url, "/index.php?route=product/category")
        return await self._scan_page_for_categories(catalog_url, depth=0)


STRATEGY_MAP: dict[str, type[BaseDiscovery]] = {
    "bitrix": BitrixDiscovery,
    "woocommerce": WooCommerceDiscovery,
    "opencart": OpenCartDiscovery,
}


class DiscoveryEngine:
    def __init__(
        self,
        supplier_id: int,
        base_url: str,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        max_depth: int = 3,
        delay_range: tuple[float, float] = (0.5, 2.0),
        check_robots: bool = True,
        timeout: int = 30,
    ):
        self.supplier_id = supplier_id
        self.base_url = base_url
        self.log_callback = log_callback or (lambda m: logger_discovery.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self.max_depth = max_depth
        self.delay_range = delay_range
        self.check_robots = check_robots
        self.timeout = timeout
        self._cancelled = False
        # ✅ ИСПРАВЛЕНИЕ: Добавлен алиас для совместимости
        self._log = self.log_callback

    def cancel(self) -> None:
        self._cancelled = True

    def _build_strategy(
        self, session: aiohttp.ClientSession, cms: Optional[str] = None
    ) -> BaseDiscovery:
        if cms and cms in STRATEGY_MAP:
            cls = STRATEGY_MAP[cms]
        else:
            cls = CatalogDiscovery

        return cls(
            base_url=self.base_url,
            session=session,
            log_callback=self.log_callback,
            progress_callback=self.progress_callback,
            max_depth=self.max_depth,
            delay_range=self.delay_range,
            check_robots=self.check_robots,
            timeout=self.timeout,
        )

    async def _detect_cms_async(self, session: aiohttp.ClientSession) -> Optional[str]:
        try:
            async with session.get(
                self.base_url,
                headers={"User-Agent": random.choice(USER_AGENTS)},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    html = await resp.text(errors="replace")
                    for cms, patterns in CMS_PATTERNS.items():
                        for pattern in patterns:
                            if re.search(pattern, html, re.IGNORECASE):
                                return cms
        except Exception:
            pass
        return None

    def _save_to_db(self, categories: list[DiscoveredCategory], db_session) -> int:
        from src.database.models import Category

        count = 0

        def _save_recursive(cats: list[DiscoveredCategory], parent_id: Optional[int] = None):
            nonlocal count
            for cat in cats:
                if self._cancelled:
                    return

                existing = db_session.query(Category).filter(
                    Category.supplier_id == self.supplier_id,
                    Category.url == cat.url,
                ).first()

                if existing:
                    self._log(f"  Дубликат пропущен: {cat.name} ({cat.url})")
                    existing.name = cat.name
                    existing.xpath_selector = cat.xpath_selector or existing.xpath_selector
                    existing.product_count = cat.product_count
                    existing.parent_id = parent_id
                    db_category = existing
                else:
                    db_category = Category(
                        supplier_id=self.supplier_id,
                        parent_id=parent_id,
                        name=cat.name,
                        url=cat.url,
                        xpath_selector=cat.xpath_selector,
                        product_count=cat.product_count,
                        external_id=cat.external_id,
                    )
                    db_session.add(db_category)
                    db_session.flush()
                    self._log(f"  Сохранено: {cat.name} (parent_id={parent_id})")

                count += 1
                if cat.children:
                    _save_recursive(cat.children, db_category.id)

        _save_recursive(categories)
        return count

    async def run(self, db_session) -> dict[str, Any]:
        self._cancelled = False
        self.log_callback(f"Движок разведки запущен для {self.base_url}")

        connector = aiohttp.TCPConnector(ssl=False, limit=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            cms = await self._detect_cms_async(session)
            strategy = self._build_strategy(session, cms)

            if cms:
                self.log_callback(f"CMS определена: {cms}, используется стратегия для {cms}")
            else:
                self.log_callback("CMS не определена, используется универсальный поиск")

            try:
                categories = await strategy.run()
            except Exception as exc:
                self.log_callback(f"Разведка не удалась: {exc}")
                return {"success": False, "error": str(exc), "categories_found": 0}

            if self._cancelled:
                self.log_callback("Разведка отменена пользователем")
                return {"success": False, "error": "cancelled", "categories_found": 0}

            if not categories:
                self.log_callback("Категории не найдены")
                self._update_supplier_timestamp(db_session)
                return {"success": True, "categories_found": 0, "categories": []}

            self.log_callback(f"Сохранение {len(categories)} категорий верхнего уровня в БД...")
            try:
                saved_count = self._save_to_db(categories, db_session)
                db_session.commit()
                self.log_callback(f"Сохранено {saved_count} категорий в базу данных")
            except Exception as exc:
                db_session.rollback()
                self.log_callback(f"Ошибка сохранения в БД: {exc}")
                return {"success": False, "error": f"DB error: {exc}", "categories_found": 0}

            self._update_supplier_timestamp(db_session)

            return {
                "success": True,
                "categories_found": saved_count,
                "categories": categories,
            }

    def _update_supplier_timestamp(self, db_session) -> None:
        from src.database.models import Supplier

        supplier = db_session.query(Supplier).filter(Supplier.id == self.supplier_id).first()
        if supplier:
            supplier.last_discovery_run = datetime.utcnow()
            db_session.flush()