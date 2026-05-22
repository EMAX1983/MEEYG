import asyncio
from playwright.async_api import async_playwright

async def intercept_requests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Видим браузер для отладки
        context = await browser.new_context()
        page = await context.new_page()
        
        # Слушаем все запросы
        page.on("request", lambda request: print(f">> {request.method} {request.url}"))
        
        await page.goto("https://tandoor.ru/catalog/product/nova-bukle-grafit-rivera-ays-860kh2050-levaya/")
        await asyncio.sleep(5)
        await browser.close()

asyncio.run(intercept_requests())
