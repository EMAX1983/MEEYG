#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест Selenium авторизации на lk.prdveri.ru — улучшенная версия"""

import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

EMAIL = "montazh_centr@mail.ru"
PASS = "Uf9kemNv"
URL = "https://lk.prdveri.ru/user/login"

print("[*] Запуск Selenium...")
print(f"    URL: {URL}")
print(f"    Email: {EMAIL}")

# Настройка Chrome
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(30)

try:
    print("\n[*] Переход на страницу входа...")
    driver.get(URL)
    
    # Ждём полную загрузку Vue.js
    print("    [1/6] Ожидание загрузки страницы...")
    time.sleep(8)
    
    print(f"    Текущий URL: {driver.current_url}")
    print(f"    Title: {driver.title}")
    
    # Сохраняем screenshot
    driver.save_screenshot("D:/Projects/MEEYG 1.0/scripts/lk_login_screenshot.png")
    print(f"    [✓] Сделан screenshot: lk_login_screenshot.png")
    
    # Подождём ещё для Vue hydration
    print("    [2/6] Ожидание Vue.js hydration...")
    time.sleep(5)
    
    # Выведем HTML для отладки
    html = driver.page_source
    with open("D:/Projects/MEEYG 1.0/scripts/lk_selenium_debug.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    # Посчитаем input elements
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"    [3/6] Найдено input элементов: {len(inputs)}")
    for i, inp in enumerate(inputs):
        try:
            inp_type = inp.get_attribute("type")
            inp_id = inp.get_attribute("id")
            inp_name = inp.get_attribute("name")
            print(f"        input[{i}]: type={inp_type}, id={inp_id}, name={inp_name}")
        except:
            pass
    
    # Попробуем через JavaScript найти и заполнить поля
    print("    [4/6] Заполнение полей через JavaScript...")
    
    # Найдем все input и заполним их
    result = driver.execute_script("""
        var inputs = document.querySelectorAll('input');
        var emailInput = null;
        var passInput = null;
        for (var i = 0; i < inputs.length; i++) {
            var t = inputs[i].getAttribute('type');
            if (t === 'email' || t === 'text') {
                if (!emailInput) emailInput = inputs[i];
            }
            if (t === 'password') {
                passInput = inputs[i];
            }
        }
        return JSON.stringify({
            total: inputs.length,
            emailInput: emailInput ? emailInput.outerHTML.substring(0, 200) : null,
            passInput: passInput ? passInput.outerHTML.substring(0, 200) : null
        });
    """)
    print(f"    JS Result: {result}")
    
    # Заполняем через focus + sendKeys (работает с Vuetify лучше)
    try:
        print("    [5/6] Заполнение email...")
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        for inp in all_inputs:
            t = inp.get_attribute("type")
            if t == "email" or (t is None):
                inp.click()
                time.sleep(0.5)
                inp.send_keys(EMAIL)
                print(f"        [✓] Введён email в input[type={t}]")
                break
        
        print("    [5/6] Заполнение password...")
        for inp in all_inputs:
            t = inp.get_attribute("type")
            if t == "password":
                inp.click()
                time.sleep(0.5)
                inp.send_keys(PASS)
                print(f"        [✓] Введён пароль")
                break
    except Exception as e:
        print(f"    [!] Ошибка заполнения: {e}")
    
    # Клик по кнопке Войти
    print("    [6/6] Клик по кнопке Войти...")
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            text = btn.text.strip()
            if "Войти" in text or "войти" in text.lower():
                driver.execute_script("arguments[0].click();", btn)
                print(f"        [✓] Клик по кнопке: '{text}'")
                break
    except Exception as e:
        print(f"    [!] Ошибка клика: {e}")
    
    # Ждём результат
    print("\n    Ожидание результата авторизации...")
    time.sleep(10)
    
    print(f"\n[*] После авторизации:")
    print(f"    URL: {driver.current_url}")
    print(f"    Title: {driver.title}")
    
    # Скриншот после
    driver.save_screenshot("D:/Projects/MEEYG 1.0/scripts/lk_after_login.png")
    
    # Cookies
    cookies = driver.get_cookies()
    auth_cookies = [c for c in cookies if 'token' in c['name'].lower() or 'jwt' in c['name'].lower() or 'session' in c['name'].lower()]
    print(f"\n[*] Cookies ({len(cookies)} всего, {len(auth_cookies)} auth):")
    for c in cookies:
        val = c['value'][:50] + "..." if len(c['value']) > 50 else c['value']
        print(f"    {c['name']} = {val}")
    
    # HTML после авторизации
    html2 = driver.page_source
    with open("D:/Projects/MEEYG 1.0/scripts/lk_selenium_after.html", "w", encoding="utf-8") as f:
        f.write(html2)
    
    # Проверяем результат
    if "/news" in driver.current_url or "/dashboard" in driver.current_url or "/catalog" in driver.current_url:
        print(f"\n[!] АВТОРИЗАЦИЯ УСПЕШНА!")
    elif "/login" in driver.current_url or "/auth" in driver.current_url:
        print(f"\n[!] АВТОРИЗАЦИЯ НЕ УСПЕШНА — всё ещё на login/auth странице")
        # Проверяем, есть ли ошибка
        try:
            error_el = driver.find_element(By.CSS_SELECTOR, '.v-alert--error, .v-snackbar--error')
            print(f"    Ошибка: {error_el.text}")
        except:
            pass
    else:
        print(f"\n[?] Неизвестный URL: {driver.current_url}")

except Exception as e:
    print(f"\n[!] ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    driver.save_screenshot("D:/Projects/MEEYG 1.0/scripts/lk_error.png")

finally:
    driver.quit()
    print("\n[*] Browser closed.")