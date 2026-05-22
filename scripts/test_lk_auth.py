#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест авторизации на lk.prdveri.ru - исправленный URL"""

import sys
import os
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select, update

from src.database.engine import create_engine
from src.database.models import Supplier
from src.modules.parser.auth_manager import AuthManager

def main():
    print("[*] Тест авторизации на lk.prdveri.ru...")
    
    engine = create_engine()
    
    with engine.begin() as conn:
        from sqlalchemy.orm import Session
        session = Session(bind=conn)
        
        # Обновляем URL у поставщика
        session.execute(
            update(Supplier)
            .where(Supplier.name == "ЛК Пра Двери")
            .values(base_url="https://lk.prdveri.ru")
        )
        session.commit()
        
        # Получаем поставщика
        supplier = session.execute(
            select(Supplier).where(Supplier.name == "ЛК Пра Двери")
        ).scalar_one_or_none()
        
        if not supplier:
            print("[!] Поставщик не найден")
            return
        
        print(f"    Base URL: {supplier.base_url}")
        print(f"    Auth URL: {supplier.auth_url}")
        print(f"    Username: {supplier.auth_username}")
        
        # Тестируем AuthManager
        auth = AuthManager(session, supplier)
        result = auth.login()
        
        if result:
            print(f"\n[!] АВТОРИЗАЦИЯ УСПЕШНА!")
            
            # Пробуем получить страницу
            resp = auth.get("/news")
            print(f"[+] GET /news status: {resp.status_code}")
            print(f"[+] URL: {resp.url}")
            
            with open("D:/Projects/MEEYG 1.0/scripts/lk_logged_in.html", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"[+] Saved HTML to scripts/lk_logged_in.html")
            
        else:
            print(f"\n[!] АВТОРИЗАЦИЯ НЕ УСПЕШНА")
            
            # Сохраняем debug
            import requests
            s = requests.Session()
            r = s.get("https://lk.prdveri.ru/", timeout=10)
            with open("D:/Projects/MEEYG 1.0/scripts/lk_main_page.html", "w", encoding="utf-8") as f:
                f.write(r.text)
            print(f"[+] Saved main page HTML")
            
        auth.logout()

if __name__ == "__main__":
    main()