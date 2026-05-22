from datetime import datetime

from sqlalchemy import select, update, delete

from src.database.models import Supplier


def create_supplier(session, name: str, base_url: str) -> Supplier:
    existing = session.execute(
        select(Supplier).where(Supplier.name == name)
    ).scalar_one_or_none()
    if existing:
        raise ValueError(f"Supplier with name '{name}' already exists")

    supplier = Supplier(name=name, base_url=base_url)
    session.add(supplier)
    session.flush()
    return supplier


def get_all_suppliers(session, active_only: bool = True) -> list[Supplier]:
    stmt = select(Supplier)
    if active_only:
        stmt = stmt.where(Supplier.is_active == True)
    stmt = stmt.order_by(Supplier.name)
    return list(session.execute(stmt).scalars().all())


def get_supplier_by_id(session, supplier_id: int) -> Supplier | None:
    return session.execute(
        select(Supplier).where(Supplier.id == supplier_id)
    ).scalar_one_or_none()


def get_supplier_by_name(session, name: str) -> Supplier | None:
    return session.execute(
        select(Supplier).where(Supplier.name == name)
    ).scalar_one_or_none()


def update_supplier(session, supplier_id: int, **kwargs) -> Supplier | None:
    supplier = get_supplier_by_id(session, supplier_id)
    if not supplier:
        return None

    if "name" in kwargs:
        new_name = kwargs["name"]
        if new_name != supplier.name:
            duplicate = session.execute(
                select(Supplier).where(
                    Supplier.name == new_name,
                    Supplier.id != supplier_id,
                )
            ).scalar_one_or_none()
            if duplicate:
                raise ValueError(f"Supplier with name '{new_name}' already exists")

    kwargs["updated_at"] = datetime.utcnow()

    session.execute(
        update(Supplier)
        .where(Supplier.id == supplier_id)
        .values(**kwargs)
    )
    session.flush()
    return get_supplier_by_id(session, supplier_id)


def delete_supplier(session, supplier_id: int) -> bool:
    supplier = get_supplier_by_id(session, supplier_id)
    if not supplier:
        return False

    session.execute(
        update(Supplier)
        .where(Supplier.id == supplier_id)
        .values(is_active=False, updated_at=datetime.utcnow())
    )
    session.flush()
    return True


def hard_delete_supplier(session, supplier_id: int) -> bool:
    result = session.execute(
        delete(Supplier).where(Supplier.id == supplier_id)
    )
    session.flush()
    return result.rowcount > 0
