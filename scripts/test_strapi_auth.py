#!/usr/bin/env python
# -*- coding: utf-8 */
"""Тест авторизации - предположение что это Strapi или similar"""

import requests
import json

BASE = "https://lk.prdveri.ru"
EMAIL = "montazh_centr@mail.ru"
PASS = "Uf9kemNv"

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
    'Accept-Language': 'ru-RU,ru;q=0.9',
})

# Пробуем разные варианты
tests = [
    # Strapi
    ("/api/auth/local", {"identifier": EMAIL, "password": PASS}),
    ("/api/v1/auth/local", {"identifier": EMAIL, "password": PASS}),
    # Стандартный
    ("/user/login", {"username": EMAIL, "password": PASS}),
    ("/api/login", {"username": EMAIL, "password": PASS}),
    ("/api/v1/login", {"username": EMAIL, "password": PASS}),
    # Nuxt Auth
    ("/auth/local", {"username": EMAIL, "password": PASS}),
    ("/api/auth/login", {"email": EMAIL, "password": PASS}),
    ("/api/v1/auth/login", {"email": EMAIL, "password": PASS}),
    # Попробовать с email как identifier
    ("/api/auth/local", {"email": EMAIL, "password": PASS}),
]

print("[*] Тест авторизации...")
for path, data in tests:
    url = BASE + path
    try:
        resp = s.post(url, json=data, timeout=10, allow_redirects=False)
        status = resp.status_code
        body = resp.text[:200]
        cookies = dict(s.cookies)
        
        marker = "✓" if status not in (404, 500, 401) else " "
        print(f"  [{marker}] POST {path}: {status}")
        print(f"       Body: {body}")
        if cookies:
            print(f"       Cookies: {cookies}")
        
        if status == 200 or (cookies and 'jwt' in str(cookies).lower()):
            print(f"\n[!] УСПЕХ! {path}")
            break
    except Exception as e:
        print(f"  [ ] POST {path}: ERROR {e}")

# Попробуем form-based (не JSON)
print("\n[*] Form-based авторизация...")
s2 = requests.Session()
s2.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

# Сначала GET login page для CSRF
try:
    r = s2.get(BASE + "/user/login", timeout=10)
    print(f"  GET /user/login: {r.status_code}")
    print(f"  Cookies after GET: {dict(s2.cookies)}")
    
    # Ищем CSRF в HTML
    import re
    csrf = re.search(r'name="_csrf"\s+value="([^"]+)"', r.text)
    if csrf:
        print(f"  Found CSRF: {csrf.group(1)[:20]}...")
    
    # Form POST
    form_data = {
        "email": EMAIL,
        "password": PASS,
    }
    if csrf:
        form_data["_csrf"] = csrf.group(1)
    
    r2 = s2.post(BASE + "/user/login", data=form_data, timeout=10, allow_redirects=True)
    print(f"  POST /user/login: {r2.status_code}")
    print(f"  Final URL: {r2.url}")
    print(f"  Cookies after POST: {dict(s2.cookies)}")
    
    if "/news" in r2.url or "/dashboard" in r2.url:
        print(f"\n[!] АВТОРИЗАЦИЯ УСПЕШНА после redirect!")
        # Сохраняем HTML
        with open("D:/Projects/MEEYG 1.0/scripts/lk_logged_in_form.html", "w", encoding="utf-8") as f:
            f.write(r2.text)
        print(f"  [!] Saved HTML: lk_logged_in_form.html")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n[*] Готово!")