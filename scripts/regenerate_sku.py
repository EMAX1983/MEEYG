"""
Скрипт для пересчёта SKU всех существующих товаров в БД.
Формат: "Производитель Коллекция XXXXXX"
Пример: "тандор Элегия-2 000001"
"""

import re
import sys
from pathlib import Path

# Добавляем корень проекта
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.session import get_session
from src.database.models import Product, Supplier


def generate_sku(supplier_name: str, raw_title: str, counter: int) -> str:
    """Та же логика что и в TandoorPlaywrightParser._generate_sku"""
    clean = raw_title.strip()
    
    # 1. Удаляем префиксы типов дверей
    for prefix in [
        "Входная дверь ", "Дверь входная ", "Дверь ",
        "Межкомнатная дверь ", "Дверь межкомнатная ",
    ]:
        clean = clean.replace(prefix, "", 1)
    
    # 2. Удаляем типы конструкций с скобками: "Глухая (ДГ)", "С остеклением (С)"
    clean = re.sub(r'\w+?\s+\([^)]*\)', '', clean)
    
    # 3. Удаляем размер в конце
    clean = re.sub(r'\s+\d{2,4}[xXх*]\d{3,4}\s*$', '', clean)
    
    # 4. Удаляем направления открывания
    for direction in ["Левое открывание", "Правое открывание", "Левая", "Правая"]:
        clean = clean.replace(direction, "")
    
    # 5. Нормализуем пробелы
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    # 6. Оставляем только название коллекции (первое слово)
    words = clean.split()
    collection_name = next((w for w in words if w and not w.isdigit()), words[0] if words else "")
    
    return f"{supplier_name} {collection_name} {counter:06d}"


def main():
    with get_session() as session:
        # Debug: проверяем общее кол-во
        all_products = session.query(Product).all()
        all_suppliers = session.query(Supplier).all()
        print(f"DEBUG: Всего продуктов в БД: {len(all_products)}")
        print(f"DEBUG: Всего поставщиков: {len(all_suppliers)}")
        for s in all_suppliers:
            print(f"  Поставщик: id={s.id}, name='{s.name}'")
        
        if not all_suppliers:
            print("Нет поставщиков в БД. Нечего обновлять.")
            return
        
        # Получаем всех поставщиков
        suppliers = all_suppliers
        
        total_updated = 0
        total_count = 0
        
        for supplier in suppliers:
            supplier_name = supplier.name.lower() if supplier.name else "тандор"
            
            # Получаем все родительские продукты этого поставщика
            parents = session.query(Product).filter(
                Product.supplier_id == supplier.id,
                Product.parent_product_id.is_(None)
            ).all()
            
            print(f"\nПоставщик '{supplier.name}' (id={supplier.id}):")
            print(f"  Родительских продуктов: {len(parents)}")
            
            counter = 1
            updated_parents = 0
            
            for parent in parents:
                # Регенерируем SKU родителя
                new_sku = generate_sku(supplier_name, parent.title, counter)
                old_sku = parent.external_sku or ""
                
                print(f"  Родитель #{parent.id}: title='{parent.title[:60]}...'")
                print(f"    Old SKU: {old_sku}")
                print(f"    New SKU: {new_sku}")
                
                if new_sku != old_sku:
                    parent.external_sku = new_sku
                    updated_parents += 1
                
                total_count += 1
                counter += 1
                
                # Регенерируем SKU детей
                children = session.query(Product).filter(
                    Product.parent_product_id == parent.id
                ).all()
                
                for child in children:
                    child_counter = counter
                    child_new_sku = generate_sku(supplier_name, child.title, child_counter)
                    child_old_sku = child.external_sku or ""
                    
                    if child_old_sku != child_new_sku:
                        child.external_sku = child_new_sku
                        updated_parents += 1
                    
                    total_count += 1
                    counter += 1
            
            total_items = len(parents) + sum(len(session.query(Product).filter(Product.parent_product_id==p.id).all()) for p in parents)
            print(f"  Итого: {updated_parents} SKU изменено из {total_items}")
            total_updated += updated_parents
        
        session.commit()
        print(f"\nИТОГО: {total_updated} SKU обновлено из {total_count} товаров")


if __name__ == "__main__":
    print("Пересчёт SKU для всех товаров...")
    print("Формат: 'Производитель Коллекция XXXXXX'\n")
    main()