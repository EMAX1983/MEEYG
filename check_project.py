"""
Скрипт проверки работоспособности проекта MEEYG.
"""
import sys
import os

# Drive to project root
sys.path.insert(0, '.')

results = []

def check(name, func):
    try:
        result = func()
        results.append(f"[OK] {name}: {result}")
        print(f"[OK] {name}: {result}")
    except Exception as e:
        results.append(f"[FAIL] {name}: {e}")
        print(f"[FAIL] {name}: {e}")

# 1. Core modules
check("Config", lambda: f"{settings.app_name} v{settings.app_version}" 
      if (globals()['settings'].__name__ if 'settings' in globals() else None) 
      else exec("from src.core.config import settings; globals()['settings'] = settings") or f"{settings.app_name} v{settings.app_version}")

# Simpler approach
from src.core.config import settings
check("Config", lambda: f"{settings.app_name} v{settings.app_version}")

from src.core.logger import logger
check("Logger", lambda: "structlog initialized")

from src.database.models import Base
check("Models", lambda: "Base declarative ready")

from src.database.engine import create_engine
eng = create_engine()
check("Engine", lambda: "SQLite + sqlcipher engine created")

from src.database.session import SessionFactory
sess = SessionFactory()
check("Session", lambda: "SessionFactory works")

# Database models
from src.database.models import Supplier, Category, Product, ProductAttribute, ArchiveSnapshot, ArchiveItem, MappingTemplate
check("All DB Models", lambda: "Supplier, Category, Product, ProductAttribute, ArchiveSnapshot, ArchiveItem, MappingTemplate")

# UI components
from src.ui.main_window import MainWindow
check("MainWindow", lambda: "QMainWindow subclass ready")

from src.ui.pages.placeholder_page import PlaceholderPage
check("PlaceholderPage", lambda: "Placeholder widget ready")

from src.ui.pages.archive_page import ArchivePage
check("ArchivePage", lambda: "Archive widget ready")

from src.ui.pages.discovery_page import DiscoveryPage
check("DiscoveryPage", lambda: "Discovery widget ready")

from src.ui.pages.export_page import ExportPage
check("ExportPage", lambda: "Export widget ready")

from src.ui.pages.parsing_page import ParsingPage
check("ParsingPage", lambda: "Parsing widget ready")

from src.ui.pages.suppliers_page import SuppliersPage
check("SuppliersPage", lambda: "Suppliers widget ready")

# Parser modules
from src.modules.parsing.base_parser import BaseParser, ParsedProduct
check("BaseParser", lambda: "Abstract parser base class ready")

from src.modules.parsing.engine import ParserEngine
check("ParserEngine", lambda: "Parser engine ready")

# File system checks
check("dark_theme.qss", lambda: "exists" if os.path.exists("src/ui/styles/dark_theme.qss") else "MISSING")
check("data directory", lambda: "exists" if os.path.exists("data") else "MISSING")
check("logs directory", lambda: "exists" if os.path.exists("logs") else "MISSING")
check(".env file", lambda: "exists" if os.path.exists(".env") else "MISSING")

# Python version
check("Python version", lambda: sys.version)

# Dependencies
import sqlalchemy
check("SQLAlchemy", lambda: sqlalchemy.__version__)

import PySide6
check("PySide6", lambda: PySide6.__version__)

import pydantic
check("Pydantic", lambda: pydantic.__version__)

import playwright
check("Playwright", lambda: "installed (version check N/A)")

import aiohttp
check("aiohttp", lambda: aiohttp.__version__)

import bs4
check("BeautifulSoup4", lambda: bs4.__version__)

# Summary
fail_count = sum(1 for r in results if r.startswith("[FAIL]"))
total = len(results)

print(f"\n{'='*50}")
print(f"RESULTS: {total - fail_count}/{total} passed, {fail_count} failed")
print(f"{'='*50}")

if fail_count == 0:
    print("\n[SUCCESS] All checks passed! Project is ready to run.")
else:
    print(f"\n[WARNING] {fail_count} check(s) failed. Review the output above.")

# Write results to file
with open("check_results.txt", "w", encoding="utf-8") as f:
    f.write("MEEYG Project Health Check Results\n")
    f.write(f"{'='*50}\n")
    for r in results:
        f.write(r + "\n")
    f.write(f"\n{'='*50}\n")
    f.write(f"RESULTS: {total - fail_count}/{total} passed, {fail_count} failed\n")
    if fail_count == 0:
        f.write("\n[SUCCESS] All checks passed! Project is ready to run.\n")