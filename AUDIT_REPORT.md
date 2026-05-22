# 🔍 ПОЛНЫЙ АУДИТ ПРОЕКТА MEEYG 1.0

**Дата:** 03.05.2026  
**Цель проекта:** Парсинг товаров с разных сайтов со всеми атрибутами и вариациями, сохранение в структуре родитель-дети (каждый в своей строке)

---

## ✅ ЧТО РАБОТАЕТ ПРАВИЛЬНО

### 1. **Архитектура базы данных**
- ✅ Модель `Product` имеет поле `parent_product_id` для иерархии
- ✅ Правильные индексы и внешние ключи
- ✅ Поле `compatible_collections` для погонажа (JSON)
- ✅ Модель `ProductAttribute` для хранения атрибутов
- ✅ Каскадное удаление настроено корректно

### 2. **Структура парсера**
- ✅ Базовый класс `BaseParser` с абстрактными методами
- ✅ Playwright для обхода защиты сайтов
- ✅ Stealth-режим и эмуляция человеческого поведения
- ✅ Асинхронная архитектура

### 3. **Логика родитель-дети**
- ✅ Парсер создает родительский товар
- ✅ Для каждого размера создается дочерний товар
- ✅ Связь через `parent_product_id`

---

## ❌ КРИТИЧЕСКИЕ ОШИБКИ

### **ОШИБКА #1: Дублирование поля в ParsedProduct**
**Файл:** `src/modules/parsing/base_parser.py` (строки 34-35)

```python
compatible_collections: List[str] = field(default_factory=list)
compatible_collections: List[str] = field(default_factory=list)  # ❌ ДУБЛИКАТ!
```

**Проблема:** Поле `compatible_collections` объявлено дважды. Это вызовет ошибку при создании dataclass.

**Влияние:** 🔴 КРИТИЧЕСКОЕ - парсер не сможет работать

**Исправление:**
```python
compatible_collections: List[str] = field(default_factory=list)
# Удалить вторую строку
```

---

### **ОШИБКА #2: Отсутствует зависимость playwright**
**Файл:** `pyproject.toml`

**Проблема:** В зависимостях нет `playwright`, хотя парсер его использует.

**Влияние:** 🔴 КРИТИЧЕСКОЕ - парсер не запустится

**Исправление:**
```toml
dependencies = [
    "sqlalchemy>=2.0.0",
    "sqlcipher3>=0.5.3",
    "pandas>=2.0.0",
    "openpyxl>=3.1.0",
    "pyside6>=6.6.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "aiohttp>=3.9.0",
    "beautifulsoup4>=4.12.0",
    "lxml>=5.0.0",
    "tenacity>=8.2.0",
    "tqdm>=4.66.0",
    "structlog>=24.0.0",
    "pydantic-settings>=2.0.0",
    "playwright>=1.40.0",  # ✅ ДОБАВИТЬ
]
```

---

### **ОШИБКА #3: Отсутствует зависимость playwright-stealth**
**Файл:** `src/modules/parsing/engine.py` (строка 12)

```python
from playwright_stealth import Stealth  # ❌ Пакет не установлен
```

**Проблема:** Используется `playwright_stealth`, но он не в зависимостях.

**Влияние:** 🟡 СРЕДНЕЕ - `engine.py` не работает, но `tandoor_playwright_parser.py` работает

**Исправление:**
```toml
dependencies = [
    # ... другие зависимости
    "playwright-stealth>=1.0.0",  # ✅ ДОБАВИТЬ
]
```

---

### **ОШИБКА #4: Несовместимость сигнатур методов**
**Файл:** `src/modules/parsing/tandoor_playwright_parser.py`

**Проблема:** Метод `run()` принимает `session: Session`, но в `base_parser.py` сигнатура другая.

**Базовый класс (строка 111):**
```python
async def run(self, session: Session, **kwargs: Any) -> Dict[str, Any]:
```

**Tandoor парсер (строка 407):**
```python
async def run(self, session: Session, **kwargs) -> Dict[str, Any]:
```

**Влияние:** 🟢 НИЗКОЕ - работает, но нарушает контракт

**Исправление:** Добавить аннотацию типа `**kwargs: Any`

---

### **ОШИБКА #5: Неправильная передача session в конструктор**
**Файл:** `run_parser.py` (строка 496-501)

```python
parser = TandoorPlaywrightParser(
    supplier_id=supplier.id,
    db_session=session,  # ❌ Неправильный параметр
    headless=True,
    log_callback=lambda msg: log.info(f"[Parser] {msg}")
)
```

