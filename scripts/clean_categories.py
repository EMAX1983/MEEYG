#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧹 Скрипт очистки таблицы категорий MEEYG 1.0
Используется для сброса данных перед повторным запуском модуля "Разведка".
"""
import os
import sqlcipher3 as sqlite3

# 📍 Пути и ключ
PROJECT_ROOT = r"D:\Projects\MEEYG 1.0"
DB_PATH = os.path.join(PROJECT_ROOT, "data", "meeyg.db")
DB_KEY = "82baec464414deb5fb7805afff26c24f0df011e75ec75430cfa79da55003674d"

def clean_categories():
    if not os.path.exists(DB_PATH):
        print(f"❌ Файл БД не найден по пути: {DB_PATH}")
        return

    print("🔐 Подключение к зашифрованной БД...")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(f"PRAGMA key = '{DB_KEY}'")

        # 1. Проверка валидности ключа
        version = conn.execute("PRAGMA cipher_version").fetchone()
        if not version:
            raise sqlite3.DatabaseError("Неверный ключ шифрования или файл повреждён.")
        print(f"✅ Ключ принят. SQLCipher: {version[0]}")

        # 2. Подсчёт записей перед удалением
        count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        print(f"📊 Найдено категорий в БД: {count}")

        if count == 0:
            print("⚠️ Таблица 'categories' уже пуста. Очистка не требуется.")
            return

        # 3. Удаление данных
        print("🗑️ Выполняется удаление...")
        conn.execute("DELETE FROM categories")
        conn.commit()
        
        print(f"✅ Успешно удалено {count} записей.")
        print(" Готово! Можно запускать новую разведку.")

    except sqlite3.DatabaseError as e:
        print(f"❌ Ошибка SQLCipher (проверьте ключ/файл): {e}")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    clean_categories()