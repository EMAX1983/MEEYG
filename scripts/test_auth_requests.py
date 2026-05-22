#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест авторизации на lk.prdveri.ru через requests"""

import requests
import re
import json

EMAIL = "montazh_centr@mail.ru"
PASSWORD = "Uf9kemNv"
BASE_URL = "https://lk.prdveri.ru"

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
})

# 1. Получаем главную страницу
print("[*] Getting main page...")
r = s.get(f"{BASE_URL}/", timeout=15)
print(f"    Status: {r.status_code}")
print(f"    URL: {r.url}")
print(f"    Title: {re.search(r'<title>([^<]+)</title>', r.text)}")

# 2. Пробуем разные API endpoint для логина
login_urls = [
    f"{BASE_URL}/api/auth/login",
    f"{BASE_URL}/api/login",
    f"{BASE_URL}/user/login",
    f"{BASE_URL}/auth/login",
    f"{BASE_URL}/login",
]

for login_url in login_urls:
    print(f"\n[*] Trying: {login_url}")
    try:
        # Сначала GET чтобы получить CSRF/cookies
        r1 = s.get(login_url, timeout=10)
        print(f"    GET status: {r1.status_code}")
        
        # Пробуем POST с JSON
        data = {"email": EMAIL, "password": PASSWORD, "username": EMAIL}
        r2 = s.post(login_url, json=data, timeout=10)
        print(f"    POST status: {r2.status_code}")
        resp_text_short = r2.text[:500]
        print(f"    Response: {resp_text_short}")
        
        if r2.status_code == 200 and len(r2.text) < 1000:
            print(f"    SUCCESS!")
            
    except Exception as e:
        print(f"    Error: {e}")

# 3. Пробуем form-data подход
print("\n[*] Trying form-data approach...")
try:
    data = {"email": EMAIL, "password": PASSWORD}
    r = s.post(f"{BASE_URL}/user/login", data=data, timeout=10, allow_redirects=True)
    print(f"    Status: {r.status_code}")
    print(f"    URL: {r.url}")
    print(f"    Title: {re.search(r'<title>([^<]+)</title>', r.text)}")
except Exception as e:
    print(f"    Error: {e}")

print("\n[*] Done")