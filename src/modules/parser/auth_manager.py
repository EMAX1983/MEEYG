#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AuthManager — модуль управления авторизацией для парсера поставщиков.

Поддерживает cookie-based авторизацию:
- Логин через POST-запрос с формой
- Сохранение cookies в сессии
- Автопереавторизация при истечении сессии
- Base64 шифрование пароля в БД
"""

import base64
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import requests
from sqlalchemy.orm import Session

from src.database.models import Supplier
from src.core.logger import logger


class AuthManager:
    """Управляет авторизацией для парсера поставщиков."""
    
    def __init__(self, db_session: Session, supplier: Supplier):
        """
        Args:
            db_session: SQLAlchemy сессия
            supplier: Объект поставщика из БД
        """
        self.session = db_session
        self.supplier = supplier
        self.base_url = supplier.base_url.rstrip("/")
        
        # HTTP-сессия с cookies
        self.http = requests.Session()
        self.http.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        self._is_authenticated = False
        self._last_auth_time = None
        
    @property
    def auth_url(self) -> Optional[str]:
        """URL для авторизации."""
        if self.supplier.auth_url:
            return urljoin(self.base_url, self.supplier.auth_url)
        return None
    
    @property
    def username(self) -> Optional[str]:
        """Логин (извлекается из БД)."""
        return self.supplier.auth_username
    
    @property
    def password(self) -> Optional[str]:
        """Пароль (декодируется из Base64)."""
        if self.supplier.auth_password:
            try:
                return base64.b64decode(self.supplier.auth_password).decode('utf-8')
            except Exception as e:
                logger.error(f"Не удалось декодировать пароль для {self.supplier.name}: {e}")
                return None
        return None
    
    @property
    def auth_method(self) -> str:
        """Метод авторизации (cookie по умолчанию)."""
        return self.supplier.auth_method or "cookie"
    
    def encode_password(self, password: str) -> str:
        """Кодирует пароль в Base64 для хранения в БД."""
        return base64.b64encode(password.encode('utf-8')).decode('utf-8')
    
    def login(self, max_retries: int = 2) -> bool:
        """
        Выполняет авторизацию на сайте поставщика.
        
        Поддерживает 2 режима:
        1. Form auth: POST на HTML-login с формой (data=login_data)
        2. API auth (Nuxt.js): POST на /api/v1/auth/local с JSON
        
        Args:
            max_retries: Количество повторных попыток
            
        Returns:
            True если авторизация успешна, False иначе
        """
        if not self.auth_url:
            logger.warning(f"Нет auth_url для поставщика {self.supplier.name}")
            return False
        
        if not self.username or not self.password:
            logger.warning(f"Нет логина/пароля для поставстера {self.supplier.name}")
            return False
        
        for attempt in range(max_retries):
            try:
                logger.info(f"[{self.supplier.name}] Попытка авторизации ({attempt + 1}/{max_retries})...")
                
                # 1. Пробуем API авторизацию (для Nuxt.js SPA)
                # Nuxt Auth local strategy: POST /api/v1/auth/local
                api_auth_url = self.auth_url.replace('/user/login', '/api/v1/auth/local')
                try:
                    # Сначала сбрасываем cookies для чистого теста
                    self.http.cookies.clear()
                    
                    api_resp = self.http.post(
                        api_auth_url,
                        json={
                            "email": self.username,
                            "password": self.password,
                            "username": self.username,
                        },
                        timeout=30,
                        allow_redirects=False
                    )
                    
                    logger.debug(f"API POST {api_auth_url}: {api_resp.status_code}")
                    logger.debug(f"Response: {api_resp.text[:200]}")
                    
                    # Успешная авторизация? Проверяем cookies или token
                    if self.http.cookies:
                        if self._check_auth_success(api_resp):
                            self._is_authenticated = True
                            self._last_auth_time = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
                            logger.info(f"[{self.supplier.name}] Авторизация успешна (API)!")
                            return True
                    
                    # Если API не сработал, пробуем form auth
                except requests.RequestException as e:
                    logger.debug(f"API авторизация не удалась: {e}")
                
                # 2. Пробуем Form-авторизацию (классический HTML login)
                self.http.cookies.clear()
                
                # GET для получения cookies/CSRF
                get_resp = self.http.get(self.auth_url, timeout=30)
                logger.debug(f"GET {self.auth_url}: {get_resp.status_code}")
                
                # POST с form data
                login_data = {
                    "email": self.username,
                    "password": self.password,
                    "_locale": "ru",
                }
                
                post_resp = self.http.post(
                    self.auth_url, 
                    data=login_data,
                    timeout=30,
                    allow_redirects=True
                )
                
                logger.debug(f"POST {self.auth_url}: {post_resp.status_code}")
                logger.debug(f"Final URL: {post_resp.url}")
                
                # Проверяем результат
                if self._check_auth_success(post_resp):
                    self._is_authenticated = True
                    self._last_auth_time = __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
                    logger.info(f"[{self.supplier.name}] Авторизация успешна!")
                    return True
                
                logger.warning(f"[{self.supplier.name}] Авторизация не удалась (status={post_resp.status_code})")
                
            except requests.RequestException as e:
                logger.error(f"[{self.supplier.name}] Ошибка при авторизации: {e}")
                
        logger.error(f"[{self.supplier.name}] Не удалось авторизоваться после {max_retries} попыток")
        return False
    
    def logout(self) -> None:
        """Завершает сессию (очищает cookies)."""
        self.http.cookies.clear()
        self._is_authenticated = False
        self._last_auth_time = None
        logger.info(f"[{self.supplier.name}] Сессия завершена")
    
    def _check_auth_success(self, response: requests.Response) -> bool:
        """
        Проверяет успешность авторизации.
        
        Критерии:
        - Нет редиректа на /login
        - Страница не содержит форму входа
        - Статус 200
        """
        if response.status_code in (401, 403):
            return False
        
        # Если редирект на login-страницу — не авторизован
        current_url = response.url.lower()
        if '/login' in current_url or '/auth' in current_url:
            # Но если это финальная страница (не редирект), то проверяем содержимое
            if 'Вход' not in response.text and 'Password' not in response.text and 'password' not in response.text.lower():
                # Возможно, это страница "вы вошли"
                pass
            else:
                return False
        
        # Проверяем, нет ли формы входа на странице
        forms_count = response.text.lower().count('<form')
        if forms_count > 0 and ('password' in response.text.lower() or 'login' in response.text.lower()):
            # Проверяем, что это не просто страница с формой входа
            if 'welcome' in response.text.lower() or 'dashboard' in response.text.lower():
                return True
            # Если есть только форма без welcome — возможно не залогинен
            if forms_count == 1 and 'Вход' in response.text:
                return False
                
        return response.status_code == 200
    
    def get(self, url: str, params: dict = None, headers: dict = None, 
            timeout: int = 30, **kwargs) -> requests.Response:
        """
        Выполняет GET-запрос с авторизацией.
        Если сессия не активна — авторизуется автоматически.
        """
        if not self._is_authenticated:
            if not self.login():
                raise RuntimeError(f"Не удалось авторизоваться для {self.supplier.name}")
        
        resp = self.http.get(
            url if url.startswith('http') else urljoin(self.base_url, url),
            params=params,
            headers=headers,
            timeout=timeout,
            **kwargs
        )
        
        # Если 401/403 — пробуем переавторизоваться
        if resp.status_code in (401, 403):
            self.logout()
            if not self.login():
                raise RuntimeError(f"Переавторизация не удалась для {self.supplier.name}")
            resp = self.http.get(
                url if url.startswith('http') else urljoin(self.base_url, url),
                params=params,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
        
        resp.raise_for_status()
        return resp
    
    def post(self, url: str, data: dict = None, json: dict = None,
             headers: dict = None, timeout: int = 30, **kwargs) -> requests.Response:
        """Выполняет POST-запрос с авторизацией."""
        if not self._is_authenticated:
            if not self.login():
                raise RuntimeError(f"Не удалось авторизоваться для {self.supplier.name}")
        
        resp = self.http.post(
            url if url.startswith('http') else urljoin(self.base_url, url),
            data=data,
            json=json,
            headers=headers,
            timeout=timeout,
            **kwargs
        )
        
        if resp.status_code in (401, 403):
            self.logout()
            if not self.login():
                raise RuntimeError(f"Переавторизация не удалась для {self.supplier.name}")
            resp = self.http.post(
                url if url.startswith('http') else urljoin(self.base_url, url),
                data=data,
                json=json,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
        
        resp.raise_for_status()
        return resp