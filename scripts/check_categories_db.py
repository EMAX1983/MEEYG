"""Check category tree structure in DB."""
from src.database.session import get_session
from src.database.models import Category, Supplier
import json

def build_tree(cats, parent_id=0, depth=0):
    res = []
    for c in cats:
        if c.parent_id == parent_id:
            entry = {"id": c.id, "name": c.name, "url": c.url, "depth": depth}
            children = build_tree(cats, c.id, depth + 1)
            if children:
                entry["children"] = children
            res.append(entry)
    return res


with get_session() as s:
    suppliers = s.query(Supplier).all()
    print(f"Suppliers: {[(x.id, x.name) for x in suppliers]}")

    sup = suppliers[0] if suppliers else None
    if sup:
        cats = s.query(Category).filter(Category.supplier_id == sup.id).all()
        print(f"\nTotal categories for '{sup.name}': {len(cats)}")

        tree = build_tree(cats)
        print(json.dumps(tree, indent=2, ensure_ascii=False)[:5000])

        # Count leaf categories (no children)
        parent_ids = set(c.parent_id for c in cats)
        leaf_cats = [c for c in cats if c.id not in parent_ids]
        print(f"\nLeaf categories (no children): {len(leaf_cats)}")
        for c in leaf_cats[:15]:
            print(f"  id={c.id} {c.name}: {c.url}")
        
        # Check total products in DB
        from src.database.models import Product
        products = s.query(Product).all()
        print(f"\nTotal products in DB: {len(products)}")
        if products:
            for p in products[:5]:
                print(f"  id={p.id} supplier_id={p.supplier_id} title={p.title[:60]} cat_id={p.category_id}")