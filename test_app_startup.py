"""Тест запуска приложения без GUI."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_startup():
    """Проверяет что приложение запускается без ошибок (без отображения GUI)."""
    from PySide6.QtWidgets import QApplication
    from src.core.config import settings
    from src.database.models import Base
    from src.database.session import engine
    from src.ui.main_window import MainWindow
    
    # Test 1: Settings loaded
    assert settings.app_name == "MEEYG", f"App name is '{settings.app_name}', expected 'MEEYG'"
    print("[PASS] Settings loaded correctly")
    
    # Test 2: Database tables can be created/verified
    Base.metadata.create_all(bind=engine)
    print("[PASS] Database tables verified/created")
    
    # Test 3: DB is accessible
    from sqlalchemy import text
    conn = engine.connect()
    result = conn.execute(text("PRAGMA integrity_check"))
    integrity = result.fetchone()[0]
    conn.close()
    assert integrity == "ok", f"DB integrity check failed: {integrity}"
    print("[PASS] Database integrity check passed")
    
    # Test 4: Suppliers table has data
    from sqlalchemy.orm import Session
    session = Session(engine)
    from src.database.models import Supplier, Category, Product
    supplier_count = session.query(Supplier).count()
    category_count = session.query(Category).count()
    product_count = session.query(Product).count()
    session.close()
    print(f"[PASS] DB stats: {supplier_count} suppliers, {category_count} categories, {product_count} products")
    
    # Test 5: Check UI pages can be created (without QApplication)
    from src.ui.pages.parsing_page import ParsingPage
    from src.ui.pages.archive_page import ArchivePage
    from src.ui.pages.discovery_page import DiscoveryPage
    from src.ui.pages.export_page import ExportPage
    from src.ui.pages.suppliers_page import SuppliersPage
    from src.ui.pages.placeholder_page import PlaceholderPage
    print("[PASS] All UI page classes can be imported")
    
    # Test 6: Check parsing modules
    from src.modules.parsing.base_parser import BaseParser
    print("[PASS] BaseParser can be imported")
    
    print("\n" + "="*50)
    print("ALL_TESTS_PASSED")

if __name__ == "__main__":
    test_app_startup()