**Проблема:** Конструктор `TandoorPlaywrightParser` не принимает `db_session`, только `supplier_id`.

**Влияние:** 🔴 КРИТИЧЕСКОЕ - скрипт `run_parser.py` не работает

**Исправление:**
```python
parser = TandoorPlaywrightParser(
    supplier_id=supplier.id,
    headless=True,
    log_callback=lambda msg: log.info(f"[Parser] {msg}")
)

# Session передается в метод run()
results = await parser.run(session=session, urls=[target_product_url], is_category=False)
```

---

### **ОШИБКА #6: Отсутствует category_id при сохранении**
**Файл:** `src/modules/parsing/tandoor_playwright_parser.py` (метод `_db_save_batch`)

**Проблема:** При создании товаров не устанавливается `category_id`, хотя это важно для структуры.

**Влияние:** 🟡 СРЕДНЕЕ - товары сохраняются без категории

**Исправление:**
```python
# В методе _db_save_batch добавить:
parent = Product(
    supplier_id=self.supplier_id,
    category_id=parent_data.category_id,  # ✅ ДОБАВИТЬ
    title=parent_data.title,
    # ... остальные поля
)

child = Product(
    supplier_id=self.supplier_id,
    category_id=parent_data.category_id,  # ✅ ДОБАВИТЬ
    parent_product_id=parent.id,
    # ... остальные поля
)
```

---

### **ОШИБКА #7: Неэффективный поиск существующих товаров**
**Файл:** `src/modules/parsing/tandoor_playwright_parser.py` (строки 306-310)

```python
existing_parent = session.query(Product).filter(
    Product.supplier_id == self.supplier_id,
    Product.external_sku == parent_data.sku,  # ❌ Может быть None
    Product.title == parent_data.title,
).first()
```

**Проблема:** Если `sku` равен `None`, фильтр не сработает корректно.

**Влияние:** 🟡 СРЕДНЕЕ - дублирование товаров

**Исправление:**
```python
if parent_data.sku:
    existing_parent = session.query(Product).filter(
        Product.supplier_id == self.supplier_id,
        Product.external_sku == parent_data.sku,
    ).first()
else:
    existing_parent = session.query(Product).filter(
        Product.supplier_id == self.supplier_id,
        Product.title == parent_data.title,
        Product.parent_product_id.is_(None),
    ).first()
```

---

### **ОШИБКА #8: Отсутствует обработка погонажа**
**Файл:** `src/modules/parsing/tandoor_playwright_parser.py`

**Проблема:** Парсер извлекает `compatible_collections`, но не парсит сами товары погонажа (доборы, наличники).

**Влияние:** 🟡 СРЕДНЕЕ - погонаж не сохраняется

**Решение:** Нужно добавить метод для парсинга погонажа как отдельных товаров с `parent_product_id`.

---

### **ОШИБКА #9: Отсутствует валидация данных перед сохранением**
**Файл:** `src/modules/parsing/tandoor_playwright_parser.py`

**Проблема:** Нет проверки обязательных полей перед сохранением в БД.

**Влияние:** 🟡 СРЕДНЕЕ - возможны ошибки БД

**Исправление:**
```python
def _validate_product_data(self, product: ParsedProduct) -> bool:
    """Проверяет, что у товара есть все обязательные поля."""
    if not product.title or not product.title.strip():
        self._log(f"Пропущен товар без названия: {product.url}")
        return False
    if product.price is None or product.price < 0:
        self._log(f"Пропущен товар с некорректной ценой: {product.title}")
        return False
    return True
```

---

### **ОШИБКА #10: Неправильная обработка размеров в engine.py**
**Файл:** `src/modules/parsing/engine.py` (строки 43-57)

**Проблема:** Логика создания родителя и детей неправильная:
1. Родитель создается с `price=0.0` вместо реальной цены
2. Размер берется из атрибутов, но может отсутствовать

**Влияние:** 🔴 КРИТИЧЕСКОЕ для `engine.py`

