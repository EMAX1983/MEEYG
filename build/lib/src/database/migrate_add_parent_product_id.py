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
