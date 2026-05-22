#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Миграция: добавляет новые поля в archive_items для полного экспорта товаров."""

import os
import sys
import logging
from pathlib import Path

from sqlalchemy import text
from dotenv import load_dotenv

# Добавить корень проекта в path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.session import engine, get_session

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

NEW_COLUMNS = [
    ("manufacturer", "TEXT DEFAULT NULL"),
    ("parent_sku", "TEXT DEFAULT NULL"),
    ("collection", "TEXT DEFAULT NULL"),
    ("brand", "TEXT DEFAULT NULL"),
    ("availability", "TEXT DEFAULT NULL"),
    ("stock_status", "TEXT DEFAULT NULL"),
    ("vendor", "TEXT DEFAULT NULL"),
    ("description", "TEXT DEFAULT NULL"),
    ("is_parent", "INTEGER DEFAULT 0"),
]


def needs_migration() -> bool:
    """Проверяет, нужны ли новые колонки."""
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(archive_items)"))
        existing_cols = {row[1] for row in result}
        for col_name, _ in NEW_COLUMNS:
            if col_name not in existing_cols:
                return True
    return False


def run_migration():
    """Выполняет миграцию."""
    with engine.connect() as conn:
        for col_name, col_def in NEW_COLUMNS:
            result = conn.execute(text("PRAGMA table_info(archive_items)"))
            existing_cols = {row[1] for row in result}
            
            if col_name not in existing_cols:
                sql = f"ALTER TABLE archive_items ADD COLUMN {col_name} {col_def}"
                logger.info(f"  → Добавляю колонку: {col_name}")
                try:
                    conn.execute(text(sql))
                    conn.commit()
                    logger.info(f"    ✅ Колонка {col_name} добавлена")
                except Exception as e:
                    logger.error(f"    ❌ Ошибка добавления {col_name}: {e}")
                    conn.rollback()
            else:
                logger.info(f"  ✓ Колонка {col_name} уже существует")


def verify():
    """Проверяет результат миграции."""
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(archive_items)"))
        cols = {row[1] for row in result}
        
        expected = {"snapshot_id", "product_id", "external_sku", "title", 
                   "price", "currency", "is_available", "category_name",
                   "image_urls", "attributes_json", "created_at"}
        expected.update({c[0] for c in NEW_COLUMNS})
        
        missing = expected - cols
        if missing:
            logger.error(f"❌ Найдены недостающие колонки: {missing}")
            return False
        else:
            logger.info(f"✅ Все {len(cols)} колонок в archive_items присутствуют")
            return True


def main():
    from src.database.models import Base
    
    logger.info("🔄 Миграция archive_items: добавление колонок для экспорта")
    logger.info("=" * 60)
    
    # 1. Создаём таблицы (если их нет) для получения схемы
    logger.info("1. Проверяем/создаём таблицы...")
    Base.metadata.create_all(bind=engine)
    
    # 2. Проверяем, нужна ли миграция
    if not needs_migration():
        logger.info("2. Миграция не требуется — все колонки уже существуют ✅")
        verify()
        return
    
    # 3. Запускаем миграцию
    logger.info("2. Запускаем миграцию...")
    run_migration()
    
    # 4. Проверяем результат
    logger.info("3. Проверяем результат...")
    if verify():
        logger.info("\n✅ Миграция завершена успешно!")
    else:
        logger.error("\n❌ Миграция завершилась с ошибками")
        sys.exit(1)


if __name__ == "__main__":
    load_dotenv()
    main()