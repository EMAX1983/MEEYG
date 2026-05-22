from src.database.session import get_session
from src.database.models import Product, ProductAttribute

with get_session() as s:
    products = s.query(Product).filter(Product.supplier_id == 1).order_by(Product.id.desc()).limit(10).all()
    for p in products:
        print(f'ID:{p.id} | Parent:{p.parent_product_id} | {p.title[:70]}')
    print('---')
    for p in products:
        attrs = s.query(ProductAttribute).filter_by(product_id=p.id).all()
        for a in attrs:
            print(f'  ID:{p.id} Attr: {a.name} = {a.value}')
