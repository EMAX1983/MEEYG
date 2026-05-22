"""
Модуль экспорта товаров в CSV-формат, совместимый с WooCommerce.

Поддерживает:
- Variable products (родители) и вариации (дети)
- Простыe товары (simple)
- Корректное сопоставление Parent → child через SKU
- Экспорт из ArchiveItem (со всеми заполненными полями)
"""

import csv
import gc
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from src.core.config import settings
from src.core.logger import logger

logger_export = logging.getLogger("meeyg.export")

# WooCommerce-совместимые колонки (CSV Export для WP All Import)
WOOCOMMERCE_COLUMNS = [
    "Type",
    "SKU",
    "Name",
    "Published",
    "Is featured",
    "Visibility in catalog",
    "Short description",
    "Description",
    "Date sale price starts at",
    "Date sale price ends at",
    "Tax status",
    "Tax class",
    "In stock?",
    "Stock",
    "Backorders allowed?",
    "Low stock amount threshold",
    "Sold individually?",
    "Weight (kg)",
    "Length (cm)",
    "Width (cm)",
    "Height (cm)",
    "Allow customer reviews?",
    "Purchase note",
    "Sale price",
    "Regular price",
    "Categories",
    "Tags",
    "Shipping class",
    "Images",
    "Download limit",
    "Download expiry days",
    "Parent",
    "Grouped products",
    "Upsells",
    "Cross-sells",
    "External URL",
    "Button text",
    "Position",
    "Attribute 1 name",
    "Attribute 1 value(s)",
    "Attribute 1 visible",
    "Attribute 2 name",
    "Attribute 2 value(s)",
    "Attribute 2 visible",
    "Attribute 3 name",
    "Attribute 3 value(s)",
    "Attribute 3 visible",
    "Attribute 1 global",
    "Attribute 2 global",
    "Attribute 3 global",
    "Attribute 1 default attribute",
    "Attribute 2 default attribute",
    "Attribute 3 default attribute",
    "Is variant",
]


@dataclass
class ExportConfig:
    supplier_ids: Optional[list[int]] = None
    snapshot_id: Optional[int] = None
    ready_only: bool = False
    available_only: bool = False
    use_archive: bool = True
    encoding: str = "utf-8-sig"
    output_dir: Optional[Path] = None

    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = settings.data_dir / "exports"
        self.output_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class ExportStats:
    total_products: int = 0
    exported_products: int = 0
    parents: int = 0
    variations: int = 0
    simple_products: int = 0
    duplicate_skus: int = 0
    empty_titles: int = 0
    empty_prices: int = 0
    errors: int = 0
    elapsed: float = 0.0
    file_size: int = 0
    output_path: str = ""


