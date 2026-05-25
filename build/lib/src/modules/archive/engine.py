import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

from src.core.logger import logger

logger_archive = logging.getLogger("meeyg.archive")


@dataclass
class SnapshotStats:
    total_products: int = 0
    total_categories: int = 0
    total_price_sum: float = 0.0
    available_count: int = 0
    unavailable_count: int = 0
    categories_with_products: int = 0
    elapsed: float = 0.0


class ArchiveEngine:
    def __init__(
        self,
        supplier_id: int,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        self.supplier_id = supplier_id
        self.log_callback = log_callback or (lambda m: logger_archive.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def _log(self, msg: str) -> None:
        self.log_callback(msg)

    def _progress(self, pct: int, total: int, msg: str) -> None:
        self.progress_callback(pct, total, msg)

    def create_snapshot(
        self,
        db_session,
        name: str,
        description: str = "",
        snapshot_type: str = "full",
    ) -> dict[str, Any]:
        from src.database.models import ArchiveItem, ArchiveSnapshot, Category, Product

        self._cancelled = False
        start_time = time.time()

        self._log(f"Creating archive snapshot '{name}' for supplier {self.supplier_id}")

        products = db_session.query(Product).filter(
            Product.supplier_id == self.supplier_id
        ).all()

        if not products:
            self._log("No products found for this supplier")
            return {"success": False, "error": "No products to archive"}

        total_products = len(products)
        self._log(f"Found {total_products} products to archive")

        category_map = {}
        categories = db_session.query(Category).filter(
            Category.supplier_id == self.supplier_id
        ).all()
        for cat in categories:
            category_map[cat.id] = cat.name

        categories_with_products = set()
        total_price_sum = 0.0
        available_count = 0
        unavailable_count = 0

        snapshot = ArchiveSnapshot(
            supplier_id=self.supplier_id,
            name=name,
            description=description,
            snapshot_type=snapshot_type,
        )
        db_session.add(snapshot)
        db_session.flush()

        batch_size = 500
        items_to_insert = []

        for i, product in enumerate(products):
            if self._cancelled:
                db_session.rollback()
                self._log("Snapshot creation cancelled")
                return {"success": False, "error": "cancelled"}

            if product.category_id and product.category_id in category_map:
                cat_name = category_map[product.category_id]
                categories_with_products.add(product.category_id)
            else:
                cat_name = None

            if product.price:
                total_price_sum += product.price

            if product.is_available:
                available_count += 1
            else:
                unavailable_count += 1

            attrs = {}
            for attr in product.attributes:
                attrs[attr.name] = attr.value

            items_to_insert.append({
                "snapshot_id": snapshot.id,
                "product_id": product.id,
                "external_sku": product.external_sku,
                "title": product.title,
                "price": product.price,
                "currency": product.currency,
                "is_available": product.is_available,
                "category_name": cat_name,
                "image_urls": product.image_urls,
                "attributes_json": json.dumps(attrs, ensure_ascii=False) if attrs else None,
            })

            if len(items_to_insert) >= batch_size:
                db_session.execute(ArchiveItem.__table__.insert(), items_to_insert)
                db_session.flush()
                items_to_insert.clear()

            pct = int(((i + 1) / total_products) * 100)
            self._progress(pct, total_products, f"Archiving product {i + 1}/{total_products}")

        if items_to_insert:
            db_session.execute(ArchiveItem.__table__.insert(), items_to_insert)
            db_session.flush()

        elapsed = time.time() - start_time

        snapshot.total_products = total_products
        snapshot.total_categories = len(categories_with_products)
        snapshot.total_price_sum = round(total_price_sum, 2)

        self._log(f"Snapshot created: {total_products} products, {len(categories_with_products)} categories")
        self._log(f"Elapsed: {elapsed:.1f}s")

        return {
            "success": True,
            "snapshot_id": snapshot.id,
            "stats": SnapshotStats(
                total_products=total_products,
                total_categories=len(categories_with_products),
                total_price_sum=round(total_price_sum, 2),
                available_count=available_count,
                unavailable_count=unavailable_count,
                categories_with_products=len(categories_with_products),
                elapsed=elapsed,
            ),
        }

    def list_snapshots(self, db_session) -> list:
        from src.database.models import ArchiveSnapshot

        return db_session.query(ArchiveSnapshot).filter(
            ArchiveSnapshot.supplier_id == self.supplier_id
        ).order_by(ArchiveSnapshot.created_at.desc()).all()

    def get_snapshot_items(self, db_session, snapshot_id: int) -> list:
        from src.database.models import ArchiveItem

        return db_session.query(ArchiveItem).filter(
            ArchiveItem.snapshot_id == snapshot_id
        ).order_by(ArchiveItem.title).all()

    def delete_snapshot(self, db_session, snapshot_id: int) -> bool:
        from src.database.models import ArchiveItem, ArchiveSnapshot

        items_deleted = db_session.query(ArchiveItem).filter(
            ArchiveItem.snapshot_id == snapshot_id
        ).delete(synchronize_session=False)

        snapshot = db_session.query(ArchiveSnapshot).filter(
            ArchiveSnapshot.id == snapshot_id,
            ArchiveSnapshot.supplier_id == self.supplier_id,
        ).first()

        if snapshot:
            db_session.delete(snapshot)
            self._log(f"Deleted snapshot {snapshot_id} ({items_deleted} items)")
            return True

        return False

    def compare_snapshots(self, db_session, snapshot_id_a: int, snapshot_id_b: int) -> dict[str, Any]:
        from src.database.models import ArchiveItem

        items_a = db_session.query(ArchiveItem).filter(
            ArchiveItem.snapshot_id == snapshot_id_a
        ).all()

        items_b = db_session.query(ArchiveItem).filter(
            ArchiveItem.snapshot_id == snapshot_id_b
        ).all()

        skus_a = {item.external_sku for item in items_a if item.external_sku}
        skus_b = {item.external_sku for item in items_b if item.external_sku}

        new_products = skus_b - skus_a
        removed_products = skus_a - skus_b
        common_products = skus_a & skus_b

        price_changes = []
        if common_products:
            prices_a = {item.external_sku: item.price for item in items_a if item.external_sku in common_products}
            prices_b = {item.external_sku: item.price for item in items_b if item.external_sku in common_products}

            for sku in common_products:
                pa = prices_a.get(sku)
                pb = prices_b.get(sku)
                if pa is not None and pb is not None and pa != pb:
                    price_changes.append({
                        "sku": sku,
                        "old_price": pa,
                        "new_price": pb,
                        "diff": round(pb - pa, 2),
                        "pct_change": round(((pb - pa) / pa) * 100, 1) if pa != 0 else 0,
                    })

        availability_changes = []
        if common_products:
            avail_a = {item.external_sku: item.is_available for item in items_a if item.external_sku in common_products}
            avail_b = {item.external_sku: item.is_available for item in items_b if item.external_sku in common_products}

            for sku in common_products:
                aa = avail_a.get(sku)
                ab = avail_b.get(sku)
                if aa is not None and ab is not None and aa != ab:
                    availability_changes.append({
                        "sku": sku,
                        "was_available": aa,
                        "is_available": ab,
                    })

        return {
            "snapshot_a_count": len(items_a),
            "snapshot_b_count": len(items_b),
            "new_products": len(new_products),
            "removed_products": len(removed_products),
            "price_changes": len(price_changes),
            "availability_changes": len(availability_changes),
            "price_change_details": price_changes[:50],
            "availability_change_details": availability_changes[:50],
        }
