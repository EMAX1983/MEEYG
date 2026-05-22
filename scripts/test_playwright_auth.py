#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест Playwright авторизации на lk.prdveri.ru"""

import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from playwright.sync_api import sync_playwright

EMAIL = "montazh_centr@mail.ru"
PASS = "Uf9kemNv"
URL = "https://lk.prdveri.ru/user/login"

print("[*] Запуск Playwright...")
print(f"    URL: {URL}")
print(f"    Email: {EMAIL}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--no-sandbox"])
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    page = context.new_page()
    
    try:
        print("\n[*] Переход на страницу входа...")
        page.goto(URL, wait_until="networkidle", timeout=30000)
        
        print(f"    URL: {page.url}")
        print(f"    Title: {page.title()}")
        
        # Скриншот
        page.screenshot(path="D:/Projects/MEEYG 1.0/scripts/lk_pw_login.png")
        print("    [✓] Screenshot: lk_pw_login.png")
        
        # Посчитаем input элементы
        inputs = page.query_selector_all("input")
        print(f"\n    Найдено input элементов: {len(inputs)}")
        for i, inp in enumerate(inputs):
            try:
                t = inp.get_attribute("type")
                inp_id = inp.get_attribute("id")
                placeholder = inp.get_attribute("placeholder")
                print(f"        input[{i}]: type={t}, id={inp_id}, placeholder={placeholder}")
            except:
                pass
        
        # Попробуем найти поля по разным селекторам
        print("\n[1] Пробуем найти email input...")
        
        # Вариант 1: по type
        email_input = page.query_selector('input[type="email"]')
        if email_input:
            print("    [✓] Найден по type=email")
        else:
            # Вариант 2: по vuetify class
            email_input = page.query_selector('.v-field__input input')
            if email_input:
                print("    [✓] Найден по .v-field__input input")
            else:
                # Вариант 3: по placeholder
                email_input = page.query_selector('input[placeholder*="почта"]')
                if email_input:
                    print("    [✓] Найден по placeholder")
                else:
                    # Вариант 4: первый input
                    email_input = page.query_selector('input')
                    if email_input:
                        print("    [✓] Найден первый input")
        
        print("\n[2] Пробуем найти password input...")
        pass_input = page.query_selector('input[type="password"]')
        if not pass_input:
            pass_input = page.query_selector('.v-field__input input[type="password"]')
        if pass_input:
            print("    [✓] Найден password input")
        
        if email_input and pass_input:
            print("\n[3] Заполняем поля...")
            email_input.click()
            email_input.fill(EMAIL)
            print(f"    [✓] Email: {EMAIL}")
            
            pass_input.click()
            pass_input.fill(PASS)
            print(f"    [✓] Password: ****")
            
            print("\n[4] Нажимаем кнопку Войти...")
            # Ищем кнопку
            btn = page.get_by_role("button", name="Войти")
            if btn:
                btn.click()
                print("    [✓] Клик по 'Войти'")
            else:
                # Submit form
                page.evaluate('''() => {
                    var form = document.querySelector('form');
                    if (form) form.requestSubmit();
                }''')
                print("    [✓] Form submit")
            
            print("\n[5] Ожидаем результат...")
            try:
                page.wait_for_url("**/news**", timeout=15000)
                print(f"    [!] Успешный редирект на: {page.url}")
            except:
                print(f"    URL: {page.url}")
            
            # Скриншот после
            page.screenshot(path="D:/Projects/MEEYG 1.0/scripts/lk_pw_after.png")
            print("    [✓] Screenshot: lk_pw_after.png")
            
            # Cookies
            cookies = context.cookies()
            print(f"\n[*] Cookies ({len(cookies)}):")
            for c in cookies:
                val = c['value'][:50] + "..." if len(c['value']) > 50 else c['value']
                print(f"    {c['name']} = {val}")
            
            # Результат
            if "/news" in page.url or "/dashboard" in page.url:
                print(f"\n[!] АВТОРИЗАЦИЯ УСПЕШНА!")
            else:
                print(f"\n[?] URL: {page.url}")
        else:
            print("\n[!] Не найдены поля ввода!")
            # Сохраним HTML
            html = page.content()
            with open("D:/Projects/MEEYG 1.0/scripts/lk_pw_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("    [✓] HTML сохранён: lk_pw_debug.html")
    
    except Exception as e:
        print(f"\n[!] ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="D:/Projects/MEEYG 1.0/scripts/lk_pw_error.png")
    
    finally:
        browser.close()
        print("\n[*] Browser closed.")