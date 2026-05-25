import asyncio
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

from playwright.async_api import async_playwright, Page
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import Category, Product, ProductAttribute
from src.modules.parsing.base_parser import BaseParser, ParsedProduct
from playwright_stealth import Stealth

PARENT_TITLE_RE = re.compile(r"\s*/.*")

class ParserEngine(BaseParser):
    """Legacy parser kept for backward compatibility. Use TandoorPlaywrightParser instead."""
    def __init__(self, base_url: str, **kwargs: Any):
        super().__init__(**kwargs)
        self.base_url = base_url

    async def _parse_product_page(self, page: Page, url: str, **kwargs) -> Optional[List[ParsedProduct]]:
        """Парсит страницу продукта. Возвращает список из одного элемента [ParsedProduct]."""
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            data = await page.evaluate('''() => {
                const title = document.querySelector("h1")?.innerText || "Без названия";
                const price = parseFloat(document.querySelector(".Product-description__item-price-value")?.innerText.replace(/[^0-9.]/g, '') || 0);
                const attrs = {};
                document.querySelectorAll(".characteristics-table__row").forEach(row => {
                    const k = row.querySelector(".key")?.innerText.trim();
                    const v = row.querySelector(".value")?.innerText.trim();
                    if (k && v) attrs[k] = v;
                });
                return { title, price, attrs };
            }''')
            product = ParsedProduct(url=url, title=data['title'].strip(), price=data['price'])
            product.attributes = data['attrs']
            return [product]
        except Exception as e:
            self._log(f"Ошибка парсинга {url}: {e}")
            return None

    def _save_product_sync(self, product: ParsedProduct, session: Session):
        # Чистое название без спецификаций после /
        clean_title = PARENT_TITLE_RE.sub("", product.title).strip()
        
        # Ищем или создаем родителя
        parent = session.query(Product).filter_by(
            supplier_id=self.supplier_id, 
            title=clean_title, 
            parent_product_id=None
        ).first()
        
        if not parent:
            parent = Product(
                supplier_id=self.supplier_id, 
                category_id=product.category_id,
                title=clean_title, 
                price=product.price,
                currency=product.currency,
                description=product.description,
            )
            session.add(parent)
            session.flush()
        elif product.category_id is not None:
            parent.category_id = product.category_id
        
        # Сохраняем вариацию с чистым названием
        child_title = clean_title
        
        child = session.query(Product).filter_by(
            parent_product_id=parent.id, 
            title=child_title
        ).first()
        
        if not child:
            child = Product(
                supplier_id=self.supplier_id, 
                parent_product_id=parent.id, 
                category_id=product.category_id,
                title=child_title, 
                price=product.price,
                currency=product.currency,
            )
            session.add(child)
            session.flush()
            
            # Сохраняем все атрибуты
            for attr_name, attr_value in product.attributes.items():
                session.add(ProductAttribute(
                    product_id=child.id, 
                    name=attr_name, 
                    value=attr_value
                ))
        elif product.category_id is not None:
            child.category_id = product.category_id
        
        session.commit()

    async def run(self, session: Session, **kwargs: Any) -> Dict[str, Any]:
        categories = session.execute(select(Category).where(Category.id.in_(kwargs.get("category_ids", [])))).scalars().all()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            await Stealth().apply_stealth_async(page)
            for cat in categories:
                await page.goto(urljoin(self.base_url, cat.url), wait_until="domcontentloaded")
                links = await page.eval_on_selector_all("a[href*='/catalog/product/']", "es => [...new Set(es.map(e => e.href))]")
                for url in links:
                    if self._cancelled: break
                    products = await self._parse_product_page(page, url)
                    if products:
                        for product in products:
                            await asyncio.to_thread(self._save_product_sync, product, session)
                        self.stats["products_parsed"] += 1
            await browser.close()
        return self.stats
