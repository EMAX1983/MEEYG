"""
WP All Import Exporter Module
Унифицированный экспорт данных для импорта в WordPress (WooCommerce).
Обрабатывает нормализацию атрибутов, изображений и генерацию SKU.
"""

import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import OrderedDict

# --- КОНФИГУРАЦИЯ НОРМАЛИЗАЦИИ ---

# Единая структура колонок (порядок важен для WP All Import)
# Основные поля WooCommerce + Атрибуты
WP_COLUMNS = [
    "parent_sku",          # SKU родителя (для вариаций)
    "name",                # Название товара
    "type",                # simple / variable
    "sku",                 # Уникальный SKU
    "regular_price",       # Цена
    "sale_price",          # Цена со скидкой
    "description",         # Полное описание
    "short_description",   # Краткое описание
    "categories",          # Категории (через >)
    "images",              # Главное фото (Featured Image)
    "gallery_images",      # Галерея (остальные фото через запятую)
    
    # Стандартизированные атрибуты (глобальные для всех дверей)
    "attr_collection",     # Коллекция
    "attr_color",          # Цвет (нормализованный)
    "attr_size",           # Размер (Ширина x Высота)
    "attr_material",       # Материал
    "attr_glass_type",     # Тип стекла
    "attr_thickness",      # Толщина полотна (мм)
    "attr_direction",      # Направление открытия (Левое/Правое)
    "attr_finish",         # Отделка
    "attr_warranty",       # Гарантия
    "attr_weight",         # Вес (кг)
    "attr_brand",          # Производитель
    
    # Дополнительные технические атрибуты (заполняются если есть)
    "attr_soundproof",     # Звукоизоляция (дБ)
    "attr_heat_insulation",# Теплоизоляция
    "attr_lock_type",      # Тип замка
    "attr_handle_style",   # Стиль ручки
    "attr_purpose",        # Назначение (Входная/Межкомнатная)
]

# Словарь синонимов для нормализации названий атрибутов из разных источников
ATTRIBUTE_NAME_MAPPING = {
    # Цвет
    "color": "attr_color",
    "colour": "attr_color",
    "цвет": "attr_color",
    "цвет изделия": "attr_color",
    "цвет покрытия": "attr_color",
    "окрас": "attr_color",
    
    # Размер
    "size": "attr_size",
    "размер": "attr_size",
    "габариты": "attr_size",
    "ширина высота": "attr_size",
    "размеры полотна": "attr_size",
    
    # Материал
    "material": "attr_material",
    "материал": "attr_material",
    "материал полотна": "attr_material",
    "основа": "attr_material",
    
    # Стекло
    "glass": "attr_glass_type",
    "glass type": "attr_glass_type",
    "тип стекла": "attr_glass_type",
    "стекло": "attr_glass_type",
    "вид стекла": "attr_glass_type",
    
    # Толщина
    "thickness": "attr_thickness",
    "толщина": "attr_thickness",
    "толщина полотна": "attr_thickness",
    "толщина двери": "attr_thickness",
    
    # Коллекция
    "collection": "attr_collection",
    "коллекция": "attr_collection",
    "серия": "attr_collection",
    "линейка": "attr_collection",
    
    # Направление
    "direction": "attr_direction",
    "направление": "attr_direction",
    "открывание": "attr_direction",
    "сторона открытия": "attr_direction",
    
    # Отделка
    "finish": "attr_finish",
    "отделка": "attr_finish",
    "покрытие": "attr_finish",
    "текстура": "attr_finish",
    
    # Производитель
    "brand": "attr_brand",
    "manufacturer": "attr_brand",
    "producer": "attr_brand",
    "производитель": "attr_brand",
    "бренд": "attr_brand",
    "завод": "attr_brand",
}

