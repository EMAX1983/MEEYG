import sys

issues = []

# Core modules
try:
    from src.core.config import settings
    print("src.core.config: OK")
except Exception as e:
    issues.append(f"src.core.config: {e}")

try:
    from src.core.logger import logger
    print("src.core.logger: OK")
except Exception as e:
    issues.append(f"src.core.logger: {e}")

# Database
try:
    from src.database.models import Base
    print("src.database.models: OK")
except Exception as e:
    issues.append(f"src.database.models: {e}")

try:
    from src.database.session import engine
    print("src.database.session: OK")
except Exception as e:
    issues.append(f"src.database.session: {e}")

try:
    from src.database.supplier_crud import *
    print("src.database.supplier_crud: OK")
except Exception as e:
    issues.append(f"src.database.supplier_crud: {e}")

# Parsing modules
try:
    from src.modules.parsing.base_parser import BaseParser
    print("src.modules.parsing.base_parser: OK")
except Exception as e:
    issues.append(f"src.modules.parsing.base_parser: {e}")

try:
    from src.modules.parsing.engine import ParsingEngine
    print("src.modules.parsing.engine: OK")
except Exception as e:
    issues.append(f"src.modules.parsing.engine: {e}")

try:
    from src.modules.parsing.tandoor_playwright_parser import TandoorPlaywrightParser
    print("src.modules.parsing.tandoor_playwright_parser: OK")
except Exception as e:
    issues.append(f"src.modules.parsing.tandoor_playwright_parser: {e}")

# UI - skip GUI widgets, just check structure
try:
    from src.ui.pages.parsing_page import ParsingPage
    print("src.ui.pages.parsing_page: OK")
except Exception as e:
    issues.append(f"src.ui.pages.parsing_page: {e}")

try:
    from src.ui.pages.archive_page import ArchivePage
    print("src.ui.pages.archive_page: OK")
except Exception as e:
    issues.append(f"src.ui.pages.archive_page: {e}")

try:
    from src.ui.pages.discovery_page import DiscoveryPage
    print("src.ui.pages.discovery_page: OK")
except Exception as e:
    issues.append(f"src.ui.pages.discovery_page: {e}")

try:
    from src.ui.pages.export_page import ExportPage
    print("src.ui.pages.export_page: OK")
except Exception as e:
    issues.append(f"src.ui.pages.export_page: {e}")

try:
    from src.ui.pages.suppliers_page import SuppliersPage
    print("src.ui.pages.suppliers_page: OK")
except Exception as e:
    issues.append(f"src.ui.pages.suppliers_page: {e}")

try:
    from src.ui.pages.placeholder_page import PlaceholderPage
    print("src.ui.pages.placeholder_page: OK")
except Exception as e:
    issues.append(f"src.ui.pages.placeholder_page: {e}")

print("\n" + "="*50)
if issues:
    print(f"FAILED: {len(issues)} imports had issues")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("ALL_IMPORTS_SUCCESS")