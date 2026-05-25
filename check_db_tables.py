from src.database.session import engine
from sqlalchemy import text

conn = engine.connect()
result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
tables = [r[0] for r in result.fetchall()]
print('Tables:', tables)

# Check record counts
for table in tables:
    count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    print(f"  {table}: {count} records")

conn.close()