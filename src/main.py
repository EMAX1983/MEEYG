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
