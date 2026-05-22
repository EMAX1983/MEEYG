
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
