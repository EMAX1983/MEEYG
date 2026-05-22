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