# Словарь синонимов для значений (приведение к единому виду)
VALUE_NORMALIZATION = {
    # Цвета (примеры, можно расширять)
    "белый": "Белый",
    "белая": "Белый",
    "белое": "Белый",
    "white": "Белый",
    "черный": "Черный",
    "чёрный": "Черный",
    "черная": "Черный",
    "black": "Черный",
    "венге": "Венге",
    "дуб": "Дуб",
    "золото": "Золото",
    "серебро": "Серебро",
    "серый": "Серый",
    "серая": "Серый",
    "бежевый": "Бежевый",
    "беж": "Бежевый",
    
    # Направление
    "левое": "Левое",
    "левая": "Левое",
    "left": "Левое",
    "правое": "Правое",
    "правая": "Правое",
    "right": "Правое",
    
    # Тип товара
    "входная": "Входная дверь",
    "входные": "Входная дверь",
    "межкомнатная": "Межкомнатная дверь",
    "межкомнатные": "Межкомнатная дверь",
    "interior": "Межкомнатная дверь",
    "exterior": "Входная дверь",
}


class WpAllImportExporter:
    """
    Экспортер данных в формат CSV, совместимый с WP All Import.
    """

    def __init__(self, output_dir: str = "data/exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Кэш нормализованных имен атрибутов для скорости
        self._name_cache = {}

    def _normalize_attribute_name(self, raw_name: str) -> Optional[str]:
        """
        Приводит сырое имя атрибута к стандартному ключу WP_COLUMNS.
        """
        clean_name = raw_name.strip().lower()
        
        if clean_name in self._name_cache:
            return self._name_cache[clean_name]
            
        # Прямое совпадение
        if clean_name in ATTRIBUTE_NAME_MAPPING:
            key = ATTRIBUTE_NAME_MAPPING[clean_name]
            self._name_cache[clean_name] = key
            return key
            
        # Частичное совпадение (если точного нет)
        for map_key, standard_key in ATTRIBUTE_NAME_MAPPING.items():
            if map_key in clean_name or clean_name in map_key:
                self._name_cache[clean_name] = standard_key
                return standard_key
                
        return None

    def _normalize_value(self, key: str, raw_value: Any) -> str:
        """
        Нормализует значение атрибута.
        Для цвета и направления применяет словарь синонимов.
        Для остальных - очистка и форматирование.
        """
        if raw_value is None or str(raw_value).strip() == "":
            return ""
            
        val_str = str(raw_value).strip()
        
        # Специфическая нормализация для цвета
        if key == "attr_color":
            lower_val = val_str.lower()
            # Ищем частичное совпадение в словаре
            for norm_key, norm_val in VALUE_NORMALIZATION.items():
                if norm_key in lower_val:
                    return norm_val
            # Если не нашли, просто капитализируем первое слово
            return val_str.capitalize()
            
        # Нормализация направления
        if key == "attr_direction":
            lower_val = val_str.lower()
            for norm_key, norm_val in VALUE_NORMALIZATION.items():
                if norm_key in lower_val:
                    return norm_val
            return val_str.capitalize()
            
        # Для размеров пытаемся привести к формату "Ширина x Высота"
        if key == "attr_size":
            # Удаляем лишние пробелы вокруг 'x', '*', 'на'
            import re
            val_str = re.sub(r'\s*[xх*]\s*', ' x ', val_str)
            val_str = re.sub(r'\s*на\s*', ' x ', val_str, flags=re.IGNORECASE)
            return val_str
            
        # Для остальных - просто возврат очищенного значения
        return val_str

    def _generate_sku(self, product_data: Dict[str, Any], is_variation: bool = False) -> str:
        """
        Генерирует уникальный SKU по правилам:
        Родитель: BRAND_COLLECTION_RANDOMID
        Вариация: BRAND_COLLECTION_SIZE_COLOR
        """
        brand = self._normalize_value("attr_brand", product_data.get("brand", "Unknown"))
        collection = self._normalize_value("attr_collection", product_data.get("collection", "NoCollection"))
        
        # Очистка для SKU (только латиница и цифры)
        def clean_for_sku(text):
            import re
            # Транслитерация (упрощенная) или удаление кириллицы
            text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
            return "_".join(text.upper().split())

        b_code = clean_for_sku(brand)[:10]
        c_code = clean_for_sku(collection)[:15]
        
        if not is_variation:
            # Для родителя добавляем короткий хэш или ID, если есть
            unique_id = product_data.get("id", "")
            if unique_id:
                return f"{b_code}_{c_code}_{str(unique_id)[-6:]}"
            return f"{b_code}_{c_CODE}_PARENT"
        
        # Для вариации добавляем размер и цвет
        size = self._normalize_value("attr_size", product_data.get("size", ""))
        color = self._normalize_value("attr_color", product_data.get("color", ""))
        
        s_code = clean_for_sku(size.replace(" x ", "").replace(" ", ""))[:8]
        col_code = clean_for_sku(color)[:8]
        
        return f"{b_code}_{c_code}_{s_code}_{col_code}"

    def _process_images(self, images: List[str]) -> tuple[str, str]:
        """
        Разделяет список изображений на главное и галерею.
        Возвращает (featured_image, gallery_images_csv).
        """
        if not images:
            return "", ""
            
        # Фильтрация пустых и дублей с сохранением порядка
        seen = set()
        unique_images = []
        for img in images:
            if img and img not in seen:
                seen.add(img)
                unique_images.append(img)
                
        if not unique_images:
            return "", ""
            
        featured = unique_images[0]
        gallery = ",".join(unique_images[1:]) if len(unique_images) > 1 else ""
        
        return featured, gallery

    def _map_product_to_row(self, product: Dict[str, Any], parent_sku: Optional[str] = None) -> OrderedDict:
        """
        Преобразует объект продукта в строку словаря с фиксированными ключами WP_COLUMNS.
        """
        row = OrderedDict.fromkeys(WP_COLUMNS, "")
        
        # Базовые поля
        row["name"] = product.get("title", "")
        row["description"] = product.get("description", "")
        row["short_description"] = product.get("short_description", "")
        row["categories"] = product.get("category_path", "")
        
        # Тип товара
        is_variation = parent_sku is not None
        row["type"] = "variation" if is_variation else ("variable" if product.get("has_variations") else "simple")
        row["parent_sku"] = parent_sku if parent_sku else ""
        
        # Цены
        row["regular_price"] = product.get("price", "")
        row["sale_price"] = product.get("sale_price", "")
        
        # SKU
        if is_variation:
            row["sku"] = self._generate_sku(product, is_variation=True)
        else:
            row["sku"] = self._generate_sku(product, is_variation=False)
            
        # Изображения
        images = product.get("images", [])
        featured, gallery = self._process_images(images)
        row["images"] = featured
        row["gallery_images"] = gallery
        
        # Атрибуты (проходим по всем сырым атрибутам продукта и раскидываем по колонкам)
        raw_attributes = product.get("attributes", {}) # dict: { "сырое имя": "значение" }
        
        for raw_name, raw_val in raw_attributes.items():
            std_key = self._normalize_attribute_name(raw_name)
            if std_key and std_key in row:
                row[std_key] = self._normalize_value(std_key, raw_val)
                
        # Явное заполнение назначения, если не вывелось из атрибутов
        if not row["attr_purpose"]:
            cat_lower = row["categories"].lower()
            if "входн" in cat_lower or "input" in cat_lower:
                row["attr_purpose"] = "Входная дверь"
            elif "межкомнат" in cat_lower or "interior" in cat_lower:
                row["attr_purpose"] = "Межкомнатная дверь"
                
        return row

    def export(self, products: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Основной метод экспорта.
        products: список словарей продуктов (плоский список: родители + дети).
                  У детей должно быть поле 'parent_sku' или флаг.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wp_import_{timestamp}.csv"
            
        filepath = os.path.join(self.output_dir, filename)
        
        rows = []
        # Группировка не требуется, WP All Import сам свяжет по parent_sku, 
        # но порядок важен: сначала родитель, потом дети.
        # Предполагаем, что входной список уже отсортирован или содержит метки.
        
        for prod in products:
            is_child = prod.get("is_variation", False) or "parent_id" in prod
            parent_sku = prod.get("parent_sku", None)
            
            # Если это ребенок, но нет явного parent_sku, пробуем взять у родителя (если объект вложен)
            if is_child and not parent_sku:
                # Логика поиска родителя, если данные вложены
                pass 
            
            row = self._map_product_to_row(prod, parent_sku=parent_sku)
            rows.append(row)
            
        # Запись в CSV
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=WP_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
            
        print(f"✅ Экспорт завершен: {filepath}")
        print(f"   Всего товаров: {len(rows)}")
        print(f"   Колонки: {len(WP_COLUMNS)}")
        
        return filepath
