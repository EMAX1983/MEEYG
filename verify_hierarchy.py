#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Скрипт верификации иерархии товаров после парсинга — ИСПРАВЛЕННАЯ ВЕРСИЯ"""

from sqlalchemy import alias
from src.database.session import get_session
from src.database.models import Product, Category
import json

def verify_hierarchy():
    print("Проверка иерархии товаров в БД (исправленная версия)\n")
    
    with get_session() as session:
        # === 1. ПРОВЕРКА РОДИТЕЛЕЙ ===
        print("РОДИТЕЛЬСКИЕ ТОВАРЫ (основные двери):")
        print("-" * 70)
        parents = session.query(Product).filter(
            Product.parent_product_id.is_(None)
        ).limit(3).all()
        
        for p in parents:
            attrs = {a.name: a.value for a in p.attributes}
            sizes_attr = attrs.get("Размер") or attrs.get("Доступные размеры") or attrs.get("sizes")
            
            print(f"ID: {p.id}")
            print(f"  Заголовок: {p.title[:60]}{'...' if len(p.title)>60 else ''}")
            print(f"  Цена: {p.price} {p.currency or ''}")
            print(f"  Размеры (у родителя): {sizes_attr or '[!] НЕ ЗАПОЛНЕНО'}")
            
            if sizes_attr and "|" in sizes_attr:
                size_list = sizes_attr.split("|")
                print(f"  [OK] Формат верный: {len(size_list)} вариантов")
            elif sizes_attr:
                print(f"  [!] Внимание: размер не содержит разделитель '|'")
            
            # === 2. ПРОВЕРКА ДЕТЕЙ ===
            children = session.query(Product).filter(
                Product.parent_product_id == p.id
            ).all()
            
            if children:
                print(f"  Детей: {len(children)}")
                for i, c in enumerate(children[:3], 1):
                    c_attrs = {a.name: a.value for a in c.attributes}
                    child_size = c_attrs.get("Размер") or c_attrs.get("size") or "—"
                    print(f"     {i}. {c.title[:40]} | Цена: {c.price} | Размер: {child_size}")
                    if child_size != "—" and "|" not in str(child_size):
                        print(f"        [OK] Размер у ребёнка корректный (одно значение)")
                    elif child_size != "—":
                        print(f"        [!] Размер у ребёнка содержит '|', должен быть один")
                if len(children) > 3:
                    print(f"     ... и ещё {len(children)-3}")
            else:
                print(f"  Детей: нет")
            print()
        
        # === 3. ПРОВЕРКА ПОГОНАЖА ===
        print("\nПОГОНАЖ (проверка compatible_collections):")
        print("-" * 70)
        
        molding_cats = ["Добор", "Наличник", "Короб", "Плинтус", "Притворная планка", "Прочее"]
        moldings = session.query(Product).join(Category).filter(
            Product.parent_product_id.isnot(None),
            Category.name.in_(molding_cats)
        ).limit(5).all()
        
        if not moldings:
            print("  [-] Не найдено товаров в категориях погонажа")
            all_children = session.query(Product).filter(
                Product.parent_product_id.isnot(None)
            ).limit(5).all()
            if all_children:
                print(f"  Найдено {len(all_children)} детей у родителей (возможно, погонаж в другой категории):")
                for c in all_children:
                    cat_name = c.category.name if c.category else "Без категории"
                    print(f"     - {c.title[:40]} [Категория: {cat_name}]")
                    if c.compatible_collections:
                        try:
                            cols = json.loads(c.compatible_collections)
                            print(f"       compatible_collections: {cols}")
                        except:
                            print(f"       compatible_collections (raw): {c.compatible_collections}")
        else:
            for m in moldings:
                collections = m.get_compatible_collections()
                print(f"ID: {m.id}")
                print(f"  Товар: {m.title[:50]}")
                print(f"  Категория: {m.category.name if m.category else '—'}")
                print(f"  compatible_collections: {collections}")
                
                if len(collections) != len(set(collections)):
                    print(f"  [X] ОБНАРУЖЕНЫ ДУБЛИКАТЫ в collections!")
                elif collections:
                    print(f"  [OK] Коллекции без дублей")
                else:
                    print(f"  [-] Collections пуст")
                print()
        
        # === 4. СТАТИСТИКА ===
        print("\nОБЩАЯ СТАТИСТИКА:")
        print("-" * 70)
        total_parents = session.query(Product).filter(
            Product.parent_product_id.is_(None)
        ).count()
        total_children = session.query(Product).filter(
            Product.parent_product_id.isnot(None)
        ).count()
        
        print(f"  Родительских товаров: {total_parents}")
        print(f"  Вариаций (детей): {total_children}")
        
        ParentAlias = alias(Product)
        orphan_children = session.query(Product).filter(
            Product.parent_product_id.isnot(None)
        ).outerjoin(
            ParentAlias, Product.parent_product_id == ParentAlias.c.id
        ).filter(
            ParentAlias.c.id.is_(None)
        ).count()
        
        if orphan_children > 0:
            print(f"  [X] Найдено {orphan_children} детей без родителя!")
        else:
            print(f"  [OK] Orphan-записей не найдено")

if __name__ == "__main__":
    verify_hierarchy()
