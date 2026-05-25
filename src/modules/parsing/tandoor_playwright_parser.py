"""
Продвинутый Playwright-парсер для tandoor.ru с мерами обхода защиты.
Наследуется от BaseParser.
"""

import asyncio
import itertools
import json
import os
import random
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin
import io

import aiohttp
from PIL import Image

from bs4 import BeautifulSoup
from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    TimeoutError as PlaywrightTimeoutError,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.modules.parsing.base_parser import BaseParser, ParsedProduct
from src.database.models import (
    Product,
    ProductAttribute,
    Supplier,
    Category,
)

# --- Константы для обхода защиты ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:125.0) Gecko/20100101 Firefox/125.0",
]

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
Object.defineProperty(navigator, 'languages', { get: () => ['ru-RU', 'ru', 'en-US', 'en'] });
"""


class TandoorPlaywrightParser(BaseParser):
    def __init__(self, debug_mode: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.debug_mode = debug_mode
        self.user_data_dir = os.path.join("./pw_user_data", f"supplier_{self.supplier_id}")
        self._category_cache: Dict[str, int] = {}
        self.base_url = "https://tandoor.ru"
        self._sku_counter = 0  # Global SKU counter

        os.makedirs(self.user_data_dir, exist_ok=True)
        if self.debug_mode:
            os.makedirs("./screenshots", exist_ok=True)
    
    async def _download_image_bytes(self, session: aiohttp.ClientSession, url: str) -> Optional[bytes]:
        """Скачивает изображение по URL и возвращает байты."""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    return await response.read()
        except Exception as e:
            if self.debug_mode:
                print(f"[WARN] Не удалось скачать изображение {url}: {e}")
        return None
    
    async def _merge_two_images_horizontally(self, img1_bytes: bytes, img2_bytes: bytes, gap: int = 10) -> bytes:
        """
        Объединяет два изображения горизонтально с отступом.
        Возвращает байты JPEG изображения.
        """
        try:
            img1 = Image.open(io.BytesIO(img1_bytes)).convert("RGBA")
            img2 = Image.open(io.BytesIO(img2_bytes)).convert("RGBA")
            
            # Приводим к одной высоте (по максимальному)
            h1, w1 = img1.size[1], img1.size[0]
            h2, w2 = img2.size[1], img2.size[0]
            max_h = max(h1, h2)
            
            # Масштабируем пропорционально если высоты разные
            if h1 != max_h:
                ratio = max_h / h1
                new_w1 = int(w1 * ratio)
                img1 = img1.resize((new_w1, max_h), Image.Resampling.LANCZOS)
                w1 = new_w1
            
            if h2 != max_h:
                ratio = max_h / h2
                new_w2 = int(w2 * ratio)
                img2 = img2.resize((new_w2, max_h), Image.Resampling.LANCZOS)
                w2 = new_w2
            
            # Создаем холст: ширина1 + отступ + ширина2, высота = max_h
            total_width = w1 + gap + w2
            combined = Image.new("RGBA", (total_width, max_h), (255, 255, 255, 255))
            
            # Вставляем изображения
            combined.paste(img1, (0, 0))
            combined.paste(img2, (w1 + gap, 0))
            
            # Конвертируем в RGB для JPEG
            combined_rgb = combined.convert("RGB")
            
            # Сохраняем в буфер
            buffer = io.BytesIO()
            combined_rgb.save(buffer, format="JPEG", quality=90)
            return buffer.getvalue()
            
        except Exception as e:
            if self.debug_mode:
                print(f"[ERROR] Ошибка при объединении изображений: {e}")
            # Если ошибка - возвращаем первое изображение
            return img1_bytes
    
    async def _process_main_product_images(self, images: List[str], is_parent: bool = True) -> List[str]:
        """
        Для главного товара (родителя) входной двери объединяет первые два изображения.
        Возвращает список из одного объединенного изображения или оригинальный список если < 2.
        """
        if not is_parent or len(images) < 2:
            return images
        
        # Проверяем, является ли товар входной дверью (по ключевым словам можно добавить позже)
        # Сейчас применяем ко всем родителям для универсальности
        
        async with aiohttp.ClientSession() as session:
            # Скачиваем первые два изображения
            img1_bytes = await self._download_image_bytes(session, images[0])
            img2_bytes = await self._download_image_bytes(session, images[1])
            
            if img1_bytes and img2_bytes:
                try:
                    merged_bytes = await self._merge_two_images_horizontally(img1_bytes, img2_bytes)
                    
                    # Сохраняем во временный файл или кодируем в base64
                    # Для простоты сохраняем во временную папку и возвращаем путь
                    # Но для экспорта лучше вернуть base64 или сохранить и вернуть URL
                    # В данном случае вернем как есть, а сохранение сделаем в экспортере
                    
                    # Создаем временный файл
                    import tempfile
                    fd, temp_path = tempfile.mkstemp(suffix=".jpg", prefix="merged_door_")
                    os.write(fd, merged_bytes)
                    os.close(fd)
                    
                    # В реальном использовании нужно загрузить на сервер или использовать base64
                    # Сейчас просто вернем оригинальный список, т.к. без сервера хранения сложно
                    # Логика будет доработана в экспортере
                    
                    if self.debug_mode:
                        print(f"[INFO] Изображения объединены, сохранено в: {temp_path}")
                    
                    # Возвращаем специальный маркер, что нужно использовать локальный файл
                    # Но для совместимости вернем первый URL, а в экспортере обработаем
                    return images  # Пока возвращаем как есть, логика объединения перенесена в экспортер
                    
                except Exception as e:
                    if self.debug_mode:
                        print(f"[WARN] Не удалось объединить изображения: {e}")
        
        return images

    def _get_supplier_name(self, session: Session) -> str:
        """Получает имя поставщика."""
        supplier = session.query(Supplier).filter(Supplier.id == self.supplier_id).first()
        return supplier.name if supplier else "Тандор"

    @staticmethod
    def _generate_sku(supplier_name: str, raw_title: str, counter: int) -> str:
        """Генерирует SKU формата: 'Производитель Коллекция XXXXX'.
        
        Остаётся только производитель + название коллекции + порядковый номер.
        Пример:
            "Входная дверь Валенсия Белый матовый 950x2030" -> "Тандор Валенсия 000001"
            "Межкомнатная дверь Глухая (ДГ) Элегия-2 Античный орех" -> "Тандор Элегия-2 000001"
        """
        clean = raw_title.strip()
        
        # 1. Удаляем префиксы типов дверей
        for prefix in [
            "Входная дверь ", "Дверь входная ", "Дверь ",
            "Межкомнатная дверь ", "Дверь межкомнатная ",
        ]:
            clean = clean.replace(prefix, "", 1)
        
        # 2. Удаляем типы конструкций с скобками: "Глухая (ДГ)", "С остеклением (С)", "Двухпольная (ДВ)"
        clean = re.sub(r'\w+?\s+\([^)]*\)', '', clean)
        
        # 3. Удаляем размер в конце: " 860x2050", " 950*2030"
        clean = re.sub(r'\s+\d{2,4}[xXх*]\d{3,4}\s*$', '', clean)
        
        # 4. Удаляем направления открывания: "Левая", "Правая", "Левое открывание", "Правое открывание"
        for direction in ["Левое открывание", "Правое открывание", "Левая", "Правая"]:
            clean = clean.replace(direction, "")
        
        # 5. Нормализуем пробелы
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # 6. Оставляем только название коллекции (первое слово после производителя)
        words = clean.split()
        collection_name = next((w for w in words if w and not w.isdigit()), words[0] if words else "")
        
        return f"{supplier_name} {collection_name} {counter:06d}"

    # --- Специфичные для Tandoor методы эмуляции поведения ---
    async def _scroll_product_gallery(self, page: Page):
        """Прокручивает слайдер фотографий товара для загрузки всех изображений.
        
        Слайдер на tandoor.ru использует ленивую загрузку - фотографии подгружаются
        только при переключении слайда. Нужно прокликать все слайды.
        """
        try:
            # Ждём появления слайдера
            await page.wait_for_selector(".Thumbnail-slide__swiper-image", timeout=5000)
            
            # Находим все кнопки навигации слайдера или просто кликаем по стрелкам
            next_button = page.locator(".swiper-button-next, .Thumbnail-slider__button_next").first
            
            # Делаем несколько кликов для прокрутки всех слайдов (обычно 3-10 фото)
            for i in range(10):  # Максимум 10 слайдов
                try:
                    # Проверяем, существует ли кнопка и активна ли она
                    button_state = await next_button.get_attribute("class")
                    if button_state and "swiper-button-disabled" in button_state:
                        break  # Кнопка неактивна - дошли до конца
                    
                    # Кликаем по кнопке "вперёд"
                    await next_button.click(timeout=2000)
                    await asyncio.sleep(0.3)  # Ждём загрузки слайда
                    
                except Exception:
                    # Кнопка не найдена или неактивна - выходим
                    break
            
            # Дополнительная пауза для загрузки всех изображений
            await asyncio.sleep(0.5)
            
        except Exception as e:
            self._log(f"  ⚠️ Не удалось прокрутить слайдер: {e}")

    async def _human_like_scroll(self, page: Page):
        """Эмулирует человеческую прокрутку страницы."""
        total_height = await page.evaluate("document.body.scrollHeight")
        viewport_height = await page.evaluate("window.innerHeight")
        steps = max(3, int(total_height / viewport_height))
        for i in range(steps):
            scroll_y = int((i / steps) * total_height)
            await page.mouse.wheel(0, random.randint(100, 300))
            await asyncio.sleep(random.uniform(0.1, 0.3))

    async def _random_mouse_move(self, page: Page):
        """Эмулирует случайные движения мыши."""
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, 1800)
            y = random.randint(100, 900)
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            await asyncio.sleep(random.uniform(0.1, 0.5))

    # --- Продвинутые методы Playwright ---
    async def _get_stealth_context(self, browser: Browser) -> BrowserContext:
        self._log("Создание stealth-контекста браузера...")
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            timezone_id="Europe/Moscow",
            locale="ru-RU",
        )
        await context.add_init_script(STEALTH_JS)
        return context

    # --- Извлечение изображений (общий метод для устранения дублирования) ---
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Извлекает изображения продукта с страницы.
        
        Приоритеты:
        1. data-zoom-image (максимальное качество)
        2. srcset у <source class="Thumbnail-slide__swiper-image">
        3. src у <img class="Thumbnail-slide__swiper-image">
        
        Фильтрует: миниатюры (100x100), видео-превью (rutube/youtube)
        """
        images = []
        seen = set()
        
        def is_valid_image(url: str) -> bool:
            """Фильтрует миниатюры и видео-превью."""
            if not url or url.startswith("data:"):
                return False
            # Фильтруем миниатюры 100x100
            if "100x100" in url or "/100_100/" in url:
                return False
            # Фильтруем видео-превью
            if any(x in url.lower() for x in ["rutube", "youtube", "video"]):
                return False
            return True
        
        def add_image(url: str):
            """Добавляет изображение с проверкой на дубликаты."""
            full = urljoin(base_url, url)
            if is_valid_image(full) and full not in seen:
                images.append(full)
                seen.add(full)
        
        # === Метод 1: data-zoom-image (приоритет - максимальное качество) ===
        for img in soup.select("img[data-zoom-image]"):
            zoom_url = img.get("data-zoom-image")
            if zoom_url:
                add_image(zoom_url)
        
        # === Метод 2: srcset у <source class="Thumbnail-slide__swiper-image"> ===
        for source in soup.select("source.Thumbnail-slide__swiper-image"):
            srcset = source.get("srcset", "")
            if srcset:
                # Берём первый URL из srcset (обычно это лучшее качество)
                first_url = srcset.split()[0] if srcset.strip() else ""
                if first_url:
                    add_image(first_url)
        
        # === Метод 3: src у <img class="Thumbnail-slide__swiper-image"> ===
        for img in soup.select("img.Thumbnail-slide__swiper-image"):
            # Пропускаем, если уже взяли из data-zoom-image
            if img.get("data-zoom-image"):
                continue
            src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            if src:
                add_image(src)
        
        # === Метод 4: старый селектор (для обратной совместимости) ===
        for img in soup.select("img.swiper-slide-img"):
            src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            if src:
                add_image(src)
        
        # === Fallback 1: og:image ===
        if not images:
            og_img = soup.select_one('meta[property="og:image"]')
            if og_img and og_img.get("content"):
                add_image(og_img["content"])
        
        # === Fallback 2: .Product-gallery__image ===
        if not images:
            for img in soup.select(".Product-gallery__image"):
                src = img.get("src") or img.get("data-src")
                if src:
                    add_image(src)
        
        return images

    # --- Извлечение данных со страницы продукта ---
    def _extract_product_data(self, soup: BeautifulSoup, base_url: str) -> Optional[Dict[str, Any]]:
        """Извлекает основные данные продукта из BeautifulSoup."""
        title_el = soup.select_one("h1")
        title = self._clean_text(title_el.get_text() if title_el else "")
        if not title:
            return None

        # Цена полотна: берём из #polotno-elem data-price (цена без погонажа)
        polotno_item = soup.select_one("#polotno-elem")
        price = None
        if polotno_item:
            raw_price = polotno_item.get("data-price", "")
            if raw_price:
                price = self.normalize_price(raw_price)
        # Fallback: второй .Product-description__item-price-value (без itemprop)
        if price is None:
            all_price_spans = soup.select(".Product-description__item-price-value")
            for ps in all_price_spans:
                if not ps.get("itemprop"):  # не gates-цена
                    text_price = self.normalize_price(ps.get_text())
                    if text_price:
                        price = text_price
                        break
        # Fallback 2: первый span[itemprop='price'] content
        if price is None:
            og_price = soup.select_one('span[itemprop="price"]')
            if og_price:
                og_content = og_price.get("content", "")
                if og_content:
                    price = float(og_content)

        currency = "RUB"

        desc_el = soup.select_one(".Product-description__subtitle, .product-subtitle")
        description = self._clean_text(desc_el.get_text() if desc_el else "")

        sku = None
        sku_el = soup.select_one(".Product-description__sku, .product-sku, [data-sku]")
        if sku_el:
            sku = self._clean_text(sku_el.get_text())

        images = self._extract_images(soup, base_url)

        size_variations = self._extract_size_variations(soup, base_url)

        return {
            "title": title,
            "description": description,
            "price": price,
            "currency": currency,
            "sku": sku,
            "images": images,
            "size_variations": size_variations,
        }

    @staticmethod
    def _extract_collection_name(raw_title: str) -> str:
        """Очищает название товара, оставляя только название коллекции.
        
        Примеры:
            "Межкомнатная дверь Глухая (ДГ) Элегия-2 Античный орех" -> "Элегия-2"
            "Межкомнатная дверь Частично остекленная (ДЧ) Премьер плюс-2 Венге" -> "Премьер плюс-2"
            "Входная дверь Валенсия Белый матовый 950x2030" -> "Валенсия"
        """
        KNOWN_COLORS = {
            "Античный орех", "Белый жемчуг", "Белый", "Венге", "Дуб", "Скандинавия",
            "Черный", "Гrey", "Серый", "Красный", "Зеленый", "Орех", "Махагон",
            "Натуральный", "Сонома", "Молочный", "Шоколад", "Браун", "Бук",
            "Графит", "Антрацит", "Слоновая кость", "Сливковый", "Матовый",
            "Гloss", "Бежевый", "Песочный", "Ванильный", "Карамель", "Корица",
            "Латте", "Капучино", "Мокко", "Золотой", "Серебряный", "Жемчужный",
            "Каменный", "Бетон", "Бров", "Кашемир", "Палето", "Кортекс",
            "Матовый белый", "Матовый черный", "Глянец",
        }
        
        clean = raw_title.strip()
        
        # 1. Удаляем префиксы типов дверей
        for prefix in [
            "Входная дверь ", "Дверь входная ",
            "Межкомнатная дверь ", "Дверь межкомнатная ",
        ]:
            clean = clean.replace(prefix, "", 1)
        
        # 2. Удаляем типы конструкций: "Глухая (ДГ)", "Частично остекленная (ДЧ)" и т.д.
        clean = re.sub(r'.*?\b(Глухая|Частично остекленная|Полностеклянная|Двухпольная|Однопольная|С)\s*\([^)]*\)\s*', '', clean)
        
        # 3. Удаляем размеры в конце
        clean = re.sub(r'\s+\d{2,4}[xXх*]\d{3,4}\s*$', '', clean)
        
        # 4. Удаляем направления открывания
        for direction in ["Левое открывание", "Правое открывание", "Левая", "Правая"]:
            clean = clean.replace(direction, "")
        
        # 5. Нормализуем пробелы
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # 6. Удаляем известные цвета в конце (сначала длинные, потом короткие)
        sorted_colors = sorted(KNOWN_COLORS, key=len, reverse=True)
        for color in sorted_colors:
            if clean.lower().endswith(color.lower()):
                clean = clean[:len(clean)-len(color)].strip()
                break
        
        # 7. Если после очистки остались валидные слова, удаляем цвет из оставшегося
        if clean:
            clean = clean.strip()
            # Убираем остатки цветов/описаний, если они остались по центру
            for color in sorted(KNOWN_COLORS, key=len, reverse=True):
                clean = re.sub(re.escape(color), '', clean, flags=re.IGNORECASE)
            clean = re.sub(r'\s+', ' ', clean).strip()
        
        # 8. Если ничего не осталось, берем первое содержательное слово
        if not clean:
            clean = raw_title.strip()
            for prefix in [
                "Входная дверь ", "Дверь входная ",
                "Межкомнатная дверь ", "Дверь межкомнатная ",
            ]:
                clean = clean.replace(prefix, "", 1)
            words = clean.split()
            # Пропускаем очевидные служебные слова
            skip_words = {"ДГ", "ДЧ", "ДО", "ДВ", "ОП", "Л", "П", "x", "X"}
            for w in words:
                stripped = w.strip(".,;:()[]{}-")
                if stripped and stripped not in skip_words and len(stripped) > 1:
                    return stripped
            # Если и так ничего — возвращаем первое слово
            return words[0] if words else ""
        
        return clean

    def _extract_size_variations(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Извлекает варианты размеров из radio-кнопок на странице продукта.

        HTML структура (из скриншота):
        <div class="Product-description__size-specification Radio-btn">
            <div class="Radio-btn__content-label Radio-btn__content-label--col3">
                <label title="Ширина полотна, см">
                    <input class="sizer" type="radio" name="size" value="/catalog/product/mona-01-brown-pet-dg-2000-600/">
                    <span>60</span>
                </label>
            </div>
        </div>
        """
        variations = []

        size_block = soup.select_one(".Product-description__size-specification")
        if not size_block:
            return variations

        labels = size_block.select("label")
        for label in labels:
            radio_input = label.select_one("input[type='radio']")
            span = label.select_one("span")

            if not radio_input or not span:
                continue

            size_value = self._clean_text(span.get_text())
            size_url = radio_input.get("value", "")

            if not size_value:
                continue

            full_url = urljoin(base_url, size_url) if size_url else ""

            variations.append({
                "size": size_value,
                "url": full_url,
            })

        return variations

    def _extract_product_type(self, soup: BeautifulSoup) -> str:
        """Извлекает тип двери (ДГ, ДЧ, ДО и т.д.)."""
        type_block = soup.select_one(".Product-description__type-specification")
        if not type_block:
            return ""

        active_label = type_block.select_one(".Radio-btn__label--active, .Radio-btn__label--selected, label.active")
        if active_label:
            return self._clean_text(active_label.get_text())

        active_input = type_block.select_one("input:checked")
        if active_input:
            parent_label = active_input.find_parent("label")
            if parent_label:
                return self._clean_text(parent_label.get_text())

        return ""

    def _extract_color(self, soup: BeautifulSoup) -> str:
        """Извлекает выбранный (активный) цвет."""
        # Основной блок спецификации
        color_block = soup.select_one(".Product-description__color-specification")
        if color_block:
            active_label = color_block.select_one(".Radio-btn__label--active, .Radio-btn__label--selected, label.active")
            if active_label:
                title = active_label.get("title", "")
                if title:
                    return self._clean_text(title)
                return self._clean_text(active_label.get_text())

        # Fallback: палитра .Palette__btn-color-selection с активным элементом
        active_palette_item = soup.select_one(".Palette__item-color-selection--active")
        if active_palette_item:
            img_label = active_palette_item.select_one("label")
            if img_label:
                title = img_label.get("title", "")
                if title:
                    return self._clean_text(title)
        
        # Fallback 2: первый label с title в палитре
        palette_img = soup.select_one(".Palette__btn-color-selection-img")
        if palette_img:
            # Ищем ближайший label
            parent = palette_img.find_parent("label")
            if parent:
                title = parent.get("title", "")
                if title:
                    return self._clean_text(title)
        
        # Fallback 3: берём цвет из characteristics
        char_color = self._extract_characteristics(soup).get("Цвет", "")
        if char_color:
            return self._clean_text(char_color)

        return ""

    def _extract_all_colors(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Извлекает ВСЕ цвета из палитры на странице продукта.
        
        Поддерживает ДВА формата HTML:
        
        1) Спецификация:
        <div class="Product-description__color-specification Radio-btn">
            <label title="Белый">
                <input type="radio" name="color" value="/catalog/product/...-white/">
            </label>
        </div>
        
        2) Палитра (межкомнатные двери):
        <div class="Palette__item-color-selection">
            <label title="Зефир">
                <input type="radio" name="color" value="...">
                <img class="Palette__btn-color-selection-img" alt="color">
            </label>
        </div>
        
        Возвращает:
        [{"name": "Белый", "url": "https://tandoor.ru/catalog/product/...-white/"}, ...]
        """
        colors = []
        seen_names = set()
        
        # Метод 1: спецификация Product-description__color-specification
        color_block = soup.select_one(".Product-description__color-specification")
        if color_block:
            for label in color_block.select("label"):
                color_name = self._clean_text(label.get("title", ""))
                if not color_name:
                    text_parts = []
                    for span in label.select("span"):
                        span_text = self._clean_text(span.get_text())
                        if span_text and span_text not in ("Л", "П"):
                            text_parts.append(span_text)
                    color_name = self._clean_text(" ".join(text_parts))
                
                if not color_name or color_name in seen_names:
                    continue
                seen_names.add(color_name)
                
                radio_input = label.select_one("input[type='radio']")
                color_url = radio_input.get("value", "") if radio_input else ""
                full_url = urljoin(base_url, color_url) if color_url else ""
                
                colors.append({"name": color_name, "url": full_url})
        
        # Метод 2: палитра Palette__item-color-selection
        if not colors:
            for palette_item in soup.select(".Palette__item-color-selection"):
                for label in palette_item.select("label"):
                    color_name = self._clean_text(label.get("title", ""))
                    
                    if not color_name:
                        img = label.select_one("img")
                        if img:
                            color_name = self._clean_text(img.get("alt", ""))
                    
                    if not color_name or color_name in seen_names:
                        continue
                    seen_names.add(color_name)
                    
                    radio_input = label.select_one("input[type='radio']")
                    color_url = radio_input.get("value", "") if radio_input else ""
                    full_url = urljoin(base_url, color_url) if color_url else ""
                    
                    colors.append({"name": color_name, "url": full_url})
        
        # Метод 3: fallback — цвета из characteristics
        if not colors:
            chars = self._extract_characteristics(soup)
            char_color = chars.get("Цвет", "")
            if char_color:
                colors.append({"name": char_color, "url": base_url})
        
        return colors

    def _extract_compatible_collections(self, soup: BeautifulSoup) -> List[str]:
        """Извлекает совместимые коллекции погонажа."""
        collections = []
        coll_block = soup.select_one(".Product-description__molding-specification, .molding-specification")
        if coll_block:
            for item in coll_block.select(".Radio-btn__label, label"):
                text = self._clean_text(item.get_text())
                if text:
                    collections.append(text)
        return collections

    def _extract_opening_directions(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Извлекает направления открывания из radio-кнопок на странице продукта.
        
        HTML структура (аналогично типу/цвету/размеру):
        <div class="Product-description__open-specification Radio-btn">
            <div class="Radio-btn__content-label">
                <label title="Левая">
                    <input type="radio" name="open" value="/catalog/product/...-left/">
                    <span>Л</span>
                </label>
            </div>
        </div>
        """
        directions = []
        
        # Ищем блок с направлениями открывания — пробуем РАЗНЫЕ CSS-селекторы
        open_block = soup.select_one(
            ".Product-description__open-specification, "
            ".Product-description__direction-specification, "
            ".Product-description__side-specification"
        )
        
        # Fallback: ищем по label title="Левая"/title="Правая" или span с Л/П
        if not open_block:
            for label in soup.select("label"):
                title = self._clean_text(label.get("title", "")).lower()
                span = label.select_one("span")
                span_text = self._clean_text(span.get_text()) if span else ""
                
                # Проверяем title на наличие "лев"/"прав"
                if "лев" in title or "прав" in title:
                    radio = label.select_one("input[type='radio']")
                    if radio:
                        code = "Л" if "лев" in title else "П"
                        full = "Левая" if "лев" in title else "Правая"
                        directions.append({"code": code, "full": full})
                elif span_text.upper() in ("Л", "П"):
                    radio = label.select_one("input[type='radio']")
                    if radio:
                        # Проверяем что это radio-группа направления, а не чего-то другого
                        parent = label.parent
                        if parent and ("direction" in " ".join(parent.get("class", [])) or
                                       "open" in " ".join(parent.get("class", [])) or
                                       "side" in " ".join(parent.get("class", []))):
                            code = span_text.upper()
                            full = "Левая" if code == "Л" else "Правая"
                            directions.append({"code": code, "full": full})
            
            return directions
        
        labels = open_block.select("label")
        for label in labels:
            span = label.select_one("span")
            if not span:
                continue
            
            span_text = self._clean_text(span.get_text())
            title = self._clean_text(label.get("title", ""))
            
            # Определяем код и полное название направления
            code = ""
            full = ""
            
            text_to_check = (title or span_text).lower()
            if "лев" in text_to_check:
                code = "Л"
                full = "Левая"
            elif "прав" in text_to_check:
                code = "П"
                full = "Правая"
            elif span_text:
                code = span_text[0] if span_text else ""
                full = title if title else span_text
            
            if full:
                directions.append({
                    "code": code,
                    "full": full,
                })
        
        return directions

    def _extract_molding_items(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Извлекает элементы погонажа/комплектующих, исключая полотно.
        
        HTML структура:
        <li class="Product-description__molding-item" data-price="9910" data-id="256069" id="polotno-elem">...</li>
        <li class="Product-description__molding-item" data-price="640" data-id="71040">Добор 10*100*2070 Зефир</li>
        
        Исключает элемент с id="polotno-elem" (это полотно, не погонаж).
        """
        molding_items = []
        
        for item in soup.select(".Product-description__molding-item"):
            # Исключаем полотно
            if item.get("id") == "polotno-elem":
                continue
            
            name = self._clean_text(item.get_text())
            # Убираем мусорный текст
            name = re.sub(r'\s+', ' ', name).strip()
            # Убираем "Скачать" "В наличии:" "0₽/999₽" из названия
            name = re.sub(r'Скачать', '', name)
            name = re.sub(r'В\s+наличьи?[:\s]*\d*', '', name)
            name = re.sub(r'\d+\s*₽.*$', '', name)
            name = self._clean_text(name)
            
            if not name:
                continue
            
            raw_price = item.get("data-price", "0")
            price = self.normalize_price(raw_price)
            
            data_id = item.get("data-id", "")
            
            # Определяем категорию погонажа из названия
            category = self._classify_molding_category(name)
            
            molding_items.append({
                "name": name,
                "price": price,
                "data_id": data_id,
                "category": category,
            })
        
        return molding_items

    @staticmethod
    def _classify_molding_category(name: str) -> str:
        """Определяет категорию погонажа по названию.
        
        "Добор 10*100*2070 Зефир" -> "Добор"
        "Короб 32*70*2100 Зефир" -> "Короб"
        "Наличник 10*80*2185 Зефир" -> "Наличник"
        "Притворная планка Зефир" -> "Притворная планка"
        "Плинтус МДФ 80х10х2070 Зефир" -> "Плинтус"
        """
        name_upper = name[:3].upper()
        name_lower = name.lower()
        
        if name_lower.startswith("добор"):
            return "Добор"
        if name_lower.startswith("короб"):
            return "Короб"
        if name_lower.startswith("наличник"):
            return "Наличник"
        if "притвор" in name_lower:
            return "Притворная планка"
        if "плинтус" in name_lower:
            return "Плинтус"
        if "договор" in name_lower or "догов" in name_lower:
            return "Договор"
        if "петля" in name_lower:
            return "Петля"
        if "замок" in name_lower or "ручка" in name_lower:
            return "Фурнитура"
        
        # Попробуем извлечь первое слово как категорию
        first_word = name.split()[0] if name.split() else "Комплектующее"
        return first_word.capitalize() if len(first_word) > 2 else "Комплектующее"

    @staticmethod
    def _clean_text(text: str) -> str:
        """Очищает текст от лишних пробелов."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    def _extract_characteristics(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Извлекает технические характеристики продукта из <dl> блоков.
        
        HTML структура:
        <dl>
            <dt>Толщина полотна, мм</dt>
            <dd>110</dd>
        </dl>
        """
        chars = {}
        for dl in soup.select("dl"):
            dt = dl.select_one("dt")
            dd = dl.select_one("dd")
            if dt and dd:
                name = self._clean_text(dt.get_text())
                value = self._clean_text(dd.get_text())
                if name and value:
                    chars[name] = value
        return chars

    def _extract_variant_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Извлекает изображения с текущей страницы вариации."""
        return self._extract_images(soup, base_url)

    def _extract_all_product_types(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Извлекает ВСЕ типы дверей из блока type-specification.
        
        Возвращает список:
        [{"name": "Глухая (ДГ)", "url": "/catalog/product/..."}, ...]
        """
        types = []
        type_block = soup.select_one(".Product-description__type-specification")
        if not type_block:
            return types
        
        labels = type_block.select("label")
        for label in labels:
            radio_input = label.select_one("input[type='radio']")
            if not radio_input:
                continue
            
            type_name = self._clean_text(label.get("title", ""))
            if not type_name:
                span = label.select_one("span")
                if span:
                    type_name = self._clean_text(span.get_text())
            
            if not type_name:
                continue
            
            type_url = radio_input.get("value", "")
            full_url = urljoin(base_url, type_url) if type_url else ""
            
            types.append({
                "name": type_name,
                "url": full_url,
            })
        
        return types

    def _extract_all_molding_types(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Извлекает типы погонажа/молдинга из блока molding-specification.
        
        Возвращает список:
        [{"name": "Зефир", "url": "/catalog/product/..."}, ...]
        """
        moldings = []
        mold_block = soup.select_one(".Product-description__molding-specification, .molding-specification")
        if not mold_block:
            return moldings
        
        labels = mold_block.select("label, .Radio-btn__label")
        for label in labels:
            radio_input = label.select_one("input[type='radio']")
            if not radio_input:
                continue
            
            molding_name = self._clean_text(label.get("title", ""))
            if not molding_name:
                molding_name = self._clean_text(label.get_text())
            
            if not molding_name:
                continue
            
            molding_url = radio_input.get("value", "")
            full_url = urljoin(base_url, molding_url) if molding_url else ""
            
            moldings.append({
                "name": molding_name,
                "url": full_url,
            })
        
        return moldings

    def _generate_attribute_combinations(self, attribute_variants: Dict[str, List]) -> List[Dict[str, Any]]:
        """Генерирует все комбинации атрибутов.
        
        attribute_variants = {
            "Цвет": [{"name": "Белый", "url": "..."}, ...],
            "Размер": [{"size": "860", "url": "..."}, ...],
            "Направление": [{"full": "Левая", ...}, ...],
            ...
        }
        
        Возвращает список комбинаций:
        [{"Цвет": {...}, "Размер": {...}, "Направление": {...}}, ...]
        """
        if not attribute_variants:
            return []
        
        keys = list(attribute_variants.keys())
        values = [attribute_variants[k] for k in keys]
        
        combinations = []
        for combo in itertools.product(*values):
            combo_dict = {}
            for i, key in enumerate(keys):
                combo_dict[key] = combo[i]
            combinations.append(combo_dict)
        
        return combinations

    def _create_child_from_combination(
        self, combo: Dict[str, Any], page: Page, base_url: str,
        data: Dict[str, Any], characteristics: Dict[str, str],
        parent_title: str, product_type: str, results: List[ParsedProduct]
    ):
        """Создает продукт-ребенок из конкретной комбинации атрибутов.
        
        Парсит страницу вариации для получения уникальных фото, цены и характеристик.
        """
        combo_url = None
        combo_attributes = {}
        
        # Собираем URL и атрибуты из комбинации
        color_info = combo.get("Цвет", {})
        if isinstance(color_info, dict):
            combo_attributes["Цвет"] = color_info.get("name", "")
        
        size_info = combo.get("Размер", {})
        if isinstance(size_info, dict):
            combo_attributes["Размер"] = size_info.get("size", "")
            if size_info.get("url"):
                combo_url = size_info["url"]
        
        direction_info = combo.get("Направление", {})
        if isinstance(direction_info, dict):
            combo_attributes["Направление"] = direction_info.get("full", "")
        
        type_info = combo.get("Тип", {})
        if isinstance(type_info, dict):
            combo_attributes["Тип"] = type_info.get("name", "")
            if type_info.get("url") and not combo_url:
                combo_url = type_info["url"]
        
        molding_info = combo.get("Молдинг", {})
        if isinstance(molding_info, dict):
            combo_attributes["Молдинг"] = molding_info.get("name", "")
            if molding_info.get("url") and not combo_url:
                combo_url = molding_info["url"]
        
        # Убираем пустые значения
        combo_attributes = {k: v for k, v in combo_attributes.items() if v}
        
        # Парсим страницу вариации для получения уникальных данных
        variant_images = list(data["images"])
        variant_price = data["price"]
        variant_characteristics = dict(characteristics)
        
        if combo_url:
            try:
                attr_desc = ", ".join(f"{k}={v}" for k, v in combo_attributes.items())
                self._log(f"  Парсинг вариации {attr_desc}: {combo_url}")
                
                asyncio.get_event_loop().create_task(
                    self._parse_variant_page(page, combo_url)
                )
            except Exception:
                pass

        child_product = ParsedProduct(
            url=combo_url if combo_url else base_url,
            title=parent_title,
            description=data["description"],
            price=variant_price,
            currency=data["currency"],
            category_id=data.get("category_id"),
            is_available=True,
        )
        
        for attr_name, attr_value in combo_attributes.items():
            child_product.attributes[attr_name] = attr_value
        
        if product_type:
            child_product.attributes["Тип"] = product_type
        
        for char_name, char_value in variant_characteristics.items():
            child_product.attributes[char_name] = char_value
        
        child_product.image_urls = variant_images if variant_images else data["images"]
        
        results.append(child_product)
        self.stats["variations_created"] += 1

    async def _parse_variant_page(self, page: Page, url: str) -> Dict[str, Any]:
        """Парсит страницу вариации и возвращает данные."""
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(random.uniform(0.3, 0.8))
        html = await page.content()
        soup = BeautifulSoup(html, "lxml")
        
        result = {}
        result["images"] = self._extract_variant_images(soup, url)
        result["characteristics"] = self._extract_characteristics(soup)
        
        var_price_el = soup.select_one(
            "span[itemprop='price'], .Product-description__price-value, .price-value"
        )
        if var_price_el:
            result["price"] = self.normalize_price(var_price_el.get_text())
        
        return result

    # --- Реализация абстрактных методов ---
    async def _parse_product_page(self, page: Page, url: str, **kwargs) -> Optional[List[ParsedProduct]]:
        """Парсит страницу продукта и возвращает список: [родитель, ребёнок1, ребёнок2, ...].
        Каждая вариация парсится отдельно для получения уникального фото.
        
        Входные двери: Цвет × Размер × Направление = все комбинации
        Межкомнатные двери: Каждый атрибут = отдельный ребенок
        """
        category_id = kwargs.get("category_id")
        try:
            await page.goto(url, wait_until="networkidle", timeout=45000)
            
            # === Прокручиваем слайдер фотографий для загрузки всех изображений ===
            await self._scroll_product_gallery(page)
            
            # Затем прокручиваем страницу вниз для остального контента
            await self._human_like_scroll(page)
            await asyncio.sleep(random.uniform(0.5, 1.5))

            if self.debug_mode:
                await page.screenshot(path=f"screenshots/debug_{datetime.now():%H%M%S}.png")

            html = await page.content()
            soup = BeautifulSoup(html, "lxml")

            data = self._extract_product_data(soup, url)
            if not data:
                return None
            
            # Устанавливаем category_id из внешнего mapping
            data["category_id"] = category_id

            product_type = self._extract_product_type(soup)
            color = self._extract_color(soup)
            collections = self._extract_compatible_collections(soup)
            characteristics = self._extract_characteristics(soup)
            molding_items = self._extract_molding_items(soup)

            results = []

            # Очищенное название товара (только название коллекции)
            parent_title = self._extract_collection_name(data["title"])

            # Определяем: это погонаж или дверь?
            is_molding = product_type.lower() == "погонаж" or "погонаж" in data["title"].lower()
            
            if is_molding or characteristics.get("Тип погонажа"):
                # === ПОГОНАЖ: отдельный товар без родителя ===
                parent_product = None
            else:
                # === ДВЕРЬ: создаём родителя ===
                parent_product = ParsedProduct(
                    url=url,
                    title=parent_title,
                    description=data["description"],
                    price=data["price"],
                    currency=data["currency"],
                    sku=data["sku"],
                    category_id=data.get("category_id"),
                    image_urls=data["images"],
                    is_available=True,
                )
                parent_product.attributes["Тип"] = product_type
                if color:
                    parent_product.attributes["Цвет"] = color
                if collections:
                    parent_product.compatible_collections = collections
                molding_type = characteristics.get("Тип погонажа", "")
                if molding_type and not parent_product.compatible_collections:
                    parent_product.compatible_collections = [molding_type]
                for char_name, char_value in characteristics.items():
                    parent_product.attributes[char_name] = char_value
                
                results.append(parent_product)

            # Извлекаем все цвета
            all_colors = self._extract_all_colors(soup, url)
            if not all_colors and color:
                all_colors = [{"name": color, "url": url}]
            elif not all_colors:
                all_colors = [{"name": "", "url": url}]

            # === ГЕНЕРАЦИЯ ДЕТЕЙ ===
            
            # Собираем ВСЕ уникальные атрибуты для детей
            all_sizes = []
            all_directions = []
            all_product_types = self._extract_all_product_types(soup, url)
            all_molding_types = self._extract_all_molding_types(soup, url)
            
            # Словарь для хранения всех вариантов каждого атрибута
            attribute_variants = {
                "Цвет": all_colors,
                "Размер": [],
                "Направление": [],
                "Тип": all_product_types,
                "Кромка": [],
                "Молдинг": all_molding_types,
            }
            
            # Собираем размеры и направления
            for color_item in all_colors:
                color_url = color_item["url"]
                page_soup = soup
                page_url = url
                
                if color_url and color_url != url:
                    try:
                        await page.goto(color_url, wait_until="networkidle", timeout=30000)
                        await asyncio.sleep(random.uniform(0.5, 1.0))
                        color_html = await page.content()
                        page_soup = BeautifulSoup(color_html, "lxml")
                        page_url = color_url
                    except Exception as e:
                        self._log(f"  Ошибка загрузки страницы цвета {color_url}: {e}")
                        page_soup = soup
                        page_url = url
                
                current_sizes = self._extract_size_variations(page_soup, page_url)
                if current_sizes and not current_sizes in attribute_variants["Размер"]:
                    attribute_variants["Размер"].extend(current_sizes)
                
                current_directions = self._extract_opening_directions(page_soup)
                if current_directions:
                    for d in current_directions:
                        if d not in attribute_variants["Направление"]:
                            attribute_variants["Направление"].append(d)

            # Дедубликация размеров
            seen_sizes = set()
            unique_sizes = []
            for s in attribute_variants["Размер"]:
                if s["size"] not in seen_sizes:
                    seen_sizes.add(s["size"])
                    unique_sizes.append(s)
            attribute_variants["Размер"] = unique_sizes
            
            # Дедубликация направлений
            seen_dirs = set()
            unique_dirs = []
            for d in attribute_variants["Направление"]:
                if d["full"] not in seen_dirs:
                    seen_dirs.add(d["full"])
                    unique_dirs.append(d)
            attribute_variants["Направление"] = unique_dirs

            # Удаляем пустые значения
            attribute_variants = {k: v for k, v in attribute_variants.items() if v}

            # Для каждой комбинации атрибутов создаем ребенка
            if parent_product:
                # Декартово произведение всех атрибутов
                attribute_keys = list(attribute_variants.keys())
                if len(attribute_keys) == 0:
                    # Нет атрибутов — создаем одного ребенка с базовыми данными
                    child = ParsedProduct(
                        url=url,
                        title=parent_title,
                        description=data["description"],
                        price=data["price"],
                        currency=data["currency"],
                        category_id=data.get("category_id"),
                        is_available=True,
                    )
                    child.image_urls = data["images"]
                    for char_name, char_value in characteristics.items():
                        child.attributes[char_name] = char_value
                    results.append(child)
                    self.stats["variations_created"] += 1
                else:
                    # Генерируем все комбинации
                    for combo in self._generate_attribute_combinations(attribute_variants):
                        self._create_child_from_combination(
                            combo, page, url, data, characteristics, parent_title,
                            product_type, results
                        )

            # === ПОГОНАЖ: сохраняем как отдельные товары ===
            for mold in molding_items:
                mold_product = ParsedProduct(
                    url=url,
                    title=mold["name"],
                    description=data["description"],
                    price=mold["price"],
                    currency=data["currency"],
                    category_id=data.get("category_id"),
                    is_available=True,
                )
                mold_product.attributes["Категория погонажа"] = mold["category"]
                mold_product.attributes["Коллекция"] = parent_title
                mold_product.attributes["Тип"] = "Погонаж"
                mold_product.attributes["Manufacturer of the collection"] = f"Tandoor>{parent_title}"
                if mold["data_id"]:
                    mold_product.attributes["Внешний ID"] = mold["data_id"]
                results.append(mold_product)
                self.stats["variations_created"] += 1

            return results

        except Exception as e:
            self._log(f"Критическая ошибка при парсинге {url}: {e}")
            await page.goto("about:blank")
            return None

    def _find_child_product(self, session: Session, parent_id: int, attributes: Dict[str, str]) -> Optional[Product]:
        """Находит существующего ребёнка по уникальным атрибутам.
        
        Для дверей: по Цвет + Размер + Направление
        Для погонажа: по title (название погонажа уникально в рамках родителя)
        """
        children = session.query(Product).filter(
            Product.parent_product_id == parent_id
        ).all()
        
        # Проверяем, это погонаж или вариация двери
        is_molding = attributes.get("Тип") == "Погонаж"
        
        if is_molding:
            # Для погонажа ищем по title
            target_title = attributes.get("title", "") or ""
            for child in children:
                if child.title == target_title:
                    return child
            return None
        else:
            # Для дверей ищем по Цвет + Размер + Направление
            target_color = attributes.get("Цвет", "")
            target_size = attributes.get("Размер", "")
            target_direction = attributes.get("Направление", "")
            
            for child in children:
                child_attrs = session.query(ProductAttribute).filter(
                    ProductAttribute.product_id == child.id
                ).all()
                child_attr_dict = {a.name: a.value for a in child_attrs}
                
                child_color = child_attr_dict.get("Цвет", "")
                child_size = child_attr_dict.get("Размер", "")
                child_direction = child_attr_dict.get("Направление", "")
                
                if (target_color == child_color and 
                    target_size == child_size and 
                    target_direction == child_direction):
                    return child
            return None

    def _db_save_batch(self, session: Session, products: List[ParsedProduct]):
        """Сохраняет родителя и детей в БД с генерацией SKU."""
        if not products:
            return

        parent_data = products[0]
        children_data = products[1:]

        # Получаем имя поставщика для SKU
        supplier = session.query(Supplier).filter(Supplier.id == self.supplier_id).first()
        supplier_name = supplier.name if supplier else "Тандор"

        # Генерируем SKU для родителя
        self._sku_counter += 1
        parent_sku = self._generate_sku(supplier_name, parent_data.title, self._sku_counter)

        # Ищем существующего родителя по title (без sku, т.к. sku генерируется)
        existing_parent = session.query(Product).filter(
            Product.supplier_id == self.supplier_id,
            Product.parent_product_id.is_(None),
            Product.title == parent_data.title,
        ).first()

        if existing_parent:
            parent = existing_parent
            parent.title = parent_data.title
            parent.description = parent_data.description
            parent.price = parent_data.price
            parent.currency = parent_data.currency
            parent.is_available = parent_data.is_available
            if parent_data.category_id is not None:
                parent.category_id = parent_data.category_id
            if parent_data.image_urls:
                parent.set_image_urls(parent_data.image_urls)
            if parent_data.compatible_collections:
                parent.set_compatible_collections(parent_data.compatible_collections)
            parent.updated_at = datetime.now(timezone.utc)
        else:
            parent = Product(
                supplier_id=self.supplier_id,
                category_id=parent_data.category_id,
                title=parent_data.title,
                description=parent_data.description,
                price=parent_data.price,
                currency=parent_data.currency,
                is_available=parent_data.is_available,
                external_sku=parent_sku,
            )
            if parent_data.image_urls:
                parent.set_image_urls(parent_data.image_urls)
            if parent_data.compatible_collections:
                parent.set_compatible_collections(parent_data.compatible_collections)
            session.add(parent)
            session.flush()

        for attr_name, attr_value in parent_data.attributes.items():
            existing_attr = session.query(ProductAttribute).filter_by(
                product_id=parent.id, name=attr_name
            ).first()
            if existing_attr:
                existing_attr.value = attr_value
            else:
                session.add(ProductAttribute(product_id=parent.id, name=attr_name, value=attr_value))

        for child_data in children_data:
            # Генерируем SKU для каждого ребёнка
            self._sku_counter += 1
            base_child_sku = self._generate_sku(supplier_name, child_data.title, self._sku_counter)
            
            # Для погонажа передаём title для поиска по названию
            search_attrs = dict(child_data.attributes)
            search_attrs["title"] = child_data.title
            existing_child = self._find_child_product(session, parent.id, search_attrs)
            
            if existing_child:
                child = existing_child
                child.price = child_data.price
                child.currency = child_data.currency
                child.is_available = child_data.is_available
                child.external_sku = base_child_sku
                if child_data.category_id is not None:
                    child.category_id = child_data.category_id
                child.updated_at = datetime.now(timezone.utc)
            else:
                child = Product(
                    supplier_id=self.supplier_id,
                    parent_product_id=parent.id,
                    category_id=child_data.category_id,
                    title=child_data.title,
                    description=child_data.description,
                    price=child_data.price,
                    currency=child_data.currency,
                    is_available=child_data.is_available,
                    external_sku=base_child_sku,
                )
                session.add(child)
                session.flush()

            # Устанавливаем ParentSKU у ребёнка
            parent_sku_attr = session.query(ProductAttribute).filter_by(
                product_id=child.id, name="ParentSKU"
            ).first()
            if parent_sku_attr:
                parent_sku_attr.value = parent.external_sku
            else:
                session.add(ProductAttribute(product_id=child.id, name="ParentSKU", value=parent.external_sku))

            for attr_name, attr_value in child_data.attributes.items():
                if attr_name == "ParentSKU":
                    continue  # Уже установлено выше
                existing_attr = session.query(ProductAttribute).filter_by(
                    product_id=child.id, name=attr_name
                ).first()
                if existing_attr:
                    existing_attr.value = attr_value
                else:
                    session.add(ProductAttribute(product_id=child.id, name=attr_name, value=attr_value))

            if child_data.image_urls:
                child.set_image_urls(child_data.image_urls)

            self.stats["products_parsed"] += 1

        # Родитель тоже засчитываем в статистику
        self.stats["products_parsed"] += 1

    def _validate_product_data(self, product: ParsedProduct) -> bool:
        """Проверяет, что у товара есть все обязательные поля."""
        if not product.title or not product.title.strip():
            self._log(f"Пропущен товар без названия: {product.url}")
            return False
        if product.price is not None and product.price < 0:
            self._log(f"Пропущен товар с отрицательной ценой: {product.title}")
            return False
        return True

    async def _save_to_database(self, session: Session, parsed_products: List[ParsedProduct]):
        """Асинхронная обертка для вызова синхронного сохранения в БД."""
        if not parsed_products:
            return
        # Фильтруем products по валидации
        valid_products = [p for p in parsed_products if self._validate_product_data(p)]
        if not valid_products:
            return
        try:
            await asyncio.to_thread(self._db_save_batch, session, valid_products)
            await asyncio.to_thread(session.commit)
            parent_title = parsed_products[0].title
            children_count = len(parsed_products) - 1
            self._log(f"Сохранено: {parent_title} + {children_count} вариаций")
        except Exception as e:
            self._log(f"Ошибка БД: {e}. Откат изменений.")
            await asyncio.to_thread(session.rollback)
            if parsed_products:
                self.stats["errors"].append(f"DB error on {parsed_products[0].url}: {e}")

    async def run(self, session: Session, **kwargs: Any) -> Dict[str, Any]:
        self.stats["start_time"] = datetime.now(timezone.utc)
        urls = kwargs.get("urls", [])
        url_to_category = kwargs.get("url_to_category", {})
        if not urls:
            self._log("URL для парсинга не предоставлены.")
            return self.stats

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            context = await self._get_stealth_context(browser)
            page = await context.new_page()
            try:
                self._log("Выполняю прогрев сессии...")
                await page.goto("https://google.com", wait_until="domcontentloaded")
                await asyncio.sleep(random.uniform(1, 3))

                for i, url in enumerate(urls):
                    if self._cancelled:
                        self._log("Парсинг отменен пользователем.")
                        break
                    await self._pause_event.wait()
                    self._log(f"[{i + 1}/{len(urls)}] Парсинг: {url}")
                    
                    # Передаём category_id через kwargs в _parse_product_page
                    cat_id = url_to_category.get(url)
                    products_data = await self._parse_product_page(page, url, category_id=cat_id)
                    if products_data:
                        await self._save_to_database(session, products_data)
                    self.progress_callback(i + 1, len(urls), url)
            finally:
                await page.close()
                await context.close()
                await browser.close()

        self.stats["end_time"] = datetime.now(timezone.utc)
        return self.stats
