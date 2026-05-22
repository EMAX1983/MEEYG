#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Добавление поставщика lk.prdveri.ru с авторизацией"""

import sys
import os
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from src.database.engine import create_engine
from src.database.models import Supplier
from src.modules.parser.auth_manager import AuthManager

def main():
    print("[*] Добавление поставщика 'ЛК Пра Двери'...")
    
    engine = create_engine()
    
    with engine.begin() as conn:
        # Используем raw session
        from sqlalchemy.orm import Session
        session = Session(bind=conn)
        
        # Проверяем, существует ли уже
        existing = session.execute(
            select(Supplier).where(Supplier.name == "ЛК Пра Двери")
        ).scalar_one_or_none()
        
        if existing:
            print(f"[+] Поставщик уже существует (id={existing.id})")
            supplier = existing
        else:
            # Создаем поставщика
            supplier = Supplier(
                name="ЛК Пра Двери",
                base_url="https://lk.prdveri.ru",
                auth_url="/user/login",
                auth_username="montazh_centr@mail.ru",
                auth_password=base64.b64encode(b"Uf9kemNv").decode('utf-8'),
                auth_method="cookie",
            )
            session.add(supplier)
            session.commit()
            print(f"[+] Создан поставщик id={supplier.id}")
        
        print(f"\n[*] Тест авторизации...")
        print(f"    Base URL: {supplier.base_url}")
        print(f"    Auth URL: {supplier.auth_url}")
        print(f"    Username: {supplier.auth_username}")
        print(f"    Method: {supplier.auth_method}")
        
        # Тестируем AuthManager
        auth = AuthManager(session, supplier)
        print(f"\n[*] Запуск AuthManager.login()...")
        
        result = auth.login()
        if result:
            print(f"[!] АВТОРИЗАЦИЯ УСПЕШНА!")
            
            # Пробуем получить страницу
            try:
                resp = auth.get("/news")
                print(f"[+] GET /news status: {resp.status_code}")
                print(f"[+] URL: {resp.url}")
                print(f"[+] Title: {resp.text[:500]}")
                
                # Сохраняем HTML для анализа
                with open("D:/Projects/MEEYG 1.0/scripts/lk_logged_in.html", "w", encoding="utf-8") as f:
                    f.write(resp.text)
                print(f"[+] Saved HTML to scripts/lk_logged_in.html")
                
            except Exception as e:
                print(f"[!] Ошибка GET /news: {e}")
        else:
            print(f"[!] АВТОРИЗАЦИЯ НЕ УСПЕШНА")
            print(f"    Возможные причины:")
            print(f"    1. Неверный URL авторизации")
            print(f"    2. Неверные имя поля")
            print(f"    3. Сайт использует JavaScript-рендеринг (нужен Selenium)")
            
        auth.logout()

if __name__ == "__main__":
    main()