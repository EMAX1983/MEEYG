#!/usr/bin/env python
# -*- coding: utf-8 -*-
from src.database.session import get_session
from src.database.models import Product, Category

def check_hierarchy():
    with get_session() as session:
        # Основные товары
        mains = session.query(Product).filter(
            Product.parent_product_id.is_(None)
        ).limit(3).all()
        
        print(f"📋 Найдено основных товаров: {len(mains)}\n")
        
        for mp in mains:
            print(f"🚪 {mp.title[:60]}{'...' if len(mp.title)>60 else ''}")
            print(f"   ID: {mp.id} | Цена: {mp.price} {mp.currency}")
            
            # Сопутствующие
            moldings = session.query(Product).filter(
                Product.parent_product_id == mp.id
            ).all()
            
            if moldings:
                print(f"   📦 Сопутствующих: {len(moldings)}")
                for m in moldings[:3]:
                    cat_name = m.category.name if m.category else "Без категории"
                    print(f"      • {m.title[:40]} [{cat_name}]")
            else:
                print("   📦 Сопутствующих: нет")
            print()

if __name__ == "__main__":
    check_hierarchy()