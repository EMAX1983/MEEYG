#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Тест авторизации на lk.prdberi.ru"""

import requests
from urllib.parse import urljoin
import re

s = requests.Session()
base_url = 'https://lk.prdberi.ru'

# Получаем главную страницу
r = s.get('https://lk.prdberi.ru/', timeout=10)
print(f"Status: {r.status_code}")
print(f"URL: {r.url}")
print(f"Content length: {len(r.text)}")

# Ищем любые input с типом password, email, text
inputs = re.findall(r'<input[^>]*>', r.text, re.IGNORECASE)
print(f"\nFound {len(inputs)} input elements:")
for inp in inputs[:30]:
    name = re.search(r'name=["\']([^"\']*)["\']', inp, re.IGNORECASE)
    type_attr = re.search(r'type=["\']([^"\']*)["\']', inp, re.IGNORECASE)
    placeholder = re.search(r'placeholder=["\']([^"\']*)["\']', inp, re.IGNORECASE)
    print(f"  type={type_attr.group(1) if type_attr else 'N/A'}, name={name.group(1) if name else 'N/A'}, placeholder={placeholder.group(1) if placeholder else 'N/A'}")

# Ищем формы
forms = re.findall(r'<form[^>]*>', r.text, re.IGNORECASE)
print(f"\nFound {len(forms)} form elements:")
for form in forms:
    action = re.search(r'action=["\']([^"\']*)["\']', form, re.IGNORECASE)
    method = re.search(r'method=["\']([^"\']*)["\']', form, re.IGNORECASE)
    print(f"  action={action.group(1) if action else 'N/A'}, method={method.group(1) if method else 'N/A'}")

# Сохраняем HTML для анализа
with open('D:/Projects/MEEYG 1.0/scripts/lk_page.html', 'w', encoding='utf-8') as f:
    f.write(r.text)
print("\nSaved HTML to scripts/lk_page.html")