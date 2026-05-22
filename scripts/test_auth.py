#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест авторизации на lk.prdberi.ru через Selenium"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Логин/пароль
EMAIL = "montazh_centr@mail.ru"
PASSWORD = "Uf9kemNv"
BASE_URL = "https://lk.prdberi.ru"

# Настройки Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=options)

try:
    print(f"[*] Opening {BASE_URL}/news...")
    driver.get(f"{BASE_URL}/news")
    time.sleep(3)
    
    print(f"Title: {driver.title}")
    print(f"URL: {driver.current_url}")
    
    # Проверяем, залогинены ли уже
    if "login" in driver.current_url.lower():
        print("[*] Need to login...")
        
        # Ищем форму входа
        try:
            # Пробуем найти input email
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"], input[name="email"], input[placeholder*="email" i], input[placeholder*="@mail" i]'))
            )
            print(f"[*] Found email input: {email_input}")
            
            # Вводим email
            email_input.clear()
            email_input.send_keys(EMAIL)
            print(f"[*] Entered email: {EMAIL}")
            
            time.sleep(1)
            
            # Ищем пароль
            password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            password_input.clear()
            password_input.send_keys(PASSWORD)
            print("[*] Entered password")
            
            time.sleep(1)
            
            # Ищем кнопку входа
            login_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], button:contains("Войти"), button:contains("Login")')
            print(f"[*] Found login button: {login_btn}")
            
            login_btn.click()
            print("[*] Clicked login button")
            
            # Ждем редиректа
            time.sleep(5)
            
            print(f"[+] After login URL: {driver.current_url}")
            print(f"[+] After login Title: {driver.title}")
            
            # Получаем cookies
            cookies = driver.get_cookies()
            print(f"\n[*] Got {len(cookies)} cookies:")
            for c in cookies:
                print(f"  {c['name']}: {c['value'][:50]}...")
                
        except Exception as e:
            print(f"[!] Error during login: {e}")
            
            # Сохраняем скриншот и HTML для анализа
            driver.save_screenshot("D:/Projects/MEEYG 1.0/scripts/login_page.png")
            with open("D:/Projects/MEEYG 1.0/scripts/login_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("[!] Saved screenshot and HTML for analysis")
            
    else:
        print("[+] Already logged in!")
        cookies = driver.get_cookies()
        print(f"[*] Got {len(cookies)} cookies")
        
finally:
    driver.quit()
    print("\n[*] Done")