**Исправление:**
```python
def _save_product_sync(self, product: ParsedProduct, session: Session):
    clean_title = PARENT_TITLE_RE.sub("", product.title).strip()
    
    # Ищем или создаем родителя
    parent = session.query(Product).filter_by(
        supplier_id=self.supplier_id, 
        title=clean_title, 
        parent_product_id=None
    ).first()
    
    if not parent:
        parent = Product(
            supplier_id=self.supplier_id, 
            title=clean_title, 
            price=product.price,  # ✅ Реальная цена
            currency=product.currency,
            description=product.description,
        )
        session.add(parent)
        session.flush()
    
    # Сохраняем вариацию
    size = product.attributes.get("Размер", "Стандарт")  # ✅ Значение по умолчанию
    
    child = session.query(Product).filter_by(
        parent_product_id=parent.id, 
        title=product.title
    ).first()
    
    if not child:
        child = Product(
            supplier_id=self.supplier_id, 
            parent_product_id=parent.id, 
            title=product.title, 
            price=product.price,
            currency=product.currency,
        )
        session.add(child)
        session.flush()
        
        # Сохраняем атрибуты
        for attr_name, attr_value in product.attributes.items():
            session.add(ProductAttribute(
                product_id=child.id, 
                name=attr_name, 
                value=attr_value
            ))
    
    session.commit()
```

---

## ⚠️ ПРЕДУПРЕЖДЕНИЯ И УЛУЧШЕНИЯ

### **ПРЕДУПРЕЖДЕНИЕ #1: Отсутствует логирование ошибок в файл**
**Рекомендация:** Добавить запись ошибок парсинга в отдельный лог-файл для анализа.

### **ПРЕДУПРЕЖДЕНИЕ #2: Нет ограничения на количество повторных попыток**
**Рекомендация:** Использовать `tenacity` для retry-логики при сетевых ошибках.

### **ПРЕДУПРЕЖДЕНИЕ #3: Отсутствует очистка старых данных**
**Рекомендация:** Добавить механизм удаления неактуальных товаров.

### **ПРЕДУПРЕЖДЕНИЕ #4: Нет транзакционности при массовом сохранении**
**Рекомендация:** Использовать batch-вставки для ускорения.

### **ПРЕДУПРЕЖДЕНИЕ #5: Отсутствует кэширование категорий**
**Проблема:** В `tandoor_playwright_parser.py` есть `_category_cache`, но он не используется.

---

## 📋 ПЛАН ИСПРАВЛЕНИЙ (ПРИОРИТЕТЫ)

### 🔴 КРИТИЧЕСКИЕ (исправить немедленно)
1. ✅ Удалить дубликат `compatible_collections` в `base_parser.py`
2. ✅ Добавить `playwright` в зависимости
3. ✅ Исправить передачу `session` в `run_parser.py`
4. ✅ Исправить логику в `engine.py`

### 🟡 СРЕДНИЕ (исправить в ближайшее время)
5. ✅ Добавить `playwright-stealth` в зависимости
6. ✅ Добавить `category_id` при сохранении
7. ✅ Улучшить поиск существующих товаров
8. ✅ Добавить валидацию данных

### 🟢 НИЗКИЕ (улучшения)
9. Добавить парсинг погонажа
10. Добавить retry-логику
11. Оптимизировать batch-вставки
12. Добавить очистку старых данных

---

## 🎯 ИТОГОВАЯ ОЦЕНКА

| Критерий | Оценка | Комментарий |
|----------|--------|-------------|
| **Архитектура БД** | ⭐⭐⭐⭐⭐ | Отлично спроектирована |
| **Логика родитель-дети** | ⭐⭐⭐⭐☆ | Работает, но есть недочеты |
| **Парсинг данных** | ⭐⭐⭐☆☆ | Основа есть, нужны доработки |
| **Обработка ошибок** | ⭐⭐☆☆☆ | Слабая, нужно улучшить |
| **Производительность** | ⭐⭐⭐☆☆ | Средняя, можно оптимизировать |
| **Код-стиль** | ⭐⭐⭐⭐☆ | Хороший, есть мелкие недочеты |

**ОБЩАЯ ОЦЕНКА:** ⭐⭐⭐☆☆ (3.5/5)

---

## 📝 ВЫВОДЫ

Проект имеет **хорошую архитектурную основу**, но содержит **критические ошибки**, которые мешают его работе:

1. **Дублирование полей** - блокирует запуск
2. **Отсутствующие зависимости** - парсер не запустится
3. **Неправильная передача параметров** - скрипты не работают

После исправления критических ошибок проект будет **полностью функциональным** для парсинга товаров в структуре родитель-дети.

**Рекомендация:** Сначала исправить все 🔴 КРИТИЧЕСКИЕ ошибки, затем протестировать на реальных данных, после чего переходить к 🟡 СРЕДНИМ улучшениям.
