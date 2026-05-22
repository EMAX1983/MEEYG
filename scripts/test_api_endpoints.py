#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест различных API endpoints для авторизации"""

import requests

BASE = "https://lk.prdveri.ru"
EMAIL = "montazh_centr@mail.ru"
PASS = "Uf9kemNv"

endpoints = [
    "/api/v1/auth/local",
    "/api/auth/local",
    "/api/v1/auth/login",
    "/api/auth/login",
    "/api/v1/login",
    "/api/login",
    "/user/login",
]

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru-RU,ru;q=0.9',
    'Content-Type': 'application/json',
})

print("[*] Тест API endpoints...")
for ep in endpoints:
    url = BASE + ep
    try:
        resp = session.post(url, json={
            "email": EMAIL,
            "password": PASS,
            "username": EMAIL,
        }, timeout=10, allow_redirects=False)
        print(f"  {ep}: {resp.status_code} - {resp.text[:100]}")
        if resp.status_code not in (404, 500):
            print(f"    ✓ Не 404/500! Cookies: {dict(session.cookies)}")
            break
    except Exception as e:
        print(f"  {ep}: ERROR {e}")

print("\n[*] Готово!")