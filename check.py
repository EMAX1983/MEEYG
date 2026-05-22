# check.py
from dotenv import load_dotenv
import os, sqlcipher3 as sqlite3

load_dotenv()
key = os.getenv('DB_KEY')

c = sqlite3.connect('data/meeyg.db')
c.execute(f"PRAGMA key = '{key}'")

print('Категорий:', c.execute('SELECT COUNT(*) FROM categories').fetchone()[0])
print('Товаров:', c.execute('SELECT COUNT(*) FROM products').fetchone()[0])
print('Атрибутов:', c.execute('SELECT COUNT(*) FROM product_attributes').fetchone()[0])

# Проверим поля в products
print('\nПоля в products:')
for col in c.execute('PRAGMA table_info(products)'):
    print(f'  {col[1]} ({col[2]})')

c.close()