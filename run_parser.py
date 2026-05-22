
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

        # Initialize the parser (session передаётся в метод run(), а не в конструктор)
        parser = TandoorPlaywrightParser(
            supplier_id=supplier.id,
            headless=True,
            log_callback=lambda msg: log.info(f"[Parser] {msg}")
        )

        try:
            log.info("Начало парсинга одного товара...")
            # Async call
            results = await parser.run(session, urls=[target_product_url])
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
