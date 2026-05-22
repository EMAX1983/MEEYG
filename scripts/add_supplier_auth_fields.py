#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Миграция: Добавление полей авторизации в таблицу suppliers"""

import sys
import os

# Добавляем корень проекта в path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from src.database.engine import create_engine
from src.database.models import Base

def run_migration():
    print("[*] Migrating: Добавление полей авторизации в suppliers...")
    
    engine = create_engine()
    
    # Для SQLite используем simpler подход
    fields = [
        ("auth_url", "TEXT DEFAULT NULL"),
        ("auth_username", "TEXT DEFAULT NULL"),
        ("auth_password", "TEXT DEFAULT NULL"),
        ("auth_method", "TEXT DEFAULT 'cookie'"),
        ("auth_token", "TEXT DEFAULT NULL"),
    ]
    
    with engine.connect() as conn:
        for field_name, field_def in fields:
            # Для SQLite проверяем через PRAGMA
            result = conn.execute(text(f"PRAGMA table_info(suppliers)"))
            columns = [row[1] for row in result.fetchall()]
            
            if field_name in columns:
                print(f"  [⚠] Колонка '{field_name}' уже существует — пропускаем")
            else:
                conn.execute(text(
                    f"ALTER TABLE suppliers ADD COLUMN {field_name} {field_def}"
                ))
                conn.commit()
                print(f"  [+] Добавлена колонка '{field_name}'")
    
    print("\n[*] Migration complete!")

if __name__ == "__main__":
    run_migration()
