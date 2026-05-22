"""
Полная миграция: parent_product_id + category_name в продуктах.
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from src.database.models import Product, Category, ProductAttribute, Base
from src.database.engine import create_engine
import json

def get_opening_direction(title):
    """Извлекает направление открывания из названия."""
    if not title:
        return "Стандарт"
    title_lower = title.lower()
    if 'левое открывание' in title_lower or 'левое' in title_lower:
        return "Левое"
    if 'правое открывание' in title_lower or 'правое' in title_lower:
        return "Правое"
    if 'двустороннее' in title_lower or 'unif' in title_lower or 'универс' in title_lower:
        return "Двустороннее"
    return "Стандарт"

engine = create_engine()

with engine.begin() as conn:
    # 1. Добавляем колонки если нет
    try:
        conn.execute("ALTER TABLE products ADD COLUMN opening_direction TEXT DEFAULT 'Стандарт'")
        print("  Колонка opening_direction добавлена")
    except Exception:
        print("  Колонка opening_direction уже существует")
    
    try:
        conn.execute("ALTER TABLE products ADD COLUMN category_name TEXT")
        print("  Колонка category_name добавлена")
    except Exception:
        print("  Колонка category_name уже существует")
    
    # 2. Заполняем opening_direction из названия
    print("\nШаг 2: Заполнение opening_direction...")
    import sqlalchemy as sa
    products = conn.execute(sa.text("SELECT id, title FROM products WHERE title IS NOT NULL AND (opening_direction IS NULL OR opening_direction = 'Стандарт')")).fetchall()
    updated_dir = 0
    for pid, title in products:
        direction = get_opening_direction(title)
        if direction != "Стандарт":
            conn.execute(sa.text(f"UPDATE products SET opening_direction = '{direction.replace("'", "''")}' WHERE id = {pid}") )
            updated_dir += 1
    conn.execute(sa.text("UPDATE products SET opening_direction = 'Стандарт' WHERE opening_direction IS NULL"))
    print(f"  Обновлено: {updated_dir} товаров")
    
    # 3. Заполняем category_name
    print("\nШаг 3: Заполнение category_name...")
    products_no_cat = conn.execute(sa.text("SELECT id, category_id FROM products WHERE category_name IS NULL AND category_id IS NOT NULL")).fetchall()
    updated_cat = 0
    for pid, cat_id in products_no_cat:
        if cat_id:
            cat_row = conn.execute(sa.text(f"SELECT name FROM categories WHERE id = {cat_id}")).fetchone()
            if cat_row:
                cat_name = cat_row[0].replace("'", "''")
                conn.execute(sa.text(f"UPDATE products SET category_name = '{cat_name}' WHERE id = {pid}"))
                updated_cat += 1
    conn.execute(sa.text("UPDATE products SET category_name = 'Без категории' WHERE category_name IS NULL"))
    print(f"  Обновлено: {updated_cat} товаров")

print("\nГотово!")