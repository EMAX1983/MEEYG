"""
Скрипт миграции: очистка названий товаров в БД.

Делает следующее:
1. Очищает title у всех продуктов (оставляет только наименование до первого /)
2. Извлекает атрибуты из title (Размер, Тип, Направление) и сохраняет в ProductAttribute
3. Для направлений "Левое открывание" / "Правое открывание" сохраняет в атрибут "Направление"
"""

import re
import sys

from src.database.models import Product, ProductAttribute, Base, engine
from src.database.session import get_session


def clean_title_and_extract_attrs(title: str) -> tuple[str, dict[str, str]]:
    """Разбирает title формата 'Название / 60 / ДГ / Левое открывание' на чистое название и атрибуты."""
    if not title or "/" not in title:
        return (title.strip(), {})
    
    parts = [p.strip() for p in title.split("/") if p.strip()]
    clean = parts[0].strip()
    attrs = {}
    
    direction_keywords = ["левое", "правое", "левое открывание", "правое открывание"]
    
    for part in parts[1:]:
        part_lower = part.lower()
        
        # Проверяем является ли часть направлением
        is_direction = False
        for kw in direction_keywords:
            if kw in part_lower:
                attrs["Направление"] = part
                is_direction = True
                break
        
        if is_direction:
            continue
        
        # Проверяем является ли часть типом (ДГ, ДЧ, ДО и т.д.)
        if re.match(r"^Д[А-Я]$", part.upper()):
            attrs["Тип"] = part
            continue
        
        # Проверяем является ли часть размером (число)
        if re.match(r"^\d+$", part):
            attrs["Размер"] = part
            continue
        
        # Неизвестная часть — пропускаем
        print(f"  ⚠ Пропущен неизвестный сегмент: '{part}'")
    
    return (clean, attrs)


def migrate():
    session = next(get_session())
    try:
        # Обрабатываем только детей (parent_product_id IS NOT NULL)
        children = session.query(Product).filter(
            Product.parent_product_id.isnot(None)
        ).all()
        
        total = len(children)
        updated = 0
        
        print(f"Найдено {total} продуктов-детей для обработки...")
        
        for i, product in enumerate(children, 1):
            clean, attrs = clean_title_and_extract_attrs(product.title)
            
            if clean != product.title or attrs:
                # Обновляем title
                if clean != product.title:
                    product.title = clean
                
                # Обновляем/создаём атрибуты
                for attr_name, attr_value in attrs.items():
                    existing = session.query(ProductAttribute).filter_by(
                        product_id=product.id,
                        name=attr_name
                    ).first()
                    
                    if existing:
                        if existing.value != attr_value:
                            existing.value = attr_value
                    else:
                        session.add(ProductAttribute(
                            product_id=product.id,
                            name=attr_name,
                            value=attr_value
                        ))
                
                updated += 1
            
            if i % 100 == 0:
                print(f"  Обработано {i}/{total}...")
        
        session.commit()
        print(f"\n✅ Миграция завершена! Обновлено {updated} из {total} продуктов.")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Ошибка миграции: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    confirm = input("Это изменит данные в БД. Продолжить? (y/n): ")
    if confirm.lower() == "y":
        migrate()
    else:
        print("Отмена.")