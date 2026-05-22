"""
Экспорт архива: CSV с разделителем | (для WP All Import) или XLSX (корректно в Excel).
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from openpyxl import Workbook

from src.database.models import Category, Product, ProductAttribute, Supplier
from src.database.session import get_session

EXPORT_DELIMITER = "|"
_EXCEL_CELL_MAX = 32767

# Шапка как в «пример импорта WP ALL Import.txt» (38 полей).
# Уникальные имена колонок для Excel (чтобы избежать авто-добавления .1, .2)
_WP_HEADER: list[str] = [
    "Name",
    "Vendor",
    "SKU",
    "Parental",
    "Наличие",
    "stock_status",
    "Images",
    "Manufacturer",
    "Attribute name 1",
    "Attribute values 1",
    "price",
]
for i in range(2, 12):
    _WP_HEADER.extend([f"Attribute name {i}", f"Attribute values {i}"])
_WP_HEADER.extend(
    [
        "Categories",
        "Tags",
        "Brand",
        "Description",
        "Availability",
        "Attribute name 12",
        "Attribute values 12",
    ]
)


def _clean_product_title(raw_title: str) -> str:
    if not raw_title:
        return ""
    title = raw_title.strip()
    for prefix in (
        "Входная дверь ",
        "Входная дверь",
        "Дверь входная ",
        "Дверь ",
    ):
        if title.startswith(prefix):
            title = title[len(prefix) :].strip()
            break
    title = re.sub(r"\s*\d{3,4}[xXх]\d{3,4}\s*$", "", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def _clean_sku(raw_sku: str, supplier_name: str = "") -> str:
    if not raw_sku or raw_sku == "-":
        return raw_sku or "-"
    sku = raw_sku.strip()
    for prefix in ("Входная дверь ", "Дверь входная ", "Дверь "):
        if sku.startswith(prefix):
            sku = sku[len(prefix) :].strip()
            break
    sku = re.sub(r"\s+\d{2,4}[xXх]\d{3,4}", "", sku)
    sku = re.sub(r"\s+", " ", sku).strip()
    if supplier_name and supplier_name not in sku:
        sku = f"{supplier_name} {sku}"
    return sku


def _category_path_gt(session, category_id: int | None) -> str:
    if not category_id:
        return ""
    parts: list[str] = []
    cat = session.get(Category, category_id)
    while cat is not None:
        parts.append(cat.name)
        cat = session.get(Category, cat.parent_id) if cat.parent_id else None
    if not parts:
        return ""
    return ">".join(reversed(parts))


def _format_price(price: float | None) -> str:
    if price is None:
        return ""
    if price == int(price):
        return str(int(price))
    s = f"{price:.4f}".rstrip("0").rstrip(".")
    return s


def _field(s: str | None) -> str:
    if s is None:
        return ""
    return str(s).replace("\r\n", "\n").replace("\r", "\n")


def _clip_cell(s: str) -> str:
    if len(s) <= _EXCEL_CELL_MAX:
        return s
    return s[: _EXCEL_CELL_MAX - 1] + "…"


def _collect_rows(ids: list[int]) -> list[list[str]]:
    rows: list[list[str]] = []
    
    # Сначала собираем ВСЕ уникальные имена атрибутов из всех товаров
    all_attr_names: set[str] = set()
    products_data: list[dict] = []
    
    with get_session() as session:
        # Первый проход: собираем все атрибуты
        for pid in ids:
            p = session.get(Product, pid)
            if not p:
                continue
            
            attrs = {
                a.name: a.value
                for a in session.query(ProductAttribute).filter_by(product_id=p.id).all()
            }
            
            # Исключаем зарезервированные атрибуты из общего списка
            reserved = {"Размер", "ParentSKU", "Производитель"}
            for key in attrs.keys():
                if key not in reserved and attrs[key] and attrs[key].strip():
                    all_attr_names.add(key)
        
        # Сортируем атрибуты для стабильного порядка
        sorted_attr_names = sorted(all_attr_names)
        
        # Ограничиваем количество атрибутов (максимум 10 пар в middle)
        if len(sorted_attr_names) > 10:
            sorted_attr_names = sorted_attr_names[:10]
        
        # Второй проход: формируем строки с единой структурой
        for pid in ids:
            p = session.get(Product, pid)
            if not p:
                continue
            sup = session.get(Supplier, p.supplier_id) if p.supplier_id else None
            supplier_name = sup.name if sup else "Тандор"

            attrs = {
                a.name: a.value
                for a in session.query(ProductAttribute).filter_by(product_id=p.id).all()
            }
            parental_raw = attrs.get("ParentSKU", "") or "-"
            parental = (
                _clean_sku(parental_raw, supplier_name) if parental_raw != "-" else ""
            )

            name = _field(_clean_product_title(p.title))
            vendor = _field(supplier_name)
            sku = _field(_clean_sku(p.external_sku or "-", supplier_name))
            parental_col = parental if parental != "-" else ""

            if p.is_available:
                nalichie = "в наличии"
                stock_status = "instock"
                availability = "в наличии"
            else:
                nalichie = "нет в наличии"
                stock_status = "outofstock"
                availability = "нет в наличии"

            urls = p.get_image_urls()
            images = _field(urls[0] if urls else "")

            collections = p.get_compatible_collections()
            manufacturer = _field(collections[0] if collections else supplier_name)

            size_val = _field(attrs.get("Размер", ""))

            # Заполняем атрибуты в ЕДИНОМ порядке для всех товаров
            middle_pairs: list[tuple[str, str]] = []
            for attr_name in sorted_attr_names:
                val = attrs.get(attr_name, "")
                if val and val.strip():
                    middle_pairs.append((attr_name, _field(val)))
                else:
                    middle_pairs.append(("", ""))  # Пустое значение, но позиция сохранена
            
            # Добиваем до 10 пар пустыми, если атрибутов меньше
            while len(middle_pairs) < 10:
                middle_pairs.append(("", ""))

            producer_val = attrs.get("Производитель", supplier_name)
            last_pair = ("Производитель", _field(producer_val))

            cats = _field(_category_path_gt(session, p.category_id))
            tags = ""
            brand = _field(supplier_name)
            desc = _field(p.description or "")

            row: list[str] = [
                name,
                vendor,
                sku,
                parental_col,
                nalichie,
                stock_status,
                images,
                manufacturer,
                "Размер",
                size_val,
                _format_price(p.price),
            ]
            for an, av in middle_pairs:
                row.append(_field(an))
                row.append(_field(av))
            row.extend(
                [cats, tags, brand, desc, availability, last_pair[0], last_pair[1]]
            )
            rows.append(row)
    return rows


def _write_csv_pipe(path: Path, rows: list[list[str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(
            f,
            delimiter=EXPORT_DELIMITER,
            quoting=csv.QUOTE_MINIMAL,
        )
        w.writerow(_WP_HEADER)
        for row in rows:
            w.writerow(row)


def _write_xlsx(path: Path, rows: list[list[str]]) -> None:
    wb = Workbook()
    ws = wb.active
    assert ws is not None
    ws.title = "Archive"
    ws.append(_WP_HEADER)
    for row in rows:
        ws.append([_clip_cell(c) for c in row])
    ws.freeze_panes = "A2"
    wb.save(path)


@dataclass
class ArchiveExportConfig:
    output_path: Path
    product_ids: list[int]


class ArchiveExporter:
    @staticmethod
    def export(config: ArchiveExportConfig) -> tuple[int, str]:
        """
        Returns (row_count, format_label): format_label is 'xlsx' or 'csv_pipe'.
        """
        path = Path(config.output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        ids = list(config.product_ids)
        if not ids:
            return 0, "csv_pipe"

        rows = _collect_rows(ids)
        suffix = path.suffix.lower()
        if suffix == ".xlsx":
            _write_xlsx(path, rows)
            return len(rows), "xlsx"
        _write_csv_pipe(path, rows)
        return len(rows), "csv_pipe"
