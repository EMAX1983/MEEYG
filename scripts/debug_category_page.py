"""Debug: find actual product cards on category page."""
import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin, urlparse

async def check():
    category_url = "/catalog/mezhkomnatnye-dveri/po-pokrytiyu/dveri-iz-massiva/"
    base_url = "https://tandoor.ru"
    url = urljoin(base_url, category_url) if not category_url.startswith("http") else category_url

    print(f"Testing URL: {url}")
    print(f"Category path: {urlparse(url).path.rstrip('/')}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Get all links with href using page.evaluate (avoid eval_on_selector_all issues)
            links_data = await page.evaluate("""() => {
                const result = [];
                const allLinks = document.querySelectorAll('a[href]');
                for (const a of allLinks) {
                    const href = a.href || a.getAttribute('href');
                    if (href && href.includes('/catalog/')) {
                        result.push(href);
                    }
                }
                return result;
            }""")
            
            print(f"\nTotal /catalog/ links: {len(links_data)}")
            
            # Group by path depth to find product pages vs category pages
            depth_groups = {}
            for href in links_data:
                path = urlparse(href).path.rstrip('/')
                depth = len([s for s in path.split('/') if s])
                if depth not in depth_groups:
                    depth_groups[depth] = []
                depth_groups[depth].append(href)
            
            for depth in sorted(depth_groups.keys()):
                print(f"\nDepth {depth}: {len(depth_groups[depth])} links")
                for link in depth_groups[depth][:5]:
                    print(f"  {link}")
            
            # Try to find actual product cards on this page
            # Check if this is a leaf category (should contain products directly)
            cat_path = urlparse(url).path.rstrip('/')
            child_cat_links = [h for h in links_data if urlparse(h).path.rstrip('/').startswith(cat_path + '/')]
            print(f"\nLinks deeper than current category: {len(child_cat_links)}")
            
            if not child_cat_links:
                print("This is a leaf category - should contain product cards!")
                
                # Try selectors for product cards
                card_count = await page.evaluate("""() => {
                    const selectors = [
                        '.Catalog-list__item', '.Catalog-item', '.goods', '.Card', 
                        '.card', '.products .item', '[class*=product]',
                        '.Catalog-grid__item', '.Catalog-cards__item'
                    ];
                    const result = {};
                    for (const sel of selectors) {
                        try {
                            result[sel] = document.querySelectorAll(sel).length;
                        } catch(e) { result[sel] = 0; }
                    }
                    return result;
                }""")
                print(f"\nCard counts by selector: {card_count}")
                
                # Dump all class names from possible product card containers
                all_classes = await page.evaluate("""() => {
                    const classes = new Set();
                    for (const el of document.querySelectorAll('[class]')) {
                        for (const cls of el.classList) {
                            if (cls.includes('item') || cls.includes('Card') || cls.includes('product') || cls.includes('goods') || cls.includes('Card')) {
                                classes.add(cls);
                            }
                        }
                    }
                    return Array.from(classes);
                }""")
                print(f"\nRelevant class names found: {all_classes}")
                
                # Save HTML dump
                html = await page.content()
                with open("scripts/category_page_dump.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"\nSaved {len(html)} bytes to scripts/category_page_dump.html")
            
        except Exception as e:
            import traceback
            print(f"Error: {e}")
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(check())