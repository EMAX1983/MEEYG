"""
Скрипт для изучения структуры страницы товара на tandoor.ru
Извлекает все данные: размеры, характеристики, фото, цену, тип, цвет, направления, коллекция
"""

import json
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080},
            timezone_id="Europe/Moscow",
            locale="ru-RU",
        )
        page = await context.new_page()

        # 1. Открываем главную
        print("[*] Открываем https://tandoor.ru ...")
        await page.goto("https://tandoor.ru", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)

        html = await page.content()
        soup = BeautifulSoup(html, "lxml")

        # Ищем первую ссылку на продукт
        product_link = None
        for a in soup.find_all("a", href=True):
            if "/catalog/product/" in a["href"]:
                product_link = urljoin("https://tandoor.ru", a["href"])
                break

        if not product_link:
            # Пробуем открыть каталог
            print("[*] Продукты на главной не найдены, открываем каталог...")
            await page.goto("https://tandoor.ru/catalog/", wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)
            html = await page.content()
            soup = BeautifulSoup(html, "lxml")
            for a in soup.find_all("a", href=True):
                if "/catalog/product/" in a["href"]:
                    product_link = urljoin("https://tandoor.ru", a["href"])
                    break

        if not product_link:
            # Берём хардкод
            product_link = "https://tandoor.ru/catalog/product/870/"

        print(f"[*] Открываем продукт: {product_link}")
        await page.goto(product_link, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(3)

        # Скроллим для lazy-load
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)
        await page.evaluate("window.scrollTo(0, 0)")

        html = await page.content()

        # Сохраним полный HTML
        with open("tandoor_product_full.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("[*] Полный HTML сохранён в tandoor_product_full.html")

        soup = BeautifulSoup(html, "lxml")

        result = {}

        # === ЗАГОЛОВОК ===
        print("\n" + "=" * 60)
        print("1. ЗАГОЛОВОК")
        print("=" * 60)
        h1 = soup.select_one("h1")
        title = h1.get_text(strip=True) if h1 else ""
        print(f"   Текст: {title}")
        print(f"   Классы: {h1.get('class', []) if h1 else 'N/A'}")
        h1_parent = h1.find_parent() if h1 else None
        if h1_parent:
            print(f"   Родитель: <{h1_parent.name}> class={h1_parent.get('class', [])}")
        result["title"] = title
        result["title_html"] = str(h1) if h1 else None

        # === ЦЕНА ===
        print("\n" + "=" * 60)
        print("2. ЦЕНА")
        print("=" * 60)
        price_candidates = soup.select(
            "span[itemprop='price'], "
            ".Product-description__price-value, "
            ".price-value, "
            ".Product-description__item-price-value, "
            "[data-price]"
        )
        print(f"   Найдено вариантов: {len(price_candidates)}")
        for i, el in enumerate(price_candidates):
            print(f"   [{i}] <{el.name}> class={el.get('class', [])} text='{el.get_text(strip=True)}'")
            print(f"       data: {el.attrs}")
        result["price_elements"] = [
            {"tag": el.name, "class": el.get("class", []), "text": el.get_text(strip=True), "attrs": el.attrs}
            for el in price_candidates
        ]

        # === ОПИСАНИЕ / ПОДЗАГОЛОВОК ===
        print("\n" + "=" * 60)
        print("3. ОПИСАНИЕ / ПОДЗАГОЛОВОК")
        print("=" * 60)
        desc_candidates = soup.select(
            ".Product-description__subtitle, "
            ".product-subtitle, "
            ".Product__description, "
            "[itemprop='description'], "
            "meta[name='description']"
        )
        for el in desc_candidates:
            if el.name == "meta":
                print(f"   <{el.name}> content='{el.get('content', '')[:200]}'")
            else:
                print(f"   <{el.name}> class={el.get('class', [])} text='{el.get_text(strip=True)[:200]}'")
        result["description_elements"] = [
            {"tag": el.name, "class": el.get("class", []), "text": el.get_text(strip=True)[:500]}
            for el in desc_candidates
        ]

        # === SKU / АРТИКУЛ ===
        print("\n" + "=" * 60)
        print("4. SKU / АРТИКУЛ")
        print("=" * 60)
        sku_candidates = soup.select(
            ".Product-description__sku, "
            ".product-sku, "
            "[data-sku], "
            "meta[property='product:sku'], "
            "meta[itemprop='sku']"
        )
        for el in sku_candidates:
            if el.name == "meta":
                print(f"   <{el.name}> property={el.get('property')} content='{el.get('content', '')}'")
            else:
                print(f"   <{el.name}> class={el.get('class', [])} text='{el.get_text(strip=True)}'")
        result["sku_elements"] = [
            {"tag": el.name, "class": el.get("class", []), "text": el.get_text(strip=True), "content": el.get("content", "")}
            for el in sku_candidates
        ]

        # === ИЗОБРАЖЕНИЯ / ГАЛЕРЕЯ ===
        print("\n" + "=" * 60)
        print("5. ИЗОБРАЖЕНИЯ / ГАЛЕРЕЯ")
        print("=" * 60)
        gallery_blocks = soup.select(
            ".Product-gallery, "
            ".product-gallery, "
            ".Product-description__gallery, "
            ".swiper, "
            "[class*='gallery']"
        )
        print(f"   Блоки галереи: {len(gallery_blocks)}")
        for gb in gallery_blocks:
            print(f"   <{gb.name}> class={gb.get('class', [])}")

        all_product_imgs = []
        # Все img на странице
        all_imgs = soup.select("img")
        print(f"   Всего img на странице: {len(all_imgs)}")

        for img in all_imgs[:30]:  # Первые 30
            src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or ""
            parent_classes = []
            parent = img.find_parent()
            for _ in range(3):
                if parent:
                    cls = parent.get("class", [])
                    if cls:
                        parent_classes.extend(cls)
                    parent = parent.find_parent()
                else:
                    break
            img_info = {
                "src": src,
                "srcset": img.get("srcset", ""),
                "alt": img.get("alt", ""),
                "width": img.get("width"),
                "height": img.get("height"),
                "class": img.get("class", []),
                "parent_classes": list(set(parent_classes))[:10],
            }
            all_product_imgs.append(img_info)

        result["gallery_count"] = len(gallery_blocks)
        result["total_images"] = len(all_imgs)
        result["images"] = all_product_imgs

        # === БЛОК ХАРАКТЕРИСТИК (dl/dt/dd) ===
        print("\n" + "=" * 60)
        print("6. ХАРАКТЕРИСТИКИ (dl/dt/dd)")
        print("=" * 60)
        char_blocks = soup.select("dl")
        print(f"   Блоков <dl>: {len(char_blocks)}")
        chars = {}
        for dl in char_blocks:
            dt = dl.select_one("dt")
            dd = dl.select_one("dd")
            if dt and dd:
                name = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                chars[name] = value
                print(f"   {name}: {value}")
        result["characteristics"] = chars

        # === СПЕЦИФИКАЦИИ: РАЗМЕР (size-specification) ===
        print("\n" + "=" * 60)
        print("7. РАЗМЕРЫ (.Product-description__size-specification)")
        print("=" * 60)
        size_block = soup.select_one(".Product-description__size-specification")
        if size_block:
            print(f"   Блок найден: <{size_block.name}> class={size_block.get('class', [])}")
            size_block_html = str(size_block)
            print(f"   HTML (первые 1000 символов): {size_block_html[:1000]}")
            labels = size_block.select("label")
            print(f"   Лейблов: {len(labels)}")
            sizes = []
            for lbl in labels:
                radio = lbl.select_one("input[type='radio']")
                span = lbl.select_one("span")
                if radio and span:
                    val = radio.get("value", "")
                    span_text = span.get_text(strip=True)
                    title_attr = lbl.get("title", "")
                    sizes.append({
                        "span_text": span_text,
                        "radio_value": val,
                        "label_title": title_attr,
                    })
                    print(f"     Размер: '{span_text}' URL={val} title='{title_attr}'")
            result["sizes"] = sizes
        else:
            result["sizes"] = "Блок НЕ найден"

        # === СПЕЦИФИКАЦИИ: ТИП ДВЕРИ (type-specification) ===
        print("\n" + "=" * 60)
        print("8. ТИП ДВЕРИ (.Product-description__type-specification)")
        print("=" * 60)
        type_block = soup.select_one(".Product-description__type-specification")
        if type_block:
            print(f"   Блок найден: class={type_block.get('class', [])}")
            print(f"   HTML (первые 1000): {str(type_block)[:1000]}")
            labels = type_block.select("label")
            types = []
            for lbl in labels:
                radio = lbl.select_one("input[type='radio']")
                span = lbl.select_one("span")
                if radio:
                    val = radio.get("value", "")
                    span_text = span.get_text(strip=True) if span else ""
                    title_attr = lbl.get("title", "")
                    is_checked = radio.get("checked") is not None
                    types.append({
                        "span_text": span_text,
                        "radio_value": val,
                        "label_title": title_attr,
                        "checked": is_checked,
                    })
                    check_mark = " (выбран)" if is_checked else ""
                    print(f"     Тип: '{span_text}' URL={val} title='{title_attr}'{check_mark}")
            result["door_types"] = types
        else:
            result["door_types"] = "Блок НЕ найден"

        # === СПЕЦИФИКАЦИИ: ЦВЕТ (color-specification) ===
        print("\n" + "=" * 60)
        print("9. ЦВЕТ (.Product-description__color-specification)")
        print("=" * 60)
        color_block = soup.select_one(".Product-description__color-specification")
        if color_block:
            print(f"   Блок найден: class={color_block.get('class', [])}")
            print(f"   HTML (первые 1000): {str(color_block)[:1000]}")
            labels = color_block.select("label")
            colors = []
            for lbl in labels:
                radio = lbl.select_one("input[type='radio']")
                span = lbl.select_one("span")
                if radio:
                    val = radio.get("value", "")
                    span_text = span.get_text(strip=True) if span else ""
                    title_attr = lbl.get("title", "")
                    is_checked = radio.get("checked") is not None
                    colors.append({
                        "span_text": span_text,
                        "radio_value": val,
                        "label_title": title_attr,
                        "checked": is_checked,
                    })
                    check_mark = " (выбран)" if is_checked else ""
                    print(f"     Цвет: '{span_text}' URL={val} title='{title_attr}'{check_mark}")
            result["colors"] = colors
        else:
            result["colors"] = "Блок НЕ найден"

        # === СПЕЦИФИКАЦИИ: НАПРАВЛЕНИЕ ОТКРЫВАНИЯ ===
        print("\n" + "=" * 60)
        print("10. НАПРАВЛЕНИЕ ОТКРЫВАНИЯ")
        print("=" * 60)
        open_block = soup.select_one(
            ".Product-description__open-specification, "
            ".Product-description__direction-specification, "
            ".Product-description__side-specification"
        )
        if open_block:
            print(f"   Блок найден: class={open_block.get('class', [])}")
            print(f"   HTML (первые 1000): {str(open_block)[:1000]}")
            labels = open_block.select("label")
            directions = []
            for lbl in labels:
                radio = lbl.select_one("input[type='radio']")
                span = lbl.select_one("span")
                if radio:
                    val = radio.get("value", "")
                    span_text = span.get_text(strip=True) if span else ""
                    title_attr = lbl.get("title", "")
                    is_checked = radio.get("checked") is not None
                    directions.append({
                        "span_text": span_text,
                        "radio_value": val,
                        "label_title": title_attr,
                        "checked": is_checked,
                    })
                    check_mark = " (выбран)" if is_checked else ""
                    print(f"     Направление: '{span_text}' URL={val} title='{title_attr}'{check_mark}")
            result["directions"] = directions
        else:
            # Поищем все блоки с Radio-btn
            radio_blocks = soup.select("[class*='Radio-btn']")
            print(f"   Основной блок НЕ найден. Всего Radio-btn блоков: {len(radio_blocks)}")
            for rb in radio_blocks[:10]:
                parent = rb.find_parent()
                parent_cls = parent.get("class", []) if parent else []
                print(f"     <{rb.name}> class={rb.get('class', [])} parent_class={parent_cls}")
            result["directions"] = "Блок НЕ найден"

        # === СПЕЦИФИКАЦИИ: ПОГОНАЖ/КОЛЛЕКЦИИ (molding-specification) ===
        print("\n" + "=" * 60)
        print("11. ПОГОНАЖ / СОВМЕСТИМЫЕ КОЛЛЕКЦИИ")
        print("=" * 60)
        mold_block = soup.select_one(
            ".Product-description__molding-specification, "
            ".molding-specification, "
            "[class*='molding']"
        )
        if mold_block:
            print(f"   Блок найден: class={mold_block.get('class', [])}")
            print(f"   HTML (первые 500): {str(mold_block)[:500]}")
            item_labels = mold_block.select("label, .Radio-btn__label")
            molding_items = []
            for lbl in item_labels:
                text = lbl.get_text(strip=True)
                molding_items.append(text)
                print(f"     '{text}'")
            result["molding"] = molding_items
        else:
            result["molding"] = "Блок НЕ найден"

        # === ВСЕ блоки спецификаций (для полного обзора) ===
        print("\n" + "=" * 60)
        print("12. ВСЕ БЛОКИ СПЕЦИФИКАЦИЙ")
        print("=" * 60)
        all_spec_blocks = soup.select("[class*='specification']")
        print(f"   Всего блоков: {len(all_spec_blocks)}")
        for sb in all_spec_blocks:
            cls = sb.get("class", [])
            print(f"   <{sb.name}> class={cls}")
            labels = sb.select("label")
            print(f"     Лейблов: {len(labels)}")
            first_text = labels[0].get_text(strip=True)[:50] if labels else "N/A"
            print(f"     Первый лейбл: '{first_text}'")
        result["all_specifications"] = [
            {
                "tag": sb.name,
                "class": sb.get("class", []),
                "labels_count": len(sb.select("label")),
            }
            for sb in all_spec_blocks
        ]

        # === META-СВОЙСТВА (OG, Schema.org) ===
        print("\n" + "=" * 60)
        print("13. META-СВОЙСТВА (OG, Schema.org)")
        print("=" * 60)
        og_tags = soup.select('meta[property^="og:"], meta[property^="product:"]')
        for tag in og_tags:
            prop = tag.get("property", "")
            content = tag.get("content", "")
            print(f"   {prop}: {content[:200]}")
        
        # Schema.org JSON-LD
        json_ld = soup.select("script[type='application/ld+json']")
        schema_data = []
        for script in json_ld:
            content = script.string or ""
            if content:
                try:
                    data = json.loads(content)
                    schema_data.append(data)
                    print(f"   Schema.org: {json.dumps(data, ensure_ascii=False)[:500]}")
                except:
                    print(f"   Schema.org (нельзя парсить JSON): {content[:200]}")
        result["og_tags"] = [{"property": t.get("property"), "content": t.get("content", "")} for t in og_tags]
        result["schema_org"] = schema_data

        # Сохраним результат
        with open("tandoor_product_audit.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        print("\n[*] Результат сохранён в tandoor_product_audit.json")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())