# MEEYG 1.0 — Архитектура и документация

**MEEYG (Make Everything Easy Yet Great)** — приложение для автоматического сбора, хранения и экспорта данных о товарах поставщиков.

---

## 📋 Содержание

1. [Архитектура приложения](#1-архитектура-приложения)
2. [База данных](#2-база-данных)
3. [Модули](#3-модули)
4. [Логика работы с товарами](#4-логика-работы-с-товарами)
5. [Экспорт в CSV](#5-экспорт-в-csv)
6. [Архивирование](#6-архивирование)
7. [Расширение функциональности](#7-расширение-функциональности)

---

## 1. Архитектура приложения

### Общая структура

```
MEEYG 1.0/
├── src/
│   ├── core/          # Ядро: логгер, базовые утилиты
│   ├── database/      # Модуль БД: модели, сессии, миграции
│   ├── modules/       # Бизнес-логика парсинга, архивирования, экспорта
│   │   ├── parser/
│   │   ├── archive/
│   │   └── exporter/
│   ├── ui/            # Qt GUI приложение
│   │   ├── pages/     # Страницы: Главная, Поставщики, Архив и т.д.
│   │   └── widgets/   # Переиспользуемые виджеты
│   └── scripts/       # Скрипты миграции, генерации, утилиты
├── data/              # SQLite база данных
├── logs/              # Логи приложения
└── ARCHITECTURE.md    # Этот файл
```

### Flow данных

```
[Поставщик (Supplier)]
       ↓
[Категории (Category)]
       ↓
[Товары (Product)]
    ├── атрибуты → [ProductAttribute]
    └── дочерние → [Product (related)]
           ↓
[Архивный снепшот (ArchiveSnapshot)]
           ↓
[Архивные элементы (ArchiveItem)]
           ↓
[CSV Export]
```

---

## 2. База данных

### Таблица `suppliers`

Хранит информацию о поставщиках.

| Поле | Тип | Описание |
|---|---|---|
| id | INTEGER | PK |
| name | TEXT | Имя поставщика (напр. "Тандор", "Флай Дорс") |
| base_url | TEXT | Базовый URL сайта поставщика |
| is_active | BOOLEAN | Активен ли поставщик |
| last_discovery_run | DATETIME | Последняя разведка категорий |
| last_scrape_run | DATETIME | Последний парсинг товаров |

### Таблица `categories`

Иерархия категорий товаров.

| Поле | Тип | Описание |
|---|---|---|
| id | INTEGER | PK |
| supplier_id | INTEGER | FK → suppliers |
| parent_id | INTEGER | FK → categories (self-reference) |
| name | TEXT | Название категории |
| url | TEXT | URL категории на сайте поставщика |
| xpath_selector | TEXT | XPath для парсинга товаров |
| sort_order | INTEGER | Порядок сортировки |

### Таблица `products`

Основная таблица товаров.

| Поле | Тип | Описание |
|---|---|---|
| id | INTEGER | PK |
| supplier_id | INTEGER | FK → suppliers |
| category_id | INTEGER | FK → categories |
| parent_product_id | INTEGER | FK → products (NULL = родитель) |
| external_sku | TEXT | Артикул поставщика |
| title | TEXT | Название товара |
| description | TEXT | Полное описание |
| price | FLOAT | Цена |
| currency | TEXT | Валюта (RUB, USD) |
| is_available | BOOLEAN | Наличие |
| is_ready_for_export | BOOLEAN | Готов к экспорту |
| compatible_collections | TEXT | JSON array коллекций погонажа |
| image_urls | TEXT | JSON array URL изображений |

### Таблица `product_attributes`

Дополнительные атрибуты товаров (размер, цвет, тип и т.д.).

| Поле | Тип | Описание |
|---|---|---|
| id | INTEGER | PK |
| product_id | INTEGER | FK → products |
| name | TEXT | Имя атрибута (Размер, Цвет, Тип) |
| value | TEXT | Значение атрибута |

**Стандартные атрибуты:**
- `Размер` — для дверей: "40", "60", "70", "80", "90"
- `Цвет` — цвет товара (Античный орех, Белый и т.д.)
- `Тип` — "ДГ" (дверное полотно), "Погонаж"
- `Направление` — "Левое", "Правое", "-"
- `ParentSKU` — SKU родителя (для дочерних товаров)
- `Manufacturer of the collection` — коллекция для погонажа

### Таблица `archive_snapshots`

Снепшоты (архивные копии) состояния товаров.

| Поле | Тип | Описание |
|---|---|---|
| id | INTEGER | PK |
| supplier_id | INTEGER | FK → suppliers |
| name | TEXT | Имя снепшота |
| snapshot_type | TEXT | Тип: "full" (полный) или "partial" |
| total_products | INTEGER | Всего товаров в снепшоте |
| created_at | DATETIME | Дата создания |

### Таблица `archive_items`

Элементы архивного снепшота — полная копия данных для экспорта.

| Поле | Тип | Описание |
|---|---|---|
| id | INTEGER | PK |
| snapshot_id | INTEGER | FK → archive_snapshots |
| product_id | INTEGER | ID оригинального товара |
| external_sku | TEXT | Артикул |
| title | TEXT | Название |
| price | FLOAT | Цена |
| currency | TEXT | Валюта |
| is_available | BOOLEAN | Наличие |
| category_name | TEXT | Путь категории |
| image_urls | TEXT | JSON изображений |
| attributes_json | TEXT | JSON всех атрибутов |
| **manufacturer** | TEXT | Производитель (Supplier.name) |
| **parent_sku** | TEXT | SKU родительского товара |
| **collection** | TEXT | Коллекция товара |
| **brand** | TEXT | Бренд (= manufacturer) |
| **availability** | TEXT | "в наличии" / "нет в наличии" |
| **stock_status** | TEXT | "instock" / "outofstock" |
| **vendor** | TEXT | Vendor (= manufacturer) |
| **description** | TEXT | Полное описание |
| **is_parent** | BOOLEAN | Флаг родительского товара |

---

## 3. Модули

### 3.1 Parser (`src/modules/parser/`)

Парсинг сайтов поставщиков.

**Основные классы:**
- `ParserEngine` — движок парсинга
- `DiscoveryWorker` — разведка категорий

### 3.2 Archive (`src/modules/archive/`)

Архивирование данных.

**Основные классы:**
- `ArchiveEngine` — создание и управление снепшотами

**Методы:**
- `create_snapshot()` — создать архивный снимок
- `list_snapshots()` — список всех снепшотов
- `get_snapshot_items()` — товары из снепшота
- `delete_snapshot()` — удалить снепшот
- `compare_snapshots()` — сравнение двух снепшотов

### 3.3 Exporter (`src/modules/exporter/`)

Экспорт данных в CSV.

---

## 4. Логика работы с товарами

### 4.1 Родительско-дочерняя структура

Товары organisуются в иерархию:

```
РОДИТЕЛЬ (parent_product_id = NULL)
├── Дочерний товар 1 (размер 40)
├── Дочерний товар 2 (размер 60)
├── Дочерний товар 3 (размер 80)
└── ...
```

**Родительский товар:**
- `parent_product_id = NULL`
- Имеет базовое название коллекции
- Определяет `compatible_collections` (для погонажа)
- Цена обычно 0 или базовая

**Дочерний товар:**
- `parent_product_id = ID родителя`
- Имеет конкретный размер/вариацию
- Наследует коллекцию от родителя
- Через атрибут `ParentSKU` ссылается на родителя

### 4.2 Генерация SKU

Формат SKU: `{Производитель} {Название} {Номер}`

**Примеры:**
```
Тандор Элегия-2 000001     — родитель
Тандор Элегия-2 000002     —_child, размер 40
Тандор Элегия-2 000003     — child, размер 60
Тандор Подпятник 000007    — погонаж
```

**Алгоритм генерации (generate_skus_v2.py):**

1. Группируем товары по `parent_product_id`
2. Родителям присваиваем номер по порядку группы
3. Детям присваиваем номер, следующий за родителем
4. Очищаем SKU от префиксов "Входная дверь", размеров типа "950x2030"

### 4.3 Погонаж и compatible_collections

Погонажные товары (карнизы, доборы, наличники) связаны с коллекциями дверей через поле `compatible_collections`:

```json
["FLYDOORS>MONE", "TANDOOR>Элегия-2"]
```

**Для отображения:**
- У родителя:显示ить как строку через запятую
- У дочернего погонажа:显示ить из атрибута `Manufacturer of the collection`

---

## 5. Экспорт в CSV

### 5.1 Формат CSV для WooCommerce

**Колонки CSV:**

| Колонка CSV | Источник | Описание |
|---|---|---|
| `ID` |ArchiveItem.id | Уникальный ID |
| `Type` |is_parent | "simple" или "variable" |
| `SKU` |external_sku| Артикул товара |
| `Name` |title| Название товара |
| `Published` | | "1" (всегда опубликовано) |
| `Is Featured` | | "0" |
| `Visibility in catalog` | | "visible" |
| `Short description` |description| Краткое описание |
| `Description` |description| Полное описание |
| `Date sale price starts` | | (пусто) |
| `Date sale price ends` | | (пусто) |
| `Tax status` | | "taxable" |
| `Tax class` | | |
| `In stock?` |stock_status| "instock" / "outofstock" |
| `Stock` | | (количество, если есть) |
| `Backorders allowed?` | | "no" |
| `Low stock amount` | | |
| `Sold individually?` | | "no" |
| `Length` |Размер (атрибут)| |
| `Width` | | |
| `Height` | | |
| `Allow customer reviews?` | | "yes" |
| `Purchase Note` | | |
| `Sale price` | | |
| `Regular price` |price| |
| `Categories` |category_name| Путь категории |
| `Tags` | | |
| `Shipping class` | | |
| `Images` |image_urls| URL изображений, через запятую |
| `Download limit` | | |
| `Download expiry days` | | |
| `Parent` |parent_sku| SKU родителя (для вариаций) |
| `Grouped products` | | |
| `Upsells` | | |
| `Cross-sells` | | |
| `External URL` | | |
| `Button text` | | |
| `Position` | | |

### 5.2 Пример генерации CSV

```python
import csv
from src.database.session import get_session
from src.database.models import ArchiveItem, ArchiveSnapshot

def export_snapshot_to_csv(snapshot_id: int, output_path: str):
    with get_session() as session:
        snapshot = session.query(ArchiveSnapshot).get(snapshot_id)
        items = session.query(ArchiveItem).filter(
            ArchiveItem.snapshot_id == snapshot_id
        ).order_by(ArchiveItem.product_id).all()
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Заголовок
            writer.writerow([
                'Type', 'SKU', 'Name', 'Published', 'Is Featured',
                'Visibility in catalog', 'Short description', 'Description',
                'In stock?', 'Stock', 'Regular price', 'Categories',
                'Images', 'Parent', 'brand', 'vendor', 'collection'
            ])
            
            for item in items:
                # Тип: variable для родителя, simple для детей
                product_type = "variable" if item.is_parent else "simple"
                
                # Статус наличия
                stock_status = "instock" if item.is_available else "outofstock"
                
                # Parent SKU (только для детей)
                parent_sku = item.parent_sku if not item.is_parent else ""
                
                writer.writerow([
                    product_type,
                    item.external_sku,
                    item.title,
                    "1",  # Published
                    "0",  # Is Featured
                    "visible",
                    item.description or "",
                    item.description or "",
                    stock_status,
                    "",  # Stock quantity
                    item.price or "0.00",
                    item.category_name,
                    item.get_image_urls()[0] if item.get_image_urls() else "",
                    parent_sku,
                    item.manufacturer,
                    item.vendor,
                    item.collection
                ])
```

### 5.3 Важные замечания

1. **Кодировка:** UTF-8 с BOM для корректного отображения кириллицы в Excel
2. **Разделитель:** Запятая (,) или точка с запятой (;) в зависимости от локали
3. **Изображения:** URL через запятую, без пробелов
4. **Категории:** Полный путь через " > " (Каталог > Межкомнатные двери > по конструкции)
5. **Вариации:** Дочерние товары должны иметь `Parent` = SKU родителя

---

## 6. Архивирование

### 6.1 Создание снепшота

```python
from src.modules.archive.engine import ArchiveEngine
from src.database.session import get_session

with get_session() as session:
    engine = ArchiveEngine(
        supplier_id=1,  # ID поставщика
        log_callback=lambda msg: print(msg),
        progress_callback=lambda pct, total, msg: print(f"{pct}%: {msg}")
    )
    
    result = engine.create_snapshot(
        db_session=session,
        name="Полный архив 2026-05-07",
        description="Ежедневный полный архив",
        snapshot_type="full"
    )
    
    print(f"Snapshot ID: {result['snapshot_id']}")
    print(f"Total products: {result['stats'].total_products}")
```

### 6.2填充 новых полей

При создании снепшота `ArchiveEngine` автоматически заполняет:

| Поле | Значение |
|---|---|
| `manufacturer` | `Supplier.name` |
| `brand` | `Supplier.name` |
| `vendor` | `Supplier.name` |
| `parent_sku` | SKU родителя (из `parent_skus` словаря) |
| `collection` | Из `compatible_collections` или категории |
| `availability` | "в наличии" / "нет в наличии" |
| `stock_status` | "instock" / "outofstock" |
| `description` | `Product.description` |
| `is_parent` | `parent_product_id is None` |

---

## 7. Расширение функциональности

### 7.1 Добавление нового поставщика

1. **UI → Поставщики → Добавить**
   - Ввести имя поставщика
   - Указать базовый URL
   
2. **Разведка категорий**
   - Нажать "Разведка" для нового поставщика
   - Система найдёт категории и URL
   
3. **Настройка XPath**
   - Для каждой категории указать XPath selector
   - XPath должен извлекать ссылки на товары

4. **Парсинг товаров**
   - Нажать "Парсинг"
   - Система спарсит товары по категориям

### 7.2 Добавление новой колонки в БД

1. **Обновить модель** (`src/database/models.py`):
   ```python
   class Product(Base):
       # ...
       new_field = Column(Text, nullable=True, comment="Описание")
   ```

2. **Создать миграцию** (`scripts/migrations/add_new_field.py`):
   ```python
   from sqlalchemy import text
   
   def run_migration():
       with engine.connect() as conn:
           conn.execute(text(
               "ALTER TABLE products ADD COLUMN new_field TEXT DEFAULT NULL"
           ))
           conn.commit()
   ```

3. **Обновить UI** (если нужно отображать):
   ```python
   # В archive_page.py
   NEW_COL = 21
   _HEADERS.append("Новая колонка")
   _KEYS.append("new_field")
   ```

4. **Заполнить данные** в `load_data()`:
   ```python
   item = {
       # ...
       "new_field": p.new_field or "-",
   }
   ```

### 7.3 Изменение формата SKU

1. Открыть `src/scripts/generate_skus_v2.py`
2. Изменить логику в функции `generate_sku()`
3. Перезапустить генерацию SKU

### 7.4 Запуск миграций

```bash
cd "D:\Projects\MEEYG 1.0"
.\.venv\Scripts\python.exe scripts\add_archive_export_fields.py
```

---

## 📞 Контакты и поддержка

При возникновении проблем:
1. Проверьте логи в `logs/meeyg.log`
2. Убедитесь, что база данных подключена
3. Проверьте подключение к интернету для парсинга

---

**Версия документации:** 1.0  
**Дата обновления:** 2026-05-07