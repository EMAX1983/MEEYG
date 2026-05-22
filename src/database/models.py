import json
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, String, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    base_url = Column(String(512), nullable=False, unique=True)
    is_active = Column(Boolean, default=True, index=True)
    last_discovery_run = Column(DateTime, nullable=True)
    last_scrape_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # 🆕 Авторизация для protected-сайтов
    auth_url = Column(String(512), nullable=True, comment="URL страницы входа (например /login)")
    auth_username = Column(String(255), nullable=True, comment="Логин для авторизации")
    auth_password = Column(Text, nullable=True, comment="Пароль для авторизации (в Base64)")
    auth_method = Column(String(50), nullable=True, default="cookie", comment="Метод авторизации: cookie | token")
    auth_token = Column(Text, nullable=True, comment="API токен (если метод token)")

    categories = relationship("Category", back_populates="supplier", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_suppliers_name_is_active", "name", "is_active"),)

    def __repr__(self) -> str:
        return (
            f"<Supplier(id={self.id}, name={self.name!r}, "
            f"base_url={self.base_url!r}, is_active={self.is_active})>"
        )


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    external_id = Column(String(255), nullable=True)
    name = Column(String(512), nullable=False)
    url = Column(String(1024), nullable=False)
    xpath_selector = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    product_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    supplier = relationship("Supplier", back_populates="categories")
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_categories_supplier_parent", "supplier_id", "parent_id"),
        Index("ix_categories_supplier_name", "supplier_id", "name"),
    )

    def __repr__(self) -> str:
        return (
            f"<Category(id={self.id}, name={self.name!r}, "
            f"supplier_id={self.supplier_id}, parent_id={self.parent_id})>"
        )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    parent_product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # 🆕 НОВОЕ ПОЛЕ: Совместимые коллекции погонажа (JSON-массив)
    compatible_collections = Column(Text, nullable=True, comment="JSON array of collections, e.g. ['FLYDOORS>MONE']")
    
    external_sku = Column(String(255), nullable=True, index=True)
    title = Column(String(1024), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    is_available = Column(Boolean, default=True)
    is_ready_for_export = Column(Boolean, default=False, index=True)
    image_urls = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    supplier = relationship("Supplier")
    category = relationship("Category", back_populates="products")
    parent = relationship("Product", remote_side=[id], backref="related_products")
    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_products_supplier_sku", "supplier_id", "external_sku"),
        Index("ix_products_supplier_category", "supplier_id", "category_id"),
        Index("ix_products_price", "price"),
        Index("ix_products_available", "is_available"),
        Index("ix_products_ready", "is_ready_for_export"),
    )

    # --- Helpers для image_urls ---
    def get_image_urls(self) -> list[str]:
        if not self.image_urls:
            return []
        try:
            return json.loads(self.image_urls)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_image_urls(self, urls: list[str]) -> None:
        self.image_urls = json.dumps(urls, ensure_ascii=False)

    # --- Helpers для compatible_collections ---
    def get_compatible_collections(self) -> list[str]:
        """Возвращает список коллекций как Python list"""
        if not self.compatible_collections:
            return []
        try:
            return json.loads(self.compatible_collections)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_compatible_collections(self, collections: list[str]) -> None:
        """Сохраняет список коллекций в БД как JSON-строку"""
        self.compatible_collections = json.dumps(collections, ensure_ascii=False)

    def __repr__(self) -> str:
        return (
            f"<Product(id={self.id}, title={self.title!r}, "
            f"price={self.price}, currency={self.currency})>"
        )


class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)

    product = relationship("Product", back_populates="attributes")

    __table_args__ = (
        Index("ix_attr_product_name", "product_id", "name"),
    )

    def __repr__(self) -> str:
        return f"<ProductAttribute(id={self.id}, name={self.name!r}, value={self.value!r})>"


class ArchiveSnapshot(Base):
    __tablename__ = "archive_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    snapshot_type = Column(String(50), nullable=False, default="full")
    total_products = Column(Integer, default=0)
    total_categories = Column(Integer, default=0)
    total_price_sum = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    supplier = relationship("Supplier")
    items = relationship("ArchiveItem", back_populates="snapshot", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_snapshots_supplier_date", "supplier_id", "created_at"),
        Index("ix_snapshots_type", "snapshot_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<ArchiveSnapshot(id={self.id}, name={self.name!r}, "
            f"products={self.total_products}, type={self.snapshot_type})>"
        )


class ArchiveItem(Base):
    __tablename__ = "archive_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(Integer, ForeignKey("archive_snapshots.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    external_sku = Column(String(255), nullable=True)
    title = Column(String(1024), nullable=False)
    price = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)
    is_available = Column(Boolean, default=True)
    category_name = Column(String(512), nullable=True)
    image_urls = Column(Text, nullable=True)
    attributes_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    # 🆕 НОВЫЕ ПОЛЯ для полного экспорта
    manufacturer = Column(String(255), nullable=True, comment="Производитель (Supplier.name)")
    parent_sku = Column(String(255), nullable=True, comment="SKU родительского товара")
    collection = Column(String(255), nullable=True, comment="Коллекция товара")
    brand = Column(String(255), nullable=True, comment="Бренд (то же что manufacturer)")
    availability = Column(String(50), nullable=True, comment="в наличии / нет в наличии")
    stock_status = Column(String(50), nullable=True, comment="instock / outofstock")
    vendor = Column(String(255), nullable=True, comment="Vendor (то же что manufacturer)")
    description = Column(Text, nullable=True, comment="Полное описание товара")
    is_parent = Column(Boolean, default=False, comment="Является ли товар родителем (базовым)")

    snapshot = relationship("ArchiveSnapshot", back_populates="items")

    __table_args__ = (
        Index("ix_archive_items_snapshot_sku", "snapshot_id", "external_sku"),
        Index("ix_archive_items_price", "price"),
        Index("ix_archive_items_snapshot_id", "snapshot_id", "product_id"),
    )

    def get_image_urls(self) -> list[str]:
        if not self.image_urls:
            return []
        try:
            return json.loads(self.image_urls)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_attributes(self) -> dict[str, str]:
        if not self.attributes_json:
            return {}
        try:
            return json.loads(self.attributes_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    def __repr__(self) -> str:
        return f"<ArchiveItem(id={self.id}, title={self.title!r}, price={self.price}, manufacturer={self.manufacturer})>"


class MappingTemplate(Base):
    __tablename__ = "mapping_templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    field_mapping = Column(Text, nullable=False)
    rules = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def get_field_mapping(self) -> dict[str, str]:
        if not self.field_mapping:
            return {}
        try:
            return json.loads(self.field_mapping)
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_rules(self) -> list[dict]:
        if not self.rules:
            return []
        try:
            return json.loads(self.rules)
        except (json.JSONDecodeError, TypeError):
            return []

    def __repr__(self) -> str:
        return f"<MappingTemplate(id={self.id}, name={self.name!r})>"