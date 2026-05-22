"""Debug: check why vlagostoykie-dveri is considered leaf."""
from src.database.session import get_session
from src.database.models import Category

with get_session() as s:
    # Find the vlagostoykie-dveri category
    cat = s.query(Category).filter(
        Category.url.like('%vlagostoykie-dveri%')
    ).first()
    
    if cat:
        print(f"Category id={cat.id}, name={cat.name}, url={cat.url}, parent_id={cat.parent_id}")
        
        # Check if it has children
        children = s.query(Category).filter(
            Category.parent_id == cat.id
        ).all()
        print(f"\nChildren: {len(children)}")
        for c in children:
            print(f"  id={c.id} name={c.name} url={c.url}")
            
            # Grandchildren
            gc = s.query(Category).filter(Category.parent_id == c.id).all()
            for g in gc:
                print(f"    gc id={g.id} name={g.name} url={g.url}")
    else:
        print("Category not found")
        
    # Also check supplier_id
    print(f"\nAll categories with 'vlago' in url or name:")
    for c in s.query(Category).all():
        if 'vlago' in (c.url or '').lower() or 'vlago' in (c.name or '').lower():
            print(f"  id={c.id} supplier_id={c.supplier_id} name={c.name} url={c.url} parent_id={c.parent_id}")