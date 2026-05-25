"""Проверка категорий дверей в БД."""
from src.database.session import engine
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.database.models import ArchiveItem, Category

conn = engine.connect()

# Check categories
result = conn.execute(text("SELECT id, name, url FROM categories WHERE name LIKE '%входн%' OR name LIKE '%door%' OR name LIKE '%interior%' OR name LIKE '%межкомнатн%'"))
rows = result.fetchall()
print("=== Categories related to doors ===")
if rows:
    for row in rows:
        print(f"  id={row[0]}, name={row[1]}, url={row[2]}")
else:
    print("  No door-related categories found")

# Check ALL categories
result2 = conn.execute(text("SELECT id, name FROM categories ORDER BY name"))
print("\n=== All categories ===")
for row in result2.fetchall():
    print(f"  id={row[0]}, name={row[1]}")

# Check archive items with images and their categories
session = Session(engine)
items_with_images = session.query(ArchiveItem).filter(
    ArchiveItem.image_urls.isnot(None),
    ArchiveItem.image_urls != '[]',
    ArchiveItem.image_urls != ''
).limit(10).all()

print(f"\n=== Archive Items with images (showing 10) ===")
for item in items_with_images:
    import json
    try:
        imgs = json.loads(item.image_urls) if isinstance(item.image_urls, str) else item.image_urls
        img_count = len(imgs) if isinstance(imgs, list) else 0
    except:
        img_count = 0
    print(f"  id={item.product_id}, title={item.title[:40]}, category={item.category_name}, images={img_count}, is_parent={item.is_parent}")

session.close()
conn.close()

print("\n=== Checking if images are URLs or local paths ===")
conn2 = engine.connect()
result3 = conn2.execute(text("SELECT image_urls FROM archive_items WHERE image_urls IS NOT NULL AND image_urls != '[]' LIMIT 5"))
for row in result3.fetchall():
    print(f"  {row[0][:200]}...")
conn2.close()