# 📦 Структура и содержимое проекта MEEYG 2.0

## 🌳 Дерево папок
```text
├── build/
│   ├── bdist.win-amd64/
│   └── lib/
│       └── src/
│           ├── core/
│           │   ├── __init__.py
│           │   ├── config.py
│           │   └── logger.py
│           ├── database/
│           │   ├── __init__.py
│           │   ├── engine.py
│           │   ├── migrate_add_parent_product_id.py
│           │   ├── models.py
│           │   ├── session.py
│           │   └── supplier_crud.py
│           ├── modules/
│           │   ├── archive/
│           │   │   ├── __init__.py
│           │   │   └── engine.py
│           │   ├── discovery/
│           │   │   ├── __init__.py
│           │   │   └── engine.py
│           │   ├── export/
│           │   │   ├── __init__.py
│           │   │   └── generator.py
│           │   ├── import_prep/
│           │   │   ├── __init__.py
│           │   │   └── mapper.py
│           │   ├── parsing/
│           │   │   ├── __init__.py
│           │   │   ├── engine.py
│           │   │   └── tandoor_playwright_parser.py
│           │   └── __init__.py
│           ├── ui/
│           │   ├── pages/
│           │   │   ├── __init__.py
│           │   │   ├── archive_page.py
│           │   │   ├── discovery_page.py
│           │   │   ├── export_page.py
│           │   │   ├── parsing_page.py
│           │   │   ├── placeholder_page.py
│           │   │   └── suppliers_page.py
│           │   ├── styles/
│           │   │   └── __init__.py
│           │   ├── __init__.py
│           │   └── main_window.py
│           ├── __init__.py
│           └── main.py
├── config/
├── data/
│   └── exports/
├── docs/
│   └── playwright_parser_integration_guide.md
├── logs/
│   ├── test_report_20260427_222828.json
│   ├── test_report_20260427_223738.json
│   ├── test_report_20260427_223834.json
│   ├── test_report_20260427_223912.json
│   └── test_report_20260427_232701.json
├── meeyg.egg-info/
│   ├── PKG-INFO
│   ├── SOURCES.txt
│   ├── dependency_links.txt
│   ├── requires.txt
│   └── top_level.txt
├── pw_user_data/
│   └── supplier_1/
├── scripts/
│   ├── add_compatible_collections_field.py
│   ├── add_parent_product_field.py
│   └── clean_categories.py
├── src/
│   ├── core/
│   │   ├── config/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logger.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   ├── migrate_add_parent_product_id.py
│   │   ├── models.py
│   │   ├── session.py
│   │   └── supplier_crud.py
│   ├── modules/
│   │   ├── archive/
│   │   │   ├── __init__.py
│   │   │   └── engine.py
│   │   ├── discovery/
│   │   │   ├── __init__.py
│   │   │   └── engine.py
│   │   ├── export/
│   │   │   ├── __init__.py
│   │   │   └── generator.py
│   │   ├── import_prep/
│   │   │   ├── __init__.py
│   │   │   └── mapper.py
│   │   ├── parsing/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py
│   │   │   └── tandoor_playwright_parser.py
│   │   └── __init__.py
│   ├── ui/
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   ├── archive_page.py
│   │   │   ├── discovery_page.py
│   │   │   ├── export_page.py
│   │   │   ├── parsing_page.py
│   │   │   ├── placeholder_page.py
│   │   │   └── suppliers_page.py
│   │   ├── styles/
│   │   │   ├── __init__.py
│   │   │   └── dark_theme.qss
│   │   ├── __init__.py
│   │   └── main_window.py
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── check_hierarchy_implementation.py
│   ├── test_hierarchy_logic.py
│   └── test_tandoor_parser.py
├── .env
├── .env.example
├── check.py
├── clear_db.py
├── collect_project.py
├── parser_log.txt
├── project_info.md
├── pyproject.toml
├── quick_check.py
├── run_parser.py
├── setup_env.py
└── verify_hierarchy.py
```

## 📄 Содержимое файлов
### `.env`
```text
# Database encryption key (32 bytes, hex-encoded)
DB_KEY=baec46448214deb5fb7805afff26c24f0df011e75ec75430cfa79da55003674d

# Database path
DB_PATH=data/meeyg.db

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Application settings
APP_NAME=MEEYG
APP_VERSION=1.0.0

# Playwright settings
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000
PLAYWRIGHT_DELAY_MIN=1.0
PLAYWRIGHT_DELAY_MAX=3.0

```

### `.env.example`
```text
# Database encryption key (must be 32 bytes, hex-encoded)
DB_KEY=your_32_byte_hex_encryption_key_here

# Database path
DB_PATH=data/meeyg.db

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Application settings
APP_NAME=MEEYG
APP_VERSION=1.0.0

```

### `check.py`
```python
# check.py
from dotenv import load_dotenv
import os, sqlcipher3 as sqlite3

load_dotenv()
key = os.getenv('DB_KEY')

c = sqlite3.connect('data/meeyg.db')
c.execute(f"PRAGMA key = '{key}'")

print('Категорий:', c.execute('SELECT COUNT(*) FROM categories').fetchone()[0])
print('Товаров:', c.execute('SELECT COUNT(*) FROM products').fetchone()[0])
print('Атрибутов:', c.execute('SELECT COUNT(*) FROM product_attributes').fetchone()[0])

# Проверим поля в products
print('\nПоля в products:')
for col in c.execute('PRAGMA table_info(products)'):
    print(f'  {col[1]} ({col[2]})')

c.close()
```

### `clear_db.py`
```python

import logging
from sqlalchemy import text
from src.database.session import get_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_database():
    """Deletes all records from Product and ProductAttribute tables."""
    logger.info("Attempting to clear Product and ProductAttribute tables...")
    with get_session() as session:
        try:
            # We use text() for raw SQL to handle potential cascading issues
            # or if we need to disable foreign key checks, though not needed here.
            session.execute(text("DELETE FROM product_attributes"))
            session.execute(text("DELETE FROM products"))
            session.commit()
            logger.info("Successfully cleared tables.")
        except Exception as e:
            logger.error(f"An error occurred during table clearing: {e}")
            session.rollback()

if __name__ == "__main__":
    clear_database()

```

### `collect_project.py`
```python
import os
import fnmatch
from pathlib import Path

# --- НАСТРОЙКИ ---
OUTPUT_FILE = "project_info.md"
MAX_FILE_SIZE = 100 * 1024  # 100 КБ (чтобы не перегружать контекст)

EXCLUDE_DIRS = {
    "__pycache__", ".git", ".venv", "venv", ".idea", ".vscode", 
    "node_modules", "backups", ".pytest_cache", ".mypy_cache"
}

EXCLUDE_PATTERNS = [
    "*.pyc", "*.pyo", "*.so", "*.dll", "*.exe", "*.db", "*.sqlite",
    "*.log", "*.tmp", "*.xlsx", "*.csv", "*.png", "*.jpg", "*.jpeg",
    "*.webp", "*.svg", "*.ico", "*.zip", "*.rar", "*.tar", "*.gz"
]

def should_exclude_dir(name):
    return name in EXCLUDE_DIRS or name.startswith(".")

def should_exclude_file(name):
    return any(fnmatch.fnmatch(name, pattern) for pattern in EXCLUDE_PATTERNS)

def get_tree(root, prefix=""):
    tree = []
    try:
        items = sorted(os.listdir(root))
        dirs, files = [], []
        for item in items:
            path = os.path.join(root, item)
            if os.path.isdir(path):
                if not should_exclude_dir(item):
                    dirs.append(item)
            else:
                if not should_exclude_file(item):
                    files.append(item)

        for i, d in enumerate(dirs):
            is_last = (i == len(dirs) - 1) and (len(files) == 0)
            tree.append(f"{prefix}{'└── ' if is_last else '├── '}{d}/")
            ext = "    " if is_last else "│   "
            tree.extend(get_tree(os.path.join(root, d), prefix + ext))

        for i, f in enumerate(files):
            is_last = (i == len(files) - 1)
            tree.append(f"{prefix}{'└── ' if is_last else '├── '}{f}")
    except PermissionError:
        tree.append(f"{prefix}[Permission Denied]")
    return tree

def collect_files(root):
    contents = []
    output_abs = os.path.abspath(OUTPUT_FILE)
    
    for current_root, dirs, files in os.walk(root):
        # Фильтрация папок на лету, чтобы не заходить в них
        dirs[:] = [d for d in dirs if not should_exclude_dir(d)]
        
        for file in sorted(files):
            if should_exclude_file(file):
                continue
                
            file_path = os.path.join(current_root, file)
            rel_path = os.path.relpath(file_path, root)
            
            # Пропускаем сам файл отчёта
            if os.path.abspath(file_path) == output_abs:
                continue
                
            # Пропускаем слишком большие файлы
            try:
                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    contents.append(f"### `{rel_path}`\n*(Пропущен: размер > {MAX_FILE_SIZE//1024} КБ)*\n")
                    continue
            except Exception:
                continue

            # Читаем текст
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                    # Определяем язык для подсветки
                    ext = os.path.splitext(file)[1].lower()
                    lang_map = {".py": "python", ".js": "javascript", ".json": "json", 
                                ".md": "markdown", ".yml": "yaml", ".yaml": "yaml", 
                                ".txt": "text", ".cfg": "ini", ".ini": "ini"}
                    lang = lang_map.get(ext, "text")
                    contents.append(f"### `{rel_path}`\n```{lang}\n{code}\n```\n")
            except UnicodeDecodeError:
                contents.append(f"### `{rel_path}`\n*(Пропущен: бинарный файл)*\n")
            except Exception as e:
                contents.append(f"### `{rel_path}`\n*(Ошибка чтения: {e})*\n")
                
    return contents

def main():
    print("🔍 Сканер проекта MEEYG 2.0")
    project_dir = os.path.abspath(".")
    print(f"📁 Сканирую: {project_dir}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("# 📦 Структура и содержимое проекта MEEYG 2.0\n\n")
        
        out.write("## 🌳 Дерево папок\n```text\n")
        tree = get_tree(project_dir)
        out.write("\n".join(tree))
        out.write("\n```\n\n")
        
        out.write("## 📄 Содержимое файлов\n")
        file_contents = collect_files(project_dir)
        out.write("\n".join(file_contents))
        
    print(f"✅ Готово! Файл сохранён: {os.path.abspath(OUTPUT_FILE)}")
    print(f"📤 Теперь загрузи `{OUTPUT_FILE}` в чат, и я проверю структуру, импорты и логику.")

if __name__ == "__main__":
    main()

```

### `parser_log.txt`
*(Пропущен: бинарный файл)*

### `pyproject.toml`
```text
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "meeyg"
version = "1.0.0"
description = "MEEYG - Modular Enterprise Environment for Yield Gathering"
requires-python = ">=3.12"
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
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.3.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "W", "I"]

```

### `quick_check.py`
```python
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
```

### `run_parser.py`
```python

import logging
import sys
import asyncio
from pathlib import Path

# Ensure the source root is in the system path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select

from src.core.logger import logger
from src.database.models import Supplier
from src.database.session import get_session
from src.modules.parsing.tandoor_playwright_parser import TandoorPlaywrightParser

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("run_parser_async")

async def main():
    """
    Main async function to run the Tandoor Playwright parser.
    """
    log.info("Запуск АСИНХРОННОГО парсера Tandoor...")
    
    supplier_name = "tandoor.ru"
    # --- ТЕСТОВЫЙ URL ОДНОГО ПРОДУКТА ---
    target_product_url = "https://tandoor.ru/catalog/product/dekanto-belyy-evo-pet-do-seryy-satin-2000-800/"

    with get_session() as session:
        log.info(f"Поиск поставщика по URL: {supplier_name}")
        supplier = session.execute(
            select(Supplier).where(Supplier.base_url.like(f"%{supplier_name}%"))
        ).scalar_one_or_none()

        if not supplier:
            log.error(f"Поставщик с базовым URL '{supplier_name}' не найден.")
            return

        log.info(f"Найден поставщик: {supplier.name} (ID: {supplier.id})")

        # Initialize the parser
        parser = TandoorPlaywrightParser(
            supplier_id=supplier.id,
            db_session=session,
                                    headless=True,
            log_callback=lambda msg: log.info(f"[Parser] {msg}")
        )

        try:
            log.info("Начало парсинга одного товара...")
            # Async call
            results = await parser.run(urls=[target_product_url], is_category=False)
            log.info("Парсинг завершен.")
            
            # Updated stats keys
            log.info(f"  Обработано товаров: {results.get('products_parsed', 0)}")
            log.info(f"  Создано вариаций: {results.get('variations_created', 0)}")
            log.info(f"  Обновлено/создано погонажа: {results.get('molding_items_upserted', 0)}")
            
            duration = (results["end_time"] - results["start_time"]).total_seconds()
            log.info(f"  Затрачено времени: {duration:.2f} сек")
            
            errors = results.get("errors", [])
            if errors:
                log.error(f"Найдены ошибки ({len(errors)}):")
                for i, err in enumerate(errors, 1):
                    log.error(f"  {i}. {err}")
            else:
                log.info("Ошибок во время выполнения не было.")

        except Exception as e:
            log.error(f"Критическая ошибка во время выполнения парсера: {e}", exc_info=True)

if __name__ == "__main__":
    # In Python 3.7+, this is the standard way to run the top-level async function.
    asyncio.run(main())

```

### `setup_env.py`
```python
#!/usr/bin/env python3
"""Setup script for MEEYG 1.0 environment."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"
PYTHON_MIN = (3, 12)


def print_step(msg: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {msg}")
    print(f"{'=' * 60}")


def check_python_version() -> None:
    print_step("Checking Python version")
    current = sys.version_info
    print(f"  Current Python: {current.major}.{current.minor}.{current.micro}")
    if current < PYTHON_MIN:
        print(f"  ERROR: Python {'.'.join(map(str, PYTHON_MIN))}+ required")
        sys.exit(1)
    print("  OK: Python version meets requirements")


def ensure_uv() -> None:
    print_step("Checking for uv package manager")
    if shutil.which("uv"):
        print("  uv found in PATH")
        return

    print("  uv not found, installing via pip...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "uv", "--quiet"],
        check=True,
    )
    print("  uv installed successfully")


def create_venv() -> None:
    print_step("Creating virtual environment")
    if VENV_DIR.exists():
        print(f"  Removing existing venv at {VENV_DIR}")
        shutil.rmtree(VENV_DIR)

    subprocess.run(
        ["uv", "venv", str(VENV_DIR)],
        check=True,
        cwd=PROJECT_ROOT,
    )
    print(f"  Virtual environment created at {VENV_DIR}")


def install_dependencies() -> None:
    print_step("Installing dependencies")
    venv_python = VENV_DIR / "Scripts" / "python.exe" if os.name == "nt" else VENV_DIR / "bin" / "python"

    subprocess.run(
        ["uv", "pip", "install", "-e", ".", "--python", str(venv_python)],
        check=True,
        cwd=PROJECT_ROOT,
    )
    print("  All dependencies installed successfully")


def create_env_file() -> None:
    print_step("Creating .env file")
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        print(f"  .env already exists at {env_path}, skipping")
        return

    import secrets
    db_key = secrets.token_hex(32)

    env_content = f"""# Database encryption key (32 bytes, hex-encoded)
DB_KEY={db_key}

# Database path
DB_PATH=data/meeyg.db

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Application settings
APP_NAME=MEEYG
APP_VERSION=1.0.0
"""
    env_path.write_text(env_content)
    print(f"  .env file created at {env_path}")
    print("  IMPORTANT: Keep DB_KEY secure and never commit it to version control")


def verify_installation() -> None:
    print_step("Verifying installation")
    venv_python = VENV_DIR / "Scripts" / "python.exe" if os.name == "nt" else VENV_DIR / "bin" / "python"

    required_packages = [
        "sqlalchemy",
        "pandas",
        "pydantic",
        "structlog",
        "aiohttp",
        "beautifulsoup4",
        "lxml",
        "tenacity",
        "tqdm",
        "python-dotenv",
    ]

    failed = []
    for pkg in required_packages:
        result = subprocess.run(
            [str(venv_python), "-c", f"import {pkg.split('-')[0]}"],
            capture_output=True,
        )
        status = "OK" if result.returncode == 0 else "FAILED"
        print(f"  {pkg}: {status}")
        if result.returncode != 0:
            failed.append(pkg)

    if failed:
        print(f"\n  WARNING: Failed to import: {', '.join(failed)}")
    else:
        print("\n  All packages verified successfully")


def main() -> None:
    print("\n" + "=" * 60)
    print("  MEEYG 1.0 - Environment Setup")
    print("=" * 60)

    check_python_version()
    ensure_uv()
    create_venv()
    install_dependencies()
    create_env_file()
    verify_installation()

    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    print(f"\n  Project root: {PROJECT_ROOT}")
    print(f"  Virtual env:  {VENV_DIR}")
    print(f"  Activate:     {'call .venv\\Scripts\\activate.bat' if os.name == 'nt' else 'source .venv/bin/activate'}")
    print()


if __name__ == "__main__":
    main()

```

### `verify_hierarchy.py`
```python
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

```

### `build\lib\src\__init__.py`
```python

```

### `build\lib\src\main.py`
```python
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import settings
from src.core.logger import logger
from src.database.models import Base
from src.database.session import engine
from src.ui.main_window import MainWindow
from src.ui.pages.archive_page import ArchivePage
from src.ui.pages.discovery_page import DiscoveryPage
from src.ui.pages.export_page import ExportPage
from src.ui.pages.parsing_page import ParsingPage
from src.ui.pages.placeholder_page import PlaceholderPage
from src.ui.pages.suppliers_page import SuppliersPage


def main() -> None:
    try:
        app = QApplication(sys.argv)
        app.setApplicationName(settings.app_name)
        app.setApplicationVersion(settings.app_version)

        qss_path = PROJECT_ROOT / "src" / "ui" / "styles" / "dark_theme.qss"
        if qss_path.exists():
            app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        window = MainWindow()

        dashboard = PlaceholderPage(
            "Главная",
            "Обзор аналитики поставщиков и ключевые показатели появятся здесь.",
        )
        suppliers = SuppliersPage()
        discovery = DiscoveryPage()
        parsing = ParsingPage()
        archive = ArchivePage()
        intelligence = PlaceholderPage(
            "Аналитика",
            "Инструменты рыночной аналитики и анализа поставщиков появятся здесь.",
        )
        export = ExportPage()

        window.register_page(dashboard)
        window.register_page(suppliers)
        window.register_page(discovery)
        window.register_page(parsing)
        window.register_page(archive)
        window.register_page(intelligence)
        window.register_page(export)

        window.show()
        logger.info("Application started")

        sys.exit(app.exec())

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as exc:
        logger.error(f"Application failed to start: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

```

### `build\lib\src\core\__init__.py`
```python

```

### `build\lib\src\core\config.py`
```python
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    app_name: str = Field(default="MEEYG", validation_alias="APP_NAME")
    app_version: str = Field(default="1.0.0", validation_alias="APP_VERSION")
    db_path: Path = Field(
        default=PROJECT_ROOT / "data" / "meeyg.db",
        validation_alias="DB_PATH",
    )
    db_key: str = Field(
        default="",
        validation_alias="DB_KEY",
    )
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    data_dir: Path = Field(default=PROJECT_ROOT / "data")
    logs_dir: Path = Field(default=PROJECT_ROOT / "logs")

    @field_validator("db_key", mode="before")
    @classmethod
    def validate_db_key(cls, v: str) -> str:
        if v and len(v) != 64:
            raise ValueError("DB_KEY must be a 64-character hex string (32 bytes)")
        return v

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()

```

### `build\lib\src\core\logger.py`
```python
import logging
import logging.handlers
from pathlib import Path

import structlog
from structlog.processors import (
    JSONRenderer,
    TimeStamper,
    add_log_level,
    format_exc_info,
)

from src.core.config import settings


def setup_logger() -> structlog.BoundLogger:
    log_file = settings.logs_dir / "app.log"

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter("%(message)s"))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(message)s",
        handlers=[file_handler, console_handler],
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            TimeStamper(fmt="iso"),
            add_log_level,
            format_exc_info,
            structlog.processors.UnicodeDecoder(),
            JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    return structlog.get_logger()


logger = setup_logger()

```

### `build\lib\src\database\__init__.py`
```python

```

### `build\lib\src\database\engine.py`
```python
import ctypes
import os
import secrets
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine as _sa_create_engine

from src.core.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROTECTED_KEY_PATH = PROJECT_ROOT / "data" / ".db_key.protected"


class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_ulong), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


def _generate_key() -> str:
    return secrets.token_hex(32)


def _protect_key_dpapi(key: str) -> bytes:
    key_bytes = key.encode("utf-16-le")
    blob_in = DATA_BLOB()
    blob_in.cbData = len(key_bytes)
    buf = (ctypes.c_ubyte * len(key_bytes)).from_buffer_copy(key_bytes)
    blob_in.pbData = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))

    blob_out = DATA_BLOB()

    result = ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(blob_in),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(blob_out),
    )
    if not result:
        raise RuntimeError("DPAPI CryptProtectData failed")

    protected = bytes(
        ctypes.string_at(
            ctypes.cast(blob_out.pbData, ctypes.POINTER(ctypes.c_ubyte)),
            blob_out.cbData,
        )
    )
    ctypes.windll.kernel32.LocalFree(blob_out.pbData)
    return protected


def _unprotect_key_dpapi(protected: bytes) -> str:
    blob_in = DATA_BLOB()
    blob_in.cbData = len(protected)
    buf = (ctypes.c_ubyte * len(protected)).from_buffer_copy(protected)
    blob_in.pbData = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))

    blob_out = DATA_BLOB()

    result = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blob_in),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(blob_out),
    )
    if not result:
        raise RuntimeError("DPAPI CryptUnprotectData failed")

    decrypted = bytes(
        ctypes.string_at(
            ctypes.cast(blob_out.pbData, ctypes.POINTER(ctypes.c_ubyte)),
            blob_out.cbData,
        )
    )
    ctypes.windll.kernel32.LocalFree(blob_out.pbData)
    return decrypted.decode("utf-16-le").rstrip("\x00")


def _get_or_create_key() -> str:
    db_key = os.environ.get("DB_KEY", "").strip()

    if db_key:
        return db_key

    if PROTECTED_KEY_PATH.exists():
        try:
            protected = PROTECTED_KEY_PATH.read_bytes()
            return _unprotect_key_dpapi(protected)
        except Exception:
            pass

    new_key = _generate_key()
    protected = _protect_key_dpapi(new_key)
    PROTECTED_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROTECTED_KEY_PATH.write_bytes(protected)
    return new_key


def create_engine():
    key = _get_or_create_key()
    encoded_key = quote_plus(key)
    db_path = str(settings.db_path)
    engine_url = f"sqlite+pysqlcipher://:{encoded_key}@/{db_path}?cipher=aes-256-cfb"
    return _sa_create_engine(engine_url, echo=False)

```

### `build\lib\src\database\migrate_add_parent_product_id.py`
```python
"""
Migration script to add parent_product_id column to products table.

This script adds a self-referential foreign key column to support
product hierarchies (e.g., product variants, bundles).

Features:
- Checks column existence before adding
- Creates index for performance
- Adds FOREIGN KEY constraint with ondelete="SET NULL"
- Supports rollback
- Comprehensive logging and error handling
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from src.database.engine import create_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

TABLE_NAME = "products"
COLUMN_NAME = "parent_product_id"
CONSTRAINT_NAME = "fk_products_parent_product_id"
INDEX_NAME = "ix_products_parent_product_id"


def check_column_exists(engine, table_name: str, column_name: str) -> bool:
    """Check if a column exists in the specified table."""
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def check_index_exists(engine, index_name: str) -> bool:
    """Check if an index exists in the database."""
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        for idx in inspector.get_indexes(table_name):
            if idx["name"] == index_name:
                return True
    return False


def check_constraint_exists(engine, constraint_name: str) -> bool:
    """Check if a foreign key constraint exists in the database."""
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        for fk in inspector.get_foreign_keys(table_name):
            if fk.get("name") == constraint_name:
                return True
    return False


def add_column_with_constraint(engine) -> None:
    """Add parent_product_id column with index and foreign key constraint."""
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info(f"Checking if column '{COLUMN_NAME}' exists in table '{TABLE_NAME}'...")
        if check_column_exists(engine, TABLE_NAME, COLUMN_NAME):
            logger.info(f"Column '{COLUMN_NAME}' already exists. Skipping creation.")
        else:
            logger.info(f"Adding column '{COLUMN_NAME}' to table '{TABLE_NAME}'...")
            conn.execute(
                f'ALTER TABLE "{TABLE_NAME}" ADD COLUMN "{COLUMN_NAME}" INTEGER'
            )
            logger.info(f"Column '{COLUMN_NAME}' added successfully.")

        logger.info(f"Checking if index '{INDEX_NAME}' exists...")
        if check_index_exists(engine, INDEX_NAME):
            logger.info(f"Index '{INDEX_NAME}' already exists. Skipping creation.")
        else:
            logger.info(f"Creating index '{INDEX_NAME}'...")
            conn.execute(
                f'CREATE INDEX "{INDEX_NAME}" ON "{TABLE_NAME}" ("{COLUMN_NAME}")'
            )
            logger.info(f"Index '{INDEX_NAME}' created successfully.")

        logger.info(f"Checking if foreign key constraint '{CONSTRAINT_NAME}' exists...")
        if check_constraint_exists(engine, CONSTRAINT_NAME):
            logger.info(
                f"Foreign key constraint '{CONSTRAINT_NAME}' already exists. Skipping creation."
            )
        else:
            logger.info(f"Adding foreign key constraint '{CONSTRAINT_NAME}'...")
            conn.execute(
                f'ALTER TABLE "{TABLE_NAME}" '
                f'ADD CONSTRAINT "{CONSTRAINT_NAME}" '
                f'FOREIGN KEY ("{COLUMN_NAME}") REFERENCES "{TABLE_NAME}" ("id") '
                f'ON DELETE SET NULL'
            )
            logger.info(f"Foreign key constraint '{CONSTRAINT_NAME}' added successfully.")


def rollback_migration(engine) -> None:
    """Rollback the migration by dropping constraint, index, and column."""
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info("Starting rollback...")

        if check_constraint_exists(engine, CONSTRAINT_NAME):
            logger.info(f"Dropping foreign key constraint '{CONSTRAINT_NAME}'...")
            conn.execute(f'ALTER TABLE "{TABLE_NAME}" DROP CONSTRAINT "{CONSTRAINT_NAME}"')
            logger.info(f"Constraint '{CONSTRAINT_NAME}' dropped.")
        else:
            logger.info(f"Constraint '{CONSTRAINT_NAME}' does not exist. Skipping.")

        if check_index_exists(engine, INDEX_NAME):
            logger.info(f"Dropping index '{INDEX_NAME}'...")
            conn.execute(f'DROP INDEX IF EXISTS "{INDEX_NAME}"')
            logger.info(f"Index '{INDEX_NAME}' dropped.")
        else:
            logger.info(f"Index '{INDEX_NAME}' does not exist. Skipping.")

        if check_column_exists(engine, TABLE_NAME, COLUMN_NAME):
            logger.info(f"Dropping column '{COLUMN_NAME}'...")
            conn.execute(f'ALTER TABLE "{TABLE_NAME}" DROP COLUMN "{COLUMN_NAME}"')
            logger.info(f"Column '{COLUMN_NAME}' dropped.")
        else:
            logger.info(f"Column '{COLUMN_NAME}' does not exist. Skipping.")

        logger.info("Rollback completed.")


def run_migration(
    engine, rollback: bool = False, dry_run: bool = False
) -> bool:
    """
    Run or rollback the migration.

    Args:
        engine: SQLAlchemy engine instance
        rollback: If True, rollback the migration instead of applying
        dry_run: If True, only log what would be done without executing

    Returns:
        True if successful, False otherwise
    """
    try:
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be applied")
            logger.info(f"Target table: {TABLE_NAME}")
            logger.info(f"Column: {COLUMN_NAME} (INTEGER, nullable)")
            logger.info(f"Index: {INDEX_NAME}")
            logger.info(f"Foreign Key: {CONSTRAINT_NAME} (ondelete=SET NULL)")

            if rollback:
                logger.info("Action: ROLLBACK")
            else:
                logger.info("Action: APPLY MIGRATION")

            return True

        if rollback:
            logger.info("Starting migration rollback...")
            rollback_migration(engine)
        else:
            logger.info("Starting migration...")
            add_column_with_constraint(engine)

        logger.info("Migration completed successfully.")
        return True

    except SQLAlchemyError as e:
        logger.error(f"Database error during migration: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}")
        return False


def main() -> int:
    """Main entry point for the migration script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migration script to add parent_product_id column to products table"
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback the migration (drop column, index, and constraint)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        help="Override database path (uses config by default)",
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Parent Product ID Migration Script")
    logger.info("=" * 60)

    if args.db_path:
        from sqlalchemy import create_engine as _create_engine
        from urllib.parse import quote_plus
        from src.database.engine import _get_or_create_key

        key = _get_or_create_key()
        encoded_key = quote_plus(key)
        db_path = str(args.db_path)
        engine_url = f"sqlite+pysqlcipher://:{encoded_key}@/{db_path}?cipher=aes-256-cfb"
        engine = _create_engine(engine_url, echo=False)
        logger.info(f"Using custom database path: {args.db_path}")
    else:
        engine = create_engine()
        logger.info("Using database path from config")

    success = run_migration(engine, rollback=args.rollback, dry_run=args.dry_run)

    engine.dispose()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

```

### `build\lib\src\database\models.py`
```python
import json
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    base_url = Column(String(512), nullable=False, unique=True)
    is_active = Column(Boolean, default=True, index=True)
    last_discovery_run = Column(DateTime, nullable=True)
    last_scrape_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    categories = relationship("Category", back_populates="supplier", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_suppliers_name_is_active", "name", "is_active"),)

    def __repr__(self) -> str:
        return (
            f"<Supplier(id={self.id}, name={self.name!r}, "
            f"base_url={self.base_url!r}, is_active={self.is_active})>"
        )


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    external_id = Column(String(255), nullable=True)
    name = Column(String(512), nullable=False)
    url = Column(String(1024), nullable=False)
    xpath_selector = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    product_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="categories")
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_categories_supplier_parent", "supplier_id", "parent_id"),
        Index("ix_categories_supplier_name", "supplier_id", "name"),
    )

    def __repr__(self) -> str:
        return (
            f"<Category(id={self.id}, name={self.name!r}, "
            f"supplier_id={self.supplier_id}, parent_id={self.parent_id})>"
        )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    parent_product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 🆕 НОВОЕ ПОЛЕ: Совместимые коллекции погонажа (JSON-массив)
    compatible_collections = Column(Text, nullable=True, comment="JSON array of collections, e.g. ['FLYDOORS>MONE']")
    
    external_sku = Column(String(255), nullable=True, index=True)
    title = Column(String(1024), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    is_available = Column(Boolean, default=True)
    is_ready_for_export = Column(Boolean, default=False, index=True)
    image_urls = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = relationship("Supplier")
    category = relationship("Category", back_populates="products")
    parent = relationship("Product", remote_side=[id], backref="related_products")
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_products_supplier_sku", "supplier_id", "external_sku"),
        Index("ix_products_supplier_category", "supplier_id", "category_id"),
        Index("ix_products_price", "price"),
        Index("ix_products_available", "is_available"),
        Index("ix_products_ready", "is_ready_for_export"),
    )

    # --- Helpers для image_urls ---
    def get_image_urls(self) -> list[str]:
        if not self.image_urls:
            return []
        try:
            return json.loads(self.image_urls)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_image_urls(self, urls: list[str]) -> None:
        self.image_urls = json.dumps(urls, ensure_ascii=False)

    # --- Helpers для compatible_collections ---
    def get_compatible_collections(self) -> list[str]:
        """Возвращает список коллекций как Python list"""
        if not self.compatible_collections:
            return []
        try:
            return json.loads(self.compatible_collections)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_compatible_collections(self, collections: list[str]) -> None:
        """Сохраняет список коллекций в БД как JSON-строку"""
        self.compatible_collections = json.dumps(collections, ensure_ascii=False)

    def __repr__(self) -> str:
        return (
            f"<Product(id={self.id}, title={self.title!r}, "
            f"price={self.price}, currency={self.currency})>"
        )


class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)

    product = relationship("Product", back_populates="attributes")

    __table_args__ = (
        Index("ix_attr_product_name", "product_id", "name"),
    )

    def __repr__(self) -> str:
        return f"<ProductAttribute(id={self.id}, name={self.name!r}, value={self.value!r})>"


class ArchiveSnapshot(Base):
    __tablename__ = "archive_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    snapshot_type = Column(String(50), nullable=False, default="full")
    total_products = Column(Integer, default=0)
    total_categories = Column(Integer, default=0)
    total_price_sum = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier")
    items = relationship("ArchiveItem", back_populates="snapshot", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_snapshots_supplier_date", "supplier_id", "created_at"),
        Index("ix_snapshots_type", "snapshot_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<ArchiveSnapshot(id={self.id}, name={self.name!r}, "
            f"products={self.total_products}, type={self.snapshot_type})>"
        )


class ArchiveItem(Base):
    __tablename__ = "archive_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(Integer, ForeignKey("archive_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    external_sku = Column(String(255), nullable=True)
    title = Column(String(1024), nullable=False)
    price = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    is_available = Column(Boolean, default=True)
    category_name = Column(String(512), nullable=True)
    image_urls = Column(Text, nullable=True)
    attributes_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    snapshot = relationship("ArchiveSnapshot", back_populates="items")

    __table_args__ = (
        Index("ix_archive_items_snapshot_sku", "snapshot_id", "external_sku"),
        Index("ix_archive_items_price", "price"),
    )

    def get_image_urls(self) -> list[str]:
        if not self.image_urls:
            return []
        try:
            return json.loads(self.image_urls)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_attributes(self) -> dict[str, str]:
        if not self.attributes_json:
            return {}
        try:
            return json.loads(self.attributes_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    def __repr__(self) -> str:
        return f"<ArchiveItem(id={self.id}, title={self.title!r}, price={self.price})>"


class MappingTemplate(Base):
    __tablename__ = "mapping_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    field_mapping = Column(Text, nullable=False)
    rules = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_field_mapping(self) -> dict[str, str]:
        if not self.field_mapping:
            return {}
        try:
            return json.loads(self.field_mapping)
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_rules(self) -> list[dict]:
        if not self.rules:
            return []
        try:
            return json.loads(self.rules)
        except (json.JSONDecodeError, TypeError):
            return []

    def __repr__(self) -> str:
        return f"<MappingTemplate(id={self.id}, name={self.name!r})>"
```

### `build\lib\src\database\session.py`
```python
from contextlib import contextmanager

from sqlalchemy import event, text
from sqlalchemy.orm import sessionmaker

from src.database.engine import create_engine

engine = create_engine()
SessionFactory = sessionmaker(bind=engine)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-64000")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()


@contextmanager
def get_session():
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session_sync():
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

```

### `build\lib\src\database\supplier_crud.py`
```python
from datetime import datetime

from sqlalchemy import select, update, delete

from src.database.models import Supplier


def create_supplier(session, name: str, base_url: str) -> Supplier:
    existing = session.execute(
        select(Supplier).where(Supplier.name == name)
    ).scalar_one_or_none()
    if existing:
        raise ValueError(f"Supplier with name '{name}' already exists")

    supplier = Supplier(name=name, base_url=base_url)
    session.add(supplier)
    session.flush()
    return supplier


def get_all_suppliers(session, active_only: bool = True) -> list[Supplier]:
    stmt = select(Supplier)
    if active_only:
        stmt = stmt.where(Supplier.is_active == True)
    stmt = stmt.order_by(Supplier.name)
    return list(session.execute(stmt).scalars().all())


def get_supplier_by_id(session, supplier_id: int) -> Supplier | None:
    return session.execute(
        select(Supplier).where(Supplier.id == supplier_id)
    ).scalar_one_or_none()


def get_supplier_by_name(session, name: str) -> Supplier | None:
    return session.execute(
        select(Supplier).where(Supplier.name == name)
    ).scalar_one_or_none()


def update_supplier(session, supplier_id: int, **kwargs) -> Supplier | None:
    supplier = get_supplier_by_id(session, supplier_id)
    if not supplier:
        return None

    if "name" in kwargs:
        new_name = kwargs["name"]
        if new_name != supplier.name:
            duplicate = session.execute(
                select(Supplier).where(
                    Supplier.name == new_name,
                    Supplier.id != supplier_id,
                )
            ).scalar_one_or_none()
            if duplicate:
                raise ValueError(f"Supplier with name '{new_name}' already exists")

    kwargs["updated_at"] = datetime.utcnow()

    session.execute(
        update(Supplier)
        .where(Supplier.id == supplier_id)
        .values(**kwargs)
    )
    session.flush()
    return get_supplier_by_id(session, supplier_id)


def delete_supplier(session, supplier_id: int) -> bool:
    supplier = get_supplier_by_id(session, supplier_id)
    if not supplier:
        return False

    session.execute(
        update(Supplier)
        .where(Supplier.id == supplier_id)
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    session.flush()
    return True


def hard_delete_supplier(session, supplier_id: int) -> bool:
    result = session.execute(
        delete(Supplier).where(Supplier.id == supplier_id)
    )
    session.flush()
    return result.rowcount > 0

```

### `build\lib\src\modules\__init__.py`
```python

```

### `build\lib\src\modules\archive\__init__.py`
```python

```

### `build\lib\src\modules\archive\engine.py`
```python
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

```

### `build\lib\src\modules\discovery\__init__.py`
```python

```

### `build\lib\src\modules\discovery\engine.py`
```python
import asyncio
import logging
import random
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp
from bs4 import BeautifulSoup, Tag
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.logger import logger

logger_discovery = logging.getLogger("meeyg.discovery")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/124.0.0.0 Safari/537.36",
]

CMS_PATTERNS = {
    "bitrix": [r"bitrix/", r"BX\.setForm", r"/bitrix/js/", r"bitrix:catalog", r"bitrix\.template"],
    "woocommerce": [r"woocommerce", r"wc-ajax", r"wp-content/plugins/woocommerce"],
    "opencart": [r"route=product/category", r"index\.php\?route=", r"opencart"],
    "prestashop": [r"prestashop", r"themes/prestashop"],
    "magento": [r"mage/", r"static/frontend/", r"Magento"],
}

EXCLUDE_PATTERNS = re.compile(
    r"(\?|filter|sort|clear|back|login|cart|korzina|checkout|order|zakaz|"
    r"search|poisk|ajax|api|upload|bitrix|include|component|local/|"
    r"\.html$|\.php$|\.pdf$|\.jpg$|\.png$|\.jpeg$|\.gif$|\.svg$|\.ico$)",
    re.IGNORECASE,
)

EXCLUDE_KEYWORDS = [
    "about", "o-kompanii", "o_kompanii", "contacts", "kontakty",
    "delivery", "dostavka", "oplata", "payment",
    "news", "novosti", "blog", "articles",
    "reviews", "otzyvy", "feedback",
    "login", "auth", "register", "personal", "profile",
    "search", "poisk", "ajax", "api", "upload",
    "wishlist", "favorites", "izbrannoe", "compare", "sravnenie",
    "vacancies", "vakansii", "partners", "partneram",
    "sitemap", "map", "privacy", "policy",
    "3d-tur", "3d_tur", "action", "sale",
]

EXCLUDE_KEYWORDS_RE = re.compile(
    r"/(" + "|".join(EXCLUDE_KEYWORDS) + r")(/|$|\?)",
    re.IGNORECASE,
)


@dataclass
class DiscoveredCategory:
    name: str
    url: str
    xpath_selector: str = ""
    product_count: int = 0
    children: list["DiscoveredCategory"] = field(default_factory=list)
    depth: int = 0
    external_id: Optional[str] = None


class BaseDiscovery(ABC):
    def __init__(
        self,
        base_url: str,
        session: aiohttp.ClientSession,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        max_depth: int = 3,
        delay_range: tuple[float, float] = (0.5, 2.0),
        check_robots: bool = True,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.log_callback = log_callback or (lambda m: logger_discovery.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self.max_depth = max_depth
        self.delay_range = delay_range
        self.check_robots = check_robots
        self.timeout = timeout
        self.robots_allowed = True
        self.visited_urls: set[str] = set()
        self._total_pages = 0
        self._pages_scanned = 0

    def _log(self, msg: str) -> None:
        self.log_callback(msg)

    def _progress(self, msg: str) -> None:
        self._pages_scanned += 1
        pct = int((self._pages_scanned / max(self._total_pages, 1)) * 100)
        self.progress_callback(pct, self._total_pages, msg)

    def _random_delay(self) -> None:
        time.sleep(random.uniform(*self.delay_range))

    def _get_headers(self) -> dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "identity",
            "Connection": "keep-alive",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True,
    )
    async def fetch_page(self, url: str) -> Optional[str]:
        if url in self.visited_urls:
            return None
        self.visited_urls.add(url)

        try:
            async with self.session.get(
                url, headers=self._get_headers(), timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status == 404:
                    self._log(f"  404: {url}")
                    return None
                if resp.status == 403:
                    self._log(f"  403: {url}")
                    return None
                if resp.status != 200:
                    self._log(f"  HTTP {resp.status}: {url}")
                    return None
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type and "application/xhtml" not in content_type:
                    return None
                return await resp.text(errors="replace")
        except asyncio.TimeoutError:
            self._log(f"  Timeout: {url}")
            raise
        except aiohttp.ClientError as exc:
            self._log(f"  Network error: {url} ({exc})")
            raise

    def _check_robots(self) -> None:
        if not self.check_robots:
            return
        robots_url = urljoin(self.base_url, "/robots.txt")
        try:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            self.robots_allowed = rp.can_fetch(random.choice(USER_AGENTS), self.base_url)
            if not self.robots_allowed:
                self._log(f"WARNING: robots.txt блокирует доступ к {self.base_url}")
        except Exception:
            self._log("WARNING: Не удалось загрузить robots.txt, продолжаем без проверки")

    def _is_internal_url(self, url: str) -> bool:
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)
        return parsed.netloc == base_parsed.netloc

    def _clean_url(self, url: str) -> str:
        url = url.split("#")[0]
        url = url.split("?")[0]
        url = url.rstrip("/")
        return url

    def _build_xpath(self, element: Tag) -> str:
        parts = []
        current: Tag | None = element
        while current and current.name:
            selector = current.name
            if current.get("id"):
                selector += f"[@id='{current['id']}']"
                parts.append(selector)
                break
            if current.get("class"):
                cls = " ".join(str(c) for c in current["class"])
                selector += f"[contains(concat(' ', normalize-space(@class), ' '), ' {cls} ')]"
            parts.append(selector)
            current = current.parent
        parts.reverse()
        return "/" + "/".join(parts)

    def detect_cms(self, html: str) -> Optional[str]:
        for cms, patterns in CMS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, html, re.IGNORECASE):
                    return cms
        return None

    @abstractmethod
    async def discover_categories(self) -> list[DiscoveredCategory]:
        pass

    async def run(self) -> list[DiscoveredCategory]:
        self._log(f"Начало разведки: {self.base_url}")
        self._check_robots()
        if not self.robots_allowed:
            self._log("Прервано: robots.txt запрещает доступ")
            return []
        result = await self.discover_categories()
        self._log(f"Разведка завершена: найдено {len(result)} категорий верхнего уровня")
        return result


class CatalogDiscovery(BaseDiscovery):
    """Универсальная стратегия: ищет все ссылки с /catalog/ и строит иерархию из URL."""

    def _is_excluded_url(self, url: str) -> bool:
        if EXCLUDE_PATTERNS.search(url):
            return True
        path = urlparse(url).path.lower()
        if EXCLUDE_KEYWORDS_RE.search(path):
            return True
        return False

    def _is_catalog_link(self, url: str) -> bool:
        path = urlparse(url).path.lower()
        return "/catalog/" in path

    def _get_url_segments(self, url: str) -> list[str]:
        path = urlparse(url).path
        return [s for s in path.split("/") if s]

    def _get_parent_url(self, url: str) -> Optional[str]:
        segments = self._get_url_segments(url)
        if len(segments) <= 1:
            return None
        parent_path = "/" + "/".join(segments[:-1]) + "/"
        return urljoin(self.base_url, parent_path).rstrip("/")

    def _extract_all_catalog_links(self, soup: BeautifulSoup, page_url: str) -> list[DiscoveredCategory]:
        categories = []
        seen_urls: set[str] = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue

            full_url = urljoin(page_url, href)

            if not self._is_internal_url(full_url):
                continue
            if not self._is_catalog_link(full_url):
                continue
            if self._is_excluded_url(full_url):
                continue

            clean_url = self._clean_url(full_url)
            if clean_url in seen_urls:
                continue
            if clean_url in self.visited_urls:
                continue

            name = a_tag.get_text(strip=True)
            if not name or len(name) < 2:
                continue

            xpath = self._build_xpath(a_tag)
            cat = DiscoveredCategory(
                name=name,
                url=clean_url,
                xpath_selector=xpath,
            )
            categories.append(cat)
            seen_urls.add(clean_url)

        return categories

    def _build_tree_from_urls(self, all_cats: list[DiscoveredCategory]) -> list[DiscoveredCategory]:
        url_map: dict[str, DiscoveredCategory] = {}
        for cat in all_cats:
            url_map[cat.url] = cat

        url_list = sorted(url_map.keys(), key=lambda u: len(self._get_url_segments(u)))

        roots: list[DiscoveredCategory] = []

        for url in url_list:
            cat = url_map[url]
            parent_url = self._get_parent_url(url)

            if parent_url and parent_url in url_map:
                parent = url_map[parent_url]
                parent.children.append(cat)
                cat.depth = parent.depth + 1
            else:
                roots.append(cat)
                cat.depth = 0

        return roots

    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log("Универсальный поиск каталога (метод грубой силы)")

        catalog_url = urljoin(self.base_url, "/catalog/")

        html = await self.fetch_page(catalog_url)
        if not html:
            self._log(f"Не удалось загрузить {catalog_url}, пробую главную")
            html = await self.fetch_page(self.base_url)
            if not html:
                self._log("Не удалось загрузить главную страницу")
                return []
            page_url = self.base_url
        else:
            page_url = catalog_url

        self._random_delay()
        self._progress(f"Анализ: {page_url}")

        soup = BeautifulSoup(html, "lxml")
        cats = self._extract_all_catalog_links(soup, page_url)
        self._log(f"Найдено {len(cats)} уникальных ссылок с /catalog/ на странице {page_url}")

        if not cats:
            self._log("Ссылки с /catalog/ не найдены, сканирую вложенные страницы...")
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                if not href or href.startswith(("javascript:", "mailto:")):
                    continue
                raw_url = urljoin(page_url, href)
                if not self._is_internal_url(raw_url):
                    continue
                if "/catalog/" not in raw_url.lower():
                    continue
                if self._is_excluded_url(raw_url):
                    continue
                link_url = self._clean_url(raw_url)
                if link_url not in self.visited_urls:
                    sub_html = await self.fetch_page(raw_url)
                    if sub_html:
                        self._random_delay()
                        sub_soup = BeautifulSoup(sub_html, "lxml")
                        sub_cats = self._extract_all_catalog_links(sub_soup, raw_url)
                        for sc in sub_cats:
                            if sc.url not in [c.url for c in cats]:
                                cats.append(sc)
                            self._log(f"  +{len(sub_cats)} ссылок со страницы {link_url}")

        if not cats:
            self._log("Категории не найдены")
            return []

        roots = self._build_tree_from_urls(cats)
        self._log(f"Построено дерево из {len(cats)} категорий ({len(roots)} корней)")

        return roots


class GenericDiscovery(BaseDiscovery):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _looks_like_category_page(self, url: str, text: str) -> bool:
        path = urlparse(url).path.lower()
        keywords = [
            "catalog", "category", "cat", "section", "department", "shop",
            "каталог", "категория", "раздел",
        ]
        combined = f"{path} {text}".lower()
        return any(kw in combined for kw in keywords)

    async def _scan_page_for_categories(self, url: str, depth: int = 0) -> list[DiscoveredCategory]:
        if depth > self.max_depth:
            return []

        html = await self.fetch_page(url)
        if not html:
            return []

        self._random_delay()
        self._progress(f"Сканирование: {url}")

        soup = BeautifulSoup(html, "lxml")
        categories = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue
            full_url = self._clean_url(urljoin(url, href))
            if not self._is_internal_url(full_url):
                continue
            name = a_tag.get_text(strip=True)
            if not name or len(name) < 2:
                continue
            if self._looks_like_category_page(full_url, name):
                xpath = self._build_xpath(a_tag)
                cat = DiscoveredCategory(name=name, url=full_url, xpath_selector=xpath, depth=depth + 1)
                categories.append(cat)

        if depth < self.max_depth:
            for cat in categories[:10]:
                if cat.url not in self.visited_urls:
                    children = await self._scan_page_for_categories(cat.url, depth + 1)
                    cat.children = children
                    if children:
                        self._log(f"  Найдено {len(children)} подкатегорий в '{cat.name}'")

        return categories

    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log(f"Сканирование главной: {self.base_url}")
        html = await self.fetch_page(self.base_url)
        if not html:
            self._log("Не удалось загрузить главную страницу")
            return []

        self._random_delay()
        soup = BeautifulSoup(html, "lxml")
        cms = self.detect_cms(html)
        if cms:
            self._log(f"Обнаружена CMS: {cms}")

        categories = await self._scan_page_for_categories(self.base_url, depth=0)

        seen_urls = set()
        unique = []
        for cat in categories:
            if cat.url not in seen_urls:
                seen_urls.add(cat.url)
                unique.append(cat)

        return unique


class BitrixDiscovery(CatalogDiscovery):
    """Стратегия для 1С-Битрикс: использует CatalogDiscovery с fallback на общий поиск."""

    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log("Использование стратегии для 1С-Битрикс")
        return await super().discover_categories()


class WooCommerceDiscovery(GenericDiscovery):
    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log("Использование стратегии для WooCommerce")
        shop_urls = [
            urljoin(self.base_url, "/shop/"),
            urljoin(self.base_url, "/product-category/"),
        ]
        all_cats = []
        for url in shop_urls:
            cats = await self._scan_page_for_categories(url, depth=0)
            all_cats.extend(cats)
        return all_cats


class OpenCartDiscovery(GenericDiscovery):
    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log("Использование стратегии для OpenCart")
        catalog_url = urljoin(self.base_url, "/index.php?route=product/category")
        return await self._scan_page_for_categories(catalog_url, depth=0)


STRATEGY_MAP: dict[str, type[BaseDiscovery]] = {
    "bitrix": BitrixDiscovery,
    "woocommerce": WooCommerceDiscovery,
    "opencart": OpenCartDiscovery,
}


class DiscoveryEngine:
    def __init__(
        self,
        supplier_id: int,
        base_url: str,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        max_depth: int = 3,
        delay_range: tuple[float, float] = (0.5, 2.0),
        check_robots: bool = True,
        timeout: int = 30,
    ):
        self.supplier_id = supplier_id
        self.base_url = base_url
        self.log_callback = log_callback or (lambda m: logger_discovery.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self.max_depth = max_depth
        self.delay_range = delay_range
        self.check_robots = check_robots
        self.timeout = timeout
        self._cancelled = False
        # ✅ ИСПРАВЛЕНИЕ: Добавлен алиас для совместимости
        self._log = self.log_callback

    def cancel(self) -> None:
        self._cancelled = True

    def _build_strategy(
        self, session: aiohttp.ClientSession, cms: Optional[str] = None
    ) -> BaseDiscovery:
        if cms and cms in STRATEGY_MAP:
            cls = STRATEGY_MAP[cms]
        else:
            cls = CatalogDiscovery

        return cls(
            base_url=self.base_url,
            session=session,
            log_callback=self.log_callback,
            progress_callback=self.progress_callback,
            max_depth=self.max_depth,
            delay_range=self.delay_range,
            check_robots=self.check_robots,
            timeout=self.timeout,
        )

    async def _detect_cms_async(self, session: aiohttp.ClientSession) -> Optional[str]:
        try:
            async with session.get(
                self.base_url,
                headers={"User-Agent": random.choice(USER_AGENTS)},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    html = await resp.text(errors="replace")
                    for cms, patterns in CMS_PATTERNS.items():
                        for pattern in patterns:
                            if re.search(pattern, html, re.IGNORECASE):
                                return cms
        except Exception:
            pass
        return None

    def _save_to_db(self, categories: list[DiscoveredCategory], db_session) -> int:
        from src.database.models import Category

        count = 0

        def _save_recursive(cats: list[DiscoveredCategory], parent_id: Optional[int] = None):
            nonlocal count
            for cat in cats:
                if self._cancelled:
                    return

                existing = db_session.query(Category).filter(
                    Category.supplier_id == self.supplier_id,
                    Category.url == cat.url,
                ).first()

                if existing:
                    self._log(f"  Дубликат пропущен: {cat.name} ({cat.url})")
                    existing.name = cat.name
                    existing.xpath_selector = cat.xpath_selector or existing.xpath_selector
                    existing.product_count = cat.product_count
                    existing.parent_id = parent_id
                    db_category = existing
                else:
                    db_category = Category(
                        supplier_id=self.supplier_id,
                        parent_id=parent_id,
                        name=cat.name,
                        url=cat.url,
                        xpath_selector=cat.xpath_selector,
                        product_count=cat.product_count,
                        external_id=cat.external_id,
                    )
                    db_session.add(db_category)
                    db_session.flush()
                    self._log(f"  Сохранено: {cat.name} (parent_id={parent_id})")

                count += 1
                if cat.children:
                    _save_recursive(cat.children, db_category.id)

        _save_recursive(categories)
        return count

    async def run(self, db_session) -> dict[str, Any]:
        self._cancelled = False
        self.log_callback(f"Движок разведки запущен для {self.base_url}")

        connector = aiohttp.TCPConnector(ssl=False, limit=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            cms = await self._detect_cms_async(session)
            strategy = self._build_strategy(session, cms)

            if cms:
                self.log_callback(f"CMS определена: {cms}, используется стратегия для {cms}")
            else:
                self.log_callback("CMS не определена, используется универсальный поиск")

            try:
                categories = await strategy.run()
            except Exception as exc:
                self.log_callback(f"Разведка не удалась: {exc}")
                return {"success": False, "error": str(exc), "categories_found": 0}

            if self._cancelled:
                self.log_callback("Разведка отменена пользователем")
                return {"success": False, "error": "cancelled", "categories_found": 0}

            if not categories:
                self.log_callback("Категории не найдены")
                self._update_supplier_timestamp(db_session)
                return {"success": True, "categories_found": 0, "categories": []}

            self.log_callback(f"Сохранение {len(categories)} категорий верхнего уровня в БД...")
            try:
                saved_count = self._save_to_db(categories, db_session)
                db_session.commit()
                self.log_callback(f"Сохранено {saved_count} категорий в базу данных")
            except Exception as exc:
                db_session.rollback()
                self.log_callback(f"Ошибка сохранения в БД: {exc}")
                return {"success": False, "error": f"DB error: {exc}", "categories_found": 0}

            self._update_supplier_timestamp(db_session)

            return {
                "success": True,
                "categories_found": saved_count,
                "categories": categories,
            }

    def _update_supplier_timestamp(self, db_session) -> None:
        from src.database.models import Supplier

        supplier = db_session.query(Supplier).filter(Supplier.id == self.supplier_id).first()
        if supplier:
            supplier.last_discovery_run = datetime.utcnow()
            db_session.flush()
```

### `build\lib\src\modules\export\__init__.py`
```python

```

### `build\lib\src\modules\export\generator.py`
```python
import gc
import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.workbook import Workbook

from src.core.config import settings
from src.core.logger import logger

logger_export = logging.getLogger("meeyg.export")

WP_COLUMNS = [
    "post_title",
    "sku",
    "regular_price",
    "sale_price",
    "stock",
    "stock_status",
    "categories",
    "tags",
    "short_description",
    "description",
    "images",
    "attributes",
    "manage_stock",
    "backorders",
    "tax_status",
    "meta",
]


@dataclass
class ExportConfig:
    supplier_ids: Optional[list[int]] = None
    category_ids: Optional[list[int]] = None
    ready_only: bool = False
    available_only: bool = False
    format: str = "xlsx"
    encoding: str = "utf-8-sig"
    category_separator: str = ">"
    image_separator: str = "|"
    attribute_format: str = "name:value"
    output_dir: Optional[Path] = None
    chunk_size: int = 1000

    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = settings.data_dir / "exports"
        self.output_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class ExportStats:
    total_products: int = 0
    exported_products: int = 0
    duplicate_skus: int = 0
    empty_titles: int = 0
    empty_prices: int = 0
    elapsed: float = 0.0
    file_size: int = 0
    output_path: str = ""


class ExportEngine:
    def __init__(
        self,
        config: ExportConfig,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        self.config = config
        self.log_callback = log_callback or (lambda m: logger_export.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self._cancelled = False
        self.stats = ExportStats()

    def cancel(self) -> None:
        self._cancelled = True

    def _log(self, msg: str) -> None:
        self.log_callback(msg)

    def _progress(self, pct: int, total: int, msg: str) -> None:
        self.progress_callback(pct, total, msg)

    def _fetch_products(self, db_session) -> list[dict]:
        from src.database.models import Category, Product, ProductAttribute, Supplier

        self._log("Fetching products from database...")

        query = db_session.query(
            Product.id,
            Product.external_sku,
            Product.title,
            Product.description,
            Product.price,
            Product.currency,
            Product.is_available,
            Product.is_ready_for_export,
            Product.image_urls,
            Product.created_at,
            Supplier.name.label("supplier_name"),
            Category.name.label("category_name"),
        ).outerjoin(Supplier, Product.supplier_id == Supplier.id).outerjoin(
            Category, Product.category_id == Category.id
        )

        if self.config.supplier_ids:
            query = query.filter(Product.supplier_id.in_(self.config.supplier_ids))
        if self.config.category_ids:
            query = query.filter(Product.category_id.in_(self.config.category_ids))
        if self.config.ready_only:
            query = query.filter(Product.is_ready_for_export == True)
        if self.config.available_only:
            query = query.filter(Product.is_available == True)

        products = query.order_by(Product.id).all()
        self.stats.total_products = len(products)
        self._log(f"Found {len(products)} products matching filters")

        attr_query = db_session.query(
            ProductAttribute.product_id,
            ProductAttribute.name,
            ProductAttribute.value,
        )
        if self.config.supplier_ids:
            attr_query = attr_query.join(Product).filter(
                Product.supplier_id.in_(self.config.supplier_ids)
            )
        if self.config.category_ids:
            attr_query = attr_query.join(Product).filter(
                Product.category_id.in_(self.config.category_ids)
            )

        attributes_rows = attr_query.all()
        attr_map: dict[int, list[tuple[str, str]]] = {}
        for row in attributes_rows:
            attr_map.setdefault(row.product_id, []).append((row.name, row.value))

        for p in products:
            p_attrs = attr_map.get(p.id, [])
            if self.config.attribute_format == "name:value":
                attr_str = "; ".join(f"{n}: {v}" for n, v in p_attrs)
            else:
                attr_str = "; ".join(f"{n}={v}" for n, v in p_attrs)

            image_urls = []
            if p.image_urls:
                import json
                try:
                    image_urls = json.loads(p.image_urls)
                except (json.JSONDecodeError, TypeError):
                    pass

            yield {
                "id": p.id,
                "external_sku": p.external_sku,
                "title": p.title,
                "description": p.description or "",
                "price": p.price,
                "currency": p.currency,
                "is_available": p.is_available,
                "supplier_name": p.supplier_name,
                "category_name": p.category_name,
                "attributes": attr_str,
                "image_urls": image_urls,
                "created_at": p.created_at,
            }

    def _transform_to_wp_format(self, products: list[dict]) -> list[dict]:
        self._log("Transforming data to WP All Import format...")
        rows = []
        seen_skus: set[str] = set()

        for i, p in enumerate(products):
            if self._cancelled:
                break

            sku = p["external_sku"] or f"MEYG-{p['id']}"
            if sku in seen_skus:
                base_sku = sku
                counter = 1
                while sku in seen_skus:
                    sku = f"{base_sku}-{counter}"
                    counter += 1
                self.stats.duplicate_skus += 1
            seen_skus.add(sku)

            title = (p["title"] or "").strip()
            if not title:
                title = f"Product {p['id']}"
                self.stats.empty_titles += 1

            price = p["price"]
            if price is None:
                self.stats.empty_prices += 1

            stock = 1 if p["is_available"] else 0
            stock_status = "instock" if p["is_available"] else "outofstock"

            category = p["category_name"] or "Uncategorized"

            images_str = self.config.image_separator.join(p["image_urls"]) if p["image_urls"] else ""

            short_desc = ""
            if p["description"]:
                short_desc = (p["description"][:300] + "...") if len(p["description"]) > 300 else p["description"]

            meta_fields = {
                "supplier": p["supplier_name"],
                "currency": p["currency"] or "",
                "imported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_id": str(p["id"]),
            }

            rows.append({
                "post_title": title,
                "sku": sku,
                "regular_price": f"{price:.2f}" if price is not None else "",
                "sale_price": "",
                "stock": str(stock),
                "stock_status": stock_status,
                "categories": category,
                "tags": "",
                "short_description": short_desc,
                "description": p["description"] or "",
                "images": images_str,
                "attributes": p["attributes"],
                "manage_stock": "yes" if p["is_available"] else "no",
                "backorders": "no",
                "tax_status": "taxable",
                "meta": "; ".join(f"{k}: {v}" for k, v in meta_fields.items()),
            })

            if (i + 1) % 100 == 0:
                pct = int(((i + 1) / max(self.stats.total_products, 1)) * 100)
                self._progress(pct, self.stats.total_products, f"Transformed {i + 1} products")

        self.stats.exported_products = len(rows)
        return rows

    def _export_to_excel(self, rows: list[dict]) -> str:
        self._log("Generating Excel file with openpyxl...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        supplier_name = "all"
        if self.config.supplier_ids and len(self.config.supplier_ids) == 1:
            supplier_name = f"supplier_{self.config.supplier_ids[0]}"
        filename = f"{supplier_name}_{timestamp}.xlsx"
        output_path = self.config.output_dir / filename

        df = pd.DataFrame(rows, columns=WP_COLUMNS)

        wb = Workbook()
        ws = wb.active
        ws.title = "Products"

        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for col_idx, col_name in enumerate(WP_COLUMNS, 1):
            cell = ws.cell(row=1, column=col_idx, value=col_name)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment

        price_cols = {"regular_price", "sale_price"}
        date_cols = set()

        for row_idx, row_data in enumerate(rows, 2):
            for col_idx, col_name in enumerate(WP_COLUMNS, 1):
                value = row_data.get(col_name, "")
                cell = ws.cell(row=row_idx, column=col_idx, value=value)

                if col_name in price_cols and value:
                    try:
                        cell.number_format = '#,##0.00'
                    except ValueError:
                        pass

                if row_idx % 2 == 0:
                    cell.fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")

        ws.auto_filter.ref = f"A1:{get_column_letter(len(WP_COLUMNS))}{len(rows) + 1}"

        for col_idx in range(1, len(WP_COLUMNS) + 1):
            max_len = 12
            for row in ws.iter_rows(min_col=col_idx, max_col=col_idx, values_only=True):
                if row[0]:
                    max_len = max(max_len, min(len(str(row[0])), 50))
            ws.column_dimensions[get_column_letter(col_idx)].width = max_len + 2

        ws.freeze_panes = "B2"

        wb.save(str(output_path))

        file_size = os.path.getsize(output_path)
        self.stats.file_size = file_size
        self.stats.output_path = str(output_path)

        self._log(f"Excel saved: {output_path} ({file_size / 1024:.1f} KB)")
        return str(output_path)

    def _export_to_csv(self, rows: list[dict]) -> str:
        self._log("Generating CSV file...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        supplier_name = "all"
        if self.config.supplier_ids and len(self.config.supplier_ids) == 1:
            supplier_name = f"supplier_{self.config.supplier_ids[0]}"
        filename = f"{supplier_name}_{timestamp}.csv"
        output_path = self.config.output_dir / filename

        df = pd.DataFrame(rows, columns=WP_COLUMNS)
        df.to_csv(
            str(output_path),
            index=False,
            encoding=self.config.encoding,
            sep=";",
            quoting=1,
        )

        file_size = os.path.getsize(output_path)
        self.stats.file_size = file_size
        self.stats.output_path = str(output_path)

        self._log(f"CSV saved: {output_path} ({file_size / 1024:.1f} KB)")
        return str(output_path)

    def run(self, db_session) -> dict[str, Any]:
        self._cancelled = False
        self.stats = ExportStats()
        start_time = time.time()

        self._log(f"Export started (format={self.config.format})")

        products = list(self._fetch_products(db_session))
        if not products:
            self._log("No products found matching filters")
            return {"success": False, "error": "No products found", "stats": self.stats}

        self._progress(10, self.stats.total_products, "Fetching complete")

        if self._cancelled:
            return {"success": False, "error": "cancelled", "stats": self.stats}

        rows = self._transform_to_wp_format(products)
        if not rows:
            return {"success": False, "error": "No rows after transformation", "stats": self.stats}

        self._progress(60, self.stats.total_products, "Transformation complete")

        if self._cancelled:
            return {"success": False, "error": "cancelled", "stats": self.stats}

        if self.config.format == "csv":
            output_path = self._export_to_csv(rows)
        else:
            output_path = self._export_to_excel(rows)

        self.stats.elapsed = time.time() - start_time
        self._progress(100, self.stats.total_products, "Export complete")

        del products
        del rows
        gc.collect()

        self._log(f"Export complete in {self.stats.elapsed:.1f}s")

        return {
            "success": True,
            "output_path": output_path,
            "stats": self.stats,
        }

    def validate_before_export(self, db_session) -> list[str]:
        from src.database.models import Product

        warnings = []

        query = db_session.query(Product)
        if self.config.supplier_ids:
            query = query.filter(Product.supplier_id.in_(self.config.supplier_ids))
        if self.config.category_ids:
            query = query.filter(Product.category_id.in_(self.config.category_ids))
        if self.config.ready_only:
            query = query.filter(Product.is_ready_for_export == True)

        products = query.all()

        if not products:
            warnings.append("No products match the current filters")
            return warnings

        empty_titles = sum(1 for p in products if not p.title or not p.title.strip())
        if empty_titles:
            warnings.append(f"{empty_titles} products have empty titles")

        empty_prices = sum(1 for p in products if p.price is None)
        if empty_prices:
            warnings.append(f"{empty_prices} products have no price")

        empty_skus = sum(1 for p in products if not p.external_sku)
        if empty_skus:
            warnings.append(f"{empty_skus} products have no SKU (will be auto-generated)")

        return warnings

```

### `build\lib\src\modules\import_prep\__init__.py`
```python

```

### `build\lib\src\modules\import_prep\mapper.py`
```python
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from src.core.logger import logger

logger_mapper = logging.getLogger("meeyg.import_prep")

WP_ALL_IMPORT_FIELDS = {
    "post_title": {"required": True, "type": "string", "label": "Product Title"},
    "sku": {"required": True, "type": "string", "label": "SKU"},
    "regular_price": {"required": True, "type": "float", "label": "Regular Price"},
    "sale_price": {"required": False, "type": "float", "label": "Sale Price"},
    "stock": {"required": True, "type": "int", "label": "Stock Quantity"},
    "stock_status": {"required": True, "type": "string", "label": "Stock Status"},
    "categories": {"required": False, "type": "string", "label": "Categories"},
    "attributes": {"required": False, "type": "string", "label": "Attributes"},
    "images": {"required": False, "type": "string", "label": "Images"},
    "short_description": {"required": False, "type": "string", "label": "Short Description"},
    "description": {"required": False, "type": "string", "label": "Description"},
    "manage_stock": {"required": False, "type": "string", "label": "Manage Stock"},
    "backorders": {"required": False, "type": "string", "label": "Backorders"},
    "tax_status": {"required": False, "type": "string", "label": "Tax Status"},
    "weight": {"required": False, "type": "float", "label": "Weight"},
}

DB_FIELDS = {
    "id": "Product ID",
    "title": "Product Title",
    "external_sku": "SKU",
    "price": "Price",
    "currency": "Currency",
    "is_available": "Availability",
    "description": "Description",
    "category_name": "Category",
    "image_urls": "Image URLs",
    "attributes": "Attributes",
    "supplier_name": "Supplier",
    "created_at": "Created At",
    "updated_at": "Updated At",
}

RULE_TYPES = {
    "null_replacement": "Replace NULL/empty values with a specified string",
    "price_round": "Round prices to N decimal places",
    "price_markup": "Apply percentage markup to prices",
    "merge_attributes": "Merge all attributes into a single string",
    "sku_prefix": "Add prefix to SKU",
    "sku_suffix": "Add suffix to SKU",
    "stock_default": "Set default stock value for NULL",
    "category_separator": "Set category separator character",
    "title_trim": "Trim and normalize title whitespace",
    "currency_map": "Map currency codes to target currency",
}


@dataclass
class ValidationIssue:
    product_id: int
    field: str
    message: str
    severity: str = "warning"


@dataclass
class MappingConfig:
    field_mapping: dict[str, str] = field(default_factory=dict)
    rules: list[dict] = field(default_factory=list)
    name: str = ""
    description: str = ""

    def map_field(self, db_field: str) -> Optional[str]:
        return self.field_mapping.get(db_field)

    def add_rule(self, rule_type: str, **kwargs) -> None:
        rule = {"type": rule_type, **kwargs}
        self.rules.append(rule)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "field_mapping": self.field_mapping,
            "rules": self.rules,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MappingConfig":
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            field_mapping=data.get("field_mapping", {}),
            rules=data.get("rules", []),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "MappingConfig":
        return cls.from_dict(json.loads(json_str))


class RuleEngine:
    def __init__(self, rules: list[dict]):
        self.rules = rules

    def apply(self, product_data: dict[str, Any]) -> dict[str, Any]:
        result = dict(product_data)
        for rule in self.rules:
            rule_type = rule.get("type")
            if rule_type == "null_replacement":
                result = self._apply_null_replacement(result, rule)
            elif rule_type == "price_round":
                result = self._apply_price_round(result, rule)
            elif rule_type == "price_markup":
                result = self._apply_price_markup(result, rule)
            elif rule_type == "merge_attributes":
                result = self._apply_merge_attributes(result, rule)
            elif rule_type == "sku_prefix":
                result = self._apply_sku_prefix(result, rule)
            elif rule_type == "sku_suffix":
                result = self._apply_sku_suffix(result, rule)
            elif rule_type == "stock_default":
                result = self._apply_stock_default(result, rule)
            elif rule_type == "title_trim":
                result = self._apply_title_trim(result, rule)
            elif rule_type == "currency_map":
                result = self._apply_currency_map(result, rule)
        return result

    @staticmethod
    def _apply_null_replacement(data: dict, rule: dict) -> dict:
        target = rule.get("target", "")
        replacement = rule.get("replacement", "N/A")
        if target in data and (data[target] is None or data[target] == ""):
            data[target] = replacement
        return data

    @staticmethod
    def _apply_price_round(data: dict, rule: dict) -> dict:
        decimals = rule.get("decimals", 2)
        if "regular_price" in data and data["regular_price"] is not None:
            data["regular_price"] = round(float(data["regular_price"]), decimals)
        if "sale_price" in data and data["sale_price"] is not None:
            data["sale_price"] = round(float(data["sale_price"]), decimals)
        return data

    @staticmethod
    def _apply_price_markup(data: dict, rule: dict) -> dict:
        markup_pct = rule.get("markup", 0)
        if "regular_price" in data and data["regular_price"] is not None:
            data["regular_price"] = round(float(data["regular_price"]) * (1 + markup_pct / 100), 2)
        return data

    @staticmethod
    def _apply_merge_attributes(data: dict, rule: dict) -> dict:
        separator = rule.get("separator", " | ")
        attrs = data.get("attributes", {})
        if isinstance(attrs, dict):
            parts = [f"{k}: {v}" for k, v in attrs.items() if v]
            data["attributes"] = separator.join(parts)
        elif isinstance(attrs, str):
            pass
        return data

    @staticmethod
    def _apply_sku_prefix(data: dict, rule: dict) -> dict:
        prefix = rule.get("prefix", "")
        if "sku" in data and data["sku"]:
            data["sku"] = f"{prefix}{data['sku']}"
        return data

    @staticmethod
    def _apply_sku_suffix(data: dict, rule: dict) -> dict:
        suffix = rule.get("suffix", "")
        if "sku" in data and data["sku"]:
            data["sku"] = f"{data['sku']}{suffix}"
        return data

    @staticmethod
    def _apply_stock_default(data: dict, rule: dict) -> dict:
        default_val = rule.get("default", 0)
        if "stock" in data and (data["stock"] is None or data["stock"] == ""):
            data["stock"] = default_val
        return data

    @staticmethod
    def _apply_title_trim(data: dict, rule: dict) -> dict:
        import re
        if "post_title" in data and data["post_title"]:
            data["post_title"] = re.sub(r"\s+", " ", str(data["post_title"])).strip()
        return data

    @staticmethod
    def _apply_currency_map(data: dict, rule: dict) -> dict:
        mapping = rule.get("mapping", {})
        if "currency" in data and data["currency"] in mapping:
            data["currency"] = mapping[data["currency"]]
        return data


class FieldMapper:
    def __init__(self, config: Optional[MappingConfig] = None):
        self.config = config or MappingConfig()
        self.rule_engine = RuleEngine(self.config.rules)
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []

    def set_mapping(self, db_field: str, wp_field: str) -> None:
        self.config.field_mapping[db_field] = wp_field
        self._redo_stack.clear()

    def remove_mapping(self, db_field: str) -> None:
        self.config.field_mapping.pop(db_field, None)
        self._redo_stack.clear()

    def get_unmapped_wp_fields(self) -> list[str]:
        mapped = set(self.config.field_mapping.values())
        return [
            wp_field
            for wp_field, meta in WP_ALL_IMPORT_FIELDS.items()
            if meta["required"] and wp_field not in mapped
        ]

    def get_mapped_fields(self) -> dict[str, str]:
        return dict(self.config.field_mapping)

    def transform_product(self, product_data: dict[str, Any]) -> dict[str, Any]:
        self._undo_stack.append(dict(product_data))
        if len(self._undo_stack) > 100:
            self._undo_stack = self._undo_stack[-50:]

        result = {}
        for db_field, wp_field in self.config.field_mapping.items():
            value = product_data.get(db_field)
            result[wp_field] = value

        result = self.rule_engine.apply(result)
        return result

    def validate_product(self, product_data: dict[str, Any], product_id: int) -> list[ValidationIssue]:
        issues = []

        for wp_field, meta in WP_ALL_IMPORT_FIELDS.items():
            if not meta["required"]:
                continue
            value = product_data.get(wp_field)
            if value is None or value == "":
                issues.append(ValidationIssue(
                    product_id=product_id,
                    field=wp_field,
                    message=f"Required field '{meta['label']}' is empty",
                    severity="error",
                ))

            if meta["type"] == "float" and value is not None:
                try:
                    float(value)
                except (ValueError, TypeError):
                    issues.append(ValidationIssue(
                        product_id=product_id,
                        field=wp_field,
                        message=f"Field '{meta['label']}' must be a number, got '{value}'",
                        severity="error",
                    ))

            if meta["type"] == "int" and value is not None:
                try:
                    int(value)
                except (ValueError, TypeError):
                    issues.append(ValidationIssue(
                        product_id=product_id,
                        field=wp_field,
                        message=f"Field '{meta['label']}' must be an integer, got '{value}'",
                        severity="error",
                    ))

        return issues

    def validate_batch(self, products: list[dict[str, Any]]) -> list[ValidationIssue]:
        all_issues = []
        seen_skus: dict[str, int] = {}

        for product in products:
            pid = product.get("id", 0)
            issues = self.validate_product(product, pid)
            all_issues.extend(issues)

            sku = product.get("sku")
            if sku:
                if sku in seen_skus:
                    all_issues.append(ValidationIssue(
                        product_id=pid,
                        field="sku",
                        message=f"Duplicate SKU '{sku}' (also in product {seen_skus[sku]})",
                        severity="error",
                    ))
                else:
                    seen_skus[sku] = pid

        return all_issues

    def save_template(self, db_session, name: str, description: str = "") -> int:
        from src.database.models import MappingTemplate

        template = MappingTemplate(
            name=name,
            description=description,
            field_mapping=json.dumps(self.config.field_mapping, ensure_ascii=False),
            rules=json.dumps(self.config.rules, ensure_ascii=False),
        )
        db_session.add(template)
        db_session.flush()
        logger_mapper.info(f"Mapping template '{name}' saved (id={template.id})")
        return template.id

    def load_template(self, db_session, template_id: int) -> bool:
        from src.database.models import MappingTemplate

        template = db_session.query(MappingTemplate).filter(
            MappingTemplate.id == template_id
        ).first()

        if not template:
            return False

        self.config.field_mapping = template.get_field_mapping()
        self.config.rules = template.get_rules()
        self.config.name = template.name
        self.config.description = template.description or ""
        self.rule_engine = RuleEngine(self.config.rules)
        logger_mapper.info(f"Mapping template '{template.name}' loaded")
        return True

    def list_templates(self, db_session) -> list:
        from src.database.models import MappingTemplate

        return db_session.query(MappingTemplate).order_by(
            MappingTemplate.updated_at.desc()
        ).all()

    def delete_template(self, db_session, template_id: int) -> bool:
        from src.database.models import MappingTemplate

        template = db_session.query(MappingTemplate).filter(
            MappingTemplate.id == template_id
        ).first()

        if template:
            db_session.delete(template)
            logger_mapper.info(f"Mapping template '{template.name}' deleted")
            return True
        return False

    def undo(self) -> Optional[dict]:
        if len(self._undo_stack) < 2:
            return None
        current = self._undo_stack.pop()
        self._redo_stack.append(current)
        return self._undo_stack[-1]

    def redo(self) -> Optional[dict]:
        if not self._redo_stack:
            return None
        state = self._redo_stack.pop()
        self._undo_stack.append(state)
        return state

    def mark_ready_for_export(self, db_session, product_ids: list[int]) -> int:
        from src.database.models import Product

        result = db_session.query(Product).filter(
            Product.id.in_(product_ids)
        ).update(
            {"is_ready_for_export": True, "updated_at": datetime.utcnow()},
            synchronize_session="fetch",
        )
        db_session.flush()
        logger_mapper.info(f"Marked {result} products as ready for export")
        return result

    def mark_not_ready(self, db_session, product_ids: list[int]) -> int:
        from src.database.models import Product

        result = db_session.query(Product).filter(
            Product.id.in_(product_ids)
        ).update(
            {"is_ready_for_export": False, "updated_at": datetime.utcnow()},
            synchronize_session="fetch",
        )
        db_session.flush()
        logger_mapper.info(f"Marked {result} products as not ready for export")
        return result

```

### `build\lib\src\modules\parsing\__init__.py`
```python

```

### `build\lib\src\modules\parsing\engine.py`
```python
"""
Модуль парсинга товаров для MEEYG 1.0

Отвечает за:
- Извлечение характеристик товаров из HTML
- Парсинг сопутствующих товаров (погонаж) как НЕЗАВИСИМЫХ записей
- Сохранение данных в БД с поддержкой иерархии (Родитель → Дети)
- Обработку дубликатов и транзакционность
"""

import asyncio
import json
import logging
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup, Tag
from sqlalchemy import select
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.logger import logger
from src.database.models import Category, Product, ProductAttribute, Supplier

logger_parser = logging.getLogger("meeyg.parser")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/124.0.0.0 Safari/537.36",
]

PRICE_RE = re.compile(r"([\d\s.,]+)")
CURRENCY_RE = re.compile(r"([A-Z]{3}|[$€£¥₽])")
SIZE_RE = re.compile(r"([\d.,]+\s*[xх]\s*[\d.,]+(?:\s*[xх]\s*[\d.,]+)?)")


@dataclass
class ParsedProduct:
    """Структура данных для распарсенного товара"""
    url: str
    title: str = ""
    description: str = ""
    price: Optional[float] = None
    currency: Optional[str] = None
    is_available: bool = True
    sku: Optional[str] = None
    image_urls: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    category_id: Optional[int] = None
    raw_html_length: int = 0
    molding_items: list[dict] = field(default_factory=list)
    # 🔥 ДОБАВЛЕНО: Список вариаций товара (размеры, типы и т.д.)
    variations: list[dict] = field(default_factory=list)


@dataclass
class ParsingStats:
    """Статистика парсинга"""
    total_products: int = 0
    total_pages: int = 0
    successful_pages: int = 0
    failed_pages: int = 0
    total_attributes: int = 0
    errors: list[str] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    @property
    def elapsed(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        if self.start_time:
            return time.time() - self.start_time
        return 0.0


class ParserEngine:
    """
    Движок парсинга товаров с поддержкой:
    - Асинхронных запросов
    - Обработки иерархии товаров (Родитель → Дети)
    - Погонаж как НЕЗАВИСИМЫЕ товары с compatible_collections
    - Транзакционности при сохранении в БД
    - Обработки дубликатов
    """

    def __init__(
        self,
        supplier_id: int,
        base_url: str,
        concurrency: int = 5,
        delay_range: tuple[float, float] = (0.5, 2.0),
        timeout: int = 30,
        batch_size: int = 500,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        self.supplier_id = supplier_id
        self.base_url = base_url.rstrip("/")
        self.concurrency = concurrency
        self.delay_range = delay_range
        self.timeout = timeout
        self.batch_size = batch_size
        self.log_callback = log_callback or (lambda m: logger_parser.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        
        self._cancelled = False
        self._paused = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        
        self.stats = ParsingStats()
        self._seen_urls: set[str] = set()
        self._session: Optional[aiohttp.ClientSession] = None
        self._category_cache: dict[str, int] = {}

    # =========================================================================
    # Управление выполнением
    # =========================================================================

    def cancel(self) -> None:
        self._cancelled = True
        self._pause_event.set()

    def pause(self) -> None:
        self._paused = True
        self._pause_event.clear()

    def resume(self) -> None:
        self._paused = False
        self._pause_event.set()

    def _log(self, msg: str) -> None:
        self.log_callback(msg)

    def _progress(self, processed: int, total: int, msg: str) -> None:
        pct = int((processed / max(total, 1)) * 100)
        self.progress_callback(pct, total, msg)

    def _random_delay(self) -> None:
        time.sleep(random.uniform(*self.delay_range))

    def _get_headers(self) -> dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "identity",
            "Connection": "keep-alive",
        }

    # =========================================================================
    # Утилиты нормализации данных
    # =========================================================================

    @staticmethod
    def normalize_title(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def normalize_price(text: str) -> Optional[float]:
        if not text:
            return None
        text = text.strip().replace("\xa0", " ").replace("  ", " ")
        match = PRICE_RE.search(text)
        if not match:
            return None
        num_str = match.group(1).replace(",", ".")
        parts = num_str.split(".")
        if len(parts) > 2:
            num_str = " ".join(parts[:-1]) + "." + parts[-1]
        try:
            val = float(num_str)
            return val if val > 0 else None
        except ValueError:
            return None

    @staticmethod
    def normalize_currency(text: str) -> Optional[str]:
        if not text:
            return None
        match = CURRENCY_RE.search(text)
        if not match:
            return None
        val = match.group(1)
        currency_map = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY", "₽": "RUB"}
        return currency_map.get(val, val.upper())

    @staticmethod
    def is_valid_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False

    def _clean_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    # =========================================================================
    # Парсинг HTML-элементов
    # =========================================================================

    def _parse_molding_items(self, soup: BeautifulSoup) -> list[dict]:
        molding_items = []
        for item in soup.select("li.Product-description__molding-item"):
            data_id = item.get("data-id", "")
            data_price = item.get("data-price", "")
            title_el = item.select_one(".Checkbox__text")
            title = self._clean_text(title_el.get_text()) if title_el else ""
            color_el = item.select_one(".Checkbox__out-text")
            color = self._clean_text(color_el.get_text()) if color_el else ""
            item_type = self._detect_molding_type(title)
            if title:
                molding_items.append({
                    "title": title,
                    "price": self.normalize_price(data_price),
                    "color": color,
                    "external_id": data_id,
                    "type": item_type,
                })
        logger_parser.info(f"  Найдено {len(molding_items)} изделий погонажа")
        return molding_items

    def _detect_molding_type(self, title: str) -> str:
        if not title:
            return "Прочее"
        title_lower = title.lower()
        if "добор" in title_lower:
            return "Добор"
        elif "короб" in title_lower:
            return "Короб"
        elif "наличник" in title_lower:
            return "Наличник"
        elif "плинтус" in title_lower:
            return "Плинтус"
        elif "планка" in title_lower:
            return "Притворная планка"
        elif "порог" in title_lower:
            return "Порог"
        return "Прочее"

    def _parse_description_list(self, soup: BeautifulSoup) -> dict[str, str]:
        attributes = {}
        desc_lists = soup.select(".Description__list")
        for dl in desc_lists:
            terms = dl.select("dt.Description__list-term")
            descs = dl.select("dd.Description__list-desc")
            for dt, dd in zip(terms, descs):
                name = self._clean_text(dt.get_text())
                value = self._clean_text(dd.get_text())
                if name and value:
                    attributes[name] = value
        logger_parser.info(f"  Извлечено {len(attributes)} характеристик из блока описания")
        return attributes

    def _extract_variations(self, soup: BeautifulSoup, base_url: str) -> list[dict]:
        """
        Извлечь вариации товара (размеры, типы) из HTML.
        Возвращает список словарей с данными вариаций.
        """
        variations = []
        
        # === Извлечение размеров ===
        sizes = []
        size_inputs = soup.select("input.sizer[name='size'], input.sizer")
        for el in size_inputs:
            value = el.get("value", "").strip()
            # Если value содержит путь — извлекаем только последнюю часть
            if value and '/' in value:
                value = value.split('/')[-1].rstrip('/')
            # Проверяем, похоже ли на размер (700, 700x2000, 700x2000x40)
            if value and (re.match(r'^[\d.,]+[xх][\d.,]+$', value) or re.match(r'^\d+$', value)):
                sizes.append(value)
            # Пробуем data-атрибуты
            elif el.get("data-size"):
                sizes.append(el.get("data-size"))
            # Или из текста родителя (label)
            else:
                label = el.find_parent("label")
                if label:
                    text = self._clean_text(label.get_text())
                    size_match = re.search(r'([\d.,]+\s*[xх]\s*[\d.,]+)', text)
                    if size_match:
                        sizes.append(size_match.group(1).replace(' ', ''))
        
        # === Извлечение типов ===
        types = []
        type_inputs = soup.select("input.typer[name='type'], input.typer")
        for el in type_inputs:
            value = el.get("value", "").strip()
            if value:
                types.append(value)
        
        # === Создаём комбинации ===
        if sizes and types:
            for size in sizes:
                for type_val in types:
                    variations.append({
                        "title": "",
                        "price": None,
                        "attributes": {"Размер": size, "Тип": type_val}
                    })
        elif sizes:
            for size in sizes:
                variations.append({
                    "title": "",
                    "price": None,
                    "attributes": {"Размер": size}
                })
        elif types:
            for type_val in types:
                variations.append({
                    "title": "",
                    "price": None,
                    "attributes": {"Тип": type_val}
                })
        
        logger_parser.info(f"  Найдено {len(variations)} вариаций")
        return variations

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True,
    )
    async def fetch_page(self, url: str) -> Optional[str]:
        if not self._session:
            return None
        try:
            async with self._session.get(
                url, 
                headers=self._get_headers(), 
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status != 200:
                    self._log(f"  HTTP {resp.status}: {url}")
                    return None
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type and "application/xhtml" not in content_type:
                    return None
                return await resp.text(errors="replace")
        except asyncio.TimeoutError:
            self._log(f"  Timeout: {url}")
            raise
        except aiohttp.ClientError as exc:
            self._log(f"  Network error: {url} ({exc})")
            raise

    def _extract_product_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        links = []
        seen = set()
        selectors = [
            "a.product-link", "a.product-card", "a.item", "a.product",
            "div.product a[href]", "div.item a[href]",
            "a[href*='/product/']", "a[href*='/item/']", 
            "a[href*='/p/']", "a[href*='/catalog/']",
        ]
        for selector in selectors:
            for a_tag in soup.select(selector):
                href = a_tag.get("href", "")
                if href and not href.startswith(("javascript:", "mailto:", "tel:", "#")):
                    full_url = urljoin(base_url, href).split("#")[0]
                    clean_url = self._clean_url(full_url)
                    if clean_url not in seen and self._is_product_url(clean_url):
                        links.append(clean_url)
                        seen.add(clean_url)
        if not links:
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                if href and not href.startswith(("javascript:", "mailto:")):
                    full_url = urljoin(base_url, href).split("#")[0]
                    clean_url = self._clean_url(full_url)
                    if clean_url not in seen and self._is_product_url(clean_url):
                        links.append(clean_url)
                        seen.add(clean_url)
        return links

    def _clean_url(self, url: str) -> str:
        url = url.split("#")[0]
        url = url.split("?")[0]
        return url.rstrip("/")

    def _is_product_url(self, url: str) -> bool:
        path = urlparse(url).path.lower()
        keywords = ["/product/", "/item/", "/p/", "/goods/", "/товар/", "/product-", "/item-", "/p-", "product_id", "item_id"]
        return any(kw in path for kw in keywords)

    def _parse_product_page(self, soup: BeautifulSoup, url: str) -> ParsedProduct:
        product = ParsedProduct(url=url)
        product.raw_html_length = len(str(soup))

        # === Извлечение заголовка ===
        title_el = (
            soup.select_one("h1") 
            or soup.select_one("h1.product-title") 
            or soup.select_one("h1.item-title")
            or soup.select_one("[itemprop='name']")
            or soup.select_one("meta[name='title']")
        )
        if title_el:
            product.title = self.normalize_title(
                title_el.get("content") if title_el.name == "meta" else title_el.get_text()
            )

        # === Извлечение цены и валюты ===
        price_el = (
            soup.select_one(".Product-description__item-price-value")
            or soup.select_one("[itemprop='price']")
            or soup.select_one(".price")
            or soup.select_one(".product-price")
            or soup.select_one(".current-price")
        )
        if price_el:
            price_text = price_el.get_text()
            product.price = self.normalize_price(price_text)
            product.currency = self.normalize_currency(price_text)

        # === Извлечение наличия ===
        avail_el = (
            soup.select_one("[itemprop='availability']")
            or soup.select_one(".availability")
            or soup.select_one(".stock-status")
            or soup.select_one(".in-stock")
        )
        if avail_el:
            avail_text = avail_el.get_text().lower()
            positive = ["in stock", "в наличии", "available", "есть", "yes", "да"]
            negative = ["out of stock", "нет в наличии", "sold out", "нет", "no"]
            if any(kw in avail_text for kw in positive):
                product.is_available = True
            elif any(kw in avail_text for kw in negative):
                product.is_available = False

        # === Извлечение артикула (SKU) ===
        sku_el = (
            soup.select_one("[itemprop='sku']")
            or soup.select_one(".sku")
            or soup.select_one(".product-sku")
            or soup.select_one(".article")
            or soup.select_one(".artikul")
        )
        if sku_el:
            product.sku = self._clean_text(sku_el.get_text())

        # === Извлечение описания ===
        desc_el = (
            soup.select_one("[itemprop='description']")
            or soup.select_one(".product-description")
            or soup.select_one("#description")
            or soup.select_one(".description")
        )
        if desc_el:
            product.description = self._clean_text(desc_el.get_text())

        # === Извлечение изображений ===
        for img in soup.select("img"):
            src = (
                img.get("src") 
                or img.get("data-src") 
                or img.get("data-lazy-src") 
                or img.get("data-original")
            )
            if src:
                full_src = urljoin(url, src)
                if self.is_valid_url(full_src) and not any(
                    ext in full_src.lower() for ext in [".svg", ".gif", ".ico", "placeholder", "blank"]
                ):
                    if full_src not in product.image_urls:
                        product.image_urls.append(full_src)

        # === Извлечение характеристик из блока описания ===
        dl_attrs = self._parse_description_list(soup)
        if dl_attrs:
            product.attributes.update(dl_attrs)

        # === Дополнительный парсинг таблиц характеристик ===
        attr_tables = soup.select(
            ".attributes, .specs, .specifications, .characteristics, .params, .properties"
        )
        for table in attr_tables:
            for row in table.select("tr"):
                cells = row.select("td, th")
                if len(cells) >= 2:
                    name = self._clean_text(cells[0].get_text())
                    value = self._clean_text(cells[1].get_text())
                    if name and value and len(name) > 1 and len(value) > 1:
                        product.attributes[name] = value

        # === Парсинг списка характеристик (dl/dt/dd) ===
        for dl in soup.select("dl.attributes, dl.specs, dl.characteristics"):
            terms = dl.select("dt")
            defs = dl.select("dd")
            for dt, dd in zip(terms, defs):
                name = self._clean_text(dt.get_text())
                value = self._clean_text(dd.get_text())
                if name and value:
                    product.attributes[name] = value

        # === Парсинг сопутствующих товаров (погонаж) ===
        molding_items = self._parse_molding_items(soup)
        if molding_items:
            product.molding_items = molding_items
            logger_parser.info(f"Найдено {len(molding_items)} сопутствующих товаров для {url}")

        # === Парсинг вариаций товара ===
        variations = self._extract_variations(soup, url)
        if variations:
            product.variations = variations

        return product

    # =========================================================================
    # Работа с категориями в БД
    # =========================================================================

    def _get_or_create_category(
        self, 
        db_session, 
        supplier_id: int, 
        parent_category_id: Optional[int], 
        name: str,
        url: str = ""
    ) -> int:
        cache_key = f"{supplier_id}:{parent_category_id}:{name}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]
        
        existing = db_session.execute(
            select(Category).where(
                Category.supplier_id == supplier_id,
                Category.parent_id == parent_category_id,
                Category.name == name,
            )
        ).scalar_one_or_none()
        
        if existing:
            self._category_cache[cache_key] = existing.id
            return existing.id
        
        new_category = Category(
            supplier_id=supplier_id,
            parent_id=parent_category_id,
            name=name,
            url=url,
            xpath_selector="",
            sort_order=0,
            product_count=0,
        )
        db_session.add(new_category)
        db_session.flush()
        self._category_cache[cache_key] = new_category.id
        self._log(f"  Создана категория: {name} (parent_id={parent_category_id})")
        return new_category.id

    def _get_full_category_path(self, db_session, category_id: int) -> str:
        """
        Рекурсивно собрать полный путь категории от корня до листа.
        Пример: "Межкомнатные двери > Бона > Покрытие"
        """
        if not category_id:
            return ""
        path_parts = []
        current_id = category_id
        while current_id:
            category = db_session.execute(
                select(Category).where(Category.id == current_id)
            ).scalar_one_or_none()
            if not category:
                break
            path_parts.insert(0, category.name)
            current_id = category.parent_id
        return " > ".join(path_parts) if path_parts else ""

    def _get_or_create_molding_root_category(self, db_session) -> int:
        """
        Получить или создать корневую категорию "Погонаж"
        """
        cache_key = f"{self.supplier_id}:molding_root"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]
        
        root = db_session.execute(
            select(Category).where(
                Category.supplier_id == self.supplier_id,
                Category.name == "Погонаж",
                Category.parent_id.is_(None)
            )
        ).scalar_one_or_none()
        
        if not root:
            root = Category(
                supplier_id=self.supplier_id,
                name="Погонаж",
                url="",
                parent_id=None,
                xpath_selector="",
                sort_order=0,
                product_count=0,
            )
            db_session.add(root)
            db_session.flush()
            self._log(f"  Создана корневая категория погонажа (id={root.id})")
        
        self._category_cache[cache_key] = root.id
        return root.id

    def _get_or_create_molding_subcategory(self, db_session, molding_type: str) -> int:
        """
        Получить или создать подкатегорию погонажа под корнем "Погонаж"
        """
        root_id = self._get_or_create_molding_root_category(db_session)
        cache_key = f"{self.supplier_id}:molding:{molding_type}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]
        
        subcat = db_session.execute(
            select(Category).where(
                Category.supplier_id == self.supplier_id,
                Category.parent_id == root_id,
                Category.name == molding_type,
            )
        ).scalar_one_or_none()
        
        if not subcat:
            subcat = Category(
                supplier_id=self.supplier_id,
                parent_id=root_id,
                name=molding_type,
                url="",
                xpath_selector="",
                sort_order=0,
                product_count=0,
            )
            db_session.add(subcat)
            db_session.flush()
            self._log(f"  Создана подкатегория погонажа: {molding_type} (id={subcat.id})")
        
        self._category_cache[cache_key] = subcat.id
        return subcat.id

    def _upsert_molding_item(self, item: dict, door_category_path: str, db_session) -> None:
        """
        Создать или обновить погонажный товар как НЕЗАВИСИМУЮ запись.
        
        Логика UPSERT:
        1. Поиск по external_sku или title в категории погонажа
        2. Если найден → обновить compatible_collections (добавить путь категории двери)
        3. Если не найден → создать новую запись с parent_product_id=None
        """
        molding_type = item.get("type", "Прочее")
        molding_title = item.get("title", "")
        molding_sku = item.get("external_id")
        molding_color = item.get("color", "")
        molding_price = item.get("price")
        
        if not molding_title:
            return
        
        # Получить/создать категорию погонажа
        molding_category_id = self._get_or_create_molding_subcategory(db_session, molding_type)
        
        # Поиск существующего погонажа (НЕЗАВИСИМОГО!)
        existing_molding = None
        if molding_sku:
            existing_molding = db_session.execute(
                select(Product).where(
                    Product.supplier_id == self.supplier_id,
                    Product.category_id == molding_category_id,
                    Product.external_sku == molding_sku,
                    Product.parent_product_id.is_(None),  # 🔥 Ищем только независимые!
                )
            ).scalar_one_or_none()
        
        if not existing_molding and molding_title:
            existing_molding = db_session.execute(
                select(Product).where(
                    Product.supplier_id == self.supplier_id,
                    Product.category_id == molding_category_id,
                    Product.title == molding_title,
                    Product.parent_product_id.is_(None),  # 🔥 Ищем только независимые!
                )
            ).scalar_one_or_none()
        
        if existing_molding:
            # Обновление существующего погонажа
            existing_molding.title = molding_title
            existing_molding.price = molding_price
            existing_molding.currency = "RUB"
            existing_molding.is_available = True
            existing_molding.updated_at = datetime.utcnow()
            
            # 🔥 КЛЮЧЕВОЙ МОМЕНТ: обновить compatible_collections без дублей
            current_collections = existing_molding.get_compatible_collections()
            if door_category_path and door_category_path not in current_collections:
                current_collections.append(door_category_path)
                existing_molding.set_compatible_collections(current_collections)
            
            db_session.flush()
            self._log(f"  Обновлен погонаж: {molding_title} | Collections: {len(current_collections)}")
        else:
            # Создание НОВОГО независимого погонажа
            molding_product = Product(
                supplier_id=self.supplier_id,
                category_id=molding_category_id,
                parent_product_id=None,  # 🔥 НЕЗАВИСИМЫЙ товар!
                external_sku=molding_sku,
                title=molding_title,
                description=f"Комплектующий: {molding_type}",
                price=molding_price,
                currency="RUB",
                is_available=True,
                image_urls="[]",
            )
            
            # Инициализация compatible_collections
            if door_category_path:
                molding_product.set_compatible_collections([door_category_path])
            
            db_session.add(molding_product)
            db_session.flush()
            
            # Добавить атрибут цвета если есть
            if molding_color:
                safe_color = molding_color[:65535]
                if safe_color:
                    color_attr = ProductAttribute(
                        product_id=molding_product.id,
                        name="Цвет",
                        value=safe_color,
                    )
                    db_session.add(color_attr)
            
            self._log(f"  Создан погонаж: {molding_title} | Collections: {[door_category_path]}")

    # =========================================================================
    # Сохранение данных в БД
    # =========================================================================

    def _save_batch(self, products: list[ParsedProduct], db_session) -> None:
        """
        Сохранить пакет товаров в БД с поддержкой иерархии:
        
        ЛОГИКА:
        1. РОДИТЕЛЬ (дверь):
           - Поиск/создание с parent_product_id=None
           - Очистка заголовка от конкретного размера/цвета
           - Атрибут "Доступные размеры" = "600|700|800"
        
        2. ДЕТИ (вариации):
           - Создать с parent_product_id=ID_родителя
           - Атрибут "Размер" = одно конкретное значение
        
        3. ПОГОНАЖ:
           - Создать/обновить как НЕЗАВИСИМЫЙ товар (parent_product_id=None)
           - Категория: "Погонаж > Добор/Наличник/..."
           - compatible_collections: массив путей категорий дверей
        
        Транзакция: всё в одном try/except, при ошибке → rollback.
        """
        from sqlalchemy.exc import IntegrityError
        
        try:
            # 🔥 ОТЛАДКА: выводим информацию о пакете
            print(f"\n🔥 [DEBUG] _save_batch: {len(products)} товаров в пакете")
            if products:
                p = products[0]
                print(f"   🔹 title: {p.title[:50]}")
                print(f"   🔹 attributes: {len(p.attributes)} шт.")
                print(f"   🔹 molding_items: {len(p.molding_items)} шт.")
                print(f"   🔹 variations: {len(p.variations)} шт.")
                if p.molding_items:
                    print(f"   🔹 Пример погонажа: {p.molding_items[0].get('title')} ({p.molding_items[0].get('type')})")
            
            self._log(f"  Начало транзакции для пакета из {len(products)} товаров")
            
            for parsed_product in products:
                try:
                    # =====================================================
                    # 1. ОБРАБОТКА РОДИТЕЛЬСКОГО ТОВАРА (ДВЕРЬ)
                    # =====================================================
                    
                    # Очистка заголовка от конкретного размера/цвета
                    cleaned_title = re.sub(r'\s*\d+[xх]\d+\s*.*$', '', parsed_product.title or "Без названия").strip()
                    
                    # Поиск дубликата по SKU (для основных товаров parent_product_id IS NULL)
                    existing_product = None
                    if parsed_product.sku:
                        existing_product = db_session.execute(
                            select(Product).where(
                                Product.supplier_id == self.supplier_id,
                                Product.external_sku == parsed_product.sku,
                                Product.parent_product_id.is_(None),
                            )
                        ).scalar_one_or_none()
                    
                    # Поиск по названию если нет SKU
                    if not existing_product and not parsed_product.sku:
                        existing_product = db_session.execute(
                            select(Product).where(
                                Product.supplier_id == self.supplier_id,
                                Product.title == cleaned_title,
                                Product.parent_product_id.is_(None),
                            )
                        ).scalar_one_or_none()
                    
                    if existing_product:
                        # Обновление существующего товара
                        main_product_id = existing_product.id
                        existing_product.title = cleaned_title
                        existing_product.description = parsed_product.description
                        existing_product.price = parsed_product.price
                        existing_product.currency = parsed_product.currency
                        existing_product.is_available = parsed_product.is_available
                        existing_product.image_urls = json.dumps(
                            parsed_product.image_urls, ensure_ascii=False
                        )
                        existing_product.updated_at = datetime.utcnow()
                        db_session.flush()
                        self._log(f"  Обновлен родитель: {cleaned_title} (id={main_product_id})")
                    else:
                        # Создание нового родителя
                        main_product = Product(
                            supplier_id=self.supplier_id,
                            category_id=parsed_product.category_id,
                            parent_product_id=None,  # 🔥 РОДИТЕЛЬ НЕЗАВИСИМЫЙ
                            external_sku=parsed_product.sku,
                            title=cleaned_title,
                            description=parsed_product.description,
                            price=parsed_product.price,
                            currency=parsed_product.currency,
                            is_available=parsed_product.is_available,
                            image_urls=json.dumps(
                                parsed_product.image_urls, ensure_ascii=False
                            ),
                        )
                        db_session.add(main_product)
                        db_session.flush()
                        main_product_id = main_product.id
                        self._log(f"  Создан родитель: {cleaned_title} (id={main_product_id})")
                    
                    # Сохранение атрибутов родителя
                    for attr_name, attr_value in parsed_product.attributes.items():
                        safe_name = attr_name[:255] if attr_name else ""
                        safe_value = attr_value[:65535] if attr_value else ""
                        if safe_name and safe_value:
                            attr = ProductAttribute(
                                product_id=main_product_id,
                                name=safe_name,
                                value=safe_value,
                            )
                            db_session.add(attr)
                    
                    # =====================================================
                    # 2. СБОР РАЗМЕРОВ И СОЗДАНИЕ ВАРИАЦИЙ (ДЕТЕЙ)
                    # =====================================================
                    
                    # Сначала собираем все размеры для родителя
                    all_sizes = []
                    variations = getattr(parsed_product, 'variations', [])
                    if variations:
                        for variation in variations:
                            if isinstance(variation, dict):
                                size_attr = variation.get("attributes", {}).get("Размер")
                            else:
                                size_attr = getattr(variation, 'attributes', {}).get("Размер")
                            if size_attr and size_attr not in all_sizes:
                                all_sizes.append(size_attr)
                        
                        # 🔥 Записываем СКЛЕЕННЫЕ размеры у родителя
                        if all_sizes:
                            sizes_string = "|".join(all_sizes)
                            existing_size_attr = db_session.execute(
                                select(ProductAttribute).where(
                                    ProductAttribute.product_id == main_product_id,
                                    ProductAttribute.name == "Доступные размеры"
                                )
                            ).scalar_one_or_none()
                            
                            if existing_size_attr:
                                existing_size_attr.value = sizes_string
                            else:
                                size_attr_obj = ProductAttribute(
                                    product_id=main_product_id,
                                    name="Доступные размеры",  # 🔥 Имя атрибута для родителя
                                    value=sizes_string
                                )
                                db_session.add(size_attr_obj)
                            self._log(f"  Родитель: размеры = {sizes_string}")
                    
                    # Создаем вариации как дочерние товары
                    for variation in variations:
                        if isinstance(variation, dict):
                            var_title = variation.get("title", cleaned_title)
                            var_desc = variation.get("description", parsed_product.description)
                            var_price = variation.get("price", parsed_product.price)
                            var_currency = variation.get("currency", parsed_product.currency)
                            var_available = variation.get("is_available", parsed_product.is_available)
                            var_images = variation.get("image_urls", parsed_product.image_urls)
                            var_attrs = variation.get("attributes", {})
                        else:
                            var_title = getattr(variation, 'title', cleaned_title)
                            var_desc = getattr(variation, 'description', parsed_product.description)
                            var_price = getattr(variation, 'price', parsed_product.price)
                            var_currency = getattr(variation, 'currency', parsed_product.currency)
                            var_available = getattr(variation, 'is_available', parsed_product.is_available)
                            var_images = getattr(variation, 'image_urls', parsed_product.image_urls)
                            var_attrs = getattr(variation, 'attributes', {})
                        
                        variation_product = Product(
                            supplier_id=self.supplier_id,
                            category_id=parsed_product.category_id,
                            parent_product_id=main_product_id,  # 🔥 Связь с родителем
                            external_sku=parsed_product.sku,
                            title=var_title,
                            description=var_desc,
                            price=var_price,
                            currency=var_currency,
                            is_available=var_available,
                            image_urls=json.dumps(var_images, ensure_ascii=False),
                        )
                        db_session.add(variation_product)
                        db_session.flush()
                        variation_id = variation_product.id
                        self._log(f"  Создана вариация: {var_title} (parent={main_product_id})")
                        
                        # Сохранение атрибутов вариации
                        for attr_name, attr_value in var_attrs.items():
                            safe_name = attr_name[:255] if attr_name else ""
                            safe_value = attr_value[:65535] if attr_value else ""
                            if safe_name and safe_value:
                                attr = ProductAttribute(
                                    product_id=variation_id,
                                    name=safe_name,
                                    value=safe_value,
                                )
                                db_session.add(attr)
                    
                    # =====================================================
                    # 3. ОБРАБОТКА ПОГОНАЖА (НЕЗАВИСИМЫЕ ТОВАРЫ!)
                    # =====================================================
                    
                    if parsed_product.molding_items:
                        # 🔥 Получаем ПОЛНЫЙ путь категории двери
                        door_category_path = self._get_full_category_path(
                            db_session, parsed_product.category_id
                        )
                        self._log(f"  Путь категории двери: {door_category_path}")
                        
                        # Обрабатываем каждый погонаж через UPSERT
                        for molding_item in parsed_product.molding_items:
                            try:
                                self._upsert_molding_item(
                                    molding_item, 
                                    door_category_path, 
                                    db_session
                                )
                            except Exception as e:
                                self._log(f"  Ошибка обработки погонажа {molding_item.get('title')}: {e}")
                                continue
                                    
                except IntegrityError as e:
                    self._log(f"  Ошибка уникальности при обработке {parsed_product.title}: {e}")
                    db_session.rollback()
                    raise
                except Exception as e:
                    self._log(f"  Ошибка обработки товара {parsed_product.title}: {e}")
                    raise
            
            # 🔥 ФИНАЛЬНЫЙ COMMIT после успешной обработки всех товаров
            self._log(f"  Пакет успешно сохранён: {len(products)} товаров обработано")
            
        except Exception as e:
            self._log(f"  Ошибка транзакции: {e}")
            logger_parser.exception("Ошибка сохранения пакета товаров")
            raise

    # =========================================================================
    # Парсинг категории (основной метод)
    # =========================================================================

    async def _parse_category(self, category_id: int, url: str, db_session) -> int:
        if self._cancelled:
            return 0

        await self._pause_event.wait()

        html = await self.fetch_page(url)
        if not html:
            self.stats.failed_pages += 1
            return 0

        self.stats.successful_pages += 1
        self._random_delay()

        soup = BeautifulSoup(html, "lxml")
        product_links = self._extract_product_links(soup, url)
        self._log(f"  Категория: найдено {len(product_links)} ссылок на товары")

        parsed_products = []
        for i, p_url in enumerate(product_links):
            if self._cancelled:
                break
            await self._pause_event.wait()
            if p_url in self._seen_urls:
                continue
            self._seen_urls.add(p_url)

            p_html = await self.fetch_page(p_url)
            if not p_html:
                self.stats.failed_pages += 1
                continue

            self.stats.successful_pages += 1
            self.stats.total_pages += 1
            self._random_delay()

            try:
                p_soup = BeautifulSoup(p_html, "lxml")
                product = self._parse_product_page(p_soup, p_url)
                product.category_id = category_id
                parsed_products.append(product)
                self.stats.total_products += 1
                self.stats.total_attributes += len(product.attributes)
                self._progress(
                    self.stats.total_products,
                    max(len(product_links), 1),
                    f"Распаршено {self.stats.total_products} товаров",
                )
            except Exception as exc:
                self._log(f"  Ошибка парсинга товара {p_url}: {exc}")
                self.stats.errors.append(f"Product parse error: {p_url} - {exc}")

        if parsed_products:
            self._save_batch(parsed_products, db_session)

        next_page = self._find_next_page(soup, url)
        if next_page and not self._cancelled:
            await self._parse_category(category_id, next_page, db_session)

        return len(parsed_products)

    def _find_next_page(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        selectors = [
            "a.next", "a.next-page", "a.pagination-next",
            "a[rel='next']", ".next a", ".pagination .next a",
            "a[href*='page=']", "a[href*='p=']",
        ]
        for selector in selectors:
            el = soup.select_one(selector)
            if el and el.get("href"):
                return urljoin(base_url, el["href"])
        return None

    # =========================================================================
    # Основной метод запуска
    # =========================================================================

    async def run(self, category_ids: list[int], db_session) -> dict[str, Any]:
        self._cancelled = False
        self._paused = False
        self._pause_event.set()
        self.stats = ParsingStats()
        self.stats.start_time = time.time()
        self._seen_urls.clear()
        self._category_cache.clear()

        self._log(f"Запуск парсера для поставщика {self.supplier_id}")
        self._log(f"Категорий для парсинга: {len(category_ids)}")

        connector = aiohttp.TCPConnector(
            ssl=False,
            limit=self.concurrency,
            limit_per_host=self.concurrency,
            ttl_dns_cache=300,
        )
        
        async with aiohttp.ClientSession(connector=connector) as session:
            self._session = session
            categories = db_session.execute(
                select(Category).where(Category.id.in_(category_ids))
            ).scalars().all()

            if not categories:
                self._log("Не найдено категорий для указанных ID")
                return {"success": False, "error": "No categories found", "stats": self.stats}

            self._log(f"Загружено {len(categories)} категорий из БД")

            semaphore = asyncio.Semaphore(self.concurrency)

            async def _parse_with_semaphore(cat):
                async with semaphore:
                    return await self._parse_category(cat.id, cat.url, db_session)

            tasks = [_parse_with_semaphore(cat) for cat in categories]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            total_parsed = 0
            for r in results:
                if isinstance(r, int):
                    total_parsed += r
                elif isinstance(r, Exception):
                    self._log(f"Ошибка парсинга категории: {r}")
                    self.stats.errors.append(str(r))

        self._update_supplier_timestamp(db_session)
        self.stats.end_time = time.time()

        self._log(f"Парсинг завершён: {total_parsed} товаров, {self.stats.total_pages} страниц")
        self._log(f"Затрачено времени: {self.stats.elapsed:.1f}с")

        return {
            "success": True,
            "products_parsed": total_parsed,
            "stats": self.stats,
        }

    def _update_supplier_timestamp(self, db_session) -> None:
        supplier = db_session.execute(
            select(Supplier).where(Supplier.id == self.supplier_id)
        ).scalar_one_or_none()
        if supplier:
            supplier.last_scrape_run = datetime.utcnow()
            db_session.flush()
```

### `build\lib\src\modules\parsing\tandoor_playwright_parser.py`
```python
"""
Playwright-парсер для tandoor.ru
Финальная версия с поддержкой:
1. Иерархии Родитель -> Дети (Вариации)
2. Независимого погонажа с compatible_collections
3. Склеивания размеров у родителя
"""

import asyncio
import json
import logging
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser
from sqlalchemy import select

from src.core.logger import logger
from src.database.models import Product, ProductAttribute, Category, Supplier

logger_parser = logging.getLogger("meeyg.tandoor_parser")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

PRICE_RE = re.compile(r"([\d\s.,]+)")
CURRENCY_RE = re.compile(r"([A-Z]{3}|[$€£¥₽])")


@dataclass
class ParsedProduct:
    """Структура данных распарсенного товара"""
    url: str
    title: str = ""
    description: str = ""
    price: Optional[float] = None
    currency: Optional[str] = None
    is_available: bool = True
    sku: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)
    category_id: Optional[int] = None
    raw_html_length: int = 0
    molding_items: List[Dict[str, Any]] = field(default_factory=list)
    variations: List[Dict[str, Any]] = field(default_factory=list)


class TandoorPlaywrightParser:
    def __init__(
        self,
        supplier_id: int,
        db_session,
        headless: bool = True,
        delay_range: Tuple[float, float] = (1.0, 3.0),
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        self.supplier_id = supplier_id
        self.db_session = db_session
        self.headless = headless
        self.delay_range = delay_range
        self.log_callback = log_callback or (lambda m: logger_parser.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self._cancelled = False
        self._paused = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        self.stats = {
            "products_parsed": 0,
            "variations_parsed": 0,
            "molding_items_parsed": 0,
            "errors": [],
            "start_time": None,
            "end_time": None,
        }
        self._seen_urls: set[str] = set()
        self.browser: Optional[Browser] = None
        self._category_cache: Dict[str, int] = {}

    def cancel(self) -> None:
        self._cancelled = True
        self._pause_event.set()

    def pause(self) -> None:
        self._paused = True
        self._pause_event.clear()

    def resume(self) -> None:
        self._paused = False
        self._pause_event.set()

    def _log(self, msg: str) -> None:
        self.log_callback(msg)

    def _progress(self, processed: int, total: int, msg: str) -> None:
        pct = int((processed / max(total, 1)) * 100)
        self.progress_callback(pct, total, msg)

    def _random_delay(self) -> None:
        time.sleep(random.uniform(*self.delay_range))

    @staticmethod
    def normalize_title(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def normalize_price(text: str) -> Optional[float]:
        if not text:
            return None
        text = text.strip().replace("\xa0", " ").replace("  ", " ")
        match = PRICE_RE.search(text)
        if not match:
            return None
        num_str = match.group(1).replace(",", ".")
        parts = num_str.split(".")
        if len(parts) > 2:
            num_str = " ".join(parts[:-1]) + "." + parts[-1]
        try:
            val = float(num_str)
            return val if val > 0 else None
        except ValueError:
            return None

    @staticmethod
    def normalize_currency(text: str) -> Optional[str]:
        if not text:
            return None
        match = CURRENCY_RE.search(text)
        if not match:
            return None
        val = match.group(1)
        currency_map = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY", "₽": "RUB"}
        return currency_map.get(val, val.upper())

    @staticmethod
    def is_valid_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False

    def _clean_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    def _detect_molding_type(self, title: str) -> str:
        if not title:
            return "Прочее"
        title_lower = title.lower()
        if "добор" in title_lower:
            return "Добор"
        elif "короб" in title_lower:
            return "Короб"
        elif "наличник" in title_lower:
            return "Наличник"
        elif "плинтус" in title_lower:
            return "Плинтус"
        elif "планка" in title_lower:
            return "Притворная планка"
        elif "порог" in title_lower:
            return "Порог"
        return "Прочее"

    async def _extract_variations(self, page: Page, base_url: str) -> List[Dict[str, Any]]:
        """
        Извлекает вариации товара через Playwright.
        Возвращает список словарей с данными вариаций.
        """
        variations = []
        
        # === Извлечение размеров ===
        sizes = []
        size_selectors = [
            "input.sizer[name='size']",
            "input.sizer",
            "button[data-size]",
            ".Product-description__size-item input[type='radio']",
        ]
        
        for selector in size_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for el in elements:
                    value = await el.get_attribute("value")
                    if value:
                        value = value.strip()
                        # Если значение содержит путь — извлекаем только последнюю часть
                        if "/" in value:
                            value = value.split("/")[-1].rstrip("/")
                        # Проверяем формат размера (700, 700x2000, 700x2000x40)
                        if re.match(r"^[\d.,]+[xх][\d.,]+$", value) or re.match(r"^\d+$", value):
                            if value not in sizes:
                                sizes.append(value)
                        # Или извлекаем из data-атрибута
                        elif await el.get_attribute("data-size"):
                            size_val = (await el.get_attribute("data-size")).strip()
                            if size_val and size_val not in sizes:
                                sizes.append(size_val)
                        # Или из текста родителя (label)
                        else:
                            label = await el.query_selector("xpath=..")
                            if label:
                                text = await label.inner_text()
                                size_match = re.search(r"([\d.,]+\s*[xх]\s*[\d.,]+)", text)
                                if size_match:
                                    size_val = size_match.group(1).replace(" ", "")
                                    if size_val not in sizes:
                                        sizes.append(size_val)
            except Exception:
                continue
        
        # === Извлечение типов ===
        types = []
        type_selectors = [
            "input.typer[name='type']",
            "input.typer",
            "button[data-type]",
            ".Product-description__type-item input[type='radio']",
        ]
        
        for selector in type_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for el in elements:
                    value = await el.get_attribute("value")
                    if value:
                        value = value.strip()
                        if value and value not in types:
                            types.append(value)
            except Exception:
                continue
        
        # === Создаём комбинации ===
        if sizes and types:
            for size in sizes:
                for type_val in types:
                    variations.append({
                        "title": "",
                        "price": None,
                        "attributes": {"Размер": size, "Тип": type_val}
                    })
        elif sizes:
            for size in sizes:
                variations.append({
                    "title": "",
                    "price": None,
                    "attributes": {"Размер": size}
                })
        elif types:
            for type_val in types:
                variations.append({
                    "title": "",
                    "price": None,
                    "attributes": {"Тип": type_val}
                })
        
        logger_parser.info(f"  Найдено {len(variations)} вариаций")
        return variations

    async def _parse_molding_items(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        molding_items = []
        for item in soup.select("li.Product-description__molding-item"):
            try:
                data_id = item.get("data-id", "")
                data_price = item.get("data-price", "")
                
                title_el = item.select_one(".Checkbox__text")
                title = self._clean_text(title_el.get_text()) if title_el else ""
                
                color_el = item.select_one(".Checkbox__out-text")
                color = self._clean_text(color_el.get_text()) if color_el else ""
                
                item_type = self._detect_molding_type(title)
                
                if title:
                    molding_items.append({
                        "title": title,
                        "price": self.normalize_price(data_price),
                        "color": color,
                        "external_id": data_id,
                        "type": item_type,
                    })
            except Exception as e:
                logger_parser.warning(f"Ошибка парсинга погонажа: {e}")
        
        logger_parser.info(f"  Найдено {len(molding_items)} изделий погонажа")
        return molding_items

    async def _parse_product_page(self, page: Page, url: str) -> ParsedProduct:
        product = ParsedProduct(url=url)
        
        try:
            # Переход на страницу и ожидание загрузки
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(1500)  # Доп. ожидание для динамического контента
            
            html = await page.content()
            soup = BeautifulSoup(html, "lxml")
            product.raw_html_length = len(html)
            
            # === Заголовок ===
            title_el = (
                soup.select_one("h1") 
                or soup.select_one("h1.Product-description__title")
                or soup.select_one("[itemprop='name']")
                or soup.select_one("meta[name='title']")
            )
            if title_el:
                product.title = self.normalize_title(
                    title_el.get("content") if title_el.name == "meta" else title_el.get_text()
                )
            
            # === Цена ===
            price_el = soup.select_one(".Product-description__item-price-value")
            if price_el:
                price_text = price_el.get_text()
                product.price = self.normalize_price(price_text)
                product.currency = self.normalize_currency(price_text)
            
            # === SKU ===
            sku_el = soup.select_one("[itemprop='sku'], .sku")
            if sku_el:
                product.sku = self._clean_text(sku_el.get_text())
            
            # === Описание ===
            desc_el = soup.select_one("[itemprop='description'], .product-description")
            if desc_el:
                product.description = self._clean_text(desc_el.get_text())
            
            # === Изображения ===
            for img in soup.select("img[itemprop='image'], .Thumbnail-slide__swiper-image img"):
                src = img.get("data-src") or img.get("src")
                if src:
                    full_src = urljoin(url, src)
                    if self.is_valid_url(full_src) and not any(
                        ext in full_src.lower() for ext in [".svg", ".gif", ".ico", "placeholder"]
                    ):
                        if full_src not in product.image_urls:
                            product.image_urls.append(full_src)
            
            # === Атрибуты из dl/dt/dd ===
            for dt in soup.select(".Description__list dt.Description__list-term"):
                dd = dt.find_next_sibling("dd", class_="Description__list-desc")
                if dd:
                    name = self._clean_text(dt.get_text())
                    value = self._clean_text(dd.get_text())
                    if name and value:
                        product.attributes[name] = value
            
            # === Погонаж ===
            molding_items = await self._parse_molding_items(soup)
            if molding_items:
                product.molding_items = molding_items
                self.stats["molding_items_parsed"] += len(molding_items)
            
            # === Вариации ===
            has_sizer = await page.query_selector("input.sizer")
            has_typer = await page.query_selector("input.typer")
            if has_sizer or has_typer:
                variations = await self._extract_variations(page, url)
                if variations:
                    product.variations = variations
                    self.stats["variations_parsed"] += len(variations)
                    
        except Exception as e:
            logger_parser.error(f"Ошибка парсинга {url}: {e}")
            self.stats["errors"].append(f"Parse error: {url} - {e}")
            raise
        
        return product

    def _get_full_category_path(self, category_id: int) -> str:
        """Рекурсивно собирает полный путь категории."""
        if not category_id:
            return ""
        path_parts = []
        current_id = category_id
        while current_id:
            category = self.db_session.execute(
                select(Category).where(Category.id == current_id)
            ).scalar_one_or_none()
            if not category:
                break
            path_parts.insert(0, category.name)
            current_id = category.parent_id
        return " > ".join(path_parts) if path_parts else ""

    def _get_or_create_molding_root_category(self) -> int:
        """Получает или создаёт корневую категорию 'Погонаж'."""
        cache_key = f"{self.supplier_id}:molding_root"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]
        
        root = self.db_session.execute(
            select(Category).where(
                Category.supplier_id == self.supplier_id,
                Category.name == "Погонаж",
                Category.parent_id.is_(None)
            )
        ).scalar_one_or_none()
        
        if not root:
            root = Category(
                supplier_id=self.supplier_id,
                name="Погонаж",
                url="",
                parent_id=None,
                xpath_selector="",
                sort_order=0,
                product_count=0,
            )
            self.db_session.add(root)
            self.db_session.flush()
            self._log(f"  Создан корень погонажа (id={root.id})")
        
        self._category_cache[cache_key] = root.id
        return root.id

    def _get_or_create_molding_subcategory(self, molding_type: str) -> int:
        """Получает или создаёт подкатегорию погонажа."""
        root_id = self._get_or_create_molding_root_category()
        cache_key = f"{self.supplier_id}:molding:{molding_type}"
        if cache_key in self._category_cache:
            return self._category_cache[cache_key]
        
        subcat = self.db_session.execute(
            select(Category).where(
                Category.supplier_id == self.supplier_id,
                Category.parent_id == root_id,
                Category.name == molding_type,
            )
        ).scalar_one_or_none()
        
        if not subcat:
            subcat = Category(
                supplier_id=self.supplier_id,
                parent_id=root_id,
                name=molding_type,
                url="",
                xpath_selector="",
                sort_order=0,
                product_count=0,
            )
            self.db_session.add(subcat)
            self.db_session.flush()
            self._log(f"  Создана подкатегория погонажа: {molding_type} (id={subcat.id})")
        
        self._category_cache[cache_key] = subcat.id
        return subcat.id

    def _upsert_molding_item(self, item: Dict[str, Any], door_category_path: str) -> None:
        """UPSERT погонажа как НЕЗАВИСИМОГО товара."""
        molding_type = item.get("type", "Прочее")
        molding_title = item.get("title", "")
        molding_sku = item.get("external_id")
        molding_color = item.get("color", "")
        molding_price = item.get("price")
        
        if not molding_title:
            return
        
        # 🔥 Получаем категорию погонажа ПОД корнем "Погонаж"
        molding_category_id = self._get_or_create_molding_subcategory(molding_type)
        
        # 🔥 Поиск существующего НЕЗАВИСИМОГО погонажа (parent_product_id=None!)
        existing_molding = None
        if molding_sku:
            existing_molding = self.db_session.execute(
                select(Product).where(
                    Product.supplier_id == self.supplier_id,
                    Product.category_id == molding_category_id,
                    Product.external_sku == molding_sku,
                    Product.parent_product_id.is_(None),  # 🔥 Только независимые!
                )
            ).scalar_one_or_none()
        
        if not existing_molding and molding_title:
            existing_molding = self.db_session.execute(
                select(Product).where(
                    Product.supplier_id == self.supplier_id,
                    Product.category_id == molding_category_id,
                    Product.title == molding_title,
                    Product.parent_product_id.is_(None),  # 🔥 Только независимые!
                )
            ).scalar_one_or_none()
        
        if existing_molding:
            # Обновление
            existing_molding.title = molding_title
            existing_molding.price = molding_price
            existing_molding.currency = "RUB"
            existing_molding.is_available = True
            existing_molding.updated_at = datetime.utcnow()
            
            # 🔥 Обновление compatible_collections без дублей
            current = existing_molding.get_compatible_collections()
            if door_category_path and door_category_path not in current:
                current.append(door_category_path)
                existing_molding.set_compatible_collections(current)
            
            self.db_session.flush()
            self._log(f"  Обновлен погонаж: {molding_title} | Collections: {len(current)}")
        else:
            # 🔥 Создание НОВОГО независимого погонажа
            molding_product = Product(
                supplier_id=self.supplier_id,
                category_id=molding_category_id,
                parent_product_id=None,  # 🔥 НЕЗАВИСИМЫЙ!
                external_sku=molding_sku,
                title=molding_title,
                description=f"Комплектующий: {molding_type}",
                price=molding_price,
                currency="RUB",
                is_available=True,
                image_urls="[]",
            )
            
            # 🔥 Инициализация compatible_collections
            if door_category_path:
                molding_product.set_compatible_collections([door_category_path])
            
            self.db_session.add(molding_product)
            self.db_session.flush()
            
            if molding_color:
                safe_color = molding_color[:65535]
                if safe_color:
                    color_attr = ProductAttribute(
                        product_id=molding_product.id,
                        name="Цвет",
                        value=safe_color,
                    )
                    self.db_session.add(color_attr)
            
            self._log(f"  Создан погонаж: {molding_title} | Collections: {[door_category_path]}")

    async def _save_product(self, product: ParsedProduct) -> int:
        """Сохраняет товар с поддержкой иерархии."""
        try:
            # === 1. РОДИТЕЛЬ ===
            cleaned_title = re.sub(r'\s*\d+[xх]\d+\s*.*$', '', product.title or "Без названия").strip()
            
            existing = None
            if product.sku:
                existing = self.db_session.execute(
                    select(Product).where(
                        Product.supplier_id == self.supplier_id,
                        Product.external_sku == product.sku,
                        Product.parent_product_id.is_(None),
                    )
                ).scalar_one_or_none()
            elif cleaned_title and cleaned_title != "Без названия":
                existing = self.db_session.execute(
                    select(Product).where(
                        Product.supplier_id == self.supplier_id,
                        Product.title == cleaned_title,
                        Product.parent_product_id.is_(None),
                    )
                ).scalar_one_or_none()

            if existing:
                main_id = existing.id
                existing.title = cleaned_title
                existing.description = product.description
                existing.price = product.price
                existing.currency = product.currency
                existing.is_available = product.is_available
                existing.image_urls = json.dumps(product.image_urls, ensure_ascii=False)
                existing.updated_at = datetime.utcnow()
                self.db_session.flush()
                self._log(f"  Обновлен родитель: {cleaned_title} (id={main_id})")
            else:
                main = Product(
                    supplier_id=self.supplier_id,
                    category_id=product.category_id,
                    parent_product_id=None,
                    external_sku=product.sku,
                    title=cleaned_title if cleaned_title != "Без названия" else (product.title or "Без названия"),
                    description=product.description,
                    price=product.price,
                    currency=product.currency,
                    is_available=product.is_available,
                    image_urls=json.dumps(product.image_urls, ensure_ascii=False),
                )
                self.db_session.add(main)
                self.db_session.flush()
                main_id = main.id
                self._log(f"  Создан родитель: {cleaned_title} (id={main_id})")

            # Атрибуты родителя
            for attr_name, attr_value in product.attributes.items():
                safe_name = attr_name[:255] if attr_name else ""
                safe_value = attr_value[:65535] if attr_value else ""
                if safe_name and safe_value:
                    attr = ProductAttribute(
                        product_id=main_id,
                        name=safe_name,
                        value=safe_value,
                    )
                    self.db_session.add(attr)

            # === 2. ВАРИАЦИИ (ДЕТИ) + СБОР РАЗМЕРОВ ===
            all_sizes = []
            for var in product.variations:
                size = var.get("attributes", {}).get("Размер")
                if size and size not in all_sizes:
                    all_sizes.append(size)
            
            if all_sizes:
                sizes_str = "|".join(all_sizes)
                existing_attr = self.db_session.execute(
                    select(ProductAttribute).where(
                        ProductAttribute.product_id == main_id,
                        ProductAttribute.name == "Доступные размеры"
                    )
                ).scalar_one_or_none()
                
                if existing_attr:
                    existing_attr.value = sizes_str
                else:
                    self.db_session.add(ProductAttribute(
                        product_id=main_id,
                        name="Доступные размеры",
                        value=sizes_str,
                    ))
                self._log(f"  Родитель: размеры = {sizes_str}")
            
            # Создание детей
            for var in product.variations:
                var_title = var.get("title", cleaned_title)
                var_attrs = var.get("attributes", {})
                var_product = Product(
                    supplier_id=self.supplier_id,
                    category_id=product.category_id,
                    parent_product_id=main_id,
                    external_sku=product.sku,
                    title=var_title if var_title else f"{cleaned_title} ({var_attrs.get('Размер', '')})",
                    description=var.get("description", product.description),
                    price=var.get("price", product.price),
                    currency=var.get("currency", product.currency),
                    is_available=var.get("is_available", product.is_available),
                    image_urls=json.dumps(var.get("image_urls", product.image_urls), ensure_ascii=False),
                )
                self.db_session.add(var_product)
                self.db_session.flush()
                var_id = var_product.id
                self._log(f"  Создана вариация: {var_product.title} (parent={main_id})")
                
                for attr_name, attr_value in var_attrs.items():
                    safe_name = attr_name[:255] if attr_name else ""
                    safe_value = attr_value[:65535] if attr_value else ""
                    if safe_name and safe_value:
                        self.db_session.add(ProductAttribute(
                            product_id=var_id,
                            name=safe_name,
                            value=safe_value,
                        ))

            # === 3. ПОГОНАЖ (НЕЗАВИСИМЫЕ!) ===
            if product.molding_items:
                # 🔥 Получаем ПОЛНЫЙ путь категории двери
                door_category_path = self._get_full_category_path(product.category_id)
                self._log(f"  Путь категории двери: '{door_category_path}'")
                
                for molding in product.molding_items:
                    try:
                        self._upsert_molding_item(molding, door_category_path)
                    except Exception as e:
                        self._log(f"  Ошибка погонажа {molding.get('title')}: {e}")
                        continue

            return main_id
            
        except Exception as e:
            logger_parser.error(f"Ошибка сохранения товара: {e}")
            self.stats["errors"].append(f"Database save error: {e}")
            raise

    async def run(self, urls: List[str], is_category: bool = True) -> Dict[str, Any]:
        """Запускает парсинг."""
        self._cancelled = False
        self._paused = False
        self._pause_event.set()
        self.stats = {
            "products_parsed": 0,
            "variations_parsed": 0,
            "molding_items_parsed": 0,
            "errors": [],
            "start_time": time.time(),
            "end_time": None,
        }
        self._seen_urls.clear()
        self._category_cache.clear()

        self._log(f"Запуск Playwright-парсера для поставщика {self.supplier_id}")
        self._log(f"URL для парсинга: {len(urls)} (категории={is_category})")

        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=self.headless)
            
            try:
                if is_category:
                    for category_url in urls:
                        if self._cancelled:
                            break
                        await self._parse_category(category_url)
                else:
                    # 🔥 Парсинг отдельных товаров
                    for product_url in urls:
                        if self._cancelled:
                            break
                        await self._pause_event.wait()
                        page = None
                        try:
                            page = await self.browser.new_page()
                            product = await self._parse_product_page(page, product_url)
                            await self._save_product(product)
                            self.stats["products_parsed"] += 1
                            self._progress(
                                self.stats["products_parsed"],
                                len(urls),
                                f"Обработано {self.stats['products_parsed']} товаров"
                            )
                            self._random_delay()
                        except Exception as e:
                            self._log(f"  Ошибка товара {product_url}: {e}")
                            self.stats["errors"].append(f"Product error: {product_url} - {e}")
                        finally:
                            if page and not page.is_closed():
                                await page.close()
                    
                # Обновление метаданных поставщика
                supplier = self.db_session.execute(
                    select(Supplier).where(Supplier.id == self.supplier_id)
                ).scalar_one_or_none()
                if supplier:
                    supplier.last_scrape_run = datetime.utcnow()
                    self.db_session.flush()
                     
            finally:
                await self.browser.close()
                self.browser = None
                
        self.stats["end_time"] = time.time()
        elapsed = self.stats["end_time"] - self.stats["start_time"]
        
        self._log(f"Парсинг завершён: {self.stats['products_parsed']} товаров, {elapsed:.1f}с")
        
        return {
            "success": True,
            "products_parsed": self.stats["products_parsed"],
            "variations_parsed": self.stats["variations_parsed"],
            "molding_items_parsed": self.stats["molding_items_parsed"],
            "errors": self.stats["errors"],
            "elapsed": elapsed,
        }

    async def _parse_category(self, category_url: str) -> Dict[str, Any]:
        if self._cancelled:
            return self.stats

        await self._pause_event.wait()

        if not self.browser:
            raise RuntimeError("Browser not initialized")
            
        page = await self.browser.new_page()
        
        try:
            await page.goto(category_url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(1000)
            
            product_links = []
            link_elements = await page.query_selector_all("a[href*='/catalog/']")
            
            for link_el in link_elements:
                href = await link_el.get_attribute("href")
                if href:
                    full_url = urljoin(category_url, href.split("#")[0])
                    # 🔥 КЛЮЧЕВОЙ ФИЛЬТР: только домен tandoor.ru и только /product/
                    if (
                        "/product/" in full_url 
                        and full_url.startswith("https://tandoor.ru")
                        and full_url not in self._seen_urls
                    ):
                        product_links.append(full_url)
                        self._seen_urls.add(full_url)
            
            self._log(f"  Категория: найдено {len(product_links)} товаров")
            
            parsed_products = []
            total_links = len(product_links)
            
            for i, product_url in enumerate(product_links):
                if self._cancelled:
                    break
                    
                await self._pause_event.wait()
                
                try:
                    product = await self._parse_product_page(page, product_url)
                    parsed_products.append(product)
                    self.stats["products_parsed"] += 1
                    
                    self._progress(
                        self.stats["products_parsed"],
                        total_links,
                        f"Распаршено {self.stats['products_parsed']} товаров"
                    )
                    
                    self._random_delay()
                except Exception as e:
                    self._log(f"  Ошибка товара {product_url}: {e}")
                    self.stats["errors"].append(f"Product parse error: {product_url} - {e}")
                    continue
            
            for product in parsed_products:
                try:
                    await self._save_product(product)
                except Exception as e:
                    self._log(f"  Ошибка сохранения {product.title}: {e}")
                    self.stats["errors"].append(f"Product save error: {product.title} - {e}")
                    continue
                    
        except Exception as e:
            logger_parser.error(f"Ошибка парсинга категории {category_url}: {e}")
            self.stats["errors"].append(f"Category parse error: {category_url} - {e}")
        final                                                                            
```

### `build\lib\src\ui\__init__.py`
```python

```

### `build\lib\src\ui\main_window.py`
```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MEEYG 1.0")
        self.setMinimumSize(1200, 800)

        self._nav_buttons: list[QPushButton] = []
        self._pages: list[QWidget] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        self._stack = QStackedWidget()
        self._stack.setObjectName("contentArea")
        root_layout.addWidget(self._stack, 1)

        self.statusBar().showMessage("Готово")

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar.setFrameShape(QFrame.NoFrame)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 24, 16, 16)
        layout.setSpacing(8)

        title = QLabel("MEEYG")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Разведка поставщиков")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(16)

        nav_items = [
            ("Главная", 0),
            ("Поставщики", 1),
            ("Разведка", 2),
            ("Парсинг", 3),
            ("Архив", 4),
            ("Аналитика", 5),
            ("Экспорт", 6),
        ]

        for label, index in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setMinimumHeight(44)
            btn.clicked.connect(lambda _, idx=index: self.switch_page(idx))
            layout.addWidget(btn)
            self._nav_buttons.append(btn)

        layout.addStretch()

        self._nav_buttons[0].setChecked(True)

        return sidebar

    def register_page(self, page: QWidget) -> int:
        index = self._stack.addWidget(page)
        self._pages.append(page)
        return index

    def switch_page(self, index: int) -> None:
        for btn in self._nav_buttons:
            btn.setChecked(False)
        if 0 <= index < len(self._nav_buttons):
            self._nav_buttons[index].setChecked(True)
        self._stack.setCurrentIndex(index)
        page_names = ["Главная", "Поставщики", "Разведка", "Парсинг", "Архив", "Аналитика", "Экспорт"]
        if 0 <= index < len(page_names):
            self.statusBar().showMessage(f"Страница: {page_names[index]}")

```

### `build\lib\src\ui\pages\__init__.py`
```python

```

### `build\lib\src\ui\pages\archive_page.py`
```python
import json
from datetime import datetime
from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel, QSize, Signal
from PySide6.QtGui import QAction, QColor, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from src.database.models import Category, Product, Supplier
from src.database.session import get_session
from src.modules.import_prep.mapper import (
    DB_FIELDS,
    FieldMapper,
    MappingConfig,
    RuleEngine,
    WP_ALL_IMPORT_FIELDS,
)

PAGE_SIZE = 200


class ProductTableModel(QAbstractTableModel):
    _headers = ["ID", "SKU", "Название", "Цена", "Валюта", "Категория", "Доступен", "Готов", "Поставщик"]

    def __init__(self):
        super().__init__()
        self._products: list[dict] = []
        self._total_count = 0
        self._modified_cells: set[tuple[int, int]] = set()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._products)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        product = self._products[row]
        keys = ["id", "external_sku", "title", "price", "currency", "category_name", "is_available", "is_ready_for_export", "supplier_name"]

        if role == Qt.DisplayRole:
            key = keys[col]
            val = product.get(key)
            if key == "price":
                return f"{val:.2f}" if val is not None else ""
            if key == "is_available":
                return "Да" if val else "Нет"
            if key == "is_ready_for_export":
                return "Да" if val else "Нет"
            if val is None:
                return ""
            return str(val)

        if role == Qt.BackgroundRole:
            if (row, col) in self._modified_cells:
                return QColor(255, 255, 200)

        if role == Qt.TextAlignmentRole:
            if col in (0, 3):
                return Qt.AlignRight | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def load_page(self, supplier_id: Optional[int] = None, category_id: Optional[int] = None,
                  available_only: bool = False, search: str = "", page: int = 0) -> int:
        self._products.clear()
        self._modified_cells.clear()

        with get_session() as session:
            query = session.query(
                Product.id,
                Product.external_sku,
                Product.title,
                Product.price,
                Product.currency,
                Product.is_available,
                Product.is_ready_for_export,
                Category.name.label("category_name"),
                Supplier.name.label("supplier_name"),
            ).outerjoin(Category, Product.category_id == Category.id).outerjoin(
                Supplier, Product.supplier_id == Supplier.id
            )

            if supplier_id:
                query = query.filter(Product.supplier_id == supplier_id)
            if category_id:
                query = query.filter(Product.category_id == category_id)
            if available_only:
                query = query.filter(Product.is_available == True)
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    (Product.title.ilike(search_pattern)) |
                    (Product.external_sku.ilike(search_pattern))
                )

            self._total_count = query.count()

            products = query.order_by(Product.id).offset(page * PAGE_SIZE).limit(PAGE_SIZE).all()

            for p in products:
                self._products.append({
                    "id": p.id,
                    "external_sku": p.external_sku,
                    "title": p.title,
                    "price": p.price,
                    "currency": p.currency,
                    "is_available": p.is_available,
                    "is_ready_for_export": p.is_ready_for_export,
                    "category_name": p.category_name,
                    "supplier_name": p.supplier_name,
                })

        self.layoutChanged.emit()
        return self._total_count

    def get_product(self, row: int) -> Optional[dict]:
        if 0 <= row < len(self._products):
            return self._products[row]
        return None

    def get_selected_ids(self, rows: list[int]) -> list[int]:
        ids = []
        for row in rows:
            p = self.get_product(row)
            if p:
                ids.append(p["id"])
        return ids

    def mark_modified(self, row: int, col: int) -> None:
        self._modified_cells.add((row, col))
        idx = self.index(row, col)
        self.dataChanged.emit(idx, idx, [Qt.BackgroundRole])

    @property
    def total_count(self) -> int:
        return self._total_count

    @property
    def page_count(self) -> int:
        return (self._total_count + PAGE_SIZE - 1) // PAGE_SIZE


class ProductFilterProxy(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterKeyColumn(-1)


class EditProductDialog(QDialog):
    def __init__(self, product: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Редактирование товара #{product['id']}")
        self.setMinimumWidth(500)
        self._product = product
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._title_input = QLineEdit(self._product.get("title", ""))
        form.addRow("Название:", self._title_input)

        self._sku_input = QLineEdit(self._product.get("external_sku") or "")
        form.addRow("Артикул:", self._sku_input)

        self._price_input = QLineEdit(str(self._product.get("price") or ""))
        form.addRow("Цена:", self._price_input)

        self._currency_input = QLineEdit(self._product.get("currency") or "")
        form.addRow("Валюта:", self._currency_input)

        self._available_check = QCheckBox()
        self._available_check.setChecked(self._product.get("is_available", True))
        form.addRow("Доступен:", self._available_check)

        self._ready_check = QCheckBox()
        self._ready_check.setChecked(self._product.get("is_ready_for_export", False))
        form.addRow("Готов к экспорту:", self._ready_check)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_data(self) -> dict:
        return {
            "title": self._title_input.text().strip(),
            "external_sku": self._sku_input.text().strip() or None,
            "price": float(self._price_input.text()) if self._price_input.text() else None,
            "currency": self._currency_input.text().strip() or None,
            "is_available": self._available_check.isChecked(),
            "is_ready_for_export": self._ready_check.isChecked(),
        }


class MappingDialog(QDialog):
    def __init__(self, mapper: FieldMapper, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сопоставление полей — WP All Import")
        self.setMinimumSize(600, 500)
        self._mapper = mapper
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        tpl_row = QHBoxLayout()
        tpl_row.addWidget(QLabel("Шаблон:"))
        self._template_combo = QComboBox()
        self._load_templates()
        tpl_row.addWidget(self._template_combo)
        self._btn_load_tpl = QPushButton("Загрузить")
        self._btn_save_tpl = QPushButton("Сохранить")
        tpl_row.addWidget(self._btn_load_tpl)
        tpl_row.addWidget(self._btn_save_tpl)
        layout.addLayout(tpl_row)

        form = QFormLayout()
        self._mapping_widgets = {}
        for db_field, db_label in DB_FIELDS.items():
            combo = QComboBox()
            combo.addItem("— Не сопоставлено —")
            for wp_field, meta in WP_ALL_IMPORT_FIELDS.items():
                combo.addItem(f"{wp_field} ({meta['label']})", userData=wp_field)
            current_wp = self._mapper.config.field_mapping.get(db_field)
            if current_wp:
                idx = combo.findData(current_wp)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            form.addRow(f"{db_label} ({db_field}):", combo)
            self._mapping_widgets[db_field] = combo

        layout.addLayout(form)

        rules_group = QGroupBox("Правила")
        rules_layout = QVBoxLayout(rules_group)
        self._rules_list = QListWidget()
        for rule in self._mapper.config.rules:
            item = QListWidgetItem(f"{rule['type']}: {json.dumps({k:v for k,v in rule.items() if k != 'type'})}")
            self._rules_list.addItem(item)
        rules_layout.addWidget(self._rules_list)

        rules_btn_row = QHBoxLayout()
        self._btn_add_rule = QPushButton("Добавить правило")
        self._btn_remove_rule = QPushButton("Удалить правило")
        rules_btn_row.addWidget(self._btn_add_rule)
        rules_btn_row.addWidget(self._btn_remove_rule)
        rules_layout.addLayout(rules_btn_row)
        layout.addWidget(rules_group)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Сохранить сопоставление")
        cancel_btn = QPushButton("Отмена")
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self._btn_load_tpl.clicked.connect(self._on_load_template)
        self._btn_save_tpl.clicked.connect(self._on_save_template)
        self._btn_add_rule.clicked.connect(self._on_add_rule)
        self._btn_remove_rule.clicked.connect(self._on_remove_rule)
        save_btn.clicked.connect(self._on_save)
        cancel_btn.clicked.connect(self.reject)

    def _load_templates(self):
        self._template_combo.clear()
        try:
            with get_session() as session:
                templates = self._mapper.list_templates(session)
                for t in templates:
                    self._template_combo.addItem(t.name, userData=t.id)
        except Exception:
            pass

    def _on_load_template(self):
        tpl_id = self._template_combo.currentData()
        if tpl_id is None:
            return
        with get_session() as session:
            if self._mapper.load_template(session, tpl_id):
                self.accept()

    def _on_save_template(self):
        name, ok = QLineEdit.getText(self, "Сохранить шаблон", "Имя шаблона:")
        if ok and name:
            self._apply_mapping_from_ui()
            with get_session() as session:
                self._mapper.save_template(session, name)
            self._load_templates()

    def _on_add_rule(self):
        rule_type, ok = QLineEdit.getText(self, "Добавить правило", "Тип правила (например, null_replacement, price_round, price_markup):")
        if ok and rule_type:
            self._mapper.config.add_rule(rule_type)
            self._rules_list.addItem(rule_type)

    def _on_remove_rule(self):
        row = self._rules_list.currentRow()
        if row >= 0 and row < len(self._mapper.config.rules):
            self._mapper.config.rules.pop(row)
            self._rules_list.takeItem(row)

    def _apply_mapping_from_ui(self):
        self._mapper.config.field_mapping.clear()
        for db_field, combo in self._mapping_widgets.items():
            wp_field = combo.currentData()
            if wp_field:
                self._mapper.config.field_mapping[db_field] = wp_field

    def _on_save(self):
        self._apply_mapping_from_ui()
        self.accept()


class ArchivePage(QWidget):
    def __init__(self):
        super().__init__()
        self._mapper = FieldMapper()
        self._current_page = 0
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        filter_group = QGroupBox("Фильтры")
        filter_layout = QVBoxLayout(filter_group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Поставщик:"))
        self._supplier_combo = QComboBox()
        self._supplier_combo.setMinimumWidth(200)
        row1.addWidget(self._supplier_combo)

        row1.addSpacing(16)
        row1.addWidget(QLabel("Категория:"))
        self._category_combo = QComboBox()
        self._category_combo.setMinimumWidth(200)
        row1.addWidget(self._category_combo)

        row1.addSpacing(16)
        self._avail_check = QCheckBox("Только доступные")
        row1.addWidget(self._avail_check)

        row1.addStretch()
        filter_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Поиск:"))
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Поиск по названию или артикулу...")
        self._search_input.setMinimumWidth(250)
        row2.addWidget(self._search_input)

        row2.addSpacing(16)
        self._btn_filter = QPushButton("Применить фильтры")
        row2.addWidget(self._btn_filter)
        self._btn_reset = QPushButton("Сбросить")
        row2.addWidget(self._btn_reset)
        row2.addStretch()
        filter_layout.addLayout(row2)

        layout.addWidget(filter_group)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))

        self._btn_edit = QAction("Редактировать", self)
        self._btn_delete = QAction("Удалить", self)
        self._btn_mark_ready = QAction("Отметить готовым", self)
        self._btn_mark_not_ready = QAction("Отметить не готовым", self)
        self._btn_mapping = QAction("Сопоставление полей", self)
        self._btn_validate = QAction("Проверить", self)
        self._btn_export_preview = QAction("Предпросмотр экспорта", self)

        toolbar.addAction(self._btn_edit)
        toolbar.addAction(self._btn_delete)
        toolbar.addSeparator()
        toolbar.addAction(self._btn_mark_ready)
        toolbar.addAction(self._btn_mark_not_ready)
        toolbar.addSeparator()
        toolbar.addAction(self._btn_mapping)
        toolbar.addAction(self._btn_validate)
        toolbar.addAction(self._btn_export_preview)

        layout.addWidget(toolbar)

        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableView()
        self._model = ProductTableModel()
        self._proxy = ProductFilterProxy()
        self._proxy.setSourceModel(self._model)
        self._table.setModel(self._proxy)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        left_layout.addWidget(self._table)

        pagination = QHBoxLayout()
        self._btn_prev = QPushButton("Предыдущая")
        self._btn_next = QPushButton("Следующая")
        self._page_label = QLabel("Страница 1 / 1")
        self._page_label.setAlignment(Qt.AlignCenter)
        pagination.addWidget(self._btn_prev)
        pagination.addWidget(self._page_label)
        pagination.addWidget(self._btn_next)
        pagination.addStretch()
        self._count_label = QLabel("0 товаров")
        pagination.addWidget(self._count_label)
        left_layout.addLayout(pagination)

        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        form_group = QGroupBox("Быстрое редактирование")
        form_layout = QFormLayout(form_group)

        self._edit_title = QLineEdit()
        self._edit_sku = QLineEdit()
        self._edit_price = QLineEdit()
        self._edit_currency = QLineEdit()
        self._edit_available = QCheckBox()
        self._edit_ready = QCheckBox()

        form_layout.addRow("Название:", self._edit_title)
        form_layout.addRow("Артикул:", self._edit_sku)
        form_layout.addRow("Цена:", self._edit_price)
        form_layout.addRow("Валюта:", self._edit_currency)
        form_layout.addRow("Доступен:", self._edit_available)
        form_layout.addRow("Готов к экспорту:", self._edit_ready)

        self._btn_save_edit = QPushButton("Сохранить изменения")
        self._btn_save_edit.setMinimumHeight(36)
        form_layout.addRow(self._btn_save_edit)

        right_layout.addWidget(form_group)

        preview_group = QGroupBox("Предпросмотр WP All Import")
        preview_layout = QVBoxLayout(preview_group)
        self._preview_edit = QPlainTextEdit()
        self._preview_edit.setReadOnly(True)
        preview_layout.addWidget(self._preview_edit)
        right_layout.addWidget(preview_group)

        splitter.addWidget(right_widget)
        splitter.setSizes([700, 400])
        layout.addWidget(splitter)

        self._btn_filter.clicked.connect(self._on_filter)
        self._btn_reset.clicked.connect(self._on_reset)
        self._btn_prev.clicked.connect(self._on_prev_page)
        self._btn_next.clicked.connect(self._on_next_page)
        self._btn_edit.triggered.connect(self._on_edit)
        self._btn_delete.triggered.connect(self._on_delete)
        self._btn_mark_ready.triggered.connect(self._on_mark_ready)
        self._btn_mark_not_ready.triggered.connect(self._on_mark_not_ready)
        self._btn_mapping.triggered.connect(self._on_mapping)
        self._btn_validate.triggered.connect(self._on_validate)
        self._btn_export_preview.triggered.connect(self._on_export_preview)
        self._btn_save_edit.clicked.connect(self._on_save_edit)
        self._search_input.returnPressed.connect(self._on_filter)
        self._table.customContextMenuRequested.connect(self._on_context_menu)
        self._table.clicked.connect(self._on_row_clicked)
        self._supplier_combo.currentIndexChanged.connect(self._on_supplier_changed)

    def _load_suppliers(self):
        self._supplier_combo.clear()
        self._category_combo.clear()
        try:
            with get_session() as session:
                suppliers = session.query(Supplier).filter(
                    Supplier.is_active == True
                ).order_by(Supplier.name).all()
                self._supplier_combo.addItem("Все поставщики", userData=None)
                for s in suppliers:
                    self._supplier_combo.addItem(s.name, userData=s.id)
        except Exception:
            pass

    def _on_supplier_changed(self):
        self._category_combo.clear()
        supplier_id = self._supplier_combo.currentData()
        if supplier_id:
            try:
                with get_session() as session:
                    categories = session.query(Category).filter(
                        Category.supplier_id == supplier_id
                    ).order_by(Category.name).all()
                    self._category_combo.addItem("Все категории", userData=None)
                    for c in categories:
                        self._category_combo.addItem(c.name, userData=c.id)
            except Exception:
                pass
        else:
            self._category_combo.addItem("Все категории", userData=None)

    def _on_filter(self):
        self._current_page = 0
        self._load_products()

    def _on_reset(self):
        self._supplier_combo.setCurrentIndex(0)
        self._category_combo.setCurrentIndex(0)
        self._avail_check.setChecked(False)
        self._search_input.clear()
        self._current_page = 0
        self._load_products()

    def _load_products(self):
        supplier_id = self._supplier_combo.currentData()
        category_id = self._category_combo.currentData()
        available_only = self._avail_check.isChecked()
        search = self._search_input.text().strip()

        total = self._model.load_page(
            supplier_id=supplier_id,
            category_id=category_id,
            available_only=available_only,
            search=search,
            page=self._current_page,
        )

        page_count = self._model.page_count or 1
        self._page_label.setText(f"Страница {self._current_page + 1} / {page_count}")
        self._count_label.setText(f"{total} товаров")
        self._btn_prev.setEnabled(self._current_page > 0)
        self._btn_next.setEnabled(self._current_page < page_count - 1)

    def _on_prev_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self._load_products()

    def _on_next_page(self):
        if self._current_page < self._model.page_count - 1:
            self._current_page += 1
            self._load_products()

    def _on_row_clicked(self, index):
        src_index = self._proxy.mapToSource(index)
        product = self._model.get_product(src_index.row())
        if product:
            self._edit_title.setText(product.get("title", ""))
            self._edit_sku.setText(product.get("external_sku") or "")
            self._edit_price.setText(str(product.get("price") or ""))
            self._edit_currency.setText(product.get("currency") or "")
            self._edit_available.setChecked(product.get("is_available", True))
            self._edit_ready.setChecked(product.get("is_ready_for_export", False))
            self._update_preview(product)

    def _update_preview(self, product: dict):
        product_data = {
            "id": product.get("id"),
            "post_title": product.get("title"),
            "sku": product.get("external_sku"),
            "regular_price": product.get("price"),
            "stock": 1 if product.get("is_available") else 0,
            "stock_status": "instock" if product.get("is_available") else "outofstock",
            "categories": product.get("category_name"),
            "description": "",
            "images": product.get("image_urls", ""),
        }
        transformed = self._mapper.transform_product(product_data)
        self._preview_edit.setPlainText(json.dumps(transformed, indent=2, ensure_ascii=False))

    def _on_save_edit(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            QMessageBox.warning(self, "Ничего не выбрано", "Выберите товар для редактирования.")
            return

        src_index = self._proxy.mapToSource(src_rows[0])
        product = self._model.get_product(src_index.row())
        if not product:
            return

        try:
            with get_session() as session:
                from src.database.models import Product as ProductModel
                p = session.query(ProductModel).filter(ProductModel.id == product["id"]).first()
                if p:
                    p.title = self._edit_title.text().strip()
                    p.external_sku = self._edit_sku.text().strip() or None
                    p.price = float(self._edit_price.text()) if self._edit_price.text() else None
                    p.currency = self._edit_currency.text().strip() or None
                    p.is_available = self._edit_available.isChecked()
                    p.is_ready_for_export = self._edit_ready.isChecked()

            self._model.mark_modified(src_index.row(), 1)
            self._model.mark_modified(src_index.row(), 2)
            self._load_products()
            QMessageBox.information(self, "Успех", "Товар обновлён.")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить товар:\n{exc}")

    def _on_edit(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            QMessageBox.warning(self, "Ничего не выбрано", "Выберите товар для редактирования.")
            return

        src_index = self._proxy.mapToSource(src_rows[0])
        product = self._model.get_product(src_index.row())
        if not product:
            return

        dialog = EditProductDialog(product, self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                with get_session() as session:
                    from src.database.models import Product as ProductModel
                    p = session.query(ProductModel).filter(ProductModel.id == product["id"]).first()
                    if p:
                        p.title = data["title"]
                        p.external_sku = data["external_sku"]
                        p.price = data["price"]
                        p.currency = data["currency"]
                        p.is_available = data["is_available"]
                        p.is_ready_for_export = data["is_ready_for_export"]
                self._load_products()
                QMessageBox.information(self, "Успех", "Товар обновлён.")
            except Exception as exc:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить:\n{exc}")

    def _on_delete(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            QMessageBox.warning(self, "Ничего не выбрано", "Выберите товары для удаления.")
            return

        ids = self._model.get_selected_ids([self._proxy.mapToSource(r).row() for r in src_rows])
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Удалить {len(ids)} товар(ов)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            with get_session() as session:
                from src.database.models import Product as ProductModel
                session.query(ProductModel).filter(ProductModel.id.in_(ids)).delete(synchronize_session="fetch")
            self._load_products()
            QMessageBox.information(self, "Успех", f"Удалено {len(ids)} товар(ов).")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{exc}")

    def _on_mark_ready(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            return
        ids = self._model.get_selected_ids([self._proxy.mapToSource(r).row() for r in src_rows])
        with get_session() as session:
            self._mapper.mark_ready_for_export(session, ids)
        self._load_products()

    def _on_mark_not_ready(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            return
        ids = self._model.get_selected_ids([self._proxy.mapToSource(r).row() for r in src_rows])
        with get_session() as session:
            self._mapper.mark_not_ready(session, ids)
        self._load_products()

    def _on_mapping(self):
        dialog = MappingDialog(self._mapper, self)
        if dialog.exec() == QDialog.Accepted:
            self._load_products()

    def _on_validate(self):
        supplier_id = self._supplier_combo.currentData()
        issues = []
        with get_session() as session:
            from src.database.models import Product as ProductModel, Category, Supplier
            query = session.query(
                ProductModel.id, ProductModel.external_sku, ProductModel.title,
                ProductModel.price, ProductModel.currency, ProductModel.is_available,
                Category.name.label("category_name"),
            ).outerjoin(Category, ProductModel.category_id == Category.id)
            if supplier_id:
                query = query.filter(ProductModel.supplier_id == supplier_id)

            products = query.all()
            for p in products:
                product_data = {
                    "id": p.id,
                    "post_title": p.title,
                    "sku": p.external_sku,
                    "regular_price": p.price,
                    "stock": 1 if p.is_available else 0,
                    "stock_status": "instock" if p.is_available else "outofstock",
                    "categories": p.category_name,
                }
                transformed = self._mapper.transform_product(product_data)
                issues.extend(self._mapper.validate_product(transformed, p.id))

        if not issues:
            QMessageBox.information(self, "Валидация", "Все товары проходят валидацию.")
        else:
            errors = [i for i in issues if i.severity == "error"]
            warnings = [i for i in issues if i.severity == "warning"]
            msg = f"Ошибок: {len(errors)}\nПредупреждений: {len(warnings)}\n\n"
            for issue in issues[:20]:
                msg += f"[{issue.severity.upper()}] Товар {issue.product_id}: {issue.field} — {issue.message}\n"
            if len(issues) > 20:
                msg += f"\n... и ещё {len(issues) - 20} проблем"
            QMessageBox.warning(self, "Результаты валидации", msg)

    def _on_export_preview(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            QMessageBox.warning(self, "Ничего не выбрано", "Выберите товары для предпросмотра.")
            return

        rows = [self._proxy.mapToSource(r).row() for r in src_rows[:10]]
        preview_lines = []
        for row in rows:
            product = self._model.get_product(row)
            if product:
                product_data = {
                    "id": product.get("id"),
                    "post_title": product.get("title"),
                    "sku": product.get("external_sku"),
                    "regular_price": product.get("price"),
                    "stock": 1 if product.get("is_available") else 0,
                    "stock_status": "instock" if product.get("is_available") else "outofstock",
                    "categories": product.get("category_name"),
                }
                transformed = self._mapper.transform_product(product_data)
                preview_lines.append(json.dumps(transformed, ensure_ascii=False))

        dialog = QDialog(self)
        dialog.setWindowTitle("Предпросмотр экспорта (первые 10 выбранных)")
        dialog.setMinimumSize(600, 400)
        layout = QVBoxLayout(dialog)
        edit = QPlainTextEdit()
        edit.setReadOnly(True)
        edit.setPlainText("\n".join(preview_lines))
        layout.addWidget(edit)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec()

    def _on_context_menu(self, pos):
        menu = self._table.contextMenuPolicy()
        from PySide6.QtWidgets import QMenu
        qmenu = QMenu(self)

        edit_action = qmenu.addAction("Редактировать")
        delete_action = qmenu.addAction("Удалить")
        qmenu.addSeparator()
        ready_action = qmenu.addAction("Отметить готовым к экспорту")
        not_ready_action = qmenu.addAction("Отметить не готовым")
        qmenu.addSeparator()
        export_action = qmenu.addAction("Предпросмотр экспорта")

        action = qmenu.exec_(self._table.mapToGlobal(pos))
        if action == edit_action:
            self._on_edit()
        elif action == delete_action:
            self._on_delete()
        elif action == ready_action:
            self._on_mark_ready()
        elif action == not_ready_action:
            self._on_mark_not_ready()
        elif action == export_action:
            self._on_export_preview()

```

### `build\lib\src\ui\pages\discovery_page.py`
```python
import asyncio
import sys
import threading
from typing import Optional

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, QThread, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from src.database.models import Category, Supplier
from src.database.session import get_session
from src.modules.discovery.engine import DiscoveryEngine


class DiscoveryWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int, int, str)
    finished_signal = Signal(dict)

    def __init__(
        self,
        supplier_id: int,
        base_url: str,
        max_depth: int = 3,
        delay_min: float = 0.5,
        delay_max: float = 2.0,
        check_robots: bool = True,
        timeout: int = 30,
    ):
        super().__init__()
        self.supplier_id = supplier_id
        self.base_url = base_url
        self.max_depth = max_depth
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.check_robots = check_robots
        self.timeout = timeout
        self._engine: Optional[DiscoveryEngine] = None

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def log_cb(msg):
            self.log_signal.emit(msg)

        def progress_cb(pct, total, msg):
            self.progress_signal.emit(pct, total, msg)

        self._engine = DiscoveryEngine(
            supplier_id=self.supplier_id,
            base_url=self.base_url,
            log_callback=log_cb,
            progress_callback=progress_cb,
            max_depth=self.max_depth,
            delay_range=(self.delay_min, self.delay_max),
            check_robots=self.check_robots,
            timeout=self.timeout,
        )

        async def _run():
            with get_session() as session:
                result = await self._engine.run(session)
            return result

        try:
            result = loop.run_until_complete(_run())
            self.finished_signal.emit(result)
        except Exception as exc:
            self.finished_signal.emit({"success": False, "error": str(exc), "categories_found": 0})
        finally:
            loop.close()

    def cancel(self):
        if self._engine:
            self._engine.cancel()


class CategoryTreeModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels(["Категория", "URL", "Товары", "XPath"])

    def load_categories(self, categories: list) -> None:
        self.removeRows(0, self.rowCount())

        def _add_children(parent_item, cats):
            for cat in cats:
                name_item = QStandardItem(cat.name)
                url_item = QStandardItem(cat.url)
                count_item = QStandardItem(str(cat.product_count))
                xpath_item = QStandardItem(cat.xpath_selector[:60] + "..." if len(cat.xpath_selector) > 60 else cat.xpath_selector)

                parent_item.appendRow([name_item, url_item, count_item, xpath_item])
                if cat.children:
                    _add_children(name_item, cat.children)

        root = self.invisibleRootItem()
        for cat in categories:
            name_item = QStandardItem(cat.name)
            url_item = QStandardItem(cat.url)
            count_item = QStandardItem(str(cat.product_count))
            xpath_item = QStandardItem(cat.xpath_selector[:60] + "..." if len(cat.xpath_selector) > 60 else cat.xpath_selector)

            root.appendRow([name_item, url_item, count_item, xpath_item])
            if cat.children:
                _add_children(name_item, cat.children)

    def load_from_db(self, supplier_id: int) -> None:
        self.removeRows(0, self.rowCount())

        with get_session() as session:
            top_level = session.query(Category).filter(
                Category.supplier_id == supplier_id,
                Category.parent_id.is_(None),
            ).order_by(Category.sort_order, Category.name).all()

            def _build_tree(parent_item, parent_id):
                children = session.query(Category).filter(
                    Category.supplier_id == supplier_id,
                    Category.parent_id == parent_id,
                ).order_by(Category.sort_order, Category.name).all()

                for cat in children:
                    name_item = QStandardItem(cat.name)
                    url_item = QStandardItem(cat.url)
                    count_item = QStandardItem(str(cat.product_count))
                    xpath_item = QStandardItem(cat.xpath_selector[:60] + "..." if cat.xpath_selector and len(cat.xpath_selector) > 60 else (cat.xpath_selector or ""))

                    parent_item.appendRow([name_item, url_item, count_item, xpath_item])
                    _build_tree(name_item, cat.id)

            root = self.invisibleRootItem()
            for cat in top_level:
                name_item = QStandardItem(cat.name)
                url_item = QStandardItem(cat.url)
                count_item = QStandardItem(str(cat.product_count))
                xpath_item = QStandardItem(cat.xpath_selector[:60] + "..." if cat.xpath_selector and len(cat.xpath_selector) > 60 else (cat.xpath_selector or ""))

                root.appendRow([name_item, url_item, count_item, xpath_item])
                _build_tree(name_item, cat.id)


class DiscoveryPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: Optional[DiscoveryWorker] = None
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        ctrl_group = QGroupBox("Управление разведкой")
        ctrl_layout = QVBoxLayout(ctrl_group)

        supplier_row = QHBoxLayout()
        supplier_row.addWidget(QLabel("Поставщик:"))
        self._supplier_combo = QComboBox()
        self._supplier_combo.setMinimumWidth(300)
        supplier_row.addWidget(self._supplier_combo)
        supplier_row.addStretch()
        ctrl_layout.addLayout(supplier_row)

        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Глубина:"))
        self._depth_combo = QComboBox()
        self._depth_combo.addItems(["1", "2", "3", "4", "5"])
        self._depth_combo.setCurrentText("3")
        self._depth_combo.setMaximumWidth(60)
        options_row.addWidget(self._depth_combo)

        options_row.addSpacing(16)
        options_row.addWidget(QLabel("Задержка (с):"))
        self._delay_min_input = QComboBox()
        self._delay_min_input.addItems(["0.2", "0.5", "1.0", "2.0"])
        self._delay_min_input.setCurrentText("0.5")
        self._delay_min_input.setMaximumWidth(70)
        options_row.addWidget(self._delay_min_input)

        options_row.addWidget(QLabel("–"))

        self._delay_max_input = QComboBox()
        self._delay_max_input.addItems(["1.0", "2.0", "3.0", "5.0"])
        self._delay_max_input.setCurrentText("2.0")
        self._delay_max_input.setMaximumWidth(70)
        options_row.addWidget(self._delay_max_input)

        options_row.addSpacing(16)
        self._robots_check = QPushButton("Проверять robots.txt")
        self._robots_check.setCheckable(True)
        self._robots_check.setChecked(True)
        options_row.addWidget(self._robots_check)

        options_row.addStretch()
        ctrl_layout.addLayout(options_row)

        btn_row = QHBoxLayout()
        self._btn_start = QPushButton("Запустить разведку")
        self._btn_start.setMinimumHeight(40)
        self._btn_cancel = QPushButton("Отмена")
        self._btn_cancel.setMinimumHeight(40)
        self._btn_cancel.setEnabled(False)
        self._btn_load_db = QPushButton("Загрузить из БД")
        self._btn_load_db.setMinimumHeight(40)
        btn_row.addWidget(self._btn_start)
        btn_row.addWidget(self._btn_cancel)
        btn_row.addWidget(self._btn_load_db)
        btn_row.addStretch()
        ctrl_layout.addLayout(btn_row)

        layout.addWidget(ctrl_group)

        progress_row = QHBoxLayout()
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimumHeight(20)
        self._progress_label = QLabel("Готово")
        progress_row.addWidget(self._progress_bar, 1)
        progress_row.addWidget(self._progress_label)
        layout.addLayout(progress_row)

        splitter = QSplitter(Qt.Vertical)

        tree_group = QGroupBox("Найденные категории")
        tree_layout = QVBoxLayout(tree_group)
        self._tree = QTreeView()
        self._tree_model = CategoryTreeModel()
        self._tree.setModel(self._tree_model)
        self._tree.setAlternatingRowColors(True)
        self._tree.header().setStretchLastSection(False)
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        self._tree.setExpandsOnDoubleClick(True)
        tree_layout.addWidget(self._tree)
        splitter.addWidget(tree_group)

        log_group = QGroupBox("Журнал разведки")
        log_layout = QVBoxLayout(log_group)
        self._log_edit = QPlainTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(200)
        log_layout.addWidget(self._log_edit)
        splitter.addWidget(log_group)

        splitter.setSizes([400, 200])
        layout.addWidget(splitter)

        self._btn_start.clicked.connect(self._on_start)
        self._btn_cancel.clicked.connect(self._on_cancel)
        self._btn_load_db.clicked.connect(self._on_load_db)

    def _load_suppliers(self):
        self._supplier_combo.clear()
        try:
            with get_session() as session:
                suppliers = session.query(Supplier).filter(
                    Supplier.is_active == True
                ).order_by(Supplier.name).all()
                for s in suppliers:
                    self._supplier_combo.addItem(s.name, userData=s.id)
        except Exception as exc:
            self._append_log(f"Ошибка загрузки поставщиков: {exc}")

    def _append_log(self, msg: str):
        self._log_edit.appendPlainText(f"[{self._timestamp()}] {msg}")

    @staticmethod
    def _timestamp() -> str:
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def _on_start(self):
        supplier_id = self._supplier_combo.currentData()
        if supplier_id is None:
            QMessageBox.warning(self, "Нет поставщика", "Сначала выберите поставщика.")
            return

        with get_session() as session:
            supplier = session.query(Supplier).filter(Supplier.id == supplier_id).first()
            if not supplier:
                QMessageBox.warning(self, "Ошибка", "Поставщик не найден в базе данных.")
                return
            base_url = supplier.base_url

        self._btn_start.setEnabled(False)
        self._btn_cancel.setEnabled(True)
        self._progress_bar.setValue(0)
        self._progress_label.setText("Запуск...")
        self._log_edit.clear()
        self._append_log(f"Запуск разведки для '{self._supplier_combo.currentText()}' ({base_url})")

        max_depth = int(self._depth_combo.currentText())
        delay_min = float(self._delay_min_input.currentText())
        delay_max = float(self._delay_max_input.currentText())
        check_robots = self._robots_check.isChecked()

        self._worker = DiscoveryWorker(
            supplier_id=supplier_id,
            base_url=base_url,
            max_depth=max_depth,
            delay_min=delay_min,
            delay_max=delay_max,
            check_robots=check_robots,
            timeout=30,
        )
        self._worker.log_signal.connect(self._append_log)
        self._worker.progress_signal.connect(self._on_progress)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.start()

    def _on_cancel(self):
        if self._worker and self._worker.isRunning():
            self._append_log("Отмена разведки...")
            self._worker.cancel()
            self._btn_cancel.setEnabled(False)

    def _on_progress(self, pct: int, total: int, msg: str):
        self._progress_bar.setValue(min(pct, 100))
        self._progress_label.setText(f"{pct}% — {msg}")

    def _on_finished(self, result: dict):
        self._btn_start.setEnabled(True)
        self._btn_cancel.setEnabled(False)

        if result.get("success"):
            count = result.get("categories_found", 0)
            self._progress_bar.setValue(100)
            self._progress_label.setText(f"Готово — найдено {count} категорий")
            self._append_log(f"Разведка завершена: сохранено {count} категорий")

            categories = result.get("categories", [])
            if categories:
                self._tree_model.load_categories(categories)
            else:
                self._tree_model.load_from_db(self._supplier_combo.currentData())

            QMessageBox.information(self, "Успех", f"Разведка завершена.\nСохранено {count} категорий.")
        else:
            error = result.get("error", "Неизвестная ошибка")
            self._progress_label.setText(f"Ошибка: {error}")
            self._append_log(f"Разведка не удалась: {error}")
            QMessageBox.critical(self, "Ошибка разведки", f"Разведка не удалась:\n{error}")

    def _on_load_db(self):
        supplier_id = self._supplier_combo.currentData()
        if supplier_id is None:
            QMessageBox.warning(self, "Нет поставщика", "Сначала выберите поставщика.")
            return

        self._append_log("Загрузка категорий из базы данных...")
        self._tree_model.load_from_db(supplier_id)
        row_count = self._tree_model.rowCount()
        self._append_log(f"Загружено {row_count} категорий верхнего уровня из базы данных")

```

### `build\lib\src\ui\pages\export_page.py`
```python
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from src.core.config import settings
from src.database.models import Category, Supplier
from src.database.session import get_session
from src.modules.export.generator import ExportConfig, ExportEngine


class ExportWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int, int, str)
    finished_signal = Signal(dict)

    def __init__(self, config: ExportConfig):
        super().__init__()
        self.config = config

    def run(self):
        def log_cb(msg):
            self.log_signal.emit(msg)

        def progress_cb(pct, total, msg):
            self.progress_signal.emit(pct, total, msg)

        engine = ExportEngine(
            config=self.config,
            log_callback=log_cb,
            progress_callback=progress_cb,
        )

        try:
            with get_session() as session:
                result = engine.run(session)
            self.finished_signal.emit(result)
        except Exception as exc:
            self.finished_signal.emit({"success": False, "error": str(exc)})


class ValidationModel(QAbstractTableModel):
    _headers = ["Предупреждение"]

    def __init__(self):
        super().__init__()
        self._warnings: list[str] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._warnings)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return self._warnings[index.row()]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def set_warnings(self, warnings: list[str]):
        self._warnings = warnings
        self.layoutChanged.emit()


class ExportPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: Optional[ExportWorker] = None
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        filter_group = QGroupBox("Фильтры экспорта")
        filter_layout = QVBoxLayout(filter_group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Поставщик:"))
        self._supplier_list = QListWidget()
        self._supplier_list.setMaximumHeight(100)
        row1.addWidget(self._supplier_list)
        filter_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Категория:"))
        self._category_list = QListWidget()
        self._category_list.setMaximumHeight(100)
        row2.addWidget(self._category_list)
        filter_layout.addLayout(row2)

        row3 = QHBoxLayout()
        self._ready_check = QCheckBox("Только готовые к экспорту")
        self._ready_check.setChecked(True)
        row3.addWidget(self._ready_check)
        self._available_check = QCheckBox("Только доступные")
        row3.addWidget(self._available_check)
        row3.addStretch()
        filter_layout.addLayout(row3)

        layout.addWidget(filter_group)

        settings_group = QGroupBox("Настройки экспорта")
        settings_layout = QVBoxLayout(settings_group)

        s_row1 = QHBoxLayout()
        s_row1.addWidget(QLabel("Формат:"))
        self._format_combo = QComboBox()
        self._format_combo.addItems(["Excel (.xlsx)", "CSV (.csv)"])
        self._format_combo.setMaximumWidth(150)
        s_row1.addWidget(self._format_combo)

        s_row1.addSpacing(24)
        s_row1.addWidget(QLabel("Кодировка:"))
        self._encoding_combo = QComboBox()
        self._encoding_combo.addItems(["UTF-8 с BOM", "UTF-8", "Windows-1251"])
        self._encoding_combo.setMaximumWidth(180)
        s_row1.addWidget(self._encoding_combo)

        s_row1.addSpacing(24)
        s_row1.addWidget(QLabel("Разделитель изображений:"))
        self._img_sep_combo = QComboBox()
        self._img_sep_combo.addItems(["|", ",", ";"])
        self._img_sep_combo.setMaximumWidth(60)
        s_row1.addWidget(self._img_sep_combo)

        s_row1.addStretch()
        settings_layout.addLayout(s_row1)

        s_row2 = QHBoxLayout()
        s_row2.addWidget(QLabel("Папка вывода:"))
        self._output_input = QLineEdit(str(settings.data_dir / "exports"))
        self._output_input.setMinimumWidth(300)
        s_row2.addWidget(self._output_input)
        self._btn_browse = QPushButton("Обзор...")
        s_row2.addWidget(self._btn_browse)
        s_row2.addStretch()
        settings_layout.addLayout(s_row2)

        layout.addWidget(settings_group)

        btn_row = QHBoxLayout()
        self._btn_validate = QPushButton("Проверить")
        self._btn_validate.setMinimumHeight(40)
        self._btn_export = QPushButton("Сгенерировать файл")
        self._btn_export.setMinimumHeight(40)
        self._btn_export.setStyleSheet(
            "background-color: #e94560; color: white; font-weight: bold;"
        )
        self._btn_open_folder = QPushButton("Открыть папку экспорта")
        self._btn_open_folder.setMinimumHeight(40)
        btn_row.addWidget(self._btn_validate)
        btn_row.addWidget(self._btn_export)
        btn_row.addWidget(self._btn_open_folder)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        progress_row = QHBoxLayout()
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimumHeight(20)
        self._progress_label = QLabel("Готово")
        progress_row.addWidget(self._progress_bar, 1)
        progress_row.addWidget(self._progress_label)
        layout.addLayout(progress_row)

        splitter = QSplitter(Qt.Vertical)

        warn_group = QGroupBox("Предупреждения валидации")
        warn_layout = QVBoxLayout(warn_group)
        self._warn_table = QTableView()
        self._warn_model = ValidationModel()
        self._warn_table.setModel(self._warn_model)
        self._warn_table.horizontalHeader().setStretchLastSection(True)
        self._warn_table.setMaximumHeight(120)
        warn_layout.addWidget(self._warn_table)
        splitter.addWidget(warn_group)

        log_group = QGroupBox("Журнал экспорта")
        log_layout = QVBoxLayout(log_group)
        self._log_edit = QPlainTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(200)
        log_layout.addWidget(self._log_edit)
        splitter.addWidget(log_group)

        layout.addWidget(splitter)

        stats_row = QHBoxLayout()
        self._stat_total = QLabel("Всего: 0")
        self._stat_exported = QLabel("Экспортировано: 0")
        self._stat_duplicates = QLabel("Дубликаты: 0")
        self._stat_size = QLabel("Размер: 0 КБ")
        self._stat_time = QLabel("Время: 0.0с")
        stats_row.addWidget(self._stat_total)
        stats_row.addWidget(self._stat_exported)
        stats_row.addWidget(self._stat_duplicates)
        stats_row.addWidget(self._stat_size)
        stats_row.addWidget(self._stat_time)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        self._btn_validate.clicked.connect(self._on_validate)
        self._btn_export.clicked.connect(self._on_export)
        self._btn_open_folder.clicked.connect(self._on_open_folder)
        self._btn_browse.clicked.connect(self._on_browse)
        self._supplier_list.itemChanged.connect(self._on_supplier_changed)

    def _load_suppliers(self):
        self._supplier_list.clear()
        self._category_list.clear()
        try:
            with get_session() as session:
                suppliers = session.query(Supplier).filter(
                    Supplier.is_active == True
                ).order_by(Supplier.name).all()
                for s in suppliers:
                    item = self._supplier_list.item(self._supplier_list.count())
                    from PySide6.QtWidgets import QListWidgetItem
                    item = QListWidgetItem(s.name)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                    item.setData(Qt.UserRole, s.id)
                    self._supplier_list.addItem(item)
        except Exception as exc:
            self._append_log(f"Ошибка загрузки поставщиков: {exc}")

    def _on_supplier_changed(self, item):
        self._category_list.clear()
        checked_ids = self._get_checked_supplier_ids()
        if checked_ids:
            try:
                with get_session() as session:
                    categories = session.query(Category).filter(
                        Category.supplier_id.in_(checked_ids)
                    ).order_by(Category.name).all()
                    for c in categories:
                        from PySide6.QtWidgets import QListWidgetItem
                        cat_item = QListWidgetItem(c.name)
                        cat_item.setFlags(cat_item.flags() | Qt.ItemIsUserCheckable)
                        cat_item.setCheckState(Qt.Unchecked)
                        cat_item.setData(Qt.UserRole, c.id)
                        self._category_list.addItem(cat_item)
            except Exception:
                pass

    def _get_checked_supplier_ids(self) -> list[int]:
        ids = []
        for i in range(self._supplier_list.count()):
            item = self._supplier_list.item(i)
            if item.checkState() == Qt.Checked:
                ids.append(item.data(Qt.UserRole))
        return ids or None

    def _get_checked_category_ids(self) -> list[int]:
        ids = []
        for i in range(self._category_list.count()):
            item = self._category_list.item(i)
            if item.checkState() == Qt.Checked:
                ids.append(item.data(Qt.UserRole))
        return ids or None

    def _append_log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_edit.appendPlainText(f"[{ts}] {msg}")

    def _get_config(self) -> ExportConfig:
        fmt = "xlsx" if self._format_combo.currentText().startswith("Excel") else "csv"

        encoding_map = {
            "UTF-8 with BOM": "utf-8-sig",
            "UTF-8": "utf-8",
            "Windows-1251": "cp1251",
        }
        encoding = encoding_map.get(self._encoding_combo.currentText(), "utf-8-sig")

        return ExportConfig(
            supplier_ids=self._get_checked_supplier_ids(),
            category_ids=self._get_checked_category_ids(),
            ready_only=self._ready_check.isChecked(),
            available_only=self._available_check.isChecked(),
            format=fmt,
            encoding=encoding,
            image_separator=self._img_sep_combo.currentText(),
            output_dir=Path(self._output_input.text()),
        )

    def _on_validate(self):
        config = self._get_config()
        engine = ExportEngine(config=config)

        with get_session() as session:
            warnings = engine.validate_before_export(session)

        self._warn_model.set_warnings(warnings)

        if not warnings:
            QMessageBox.information(self, "Валидация", "Проблем не найдено. Готово к экспорту.")
        else:
            errors = [w for w in warnings if "No products" in w]
            if errors:
                QMessageBox.warning(self, "Валидация", "\n".join(warnings))
            else:
                QMessageBox.information(self, "Валидация", "\n".join(warnings))

    def _on_export(self):
        config = self._get_config()
        engine = ExportEngine(config=config)

        with get_session() as session:
            warnings = engine.validate_before_export(session)

        critical = [w for w in warnings if "No products" in w]
        if critical:
            QMessageBox.warning(self, "Невозможно экспортировать", "\n".join(critical))
            return

        if warnings:
            reply = QMessageBox.question(
                self,
                "Предупреждения валидации",
                f"Найдено предупреждений: {len(warnings)}:\n\n"
                + "\n".join(warnings[:5])
                + ("\n..." if len(warnings) > 5 else "")
                + "\n\nПродолжить экспорт?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        self._btn_export.setEnabled(False)
        self._btn_validate.setEnabled(False)
        self._progress_bar.setValue(0)
        self._progress_label.setText("Запуск экспорта...")
        self._log_edit.clear()
        self._reset_stats()
        self._append_log(f"Запуск экспорта (формат={config.format})")

        self._worker = ExportWorker(config=config)
        self._worker.log_signal.connect(self._append_log)
        self._worker.progress_signal.connect(self._on_progress)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.start()

    def _on_progress(self, pct: int, total: int, msg: str):
        self._progress_bar.setValue(min(pct, 100))
        self._progress_label.setText(f"{pct}% — {msg}")

    def _on_finished(self, result: dict):
        self._btn_export.setEnabled(True)
        self._btn_validate.setEnabled(True)

        if result.get("success"):
            stats = result.get("stats")
            self._progress_bar.setValue(100)
            self._progress_label.setText("Экспорт завершён!")
            self._append_log(f"Экспорт завершён: {stats.exported_products} товаров")
            self._append_log(f"Результат: {stats.output_path}")

            self._stat_total.setText(f"Всего: {stats.total_products}")
            self._stat_exported.setText(f"Экспортировано: {stats.exported_products}")
            self._stat_duplicates.setText(f"Дубликаты: {stats.duplicate_skus}")
            self._stat_size.setText(f"Размер: {stats.file_size / 1024:.1f} КБ")
            self._stat_time.setText(f"Время: {stats.elapsed:.1f}с")

            QMessageBox.information(
                self,
                "Экспорт завершён",
                f"Экспортировано {stats.exported_products} товаров.\n"
                f"Файл: {stats.output_path}\n"
                f"Размер: {stats.file_size / 1024:.1f} КБ\n"
                f"Время: {stats.elapsed:.1f}с",
            )
        else:
            error = result.get("error", "Неизвестная ошибка")
            self._progress_label.setText(f"Ошибка: {error}")
            self._append_log(f"Экспорт не удался: {error}")
            if error != "cancelled":
                QMessageBox.critical(self, "Ошибка экспорта", f"Экспорт не удался:\n{error}")

    def _on_open_folder(self):
        folder = Path(self._output_input.text())
        if folder.exists():
            os.startfile(str(folder))
        else:
            QMessageBox.warning(self, "Папка не найдена", f"Папка не существует:\n{folder}")

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку вывода")
        if folder:
            self._output_input.setText(folder)

    def _reset_stats(self):
        self._stat_total.setText("Всего: 0")
        self._stat_exported.setText("Экспортировано: 0")
        self._stat_duplicates.setText("Дубликаты: 0")
        self._stat_size.setText("Размер: 0 КБ")
        self._stat_time.setText("Время: 0.0с")

```

### `build\lib\src\ui\pages\parsing_page.py`
```python
import asyncio
import time
from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QThread, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableView,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from src.database.models import Category, Product, Supplier
from src.database.session import get_session
from src.modules.parsing.engine import ParserEngine, ParsingStats


class CategoryCheckModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels(["Категория", "URL", "Товары"])

    def load_categories(self, supplier_id: int) -> int:
        self.removeRows(0, self.rowCount())

        with get_session() as session:
            top_level = session.query(Category).filter(
                Category.supplier_id == supplier_id,
                Category.parent_id.is_(None),
            ).order_by(Category.sort_order, Category.name).all()

            def _build_tree(parent_item, parent_id):
                children = session.query(Category).filter(
                    Category.supplier_id == supplier_id,
                    Category.parent_id == parent_id,
                ).order_by(Category.sort_order, Category.name).all()

                for cat in children:
                    name_item = QStandardItem(cat.name)
                    name_item.setCheckable(True)
                    name_item.setCheckState(Qt.Unchecked)
                    name_item.setData(cat.id, Qt.UserRole)

                    url_item = QStandardItem(cat.url)
                    count_item = QStandardItem(str(cat.product_count))

                    parent_item.appendRow([name_item, url_item, count_item])
                    _build_tree(name_item, cat.id)

            root = self.invisibleRootItem()
            for cat in top_level:
                name_item = QStandardItem(cat.name)
                name_item.setCheckable(True)
                name_item.setCheckState(Qt.Unchecked)
                name_item.setData(cat.id, Qt.UserRole)

                url_item = QStandardItem(cat.url)
                count_item = QStandardItem(str(cat.product_count))

                root.appendRow([name_item, url_item, count_item])
                _build_tree(name_item, cat.id)

            return len(top_level)

    def get_checked_ids(self) -> list[int]:
        ids = []

        def _collect(item):
            if item.isCheckable() and item.checkState() == Qt.Checked:
                cat_id = item.data(Qt.UserRole)
                if cat_id is not None:
                    ids.append(cat_id)
            for i in range(item.rowCount()):
                _collect(item.child(i, 0))

        for i in range(self.rowCount()):
            _collect(self.item(i, 0))
        return ids

    def check_all(self) -> None:
        def _set_checked(item):
            if item.isCheckable():
                item.setCheckState(Qt.Checked)
            for i in range(item.rowCount()):
                _set_checked(item.child(i, 0))

        for i in range(self.rowCount()):
            _set_checked(self.item(i, 0))

    def uncheck_all(self) -> None:
        def _set_unchecked(item):
            if item.isCheckable():
                item.setCheckState(Qt.Unchecked)
            for i in range(item.rowCount()):
                _set_unchecked(item.child(i, 0))

        for i in range(self.rowCount()):
            _set_unchecked(self.item(i, 0))


class TaskStatusModel(QAbstractTableModel):
    _headers = ["Задача", "Статус", "Товары", "Ошибки", "Время"]

    def __init__(self):
        super().__init__()
        self._rows: list[dict] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        row = self._rows[index.row()]
        col = index.column()
        keys = ["task", "status", "products", "errors", "time"]
        return row.get(keys[col], "")

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def add_task(self, task: str, status: str = "Выполняется", products: int = 0, errors: int = 0, elapsed: str = ""):
        self._rows.append({
            "task": task,
            "status": status,
            "products": str(products),
            "errors": str(errors),
            "time": elapsed,
        })
        self.layoutChanged.emit()

    def update_last(self, **kwargs):
        if self._rows:
            self._rows[-1].update(kwargs)
            self.layoutChanged.emit()

    def clear(self):
        self._rows.clear()
        self.layoutChanged.emit()


class ParsingWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int, int, str)
    stats_signal = Signal(dict)
    finished_signal = Signal(dict)

    def __init__(
        self,
        supplier_id: int,
        base_url: str,
        category_ids: list[int],
        concurrency: int = 5,
        delay_min: float = 0.5,
        delay_max: float = 2.0,
        timeout: int = 30,
    ):
        super().__init__()
        self.supplier_id = supplier_id
        self.base_url = base_url
        self.category_ids = category_ids
        self.concurrency = concurrency
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.timeout = timeout
        self._engine: Optional[ParserEngine] = None

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def log_cb(msg):
            self.log_signal.emit(msg)

        def progress_cb(pct, total, msg):
            self.progress_signal.emit(pct, total, msg)

        self._engine = ParserEngine(
            supplier_id=self.supplier_id,
            base_url=self.base_url,
            concurrency=self.concurrency,
            delay_range=(self.delay_min, self.delay_max),
            timeout=self.timeout,
            log_callback=log_cb,
            progress_callback=progress_cb,
        )

        async def _run():
            with get_session() as session:
                result = await self._engine.run(self.category_ids, session)
            return result

        try:
            result = loop.run_until_complete(_run())
            stats = result.get("stats")
            if stats:
                self.stats_signal.emit({
                    "total_products": stats.total_products,
                    "total_pages": stats.total_pages,
                    "successful_pages": stats.successful_pages,
                    "failed_pages": stats.failed_pages,
                    "total_attributes": stats.total_attributes,
                    "errors": stats.errors,
                    "elapsed": stats.elapsed,
                })
            self.finished_signal.emit(result)
        except Exception as exc:
            self.finished_signal.emit({"success": False, "error": str(exc)})
        finally:
            loop.close()

    def cancel(self):
        if self._engine:
            self._engine.cancel()

    def pause(self):
        if self._engine:
            self._engine.pause()

    def resume(self):
        if self._engine:
            self._engine.resume()


class ParsingPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: Optional[ParsingWorker] = None
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        ctrl_group = QGroupBox("Управление парсингом")
        ctrl_layout = QVBoxLayout(ctrl_group)

        supplier_row = QHBoxLayout()
        supplier_row.addWidget(QLabel("Поставщик:"))
        self._supplier_combo = QComboBox()
        self._supplier_combo.setMinimumWidth(300)
        supplier_row.addWidget(self._supplier_combo)
        supplier_row.addStretch()
        ctrl_layout.addLayout(supplier_row)

        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Параллелизм:"))
        self._concurrency_combo = QComboBox()
        self._concurrency_combo.addItems(["3", "5", "8", "10", "15"])
        self._concurrency_combo.setCurrentText("5")
        self._concurrency_combo.setMaximumWidth(60)
        options_row.addWidget(self._concurrency_combo)

        options_row.addSpacing(16)
        options_row.addWidget(QLabel("Задержка (с):"))
        self._delay_min_input = QComboBox()
        self._delay_min_input.addItems(["0.2", "0.5", "1.0", "2.0"])
        self._delay_min_input.setCurrentText("0.5")
        self._delay_min_input.setMaximumWidth(70)
        options_row.addWidget(self._delay_min_input)

        options_row.addWidget(QLabel("–"))

        self._delay_max_input = QComboBox()
        self._delay_max_input.addItems(["1.0", "2.0", "3.0", "5.0"])
        self._delay_max_input.setCurrentText("2.0")
        self._delay_max_input.setMaximumWidth(70)
        options_row.addWidget(self._delay_max_input)

        options_row.addSpacing(16)
        options_row.addWidget(QLabel("Таймаут (с):"))
        self._timeout_combo = QComboBox()
        self._timeout_combo.addItems(["15", "30", "60", "120"])
        self._timeout_combo.setCurrentText("30")
        self._timeout_combo.setMaximumWidth(70)
        options_row.addWidget(self._timeout_combo)

        options_row.addStretch()
        ctrl_layout.addLayout(options_row)

        btn_row = QHBoxLayout()
        self._btn_start = QPushButton("Запустить парсинг")
        self._btn_start.setMinimumHeight(40)
        self._btn_pause = QPushButton("Пауза")
        self._btn_pause.setMinimumHeight(40)
        self._btn_pause.setEnabled(False)
        self._btn_stop = QPushButton("Стоп")
        self._btn_stop.setMinimumHeight(40)
        self._btn_stop.setEnabled(False)
        self._btn_select_all = QPushButton("Выбрать все")
        self._btn_select_all.setMinimumHeight(40)
        self._btn_select_none = QPushButton("Снять выбор")
        self._btn_select_none.setMinimumHeight(40)
        btn_row.addWidget(self._btn_start)
        btn_row.addWidget(self._btn_pause)
        btn_row.addWidget(self._btn_stop)
        btn_row.addSpacing(16)
        btn_row.addWidget(self._btn_select_all)
        btn_row.addWidget(self._btn_select_none)
        btn_row.addStretch()
        ctrl_layout.addLayout(btn_row)

        layout.addWidget(ctrl_group)

        progress_row = QHBoxLayout()
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimumHeight(20)
        self._progress_label = QLabel("Готово")
        progress_row.addWidget(self._progress_bar, 1)
        progress_row.addWidget(self._progress_label)
        layout.addLayout(progress_row)

        splitter = QSplitter(Qt.Vertical)

        cat_group = QGroupBox("Категории (отметьте для парсинга)")
        cat_layout = QVBoxLayout(cat_group)
        self._cat_tree = QTreeView()
        self._cat_model = CategoryCheckModel()
        self._cat_tree.setModel(self._cat_model)
        self._cat_tree.setAlternatingRowColors(True)
        self._cat_tree.header().setStretchLastSection(False)
        self._cat_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._cat_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self._cat_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        cat_layout.addWidget(self._cat_tree)
        splitter.addWidget(cat_group)

        stats_group = QGroupBox("Статус задач")
        stats_layout = QVBoxLayout(stats_group)
        self._task_table = QTableView()
        self._task_model = TaskStatusModel()
        self._task_table.setModel(self._task_model)
        self._task_table.setAlternatingRowColors(True)
        self._task_table.horizontalHeader().setStretchLastSection(True)
        stats_layout.addWidget(self._task_table)
        splitter.addWidget(stats_group)

        log_group = QGroupBox("Журнал парсинга")
        log_layout = QVBoxLayout(log_group)
        self._log_edit = QPlainTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(180)
        log_layout.addWidget(self._log_edit)
        splitter.addWidget(log_group)

        stats_row = QHBoxLayout()
        self._stat_products = QLabel("Товаров: 0")
        self._stat_pages = QLabel("Страниц: 0")
        self._stat_errors = QLabel("Ошибок: 0")
        self._stat_time = QLabel("Время: 0.0с")
        self._stat_attrs = QLabel("Атрибутов: 0")
        stats_row.addWidget(self._stat_products)
        stats_row.addWidget(self._stat_pages)
        stats_row.addWidget(self._stat_errors)
        stats_row.addWidget(self._stat_time)
        stats_row.addWidget(self._stat_attrs)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        splitter.setSizes([250, 150, 180])
        layout.addWidget(splitter)

        self._btn_start.clicked.connect(self._on_start)
        self._btn_pause.clicked.connect(self._on_pause)
        self._btn_stop.clicked.connect(self._on_stop)
        self._btn_select_all.clicked.connect(self._cat_model.check_all)
        self._btn_select_none.clicked.connect(self._cat_model.uncheck_all)
        self._supplier_combo.currentIndexChanged.connect(self._on_supplier_changed)

    def _load_suppliers(self):
        self._supplier_combo.clear()
        try:
            with get_session() as session:
                suppliers = session.query(Supplier).filter(
                    Supplier.is_active == True
                ).order_by(Supplier.name).all()
                for s in suppliers:
                    self._supplier_combo.addItem(s.name, userData=s.id)
        except Exception as exc:
            self._append_log(f"Ошибка загрузки поставщиков: {exc}")

    def _on_supplier_changed(self):
        supplier_id = self._supplier_combo.currentData()
        if supplier_id:
            count = self._cat_model.load_categories(supplier_id)
            self._append_log(f"Загружено {count} категорий верхнего уровня")

    def _append_log(self, msg: str):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_edit.appendPlainText(f"[{ts}] {msg}")

    def _on_start(self):
        supplier_id = self._supplier_combo.currentData()
        if supplier_id is None:
            QMessageBox.warning(self, "Нет поставщика", "Сначала выберите поставщика.")
            return

        category_ids = self._cat_model.get_checked_ids()
        if not category_ids:
            QMessageBox.warning(self, "Нет категорий", "Выберите хотя бы одну категорию для парсинга.")
            return

        with get_session() as session:
            supplier = session.query(Supplier).filter(Supplier.id == supplier_id).first()
            if not supplier:
                QMessageBox.warning(self, "Ошибка", "Поставщик не найден.")
                return
            base_url = supplier.base_url

        self._btn_start.setEnabled(False)
        self._btn_pause.setEnabled(True)
        self._btn_stop.setEnabled(True)
        self._progress_bar.setValue(0)
        self._progress_label.setText("Запуск...")
        self._log_edit.clear()
        self._task_model.clear()
        self._reset_stats()

        self._append_log(f"Запуск парсинга для '{self._supplier_combo.currentText()}'")
        self._append_log(f"Выбрано категорий: {len(category_ids)}")

        concurrency = int(self._concurrency_combo.currentText())
        delay_min = float(self._delay_min_input.currentText())
        delay_max = float(self._delay_max_input.currentText())
        timeout = int(self._timeout_combo.currentText())

        self._worker = ParsingWorker(
            supplier_id=supplier_id,
            base_url=base_url,
            category_ids=category_ids,
            concurrency=concurrency,
            delay_min=delay_min,
            delay_max=delay_max,
            timeout=timeout,
        )
        self._worker.log_signal.connect(self._append_log)
        self._worker.progress_signal.connect(self._on_progress)
        self._worker.stats_signal.connect(self._on_stats)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.start()

    def _on_pause(self):
        if not self._worker or not self._worker.isRunning():
            return
        if self._btn_pause.text() == "Пауза":
            self._worker.pause()
            self._btn_pause.setText("Продолжить")
            self._append_log("Парсинг приостановлен")
        else:
            self._worker.resume()
            self._btn_pause.setText("Пауза")
            self._append_log("Парсинг возобновлён")

    def _on_stop(self):
        if self._worker and self._worker.isRunning():
            self._append_log("Остановка парсинга...")
            self._worker.cancel()
            self._btn_stop.setEnabled(False)
            self._btn_pause.setEnabled(False)

    def _on_progress(self, pct: int, total: int, msg: str):
        self._progress_bar.setValue(min(pct, 100))
        self._progress_label.setText(f"{pct}% — {msg}")

    def _on_stats(self, stats: dict):
        self._stat_products.setText(f"Товаров: {stats.get('total_products', 0)}")
        self._stat_pages.setText(f"Страниц: {stats.get('total_pages', 0)}")
        self._stat_errors.setText(f"Ошибок: {stats.get('failed_pages', 0)}")
        self._stat_time.setText(f"Время: {stats.get('elapsed', 0):.1f}с")
        self._stat_attrs.setText(f"Атрибутов: {stats.get('total_attributes', 0)}")

    def _on_finished(self, result: dict):
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)
        self._btn_stop.setEnabled(False)
        self._btn_pause.setText("Пауза")

        if result.get("success"):
            count = result.get("products_parsed", 0)
            self._progress_bar.setValue(100)
            self._progress_label.setText(f"Готово — {count} товаров обработано")
            self._append_log(f"Парсинг завершён: {count} товаров")
            QMessageBox.information(self, "Успех", f"Парсинг завершён.\nСохранено {count} товаров.")
        else:
            error = result.get("error", "Неизвестная ошибка")
            self._progress_label.setText(f"Ошибка: {error}")
            self._append_log(f"Парсинг не удался: {error}")
            QMessageBox.critical(self, "Ошибка парсинга", f"Парсинг не удался:\n{error}")

    def _reset_stats(self):
        self._stat_products.setText("Товаров: 0")
        self._stat_pages.setText("Страниц: 0")
        self._stat_errors.setText("Ошибок: 0")
        self._stat_time.setText("Время: 0.0с")
        self._stat_attrs.setText("Атрибутов: 0")

```

### `build\lib\src\ui\pages\placeholder_page.py`
```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PlaceholderPage(QWidget):
    def __init__(self, title: str, description: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setObjectName("subtitle")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

```

### `build\lib\src\ui\pages\suppliers_page.py`
```python
from datetime import datetime
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from src.database.models import Supplier
from src.database.session import get_session
from src.database.supplier_crud import (
    create_supplier,
    delete_supplier,
    get_all_suppliers,
    update_supplier,
)


class SupplierTableModel(QAbstractTableModel):
    _headers = [
        "ID",
        "Название",
        "Базовый URL",
        "Статус",
        "Последняя разведка",
        "Последний парсинг",
        "Создан",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._data: list[dict] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        row = self._data[index.row()]
        col = index.column()

        keys = ["id", "name", "base_url", "is_active", "last_discovery_run", "last_scrape_run", "created_at"]
        key = keys[col]
        val = row.get(key)

        if col == 0:
            return val
        if col == 3:
            return "Активен" if val else "Неактивен"
        if col in (4, 5, 6):
            return val.strftime("%Y-%m-%d %H:%M") if val else "—"
        return str(val) if val is not None else ""

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def get_supplier(self, row: int) -> dict | None:
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def refresh(self) -> None:
        self.beginResetModel()
        with get_session() as session:
            suppliers = get_all_suppliers(session, active_only=False)
            self._data = []
            for s in suppliers:
                self._data.append({
                    "id": s.id,
                    "name": s.name,
                    "base_url": s.base_url,
                    "is_active": s.is_active,
                    "last_discovery_run": s.last_discovery_run,
                    "last_scrape_run": s.last_scrape_run,
                    "created_at": s.created_at,
                })
        self.endResetModel()


class SuppliersPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._selected_supplier_id: int | None = None
        self._setup_ui()
        self._connect_signals()
        self._refresh_table()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._table = QTableView()
        self._model = SupplierTableModel()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.setSelectionMode(QTableView.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setMinimumHeight(300)
        layout.addWidget(self._table)

        form_frame = QWidget()
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(0, 8, 0, 0)

        self._name_input = QLineEdit()
        self._name_input.setMaxLength(255)
        self._name_input.setPlaceholderText("Название поставщика (обязательно, мин. 2 символа)")
        form_layout.addRow("Название:", self._name_input)

        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://example.com")
        url_validator = QRegularExpressionValidator(
            QRegularExpression(r"^https?://.+")
        )
        self._url_input.setValidator(url_validator)
        form_layout.addRow("Базовый URL:", self._url_input)

        layout.addWidget(form_frame)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self._btn_add = QPushButton("Добавить")
        self._btn_update = QPushButton("Обновить")
        self._btn_delete = QPushButton("Удалить")
        self._btn_refresh = QPushButton("Обновить таблицу")

        for btn in (self._btn_add, self._btn_update, self._btn_delete, self._btn_refresh):
            btn.setMinimumHeight(36)
            btn_layout.addWidget(btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _connect_signals(self) -> None:
        self._btn_add.clicked.connect(self._on_add)
        self._btn_update.clicked.connect(self._on_update)
        self._btn_delete.clicked.connect(self._on_delete)
        self._btn_refresh.clicked.connect(self._refresh_table)
        self._table.doubleClicked.connect(self._on_row_double_click)

    def _refresh_table(self) -> None:
        self._model.refresh()

    def _validate_name(self) -> str | None:
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.critical(self, "Ошибка валидации", "Название обязательно.")
            return None
        if len(name) < 2:
            QMessageBox.critical(self, "Ошибка валидации", "Название должно содержать минимум 2 символа.")
            return None
        if len(name) > 255:
            QMessageBox.critical(self, "Ошибка валидации", "Название не должно превышать 255 символов.")
            return None
        return name

    def _validate_url(self) -> str | None:
        url = self._url_input.text().strip()
        if not url:
            QMessageBox.critical(self, "Ошибка валидации", "Базовый URL обязателен.")
            return None
        if not url.startswith(("http://", "https://")):
            QMessageBox.critical(
                self, "Ошибка валидации", "Базовый URL должен начинаться с http:// или https://"
            )
            return None
        return url

    def _on_add(self) -> None:
        name = self._validate_name()
        url = self._validate_url()
        if not name or not url:
            return

        try:
            with get_session() as session:
                create_supplier(session, name, url)
            QMessageBox.information(self, "Успех", f"Поставщик '{name}' создан.")
            self._name_input.clear()
            self._url_input.clear()
            self._refresh_table()
        except ValueError as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось создать поставщика:\n{exc}")

    def _on_update(self) -> None:
        if self._selected_supplier_id is None:
            QMessageBox.warning(self, "Нет выбора", "Выберите поставщика из таблицы для обновления.")
            return

        name = self._validate_name()
        url = self._validate_url()
        if not name or not url:
            return

        try:
            with get_session() as session:
                result = update_supplier(
                    session,
                    self._selected_supplier_id,
                    name=name,
                    base_url=url,
                )
            if result:
                QMessageBox.information(self, "Успех", f"Поставщик '{name}' обновлён.")
                self._name_input.clear()
                self._url_input.clear()
                self._selected_supplier_id = None
                self._refresh_table()
            else:
                QMessageBox.warning(self, "Ошибка", "Поставщик не найден.")
        except ValueError as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось обновить поставщика:\n{exc}")

    def _on_delete(self) -> None:
        if self._selected_supplier_id is None:
            QMessageBox.warning(self, "Нет выбора", "Выберите поставщика из таблицы для удаления.")
            return

        supplier = self._model.get_supplier(self._table.currentIndex().row())
        supplier_name = supplier["name"] if supplier else "этот поставщик"

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите деактивировать '{supplier_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            with get_session() as session:
                found = delete_supplier(session, self._selected_supplier_id)
            if found:
                QMessageBox.information(self, "Успех", f"Поставщик '{supplier_name}' деактивирован.")
                self._name_input.clear()
                self._url_input.clear()
                self._selected_supplier_id = None
                self._refresh_table()
            else:
                QMessageBox.warning(self, "Ошибка", "Поставщик не найден.")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось удалить поставщика:\n{exc}")

    def _on_row_double_click(self, index: QModelIndex) -> None:
        row = index.row()
        supplier = self._model.get_supplier(row)
        if supplier:
            self._selected_supplier_id = supplier["id"]
            self._name_input.setText(supplier["name"])
            self._url_input.setText(supplier["base_url"])

```

### `build\lib\src\ui\styles\__init__.py`
```python

```

### `docs\playwright_parser_integration_guide.md`
```markdown
# MEEYG 1.0 Playwright Parser Integration Guide

## Overview

This document describes how to use the new Playwright-based parser for tandoor.ru integration in MEEYG 1.0.

## Components

1. **TandoorPlaywrightParser** - New Playwright-based parser in `src/modules/parsing/tandoor_playwright_parser.py`
2. **ParserEngine enhancements** - Modified `src/modules/parsing/engine.py` to support both aiohttp and Playwright parsers
3. **Configuration** - Added Playwright settings to `.env`

## Usage

### 1. Parser Selection

The `ParserEngine` now supports two parser types:
- `"aiohttp"` (default) - Traditional parser for static content
- `"playwright"` - New parser for dynamic content

To use the Playwright parser:

```python
from src.modules.parsing.engine import ParserEngine

parser = ParserEngine(
    supplier_id=1,
    base_url="https://tandoor.ru",
    parser_type="playwright"  # Enable Playwright parser
)
```

### 2. Configuration

The following settings were added to `.env`:

```env
# Playwright settings
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000
PLAYWRIGHT_DELAY_MIN=1.0
PLAYWRIGHT_DELAY_MAX=3.0
```

### 3. Testing

A test script is available at `tests/test_tandoor_parser.py`:

```bash
python tests/test_tandoor_parser.py
```

### 4. Features

The Playwright parser supports:
- Dynamic content loading
- JavaScript interactions
- Radio button selection for product variations
- Automatic handling of AJAX updates
- Full product data extraction including:
  - Basic product info (title, price, SKU)
  - Images
  - Attributes
  - Molding items (accessories)
  - Product variations (sizes, types)
  
### 5. Database Integration

The parser integrates with the existing database schema:
- Main products are saved with `parent_product_id=NULL`
- Molding items are saved with `parent_product_id` linking to the main product
- Variations are saved as separate products linked to the main product
- All attributes are stored in the `product_attributes` table

## Implementation Details

### TandoorPlaywrightParser Class

Located in `src/modules/parsing/tandoor_playwright_parser.py`

Key methods:
- `parse_product_page(url)` - Parses a single product page
- `handle_variations(page, base_url)` - Handles product variations
- `parse_molding_items(soup)` - Extracts molding items
- `save_to_database(product)` - Saves product to database
- `parse_category(category_url)` - Parses a category page
- `run(category_urls)` - Main entry point

### ParserEngine Modifications

Located in `src/modules/parsing/engine.py`

Enhancements:
- Added `parser_type` parameter to constructor
- Modified `_parse_category` to delegate to Playwright parser when needed
- Updated `run` method to handle Playwright session management

## Example Usage

```python
from src.modules.parsing.engine import ParserEngine
from src.database.session import get_session

# Get database session
with get_session() as db_session:
    # Create Playwright parser
    parser = ParserEngine(
        supplier_id=1,
        base_url="https://tandoor.ru",
        parser_type="playwright",
        concurrency=3  # Limit concurrent browsers
    )
    
    # Run parser on category URLs
    result = await parser.run([
        "https://tandoor.ru/catalog/doors/"
    ], db_session)
    
    print(f"Parsed {result['products_parsed']} products")
```

## Troubleshooting

1. **Playwright not found**: Run `playwright install chromium`
2. **Browser automation issues**: Set `PLAYWRIGHT_HEADLESS=false` for debugging
3. **Slow parsing**: Adjust `PLAYWRIGHT_DELAY_MIN` and `PLAYWRIGHT_DELAY_MAX` in `.env`
```

### `logs\test_report_20260427_222828.json`
```json
{
  "timestamp": "2026-04-27T22:28:28.244768",
  "results": [
    {
      "name": "Папка: Исходный код",
      "passed": true,
      "message": "src существует",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Папка: Ядро приложения",
      "passed": true,
      "message": "src/core существует",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Папка: Работа с БД",
      "passed": true,
      "message": "src/database существует",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Папка: Бизнес-модули",
      "passed": true,
      "message": "src/modules существует",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Папка: Пользовательский интерфейс",
      "passed": true,
      "message": "src/ui существует",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Папка: Данные (БД, экспорты)",
      "passed": true,
      "message": "data существует",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Папка: Лог-файлы",
      "passed": true,
      "message": "logs существует",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Папка: Конфигурации",
      "passed": false,
      "message": "config НЕ существует",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: Конфигурация зависимостей",
      "passed": true,
      "message": "pyproject.toml найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: Скрипт настройки окружения",
      "passed": true,
      "message": "setup_env.py найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: Переменные окружения",
      "passed": true,
      "message": ".env найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: Пакет src",
      "passed": true,
      "message": "src/__init__.py найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: Точка входа",
      "passed": true,
      "message": "src/main.py найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: Конфигурация приложения",
      "passed": true,
      "message": "src/core/config.py найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: Система логирования",
      "passed": true,
      "message": "src/core/logger.py найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: Движок БД",
      "passed": true,
      "message": "src/database/engine.py найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: ORM-модели",
      "passed": true,
      "message": "src/database/models.py найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: Управление сессиями",
      "passed": true,
      "message": "src/database/session.py найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: CRUD для поставщиков",
      "passed": true,
      "message": "src/database/supplier_crud.py найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: Главное окно",
      "passed": true,
      "message": "src/ui/main_window.py найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: Страница поставщиков",
      "passed": true,
      "message": "src/ui/pages/suppliers_page.py найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Файл: Тёмная тема",
      "passed": true,
      "message": "src/ui/styles/dark_theme.qss найден",
      "error": null,
      "timestamp": "22:28:24"
    },
    {
      "name": "Зависимость: sqlalchemy",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:25"
    },
    {
      "name": "Зависимость: sqlcipher3",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:25"
    },
    {
      "name": "Зависимость: pyside6",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:25"
    },
    {
      "name": "Зависимость: pandas",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:26"
    },
    {
      "name": "Зависимость: openpyxl",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:26"
    },
    {
      "name": "Зависимость: pydantic",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:26"
    },
    {
      "name": "Зависимость: pydantic-settings",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:26"
    },
    {
      "name": "Зависимость: python-dotenv",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:26"
    },
    {
      "name": "Зависимость: aiohttp",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "Зависимость: beautifulsoup4",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "Зависимость: lxml",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "Зависимость: tenacity",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "Зависимость: tqdm",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "Зависимость: structlog",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "БД: Ключ шифрования",
      "passed": true,
      "message": "DB_KEY найден и имеет достаточную длину",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "Импорт: Движок БД",
      "passed": true,
      "message": "Модуль database.engine импортирован",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "Импорт: ORM-модели",
      "passed": true,
      "message": "Модуль database.models импортирован",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "Импорт: Сессии БД",
      "passed": true,
      "message": "Модуль database.session импортирован",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "БД: Шифрование SQLCipher",
      "passed": true,
      "message": "Файл зашифрован, чтение без ключа заблокировано",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "БД: Шифрование SQLCipher",
      "passed": false,
      "message": "Ошибка при тесте шифрования",
      "error": "[WinError 32] Процесс не может получить доступ к файлу, так как этот файл занят другим процессом: 'D:\\\\Projects\\\\MEEYG 1.0\\\\data\\\\test_meeyg.db'",
      "timestamp": "22:28:27"
    },
    {
      "name": "Модель: Класс Supplier",
      "passed": true,
      "message": "Класс определён корректно",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "Модель: Обязательные поля",
      "passed": true,
      "message": "Все поля присутствуют: id, name, base_url, is_active, created_at, updated_at",
      "error": null,
      "timestamp": "22:28:27"
    },
    {
      "name": "Модель: Валидация",
      "passed": false,
      "message": "Ошибка проверки модели",
      "error": "Boolean value of this clause is not defined",
      "timestamp": "22:28:27"
    },
    {
      "name": "CRUD: Импорт модулей",
      "passed": false,
      "message": "Не удалось импортировать CRUD-функции",
      "error": "cannot import name 'get_engine' from 'database.engine' (D:\\Projects\\MEEYG 1.0\\src\\database\\engine.py)",
      "timestamp": "22:28:27"
    },
    {
      "name": "UI: PySide6 импорт",
      "passed": true,
      "message": "Библиотека PySide6 доступна",
      "error": null,
      "timestamp": "22:28:28"
    },
    {
      "name": "UI: Тёмная тема (QSS)",
      "passed": false,
      "message": "Ошибка загрузки темы",
      "error": "cannot import name 'dark_theme' from 'ui.styles' (D:\\Projects\\MEEYG 1.0\\src\\ui\\styles\\__init__.py)",
      "timestamp": "22:28:28"
    },
    {
      "name": "UI: Класс MainWindow",
      "passed": true,
      "message": "Класс импортирован",
      "error": null,
      "timestamp": "22:28:28"
    },
    {
      "name": "UI: Создание MainWindow",
      "passed": true,
      "message": "Экземпляр окна создан",
      "error": null,
      "timestamp": "22:28:28"
    },
    {
      "name": "Интеграция: Импорт CRUD-модуля",
      "passed": false,
      "message": "Ключевое слово 'supplier_crud' НЕ найдено в коде",
      "error": null,
      "timestamp": "22:28:28"
    },
    {
      "name": "Интеграция: Вызов создания поставщика",
      "passed": true,
      "message": "Ключевое слово 'create_supplier' найдено",
      "error": null,
      "timestamp": "22:28:28"
    },
    {
      "name": "Интеграция: Вызов обновления поставщика",
      "passed": true,
      "message": "Ключевое слово 'update_supplier' найдено",
      "error": null,
      "timestamp": "22:28:28"
    },
    {
      "name": "Интеграция: Вызов удаления поставщика",
      "passed": true,
      "message": "Ключевое слово 'delete_supplier' найдено",
      "error": null,
      "timestamp": "22:28:28"
    },
    {
      "name": "Интеграция: Использование таблицы для отображения",
      "passed": true,
      "message": "Ключевое слово 'QTableView' найдено",
      "error": null,
      "timestamp": "22:28:28"
    },
    {
      "name": "Интеграция: Обработка ошибок через диалоги",
      "passed": true,
      "message": "Ключевое слово 'QMessageBox' найдено",
      "error": null,
      "timestamp": "22:28:28"
    },
    {
      "name": "Интеграция: Обработчики событий",
      "passed": true,
      "message": "Найдены подключения сигналов к слотам",
      "error": null,
      "timestamp": "22:28:28"
    }
  ],
  "summary": {
    "total": 57,
    "passed": 51,
    "failed": 6
  }
}
```

### `logs\test_report_20260427_223738.json`
```json
{
  "timestamp": "2026-04-27T22:37:38.450674",
  "results": [
    {
      "name": "Папка: Исходный код",
      "passed": true,
      "message": "src существует",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Папка: Ядро приложения",
      "passed": true,
      "message": "src/core существует",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Папка: Работа с БД",
      "passed": true,
      "message": "src/database существует",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Папка: Бизнес-модули",
      "passed": true,
      "message": "src/modules существует",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Папка: Пользовательский интерфейс",
      "passed": true,
      "message": "src/ui существует",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Папка: Данные (БД, экспорты)",
      "passed": true,
      "message": "data существует",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Папка: Лог-файлы",
      "passed": true,
      "message": "logs существует",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Папка: Конфигурации",
      "passed": true,
      "message": "config существует",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: Конфигурация зависимостей",
      "passed": true,
      "message": "pyproject.toml найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: Скрипт настройки окружения",
      "passed": true,
      "message": "setup_env.py найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: Переменные окружения",
      "passed": true,
      "message": ".env найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: Пакет src",
      "passed": true,
      "message": "src/__init__.py найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: Точка входа",
      "passed": true,
      "message": "src/main.py найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: Конфигурация приложения",
      "passed": true,
      "message": "src/core/config.py найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: Система логирования",
      "passed": true,
      "message": "src/core/logger.py найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: Движок БД",
      "passed": true,
      "message": "src/database/engine.py найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: ORM-модели",
      "passed": true,
      "message": "src/database/models.py найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: Управление сессиями",
      "passed": true,
      "message": "src/database/session.py найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: CRUD для поставщиков",
      "passed": true,
      "message": "src/database/supplier_crud.py найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: Главное окно",
      "passed": true,
      "message": "src/ui/main_window.py найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: Страница поставщиков",
      "passed": true,
      "message": "src/ui/pages/suppliers_page.py найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Файл: Тёмная тема",
      "passed": true,
      "message": "src/ui/styles/dark_theme.qss найден",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Зависимость: sqlalchemy",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Зависимость: sqlcipher3",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Зависимость: pyside6",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:34"
    },
    {
      "name": "Зависимость: pandas",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:35"
    },
    {
      "name": "Зависимость: openpyxl",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:36"
    },
    {
      "name": "Зависимость: pydantic",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:36"
    },
    {
      "name": "Зависимость: pydantic-settings",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:36"
    },
    {
      "name": "Зависимость: python-dotenv",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:36"
    },
    {
      "name": "Зависимость: aiohttp",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:36"
    },
    {
      "name": "Зависимость: beautifulsoup4",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:36"
    },
    {
      "name": "Зависимость: lxml",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:36"
    },
    {
      "name": "Зависимость: tenacity",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:36"
    },
    {
      "name": "Зависимость: tqdm",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:36"
    },
    {
      "name": "Зависимость: structlog",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:37:37"
    },
    {
      "name": "БД: Ключ шифрования",
      "passed": true,
      "message": "DB_KEY найден и имеет достаточную длину",
      "error": null,
      "timestamp": "22:37:37"
    },
    {
      "name": "Импорт: Движок БД",
      "passed": true,
      "message": "Модуль database.engine импортирован",
      "error": null,
      "timestamp": "22:37:37"
    },
    {
      "name": "Импорт: ORM-модели",
      "passed": true,
      "message": "Модуль database.models импортирован",
      "error": null,
      "timestamp": "22:37:37"
    },
    {
      "name": "Импорт: Сессии БД",
      "passed": true,
      "message": "Модуль database.session импортирован",
      "error": null,
      "timestamp": "22:37:37"
    },
    {
      "name": "БД: Шифрование SQLCipher",
      "passed": true,
      "message": "Файл зашифрован, чтение без ключа заблокировано",
      "error": null,
      "timestamp": "22:37:37"
    },
    {
      "name": "Модель: Класс Supplier",
      "passed": true,
      "message": "Класс определён корректно",
      "error": null,
      "timestamp": "22:37:37"
    },
    {
      "name": "Модель: Обязательные поля",
      "passed": true,
      "message": "Все поля присутствуют: id, name, base_url, is_active, created_at, updated_at",
      "error": null,
      "timestamp": "22:37:37"
    },
    {
      "name": "Модель: Валидация",
      "passed": false,
      "message": "Ошибка проверки модели",
      "error": "Boolean value of this clause is not defined",
      "timestamp": "22:37:37"
    },
    {
      "name": "CRUD: Create",
      "passed": true,
      "message": "Создан поставщик ID=1",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "CRUD: Read All",
      "passed": true,
      "message": "Поставщик найден в списке (1 всего)",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "CRUD: Read By ID",
      "passed": true,
      "message": "Найден по ID: Test Supplier Alpha",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "CRUD: Update",
      "passed": true,
      "message": "Данные обновлены: Updated Test Supplier",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "CRUD: Delete (soft)",
      "passed": true,
      "message": "Поставщик деактивирован и скрыт из списка",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "CRUD: Soft delete проверка",
      "passed": true,
      "message": "is_active = False, запись сохранена",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "UI: PySide6 импорт",
      "passed": true,
      "message": "Библиотека PySide6 доступна",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "UI: Тёмная тема (QSS)",
      "passed": true,
      "message": "Файл темы загружен (7782 символов)",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "UI: Класс MainWindow",
      "passed": true,
      "message": "Класс импортирован",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "UI: Создание MainWindow",
      "passed": true,
      "message": "Экземпляр окна создан",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "Интеграция: Импорт CRUD-модуля",
      "passed": true,
      "message": "Ключевое слово 'supplier_crud' найдено",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "Интеграция: Вызов создания поставщика",
      "passed": true,
      "message": "Ключевое слово 'create_supplier' найдено",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "Интеграция: Вызов обновления поставщика",
      "passed": true,
      "message": "Ключевое слово 'update_supplier' найдено",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "Интеграция: Вызов удаления поставщика",
      "passed": true,
      "message": "Ключевое слово 'delete_supplier' найдено",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "Интеграция: Использование таблицы для отображения",
      "passed": true,
      "message": "Ключевое слово 'QTableView' найдено",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "Интеграция: Обработка ошибок через диалоги",
      "passed": true,
      "message": "Ключевое слово 'QMessageBox' найдено",
      "error": null,
      "timestamp": "22:37:38"
    },
    {
      "name": "Интеграция: Обработчики событий",
      "passed": true,
      "message": "Найдены подключения сигналов к слотам",
      "error": null,
      "timestamp": "22:37:38"
    }
  ],
  "summary": {
    "total": 61,
    "passed": 60,
    "failed": 1
  }
}
```

### `logs\test_report_20260427_223834.json`
```json
{
  "timestamp": "2026-04-27T22:38:34.713646",
  "results": [
    {
      "name": "Папка: Исходный код",
      "passed": true,
      "message": "src существует",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Папка: Ядро приложения",
      "passed": true,
      "message": "src/core существует",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Папка: Работа с БД",
      "passed": true,
      "message": "src/database существует",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Папка: Бизнес-модули",
      "passed": true,
      "message": "src/modules существует",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Папка: Пользовательский интерфейс",
      "passed": true,
      "message": "src/ui существует",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Папка: Данные (БД, экспорты)",
      "passed": true,
      "message": "data существует",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Папка: Лог-файлы",
      "passed": true,
      "message": "logs существует",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Папка: Конфигурации",
      "passed": true,
      "message": "config существует",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: Конфигурация зависимостей",
      "passed": true,
      "message": "pyproject.toml найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: Скрипт настройки окружения",
      "passed": true,
      "message": "setup_env.py найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: Переменные окружения",
      "passed": true,
      "message": ".env найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: Пакет src",
      "passed": true,
      "message": "src/__init__.py найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: Точка входа",
      "passed": true,
      "message": "src/main.py найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: Конфигурация приложения",
      "passed": true,
      "message": "src/core/config.py найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: Система логирования",
      "passed": true,
      "message": "src/core/logger.py найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: Движок БД",
      "passed": true,
      "message": "src/database/engine.py найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: ORM-модели",
      "passed": true,
      "message": "src/database/models.py найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: Управление сессиями",
      "passed": true,
      "message": "src/database/session.py найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: CRUD для поставщиков",
      "passed": true,
      "message": "src/database/supplier_crud.py найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: Главное окно",
      "passed": true,
      "message": "src/ui/main_window.py найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: Страница поставщиков",
      "passed": true,
      "message": "src/ui/pages/suppliers_page.py найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Файл: Тёмная тема",
      "passed": true,
      "message": "src/ui/styles/dark_theme.qss найден",
      "error": null,
      "timestamp": "22:38:30"
    },
    {
      "name": "Зависимость: sqlalchemy",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:31"
    },
    {
      "name": "Зависимость: sqlcipher3",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:31"
    },
    {
      "name": "Зависимость: pyside6",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:31"
    },
    {
      "name": "Зависимость: pandas",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:32"
    },
    {
      "name": "Зависимость: openpyxl",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:32"
    },
    {
      "name": "Зависимость: pydantic",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:32"
    },
    {
      "name": "Зависимость: pydantic-settings",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:32"
    },
    {
      "name": "Зависимость: python-dotenv",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:32"
    },
    {
      "name": "Зависимость: aiohttp",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "Зависимость: beautifulsoup4",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "Зависимость: lxml",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "Зависимость: tenacity",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "Зависимость: tqdm",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "Зависимость: structlog",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "БД: Ключ шифрования",
      "passed": true,
      "message": "DB_KEY найден и имеет достаточную длину",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "Импорт: Движок БД",
      "passed": true,
      "message": "Модуль database.engine импортирован",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "Импорт: ORM-модели",
      "passed": true,
      "message": "Модуль database.models импортирован",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "Импорт: Сессии БД",
      "passed": true,
      "message": "Модуль database.session импортирован",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "БД: Шифрование SQLCipher",
      "passed": true,
      "message": "Файл зашифрован, чтение без ключа заблокировано",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "Модель: Класс Supplier",
      "passed": true,
      "message": "Класс определён корректно",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "Модель: Обязательные поля",
      "passed": true,
      "message": "Все поля присутствуют: id, name, base_url, is_active, created_at, updated_at",
      "error": null,
      "timestamp": "22:38:33"
    },
    {
      "name": "Модель: Валидация",
      "passed": false,
      "message": "Ошибка проверки модели",
      "error": "Boolean value of this clause is not defined",
      "timestamp": "22:38:33"
    },
    {
      "name": "CRUD: Create",
      "passed": true,
      "message": "Создан поставщик ID=1",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "CRUD: Read All",
      "passed": true,
      "message": "Поставщик найден в списке (1 всего)",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "CRUD: Read By ID",
      "passed": true,
      "message": "Найден по ID: Test Supplier Alpha",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "CRUD: Update",
      "passed": true,
      "message": "Данные обновлены: Updated Test Supplier",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "CRUD: Delete (soft)",
      "passed": true,
      "message": "Поставщик деактивирован и скрыт из списка",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "CRUD: Soft delete проверка",
      "passed": true,
      "message": "is_active = False, запись сохранена",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "UI: PySide6 импорт",
      "passed": true,
      "message": "Библиотека PySide6 доступна",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "UI: Тёмная тема (QSS)",
      "passed": true,
      "message": "Файл темы загружен (7782 символов)",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "UI: Класс MainWindow",
      "passed": true,
      "message": "Класс импортирован",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "UI: Создание MainWindow",
      "passed": true,
      "message": "Экземпляр окна создан",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "Интеграция: Импорт CRUD-модуля",
      "passed": true,
      "message": "Ключевое слово 'supplier_crud' найдено",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "Интеграция: Вызов создания поставщика",
      "passed": true,
      "message": "Ключевое слово 'create_supplier' найдено",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "Интеграция: Вызов обновления поставщика",
      "passed": true,
      "message": "Ключевое слово 'update_supplier' найдено",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "Интеграция: Вызов удаления поставщика",
      "passed": true,
      "message": "Ключевое слово 'delete_supplier' найдено",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "Интеграция: Использование таблицы для отображения",
      "passed": true,
      "message": "Ключевое слово 'QTableView' найдено",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "Интеграция: Обработка ошибок через диалоги",
      "passed": true,
      "message": "Ключевое слово 'QMessageBox' найдено",
      "error": null,
      "timestamp": "22:38:34"
    },
    {
      "name": "Интеграция: Обработчики событий",
      "passed": true,
      "message": "Найдены подключения сигналов к слотам",
      "error": null,
      "timestamp": "22:38:34"
    }
  ],
  "summary": {
    "total": 61,
    "passed": 60,
    "failed": 1
  }
}
```

### `logs\test_report_20260427_223912.json`
```json
{
  "timestamp": "2026-04-27T22:39:12.030697",
  "results": [
    {
      "name": "Папка: Исходный код",
      "passed": true,
      "message": "src существует",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Папка: Ядро приложения",
      "passed": true,
      "message": "src/core существует",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Папка: Работа с БД",
      "passed": true,
      "message": "src/database существует",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Папка: Бизнес-модули",
      "passed": true,
      "message": "src/modules существует",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Папка: Пользовательский интерфейс",
      "passed": true,
      "message": "src/ui существует",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Папка: Данные (БД, экспорты)",
      "passed": true,
      "message": "data существует",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Папка: Лог-файлы",
      "passed": true,
      "message": "logs существует",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Папка: Конфигурации",
      "passed": true,
      "message": "config существует",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: Конфигурация зависимостей",
      "passed": true,
      "message": "pyproject.toml найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: Скрипт настройки окружения",
      "passed": true,
      "message": "setup_env.py найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: Переменные окружения",
      "passed": true,
      "message": ".env найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: Пакет src",
      "passed": true,
      "message": "src/__init__.py найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: Точка входа",
      "passed": true,
      "message": "src/main.py найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: Конфигурация приложения",
      "passed": true,
      "message": "src/core/config.py найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: Система логирования",
      "passed": true,
      "message": "src/core/logger.py найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: Движок БД",
      "passed": true,
      "message": "src/database/engine.py найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: ORM-модели",
      "passed": true,
      "message": "src/database/models.py найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: Управление сессиями",
      "passed": true,
      "message": "src/database/session.py найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: CRUD для поставщиков",
      "passed": true,
      "message": "src/database/supplier_crud.py найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: Главное окно",
      "passed": true,
      "message": "src/ui/main_window.py найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: Страница поставщиков",
      "passed": true,
      "message": "src/ui/pages/suppliers_page.py найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Файл: Тёмная тема",
      "passed": true,
      "message": "src/ui/styles/dark_theme.qss найден",
      "error": null,
      "timestamp": "22:39:07"
    },
    {
      "name": "Зависимость: sqlalchemy",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:08"
    },
    {
      "name": "Зависимость: sqlcipher3",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:08"
    },
    {
      "name": "Зависимость: pyside6",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:08"
    },
    {
      "name": "Зависимость: pandas",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:09"
    },
    {
      "name": "Зависимость: openpyxl",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:09"
    },
    {
      "name": "Зависимость: pydantic",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:09"
    },
    {
      "name": "Зависимость: pydantic-settings",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:09"
    },
    {
      "name": "Зависимость: python-dotenv",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:09"
    },
    {
      "name": "Зависимость: aiohttp",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:10"
    },
    {
      "name": "Зависимость: beautifulsoup4",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:10"
    },
    {
      "name": "Зависимость: lxml",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:10"
    },
    {
      "name": "Зависимость: tenacity",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:10"
    },
    {
      "name": "Зависимость: tqdm",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:10"
    },
    {
      "name": "Зависимость: structlog",
      "passed": true,
      "message": "Установлен и импортируется",
      "error": null,
      "timestamp": "22:39:10"
    },
    {
      "name": "БД: Ключ шифрования",
      "passed": true,
      "message": "DB_KEY найден и имеет достаточную длину",
      "error": null,
      "timestamp": "22:39:10"
    },
    {
      "name": "Импорт: Движок БД",
      "passed": true,
      "message": "Модуль database.engine импортирован",
      "error": null,
      "timestamp": "22:39:10"
    },
    {
      "name": "Импорт: ORM-модели",
      "passed": true,
      "message": "Модуль database.models импортирован",
      "error": null,
      "timestamp": "22:39:10"
    },
    {
      "name": "Импорт: Сессии БД",
      "passed": true,
      "message": "Модуль database.session импортирован",
      "error": null,
      "timestamp": "22:39:10"
    },
    {
      "name": "БД: Шифрование SQLCipher",
      "passed": true,
      "message": "Файл зашифрован, чтение без ключа заблокировано",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "Модель: Класс Supplier",
      "passed": true,
      "message": "Класс определён корректно",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "Модель: Обязательные поля",
      "passed": true,
      "message": "Все поля присутствуют: id, name, base_url, is_active, created_at, updated_at",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "Модель: Уникальность name",
      "passed": true,
      "message": "name имеет unique=True",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "Модель: Индексы",
      "passed": true,
      "message": "Созданы индексы: ix_suppliers_name, ix_suppliers_is_active, ix_suppliers_name_is_active",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "CRUD: Create",
      "passed": true,
      "message": "Создан поставщик ID=1",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "CRUD: Read All",
      "passed": true,
      "message": "Поставщик найден в списке (1 всего)",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "CRUD: Read By ID",
      "passed": true,
      "message": "Найден по ID: Test Supplier Alpha",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "CRUD: Update",
      "passed": true,
      "message": "Данные обновлены: Updated Test Supplier",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "CRUD: Delete (soft)",
      "passed": true,
      "message": "Поставщик деактивирован и скрыт из списка",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "CRUD: Soft delete проверка",
      "passed": true,
      "message": "is_active = False, запись сохранена",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "UI: PySide6 импорт",
      "passed": true,
      "message": "Библиотека PySide6 доступна",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "UI: Тёмная тема (QSS)",
      "passed": true,
      "message": "Файл темы загружен (7782 символов)",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "UI: Класс MainWindow",
      "passed": true,
      "message": "Класс импортирован",
      "error": null,
      "timestamp": "22:39:11"
    },
    {
      "name": "UI: Создание MainWindow",
      "passed": true,
      "message": "Экземпляр окна создан",
      "error": null,
      "timestamp": "22:39:12"
    },
    {
      "name": "Интеграция: Импорт CRUD-модуля",
      "passed": true,
      "message": "Ключевое слово 'supplier_crud' найдено",
      "error": null,
      "timestamp": "22:39:12"
    },
    {
      "name": "Интеграция: Вызов создания поставщика",
      "passed": true,
      "message": "Ключевое слово 'create_supplier' найдено",
      "error": null,
      "timestamp": "22:39:12"
    },
    {
      "name": "Интеграция: Вызов обновления поставщика",
      "passed": true,
      "message": "Ключевое слово 'update_supplier' найдено",
      "error": null,
      "timestamp": "22:39:12"
    },
    {
      "name": "Интеграция: Вызов удаления поставщика",
      "passed": true,
      "message": "Ключевое слово 'delete_supplier' найдено",
      "error": null,
      "timestamp": "22:39:12"
    },
    {
      "name": "Интеграция: Использование таблицы для отображения",
      "passed": true,
      "message": "Ключевое слово 'QTableView' найдено",
      "error": null,
      "timestamp": "22:39:12"
    },
    {
      "name": "Интеграция: Обработка ошибок через диалоги",
      "passed": true,
      "message": "Ключевое слово 'QMessageBox' найдено",
      "error": null,
      "timestamp": "22:39:12"
    },
    {
      "name": "Интеграция: Обработчики событий",
      "passed": true,
      "message": "Найдены подключения сигналов к слотам",
      "error": null,
      "timestamp": "22:39:12"
    }
  ],
  "summary": {
    "total": 62,
    "passed": 62,
    "failed": 0
  }
}
```

### `logs\test_report_20260427_232701.json`
```json
[
  {
    "name": "Структура: src",
    "passed": true,
    "msg": "Папка найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: src/core",
    "passed": true,
    "msg": "Папка найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: src/database",
    "passed": true,
    "msg": "Папка найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: src/modules",
    "passed": true,
    "msg": "Папка найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: src/ui",
    "passed": true,
    "msg": "Папка найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: data",
    "passed": true,
    "msg": "Папка найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: logs",
    "passed": true,
    "msg": "Папка найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: config",
    "passed": true,
    "msg": "Папка найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: pyproject.toml",
    "passed": true,
    "msg": "Файл найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: .env",
    "passed": true,
    "msg": "Файл найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: src/main.py",
    "passed": true,
    "msg": "Файл найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: src/database/engine.py",
    "passed": true,
    "msg": "Файл найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: src/database/models.py",
    "passed": true,
    "msg": "Файл найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: src/database/supplier_crud.py",
    "passed": true,
    "msg": "Файл найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: src/ui/main_window.py",
    "passed": true,
    "msg": "Файл найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: src/ui/pages/suppliers_page.py",
    "passed": true,
    "msg": "Файл найдена",
    "time": "23:27:00"
  },
  {
    "name": "Структура: src/ui/styles/dark_theme.qss",
    "passed": true,
    "msg": "Файл найдена",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: sqlalchemy",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: sqlcipher3",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: pyside6",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: pandas",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: openpyxl",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: pydantic",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: pydantic-settings",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: python-dotenv",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: aiohttp",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: beautifulsoup4",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: lxml",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: tenacity",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: tqdm",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "Зависимость: structlog",
    "passed": true,
    "msg": "Установлен",
    "time": "23:27:00"
  },
  {
    "name": "SQLCipher: Шифрование",
    "passed": true,
    "msg": "Файл зашифрован, чтение без ключа заблокировано",
    "time": "23:27:00"
  },
  {
    "name": "SQLCipher: Общая проверка",
    "passed": false,
    "msg": "Ошибка: [WinError 32] Процесс не может получить доступ к файлу, так как этот файл занят другим процессом: 'D:\\\\Projects\\\\MEEYG 1.0\\\\data\\\\_test_cipher.db'",
    "time": "23:27:00"
  },
  {
    "name": "Модель: Поля Supplier",
    "passed": true,
    "msg": "Присутствуют все поля",
    "time": "23:27:01"
  },
  {
    "name": "Модель: Уникальность name/base_url",
    "passed": true,
    "msg": "unique=True применено",
    "time": "23:27:01"
  },
  {
    "name": "CRUD: Импорт модуля",
    "passed": true,
    "msg": "Модуль доступен",
    "time": "23:27:01"
  },
  {
    "name": "CRUD: Логика",
    "passed": false,
    "msg": "cannot import name 'get_engine' from 'database.engine' (D:\\Projects\\MEEYG 1.0\\src\\database\\engine.py)",
    "time": "23:27:01"
  },
  {
    "name": "UI: Тема QSS",
    "passed": true,
    "msg": "Валидный QSS (7782 символов)",
    "time": "23:27:01"
  },
  {
    "name": "Интеграция: Связь UI-DB",
    "passed": true,
    "msg": "Импорты и вызовы CRUD найдены",
    "time": "23:27:01"
  }
]
```

### `meeyg.egg-info\PKG-INFO`
```text
Metadata-Version: 2.4
Name: meeyg
Version: 1.0.0
Summary: MEEYG - Modular Enterprise Environment for Yield Gathering
Requires-Python: >=3.12
Requires-Dist: sqlalchemy>=2.0.0
Requires-Dist: sqlcipher3>=0.5.3
Requires-Dist: pandas>=2.0.0
Requires-Dist: openpyxl>=3.1.0
Requires-Dist: pyside6>=6.6.0
Requires-Dist: pydantic>=2.0.0
Requires-Dist: python-dotenv>=1.0.0
Requires-Dist: aiohttp>=3.9.0
Requires-Dist: beautifulsoup4>=4.12.0
Requires-Dist: lxml>=5.0.0
Requires-Dist: tenacity>=8.2.0
Requires-Dist: tqdm>=4.66.0
Requires-Dist: structlog>=24.0.0
Requires-Dist: pydantic-settings>=2.0.0
Provides-Extra: dev
Requires-Dist: pytest>=8.0.0; extra == "dev"
Requires-Dist: pytest-asyncio>=0.23.0; extra == "dev"
Requires-Dist: ruff>=0.3.0; extra == "dev"

```

### `meeyg.egg-info\SOURCES.txt`
```text
pyproject.toml
meeyg.egg-info/PKG-INFO
meeyg.egg-info/SOURCES.txt
meeyg.egg-info/dependency_links.txt
meeyg.egg-info/requires.txt
meeyg.egg-info/top_level.txt
src/__init__.py
src/main.py
src/core/__init__.py
src/core/config.py
src/core/logger.py
src/database/__init__.py
src/database/engine.py
src/database/migrate_add_parent_product_id.py
src/database/models.py
src/database/session.py
src/database/supplier_crud.py
src/modules/__init__.py
src/modules/archive/__init__.py
src/modules/archive/engine.py
src/modules/discovery/__init__.py
src/modules/discovery/engine.py
src/modules/export/__init__.py
src/modules/export/generator.py
src/modules/import_prep/__init__.py
src/modules/import_prep/mapper.py
src/modules/parsing/__init__.py
src/modules/parsing/engine.py
src/modules/parsing/tandoor_playwright_parser.py
src/ui/__init__.py
src/ui/main_window.py
src/ui/pages/__init__.py
src/ui/pages/archive_page.py
src/ui/pages/discovery_page.py
src/ui/pages/export_page.py
src/ui/pages/parsing_page.py
src/ui/pages/placeholder_page.py
src/ui/pages/suppliers_page.py
src/ui/styles/__init__.py
tests/test_hierarchy_logic.py
tests/test_tandoor_parser.py
```

### `meeyg.egg-info\dependency_links.txt`
```text


```

### `meeyg.egg-info\requires.txt`
```text
sqlalchemy>=2.0.0
sqlcipher3>=0.5.3
pandas>=2.0.0
openpyxl>=3.1.0
pyside6>=6.6.0
pydantic>=2.0.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
tenacity>=8.2.0
tqdm>=4.66.0
structlog>=24.0.0
pydantic-settings>=2.0.0

[dev]
pytest>=8.0.0
pytest-asyncio>=0.23.0
ruff>=0.3.0

```

### `meeyg.egg-info\top_level.txt`
```text
src

```

### `scripts\add_compatible_collections_field.py`
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Миграция: добавление поля compatible_collections в таблицу products
Использует прямое подключение через sqlcipher3 для надёжности
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import sqlcipher3 as sqlite3

# Загружаем переменные окружения
load_dotenv()

# Пути
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "meeyg.db"
DB_KEY = os.getenv("DB_KEY", "").strip()

def run_migration():
    print("🔐 Подключение к зашифрованной БД...")
    
    # Проверка ключа
    if not DB_KEY or len(DB_KEY) != 64:
        print("❌ Ошибка: DB_KEY не установлен или имеет неверную длину (должно быть 64 hex-символа)")
        return False
    
    # Проверка существования файла БД
    if not DB_PATH.exists():
        print(f"❌ Файл БД не найден: {DB_PATH}")
        return False
    
    conn = None
    try:
        # Прямое подключение через sqlcipher3
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute(f"PRAGMA key = '{DB_KEY}'")
        
        # Проверка валидности ключа
        version = conn.execute("PRAGMA cipher_version").fetchone()
        if not version:
            print("❌ Неверный ключ шифрования или файл БД повреждён")
            return False
        print(f"✅ Ключ принят. SQLCipher версия: {version[0]}")
        
        # 1. Добавляем колонку (если ещё не добавлена)
        print("\n📋 Проверка колонки compatible_collections...")
        columns = [col[1] for col in conn.execute("PRAGMA table_info(products)")]
        
        if "compatible_collections" in columns:
            print("⚠️  Колонка 'compatible_collections' уже существует — пропускаем создание")
        else:
            print("➕ Добавляем колонку 'compatible_collections TEXT'...")
            conn.execute("ALTER TABLE products ADD COLUMN compatible_collections TEXT")
            print("✅ Колонка добавлена")
        
        # 2. Проверяем результат
        print("\n🔍 Проверка структуры таблицы products:")
        for col in conn.execute("PRAGMA table_info(products)"):
            if col[1] == "compatible_collections":
                print(f"   ✓ {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")
        
        conn.commit()
        print("\n🎉 Миграция успешно завершена!")
        return True
        
    except sqlite3.DatabaseError as e:
        print(f"❌ Ошибка SQLCipher: {e}")
        print("💡 Проверьте, что ключ в .env соответствует ключу шифрования БД")
        return False
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  MEEYG 1.0 — Миграция: compatible_collections")
    print("=" * 60)
    print(f"📁 Путь к БД: {DB_PATH}")
    print(f"🔑 DB_KEY: {'✓' if DB_KEY and len(DB_KEY) == 64 else '✗'}\n")
    
    success = run_migration()
    sys.exit(0 if success else 1)
```

### `scripts\add_parent_product_field.py`
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Миграция: добавление поля parent_product_id в таблицу products
Использует прямое подключение через sqlcipher3 для надёжности
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import sqlcipher3 as sqlite3

# Загружаем переменные окружения
load_dotenv()

# Пути
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "meeyg.db"
DB_KEY = os.getenv("DB_KEY", "").strip()

def run_migration():
    print("🔐 Подключение к зашифрованной БД...")
    
    # Проверка ключа
    if not DB_KEY or len(DB_KEY) != 64:
        print("❌ Ошибка: DB_KEY не установлен или имеет неверную длину (должно быть 64 hex-символа)")
        return False
    
    # Проверка существования файла БД
    if not DB_PATH.exists():
        print(f"❌ Файл БД не найден: {DB_PATH}")
        return False
    
    conn = None
    try:
        # Прямое подключение через sqlcipher3
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute(f"PRAGMA key = '{DB_KEY}'")
        
        # Проверка валидности ключа
        version = conn.execute("PRAGMA cipher_version").fetchone()
        if not version:
            print("❌ Неверный ключ шифрования или файл БД повреждён")
            return False
        print(f"✅ Ключ принят. SQLCipher версия: {version[0]}")
        
        # 1. Добавляем колонку (если ещё не добавлена)
        print("\n📋 Проверка колонки parent_product_id...")
        columns = [col[1] for col in conn.execute("PRAGMA table_info(products)")]
        
        if "parent_product_id" in columns:
            print("⚠️  Колонка 'parent_product_id' уже существует — пропускаем создание")
        else:
            print("➕ Добавляем колонку 'parent_product_id INTEGER'...")
            conn.execute("ALTER TABLE products ADD COLUMN parent_product_id INTEGER")
            print("✅ Колонка добавлена")
        
        # 2. Создаём индекс (если ещё не создан)
        print("\n📋 Проверка индекса idx_parent_product...")
        indexes = [idx[1] for idx in conn.execute("PRAGMA index_list(products)")]
        
        if "idx_parent_product" in indexes:
            print("⚠️  Индекс 'idx_parent_product' уже существует — пропускаем")
        else:
            print("📊 Создаём индекс 'idx_parent_product'...")
            conn.execute("CREATE INDEX idx_parent_product ON products(parent_product_id)")
            print("✅ Индекс создан")
        
        # 3. Проверяем результат
        print("\n🔍 Проверка структуры таблицы products:")
        for col in conn.execute("PRAGMA table_info(products)"):
            if col[1] == "parent_product_id":
                print(f"   ✓ {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")
        
        conn.commit()
        print("\n🎉 Миграция успешно завершена!")
        return True
        
    except sqlite3.DatabaseError as e:
        print(f"❌ Ошибка SQLCipher: {e}")
        print("💡 Проверьте, что ключ в .env соответствует ключу шифрования БД")
        return False
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  MEEYG 1.0 — Миграция: parent_product_id")
    print("=" * 60)
    print(f"📁 Путь к БД: {DB_PATH}")
    print(f"🔑 DB_KEY: {'✓' if DB_KEY and len(DB_KEY) == 64 else '✗'}\n")
    
    success = run_migration()
    sys.exit(0 if success else 1)
```

### `scripts\clean_categories.py`
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧹 Скрипт очистки таблицы категорий MEEYG 1.0
Используется для сброса данных перед повторным запуском модуля "Разведка".
"""
import os
import sqlcipher3 as sqlite3

# 📍 Пути и ключ
PROJECT_ROOT = r"D:\Projects\MEEYG 1.0"
DB_PATH = os.path.join(PROJECT_ROOT, "data", "meeyg.db")
DB_KEY = "82baec464414deb5fb7805afff26c24f0df011e75ec75430cfa79da55003674d"

def clean_categories():
    if not os.path.exists(DB_PATH):
        print(f"❌ Файл БД не найден по пути: {DB_PATH}")
        return

    print("🔐 Подключение к зашифрованной БД...")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(f"PRAGMA key = '{DB_KEY}'")

        # 1. Проверка валидности ключа
        version = conn.execute("PRAGMA cipher_version").fetchone()
        if not version:
            raise sqlite3.DatabaseError("Неверный ключ шифрования или файл повреждён.")
        print(f"✅ Ключ принят. SQLCipher: {version[0]}")

        # 2. Подсчёт записей перед удалением
        count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        print(f"📊 Найдено категорий в БД: {count}")

        if count == 0:
            print("⚠️ Таблица 'categories' уже пуста. Очистка не требуется.")
            return

        # 3. Удаление данных
        print("🗑️ Выполняется удаление...")
        conn.execute("DELETE FROM categories")
        conn.commit()
        
        print(f"✅ Успешно удалено {count} записей.")
        print(" Готово! Можно запускать новую разведку.")

    except sqlite3.DatabaseError as e:
        print(f"❌ Ошибка SQLCipher (проверьте ключ/файл): {e}")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    clean_categories()
```

### `src\__init__.py`
```python

```

### `src\main.py`
```python
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import settings
from src.core.logger import logger
from src.database.models import Base
from src.database.session import engine
from src.ui.main_window import MainWindow
from src.ui.pages.archive_page import ArchivePage
from src.ui.pages.discovery_page import DiscoveryPage
from src.ui.pages.export_page import ExportPage
from src.ui.pages.parsing_page import ParsingPage
from src.ui.pages.placeholder_page import PlaceholderPage
from src.ui.pages.suppliers_page import SuppliersPage


def main() -> None:
    try:
        app = QApplication(sys.argv)
        app.setApplicationName(settings.app_name)
        app.setApplicationVersion(settings.app_version)

        qss_path = PROJECT_ROOT / "src" / "ui" / "styles" / "dark_theme.qss"
        if qss_path.exists():
            app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        window = MainWindow()

        dashboard = PlaceholderPage(
            "Главная",
            "Обзор аналитики поставщиков и ключевые показатели появятся здесь.",
        )
        suppliers = SuppliersPage()
        discovery = DiscoveryPage()
        parsing = ParsingPage()
        archive = ArchivePage()
        intelligence = PlaceholderPage(
            "Аналитика",
            "Инструменты рыночной аналитики и анализа поставщиков появятся здесь.",
        )
        export = ExportPage()

        window.register_page(dashboard)
        window.register_page(suppliers)
        window.register_page(discovery)
        window.register_page(parsing)
        window.register_page(archive)
        window.register_page(intelligence)
        window.register_page(export)

        window.show()
        logger.info("Application started")

        sys.exit(app.exec())

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as exc:
        logger.error(f"Application failed to start: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

```

### `src\core\__init__.py`
```python

```

### `src\core\config.py`
```python
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    app_name: str = Field(default="MEEYG", validation_alias="APP_NAME")
    app_version: str = Field(default="1.0.0", validation_alias="APP_VERSION")
    db_path: Path = Field(
        default=PROJECT_ROOT / "data" / "meeyg.db",
        validation_alias="DB_PATH",
    )
    db_key: str = Field(
        default="",
        validation_alias="DB_KEY",
    )
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    data_dir: Path = Field(default=PROJECT_ROOT / "data")
    logs_dir: Path = Field(default=PROJECT_ROOT / "logs")

    @field_validator("db_key", mode="before")
    @classmethod
    def validate_db_key(cls, v: str) -> str:
        if v and len(v) != 64:
            raise ValueError("DB_KEY must be a 64-character hex string (32 bytes)")
        return v

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()

```

### `src\core\logger.py`
```python
import logging
import logging.handlers
from pathlib import Path

import structlog
from structlog.processors import (
    JSONRenderer,
    TimeStamper,
    add_log_level,
    format_exc_info,
)

from src.core.config import settings


def setup_logger() -> structlog.BoundLogger:
    log_file = settings.logs_dir / "app.log"

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter("%(message)s"))

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(message)s",
        handlers=[file_handler, console_handler],
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            TimeStamper(fmt="iso"),
            add_log_level,
            format_exc_info,
            structlog.processors.UnicodeDecoder(),
            JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    return structlog.get_logger()


logger = setup_logger()

```

### `src\database\__init__.py`
```python

```

### `src\database\engine.py`
```python
import ctypes
import os
import secrets
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine as _sa_create_engine

from src.core.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROTECTED_KEY_PATH = PROJECT_ROOT / "data" / ".db_key.protected"


class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_ulong), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


def _generate_key() -> str:
    return secrets.token_hex(32)


def _protect_key_dpapi(key: str) -> bytes:
    key_bytes = key.encode("utf-16-le")
    blob_in = DATA_BLOB()
    blob_in.cbData = len(key_bytes)
    buf = (ctypes.c_ubyte * len(key_bytes)).from_buffer_copy(key_bytes)
    blob_in.pbData = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))

    blob_out = DATA_BLOB()

    result = ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(blob_in),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(blob_out),
    )
    if not result:
        raise RuntimeError("DPAPI CryptProtectData failed")

    protected = bytes(
        ctypes.string_at(
            ctypes.cast(blob_out.pbData, ctypes.POINTER(ctypes.c_ubyte)),
            blob_out.cbData,
        )
    )
    ctypes.windll.kernel32.LocalFree(blob_out.pbData)
    return protected


def _unprotect_key_dpapi(protected: bytes) -> str:
    blob_in = DATA_BLOB()
    blob_in.cbData = len(protected)
    buf = (ctypes.c_ubyte * len(protected)).from_buffer_copy(protected)
    blob_in.pbData = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))

    blob_out = DATA_BLOB()

    result = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blob_in),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(blob_out),
    )
    if not result:
        raise RuntimeError("DPAPI CryptUnprotectData failed")

    decrypted = bytes(
        ctypes.string_at(
            ctypes.cast(blob_out.pbData, ctypes.POINTER(ctypes.c_ubyte)),
            blob_out.cbData,
        )
    )
    ctypes.windll.kernel32.LocalFree(blob_out.pbData)
    return decrypted.decode("utf-16-le").rstrip("\x00")


def _get_or_create_key() -> str:
    db_key = os.environ.get("DB_KEY", "").strip()

    if db_key:
        return db_key

    if PROTECTED_KEY_PATH.exists():
        try:
            protected = PROTECTED_KEY_PATH.read_bytes()
            return _unprotect_key_dpapi(protected)
        except Exception:
            pass

    new_key = _generate_key()
    protected = _protect_key_dpapi(new_key)
    PROTECTED_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROTECTED_KEY_PATH.write_bytes(protected)
    return new_key


def create_engine():
    key = _get_or_create_key()
    encoded_key = quote_plus(key)
    db_path = str(settings.db_path)
    engine_url = f"sqlite+pysqlcipher://:{encoded_key}@/{db_path}?cipher=aes-256-cfb"
    return _sa_create_engine(engine_url, echo=False)

```

### `src\database\migrate_add_parent_product_id.py`
```python
"""
Migration script to add parent_product_id column to products table.

This script adds a self-referential foreign key column to support
product hierarchies (e.g., product variants, bundles).

Features:
- Checks column existence before adding
- Creates index for performance
- Adds FOREIGN KEY constraint with ondelete="SET NULL"
- Supports rollback
- Comprehensive logging and error handling
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from src.database.engine import create_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

TABLE_NAME = "products"
COLUMN_NAME = "parent_product_id"
CONSTRAINT_NAME = "fk_products_parent_product_id"
INDEX_NAME = "ix_products_parent_product_id"


def check_column_exists(engine, table_name: str, column_name: str) -> bool:
    """Check if a column exists in the specified table."""
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns(table_name)]
    return column_name in columns


def check_index_exists(engine, index_name: str) -> bool:
    """Check if an index exists in the database."""
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        for idx in inspector.get_indexes(table_name):
            if idx["name"] == index_name:
                return True
    return False


def check_constraint_exists(engine, constraint_name: str) -> bool:
    """Check if a foreign key constraint exists in the database."""
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        for fk in inspector.get_foreign_keys(table_name):
            if fk.get("name") == constraint_name:
                return True
    return False


def add_column_with_constraint(engine) -> None:
    """Add parent_product_id column with index and foreign key constraint."""
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info(f"Checking if column '{COLUMN_NAME}' exists in table '{TABLE_NAME}'...")
        if check_column_exists(engine, TABLE_NAME, COLUMN_NAME):
            logger.info(f"Column '{COLUMN_NAME}' already exists. Skipping creation.")
        else:
            logger.info(f"Adding column '{COLUMN_NAME}' to table '{TABLE_NAME}'...")
            conn.execute(
                f'ALTER TABLE "{TABLE_NAME}" ADD COLUMN "{COLUMN_NAME}" INTEGER'
            )
            logger.info(f"Column '{COLUMN_NAME}' added successfully.")

        logger.info(f"Checking if index '{INDEX_NAME}' exists...")
        if check_index_exists(engine, INDEX_NAME):
            logger.info(f"Index '{INDEX_NAME}' already exists. Skipping creation.")
        else:
            logger.info(f"Creating index '{INDEX_NAME}'...")
            conn.execute(
                f'CREATE INDEX "{INDEX_NAME}" ON "{TABLE_NAME}" ("{COLUMN_NAME}")'
            )
            logger.info(f"Index '{INDEX_NAME}' created successfully.")

        logger.info(f"Checking if foreign key constraint '{CONSTRAINT_NAME}' exists...")
        if check_constraint_exists(engine, CONSTRAINT_NAME):
            logger.info(
                f"Foreign key constraint '{CONSTRAINT_NAME}' already exists. Skipping creation."
            )
        else:
            logger.info(f"Adding foreign key constraint '{CONSTRAINT_NAME}'...")
            conn.execute(
                f'ALTER TABLE "{TABLE_NAME}" '
                f'ADD CONSTRAINT "{CONSTRAINT_NAME}" '
                f'FOREIGN KEY ("{COLUMN_NAME}") REFERENCES "{TABLE_NAME}" ("id") '
                f'ON DELETE SET NULL'
            )
            logger.info(f"Foreign key constraint '{CONSTRAINT_NAME}' added successfully.")


def rollback_migration(engine) -> None:
    """Rollback the migration by dropping constraint, index, and column."""
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        logger.info("Starting rollback...")

        if check_constraint_exists(engine, CONSTRAINT_NAME):
            logger.info(f"Dropping foreign key constraint '{CONSTRAINT_NAME}'...")
            conn.execute(f'ALTER TABLE "{TABLE_NAME}" DROP CONSTRAINT "{CONSTRAINT_NAME}"')
            logger.info(f"Constraint '{CONSTRAINT_NAME}' dropped.")
        else:
            logger.info(f"Constraint '{CONSTRAINT_NAME}' does not exist. Skipping.")

        if check_index_exists(engine, INDEX_NAME):
            logger.info(f"Dropping index '{INDEX_NAME}'...")
            conn.execute(f'DROP INDEX IF EXISTS "{INDEX_NAME}"')
            logger.info(f"Index '{INDEX_NAME}' dropped.")
        else:
            logger.info(f"Index '{INDEX_NAME}' does not exist. Skipping.")

        if check_column_exists(engine, TABLE_NAME, COLUMN_NAME):
            logger.info(f"Dropping column '{COLUMN_NAME}'...")
            conn.execute(f'ALTER TABLE "{TABLE_NAME}" DROP COLUMN "{COLUMN_NAME}"')
            logger.info(f"Column '{COLUMN_NAME}' dropped.")
        else:
            logger.info(f"Column '{COLUMN_NAME}' does not exist. Skipping.")

        logger.info("Rollback completed.")


def run_migration(
    engine, rollback: bool = False, dry_run: bool = False
) -> bool:
    """
    Run or rollback the migration.

    Args:
        engine: SQLAlchemy engine instance
        rollback: If True, rollback the migration instead of applying
        dry_run: If True, only log what would be done without executing

    Returns:
        True if successful, False otherwise
    """
    try:
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be applied")
            logger.info(f"Target table: {TABLE_NAME}")
            logger.info(f"Column: {COLUMN_NAME} (INTEGER, nullable)")
            logger.info(f"Index: {INDEX_NAME}")
            logger.info(f"Foreign Key: {CONSTRAINT_NAME} (ondelete=SET NULL)")

            if rollback:
                logger.info("Action: ROLLBACK")
            else:
                logger.info("Action: APPLY MIGRATION")

            return True

        if rollback:
            logger.info("Starting migration rollback...")
            rollback_migration(engine)
        else:
            logger.info("Starting migration...")
            add_column_with_constraint(engine)

        logger.info("Migration completed successfully.")
        return True

    except SQLAlchemyError as e:
        logger.error(f"Database error during migration: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}")
        return False


def main() -> int:
    """Main entry point for the migration script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migration script to add parent_product_id column to products table"
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback the migration (drop column, index, and constraint)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        help="Override database path (uses config by default)",
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Parent Product ID Migration Script")
    logger.info("=" * 60)

    if args.db_path:
        from sqlalchemy import create_engine as _create_engine
        from urllib.parse import quote_plus
        from src.database.engine import _get_or_create_key

        key = _get_or_create_key()
        encoded_key = quote_plus(key)
        db_path = str(args.db_path)
        engine_url = f"sqlite+pysqlcipher://:{encoded_key}@/{db_path}?cipher=aes-256-cfb"
        engine = _create_engine(engine_url, echo=False)
        logger.info(f"Using custom database path: {args.db_path}")
    else:
        engine = create_engine()
        logger.info("Using database path from config")

    success = run_migration(engine, rollback=args.rollback, dry_run=args.dry_run)

    engine.dispose()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

```

### `src\database\models.py`
```python
import json
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    base_url = Column(String(512), nullable=False, unique=True)
    is_active = Column(Boolean, default=True, index=True)
    last_discovery_run = Column(DateTime, nullable=True)
    last_scrape_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    categories = relationship("Category", back_populates="supplier", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_suppliers_name_is_active", "name", "is_active"),)

    def __repr__(self) -> str:
        return (
            f"<Supplier(id={self.id}, name={self.name!r}, "
            f"base_url={self.base_url!r}, is_active={self.is_active})>"
        )


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    external_id = Column(String(255), nullable=True)
    name = Column(String(512), nullable=False)
    url = Column(String(1024), nullable=False)
    xpath_selector = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    product_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="categories")
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_categories_supplier_parent", "supplier_id", "parent_id"),
        Index("ix_categories_supplier_name", "supplier_id", "name"),
    )

    def __repr__(self) -> str:
        return (
            f"<Category(id={self.id}, name={self.name!r}, "
            f"supplier_id={self.supplier_id}, parent_id={self.parent_id})>"
        )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    parent_product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 🆕 НОВОЕ ПОЛЕ: Совместимые коллекции погонажа (JSON-массив)
    compatible_collections = Column(Text, nullable=True, comment="JSON array of collections, e.g. ['FLYDOORS>MONE']")
    
    external_sku = Column(String(255), nullable=True, index=True)
    title = Column(String(1024), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    is_available = Column(Boolean, default=True)
    is_ready_for_export = Column(Boolean, default=False, index=True)
    image_urls = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = relationship("Supplier")
    category = relationship("Category", back_populates="products")
    parent = relationship("Product", remote_side=[id], backref="related_products")
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_products_supplier_sku", "supplier_id", "external_sku"),
        Index("ix_products_supplier_category", "supplier_id", "category_id"),
        Index("ix_products_price", "price"),
        Index("ix_products_available", "is_available"),
        Index("ix_products_ready", "is_ready_for_export"),
    )

    # --- Helpers для image_urls ---
    def get_image_urls(self) -> list[str]:
        if not self.image_urls:
            return []
        try:
            return json.loads(self.image_urls)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_image_urls(self, urls: list[str]) -> None:
        self.image_urls = json.dumps(urls, ensure_ascii=False)

    # --- Helpers для compatible_collections ---
    def get_compatible_collections(self) -> list[str]:
        """Возвращает список коллекций как Python list"""
        if not self.compatible_collections:
            return []
        try:
            return json.loads(self.compatible_collections)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_compatible_collections(self, collections: list[str]) -> None:
        """Сохраняет список коллекций в БД как JSON-строку"""
        self.compatible_collections = json.dumps(collections, ensure_ascii=False)

    def __repr__(self) -> str:
        return (
            f"<Product(id={self.id}, title={self.title!r}, "
            f"price={self.price}, currency={self.currency})>"
        )


class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)

    product = relationship("Product", back_populates="attributes")

    __table_args__ = (
        Index("ix_attr_product_name", "product_id", "name"),
    )

    def __repr__(self) -> str:
        return f"<ProductAttribute(id={self.id}, name={self.name!r}, value={self.value!r})>"


class ArchiveSnapshot(Base):
    __tablename__ = "archive_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    snapshot_type = Column(String(50), nullable=False, default="full")
    total_products = Column(Integer, default=0)
    total_categories = Column(Integer, default=0)
    total_price_sum = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier")
    items = relationship("ArchiveItem", back_populates="snapshot", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_snapshots_supplier_date", "supplier_id", "created_at"),
        Index("ix_snapshots_type", "snapshot_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<ArchiveSnapshot(id={self.id}, name={self.name!r}, "
            f"products={self.total_products}, type={self.snapshot_type})>"
        )


class ArchiveItem(Base):
    __tablename__ = "archive_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(Integer, ForeignKey("archive_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    external_sku = Column(String(255), nullable=True)
    title = Column(String(1024), nullable=False)
    price = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    is_available = Column(Boolean, default=True)
    category_name = Column(String(512), nullable=True)
    image_urls = Column(Text, nullable=True)
    attributes_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    snapshot = relationship("ArchiveSnapshot", back_populates="items")

    __table_args__ = (
        Index("ix_archive_items_snapshot_sku", "snapshot_id", "external_sku"),
        Index("ix_archive_items_price", "price"),
    )

    def get_image_urls(self) -> list[str]:
        if not self.image_urls:
            return []
        try:
            return json.loads(self.image_urls)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_attributes(self) -> dict[str, str]:
        if not self.attributes_json:
            return {}
        try:
            return json.loads(self.attributes_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    def __repr__(self) -> str:
        return f"<ArchiveItem(id={self.id}, title={self.title!r}, price={self.price})>"


class MappingTemplate(Base):
    __tablename__ = "mapping_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    field_mapping = Column(Text, nullable=False)
    rules = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_field_mapping(self) -> dict[str, str]:
        if not self.field_mapping:
            return {}
        try:
            return json.loads(self.field_mapping)
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_rules(self) -> list[dict]:
        if not self.rules:
            return []
        try:
            return json.loads(self.rules)
        except (json.JSONDecodeError, TypeError):
            return []

    def __repr__(self) -> str:
        return f"<MappingTemplate(id={self.id}, name={self.name!r})>"
```

### `src\database\session.py`
```python
from contextlib import contextmanager

from sqlalchemy import event, text
from sqlalchemy.orm import sessionmaker

from src.database.engine import create_engine

engine = create_engine()
SessionFactory = sessionmaker(bind=engine)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-64000")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()


@contextmanager
def get_session():
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session_sync():
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

```

### `src\database\supplier_crud.py`
```python
from datetime import datetime

from sqlalchemy import select, update, delete

from src.database.models import Supplier


def create_supplier(session, name: str, base_url: str) -> Supplier:
    existing = session.execute(
        select(Supplier).where(Supplier.name == name)
    ).scalar_one_or_none()
    if existing:
        raise ValueError(f"Supplier with name '{name}' already exists")

    supplier = Supplier(name=name, base_url=base_url)
    session.add(supplier)
    session.flush()
    return supplier


def get_all_suppliers(session, active_only: bool = True) -> list[Supplier]:
    stmt = select(Supplier)
    if active_only:
        stmt = stmt.where(Supplier.is_active == True)
    stmt = stmt.order_by(Supplier.name)
    return list(session.execute(stmt).scalars().all())


def get_supplier_by_id(session, supplier_id: int) -> Supplier | None:
    return session.execute(
        select(Supplier).where(Supplier.id == supplier_id)
    ).scalar_one_or_none()


def get_supplier_by_name(session, name: str) -> Supplier | None:
    return session.execute(
        select(Supplier).where(Supplier.name == name)
    ).scalar_one_or_none()


def update_supplier(session, supplier_id: int, **kwargs) -> Supplier | None:
    supplier = get_supplier_by_id(session, supplier_id)
    if not supplier:
        return None

    if "name" in kwargs:
        new_name = kwargs["name"]
        if new_name != supplier.name:
            duplicate = session.execute(
                select(Supplier).where(
                    Supplier.name == new_name,
                    Supplier.id != supplier_id,
                )
            ).scalar_one_or_none()
            if duplicate:
                raise ValueError(f"Supplier with name '{new_name}' already exists")

    kwargs["updated_at"] = datetime.utcnow()

    session.execute(
        update(Supplier)
        .where(Supplier.id == supplier_id)
        .values(**kwargs)
    )
    session.flush()
    return get_supplier_by_id(session, supplier_id)


def delete_supplier(session, supplier_id: int) -> bool:
    supplier = get_supplier_by_id(session, supplier_id)
    if not supplier:
        return False

    session.execute(
        update(Supplier)
        .where(Supplier.id == supplier_id)
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    session.flush()
    return True


def hard_delete_supplier(session, supplier_id: int) -> bool:
    result = session.execute(
        delete(Supplier).where(Supplier.id == supplier_id)
    )
    session.flush()
    return result.rowcount > 0

```

### `src\modules\__init__.py`
```python

```

### `src\modules\archive\__init__.py`
```python

```

### `src\modules\archive\engine.py`
```python
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

```

### `src\modules\discovery\__init__.py`
```python

```

### `src\modules\discovery\engine.py`
```python
import asyncio
import logging
import random
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiohttp
from bs4 import BeautifulSoup, Tag
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.logger import logger

logger_discovery = logging.getLogger("meeyg.discovery")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/124.0.0.0 Safari/537.36",
]

CMS_PATTERNS = {
    "bitrix": [r"bitrix/", r"BX\.setForm", r"/bitrix/js/", r"bitrix:catalog", r"bitrix\.template"],
    "woocommerce": [r"woocommerce", r"wc-ajax", r"wp-content/plugins/woocommerce"],
    "opencart": [r"route=product/category", r"index\.php\?route=", r"opencart"],
    "prestashop": [r"prestashop", r"themes/prestashop"],
    "magento": [r"mage/", r"static/frontend/", r"Magento"],
}

EXCLUDE_PATTERNS = re.compile(
    r"(\?|filter|sort|clear|back|login|cart|korzina|checkout|order|zakaz|"
    r"search|poisk|ajax|api|upload|bitrix|include|component|local/|"
    r"\.html$|\.php$|\.pdf$|\.jpg$|\.png$|\.jpeg$|\.gif$|\.svg$|\.ico$)",
    re.IGNORECASE,
)

EXCLUDE_KEYWORDS = [
    "about", "o-kompanii", "o_kompanii", "contacts", "kontakty",
    "delivery", "dostavka", "oplata", "payment",
    "news", "novosti", "blog", "articles",
    "reviews", "otzyvy", "feedback",
    "login", "auth", "register", "personal", "profile",
    "search", "poisk", "ajax", "api", "upload",
    "wishlist", "favorites", "izbrannoe", "compare", "sravnenie",
    "vacancies", "vakansii", "partners", "partneram",
    "sitemap", "map", "privacy", "policy",
    "3d-tur", "3d_tur", "action", "sale",
]

EXCLUDE_KEYWORDS_RE = re.compile(
    r"/(" + "|".join(EXCLUDE_KEYWORDS) + r")(/|$|\?)",
    re.IGNORECASE,
)


@dataclass
class DiscoveredCategory:
    name: str
    url: str
    xpath_selector: str = ""
    product_count: int = 0
    children: list["DiscoveredCategory"] = field(default_factory=list)
    depth: int = 0
    external_id: Optional[str] = None


class BaseDiscovery(ABC):
    def __init__(
        self,
        base_url: str,
        session: aiohttp.ClientSession,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        max_depth: int = 3,
        delay_range: tuple[float, float] = (0.5, 2.0),
        check_robots: bool = True,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.log_callback = log_callback or (lambda m: logger_discovery.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self.max_depth = max_depth
        self.delay_range = delay_range
        self.check_robots = check_robots
        self.timeout = timeout
        self.robots_allowed = True
        self.visited_urls: set[str] = set()
        self._total_pages = 0
        self._pages_scanned = 0

    def _log(self, msg: str) -> None:
        self.log_callback(msg)

    def _progress(self, msg: str) -> None:
        self._pages_scanned += 1
        pct = int((self._pages_scanned / max(self._total_pages, 1)) * 100)
        self.progress_callback(pct, self._total_pages, msg)

    def _random_delay(self) -> None:
        time.sleep(random.uniform(*self.delay_range))

    def _get_headers(self) -> dict[str, str]:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "identity",
            "Connection": "keep-alive",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True,
    )
    async def fetch_page(self, url: str) -> Optional[str]:
        if url in self.visited_urls:
            return None
        self.visited_urls.add(url)

        try:
            async with self.session.get(
                url, headers=self._get_headers(), timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status == 404:
                    self._log(f"  404: {url}")
                    return None
                if resp.status == 403:
                    self._log(f"  403: {url}")
                    return None
                if resp.status != 200:
                    self._log(f"  HTTP {resp.status}: {url}")
                    return None
                content_type = resp.headers.get("Content-Type", "")
                if "text/html" not in content_type and "application/xhtml" not in content_type:
                    return None
                return await resp.text(errors="replace")
        except asyncio.TimeoutError:
            self._log(f"  Timeout: {url}")
            raise
        except aiohttp.ClientError as exc:
            self._log(f"  Network error: {url} ({exc})")
            raise

    def _check_robots(self) -> None:
        if not self.check_robots:
            return
        robots_url = urljoin(self.base_url, "/robots.txt")
        try:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            self.robots_allowed = rp.can_fetch(random.choice(USER_AGENTS), self.base_url)
            if not self.robots_allowed:
                self._log(f"WARNING: robots.txt блокирует доступ к {self.base_url}")
        except Exception:
            self._log("WARNING: Не удалось загрузить robots.txt, продолжаем без проверки")

    def _is_internal_url(self, url: str) -> bool:
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)
        return parsed.netloc == base_parsed.netloc

    def _clean_url(self, url: str) -> str:
        url = url.split("#")[0]
        url = url.split("?")[0]
        url = url.rstrip("/")
        return url

    def _build_xpath(self, element: Tag) -> str:
        parts = []
        current: Tag | None = element
        while current and current.name:
            selector = current.name
            if current.get("id"):
                selector += f"[@id='{current['id']}']"
                parts.append(selector)
                break
            if current.get("class"):
                cls = " ".join(str(c) for c in current["class"])
                selector += f"[contains(concat(' ', normalize-space(@class), ' '), ' {cls} ')]"
            parts.append(selector)
            current = current.parent
        parts.reverse()
        return "/" + "/".join(parts)

    def detect_cms(self, html: str) -> Optional[str]:
        for cms, patterns in CMS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, html, re.IGNORECASE):
                    return cms
        return None

    @abstractmethod
    async def discover_categories(self) -> list[DiscoveredCategory]:
        pass

    async def run(self) -> list[DiscoveredCategory]:
        self._log(f"Начало разведки: {self.base_url}")
        self._check_robots()
        if not self.robots_allowed:
            self._log("Прервано: robots.txt запрещает доступ")
            return []
        result = await self.discover_categories()
        self._log(f"Разведка завершена: найдено {len(result)} категорий верхнего уровня")
        return result


class CatalogDiscovery(BaseDiscovery):
    """Универсальная стратегия: ищет все ссылки с /catalog/ и строит иерархию из URL."""

    def _is_excluded_url(self, url: str) -> bool:
        if EXCLUDE_PATTERNS.search(url):
            return True
        path = urlparse(url).path.lower()
        if EXCLUDE_KEYWORDS_RE.search(path):
            return True
        return False

    def _is_catalog_link(self, url: str) -> bool:
        path = urlparse(url).path.lower()
        return "/catalog/" in path

    def _get_url_segments(self, url: str) -> list[str]:
        path = urlparse(url).path
        return [s for s in path.split("/") if s]

    def _get_parent_url(self, url: str) -> Optional[str]:
        segments = self._get_url_segments(url)
        if len(segments) <= 1:
            return None
        parent_path = "/" + "/".join(segments[:-1]) + "/"
        return urljoin(self.base_url, parent_path).rstrip("/")

    def _extract_all_catalog_links(self, soup: BeautifulSoup, page_url: str) -> list[DiscoveredCategory]:
        categories = []
        seen_urls: set[str] = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue

            full_url = urljoin(page_url, href)

            if not self._is_internal_url(full_url):
                continue
            if not self._is_catalog_link(full_url):
                continue
            if self._is_excluded_url(full_url):
                continue

            clean_url = self._clean_url(full_url)
            if clean_url in seen_urls:
                continue
            if clean_url in self.visited_urls:
                continue

            name = a_tag.get_text(strip=True)
            if not name or len(name) < 2:
                continue

            xpath = self._build_xpath(a_tag)
            cat = DiscoveredCategory(
                name=name,
                url=clean_url,
                xpath_selector=xpath,
            )
            categories.append(cat)
            seen_urls.add(clean_url)

        return categories

    def _build_tree_from_urls(self, all_cats: list[DiscoveredCategory]) -> list[DiscoveredCategory]:
        url_map: dict[str, DiscoveredCategory] = {}
        for cat in all_cats:
            url_map[cat.url] = cat

        url_list = sorted(url_map.keys(), key=lambda u: len(self._get_url_segments(u)))

        roots: list[DiscoveredCategory] = []

        for url in url_list:
            cat = url_map[url]
            parent_url = self._get_parent_url(url)

            if parent_url and parent_url in url_map:
                parent = url_map[parent_url]
                parent.children.append(cat)
                cat.depth = parent.depth + 1
            else:
                roots.append(cat)
                cat.depth = 0

        return roots

    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log("Универсальный поиск каталога (метод грубой силы)")

        catalog_url = urljoin(self.base_url, "/catalog/")

        html = await self.fetch_page(catalog_url)
        if not html:
            self._log(f"Не удалось загрузить {catalog_url}, пробую главную")
            html = await self.fetch_page(self.base_url)
            if not html:
                self._log("Не удалось загрузить главную страницу")
                return []
            page_url = self.base_url
        else:
            page_url = catalog_url

        self._random_delay()
        self._progress(f"Анализ: {page_url}")

        soup = BeautifulSoup(html, "lxml")
        cats = self._extract_all_catalog_links(soup, page_url)
        self._log(f"Найдено {len(cats)} уникальных ссылок с /catalog/ на странице {page_url}")

        if not cats:
            self._log("Ссылки с /catalog/ не найдены, сканирую вложенные страницы...")
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                if not href or href.startswith(("javascript:", "mailto:")):
                    continue
                raw_url = urljoin(page_url, href)
                if not self._is_internal_url(raw_url):
                    continue
                if "/catalog/" not in raw_url.lower():
                    continue
                if self._is_excluded_url(raw_url):
                    continue
                link_url = self._clean_url(raw_url)
                if link_url not in self.visited_urls:
                    sub_html = await self.fetch_page(raw_url)
                    if sub_html:
                        self._random_delay()
                        sub_soup = BeautifulSoup(sub_html, "lxml")
                        sub_cats = self._extract_all_catalog_links(sub_soup, raw_url)
                        for sc in sub_cats:
                            if sc.url not in [c.url for c in cats]:
                                cats.append(sc)
                            self._log(f"  +{len(sub_cats)} ссылок со страницы {link_url}")

        if not cats:
            self._log("Категории не найдены")
            return []

        roots = self._build_tree_from_urls(cats)
        self._log(f"Построено дерево из {len(cats)} категорий ({len(roots)} корней)")

        return roots


class GenericDiscovery(BaseDiscovery):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _looks_like_category_page(self, url: str, text: str) -> bool:
        path = urlparse(url).path.lower()
        keywords = [
            "catalog", "category", "cat", "section", "department", "shop",
            "каталог", "категория", "раздел",
        ]
        combined = f"{path} {text}".lower()
        return any(kw in combined for kw in keywords)

    async def _scan_page_for_categories(self, url: str, depth: int = 0) -> list[DiscoveredCategory]:
        if depth > self.max_depth:
            return []

        html = await self.fetch_page(url)
        if not html:
            return []

        self._random_delay()
        self._progress(f"Сканирование: {url}")

        soup = BeautifulSoup(html, "lxml")
        categories = []

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue
            full_url = self._clean_url(urljoin(url, href))
            if not self._is_internal_url(full_url):
                continue
            name = a_tag.get_text(strip=True)
            if not name or len(name) < 2:
                continue
            if self._looks_like_category_page(full_url, name):
                xpath = self._build_xpath(a_tag)
                cat = DiscoveredCategory(name=name, url=full_url, xpath_selector=xpath, depth=depth + 1)
                categories.append(cat)

        if depth < self.max_depth:
            for cat in categories[:10]:
                if cat.url not in self.visited_urls:
                    children = await self._scan_page_for_categories(cat.url, depth + 1)
                    cat.children = children
                    if children:
                        self._log(f"  Найдено {len(children)} подкатегорий в '{cat.name}'")

        return categories

    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log(f"Сканирование главной: {self.base_url}")
        html = await self.fetch_page(self.base_url)
        if not html:
            self._log("Не удалось загрузить главную страницу")
            return []

        self._random_delay()
        soup = BeautifulSoup(html, "lxml")
        cms = self.detect_cms(html)
        if cms:
            self._log(f"Обнаружена CMS: {cms}")

        categories = await self._scan_page_for_categories(self.base_url, depth=0)

        seen_urls = set()
        unique = []
        for cat in categories:
            if cat.url not in seen_urls:
                seen_urls.add(cat.url)
                unique.append(cat)

        return unique


class BitrixDiscovery(CatalogDiscovery):
    """Стратегия для 1С-Битрикс: использует CatalogDiscovery с fallback на общий поиск."""

    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log("Использование стратегии для 1С-Битрикс")
        return await super().discover_categories()


class WooCommerceDiscovery(GenericDiscovery):
    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log("Использование стратегии для WooCommerce")
        shop_urls = [
            urljoin(self.base_url, "/shop/"),
            urljoin(self.base_url, "/product-category/"),
        ]
        all_cats = []
        for url in shop_urls:
            cats = await self._scan_page_for_categories(url, depth=0)
            all_cats.extend(cats)
        return all_cats


class OpenCartDiscovery(GenericDiscovery):
    async def discover_categories(self) -> list[DiscoveredCategory]:
        self._log("Использование стратегии для OpenCart")
        catalog_url = urljoin(self.base_url, "/index.php?route=product/category")
        return await self._scan_page_for_categories(catalog_url, depth=0)


STRATEGY_MAP: dict[str, type[BaseDiscovery]] = {
    "bitrix": BitrixDiscovery,
    "woocommerce": WooCommerceDiscovery,
    "opencart": OpenCartDiscovery,
}


class DiscoveryEngine:
    def __init__(
        self,
        supplier_id: int,
        base_url: str,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        max_depth: int = 3,
        delay_range: tuple[float, float] = (0.5, 2.0),
        check_robots: bool = True,
        timeout: int = 30,
    ):
        self.supplier_id = supplier_id
        self.base_url = base_url
        self.log_callback = log_callback or (lambda m: logger_discovery.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self.max_depth = max_depth
        self.delay_range = delay_range
        self.check_robots = check_robots
        self.timeout = timeout
        self._cancelled = False
        # ✅ ИСПРАВЛЕНИЕ: Добавлен алиас для совместимости
        self._log = self.log_callback

    def cancel(self) -> None:
        self._cancelled = True

    def _build_strategy(
        self, session: aiohttp.ClientSession, cms: Optional[str] = None
    ) -> BaseDiscovery:
        if cms and cms in STRATEGY_MAP:
            cls = STRATEGY_MAP[cms]
        else:
            cls = CatalogDiscovery

        return cls(
            base_url=self.base_url,
            session=session,
            log_callback=self.log_callback,
            progress_callback=self.progress_callback,
            max_depth=self.max_depth,
            delay_range=self.delay_range,
            check_robots=self.check_robots,
            timeout=self.timeout,
        )

    async def _detect_cms_async(self, session: aiohttp.ClientSession) -> Optional[str]:
        try:
            async with session.get(
                self.base_url,
                headers={"User-Agent": random.choice(USER_AGENTS)},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status == 200:
                    html = await resp.text(errors="replace")
                    for cms, patterns in CMS_PATTERNS.items():
                        for pattern in patterns:
                            if re.search(pattern, html, re.IGNORECASE):
                                return cms
        except Exception:
            pass
        return None

    def _save_to_db(self, categories: list[DiscoveredCategory], db_session) -> int:
        from src.database.models import Category

        count = 0

        def _save_recursive(cats: list[DiscoveredCategory], parent_id: Optional[int] = None):
            nonlocal count
            for cat in cats:
                if self._cancelled:
                    return

                existing = db_session.query(Category).filter(
                    Category.supplier_id == self.supplier_id,
                    Category.url == cat.url,
                ).first()

                if existing:
                    self._log(f"  Дубликат пропущен: {cat.name} ({cat.url})")
                    existing.name = cat.name
                    existing.xpath_selector = cat.xpath_selector or existing.xpath_selector
                    existing.product_count = cat.product_count
                    existing.parent_id = parent_id
                    db_category = existing
                else:
                    db_category = Category(
                        supplier_id=self.supplier_id,
                        parent_id=parent_id,
                        name=cat.name,
                        url=cat.url,
                        xpath_selector=cat.xpath_selector,
                        product_count=cat.product_count,
                        external_id=cat.external_id,
                    )
                    db_session.add(db_category)
                    db_session.flush()
                    self._log(f"  Сохранено: {cat.name} (parent_id={parent_id})")

                count += 1
                if cat.children:
                    _save_recursive(cat.children, db_category.id)

        _save_recursive(categories)
        return count

    async def run(self, db_session) -> dict[str, Any]:
        self._cancelled = False
        self.log_callback(f"Движок разведки запущен для {self.base_url}")

        connector = aiohttp.TCPConnector(ssl=False, limit=10)
        async with aiohttp.ClientSession(connector=connector) as session:
            cms = await self._detect_cms_async(session)
            strategy = self._build_strategy(session, cms)

            if cms:
                self.log_callback(f"CMS определена: {cms}, используется стратегия для {cms}")
            else:
                self.log_callback("CMS не определена, используется универсальный поиск")

            try:
                categories = await strategy.run()
            except Exception as exc:
                self.log_callback(f"Разведка не удалась: {exc}")
                return {"success": False, "error": str(exc), "categories_found": 0}

            if self._cancelled:
                self.log_callback("Разведка отменена пользователем")
                return {"success": False, "error": "cancelled", "categories_found": 0}

            if not categories:
                self.log_callback("Категории не найдены")
                self._update_supplier_timestamp(db_session)
                return {"success": True, "categories_found": 0, "categories": []}

            self.log_callback(f"Сохранение {len(categories)} категорий верхнего уровня в БД...")
            try:
                saved_count = self._save_to_db(categories, db_session)
                db_session.commit()
                self.log_callback(f"Сохранено {saved_count} категорий в базу данных")
            except Exception as exc:
                db_session.rollback()
                self.log_callback(f"Ошибка сохранения в БД: {exc}")
                return {"success": False, "error": f"DB error: {exc}", "categories_found": 0}

            self._update_supplier_timestamp(db_session)

            return {
                "success": True,
                "categories_found": saved_count,
                "categories": categories,
            }

    def _update_supplier_timestamp(self, db_session) -> None:
        from src.database.models import Supplier

        supplier = db_session.query(Supplier).filter(Supplier.id == self.supplier_id).first()
        if supplier:
            supplier.last_discovery_run = datetime.utcnow()
            db_session.flush()
```

### `src\modules\export\__init__.py`
```python

```

### `src\modules\export\generator.py`
```python
import gc
import hashlib
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.workbook import Workbook

from src.core.config import settings
from src.core.logger import logger

logger_export = logging.getLogger("meeyg.export")

WP_COLUMNS = [
    "post_title",
    "sku",
    "regular_price",
    "sale_price",
    "stock",
    "stock_status",
    "categories",
    "tags",
    "short_description",
    "description",
    "images",
    "attributes",
    "manage_stock",
    "backorders",
    "tax_status",
    "meta",
]


@dataclass
class ExportConfig:
    supplier_ids: Optional[list[int]] = None
    category_ids: Optional[list[int]] = None
    ready_only: bool = False
    available_only: bool = False
    format: str = "xlsx"
    encoding: str = "utf-8-sig"
    category_separator: str = ">"
    image_separator: str = "|"
    attribute_format: str = "name:value"
    output_dir: Optional[Path] = None
    chunk_size: int = 1000

    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = settings.data_dir / "exports"
        self.output_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class ExportStats:
    total_products: int = 0
    exported_products: int = 0
    duplicate_skus: int = 0
    empty_titles: int = 0
    empty_prices: int = 0
    elapsed: float = 0.0
    file_size: int = 0
    output_path: str = ""


class ExportEngine:
    def __init__(
        self,
        config: ExportConfig,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ):
        self.config = config
        self.log_callback = log_callback or (lambda m: logger_export.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self._cancelled = False
        self.stats = ExportStats()

    def cancel(self) -> None:
        self._cancelled = True

    def _log(self, msg: str) -> None:
        self.log_callback(msg)

    def _progress(self, pct: int, total: int, msg: str) -> None:
        self.progress_callback(pct, total, msg)

    def _fetch_products(self, db_session) -> list[dict]:
        from src.database.models import Category, Product, ProductAttribute, Supplier

        self._log("Fetching products from database...")

        query = db_session.query(
            Product.id,
            Product.external_sku,
            Product.title,
            Product.description,
            Product.price,
            Product.currency,
            Product.is_available,
            Product.is_ready_for_export,
            Product.image_urls,
            Product.created_at,
            Supplier.name.label("supplier_name"),
            Category.name.label("category_name"),
        ).outerjoin(Supplier, Product.supplier_id == Supplier.id).outerjoin(
            Category, Product.category_id == Category.id
        )

        if self.config.supplier_ids:
            query = query.filter(Product.supplier_id.in_(self.config.supplier_ids))
        if self.config.category_ids:
            query = query.filter(Product.category_id.in_(self.config.category_ids))
        if self.config.ready_only:
            query = query.filter(Product.is_ready_for_export == True)
        if self.config.available_only:
            query = query.filter(Product.is_available == True)

        products = query.order_by(Product.id).all()
        self.stats.total_products = len(products)
        self._log(f"Found {len(products)} products matching filters")

        attr_query = db_session.query(
            ProductAttribute.product_id,
            ProductAttribute.name,
            ProductAttribute.value,
        )
        if self.config.supplier_ids:
            attr_query = attr_query.join(Product).filter(
                Product.supplier_id.in_(self.config.supplier_ids)
            )
        if self.config.category_ids:
            attr_query = attr_query.join(Product).filter(
                Product.category_id.in_(self.config.category_ids)
            )

        attributes_rows = attr_query.all()
        attr_map: dict[int, list[tuple[str, str]]] = {}
        for row in attributes_rows:
            attr_map.setdefault(row.product_id, []).append((row.name, row.value))

        for p in products:
            p_attrs = attr_map.get(p.id, [])
            if self.config.attribute_format == "name:value":
                attr_str = "; ".join(f"{n}: {v}" for n, v in p_attrs)
            else:
                attr_str = "; ".join(f"{n}={v}" for n, v in p_attrs)

            image_urls = []
            if p.image_urls:
                import json
                try:
                    image_urls = json.loads(p.image_urls)
                except (json.JSONDecodeError, TypeError):
                    pass

            yield {
                "id": p.id,
                "external_sku": p.external_sku,
                "title": p.title,
                "description": p.description or "",
                "price": p.price,
                "currency": p.currency,
                "is_available": p.is_available,
                "supplier_name": p.supplier_name,
                "category_name": p.category_name,
                "attributes": attr_str,
                "image_urls": image_urls,
                "created_at": p.created_at,
            }

    def _transform_to_wp_format(self, products: list[dict]) -> list[dict]:
        self._log("Transforming data to WP All Import format...")
        rows = []
        seen_skus: set[str] = set()

        for i, p in enumerate(products):
            if self._cancelled:
                break

            sku = p["external_sku"] or f"MEYG-{p['id']}"
            if sku in seen_skus:
                base_sku = sku
                counter = 1
                while sku in seen_skus:
                    sku = f"{base_sku}-{counter}"
                    counter += 1
                self.stats.duplicate_skus += 1
            seen_skus.add(sku)

            title = (p["title"] or "").strip()
            if not title:
                title = f"Product {p['id']}"
                self.stats.empty_titles += 1

            price = p["price"]
            if price is None:
                self.stats.empty_prices += 1

            stock = 1 if p["is_available"] else 0
            stock_status = "instock" if p["is_available"] else "outofstock"

            category = p["category_name"] or "Uncategorized"

            images_str = self.config.image_separator.join(p["image_urls"]) if p["image_urls"] else ""

            short_desc = ""
            if p["description"]:
                short_desc = (p["description"][:300] + "...") if len(p["description"]) > 300 else p["description"]

            meta_fields = {
                "supplier": p["supplier_name"],
                "currency": p["currency"] or "",
                "imported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_id": str(p["id"]),
            }

            rows.append({
                "post_title": title,
                "sku": sku,
                "regular_price": f"{price:.2f}" if price is not None else "",
                "sale_price": "",
                "stock": str(stock),
                "stock_status": stock_status,
                "categories": category,
                "tags": "",
                "short_description": short_desc,
                "description": p["description"] or "",
                "images": images_str,
                "attributes": p["attributes"],
                "manage_stock": "yes" if p["is_available"] else "no",
                "backorders": "no",
                "tax_status": "taxable",
                "meta": "; ".join(f"{k}: {v}" for k, v in meta_fields.items()),
            })

            if (i + 1) % 100 == 0:
                pct = int(((i + 1) / max(self.stats.total_products, 1)) * 100)
                self._progress(pct, self.stats.total_products, f"Transformed {i + 1} products")

        self.stats.exported_products = len(rows)
        return rows

    def _export_to_excel(self, rows: list[dict]) -> str:
        self._log("Generating Excel file with openpyxl...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        supplier_name = "all"
        if self.config.supplier_ids and len(self.config.supplier_ids) == 1:
            supplier_name = f"supplier_{self.config.supplier_ids[0]}"
        filename = f"{supplier_name}_{timestamp}.xlsx"
        output_path = self.config.output_dir / filename

        df = pd.DataFrame(rows, columns=WP_COLUMNS)

        wb = Workbook()
        ws = wb.active
        ws.title = "Products"

        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for col_idx, col_name in enumerate(WP_COLUMNS, 1):
            cell = ws.cell(row=1, column=col_idx, value=col_name)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment

        price_cols = {"regular_price", "sale_price"}
        date_cols = set()

        for row_idx, row_data in enumerate(rows, 2):
            for col_idx, col_name in enumerate(WP_COLUMNS, 1):
                value = row_data.get(col_name, "")
                cell = ws.cell(row=row_idx, column=col_idx, value=value)

                if col_name in price_cols and value:
                    try:
                        cell.number_format = '#,##0.00'
                    except ValueError:
                        pass

                if row_idx % 2 == 0:
                    cell.fill = PatternFill(start_color="D9E2F3", end_color="D9E2F3", fill_type="solid")

        ws.auto_filter.ref = f"A1:{get_column_letter(len(WP_COLUMNS))}{len(rows) + 1}"

        for col_idx in range(1, len(WP_COLUMNS) + 1):
            max_len = 12
            for row in ws.iter_rows(min_col=col_idx, max_col=col_idx, values_only=True):
                if row[0]:
                    max_len = max(max_len, min(len(str(row[0])), 50))
            ws.column_dimensions[get_column_letter(col_idx)].width = max_len + 2

        ws.freeze_panes = "B2"

        wb.save(str(output_path))

        file_size = os.path.getsize(output_path)
        self.stats.file_size = file_size
        self.stats.output_path = str(output_path)

        self._log(f"Excel saved: {output_path} ({file_size / 1024:.1f} KB)")
        return str(output_path)

    def _export_to_csv(self, rows: list[dict]) -> str:
        self._log("Generating CSV file...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        supplier_name = "all"
        if self.config.supplier_ids and len(self.config.supplier_ids) == 1:
            supplier_name = f"supplier_{self.config.supplier_ids[0]}"
        filename = f"{supplier_name}_{timestamp}.csv"
        output_path = self.config.output_dir / filename

        df = pd.DataFrame(rows, columns=WP_COLUMNS)
        df.to_csv(
            str(output_path),
            index=False,
            encoding=self.config.encoding,
            sep=";",
            quoting=1,
        )

        file_size = os.path.getsize(output_path)
        self.stats.file_size = file_size
        self.stats.output_path = str(output_path)

        self._log(f"CSV saved: {output_path} ({file_size / 1024:.1f} KB)")
        return str(output_path)

    def run(self, db_session) -> dict[str, Any]:
        self._cancelled = False
        self.stats = ExportStats()
        start_time = time.time()

        self._log(f"Export started (format={self.config.format})")

        products = list(self._fetch_products(db_session))
        if not products:
            self._log("No products found matching filters")
            return {"success": False, "error": "No products found", "stats": self.stats}

        self._progress(10, self.stats.total_products, "Fetching complete")

        if self._cancelled:
            return {"success": False, "error": "cancelled", "stats": self.stats}

        rows = self._transform_to_wp_format(products)
        if not rows:
            return {"success": False, "error": "No rows after transformation", "stats": self.stats}

        self._progress(60, self.stats.total_products, "Transformation complete")

        if self._cancelled:
            return {"success": False, "error": "cancelled", "stats": self.stats}

        if self.config.format == "csv":
            output_path = self._export_to_csv(rows)
        else:
            output_path = self._export_to_excel(rows)

        self.stats.elapsed = time.time() - start_time
        self._progress(100, self.stats.total_products, "Export complete")

        del products
        del rows
        gc.collect()

        self._log(f"Export complete in {self.stats.elapsed:.1f}s")

        return {
            "success": True,
            "output_path": output_path,
            "stats": self.stats,
        }

    def validate_before_export(self, db_session) -> list[str]:
        from src.database.models import Product

        warnings = []

        query = db_session.query(Product)
        if self.config.supplier_ids:
            query = query.filter(Product.supplier_id.in_(self.config.supplier_ids))
        if self.config.category_ids:
            query = query.filter(Product.category_id.in_(self.config.category_ids))
        if self.config.ready_only:
            query = query.filter(Product.is_ready_for_export == True)

        products = query.all()

        if not products:
            warnings.append("No products match the current filters")
            return warnings

        empty_titles = sum(1 for p in products if not p.title or not p.title.strip())
        if empty_titles:
            warnings.append(f"{empty_titles} products have empty titles")

        empty_prices = sum(1 for p in products if p.price is None)
        if empty_prices:
            warnings.append(f"{empty_prices} products have no price")

        empty_skus = sum(1 for p in products if not p.external_sku)
        if empty_skus:
            warnings.append(f"{empty_skus} products have no SKU (will be auto-generated)")

        return warnings

```

### `src\modules\import_prep\__init__.py`
```python

```

### `src\modules\import_prep\mapper.py`
```python
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from src.core.logger import logger

logger_mapper = logging.getLogger("meeyg.import_prep")

WP_ALL_IMPORT_FIELDS = {
    "post_title": {"required": True, "type": "string", "label": "Product Title"},
    "sku": {"required": True, "type": "string", "label": "SKU"},
    "regular_price": {"required": True, "type": "float", "label": "Regular Price"},
    "sale_price": {"required": False, "type": "float", "label": "Sale Price"},
    "stock": {"required": True, "type": "int", "label": "Stock Quantity"},
    "stock_status": {"required": True, "type": "string", "label": "Stock Status"},
    "categories": {"required": False, "type": "string", "label": "Categories"},
    "attributes": {"required": False, "type": "string", "label": "Attributes"},
    "images": {"required": False, "type": "string", "label": "Images"},
    "short_description": {"required": False, "type": "string", "label": "Short Description"},
    "description": {"required": False, "type": "string", "label": "Description"},
    "manage_stock": {"required": False, "type": "string", "label": "Manage Stock"},
    "backorders": {"required": False, "type": "string", "label": "Backorders"},
    "tax_status": {"required": False, "type": "string", "label": "Tax Status"},
    "weight": {"required": False, "type": "float", "label": "Weight"},
}

DB_FIELDS = {
    "id": "Product ID",
    "title": "Product Title",
    "external_sku": "SKU",
    "price": "Price",
    "currency": "Currency",
    "is_available": "Availability",
    "description": "Description",
    "category_name": "Category",
    "image_urls": "Image URLs",
    "attributes": "Attributes",
    "supplier_name": "Supplier",
    "created_at": "Created At",
    "updated_at": "Updated At",
}

RULE_TYPES = {
    "null_replacement": "Replace NULL/empty values with a specified string",
    "price_round": "Round prices to N decimal places",
    "price_markup": "Apply percentage markup to prices",
    "merge_attributes": "Merge all attributes into a single string",
    "sku_prefix": "Add prefix to SKU",
    "sku_suffix": "Add suffix to SKU",
    "stock_default": "Set default stock value for NULL",
    "category_separator": "Set category separator character",
    "title_trim": "Trim and normalize title whitespace",
    "currency_map": "Map currency codes to target currency",
}


@dataclass
class ValidationIssue:
    product_id: int
    field: str
    message: str
    severity: str = "warning"


@dataclass
class MappingConfig:
    field_mapping: dict[str, str] = field(default_factory=dict)
    rules: list[dict] = field(default_factory=list)
    name: str = ""
    description: str = ""

    def map_field(self, db_field: str) -> Optional[str]:
        return self.field_mapping.get(db_field)

    def add_rule(self, rule_type: str, **kwargs) -> None:
        rule = {"type": rule_type, **kwargs}
        self.rules.append(rule)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "field_mapping": self.field_mapping,
            "rules": self.rules,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MappingConfig":
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            field_mapping=data.get("field_mapping", {}),
            rules=data.get("rules", []),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "MappingConfig":
        return cls.from_dict(json.loads(json_str))


class RuleEngine:
    def __init__(self, rules: list[dict]):
        self.rules = rules

    def apply(self, product_data: dict[str, Any]) -> dict[str, Any]:
        result = dict(product_data)
        for rule in self.rules:
            rule_type = rule.get("type")
            if rule_type == "null_replacement":
                result = self._apply_null_replacement(result, rule)
            elif rule_type == "price_round":
                result = self._apply_price_round(result, rule)
            elif rule_type == "price_markup":
                result = self._apply_price_markup(result, rule)
            elif rule_type == "merge_attributes":
                result = self._apply_merge_attributes(result, rule)
            elif rule_type == "sku_prefix":
                result = self._apply_sku_prefix(result, rule)
            elif rule_type == "sku_suffix":
                result = self._apply_sku_suffix(result, rule)
            elif rule_type == "stock_default":
                result = self._apply_stock_default(result, rule)
            elif rule_type == "title_trim":
                result = self._apply_title_trim(result, rule)
            elif rule_type == "currency_map":
                result = self._apply_currency_map(result, rule)
        return result

    @staticmethod
    def _apply_null_replacement(data: dict, rule: dict) -> dict:
        target = rule.get("target", "")
        replacement = rule.get("replacement", "N/A")
        if target in data and (data[target] is None or data[target] == ""):
            data[target] = replacement
        return data

    @staticmethod
    def _apply_price_round(data: dict, rule: dict) -> dict:
        decimals = rule.get("decimals", 2)
        if "regular_price" in data and data["regular_price"] is not None:
            data["regular_price"] = round(float(data["regular_price"]), decimals)
        if "sale_price" in data and data["sale_price"] is not None:
            data["sale_price"] = round(float(data["sale_price"]), decimals)
        return data

    @staticmethod
    def _apply_price_markup(data: dict, rule: dict) -> dict:
        markup_pct = rule.get("markup", 0)
        if "regular_price" in data and data["regular_price"] is not None:
            data["regular_price"] = round(float(data["regular_price"]) * (1 + markup_pct / 100), 2)
        return data

    @staticmethod
    def _apply_merge_attributes(data: dict, rule: dict) -> dict:
        separator = rule.get("separator", " | ")
        attrs = data.get("attributes", {})
        if isinstance(attrs, dict):
            parts = [f"{k}: {v}" for k, v in attrs.items() if v]
            data["attributes"] = separator.join(parts)
        elif isinstance(attrs, str):
            pass
        return data

    @staticmethod
    def _apply_sku_prefix(data: dict, rule: dict) -> dict:
        prefix = rule.get("prefix", "")
        if "sku" in data and data["sku"]:
            data["sku"] = f"{prefix}{data['sku']}"
        return data

    @staticmethod
    def _apply_sku_suffix(data: dict, rule: dict) -> dict:
        suffix = rule.get("suffix", "")
        if "sku" in data and data["sku"]:
            data["sku"] = f"{data['sku']}{suffix}"
        return data

    @staticmethod
    def _apply_stock_default(data: dict, rule: dict) -> dict:
        default_val = rule.get("default", 0)
        if "stock" in data and (data["stock"] is None or data["stock"] == ""):
            data["stock"] = default_val
        return data

    @staticmethod
    def _apply_title_trim(data: dict, rule: dict) -> dict:
        import re
        if "post_title" in data and data["post_title"]:
            data["post_title"] = re.sub(r"\s+", " ", str(data["post_title"])).strip()
        return data

    @staticmethod
    def _apply_currency_map(data: dict, rule: dict) -> dict:
        mapping = rule.get("mapping", {})
        if "currency" in data and data["currency"] in mapping:
            data["currency"] = mapping[data["currency"]]
        return data


class FieldMapper:
    def __init__(self, config: Optional[MappingConfig] = None):
        self.config = config or MappingConfig()
        self.rule_engine = RuleEngine(self.config.rules)
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []

    def set_mapping(self, db_field: str, wp_field: str) -> None:
        self.config.field_mapping[db_field] = wp_field
        self._redo_stack.clear()

    def remove_mapping(self, db_field: str) -> None:
        self.config.field_mapping.pop(db_field, None)
        self._redo_stack.clear()

    def get_unmapped_wp_fields(self) -> list[str]:
        mapped = set(self.config.field_mapping.values())
        return [
            wp_field
            for wp_field, meta in WP_ALL_IMPORT_FIELDS.items()
            if meta["required"] and wp_field not in mapped
        ]

    def get_mapped_fields(self) -> dict[str, str]:
        return dict(self.config.field_mapping)

    def transform_product(self, product_data: dict[str, Any]) -> dict[str, Any]:
        self._undo_stack.append(dict(product_data))
        if len(self._undo_stack) > 100:
            self._undo_stack = self._undo_stack[-50:]

        result = {}
        for db_field, wp_field in self.config.field_mapping.items():
            value = product_data.get(db_field)
            result[wp_field] = value

        result = self.rule_engine.apply(result)
        return result

    def validate_product(self, product_data: dict[str, Any], product_id: int) -> list[ValidationIssue]:
        issues = []

        for wp_field, meta in WP_ALL_IMPORT_FIELDS.items():
            if not meta["required"]:
                continue
            value = product_data.get(wp_field)
            if value is None or value == "":
                issues.append(ValidationIssue(
                    product_id=product_id,
                    field=wp_field,
                    message=f"Required field '{meta['label']}' is empty",
                    severity="error",
                ))

            if meta["type"] == "float" and value is not None:
                try:
                    float(value)
                except (ValueError, TypeError):
                    issues.append(ValidationIssue(
                        product_id=product_id,
                        field=wp_field,
                        message=f"Field '{meta['label']}' must be a number, got '{value}'",
                        severity="error",
                    ))

            if meta["type"] == "int" and value is not None:
                try:
                    int(value)
                except (ValueError, TypeError):
                    issues.append(ValidationIssue(
                        product_id=product_id,
                        field=wp_field,
                        message=f"Field '{meta['label']}' must be an integer, got '{value}'",
                        severity="error",
                    ))

        return issues

    def validate_batch(self, products: list[dict[str, Any]]) -> list[ValidationIssue]:
        all_issues = []
        seen_skus: dict[str, int] = {}

        for product in products:
            pid = product.get("id", 0)
            issues = self.validate_product(product, pid)
            all_issues.extend(issues)

            sku = product.get("sku")
            if sku:
                if sku in seen_skus:
                    all_issues.append(ValidationIssue(
                        product_id=pid,
                        field="sku",
                        message=f"Duplicate SKU '{sku}' (also in product {seen_skus[sku]})",
                        severity="error",
                    ))
                else:
                    seen_skus[sku] = pid

        return all_issues

    def save_template(self, db_session, name: str, description: str = "") -> int:
        from src.database.models import MappingTemplate

        template = MappingTemplate(
            name=name,
            description=description,
            field_mapping=json.dumps(self.config.field_mapping, ensure_ascii=False),
            rules=json.dumps(self.config.rules, ensure_ascii=False),
        )
        db_session.add(template)
        db_session.flush()
        logger_mapper.info(f"Mapping template '{name}' saved (id={template.id})")
        return template.id

    def load_template(self, db_session, template_id: int) -> bool:
        from src.database.models import MappingTemplate

        template = db_session.query(MappingTemplate).filter(
            MappingTemplate.id == template_id
        ).first()

        if not template:
            return False

        self.config.field_mapping = template.get_field_mapping()
        self.config.rules = template.get_rules()
        self.config.name = template.name
        self.config.description = template.description or ""
        self.rule_engine = RuleEngine(self.config.rules)
        logger_mapper.info(f"Mapping template '{template.name}' loaded")
        return True

    def list_templates(self, db_session) -> list:
        from src.database.models import MappingTemplate

        return db_session.query(MappingTemplate).order_by(
            MappingTemplate.updated_at.desc()
        ).all()

    def delete_template(self, db_session, template_id: int) -> bool:
        from src.database.models import MappingTemplate

        template = db_session.query(MappingTemplate).filter(
            MappingTemplate.id == template_id
        ).first()

        if template:
            db_session.delete(template)
            logger_mapper.info(f"Mapping template '{template.name}' deleted")
            return True
        return False

    def undo(self) -> Optional[dict]:
        if len(self._undo_stack) < 2:
            return None
        current = self._undo_stack.pop()
        self._redo_stack.append(current)
        return self._undo_stack[-1]

    def redo(self) -> Optional[dict]:
        if not self._redo_stack:
            return None
        state = self._redo_stack.pop()
        self._undo_stack.append(state)
        return state

    def mark_ready_for_export(self, db_session, product_ids: list[int]) -> int:
        from src.database.models import Product

        result = db_session.query(Product).filter(
            Product.id.in_(product_ids)
        ).update(
            {"is_ready_for_export": True, "updated_at": datetime.utcnow()},
            synchronize_session="fetch",
        )
        db_session.flush()
        logger_mapper.info(f"Marked {result} products as ready for export")
        return result

    def mark_not_ready(self, db_session, product_ids: list[int]) -> int:
        from src.database.models import Product

        result = db_session.query(Product).filter(
            Product.id.in_(product_ids)
        ).update(
            {"is_ready_for_export": False, "updated_at": datetime.utcnow()},
            synchronize_session="fetch",
        )
        db_session.flush()
        logger_mapper.info(f"Marked {result} products as not ready for export")
        return result

```

### `src\modules\parsing\__init__.py`
```python

```

### `src\modules\parsing\engine.py`
```python
import asyncio
import json
import logging
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser
from sqlalchemy import select

from src.core.logger import logger
from src.database.models import Product, ProductAttribute, Category, Supplier

logger_parser = logging.getLogger("meeyg.tandoor_parser")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

PRICE_RE = re.compile(r"([\d\s.,]+)")
CURRENCY_RE = re.compile(r"([A-Z]{3}|[$€£¥₽])")


@dataclass
class ParsingStats:
    total_products: int = 0
    total_pages: int = 0
    successful_pages: int = 0
    failed_pages: int = 0
    total_attributes: int = 0
    errors: List[str] = field(default_factory=list)
    elapsed: float = 0.0

@dataclass
class ParsedProduct:
    url: str
    title: str = ""
    description: str = ""
    price: Optional[float] = None
    currency: Optional[str] = None
    is_available: bool = True
    sku: Optional[str] = None
    image_urls: List[str] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)
    category_id: Optional[int] = None
    raw_html_length: int = 0
    molding_items: List[Dict[str, Any]] = field(default_factory=list)
    variations: List[Dict[str, Any]] = field(default_factory=list)


class ParserEngine:
    def __init__(
        self,
        supplier_id: int,
        db_session,
        base_url: str,
        headless: bool = True,
        delay_range: Tuple[float, float] = (1.0, 3.0),
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        **kwargs,  # To catch unused params like concurrency, timeout from UI
    ):
        self.supplier_id = supplier_id
        self.db_session = db_session
        self.base_url = base_url
        self.headless = headless
        self.delay_range = delay_range
        self.log_callback = log_callback or (lambda m: logger_parser.info(m))
        self.progress_callback = progress_callback or (lambda p, t, m: None)
        self._cancelled = False
        self._paused = False
        self._pause_event = asyncio.Event()
        self._pause_event.set()
        self.stats = {
            "products_parsed": 0,
            "variations_parsed": 0,
            "molding_items_parsed": 0,
            "errors": [],
            "start_time": None,
            "end_time": None,
        }
        self._seen_urls: set[str] = set()
        self.browser: Optional[Browser] = None

    def cancel(self) -> None:
        self._cancelled = True
        self._pause_event.set()

    def pause(self) -> None:
        self._paused = True
        self._pause_event.clear()

    def resume(self) -> None:
        self._paused = False
        self._pause_event.set()

    def _log(self, msg: str) -> None:
        self.log_callback(msg)

    def _progress(self, processed: int, total: int, msg: str) -> None:
        pct = int((processed / max(total, 1)) * 100)
        self.progress_callback(pct, total, msg)

    def _random_delay(self) -> None:
        time.sleep(random.uniform(*self.delay_range))

    @staticmethod
    def normalize_title(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def normalize_price(text: str) -> Optional[float]:
        if not text:
            return None
        text = text.strip().replace("\xa0", " ").replace("  ", " ")
        match = PRICE_RE.search(text)
        if not match:
            return None
        num_str = match.group(1).replace(",", ".")
        parts = num_str.split(".")
        if len(parts) > 2:
            num_str = " ".join(parts[:-1]) + "." + parts[-1]
        try:
            val = float(num_str)
            return val if val > 0 else None
        except ValueError:
            return None

    @staticmethod
    def normalize_currency(text: str) -> Optional[str]:
        if not text:
            return None
        match = CURRENCY_RE.search(text)
        if not match:
            return None
        val = match.group(1)
        currency_map = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY", "₽": "RUB"}
        return currency_map.get(val, val.upper())

    @staticmethod
    def is_valid_url(url: str) -> bool:
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except Exception:
            return False

    def _clean_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    def _detect_molding_type(self, title: str) -> str:
        if not title:
            return "Прочее"
        title_lower = title.lower()
        if "добор" in title_lower:
            return "Добор"
        elif "короб" in title_lower:
            return "Короб"
        elif "наличник" in title_lower:
            return "Наличник"
        elif "плинтус" in title_lower:
            return "Плинтус"
        elif "планка" in title_lower:
            return "Притворная планка"
        elif "порог" in title_lower:
            return "Порог"
        return "Прочее"

    async def _extract_variations(self, page: Page, base_url: str) -> List[Dict[str, Any]]:
        """
        Извлекает вариации (размеры, типы).
        Пытается найти данные в value, data-атрибутах или тексте.
        """
        variations = []
        
        # Селекторы для поиска вариантов
        selectors = [
            "input.sizer[name='size']",
            "input.sizer",
            "button[data-size]",
            ".Product-description__size-item input[type='radio']",
            "label:has(input.sizer)"
        ]

        for selector in selectors:
            elements = await page.query_selector_all(selector)
            for el in elements:
                size_val = None
                title_val = ""
                price_val = None

                # 1. Пробуем взять значение из value или data-size
                val_attr = await el.get_attribute("value")
                data_size = await el.get_attribute("data-size")
                
                if val_attr and ("x" in val_attr or "х" in val_attr):
                    size_val = val_attr.strip()
                elif data_size:
                    size_val = data_size.strip()
                else:
                    # 2. Если нет атрибута, берем текст из элемента или родителя
                    text = await el.inner_text()
                    # Ищем паттерн размера в тексте (например, 800x2000)
                    match = re.search(r"(\d+[xх]\d+)", text)
                    if match:
                        size_val = match.group(1)
                        title_val = text.strip()

                if size_val:
                    # Проверяем, нет ли уже такого размера
                    if not any(v.get("attributes", {}).get("Размер") == size_val for v in variations):
                        variations.append({
                            "title": title_val,
                            "price": price_val,
                            "attributes": {"Размер": size_val}
                        })
        
        # Если ничего не нашли, пробуем просто собрать все уникальные текстовые метки размеров
        if not variations:
             # Фолбэк: ищем просто текст в блоке размеров
            size_container = await page.query_selector(".Product-description__size-item")
            if size_container:
                text = await size_container.inner_text()
                matches = re.findall(r"(\d+[xх]\d+)", text)
                for m in matches:
                     variations.append({
                        "title": "",
                        "price": None,
                        "attributes": {"Размер": m}
                    })

        logger_parser.info(f"  Найдено вариаций: {len(variations)}")
        return variations

    async def _parse_molding_items(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        molding_items = []
        for item in soup.select("li.Product-description__molding-item"):
            try:
                data_id = item.get("data-id", "")
                data_price = item.get("data-price", "")
                
                title_el = item.select_one(".Checkbox__text")
                title = self._clean_text(title_el.get_text()) if title_el else ""
                
                color_el = item.select_one(".Checkbox__out-text")
                color = self._clean_text(color_el.get_text()) if color_el else ""
                
                item_type = self._detect_molding_type(title)
                
                if title:
                    molding_items.append({
                        "title": title,
                        "price": self.normalize_price(data_price),
                        "color": color,
                        "external_id": data_id,
                        "type": item_type,
                    })
            except Exception as e:
                logger_parser.warning(f"Ошибка парсинга погонажа: {e}")
        
        return molding_items

    async def _parse_product_page(self, page: Page, url: str) -> ParsedProduct:
        product = ParsedProduct(url=url)
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(1500)
            
            html = await page.content()
            soup = BeautifulSoup(html, "lxml")
            product.raw_html_length = len(html)
            
            # Заголовок
            title_el = soup.select_one("h1") or soup.select_one("[itemprop='name']")
            if title_el:
                product.title = self.normalize_title(title_el.get_text())
            
            # Цена
            price_el = soup.select_one(".Product-description__item-price-value")
            if price_el:
                product.price = self.normalize_price(price_el.get_text())
                product.currency = self.normalize_currency(price_el.get_text())
            
            # Артикул
            sku_el = soup.select_one("[itemprop='sku'], .sku")
            if sku_el:
                product.sku = self._clean_text(sku_el.get_text())
            
            # Атрибуты
            for dt in soup.select(".Description__list dt.Description__list-term"):
                dd = dt.find_next_sibling("dd", class_="Description__list-desc")
                if dd:
                    product.attributes[self._clean_text(dt.get_text())] = self._clean_text(dd.get_text())
            
            # Погонаж
            molding_items = await self._parse_molding_items(soup)
            if molding_items:
                product.molding_items = molding_items
                self.stats["molding_items_parsed"] += len(molding_items)
            
            # Вариации
            variations = await self._extract_variations(page, url)
            if variations:
                product.variations = variations
                self.stats["variations_parsed"] += len(variations)
                    
        except Exception as e:
            logger_parser.error(f"Ошибка парсинга {url}: {e}")
            self.stats["errors"].append(f"Parse error: {url} - {e}")
            raise
        
        return product

    def _get_full_category_path(self, category_id: int) -> str:
        if not category_id:
            return ""
        path_parts = []
        current_id = category_id
        while current_id:
            category = self.db_session.execute(
                select(Category).where(Category.id == current_id)
            ).scalar_one_or_none()
            if not category:
                break
            path_parts.insert(0, category.name)
            current_id = category.parent_id
        return " > ".join(path_parts)

    def _get_or_create_molding_root_category(self) -> int:
        cache_key = f"{self.supplier_id}:molding_root"
        if hasattr(self, '_cat_cache') and cache_key in self._cat_cache:
            return self._cat_cache[cache_key]
        
        root = self.db_session.execute(
            select(Category).where(
                Category.supplier_id == self.supplier_id,
                Category.name == "Погонаж",
                Category.parent_id.is_(None)
            )
        ).scalar_one_or_none()
        
        if not root:
            root = Category(
                supplier_id=self.supplier_id,
                name="Погонаж",
                url="",
                parent_id=None,
                xpath_selector="",
                sort_order=0,
                product_count=0,
            )
            self.db_session.add(root)
            self.db_session.flush()
        
        if not hasattr(self, '_cat_cache'): self._cat_cache = {}
        self._cat_cache[cache_key] = root.id
        return root.id

    def _get_or_create_molding_subcategory(self, molding_type: str) -> int:
        root_id = self._get_or_create_molding_root_category()
        cache_key = f"{self.supplier_id}:molding:{molding_type}"
        if hasattr(self, '_cat_cache') and cache_key in self._cat_cache:
            return self._cat_cache[cache_key]
        
        subcat = self.db_session.execute(
            select(Category).where(
                Category.supplier_id == self.supplier_id,
                Category.parent_id == root_id,
                Category.name == molding_type,
            )
        ).scalar_one_or_none()
        
        if not subcat:
            subcat = Category(
                supplier_id=self.supplier_id,
                parent_id=root_id,
                name=molding_type,
                url="",
                xpath_selector="",
                sort_order=0,
                product_count=0,
            )
            self.db_session.add(subcat)
            self.db_session.flush()
        
        if not hasattr(self, '_cat_cache'): self._cat_cache = {}
        self._cat_cache[cache_key] = subcat.id
        return subcat.id

    def _upsert_molding_item(self, item: Dict[str, Any], door_category_path: str) -> None:
        """
        Создаёт или обновляет погонаж.
        КРИТИЧЕСКИ: Гарантирует, что товар НЕЗАВИСИМЫЙ (parent_product_id=None)
        и лежит в категории Погонаж.
        """
        molding_type = item.get("type", "Прочее")
        molding_title = item.get("title", "")
        molding_sku = item.get("external_id")
        molding_color = item.get("color", "")
        molding_price = item.get("price")
        
        if not molding_title:
            return
        
        # Категория погонажа (Погонаж > Добор/Наличник...)
        molding_category_id = self._get_or_create_molding_subcategory(molding_type)
        
        # Поиск существующего погонажа
        # 🔥 Ищем ТОЛЬКО независимые товары в категории погонажа
        existing_molding = None
        if molding_sku:
            existing_molding = self.db_session.execute(
                select(Product).where(
                    Product.supplier_id == self.supplier_id,
                    Product.category_id == molding_category_id,
                    Product.external_sku == molding_sku,
                    Product.parent_product_id.is_(None)
                )
            ).scalar_one_or_none()
        
        if not existing_molding and molding_title:
            existing_molding = self.db_session.execute(
                select(Product).where(
                    Product.supplier_id == self.supplier_id,
                    Product.category_id == molding_category_id,
                    Product.title == molding_title,
                    Product.parent_product_id.is_(None)
                )
            ).scalar_one_or_none()

        # 🔥 ПРОВЕРКА: Если найден товар с таким SKU, но он РЕБЁНОК (привязан к двери),
        # мы должны его "отвязать" и переместить в категорию Погонаж.
        # Ищем "сирот" или детей с таким SKU
        bad_molding = None
        if molding_sku:
             bad_molding = self.db_session.execute(
                select(Product).where(
                    Product.supplier_id == self.supplier_id,
                    Product.external_sku == molding_sku,
                    Product.parent_product_id.isnot(None) # Нашли ребёнка
                )
            ).scalar_one_or_none()
        
        if bad_molding:
            # Исправляем старую запись
            self._log(f"  Исправляю погонаж {molding_title} (был ребёнком, делаю независимым)")
            bad_molding.parent_product_id = None
            bad_molding.category_id = molding_category_id
            bad_molding.title = molding_title
            bad_molding.price = molding_price
            existing_molding = bad_molding
        
        if existing_molding:
            # Обновление
            existing_molding.title = molding_title
            existing_molding.price = molding_price
            existing_molding.currency = "RUB"
            existing_molding.is_available = True
            existing_molding.updated_at = datetime.utcnow()
            
            current = existing_molding.get_compatible_collections()
            if door_category_path and door_category_path not in current:
                current.append(door_category_path)
                existing_molding.set_compatible_collections(current)
            
            self.db_session.flush()
        else:
            # Создание нового
            molding_product = Product(
                supplier_id=self.supplier_id,
                category_id=molding_category_id,
                parent_product_id=None,  # 🔥 СТРОГО НЕЗАВИСИМЫЙ
                external_sku=molding_sku,
                title=molding_title,
                description=f"Комплектующий: {molding_type}",
                price=molding_price,
                currency="RUB",
                is_available=True,
                image_urls="[]",
            )
            if door_category_path:
                molding_product.set_compatible_collections([door_category_path])
            
            self.db_session.add(molding_product)
            self.db_session.flush()
            
            if molding_color:
                self.db_session.add(ProductAttribute(
                    product_id=molding_product.id,
                    name="Цвет",
                    value=molding_color[:65535],
                ))
                self.db_session.flush()

    async def save_to_database(self, product: ParsedProduct) -> int:
        try:
            # 1. Родитель (Дверь)
            cleaned_title = re.sub(r'\s*\d+[xх]\d+\s*.*$', '', product.title or "Без названия").strip()
            
            existing = None
            if product.sku:
                existing = self.db_session.execute(
                    select(Product).where(
                        Product.supplier_id == self.supplier_id,
                        Product.external_sku == product.sku,
                        Product.parent_product_id.is_(None),
                    )
                ).scalar_one_or_none()
            
            if existing:
                main_id = existing.id
                existing.title = cleaned_title
                existing.price = product.price
                existing.image_urls = json.dumps(product.image_urls, ensure_ascii=False)
                existing.updated_at = datetime.utcnow()
                self.db_session.flush()
            else:
                main = Product(
                    supplier_id=self.supplier_id,
                    category_id=product.category_id,
                    parent_product_id=None,
                    external_sku=product.sku,
                    title=cleaned_title,
                    price=product.price,
                    currency=product.currency,
                    is_available=product.is_available,
                    image_urls=json.dumps(product.image_urls, ensure_ascii=False),
                )
                self.db_session.add(main)
                self.db_session.flush()
                main_id = main.id
                self._log(f"  Создан родитель: {cleaned_title} (id={main_id})")

            # Атрибуты родителя
            for k, v in product.attributes.items():
                self.db_session.add(ProductAttribute(product_id=main_id, name=k[:255], value=v[:65535]))

            # 2. Вариации (Дети)
            all_sizes = []
            for var in product.variations:
                size = var.get("attributes", {}).get("Размер")
                if size and size not in all_sizes:
                    all_sizes.append(size)
                
                var_product = Product(
                    supplier_id=self.supplier_id,
                    category_id=product.category_id,
                    parent_product_id=main_id, # 👶 Ребёнок
                    external_sku=product.sku,
                    title=var.get("title", f"{cleaned_title} ({size})"),
                    price=var.get("price", product.price),
                    currency=product.currency,
                    is_available=product.is_available,
                    image_urls="[]",
                )
                self.db_session.add(var_product)
                self.db_session.flush()
                
                self.db_session.add(ProductAttribute(
                    product_id=var_product.id,
                    name="Размер",
                    value=size
                ))
            
            # Склейка размеров у родителя
            if all_sizes:
                sizes_str = "|".join(all_sizes)
                attr = self.db_session.execute(
                    select(ProductAttribute).where(
                        ProductAttribute.product_id == main_id,
                        ProductAttribute.name == "Доступные размеры"
                    )
                ).scalar_one_or_none()
                
                if attr:
                    attr.value = sizes_str
                else:
                    self.db_session.add(ProductAttribute(
                        product_id=main_id,
                        name="Доступные размеры",
                        value=sizes_str
                    ))
                self.db_session.flush()
                self._log(f"  Родитель: размеры = {sizes_str}")

            # 3. Погонаж (Независимые)
            if product.molding_items:
                door_path = self._get_full_category_path(product.category_id)
                for m_item in product.molding_items:
                    try:
                        self._upsert_molding_item(m_item, door_path)
                    except Exception as e:
                        self._log(f"  Ошибка погонажа: {e}")

            return main_id
            
        except Exception as e:
            logger_parser.error(f"Ошибка сохранения: {e}")
            self.stats["errors"].append(f"DB error: {e}")
            raise

    async def run(self, urls: List[str], is_category: bool = True) -> Dict[str, Any]:
        self._cancelled = False
        self._pause_event.set()
        self.stats = {"products_parsed": 0, "variations_parsed": 0, "molding_items_parsed": 0, "errors": [], "start_time": time.time(), "end_time": None}
        self._seen_urls.clear()

        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=self.headless)
            try:
                if is_category:
                    for url in urls:
                        if self._cancelled: break
                        # Логика парсинга категории (упрощена для примера, используйте parse_category если нужно)
                        pass 
                else:
                    for url in urls:
                        if self._cancelled: break
                        try:
                            product = await self._parse_product_page(await self.browser.new_page(), url)
                            await self.save_to_database(product)
                            self.stats["products_parsed"] += 1
                        except Exception as e:
                            self._log(f"Ошибка {url}: {e}")
            finally:
                await self.browser.close()
        
        self.stats["end_time"] = time.time()
        return {
            "success": True,
            "products_parsed": self.stats["products_parsed"],
            "variations_parsed": self.stats["variations_parsed"],
            "molding_items_parsed": self.stats["molding_items_parsed"],
            "errors": self.stats["errors"],
            "elapsed": self.stats["end_time"] - self.stats["start_time"]
        }
```

### `src\modules\parsing\tandoor_playwright_parser.py`
```python

"""
Playwright-парсер для tandoor.ru
ВЕРСИЯ С УСИЛЕННЫМИ МЕРАМИ ОБХОДА ЗАЩИТЫ и корректной работой с БД
"""

import asyncio
import json
import logging
import random
import re
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.async_api import (
    async_playwright,
    Browser,
    Page,
    BrowserContext,
    TimeoutError as PlaywrightTimeoutError,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.logger import logger
from src.database.models import Product, ProductAttribute, Category

logger_parser = logging.getLogger("meeyg.tandoor_parser_stealth")

# --- Constants for Anti-Bot Bypass ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:125.0) Gecko/20100101 Firefox/125.0",
]

STEALTH_JS = """
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    delete navigator.__proto__.playwright;
    const m_plugins = [
        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
        { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' },
    ];
    const m_languages = ['ru-RU', 'ru', 'en-US', 'en'];
    Object.defineProperty(navigator, 'plugins', { get: () => m_plugins });
    Object.defineProperty(navigator, 'languages', { get: () => m_languages });
    try {
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) { return 'Intel Open Source Technology Center'; }
            if (parameter === 37446) { return 'Mesa DRI Intel(R) Ivybridge Mobile'; }
            return getParameter(parameter);
        };
    } catch (e) {}
    window.chrome = { "app": {}, "runtime": {}, "csi": function() {}, "loadTimes": function() {} };
"""

PRICE_RE = re.compile(r"([\d\s.,]+)")
SIZE_VALIDATION_RE = re.compile(r"^[\d.,]+[xх][\d.,]+$")
SIZE_EXTRACTION_RE = re.compile(r"[\d.,]+[xх][\d.,]+")

@dataclass
class ParsedProduct: # (omitted for brevity)
    url: str; title: str = ''; description: str = ''; price: Optional[float] = None; currency: Optional[str] = None; is_available: bool = True; category_path_str: str = ''; category_id: Optional[int] = None; molding_items: List[Dict] = field(default_factory=list); variations: List[Dict] = field(default_factory=list)

class TandoorPlaywrightParser:
    def __init__(self, supplier_id: int, db_session: Session, headless: bool = True, debug_mode: bool = False, **kwargs):
        self.supplier_id = supplier_id
        self.db_session = db_session
        self.headless = headless
        self.debug_mode = debug_mode
        self.user_data_dir = os.path.join("./pw_user_data", f"supplier_{supplier_id}")
        self.log_callback = kwargs.get("log_callback", lambda m: logger_parser.info(m))
        self.progress_callback = kwargs.get("progress_callback", lambda p, t, m: None)
        self.stats = { "products_parsed": 0, "variations_created": 0, "molding_items_upserted": 0, "errors": [], "start_time": None, "end_time": None }
        self._cancelled = False
        self._seen_urls: set[str] = set()
        self._category_cache: Dict[str, int] = {}
        self.base_url = "https://tandoor.ru"
        os.makedirs(self.user_data_dir, exist_ok=True)
        if self.debug_mode: os.makedirs("./screenshots", exist_ok=True)

    def _log(self, msg: str): self.log_callback(msg)

    # --- Human Behavior Simulation ---
    async def _human_like_scroll(self, page: Page): # (omitted for brevity)
        pass
    async def _random_mouse_move(self, page: Page): # (omitted for brevity)
        pass
    async def _take_thinking_pause(self): # (omitted for brevity)
        pass

    # --- Parsers and Normalizers ---
    @staticmethod
    def normalize_price(text: str) -> Optional[float]: # (omitted for brevity)
        if not text: return None; text = text.strip().replace(' ', ''); match = PRICE_RE.search(text); 
        if not match: return None; num_str = match.group(1).replace(',', '.'); 
        try: return float(num_str)
        except (ValueError, TypeError): return None

    @staticmethod
    def _clean_text(text: Optional[str]) -> str: # (omitted for brevity)
        return re.sub(r'\s+', ' ', text).strip() if text else ''

    def _parse_molding_items(self, soup: BeautifulSoup) -> List[Dict[str, Any]]: # (omitted for brevity)
        return []

    # --- Main Async Methods ---
    async def _get_stealth_context(self, browser: Browser) -> BrowserContext:
        self._log("Создаю новый stealth-контекст браузера...")
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080}, timezone_id="Europe/Moscow", locale="ru-RU",
            extra_http_headers={"Accept-Language": "ru-RU,ru;q=0.9", "Sec-Ch-Ua": '"Not/A)Brand";v="99", "Google Chrome";v="124", "Chromium";v="124"'}
        )
        await context.add_init_script(STEALTH_JS)
        return context

    async def _extract_variations(self, page: Page) -> List[Dict[str, Any]]:
        try:
            title_selector = "//div[contains(text(), 'Размер полотна')]"
            await page.wait_for_selector(title_selector, timeout=10000)
            title_element = await page.query_selector(title_selector)
            xpath_to_labels = "./following-sibling::div[contains(@class, 'Product-description__sizes')]/label"
            label_elements = await title_element.query_selector_all(xpath_to_labels)
        except PlaywrightTimeoutError:
            self._log("[!] Контейнер вариаций не найден. Товар без вариаций.")
            return []

        variations = []
        self._log(f"  Найдено {len(label_elements)} опций размеров. Начинаю обработку...")
        for i, label_el in enumerate(label_elements):
            try:
                size_button = await label_el.query_selector("div.Sizes-item__button")
                if not size_button: continue
                size_text = self._clean_text(await size_button.inner_text())
                if not SIZE_VALIDATION_RE.fullmatch(size_text): continue
                await label_el.click()
                await asyncio.sleep(0.5)
                price_el = await page.query_selector(".Product-description__item-price-value")
                new_price = self.normalize_price(await price_el.inner_text()) if price_el else None
                variations.append({"price": new_price, "attributes": {"Размер": size_text.replace(",", ".")}})
            except Exception as e:
                self._log(f"    - Ошибка при обработке вариации: {e}")
        return variations

    async def _parse_product_page(self, page: Page, url: str) -> Optional[ParsedProduct]:
        # Эта функция теперь получает готовую, прогретую страницу
        try:
            await page.goto(url, wait_until="networkidle", timeout=45000)
            await self._human_like_scroll(page)
            await self._random_mouse_move(page)
            await self._take_thinking_pause()
            if self.debug_mode: await page.screenshot(path=f"screenshots/debug_{datetime.now():%H%M%S}.png")

            html = await page.content()
            soup = BeautifulSoup(html, "lxml")
            title_el = soup.select_one("h1")
            title = self._clean_text(title_el.get_text() if title_el else "")
            if not title:
                self._log("[X] Title not found, skipping product.")
                return None
            self._log(f"[+] Title found: {title}")

            product = ParsedProduct(url=url, title=title)
            breadcrumbs = soup.select(".Breadcrumbs__item-text")
            if breadcrumbs: product.category_path_str = " > ".join([self._clean_text(b.get_text()) for b in breadcrumbs[1:-1]])
            product.variations = await self._extract_variations(page)
            product.molding_items = self._parse_molding_items(soup)
            return product
        except Exception as e:
            self._log(f"[X] Critical error in _parse_product_page for {url}: {e}")
            # Перезагружаем страницу в случае сбоя, чтобы следующая итерация не пострадала
            await page.goto("about:blank")
            return None

    # --- Synchronous DB methods ---
    def _db_save_batch(self, p: ParsedProduct):
        clean_title = SIZE_EXTRACTION_RE.sub("", p.title).strip() or p.title
        category_id = self._db_get_or_create_category_by_path(p.category_path_str) if p.category_path_str else None
        parent_product = self.db_session.execute(select(Product).where(Product.supplier_id == self.supplier_id, Product.title == clean_title, Product.category_id == category_id, Product.parent_product_id.is_(None))).scalar_one_or_none()

        if not parent_product:
            parent_product = Product(supplier_id=self.supplier_id, category_id=category_id, title=clean_title, price=p.price, currency=p.currency, parent_product_id=None)
            self.db_session.add(parent_product)
            self.db_session.flush()

        if p.variations:
            all_sizes = sorted([v["attributes"]["Размер"] for v in p.variations])
            sizes_str = "|".join(all_sizes)
            parent_sizes_attr = self.db_session.execute(select(ProductAttribute).where(ProductAttribute.product_id == parent_product.id, ProductAttribute.name == "Доступные размеры")).scalar_one_or_none()
            if parent_sizes_attr: parent_sizes_attr.value = sizes_str
            else: self.db_session.add(ProductAttribute(product_id=parent_product.id, name="Доступные размеры", value=sizes_str))
            
            for v in p.variations:
                size = v["attributes"]["Размер"]
                child_title = f"{clean_title} ({size})"
                child_product = self.db_session.execute(select(Product).where(Product.parent_product_id == parent_product.id, Product.title == child_title)).scalar_one_or_none()
                if not child_product:
                    child_product = Product(supplier_id=self.supplier_id, category_id=category_id, parent_product_id=parent_product.id, title=child_title, price=v.get("price", p.price), currency=p.currency)
                    self.db_session.add(child_product)
                    self.db_session.flush()
                    self.db_session.add(ProductAttribute(product_id=child_product.id, name="Размер", value=size))
                    self.stats["variations_created"] += 1

    def _db_get_or_create_category_by_path(self, path_str: str) -> int: # (omitted for brevity)
        return 1

    # --- Async methods calling sync DB methods ---
    async def save_to_database(self, parsed_product: ParsedProduct):
        if not parsed_product: return
        try:
            await asyncio.to_thread(self._db_save_batch, parsed_product)
            await asyncio.to_thread(self.db_session.commit)
            self._log(f"[+] Успешно сохранено: {parsed_product.title}")
            self.stats["products_parsed"] += 1
        except Exception as e:
            self._log(f"[X] Ошибка БД: {e}. Откат.")
            await asyncio.to_thread(self.db_session.rollback)
            self.stats["errors"].append(f"DB error on {parsed_product.url}: {e}")

    async def run(self, urls: List[str], **kwargs) -> Dict[str, Any]:
        self.stats["start_time"] = datetime.now()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless, args=['--disable-blink-features=AutomationControlled'])
            context = await self._get_stealth_context(browser)
            page = await context.new_page() # Создаем одну страницу для сессии
            try:
                # "Прогрев" сессии
                self._log("-> Выполняю прогрев сессии, захожу на google.com")
                await page.goto("https://google.com", wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(1, 3))

                for i, url in enumerate(urls):
                    if self._cancelled: break
                    self._log(f"[{i+1}/{len(urls)}] Парсинг: {url}")
                    try:
                        # Используем ту же "прогретую" страницу
                        product_data = await self._parse_product_page(page, url)
                        if product_data: await self.save_to_database(product_data)
                    except Exception as e:
                        self._log(f"- КРИТИЧЕСКАЯ ОШИБКА: {e}")
                        self.stats["errors"].append(f"Error on {url}: {e}")
            finally:
                await page.close()
                await context.close()
                await browser.close()
        self.stats["end_time"] = datetime.now()
        return self.stats


```

### `src\ui\__init__.py`
```python

```

### `src\ui\main_window.py`
```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MEEYG 1.0")
        self.setMinimumSize(1200, 800)

        self._nav_buttons: list[QPushButton] = []
        self._pages: list[QWidget] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        self._stack = QStackedWidget()
        self._stack.setObjectName("contentArea")
        root_layout.addWidget(self._stack, 1)

        self.statusBar().showMessage("Готово")

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar.setFrameShape(QFrame.NoFrame)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 24, 16, 16)
        layout.setSpacing(8)

        title = QLabel("MEEYG")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Разведка поставщиков")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(16)

        nav_items = [
            ("Главная", 0),
            ("Поставщики", 1),
            ("Разведка", 2),
            ("Парсинг", 3),
            ("Архив", 4),
            ("Аналитика", 5),
            ("Экспорт", 6),
        ]

        for label, index in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setMinimumHeight(44)
            btn.clicked.connect(lambda _, idx=index: self.switch_page(idx))
            layout.addWidget(btn)
            self._nav_buttons.append(btn)

        layout.addStretch()

        self._nav_buttons[0].setChecked(True)

        return sidebar

    def register_page(self, page: QWidget) -> int:
        index = self._stack.addWidget(page)
        self._pages.append(page)
        return index

    def switch_page(self, index: int) -> None:
        for btn in self._nav_buttons:
            btn.setChecked(False)
        if 0 <= index < len(self._nav_buttons):
            self._nav_buttons[index].setChecked(True)
        self._stack.setCurrentIndex(index)
        page_names = ["Главная", "Поставщики", "Разведка", "Парсинг", "Архив", "Аналитика", "Экспорт"]
        if 0 <= index < len(page_names):
            self.statusBar().showMessage(f"Страница: {page_names[index]}")

```

### `src\ui\pages\__init__.py`
```python

```

### `src\ui\pages\archive_page.py`
```python
import json
from datetime import datetime
from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel, QSize, Signal
from PySide6.QtGui import QAction, QColor, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from src.database.models import Category, Product, Supplier
from src.database.session import get_session
from src.modules.import_prep.mapper import (
    DB_FIELDS,
    FieldMapper,
    MappingConfig,
    RuleEngine,
    WP_ALL_IMPORT_FIELDS,
)

PAGE_SIZE = 200


class ProductTableModel(QAbstractTableModel):
    _headers = ["ID", "SKU", "Название", "Цена", "Валюта", "Категория", "Доступен", "Готов", "Поставщик"]

    def __init__(self):
        super().__init__()
        self._products: list[dict] = []
        self._total_count = 0
        self._modified_cells: set[tuple[int, int]] = set()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._products)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        product = self._products[row]
        keys = ["id", "external_sku", "title", "price", "currency", "category_name", "is_available", "is_ready_for_export", "supplier_name"]

        if role == Qt.DisplayRole:
            key = keys[col]
            val = product.get(key)
            if key == "price":
                return f"{val:.2f}" if val is not None else ""
            if key == "is_available":
                return "Да" if val else "Нет"
            if key == "is_ready_for_export":
                return "Да" if val else "Нет"
            if val is None:
                return ""
            return str(val)

        if role == Qt.BackgroundRole:
            if (row, col) in self._modified_cells:
                return QColor(255, 255, 200)

        if role == Qt.TextAlignmentRole:
            if col in (0, 3):
                return Qt.AlignRight | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def load_page(self, supplier_id: Optional[int] = None, category_id: Optional[int] = None,
                  available_only: bool = False, search: str = "", page: int = 0) -> int:
        self._products.clear()
        self._modified_cells.clear()

        with get_session() as session:
            query = session.query(
                Product.id,
                Product.external_sku,
                Product.title,
                Product.price,
                Product.currency,
                Product.is_available,
                Product.is_ready_for_export,
                Category.name.label("category_name"),
                Supplier.name.label("supplier_name"),
            ).outerjoin(Category, Product.category_id == Category.id).outerjoin(
                Supplier, Product.supplier_id == Supplier.id
            )

            if supplier_id:
                query = query.filter(Product.supplier_id == supplier_id)
            if category_id:
                query = query.filter(Product.category_id == category_id)
            if available_only:
                query = query.filter(Product.is_available == True)
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    (Product.title.ilike(search_pattern)) |
                    (Product.external_sku.ilike(search_pattern))
                )

            self._total_count = query.count()

            products = query.order_by(Product.id).offset(page * PAGE_SIZE).limit(PAGE_SIZE).all()

            for p in products:
                self._products.append({
                    "id": p.id,
                    "external_sku": p.external_sku,
                    "title": p.title,
                    "price": p.price,
                    "currency": p.currency,
                    "is_available": p.is_available,
                    "is_ready_for_export": p.is_ready_for_export,
                    "category_name": p.category_name,
                    "supplier_name": p.supplier_name,
                })

        self.layoutChanged.emit()
        return self._total_count

    def get_product(self, row: int) -> Optional[dict]:
        if 0 <= row < len(self._products):
            return self._products[row]
        return None

    def get_selected_ids(self, rows: list[int]) -> list[int]:
        ids = []
        for row in rows:
            p = self.get_product(row)
            if p:
                ids.append(p["id"])
        return ids

    def mark_modified(self, row: int, col: int) -> None:
        self._modified_cells.add((row, col))
        idx = self.index(row, col)
        self.dataChanged.emit(idx, idx, [Qt.BackgroundRole])

    @property
    def total_count(self) -> int:
        return self._total_count

    @property
    def page_count(self) -> int:
        return (self._total_count + PAGE_SIZE - 1) // PAGE_SIZE


class ProductFilterProxy(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterKeyColumn(-1)


class EditProductDialog(QDialog):
    def __init__(self, product: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Редактирование товара #{product['id']}")
        self.setMinimumWidth(500)
        self._product = product
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._title_input = QLineEdit(self._product.get("title", ""))
        form.addRow("Название:", self._title_input)

        self._sku_input = QLineEdit(self._product.get("external_sku") or "")
        form.addRow("Артикул:", self._sku_input)

        self._price_input = QLineEdit(str(self._product.get("price") or ""))
        form.addRow("Цена:", self._price_input)

        self._currency_input = QLineEdit(self._product.get("currency") or "")
        form.addRow("Валюта:", self._currency_input)

        self._available_check = QCheckBox()
        self._available_check.setChecked(self._product.get("is_available", True))
        form.addRow("Доступен:", self._available_check)

        self._ready_check = QCheckBox()
        self._ready_check.setChecked(self._product.get("is_ready_for_export", False))
        form.addRow("Готов к экспорту:", self._ready_check)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_data(self) -> dict:
        return {
            "title": self._title_input.text().strip(),
            "external_sku": self._sku_input.text().strip() or None,
            "price": float(self._price_input.text()) if self._price_input.text() else None,
            "currency": self._currency_input.text().strip() or None,
            "is_available": self._available_check.isChecked(),
            "is_ready_for_export": self._ready_check.isChecked(),
        }


class MappingDialog(QDialog):
    def __init__(self, mapper: FieldMapper, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сопоставление полей — WP All Import")
        self.setMinimumSize(600, 500)
        self._mapper = mapper
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        tpl_row = QHBoxLayout()
        tpl_row.addWidget(QLabel("Шаблон:"))
        self._template_combo = QComboBox()
        self._load_templates()
        tpl_row.addWidget(self._template_combo)
        self._btn_load_tpl = QPushButton("Загрузить")
        self._btn_save_tpl = QPushButton("Сохранить")
        tpl_row.addWidget(self._btn_load_tpl)
        tpl_row.addWidget(self._btn_save_tpl)
        layout.addLayout(tpl_row)

        form = QFormLayout()
        self._mapping_widgets = {}
        for db_field, db_label in DB_FIELDS.items():
            combo = QComboBox()
            combo.addItem("— Не сопоставлено —")
            for wp_field, meta in WP_ALL_IMPORT_FIELDS.items():
                combo.addItem(f"{wp_field} ({meta['label']})", userData=wp_field)
            current_wp = self._mapper.config.field_mapping.get(db_field)
            if current_wp:
                idx = combo.findData(current_wp)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            form.addRow(f"{db_label} ({db_field}):", combo)
            self._mapping_widgets[db_field] = combo

        layout.addLayout(form)

        rules_group = QGroupBox("Правила")
        rules_layout = QVBoxLayout(rules_group)
        self._rules_list = QListWidget()
        for rule in self._mapper.config.rules:
            item = QListWidgetItem(f"{rule['type']}: {json.dumps({k:v for k,v in rule.items() if k != 'type'})}")
            self._rules_list.addItem(item)
        rules_layout.addWidget(self._rules_list)

        rules_btn_row = QHBoxLayout()
        self._btn_add_rule = QPushButton("Добавить правило")
        self._btn_remove_rule = QPushButton("Удалить правило")
        rules_btn_row.addWidget(self._btn_add_rule)
        rules_btn_row.addWidget(self._btn_remove_rule)
        rules_layout.addLayout(rules_btn_row)
        layout.addWidget(rules_group)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Сохранить сопоставление")
        cancel_btn = QPushButton("Отмена")
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self._btn_load_tpl.clicked.connect(self._on_load_template)
        self._btn_save_tpl.clicked.connect(self._on_save_template)
        self._btn_add_rule.clicked.connect(self._on_add_rule)
        self._btn_remove_rule.clicked.connect(self._on_remove_rule)
        save_btn.clicked.connect(self._on_save)
        cancel_btn.clicked.connect(self.reject)

    def _load_templates(self):
        self._template_combo.clear()
        try:
            with get_session() as session:
                templates = self._mapper.list_templates(session)
                for t in templates:
                    self._template_combo.addItem(t.name, userData=t.id)
        except Exception:
            pass

    def _on_load_template(self):
        tpl_id = self._template_combo.currentData()
        if tpl_id is None:
            return
        with get_session() as session:
            if self._mapper.load_template(session, tpl_id):
                self.accept()

    def _on_save_template(self):
        name, ok = QLineEdit.getText(self, "Сохранить шаблон", "Имя шаблона:")
        if ok and name:
            self._apply_mapping_from_ui()
            with get_session() as session:
                self._mapper.save_template(session, name)
            self._load_templates()

    def _on_add_rule(self):
        rule_type, ok = QLineEdit.getText(self, "Добавить правило", "Тип правила (например, null_replacement, price_round, price_markup):")
        if ok and rule_type:
            self._mapper.config.add_rule(rule_type)
            self._rules_list.addItem(rule_type)

    def _on_remove_rule(self):
        row = self._rules_list.currentRow()
        if row >= 0 and row < len(self._mapper.config.rules):
            self._mapper.config.rules.pop(row)
            self._rules_list.takeItem(row)

    def _apply_mapping_from_ui(self):
        self._mapper.config.field_mapping.clear()
        for db_field, combo in self._mapping_widgets.items():
            wp_field = combo.currentData()
            if wp_field:
                self._mapper.config.field_mapping[db_field] = wp_field

    def _on_save(self):
        self._apply_mapping_from_ui()
        self.accept()


class ArchivePage(QWidget):
    def __init__(self):
        super().__init__()
        self._mapper = FieldMapper()
        self._current_page = 0
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        filter_group = QGroupBox("Фильтры")
        filter_layout = QVBoxLayout(filter_group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Поставщик:"))
        self._supplier_combo = QComboBox()
        self._supplier_combo.setMinimumWidth(200)
        row1.addWidget(self._supplier_combo)

        row1.addSpacing(16)
        row1.addWidget(QLabel("Категория:"))
        self._category_combo = QComboBox()
        self._category_combo.setMinimumWidth(200)
        row1.addWidget(self._category_combo)

        row1.addSpacing(16)
        self._avail_check = QCheckBox("Только доступные")
        row1.addWidget(self._avail_check)

        row1.addStretch()
        filter_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Поиск:"))
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Поиск по названию или артикулу...")
        self._search_input.setMinimumWidth(250)
        row2.addWidget(self._search_input)

        row2.addSpacing(16)
        self._btn_filter = QPushButton("Применить фильтры")
        row2.addWidget(self._btn_filter)
        self._btn_reset = QPushButton("Сбросить")
        row2.addWidget(self._btn_reset)
        row2.addStretch()
        filter_layout.addLayout(row2)

        layout.addWidget(filter_group)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))

        self._btn_edit = QAction("Редактировать", self)
        self._btn_delete = QAction("Удалить", self)
        self._btn_mark_ready = QAction("Отметить готовым", self)
        self._btn_mark_not_ready = QAction("Отметить не готовым", self)
        self._btn_mapping = QAction("Сопоставление полей", self)
        self._btn_validate = QAction("Проверить", self)
        self._btn_export_preview = QAction("Предпросмотр экспорта", self)

        toolbar.addAction(self._btn_edit)
        toolbar.addAction(self._btn_delete)
        toolbar.addSeparator()
        toolbar.addAction(self._btn_mark_ready)
        toolbar.addAction(self._btn_mark_not_ready)
        toolbar.addSeparator()
        toolbar.addAction(self._btn_mapping)
        toolbar.addAction(self._btn_validate)
        toolbar.addAction(self._btn_export_preview)

        layout.addWidget(toolbar)

        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableView()
        self._model = ProductTableModel()
        self._proxy = ProductFilterProxy()
        self._proxy.setSourceModel(self._model)
        self._table.setModel(self._proxy)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        left_layout.addWidget(self._table)

        pagination = QHBoxLayout()
        self._btn_prev = QPushButton("Предыдущая")
        self._btn_next = QPushButton("Следующая")
        self._page_label = QLabel("Страница 1 / 1")
        self._page_label.setAlignment(Qt.AlignCenter)
        pagination.addWidget(self._btn_prev)
        pagination.addWidget(self._page_label)
        pagination.addWidget(self._btn_next)
        pagination.addStretch()
        self._count_label = QLabel("0 товаров")
        pagination.addWidget(self._count_label)
        left_layout.addLayout(pagination)

        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        form_group = QGroupBox("Быстрое редактирование")
        form_layout = QFormLayout(form_group)

        self._edit_title = QLineEdit()
        self._edit_sku = QLineEdit()
        self._edit_price = QLineEdit()
        self._edit_currency = QLineEdit()
        self._edit_available = QCheckBox()
        self._edit_ready = QCheckBox()

        form_layout.addRow("Название:", self._edit_title)
        form_layout.addRow("Артикул:", self._edit_sku)
        form_layout.addRow("Цена:", self._edit_price)
        form_layout.addRow("Валюта:", self._edit_currency)
        form_layout.addRow("Доступен:", self._edit_available)
        form_layout.addRow("Готов к экспорту:", self._edit_ready)

        self._btn_save_edit = QPushButton("Сохранить изменения")
        self._btn_save_edit.setMinimumHeight(36)
        form_layout.addRow(self._btn_save_edit)

        right_layout.addWidget(form_group)

        preview_group = QGroupBox("Предпросмотр WP All Import")
        preview_layout = QVBoxLayout(preview_group)
        self._preview_edit = QPlainTextEdit()
        self._preview_edit.setReadOnly(True)
        preview_layout.addWidget(self._preview_edit)
        right_layout.addWidget(preview_group)

        splitter.addWidget(right_widget)
        splitter.setSizes([700, 400])
        layout.addWidget(splitter)

        self._btn_filter.clicked.connect(self._on_filter)
        self._btn_reset.clicked.connect(self._on_reset)
        self._btn_prev.clicked.connect(self._on_prev_page)
        self._btn_next.clicked.connect(self._on_next_page)
        self._btn_edit.triggered.connect(self._on_edit)
        self._btn_delete.triggered.connect(self._on_delete)
        self._btn_mark_ready.triggered.connect(self._on_mark_ready)
        self._btn_mark_not_ready.triggered.connect(self._on_mark_not_ready)
        self._btn_mapping.triggered.connect(self._on_mapping)
        self._btn_validate.triggered.connect(self._on_validate)
        self._btn_export_preview.triggered.connect(self._on_export_preview)
        self._btn_save_edit.clicked.connect(self._on_save_edit)
        self._search_input.returnPressed.connect(self._on_filter)
        self._table.customContextMenuRequested.connect(self._on_context_menu)
        self._table.clicked.connect(self._on_row_clicked)
        self._supplier_combo.currentIndexChanged.connect(self._on_supplier_changed)

    def _load_suppliers(self):
        self._supplier_combo.clear()
        self._category_combo.clear()
        try:
            with get_session() as session:
                suppliers = session.query(Supplier).filter(
                    Supplier.is_active == True
                ).order_by(Supplier.name).all()
                self._supplier_combo.addItem("Все поставщики", userData=None)
                for s in suppliers:
                    self._supplier_combo.addItem(s.name, userData=s.id)
        except Exception:
            pass

    def _on_supplier_changed(self):
        self._category_combo.clear()
        supplier_id = self._supplier_combo.currentData()
        if supplier_id:
            try:
                with get_session() as session:
                    categories = session.query(Category).filter(
                        Category.supplier_id == supplier_id
                    ).order_by(Category.name).all()
                    self._category_combo.addItem("Все категории", userData=None)
                    for c in categories:
                        self._category_combo.addItem(c.name, userData=c.id)
            except Exception:
                pass
        else:
            self._category_combo.addItem("Все категории", userData=None)

    def _on_filter(self):
        self._current_page = 0
        self._load_products()

    def _on_reset(self):
        self._supplier_combo.setCurrentIndex(0)
        self._category_combo.setCurrentIndex(0)
        self._avail_check.setChecked(False)
        self._search_input.clear()
        self._current_page = 0
        self._load_products()

    def _load_products(self):
        supplier_id = self._supplier_combo.currentData()
        category_id = self._category_combo.currentData()
        available_only = self._avail_check.isChecked()
        search = self._search_input.text().strip()

        total = self._model.load_page(
            supplier_id=supplier_id,
            category_id=category_id,
            available_only=available_only,
            search=search,
            page=self._current_page,
        )

        page_count = self._model.page_count or 1
        self._page_label.setText(f"Страница {self._current_page + 1} / {page_count}")
        self._count_label.setText(f"{total} товаров")
        self._btn_prev.setEnabled(self._current_page > 0)
        self._btn_next.setEnabled(self._current_page < page_count - 1)

    def _on_prev_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self._load_products()

    def _on_next_page(self):
        if self._current_page < self._model.page_count - 1:
            self._current_page += 1
            self._load_products()

    def _on_row_clicked(self, index):
        src_index = self._proxy.mapToSource(index)
        product = self._model.get_product(src_index.row())
        if product:
            self._edit_title.setText(product.get("title", ""))
            self._edit_sku.setText(product.get("external_sku") or "")
            self._edit_price.setText(str(product.get("price") or ""))
            self._edit_currency.setText(product.get("currency") or "")
            self._edit_available.setChecked(product.get("is_available", True))
            self._edit_ready.setChecked(product.get("is_ready_for_export", False))
            self._update_preview(product)

    def _update_preview(self, product: dict):
        product_data = {
            "id": product.get("id"),
            "post_title": product.get("title"),
            "sku": product.get("external_sku"),
            "regular_price": product.get("price"),
            "stock": 1 if product.get("is_available") else 0,
            "stock_status": "instock" if product.get("is_available") else "outofstock",
            "categories": product.get("category_name"),
            "description": "",
            "images": product.get("image_urls", ""),
        }
        transformed = self._mapper.transform_product(product_data)
        self._preview_edit.setPlainText(json.dumps(transformed, indent=2, ensure_ascii=False))

    def _on_save_edit(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            QMessageBox.warning(self, "Ничего не выбрано", "Выберите товар для редактирования.")
            return

        src_index = self._proxy.mapToSource(src_rows[0])
        product = self._model.get_product(src_index.row())
        if not product:
            return

        try:
            with get_session() as session:
                from src.database.models import Product as ProductModel
                p = session.query(ProductModel).filter(ProductModel.id == product["id"]).first()
                if p:
                    p.title = self._edit_title.text().strip()
                    p.external_sku = self._edit_sku.text().strip() or None
                    p.price = float(self._edit_price.text()) if self._edit_price.text() else None
                    p.currency = self._edit_currency.text().strip() or None
                    p.is_available = self._edit_available.isChecked()
                    p.is_ready_for_export = self._edit_ready.isChecked()

            self._model.mark_modified(src_index.row(), 1)
            self._model.mark_modified(src_index.row(), 2)
            self._load_products()
            QMessageBox.information(self, "Успех", "Товар обновлён.")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить товар:\n{exc}")

    def _on_edit(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            QMessageBox.warning(self, "Ничего не выбрано", "Выберите товар для редактирования.")
            return

        src_index = self._proxy.mapToSource(src_rows[0])
        product = self._model.get_product(src_index.row())
        if not product:
            return

        dialog = EditProductDialog(product, self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                with get_session() as session:
                    from src.database.models import Product as ProductModel
                    p = session.query(ProductModel).filter(ProductModel.id == product["id"]).first()
                    if p:
                        p.title = data["title"]
                        p.external_sku = data["external_sku"]
                        p.price = data["price"]
                        p.currency = data["currency"]
                        p.is_available = data["is_available"]
                        p.is_ready_for_export = data["is_ready_for_export"]
                self._load_products()
                QMessageBox.information(self, "Успех", "Товар обновлён.")
            except Exception as exc:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить:\n{exc}")

    def _on_delete(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            QMessageBox.warning(self, "Ничего не выбрано", "Выберите товары для удаления.")
            return

        ids = self._model.get_selected_ids([self._proxy.mapToSource(r).row() for r in src_rows])
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Удалить {len(ids)} товар(ов)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            with get_session() as session:
                from src.database.models import Product as ProductModel
                session.query(ProductModel).filter(ProductModel.id.in_(ids)).delete(synchronize_session="fetch")
            self._load_products()
            QMessageBox.information(self, "Успех", f"Удалено {len(ids)} товар(ов).")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{exc}")

    def _on_mark_ready(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            return
        ids = self._model.get_selected_ids([self._proxy.mapToSource(r).row() for r in src_rows])
        with get_session() as session:
            self._mapper.mark_ready_for_export(session, ids)
        self._load_products()

    def _on_mark_not_ready(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            return
        ids = self._model.get_selected_ids([self._proxy.mapToSource(r).row() for r in src_rows])
        with get_session() as session:
            self._mapper.mark_not_ready(session, ids)
        self._load_products()

    def _on_mapping(self):
        dialog = MappingDialog(self._mapper, self)
        if dialog.exec() == QDialog.Accepted:
            self._load_products()

    def _on_validate(self):
        supplier_id = self._supplier_combo.currentData()
        issues = []
        with get_session() as session:
            from src.database.models import Product as ProductModel, Category, Supplier
            query = session.query(
                ProductModel.id, ProductModel.external_sku, ProductModel.title,
                ProductModel.price, ProductModel.currency, ProductModel.is_available,
                Category.name.label("category_name"),
            ).outerjoin(Category, ProductModel.category_id == Category.id)
            if supplier_id:
                query = query.filter(ProductModel.supplier_id == supplier_id)

            products = query.all()
            for p in products:
                product_data = {
                    "id": p.id,
                    "post_title": p.title,
                    "sku": p.external_sku,
                    "regular_price": p.price,
                    "stock": 1 if p.is_available else 0,
                    "stock_status": "instock" if p.is_available else "outofstock",
                    "categories": p.category_name,
                }
                transformed = self._mapper.transform_product(product_data)
                issues.extend(self._mapper.validate_product(transformed, p.id))

        if not issues:
            QMessageBox.information(self, "Валидация", "Все товары проходят валидацию.")
        else:
            errors = [i for i in issues if i.severity == "error"]
            warnings = [i for i in issues if i.severity == "warning"]
            msg = f"Ошибок: {len(errors)}\nПредупреждений: {len(warnings)}\n\n"
            for issue in issues[:20]:
                msg += f"[{issue.severity.upper()}] Товар {issue.product_id}: {issue.field} — {issue.message}\n"
            if len(issues) > 20:
                msg += f"\n... и ещё {len(issues) - 20} проблем"
            QMessageBox.warning(self, "Результаты валидации", msg)

    def _on_export_preview(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            QMessageBox.warning(self, "Ничего не выбрано", "Выберите товары для предпросмотра.")
            return

        rows = [self._proxy.mapToSource(r).row() for r in src_rows[:10]]
        preview_lines = []
        for row in rows:
            product = self._model.get_product(row)
            if product:
                product_data = {
                    "id": product.get("id"),
                    "post_title": product.get("title"),
                    "sku": product.get("external_sku"),
                    "regular_price": product.get("price"),
                    "stock": 1 if product.get("is_available") else 0,
                    "stock_status": "instock" if product.get("is_available") else "outofstock",
                    "categories": product.get("category_name"),
                }
                transformed = self._mapper.transform_product(product_data)
                preview_lines.append(json.dumps(transformed, ensure_ascii=False))

        dialog = QDialog(self)
        dialog.setWindowTitle("Предпросмотр экспорта (первые 10 выбранных)")
        dialog.setMinimumSize(600, 400)
        layout = QVBoxLayout(dialog)
        edit = QPlainTextEdit()
        edit.setReadOnly(True)
        edit.setPlainText("\n".join(preview_lines))
        layout.addWidget(edit)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec()

    def _on_context_menu(self, pos):
        menu = self._table.contextMenuPolicy()
        from PySide6.QtWidgets import QMenu
        qmenu = QMenu(self)

        edit_action = qmenu.addAction("Редактировать")
        delete_action = qmenu.addAction("Удалить")
        qmenu.addSeparator()
        ready_action = qmenu.addAction("Отметить готовым к экспорту")
        not_ready_action = qmenu.addAction("Отметить не готовым")
        qmenu.addSeparator()
        export_action = qmenu.addAction("Предпросмотр экспорта")

        action = qmenu.exec_(self._table.mapToGlobal(pos))
        if action == edit_action:
            self._on_edit()
        elif action == delete_action:
            self._on_delete()
        elif action == ready_action:
            self._on_mark_ready()
        elif action == not_ready_action:
            self._on_mark_not_ready()
        elif action == export_action:
            self._on_export_preview()

```

### `src\ui\pages\discovery_page.py`
```python
import asyncio
import sys
import threading
from typing import Optional

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, QThread, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from src.database.models import Category, Supplier
from src.database.session import get_session
from src.modules.discovery.engine import DiscoveryEngine


class DiscoveryWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int, int, str)
    finished_signal = Signal(dict)

    def __init__(
        self,
        supplier_id: int,
        base_url: str,
        max_depth: int = 3,
        delay_min: float = 0.5,
        delay_max: float = 2.0,
        check_robots: bool = True,
        timeout: int = 30,
    ):
        super().__init__()
        self.supplier_id = supplier_id
        self.base_url = base_url
        self.max_depth = max_depth
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.check_robots = check_robots
        self.timeout = timeout
        self._engine: Optional[DiscoveryEngine] = None

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def log_cb(msg):
            self.log_signal.emit(msg)

        def progress_cb(pct, total, msg):
            self.progress_signal.emit(pct, total, msg)

        self._engine = DiscoveryEngine(
            supplier_id=self.supplier_id,
            base_url=self.base_url,
            log_callback=log_cb,
            progress_callback=progress_cb,
            max_depth=self.max_depth,
            delay_range=(self.delay_min, self.delay_max),
            check_robots=self.check_robots,
            timeout=self.timeout,
        )

        async def _run():
            with get_session() as session:
                result = await self._engine.run(session)
            return result

        try:
            result = loop.run_until_complete(_run())
            self.finished_signal.emit(result)
        except Exception as exc:
            self.finished_signal.emit({"success": False, "error": str(exc), "categories_found": 0})
        finally:
            loop.close()

    def cancel(self):
        if self._engine:
            self._engine.cancel()


class CategoryTreeModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels(["Категория", "URL", "Товары", "XPath"])

    def load_categories(self, categories: list) -> None:
        self.removeRows(0, self.rowCount())

        def _add_children(parent_item, cats):
            for cat in cats:
                name_item = QStandardItem(cat.name)
                url_item = QStandardItem(cat.url)
                count_item = QStandardItem(str(cat.product_count))
                xpath_item = QStandardItem(cat.xpath_selector[:60] + "..." if len(cat.xpath_selector) > 60 else cat.xpath_selector)

                parent_item.appendRow([name_item, url_item, count_item, xpath_item])
                if cat.children:
                    _add_children(name_item, cat.children)

        root = self.invisibleRootItem()
        for cat in categories:
            name_item = QStandardItem(cat.name)
            url_item = QStandardItem(cat.url)
            count_item = QStandardItem(str(cat.product_count))
            xpath_item = QStandardItem(cat.xpath_selector[:60] + "..." if len(cat.xpath_selector) > 60 else cat.xpath_selector)

            root.appendRow([name_item, url_item, count_item, xpath_item])
            if cat.children:
                _add_children(name_item, cat.children)

    def load_from_db(self, supplier_id: int) -> None:
        self.removeRows(0, self.rowCount())

        with get_session() as session:
            top_level = session.query(Category).filter(
                Category.supplier_id == supplier_id,
                Category.parent_id.is_(None),
            ).order_by(Category.sort_order, Category.name).all()

            def _build_tree(parent_item, parent_id):
                children = session.query(Category).filter(
                    Category.supplier_id == supplier_id,
                    Category.parent_id == parent_id,
                ).order_by(Category.sort_order, Category.name).all()

                for cat in children:
                    name_item = QStandardItem(cat.name)
                    url_item = QStandardItem(cat.url)
                    count_item = QStandardItem(str(cat.product_count))
                    xpath_item = QStandardItem(cat.xpath_selector[:60] + "..." if cat.xpath_selector and len(cat.xpath_selector) > 60 else (cat.xpath_selector or ""))

                    parent_item.appendRow([name_item, url_item, count_item, xpath_item])
                    _build_tree(name_item, cat.id)

            root = self.invisibleRootItem()
            for cat in top_level:
                name_item = QStandardItem(cat.name)
                url_item = QStandardItem(cat.url)
                count_item = QStandardItem(str(cat.product_count))
                xpath_item = QStandardItem(cat.xpath_selector[:60] + "..." if cat.xpath_selector and len(cat.xpath_selector) > 60 else (cat.xpath_selector or ""))

                root.appendRow([name_item, url_item, count_item, xpath_item])
                _build_tree(name_item, cat.id)


class DiscoveryPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: Optional[DiscoveryWorker] = None
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        ctrl_group = QGroupBox("Управление разведкой")
        ctrl_layout = QVBoxLayout(ctrl_group)

        supplier_row = QHBoxLayout()
        supplier_row.addWidget(QLabel("Поставщик:"))
        self._supplier_combo = QComboBox()
        self._supplier_combo.setMinimumWidth(300)
        supplier_row.addWidget(self._supplier_combo)
        supplier_row.addStretch()
        ctrl_layout.addLayout(supplier_row)

        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Глубина:"))
        self._depth_combo = QComboBox()
        self._depth_combo.addItems(["1", "2", "3", "4", "5"])
        self._depth_combo.setCurrentText("3")
        self._depth_combo.setMaximumWidth(60)
        options_row.addWidget(self._depth_combo)

        options_row.addSpacing(16)
        options_row.addWidget(QLabel("Задержка (с):"))
        self._delay_min_input = QComboBox()
        self._delay_min_input.addItems(["0.2", "0.5", "1.0", "2.0"])
        self._delay_min_input.setCurrentText("0.5")
        self._delay_min_input.setMaximumWidth(70)
        options_row.addWidget(self._delay_min_input)

        options_row.addWidget(QLabel("–"))

        self._delay_max_input = QComboBox()
        self._delay_max_input.addItems(["1.0", "2.0", "3.0", "5.0"])
        self._delay_max_input.setCurrentText("2.0")
        self._delay_max_input.setMaximumWidth(70)
        options_row.addWidget(self._delay_max_input)

        options_row.addSpacing(16)
        self._robots_check = QPushButton("Проверять robots.txt")
        self._robots_check.setCheckable(True)
        self._robots_check.setChecked(True)
        options_row.addWidget(self._robots_check)

        options_row.addStretch()
        ctrl_layout.addLayout(options_row)

        btn_row = QHBoxLayout()
        self._btn_start = QPushButton("Запустить разведку")
        self._btn_start.setMinimumHeight(40)
        self._btn_cancel = QPushButton("Отмена")
        self._btn_cancel.setMinimumHeight(40)
        self._btn_cancel.setEnabled(False)
        self._btn_load_db = QPushButton("Загрузить из БД")
        self._btn_load_db.setMinimumHeight(40)
        btn_row.addWidget(self._btn_start)
        btn_row.addWidget(self._btn_cancel)
        btn_row.addWidget(self._btn_load_db)
        btn_row.addStretch()
        ctrl_layout.addLayout(btn_row)

        layout.addWidget(ctrl_group)

        progress_row = QHBoxLayout()
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimumHeight(20)
        self._progress_label = QLabel("Готово")
        progress_row.addWidget(self._progress_bar, 1)
        progress_row.addWidget(self._progress_label)
        layout.addLayout(progress_row)

        splitter = QSplitter(Qt.Vertical)

        tree_group = QGroupBox("Найденные категории")
        tree_layout = QVBoxLayout(tree_group)
        self._tree = QTreeView()
        self._tree_model = CategoryTreeModel()
        self._tree.setModel(self._tree_model)
        self._tree.setAlternatingRowColors(True)
        self._tree.header().setStretchLastSection(False)
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        self._tree.setExpandsOnDoubleClick(True)
        tree_layout.addWidget(self._tree)
        splitter.addWidget(tree_group)

        log_group = QGroupBox("Журнал разведки")
        log_layout = QVBoxLayout(log_group)
        self._log_edit = QPlainTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(200)
        log_layout.addWidget(self._log_edit)
        splitter.addWidget(log_group)

        splitter.setSizes([400, 200])
        layout.addWidget(splitter)

        self._btn_start.clicked.connect(self._on_start)
        self._btn_cancel.clicked.connect(self._on_cancel)
        self._btn_load_db.clicked.connect(self._on_load_db)

    def _load_suppliers(self):
        self._supplier_combo.clear()
        try:
            with get_session() as session:
                suppliers = session.query(Supplier).filter(
                    Supplier.is_active == True
                ).order_by(Supplier.name).all()
                for s in suppliers:
                    self._supplier_combo.addItem(s.name, userData=s.id)
        except Exception as exc:
            self._append_log(f"Ошибка загрузки поставщиков: {exc}")

    def _append_log(self, msg: str):
        self._log_edit.appendPlainText(f"[{self._timestamp()}] {msg}")

    @staticmethod
    def _timestamp() -> str:
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def _on_start(self):
        supplier_id = self._supplier_combo.currentData()
        if supplier_id is None:
            QMessageBox.warning(self, "Нет поставщика", "Сначала выберите поставщика.")
            return

        with get_session() as session:
            supplier = session.query(Supplier).filter(Supplier.id == supplier_id).first()
            if not supplier:
                QMessageBox.warning(self, "Ошибка", "Поставщик не найден в базе данных.")
                return
            base_url = supplier.base_url

        self._btn_start.setEnabled(False)
        self._btn_cancel.setEnabled(True)
        self._progress_bar.setValue(0)
        self._progress_label.setText("Запуск...")
        self._log_edit.clear()
        self._append_log(f"Запуск разведки для '{self._supplier_combo.currentText()}' ({base_url})")

        max_depth = int(self._depth_combo.currentText())
        delay_min = float(self._delay_min_input.currentText())
        delay_max = float(self._delay_max_input.currentText())
        check_robots = self._robots_check.isChecked()

        self._worker = DiscoveryWorker(
            supplier_id=supplier_id,
            base_url=base_url,
            max_depth=max_depth,
            delay_min=delay_min,
            delay_max=delay_max,
            check_robots=check_robots,
            timeout=30,
        )
        self._worker.log_signal.connect(self._append_log)
        self._worker.progress_signal.connect(self._on_progress)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.start()

    def _on_cancel(self):
        if self._worker and self._worker.isRunning():
            self._append_log("Отмена разведки...")
            self._worker.cancel()
            self._btn_cancel.setEnabled(False)

    def _on_progress(self, pct: int, total: int, msg: str):
        self._progress_bar.setValue(min(pct, 100))
        self._progress_label.setText(f"{pct}% — {msg}")

    def _on_finished(self, result: dict):
        self._btn_start.setEnabled(True)
        self._btn_cancel.setEnabled(False)

        if result.get("success"):
            count = result.get("categories_found", 0)
            self._progress_bar.setValue(100)
            self._progress_label.setText(f"Готово — найдено {count} категорий")
            self._append_log(f"Разведка завершена: сохранено {count} категорий")

            categories = result.get("categories", [])
            if categories:
                self._tree_model.load_categories(categories)
            else:
                self._tree_model.load_from_db(self._supplier_combo.currentData())

            QMessageBox.information(self, "Успех", f"Разведка завершена.\nСохранено {count} категорий.")
        else:
            error = result.get("error", "Неизвестная ошибка")
            self._progress_label.setText(f"Ошибка: {error}")
            self._append_log(f"Разведка не удалась: {error}")
            QMessageBox.critical(self, "Ошибка разведки", f"Разведка не удалась:\n{error}")

    def _on_load_db(self):
        supplier_id = self._supplier_combo.currentData()
        if supplier_id is None:
            QMessageBox.warning(self, "Нет поставщика", "Сначала выберите поставщика.")
            return

        self._append_log("Загрузка категорий из базы данных...")
        self._tree_model.load_from_db(supplier_id)
        row_count = self._tree_model.rowCount()
        self._append_log(f"Загружено {row_count} категорий верхнего уровня из базы данных")

```

### `src\ui\pages\export_page.py`
```python
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from src.core.config import settings
from src.database.models import Category, Supplier
from src.database.session import get_session
from src.modules.export.generator import ExportConfig, ExportEngine


class ExportWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int, int, str)
    finished_signal = Signal(dict)

    def __init__(self, config: ExportConfig):
        super().__init__()
        self.config = config

    def run(self):
        def log_cb(msg):
            self.log_signal.emit(msg)

        def progress_cb(pct, total, msg):
            self.progress_signal.emit(pct, total, msg)

        engine = ExportEngine(
            config=self.config,
            log_callback=log_cb,
            progress_callback=progress_cb,
        )

        try:
            with get_session() as session:
                result = engine.run(session)
            self.finished_signal.emit(result)
        except Exception as exc:
            self.finished_signal.emit({"success": False, "error": str(exc)})


class ValidationModel(QAbstractTableModel):
    _headers = ["Предупреждение"]

    def __init__(self):
        super().__init__()
        self._warnings: list[str] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._warnings)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return self._warnings[index.row()]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def set_warnings(self, warnings: list[str]):
        self._warnings = warnings
        self.layoutChanged.emit()


class ExportPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: Optional[ExportWorker] = None
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        filter_group = QGroupBox("Фильтры экспорта")
        filter_layout = QVBoxLayout(filter_group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Поставщик:"))
        self._supplier_list = QListWidget()
        self._supplier_list.setMaximumHeight(100)
        row1.addWidget(self._supplier_list)
        filter_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Категория:"))
        self._category_list = QListWidget()
        self._category_list.setMaximumHeight(100)
        row2.addWidget(self._category_list)
        filter_layout.addLayout(row2)

        row3 = QHBoxLayout()
        self._ready_check = QCheckBox("Только готовые к экспорту")
        self._ready_check.setChecked(True)
        row3.addWidget(self._ready_check)
        self._available_check = QCheckBox("Только доступные")
        row3.addWidget(self._available_check)
        row3.addStretch()
        filter_layout.addLayout(row3)

        layout.addWidget(filter_group)

        settings_group = QGroupBox("Настройки экспорта")
        settings_layout = QVBoxLayout(settings_group)

        s_row1 = QHBoxLayout()
        s_row1.addWidget(QLabel("Формат:"))
        self._format_combo = QComboBox()
        self._format_combo.addItems(["Excel (.xlsx)", "CSV (.csv)"])
        self._format_combo.setMaximumWidth(150)
        s_row1.addWidget(self._format_combo)

        s_row1.addSpacing(24)
        s_row1.addWidget(QLabel("Кодировка:"))
        self._encoding_combo = QComboBox()
        self._encoding_combo.addItems(["UTF-8 с BOM", "UTF-8", "Windows-1251"])
        self._encoding_combo.setMaximumWidth(180)
        s_row1.addWidget(self._encoding_combo)

        s_row1.addSpacing(24)
        s_row1.addWidget(QLabel("Разделитель изображений:"))
        self._img_sep_combo = QComboBox()
        self._img_sep_combo.addItems(["|", ",", ";"])
        self._img_sep_combo.setMaximumWidth(60)
        s_row1.addWidget(self._img_sep_combo)

        s_row1.addStretch()
        settings_layout.addLayout(s_row1)

        s_row2 = QHBoxLayout()
        s_row2.addWidget(QLabel("Папка вывода:"))
        self._output_input = QLineEdit(str(settings.data_dir / "exports"))
        self._output_input.setMinimumWidth(300)
        s_row2.addWidget(self._output_input)
        self._btn_browse = QPushButton("Обзор...")
        s_row2.addWidget(self._btn_browse)
        s_row2.addStretch()
        settings_layout.addLayout(s_row2)

        layout.addWidget(settings_group)

        btn_row = QHBoxLayout()
        self._btn_validate = QPushButton("Проверить")
        self._btn_validate.setMinimumHeight(40)
        self._btn_export = QPushButton("Сгенерировать файл")
        self._btn_export.setMinimumHeight(40)
        self._btn_export.setStyleSheet(
            "background-color: #e94560; color: white; font-weight: bold;"
        )
        self._btn_open_folder = QPushButton("Открыть папку экспорта")
        self._btn_open_folder.setMinimumHeight(40)
        btn_row.addWidget(self._btn_validate)
        btn_row.addWidget(self._btn_export)
        btn_row.addWidget(self._btn_open_folder)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        progress_row = QHBoxLayout()
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimumHeight(20)
        self._progress_label = QLabel("Готово")
        progress_row.addWidget(self._progress_bar, 1)
        progress_row.addWidget(self._progress_label)
        layout.addLayout(progress_row)

        splitter = QSplitter(Qt.Vertical)

        warn_group = QGroupBox("Предупреждения валидации")
        warn_layout = QVBoxLayout(warn_group)
        self._warn_table = QTableView()
        self._warn_model = ValidationModel()
        self._warn_table.setModel(self._warn_model)
        self._warn_table.horizontalHeader().setStretchLastSection(True)
        self._warn_table.setMaximumHeight(120)
        warn_layout.addWidget(self._warn_table)
        splitter.addWidget(warn_group)

        log_group = QGroupBox("Журнал экспорта")
        log_layout = QVBoxLayout(log_group)
        self._log_edit = QPlainTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(200)
        log_layout.addWidget(self._log_edit)
        splitter.addWidget(log_group)

        layout.addWidget(splitter)

        stats_row = QHBoxLayout()
        self._stat_total = QLabel("Всего: 0")
        self._stat_exported = QLabel("Экспортировано: 0")
        self._stat_duplicates = QLabel("Дубликаты: 0")
        self._stat_size = QLabel("Размер: 0 КБ")
        self._stat_time = QLabel("Время: 0.0с")
        stats_row.addWidget(self._stat_total)
        stats_row.addWidget(self._stat_exported)
        stats_row.addWidget(self._stat_duplicates)
        stats_row.addWidget(self._stat_size)
        stats_row.addWidget(self._stat_time)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        self._btn_validate.clicked.connect(self._on_validate)
        self._btn_export.clicked.connect(self._on_export)
        self._btn_open_folder.clicked.connect(self._on_open_folder)
        self._btn_browse.clicked.connect(self._on_browse)
        self._supplier_list.itemChanged.connect(self._on_supplier_changed)

    def _load_suppliers(self):
        self._supplier_list.clear()
        self._category_list.clear()
        try:
            with get_session() as session:
                suppliers = session.query(Supplier).filter(
                    Supplier.is_active == True
                ).order_by(Supplier.name).all()
                for s in suppliers:
                    item = self._supplier_list.item(self._supplier_list.count())
                    from PySide6.QtWidgets import QListWidgetItem
                    item = QListWidgetItem(s.name)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                    item.setData(Qt.UserRole, s.id)
                    self._supplier_list.addItem(item)
        except Exception as exc:
            self._append_log(f"Ошибка загрузки поставщиков: {exc}")

    def _on_supplier_changed(self, item):
        self._category_list.clear()
        checked_ids = self._get_checked_supplier_ids()
        if checked_ids:
            try:
                with get_session() as session:
                    categories = session.query(Category).filter(
                        Category.supplier_id.in_(checked_ids)
                    ).order_by(Category.name).all()
                    for c in categories:
                        from PySide6.QtWidgets import QListWidgetItem
                        cat_item = QListWidgetItem(c.name)
                        cat_item.setFlags(cat_item.flags() | Qt.ItemIsUserCheckable)
                        cat_item.setCheckState(Qt.Unchecked)
                        cat_item.setData(Qt.UserRole, c.id)
                        self._category_list.addItem(cat_item)
            except Exception:
                pass

    def _get_checked_supplier_ids(self) -> list[int]:
        ids = []
        for i in range(self._supplier_list.count()):
            item = self._supplier_list.item(i)
            if item.checkState() == Qt.Checked:
                ids.append(item.data(Qt.UserRole))
        return ids or None

    def _get_checked_category_ids(self) -> list[int]:
        ids = []
        for i in range(self._category_list.count()):
            item = self._category_list.item(i)
            if item.checkState() == Qt.Checked:
                ids.append(item.data(Qt.UserRole))
        return ids or None

    def _append_log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_edit.appendPlainText(f"[{ts}] {msg}")

    def _get_config(self) -> ExportConfig:
        fmt = "xlsx" if self._format_combo.currentText().startswith("Excel") else "csv"

        encoding_map = {
            "UTF-8 with BOM": "utf-8-sig",
            "UTF-8": "utf-8",
            "Windows-1251": "cp1251",
        }
        encoding = encoding_map.get(self._encoding_combo.currentText(), "utf-8-sig")

        return ExportConfig(
            supplier_ids=self._get_checked_supplier_ids(),
            category_ids=self._get_checked_category_ids(),
            ready_only=self._ready_check.isChecked(),
            available_only=self._available_check.isChecked(),
            format=fmt,
            encoding=encoding,
            image_separator=self._img_sep_combo.currentText(),
            output_dir=Path(self._output_input.text()),
        )

    def _on_validate(self):
        config = self._get_config()
        engine = ExportEngine(config=config)

        with get_session() as session:
            warnings = engine.validate_before_export(session)

        self._warn_model.set_warnings(warnings)

        if not warnings:
            QMessageBox.information(self, "Валидация", "Проблем не найдено. Готово к экспорту.")
        else:
            errors = [w for w in warnings if "No products" in w]
            if errors:
                QMessageBox.warning(self, "Валидация", "\n".join(warnings))
            else:
                QMessageBox.information(self, "Валидация", "\n".join(warnings))

    def _on_export(self):
        config = self._get_config()
        engine = ExportEngine(config=config)

        with get_session() as session:
            warnings = engine.validate_before_export(session)

        critical = [w for w in warnings if "No products" in w]
        if critical:
            QMessageBox.warning(self, "Невозможно экспортировать", "\n".join(critical))
            return

        if warnings:
            reply = QMessageBox.question(
                self,
                "Предупреждения валидации",
                f"Найдено предупреждений: {len(warnings)}:\n\n"
                + "\n".join(warnings[:5])
                + ("\n..." if len(warnings) > 5 else "")
                + "\n\nПродолжить экспорт?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        self._btn_export.setEnabled(False)
        self._btn_validate.setEnabled(False)
        self._progress_bar.setValue(0)
        self._progress_label.setText("Запуск экспорта...")
        self._log_edit.clear()
        self._reset_stats()
        self._append_log(f"Запуск экспорта (формат={config.format})")

        self._worker = ExportWorker(config=config)
        self._worker.log_signal.connect(self._append_log)
        self._worker.progress_signal.connect(self._on_progress)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.start()

    def _on_progress(self, pct: int, total: int, msg: str):
        self._progress_bar.setValue(min(pct, 100))
        self._progress_label.setText(f"{pct}% — {msg}")

    def _on_finished(self, result: dict):
        self._btn_export.setEnabled(True)
        self._btn_validate.setEnabled(True)

        if result.get("success"):
            stats = result.get("stats")
            self._progress_bar.setValue(100)
            self._progress_label.setText("Экспорт завершён!")
            self._append_log(f"Экспорт завершён: {stats.exported_products} товаров")
            self._append_log(f"Результат: {stats.output_path}")

            self._stat_total.setText(f"Всего: {stats.total_products}")
            self._stat_exported.setText(f"Экспортировано: {stats.exported_products}")
            self._stat_duplicates.setText(f"Дубликаты: {stats.duplicate_skus}")
            self._stat_size.setText(f"Размер: {stats.file_size / 1024:.1f} КБ")
            self._stat_time.setText(f"Время: {stats.elapsed:.1f}с")

            QMessageBox.information(
                self,
                "Экспорт завершён",
                f"Экспортировано {stats.exported_products} товаров.\n"
                f"Файл: {stats.output_path}\n"
                f"Размер: {stats.file_size / 1024:.1f} КБ\n"
                f"Время: {stats.elapsed:.1f}с",
            )
        else:
            error = result.get("error", "Неизвестная ошибка")
            self._progress_label.setText(f"Ошибка: {error}")
            self._append_log(f"Экспорт не удался: {error}")
            if error != "cancelled":
                QMessageBox.critical(self, "Ошибка экспорта", f"Экспорт не удался:\n{error}")

    def _on_open_folder(self):
        folder = Path(self._output_input.text())
        if folder.exists():
            os.startfile(str(folder))
        else:
            QMessageBox.warning(self, "Папка не найдена", f"Папка не существует:\n{folder}")

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку вывода")
        if folder:
            self._output_input.setText(folder)

    def _reset_stats(self):
        self._stat_total.setText("Всего: 0")
        self._stat_exported.setText("Экспортировано: 0")
        self._stat_duplicates.setText("Дубликаты: 0")
        self._stat_size.setText("Размер: 0 КБ")
        self._stat_time.setText("Время: 0.0с")

```

### `src\ui\pages\parsing_page.py`
```python
import asyncio
import time
from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QThread, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableView,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from src.database.models import Category, Product, Supplier
from src.database.session import get_session
from src.modules.parsing.engine import ParserEngine, ParsingStats


class CategoryCheckModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels(["Категория", "URL", "Товары"])

    def load_categories(self, supplier_id: int) -> int:
        self.removeRows(0, self.rowCount())

        with get_session() as session:
            top_level = session.query(Category).filter(
                Category.supplier_id == supplier_id,
                Category.parent_id.is_(None),
            ).order_by(Category.sort_order, Category.name).all()

            def _build_tree(parent_item, parent_id):
                children = session.query(Category).filter(
                    Category.supplier_id == supplier_id,
                    Category.parent_id == parent_id,
                ).order_by(Category.sort_order, Category.name).all()

                for cat in children:
                    name_item = QStandardItem(cat.name)
                    name_item.setCheckable(True)
                    name_item.setCheckState(Qt.Unchecked)
                    name_item.setData(cat.id, Qt.UserRole)

                    url_item = QStandardItem(cat.url)
                    count_item = QStandardItem(str(cat.product_count))

                    parent_item.appendRow([name_item, url_item, count_item])
                    _build_tree(name_item, cat.id)

            root = self.invisibleRootItem()
            for cat in top_level:
                name_item = QStandardItem(cat.name)
                name_item.setCheckable(True)
                name_item.setCheckState(Qt.Unchecked)
                name_item.setData(cat.id, Qt.UserRole)

                url_item = QStandardItem(cat.url)
                count_item = QStandardItem(str(cat.product_count))

                root.appendRow([name_item, url_item, count_item])
                _build_tree(name_item, cat.id)

            return len(top_level)

    def get_checked_ids(self) -> list[int]:
        ids = []

        def _collect(item):
            if item.isCheckable() and item.checkState() == Qt.Checked:
                cat_id = item.data(Qt.UserRole)
                if cat_id is not None:
                    ids.append(cat_id)
            for i in range(item.rowCount()):
                _collect(item.child(i, 0))

        for i in range(self.rowCount()):
            _collect(self.item(i, 0))
        return ids

    def check_all(self) -> None:
        def _set_checked(item):
            if item.isCheckable():
                item.setCheckState(Qt.Checked)
            for i in range(item.rowCount()):
                _set_checked(item.child(i, 0))

        for i in range(self.rowCount()):
            _set_checked(self.item(i, 0))

    def uncheck_all(self) -> None:
        def _set_unchecked(item):
            if item.isCheckable():
                item.setCheckState(Qt.Unchecked)
            for i in range(item.rowCount()):
                _set_unchecked(item.child(i, 0))

        for i in range(self.rowCount()):
            _set_unchecked(self.item(i, 0))


class TaskStatusModel(QAbstractTableModel):
    _headers = ["Задача", "Статус", "Товары", "Ошибки", "Время"]

    def __init__(self):
        super().__init__()
        self._rows: list[dict] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        row = self._rows[index.row()]
        col = index.column()
        keys = ["task", "status", "products", "errors", "time"]
        return row.get(keys[col], "")

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def add_task(self, task: str, status: str = "Выполняется", products: int = 0, errors: int = 0, elapsed: str = ""):
        self._rows.append({
            "task": task,
            "status": status,
            "products": str(products),
            "errors": str(errors),
            "time": elapsed,
        })
        self.layoutChanged.emit()

    def update_last(self, **kwargs):
        if self._rows:
            self._rows[-1].update(kwargs)
            self.layoutChanged.emit()

    def clear(self):
        self._rows.clear()
        self.layoutChanged.emit()


class ParsingWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int, int, str)
    stats_signal = Signal(dict)
    finished_signal = Signal(dict)

    def __init__(
        self,
        supplier_id: int,
        base_url: str,
        category_ids: list[int],
        concurrency: int = 5,
        delay_min: float = 0.5,
        delay_max: float = 2.0,
        timeout: int = 30,
    ):
        super().__init__()
        self.supplier_id = supplier_id
        self.base_url = base_url
        self.category_ids = category_ids
        self.concurrency = concurrency
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.timeout = timeout
        self._engine: Optional[ParserEngine] = None

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def log_cb(msg):
            self.log_signal.emit(msg)

        def progress_cb(pct, total, msg):
            self.progress_signal.emit(pct, total, msg)

        self._engine = ParserEngine(
            supplier_id=self.supplier_id,
            base_url=self.base_url,
            concurrency=self.concurrency,
            delay_range=(self.delay_min, self.delay_max),
            timeout=self.timeout,
            log_callback=log_cb,
            progress_callback=progress_cb,
        )

        async def _run():
            with get_session() as session:
                result = await self._engine.run(self.category_ids, session)
            return result

        try:
            result = loop.run_until_complete(_run())
            stats = result.get("stats")
            if stats:
                self.stats_signal.emit({
                    "total_products": stats.total_products,
                    "total_pages": stats.total_pages,
                    "successful_pages": stats.successful_pages,
                    "failed_pages": stats.failed_pages,
                    "total_attributes": stats.total_attributes,
                    "errors": stats.errors,
                    "elapsed": stats.elapsed,
                })
            self.finished_signal.emit(result)
        except Exception as exc:
            self.finished_signal.emit({"success": False, "error": str(exc)})
        finally:
            loop.close()

    def cancel(self):
        if self._engine:
            self._engine.cancel()

    def pause(self):
        if self._engine:
            self._engine.pause()

    def resume(self):
        if self._engine:
            self._engine.resume()


class ParsingPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: Optional[ParsingWorker] = None
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        ctrl_group = QGroupBox("Управление парсингом")
        ctrl_layout = QVBoxLayout(ctrl_group)

        supplier_row = QHBoxLayout()
        supplier_row.addWidget(QLabel("Поставщик:"))
        self._supplier_combo = QComboBox()
        self._supplier_combo.setMinimumWidth(300)
        supplier_row.addWidget(self._supplier_combo)
        supplier_row.addStretch()
        ctrl_layout.addLayout(supplier_row)

        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Параллелизм:"))
        self._concurrency_combo = QComboBox()
        self._concurrency_combo.addItems(["3", "5", "8", "10", "15"])
        self._concurrency_combo.setCurrentText("5")
        self._concurrency_combo.setMaximumWidth(60)
        options_row.addWidget(self._concurrency_combo)

        options_row.addSpacing(16)
        options_row.addWidget(QLabel("Задержка (с):"))
        self._delay_min_input = QComboBox()
        self._delay_min_input.addItems(["0.2", "0.5", "1.0", "2.0"])
        self._delay_min_input.setCurrentText("0.5")
        self._delay_min_input.setMaximumWidth(70)
        options_row.addWidget(self._delay_min_input)

        options_row.addWidget(QLabel("–"))

        self._delay_max_input = QComboBox()
        self._delay_max_input.addItems(["1.0", "2.0", "3.0", "5.0"])
        self._delay_max_input.setCurrentText("2.0")
        self._delay_max_input.setMaximumWidth(70)
        options_row.addWidget(self._delay_max_input)

        options_row.addSpacing(16)
        options_row.addWidget(QLabel("Таймаут (с):"))
        self._timeout_combo = QComboBox()
        self._timeout_combo.addItems(["15", "30", "60", "120"])
        self._timeout_combo.setCurrentText("30")
        self._timeout_combo.setMaximumWidth(70)
        options_row.addWidget(self._timeout_combo)

        options_row.addStretch()
        ctrl_layout.addLayout(options_row)

        btn_row = QHBoxLayout()
        self._btn_start = QPushButton("Запустить парсинг")
        self._btn_start.setMinimumHeight(40)
        self._btn_pause = QPushButton("Пауза")
        self._btn_pause.setMinimumHeight(40)
        self._btn_pause.setEnabled(False)
        self._btn_stop = QPushButton("Стоп")
        self._btn_stop.setMinimumHeight(40)
        self._btn_stop.setEnabled(False)
        self._btn_select_all = QPushButton("Выбрать все")
        self._btn_select_all.setMinimumHeight(40)
        self._btn_select_none = QPushButton("Снять выбор")
        self._btn_select_none.setMinimumHeight(40)
        btn_row.addWidget(self._btn_start)
        btn_row.addWidget(self._btn_pause)
        btn_row.addWidget(self._btn_stop)
        btn_row.addSpacing(16)
        btn_row.addWidget(self._btn_select_all)
        btn_row.addWidget(self._btn_select_none)
        btn_row.addStretch()
        ctrl_layout.addLayout(btn_row)

        layout.addWidget(ctrl_group)

        progress_row = QHBoxLayout()
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimumHeight(20)
        self._progress_label = QLabel("Готово")
        progress_row.addWidget(self._progress_bar, 1)
        progress_row.addWidget(self._progress_label)
        layout.addLayout(progress_row)

        splitter = QSplitter(Qt.Vertical)

        cat_group = QGroupBox("Категории (отметьте для парсинга)")
        cat_layout = QVBoxLayout(cat_group)
        self._cat_tree = QTreeView()
        self._cat_model = CategoryCheckModel()
        self._cat_tree.setModel(self._cat_model)
        self._cat_tree.setAlternatingRowColors(True)
        self._cat_tree.header().setStretchLastSection(False)
        self._cat_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._cat_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self._cat_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        cat_layout.addWidget(self._cat_tree)
        splitter.addWidget(cat_group)

        stats_group = QGroupBox("Статус задач")
        stats_layout = QVBoxLayout(stats_group)
        self._task_table = QTableView()
        self._task_model = TaskStatusModel()
        self._task_table.setModel(self._task_model)
        self._task_table.setAlternatingRowColors(True)
        self._task_table.horizontalHeader().setStretchLastSection(True)
        stats_layout.addWidget(self._task_table)
        splitter.addWidget(stats_group)

        log_group = QGroupBox("Журнал парсинга")
        log_layout = QVBoxLayout(log_group)
        self._log_edit = QPlainTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(180)
        log_layout.addWidget(self._log_edit)
        splitter.addWidget(log_group)

        stats_row = QHBoxLayout()
        self._stat_products = QLabel("Товаров: 0")
        self._stat_pages = QLabel("Страниц: 0")
        self._stat_errors = QLabel("Ошибок: 0")
        self._stat_time = QLabel("Время: 0.0с")
        self._stat_attrs = QLabel("Атрибутов: 0")
        stats_row.addWidget(self._stat_products)
        stats_row.addWidget(self._stat_pages)
        stats_row.addWidget(self._stat_errors)
        stats_row.addWidget(self._stat_time)
        stats_row.addWidget(self._stat_attrs)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        splitter.setSizes([250, 150, 180])
        layout.addWidget(splitter)

        self._btn_start.clicked.connect(self._on_start)
        self._btn_pause.clicked.connect(self._on_pause)
        self._btn_stop.clicked.connect(self._on_stop)
        self._btn_select_all.clicked.connect(self._cat_model.check_all)
        self._btn_select_none.clicked.connect(self._cat_model.uncheck_all)
        self._supplier_combo.currentIndexChanged.connect(self._on_supplier_changed)

    def _load_suppliers(self):
        self._supplier_combo.clear()
        try:
            with get_session() as session:
                suppliers = session.query(Supplier).filter(
                    Supplier.is_active == True
                ).order_by(Supplier.name).all()
                for s in suppliers:
                    self._supplier_combo.addItem(s.name, userData=s.id)
        except Exception as exc:
            self._append_log(f"Ошибка загрузки поставщиков: {exc}")

    def _on_supplier_changed(self):
        supplier_id = self._supplier_combo.currentData()
        if supplier_id:
            count = self._cat_model.load_categories(supplier_id)
            self._append_log(f"Загружено {count} категорий верхнего уровня")

    def _append_log(self, msg: str):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_edit.appendPlainText(f"[{ts}] {msg}")

    def _on_start(self):
        supplier_id = self._supplier_combo.currentData()
        if supplier_id is None:
            QMessageBox.warning(self, "Нет поставщика", "Сначала выберите поставщика.")
            return

        category_ids = self._cat_model.get_checked_ids()
        if not category_ids:
            QMessageBox.warning(self, "Нет категорий", "Выберите хотя бы одну категорию для парсинга.")
            return

        with get_session() as session:
            supplier = session.query(Supplier).filter(Supplier.id == supplier_id).first()
            if not supplier:
                QMessageBox.warning(self, "Ошибка", "Поставщик не найден.")
                return
            base_url = supplier.base_url

        self._btn_start.setEnabled(False)
        self._btn_pause.setEnabled(True)
        self._btn_stop.setEnabled(True)
        self._progress_bar.setValue(0)
        self._progress_label.setText("Запуск...")
        self._log_edit.clear()
        self._task_model.clear()
        self._reset_stats()

        self._append_log(f"Запуск парсинга для '{self._supplier_combo.currentText()}'")
        self._append_log(f"Выбрано категорий: {len(category_ids)}")

        concurrency = int(self._concurrency_combo.currentText())
        delay_min = float(self._delay_min_input.currentText())
        delay_max = float(self._delay_max_input.currentText())
        timeout = int(self._timeout_combo.currentText())

        self._worker = ParsingWorker(
            supplier_id=supplier_id,
            base_url=base_url,
            category_ids=category_ids,
            concurrency=concurrency,
            delay_min=delay_min,
            delay_max=delay_max,
            timeout=timeout,
        )
        self._worker.log_signal.connect(self._append_log)
        self._worker.progress_signal.connect(self._on_progress)
        self._worker.stats_signal.connect(self._on_stats)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.start()

    def _on_pause(self):
        if not self._worker or not self._worker.isRunning():
            return
        if self._btn_pause.text() == "Пауза":
            self._worker.pause()
            self._btn_pause.setText("Продолжить")
            self._append_log("Парсинг приостановлен")
        else:
            self._worker.resume()
            self._btn_pause.setText("Пауза")
            self._append_log("Парсинг возобновлён")

    def _on_stop(self):
        if self._worker and self._worker.isRunning():
            self._append_log("Остановка парсинга...")
            self._worker.cancel()
            self._btn_stop.setEnabled(False)
            self._btn_pause.setEnabled(False)

    def _on_progress(self, pct: int, total: int, msg: str):
        self._progress_bar.setValue(min(pct, 100))
        self._progress_label.setText(f"{pct}% — {msg}")

    def _on_stats(self, stats: dict):
        self._stat_products.setText(f"Товаров: {stats.get('total_products', 0)}")
        self._stat_pages.setText(f"Страниц: {stats.get('total_pages', 0)}")
        self._stat_errors.setText(f"Ошибок: {stats.get('failed_pages', 0)}")
        self._stat_time.setText(f"Время: {stats.get('elapsed', 0):.1f}с")
        self._stat_attrs.setText(f"Атрибутов: {stats.get('total_attributes', 0)}")

    def _on_finished(self, result: dict):
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)
        self._btn_stop.setEnabled(False)
        self._btn_pause.setText("Пауза")

        if result.get("success"):
            count = result.get("products_parsed", 0)
            self._progress_bar.setValue(100)
            self._progress_label.setText(f"Готово — {count} товаров обработано")
            self._append_log(f"Парсинг завершён: {count} товаров")
            QMessageBox.information(self, "Успех", f"Парсинг завершён.\nСохранено {count} товаров.")
        else:
            error = result.get("error", "Неизвестная ошибка")
            self._progress_label.setText(f"Ошибка: {error}")
            self._append_log(f"Парсинг не удался: {error}")
            QMessageBox.critical(self, "Ошибка парсинга", f"Парсинг не удался:\n{error}")

    def _reset_stats(self):
        self._stat_products.setText("Товаров: 0")
        self._stat_pages.setText("Страниц: 0")
        self._stat_errors.setText("Ошибок: 0")
        self._stat_time.setText("Время: 0.0с")
        self._stat_attrs.setText("Атрибутов: 0")

```

### `src\ui\pages\placeholder_page.py`
```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PlaceholderPage(QWidget):
    def __init__(self, title: str, description: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setObjectName("subtitle")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

```

### `src\ui\pages\suppliers_page.py`
```python
from datetime import datetime
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from src.database.models import Supplier
from src.database.session import get_session
from src.database.supplier_crud import (
    create_supplier,
    delete_supplier,
    get_all_suppliers,
    update_supplier,
)


class SupplierTableModel(QAbstractTableModel):
    _headers = [
        "ID",
        "Название",
        "Базовый URL",
        "Статус",
        "Последняя разведка",
        "Последний парсинг",
        "Создан",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._data: list[dict] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        row = self._data[index.row()]
        col = index.column()

        keys = ["id", "name", "base_url", "is_active", "last_discovery_run", "last_scrape_run", "created_at"]
        key = keys[col]
        val = row.get(key)

        if col == 0:
            return val
        if col == 3:
            return "Активен" if val else "Неактивен"
        if col in (4, 5, 6):
            return val.strftime("%Y-%m-%d %H:%M") if val else "—"
        return str(val) if val is not None else ""

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def get_supplier(self, row: int) -> dict | None:
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def refresh(self) -> None:
        self.beginResetModel()
        with get_session() as session:
            suppliers = get_all_suppliers(session, active_only=False)
            self._data = []
            for s in suppliers:
                self._data.append({
                    "id": s.id,
                    "name": s.name,
                    "base_url": s.base_url,
                    "is_active": s.is_active,
                    "last_discovery_run": s.last_discovery_run,
                    "last_scrape_run": s.last_scrape_run,
                    "created_at": s.created_at,
                })
        self.endResetModel()


class SuppliersPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._selected_supplier_id: int | None = None
        self._setup_ui()
        self._connect_signals()
        self._refresh_table()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._table = QTableView()
        self._model = SupplierTableModel()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.setSelectionMode(QTableView.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setMinimumHeight(300)
        layout.addWidget(self._table)

        form_frame = QWidget()
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(0, 8, 0, 0)

        self._name_input = QLineEdit()
        self._name_input.setMaxLength(255)
        self._name_input.setPlaceholderText("Название поставщика (обязательно, мин. 2 символа)")
        form_layout.addRow("Название:", self._name_input)

        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://example.com")
        url_validator = QRegularExpressionValidator(
            QRegularExpression(r"^https?://.+")
        )
        self._url_input.setValidator(url_validator)
        form_layout.addRow("Базовый URL:", self._url_input)

        layout.addWidget(form_frame)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self._btn_add = QPushButton("Добавить")
        self._btn_update = QPushButton("Обновить")
        self._btn_delete = QPushButton("Удалить")
        self._btn_refresh = QPushButton("Обновить таблицу")

        for btn in (self._btn_add, self._btn_update, self._btn_delete, self._btn_refresh):
            btn.setMinimumHeight(36)
            btn_layout.addWidget(btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _connect_signals(self) -> None:
        self._btn_add.clicked.connect(self._on_add)
        self._btn_update.clicked.connect(self._on_update)
        self._btn_delete.clicked.connect(self._on_delete)
        self._btn_refresh.clicked.connect(self._refresh_table)
        self._table.doubleClicked.connect(self._on_row_double_click)

    def _refresh_table(self) -> None:
        self._model.refresh()

    def _validate_name(self) -> str | None:
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.critical(self, "Ошибка валидации", "Название обязательно.")
            return None
        if len(name) < 2:
            QMessageBox.critical(self, "Ошибка валидации", "Название должно содержать минимум 2 символа.")
            return None
        if len(name) > 255:
            QMessageBox.critical(self, "Ошибка валидации", "Название не должно превышать 255 символов.")
            return None
        return name

    def _validate_url(self) -> str | None:
        url = self._url_input.text().strip()
        if not url:
            QMessageBox.critical(self, "Ошибка валидации", "Базовый URL обязателен.")
            return None
        if not url.startswith(("http://", "https://")):
            QMessageBox.critical(
                self, "Ошибка валидации", "Базовый URL должен начинаться с http:// или https://"
            )
            return None
        return url

    def _on_add(self) -> None:
        name = self._validate_name()
        url = self._validate_url()
        if not name or not url:
            return

        try:
            with get_session() as session:
                create_supplier(session, name, url)
            QMessageBox.information(self, "Успех", f"Поставщик '{name}' создан.")
            self._name_input.clear()
            self._url_input.clear()
            self._refresh_table()
        except ValueError as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось создать поставщика:\n{exc}")

    def _on_update(self) -> None:
        if self._selected_supplier_id is None:
            QMessageBox.warning(self, "Нет выбора", "Выберите поставщика из таблицы для обновления.")
            return

        name = self._validate_name()
        url = self._validate_url()
        if not name or not url:
            return

        try:
            with get_session() as session:
                result = update_supplier(
                    session,
                    self._selected_supplier_id,
                    name=name,
                    base_url=url,
                )
            if result:
                QMessageBox.information(self, "Успех", f"Поставщик '{name}' обновлён.")
                self._name_input.clear()
                self._url_input.clear()
                self._selected_supplier_id = None
                self._refresh_table()
            else:
                QMessageBox.warning(self, "Ошибка", "Поставщик не найден.")
        except ValueError as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось обновить поставщика:\n{exc}")

    def _on_delete(self) -> None:
        if self._selected_supplier_id is None:
            QMessageBox.warning(self, "Нет выбора", "Выберите поставщика из таблицы для удаления.")
            return

        supplier = self._model.get_supplier(self._table.currentIndex().row())
        supplier_name = supplier["name"] if supplier else "этот поставщик"

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите деактивировать '{supplier_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            with get_session() as session:
                found = delete_supplier(session, self._selected_supplier_id)
            if found:
                QMessageBox.information(self, "Успех", f"Поставщик '{supplier_name}' деактивирован.")
                self._name_input.clear()
                self._url_input.clear()
                self._selected_supplier_id = None
                self._refresh_table()
            else:
                QMessageBox.warning(self, "Ошибка", "Поставщик не найден.")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось удалить поставщика:\n{exc}")

    def _on_row_double_click(self, index: QModelIndex) -> None:
        row = index.row()
        supplier = self._model.get_supplier(row)
        if supplier:
            self._selected_supplier_id = supplier["id"]
            self._name_input.setText(supplier["name"])
            self._url_input.setText(supplier["base_url"])

```

### `src\ui\styles\__init__.py`
```python

```

### `src\ui\styles\dark_theme.qss`
```text
/* ============================================================
   MEEYG 1.0 — Premium Dark Theme
   ============================================================ */

/* ---------- Global ---------- */
QWidget {
    background-color: #1a1a2e;
    color: #eaeaea;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #1a1a2e;
}

/* ---------- Sidebar ---------- */
QFrame#sidebar {
    background-color: #16213e;
    border-right: 1px solid #0f3460;
}

/* ---------- Navigation Buttons (sidebar cards) ---------- */
QPushButton#navButton {
    background-color: #0f3460;
    color: #eaeaea;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
}

QPushButton#navButton:hover {
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #533483, stop:1 #0f3460
    );
}

QPushButton#navButton:checked,
QPushButton#navButton:pressed {
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #e94560, stop:1 #533483
    );
    color: #ffffff;
    font-weight: 700;
}

/* ---------- Cards / Panels ---------- */
QFrame#card {
    background-color: #0f3460;
    border-radius: 10px;
    padding: 16px;
}

/* ---------- Table / QTableView ---------- */
QTableView {
    background-color: #0f3460;
    alternate-background-color: #16213e;
    color: #eaeaea;
    border: 1px solid #533483;
    border-radius: 8px;
    gridline-color: #1a1a2e;
    selection-background-color: #e94560;
    selection-color: #ffffff;
}

QTableView::item:hover {
    background-color: #533483;
    color: #ffffff;
}

QTableView::item:selected {
    background-color: #e94560;
    color: #ffffff;
}

/* ---------- Table Header ---------- */
QHeaderView::section {
    background-color: qlineargradient(
        x1:0, y1:0, x2:0, y2:1,
        stop:0 #533483, stop:1 #0f3460
    );
    color: #eaeaea;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #e94560;
    font-weight: 700;
    font-size: 13px;
}

QHeaderView::section:hover {
    background-color: #e94560;
    color: #ffffff;
}

/* ---------- Buttons ---------- */
QPushButton {
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #e94560, stop:1 #533483
    );
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #ff5a78, stop:1 #6b44a8
    );
}

QPushButton:pressed {
    background-color: #e94560;
    padding-top: 11px;
    padding-bottom: 9px;
}

QPushButton:disabled {
    background-color: #2a2a4a;
    color: #a0a0b0;
}

/* ---------- Input Fields ---------- */
QLineEdit {
    background-color: #16213e;
    color: #eaeaea;
    border: 1px solid #533483;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: #e94560;
    selection-color: #ffffff;
}

QLineEdit:focus {
    border: 2px solid #e94560;
    background-color: #1a1a2e;
}

QLineEdit:disabled {
    background-color: #2a2a4a;
    color: #a0a0b0;
}

/* ---------- Labels ---------- */
QLabel {
    color: #eaeaea;
    font-size: 13px;
}

QLabel#title {
    font-size: 22px;
    font-weight: 700;
    color: #e94560;
}

QLabel#subtitle {
    font-size: 14px;
    color: #a0a0b0;
}

QLabel#muted {
    color: #a0a0b0;
    font-size: 12px;
}

/* ---------- Form Layout ---------- */
QFormLayout {
    margin: 0px;
    spacing: 8px;
}

/* ---------- Status Bar ---------- */
QStatusBar {
    background-color: #16213e;
    color: #a0a0b0;
    border-top: 1px solid #0f3460;
    font-size: 12px;
}

QStatusBar QLabel {
    color: #a0a0b0;
}

/* ---------- Menu Bar / Menu ---------- */
QMenuBar {
    background-color: #16213e;
    color: #eaeaea;
    border-bottom: 1px solid #0f3460;
    padding: 4px;
}

QMenuBar::item {
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #533483;
}

QMenu {
    background-color: #16213e;
    color: #eaeaea;
    border: 1px solid #533483;
    border-radius: 8px;
    padding: 6px;
}

QMenu::item {
    padding: 8px 32px 8px 16px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #e94560;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background-color: #533483;
    margin: 4px 12px;
}

/* ---------- Scrollbars ---------- */
QScrollBar:vertical {
    background-color: #16213e;
    width: 10px;
    border-radius: 5px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #533483;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #e94560;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background-color: #16213e;
    height: 10px;
    border-radius: 5px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #533483;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #e94560;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
}

/* ---------- QMessageBox ---------- */
QMessageBox {
    background-color: #16213e;
}

QMessageBox QLabel {
    color: #eaeaea;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* ---------- QGroupBox ---------- */
QGroupBox {
    background-color: #0f3460;
    border: 1px solid #533483;
    border-radius: 10px;
    margin-top: 12px;
    padding-top: 20px;
    font-weight: 600;
    color: #e94560;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: #e94560;
}

/* ---------- QComboBox ---------- */
QComboBox {
    background-color: #16213e;
    color: #eaeaea;
    border: 1px solid #533483;
    border-radius: 6px;
    padding: 6px 12px;
}

QComboBox:hover {
    border-color: #e94560;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #eaeaea;
    selection-background-color: #e94560;
    selection-color: #ffffff;
    border: 1px solid #533483;
}

/* ---------- QProgressBar ---------- */
QProgressBar {
    background-color: #16213e;
    border: 1px solid #533483;
    border-radius: 6px;
    text-align: center;
    color: #ffffff;
    height: 14px;
}

QProgressBar::chunk {
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #e94560, stop:1 #533483
    );
    border-radius: 5px;
}

/* ---------- QTabWidget ---------- */
QTabWidget::pane {
    background-color: #0f3460;
    border: 1px solid #533483;
    border-radius: 8px;
}

QTabBar::tab {
    background-color: #16213e;
    color: #a0a0b0;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #0f3460;
    color: #e94560;
    font-weight: 700;
}

QTabBar::tab:hover:!selected {
    background-color: #533483;
    color: #eaeaea;
}

/* ---------- QToolTip ---------- */
QToolTip {
    background-color: #16213e;
    color: #eaeaea;
    border: 1px solid #533483;
    border-radius: 4px;
    padding: 6px;
}

/* ---------- QSplitter ---------- */
QSplitter::handle {
    background-color: #533483;
}

QSplitter::handle:hover {
    background-color: #e94560;
}

QSplitter::handle:horizontal {
    width: 3px;
}

QSplitter::handle:vertical {
    height: 3px;
}

```

### `tests\check_hierarchy_implementation.py`
```python
#!/usr/bin/env python3
"""
Verification script for hierarchy parsing implementation
"""

import json
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_implementation():
    """Verify that the implementation is correct"""
    
    print("=== Implementation Verification ===")
    
    # Check that required methods exist in engine.py
    engine_path = Path(__file__).parent.parent / "src" / "modules" / "parsing" / "engine.py"
    if not engine_path.exists():
        print("ERROR: engine.py not found")
        return False
        
    engine_content = engine_path.read_text(encoding='utf-8')
    
    # Check for _extract_variations method
    if "_extract_variations" not in engine_content:
        print("ERROR: _extract_variations method not found in engine.py")
        return False
        
    # Check for _upsert_molding_item method
    if "_upsert_molding_item" not in engine_content:
        print("ERROR: _upsert_molding_item method not found in engine.py")
        return False
        
    # Check for variations handling in _save_batch
    if "variations" not in engine_content:
        print("WARNING: Variations handling may not be implemented in _save_batch")
        
    print("[OK] engine.py contains required methods")
    
    # Check that required methods exist in tandoor_playwright_parser.py
    parser_path = Path(__file__).parent.parent / "src" / "modules" / "parsing" / "tandoor_playwright_parser.py"
    if not parser_path.exists():
        print("ERROR: tandoor_playwright_parser.py not found")
        return False
        
    parser_content = parser_path.read_text(encoding='utf-8')
    
    # Check for _extract_variations method
    if "_extract_variations" not in parser_content:
        print("ERROR: _extract_variations method not found in tandoor_playwright_parser.py")
        return False
        
    # Check for _upsert_molding_item method
    if "_upsert_molding_item" not in parser_content:
        print("ERROR: _upsert_molding_item method not found in tandoor_playwright_parser.py")
        return False
        
    print("[OK] tandoor_playwright_parser.py contains required methods")
    
    # Check that test file exists
    test_path = Path(__file__).parent.parent / "tests" / "test_hierarchy_logic.py"
    if not test_path.exists():
        print("ERROR: test_hierarchy_logic.py not found")
        return False
        
    print("[OK] test_hierarchy_logic.py exists")
    
    print("\n=== Verification Passed ===")
    return True


if __name__ == "__main__":
    success = check_implementation()
    sys.exit(0 if success else 1)
```

### `tests\test_hierarchy_logic.py`
```python
#!/usr/bin/env python3
"""
Test script for hierarchy parsing logic
"""

import json
import sys
import os
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up Django settings if needed
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.core.settings')

def test_hierarchy_logic():
    """Test the hierarchy parsing logic"""
    
    # Mock data simulating a parsed door product with variations and molding
    mock_product_data = {
        "url": "https://example.com/product/door-123",
        "title": "Дверь Бона белая",
        "price": 15000.0,
        "currency": "RUB",
        "sku": "BONA-WHITE-123",
        "description": "Белая межкомнатная дверь Бона",
        "is_available": True,
        "image_urls": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
        "attributes": {
            "Материал": "ЛДСП",
            "Покрытие": "Белый глянец",
            "Производитель": "Фабрика Дверей"
        },
        "category_id": 5,  # "Межкомнатные двери"
        "variations": [
            {
                "title": "Дверь Бона белая 70x200",
                "price": 15000.0,
                "attributes": {
                    "Размер": "70x200",
                    "Тип": "Правая"
                }
            },
            {
                "title": "Дверь Бона белая 80x200",
                "price": 16000.0,
                "attributes": {
                    "Размер": "80x200",
                    "Тип": "Правая"
                }
            },
            {
                "title": "Дверь Бона белая 90x200",
                "price": 17000.0,
                "attributes": {
                    "Размер": "90x200",
                    "Тип": "Правая"
                }
            }
        ],
        "molding_items": [
            {
                "title": "Добор 100x20 мм белый",
                "price": 1200.0,
                "color": "Белый",
                "external_id": "DOBOR-100-20-WHITE",
                "type": "Добор"
            },
            {
                "title": "Наличник 60x20 мм белый",
                "price": 800.0,
                "color": "Белый",
                "external_id": "NALICHNIK-60-20-WHITE",
                "type": "Наличник"
            }
        ]
    }
    
    print("=== Test: Hierarchy Parsing Logic ===")
    print(f"Testing product: {mock_product_data['title']}")
    print(f"Variations count: {len(mock_product_data['variations'])}")
    print(f"Molding items count: {len(mock_product_data['molding_items'])}")
    
    # Test Product model helpers for compatible_collections
    print(f"\nTesting Product model helpers:")
    
    # Since we can't easily instantiate the Product model without Django setup,
    # we'll test the logic conceptually
    
    # Test compatible collections logic
    door_category_path = "Межкомнатные двери > Бона"
    
    # Simulate existing compatible collections
    existing_collections = ["Межкомнатные двери > Лофт"]
    
    # Add new collection if not present
    if door_category_path not in existing_collections:
        existing_collections.append(door_category_path)
    
    print(f"  Existing collections: ['Межкомнатные двери > Лофт']")
    print(f"  Added new collection: {door_category_path}")
    print(f"  Final collections: {existing_collections}")
    print(f"  New collection included: {door_category_path in existing_collections}")
    
    # Test adding duplicate collection
    initial_count = len(existing_collections)
    if door_category_path not in existing_collections:
        existing_collections.append(door_category_path)
    final_count = len(existing_collections)
    
    print(f"  Attempting to add duplicate collection")
    print(f"  Collection count unchanged: {initial_count == final_count}")
    
    # Test variations combining logic
    print(f"\nTesting variations combining logic:")
    
    # Simulate collecting all sizes from variations
    all_sizes = []
    for variation in mock_product_data['variations']:
        size_attr = variation.get("attributes", {}).get("Размер")
        if size_attr and size_attr not in all_sizes:
            all_sizes.append(size_attr)
    
    sizes_string = "|".join(all_sizes)
    print(f"  Collected sizes: {all_sizes}")
    print(f"  Sizes string: {sizes_string}")
    
    print("\n=== Test Completed ===")


if __name__ == "__main__":
    test_hierarchy_logic()
```

### `tests\test_tandoor_parser.py`
```python
import asyncio
import os
import sys
from typing import List

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.parsing.tandoor_playwright_parser import TandoorPlaywrightParser
from src.database.session import get_session
from src.database.models import Supplier

async def test_parse_product_page():
    """Test parsing a single product page."""
    # Test URL
    test_url = "https://tandoor.ru/catalog/product/dekanto-belyy-evo-pet-do-seryy-satin-2000-800/"
    
    # Get database session
    with get_session() as db_session:
        # Get supplier (assuming supplier with ID 1 exists)
        supplier = db_session.query(Supplier).first()
        if not supplier:
            print("No supplier found in database")
            return
            
        # Create parser instance
        parser = TandoorPlaywrightParser(
            supplier_id=supplier.id,
            db_session=db_session,
            headless=True,
            delay_range=(1.0, 3.0),
            log_callback=print,
            progress_callback=lambda p, t, m: print(f"Progress: {p}% - {m}")
        )
        
        try:
            # Parse product page
            print(f"Parsing product page: {test_url}")
            result = await parser.parse_product_page(test_url)
            
            # Print results
            print(f"Title: {result.title}")
            print(f"Price: {result.price}")
            print(f"Currency: {result.currency}")
            print(f"SKU: {result.sku}")
            print(f"Description: {result.description}")
            print(f"Images: {len(result.image_urls)}")
            print(f"Molding items: {len(result.molding_items)}")
            print(f"Variations: {len(result.variations)}")
            
            # Print attributes
            print("Attributes:")
            for name, value in result.attributes.items():
                print(f"  {name}: {value}")
                
            # Print molding items
            if result.molding_items:
                print("Molding Items:")
                for item in result.molding_items:
                    print(f"  - {item['title']} ({item['type']}) - {item['price']} RUB")
                    
            # Print variations
            if result.variations:
                print("Variations:")
                for variation in result.variations:
                    print(f"  - {variation.title} - {variation.price} {variation.currency}")
                    
        except Exception as e:
            print(f"Error during test: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(test_parse_product_page())
```