class ExportEngine:
    """Экспорт товаров в CSV для WooCommerce."""

    def __init__(
        self,
        config: ExportConfig,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        self.config = config
        self.log_callback = log_callback or (lambda m: logger_export.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self._cancelled = False
        self.stats = ExportStats()

    def cancel(self) -> None:
        self._cancelled = True

    def _log(self, msg: str) -> None:
        self.log_callback(msg)

    def _progress(self, pct: int, total: int, msg: str) -> None:
        self.progress_callback(pct, total, msg)

    # ====== ИСТОЧНИК ДАННЫХ ======

    def _fetch_archive_items(self, db_session) -> list[dict]:
        """Загружает данные из ArchiveSnapshot (если use_archive=True)."""
        from src.database.models import ArchiveItem, ArchiveSnapshot

        if self.config.snapshot_id:
            snapshot = db_session.query(ArchiveSnapshot).get(self.config.snapshot_id)
        else:
            snapshot = (
                db_session.query(ArchiveSnapshot)
                .filter(
                    ArchiveSnapshot.supplier_id.in_(self.config.supplier_ids)
                    if self.config.supplier_ids
                    else True
                )
                .order_by(ArchiveSnapshot.created_at.desc())
                .first()
            )

        if not snapshot:
            self._log("No archive snapshot found, falling back to Product export")
            return []

        query = db_session.query(ArchiveItem).filter(
            ArchiveItem.snapshot_id == snapshot.id
        )
        if self.config.available_only:
            query = query.filter(ArchiveItem.is_available == True)

        items = query.order_by(ArchiveItem.product_id).all()
        self.stats.total_products = len(items)
        self._log(f"Loaded {len(items)} items from archive snapshot '{snapshot.name}'")

        results = []
        for item in items:
            attrs = item.get_attributes()
            results.append({
                "_is_parent": item.is_parent,
                "_has_parent": not item.is_parent,
                "_parent_sku": item.parent_sku or "",
                "_manufacturer": item.manufacturer or "",
                "_collection": item.collection or "",
                "_brand": item.brand or "",
                "_vendor": item.vendor or "",
                "_availability": item.availability or "",
                "_stock_status": item.stock_status or ("instock" if item.is_available else "outofstock"),
                "_description": item.description or "",
                "id": item.product_id,
                "external_sku": item.external_sku,
                "title": item.title,
                "price": item.price,
                "currency": item.currency or "RUB",
                "is_available": item.is_available,
                "category_name": item.category_name or "Uncategorized",
                "image_urls": item.get_image_urls(),
                "attributes_raw": attrs,
            })
        return results

    def _fetch_products(self, db_session) -> list[dict]:
        """Загружает данные напрямую из Product (fallback)."""
        from src.database.models import Category, Product, ProductAttribute, Supplier

        self._log("Fetching products from database (fallback)...")

        query = db_session.query(Product)
        if self.config.supplier_ids:
            query = query.filter(Product.supplier_id.in_(self.config.supplier_ids))
        if self.config.ready_only:
            query = query.filter(Product.is_ready_for_export == True)
        if self.config.available_only:
            query = query.filter(Product.is_available == True)

        products = query.order_by(Product.id).all()
        self.stats.total_products = len(products)
        self._log(f"Found {len(products)} products")

        # Загружаем атрибуты
        attr_query = db_session.query(ProductAttribute)
        if self.config.supplier_ids:
            attr_query = attr_query.join(Product).filter(
                Product.supplier_id.in_(self.config.supplier_ids)
            )
        attributes_map: dict[int, dict[str, str]] = {}
        for attr in attr_query:
            attributes_map.setdefault(attr.product_id, {})[attr.name] = attr.value

        # Загружаем parents для children
        parent_ids = {p.parent_product_id for p in products if p.parent_product_id}
        parent_map: dict[int, Product] = {}
        if parent_ids:
            parents = db_session.query(Product).filter(Product.id.in_(parent_ids)).all()
            parent_map = {p.id: p for p in parents}

        # Загружаем SKU родителей
        parent_sku_map: dict[int, str] = {}
        for pid, parent in parent_map.items():
            parent_sku_map[pid] = parent.external_sku or ""

        # Загружаем Supplier.name
        supplier_names: dict[int, str] = {}
        if self.config.supplier_ids:
            suppliers = db_session.query(Supplier).filter(
                Supplier.id.in_(self.config.supplier_ids)
            ).all()
            supplier_names = {s.id: s.name for s in suppliers}

        results = []
        for p in products:
            attrs = attributes_map.get(p.id, {})
            is_parent = p.parent_product_id is None
            parent_sku = ""
            manufacturer = ""

            if is_parent:
                manufacturer = supplier_names.get(p.supplier_id, "")
            else:
                parent = parent_map.get(p.parent_product_id)
                if parent:
                    parent_sku = parent.external_sku or ""
                    manufacturer = supplier_names.get(parent.supplier_id, "")

            # Коллекция
            collection = ""
            mfr_coll = attrs.get("Manufacturer of the collection", "")
            if mfr_coll and ">" in mfr_coll:
                collection = mfr_coll.split(">")[-1].strip()
            elif mfr_coll:
                collection = mfr_coll
            elif is_parent:
                collection = (p.title or "").strip()
            attrs["Manufacturer of the collection"] = collection

            image_urls = []
            if p.image_urls:
                try:
                    image_urls = json.loads(p.image_urls)
                except (json.JSONDecodeError, TypeError):
                    pass

            cat_name = "Uncategorized"
            if p.category:
                cat_name = p.category.name
                if p.category.parent:
                    cat_name = f"{p.category.parent.name} > {p.category.name}"

            results.append({
                "_is_parent": is_parent,
                "_has_parent": p.parent_product_id is not None,
                "_parent_sku": parent_sku,
                "_manufacturer": manufacturer,
                "_collection": collection,
                "_brand": manufacturer,
                "_vendor": manufacturer,
                "_availability": "в наличии" if p.is_available else "нет в наличии",
                "_stock_status": "instock" if p.is_available else "outofstock",
                "_description": p.description or "",
                "id": p.id,
                "external_sku": p.external_sku,
                "title": p.title,
                "price": p.price,
                "currency": p.currency or "RUB",
                "is_available": p.is_available,
                "category_name": cat_name,
                "image_urls": image_urls,
                "attributes_raw": attrs,
            })
        return results

    # ====== ТРАНСФОРМАЦИЯ ======

    def _transform_to_csv_rows(self, items: list[dict]) -> list[list]:
        """Преобразует данные товаров в строки CSV."""
        self._log("Transforming data to WooCommerce CSV format...")
        rows = []
        seen_skus: set[str] = set()

        for i, item in enumerate(items):
            if self._cancelled:
                break

            title = (item["title"] or "").strip()
            if not title:
                title = f"Product {item['id']}"
                self.stats.empty_titles += 1

            sku = item["external_sku"] or f"MEYG-{item['id']}"
            if sku in seen_skus:
                base = sku
                c = 1
                while sku in seen_skus:
                    sku = f"{base}-{c}"
                    c += 1
                self.stats.duplicate_skus += 1
            seen_skus.add(sku)

            price = item["price"]
            if price is None:
                self.stats.empty_prices += 1
                price = 0.0

            is_parent = item["_is_parent"]
            has_parent = item["_has_parent"]
            attrs = item.get("attributes_raw", {})

            # Определяем тип
            if is_parent:
                product_type = "variable"
                self.stats.parents += 1
            elif has_parent:
                product_type = ""
                self.stats.variations += 1
            else:
                product_type = "simple"
                self.stats.simple_products += 1

            # Parent SKU
            parent_sku = item["_parent_sku"] if has_parent else ""

            # Категории
            category = item["category_name"] or "Uncategorized"

            # Изображения
            image_urls = item.get("image_urls", [])
            if image_urls and isinstance(image_urls, str):
                images_str = image_urls
            elif image_urls and isinstance(image_urls, list):
                images_str = ",".join(url for url in image_urls if url and url.startswith("http"))
            else:
                images_str = ""

            # Краткое описание
            desc = item["_description"] or ""
            short_desc = (desc[:500] + "...") if len(desc) > 500 else desc

            # Извлекаем ключевые атрибуты для WooCommerce
            size = attrs.get("Размер", "")
            color = attrs.get("Цвет", "")
            direction = attrs.get("Направление", "")

            # Тип товара и атрибуты для вариаций
            product_type_attr = attrs.get("Тип", "")
            if product_type_attr == "Погонаж":
                # Для погонажа — это простой товар
                if is_parent or has_parent:
                    product_type = "simple" if not has_parent else ""
                    if product_type == "simple":
                        self.stats.simple_products += 1
                        self.stats.parents -= is_parent  # undo if was counted

            # Для вариаций (child products) тип пустой
            if has_parent:
                # variation
                attr1_name = "Цвет"
                attr1_val = color or ""
                attr2_name = "Размер"
                attr2_val = size or ""
                attr3_name = "Направление"
                attr3_val = direction or ""
                is_variant = "1"
            elif is_parent:
                # variable — атрибуты с вариантами
                attr1_name = "pa_цвет"
                attr1_val = color or ""
                attr2_name = "pa_размер"
                attr2_val = size or ""
                attr3_name = "pa_направление"
                attr3_val = direction or ""
                is_variant = ""
            else:
                # simple
                attr1_name = ""
                attr1_val = ""
                attr2_name = ""
                attr2_val = ""
                attr3_name = ""
                attr3_val = ""
                is_variant = ""

            # Строим строку CSV
            row = [
                product_type,                        # Type
                sku,                                  # SKU
                title,                                # Name
                "1",                                  # Published
                "0",                                  # Is featured
                "visible",                            # Visibility
                short_desc,                           # Short description
                desc,                                 # Description
                "",                                   # Date sale starts
                "",                                   # Date sale ends
                "taxable",                            # Tax status
                "",                                   # Tax class
                item["_stock_status"],                # In stock?
                "",                                   # Stock quantity
                "no",                                 # Backorders
                "",                                   # Low stock amount
                "no",                                 # Sold individually
                "",                                   # Weight
                size or "",                           # Length
                "",                                   # Width
                self._extract_thickness(attrs) if not has_parent else "",  # Height
                "yes",                                # Allow reviews
                "",                                   # Purchase note
                "",                                   # Sale price
                f"{price:.2f}" if price else "",      # Regular price
                category,                             # Categories
                "",                                   # Tags
                "",                                   # Shipping class
                images_str,                           # Images
                "",                                   # Download limit
                "",                                   # Download expiry
                parent_sku,                           # Parent
                "",                                   # Grouped products
                "",                                   # Upsells
                "",                                   # Cross-sells
                "",                                   # External URL
                "",                                   # Button text
                "",                                   # Position
                attr1_name,                           # Attr 1 name
                attr1_val,                            # Attr 1 values
                "1" if not has_parent and attr1_val else "0",  # Attr 1 visible
                attr2_name,                           # Attr 2 name
                attr2_val,                            # Attr 2 values
                "1" if not has_parent and attr2_val else "0",  # Attr 2 visible
                attr3_name,                           # Attr 3 name
                attr3_val,                            # Attr 3 values
                "1" if not has_parent and attr3_val else "0",  # Attr 3 visible
                "yes" if not has_parent else "",      # Attr 1 global
                "yes" if not has_parent else "",      # Attr 2 global
                "yes" if not has_parent else "",      # Attr 3 global
                "",                                   # Attr 1 default
                "",                                   # Attr 2 default
                "",                                   # Attr 3 default
                is_variant,                           # Is variant
            ]
            rows.append(row)

            if (i + 1) % 100 == 0:
                pct = int(((i + 1) / max(self.stats.total_products, 1)) * 100)
                self._progress(pct, self.stats.total_products, f"Transformed {i + 1} products")

        self.stats.exported_products = len(rows)
        self._log(f"Transformed {len(rows)} products (parents={self.stats.parents}, var={self.stats.variations}, simple={self.stats.simple_products})")
        return rows

    @staticmethod
    def _extract_thickness(attrs: dict) -> str:
        """Извлекает толщину из характеристик."""
        thickness_key = "Толщина полотна, мм"
        if thickness_key in attrs:
            try:
                return str(float(attrs[thickness_key]) / 10)
            except (ValueError, TypeError):
                pass
        return ""

    # ====== ЭКСПОРТ ======

    def _export_to_csv(self, rows: list[list]) -> str:
        self._log("Generating WooCommerce CSV file...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        supplier_name = "all"
        if self.config.supplier_ids and len(self.config.supplier_ids) == 1:
            supplier_name = f"supplier_{self.config.supplier_ids[0]}"
        filename = f"woocommerce_{supplier_name}_{timestamp}.csv"
        output_path = self.config.output_dir / filename

        with open(str(output_path), "w", newline="", encoding=self.config.encoding) as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(WOOCOMMERCE_COLUMNS)
            writer.writerows(rows)

        file_size = os.path.getsize(output_path)
        self.stats.file_size = file_size
        self.stats.output_path = str(output_path)

        self._log(f"CSV saved: {output_path} ({file_size / 1024:.1f} KB)")
        return str(output_path)

    def run(self, db_session) -> dict[str, Any]:
        """Запускает экспорт."""
        self._cancelled = False
        self.stats = ExportStats()
        start_time = time.time()

        self._log(f"Export started (encoding={self.config.encoding})")

        # Определяем источник данных
        if self.config.use_archive:
            items = self._fetch_archive_items(db_session)
        else:
            items = []

        if not items:
            items = self._fetch_products(db_session)

        if not items:
            self._log("No products found matching filters")
            return {"success": False, "error": "No products found", "stats": self.stats}

        self._progress(10, self.stats.total_products, "Fetching complete")

        if self._cancelled:
            return {"success": False, "error": "cancelled", "stats": self.stats}

        rows = self._transform_to_csv_rows(items)
        if not rows:
            return {"success": False, "error": "No rows after transformation", "stats": self.stats}

        self._progress(60, self.stats.total_products, "Transformation complete")

        if self._cancelled:
            return {"success": False, "error": "cancelled", "stats": self.stats}

        output_path = self._export_to_csv(rows)

        self.stats.elapsed = time.time() - start_time
        self._progress(100, self.stats.total_products, "Export complete")

        del items
        del rows
        gc.collect()

        self._log(f"Export complete in {self.stats.elapsed:.1f}s")

        return {
            "success": True,
            "output_path": output_path,
            "stats": self.stats,
        }

    def validate_before_export(self, db_session) -> list[str]:
        """Проверяет данные перед экспортом."""
        from src.database.models import Product

        warnings = []

        query = db_session.query(Product)
        if self.config.supplier_ids:
            query = query.filter(Product.supplier_id.in_(self.config.supplier_ids))

        products = query.all()

        if not products:
            warnings.append("No products match the current filters")
            return warnings

        empty_titles = sum(1 for p in products if not p.title or not p.title.strip())
        if empty_titles:
            warnings.append(f"{empty_titles} products have empty titles")

        empty_prices = sum(1 for p in products if p.price is None)
        if empty_prices:
            warnings.append(f"{empty_prices} products have no price")

        empty_skus = sum(1 for p in products if not p.external_sku)
        if empty_skus:
            warnings.append(f"{empty_skus} products have no SKU (will be auto-generated)")

        # Проверяем parent-child consistency
        children_without_parent_sku = 0
        for p in products:
            if p.parent_product_id:
                has_parent_sku_attr = any(
                    a.name == "ParentSKU" and a.value
                    for a in p.attributes
                )
                if not has_parent_sku_attr:
                    children_without_parent_sku += 1

        if children_without_parent_sku:
            warnings.append(f"{children_without_parent_sku} children have no ParentSKU attribute")

        return warnings