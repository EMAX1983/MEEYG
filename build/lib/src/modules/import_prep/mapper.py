import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from src.core.logger import logger

logger_mapper = logging.getLogger("meeyg.import_prep")

WP_ALL_IMPORT_FIELDS = {
    "post_title": {"required": True, "type": "string", "label": "Product Title"},
    "sku": {"required": True, "type": "string", "label": "SKU"},
    "regular_price": {"required": True, "type": "float", "label": "Regular Price"},
    "sale_price": {"required": False, "type": "float", "label": "Sale Price"},
    "stock": {"required": True, "type": "int", "label": "Stock Quantity"},
    "stock_status": {"required": True, "type": "string", "label": "Stock Status"},
    "categories": {"required": False, "type": "string", "label": "Categories"},
    "attributes": {"required": False, "type": "string", "label": "Attributes"},
    "images": {"required": False, "type": "string", "label": "Images"},
    "short_description": {"required": False, "type": "string", "label": "Short Description"},
    "description": {"required": False, "type": "string", "label": "Description"},
    "manage_stock": {"required": False, "type": "string", "label": "Manage Stock"},
    "backorders": {"required": False, "type": "string", "label": "Backorders"},
    "tax_status": {"required": False, "type": "string", "label": "Tax Status"},
    "weight": {"required": False, "type": "float", "label": "Weight"},
}

DB_FIELDS = {
    "id": "Product ID",
    "title": "Product Title",
    "external_sku": "SKU",
    "price": "Price",
    "currency": "Currency",
    "is_available": "Availability",
    "description": "Description",
    "category_name": "Category",
    "image_urls": "Image URLs",
    "attributes": "Attributes",
    "supplier_name": "Supplier",
    "created_at": "Created At",
    "updated_at": "Updated At",
}

RULE_TYPES = {
    "null_replacement": "Replace NULL/empty values with a specified string",
    "price_round": "Round prices to N decimal places",
    "price_markup": "Apply percentage markup to prices",
    "merge_attributes": "Merge all attributes into a single string",
    "sku_prefix": "Add prefix to SKU",
    "sku_suffix": "Add suffix to SKU",
    "stock_default": "Set default stock value for NULL",
    "category_separator": "Set category separator character",
    "title_trim": "Trim and normalize title whitespace",
    "currency_map": "Map currency codes to target currency",
}


@dataclass
class ValidationIssue:
    product_id: int
    field: str
    message: str
    severity: str = "warning"


@dataclass
class MappingConfig:
    field_mapping: dict[str, str] = field(default_factory=dict)
    rules: list[dict] = field(default_factory=list)
    name: str = ""
    description: str = ""

    def map_field(self, db_field: str) -> Optional[str]:
        return self.field_mapping.get(db_field)

    def add_rule(self, rule_type: str, **kwargs) -> None:
        rule = {"type": rule_type, **kwargs}
        self.rules.append(rule)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "field_mapping": self.field_mapping,
            "rules": self.rules,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MappingConfig":
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            field_mapping=data.get("field_mapping", {}),
            rules=data.get("rules", []),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "MappingConfig":
        return cls.from_dict(json.loads(json_str))


class RuleEngine:
    def __init__(self, rules: list[dict]):
        self.rules = rules

    def apply(self, product_data: dict[str, Any]) -> dict[str, Any]:
        result = dict(product_data)
        for rule in self.rules:
            rule_type = rule.get("type")
            if rule_type == "null_replacement":
                result = self._apply_null_replacement(result, rule)
            elif rule_type == "price_round":
                result = self._apply_price_round(result, rule)
            elif rule_type == "price_markup":
                result = self._apply_price_markup(result, rule)
            elif rule_type == "merge_attributes":
                result = self._apply_merge_attributes(result, rule)
            elif rule_type == "sku_prefix":
                result = self._apply_sku_prefix(result, rule)
            elif rule_type == "sku_suffix":
                result = self._apply_sku_suffix(result, rule)
            elif rule_type == "stock_default":
                result = self._apply_stock_default(result, rule)
            elif rule_type == "title_trim":
                result = self._apply_title_trim(result, rule)
            elif rule_type == "currency_map":
                result = self._apply_currency_map(result, rule)
        return result

    @staticmethod
    def _apply_null_replacement(data: dict, rule: dict) -> dict:
        target = rule.get("target", "")
        replacement = rule.get("replacement", "N/A")
        if target in data and (data[target] is None or data[target] == ""):
            data[target] = replacement
        return data

    @staticmethod
    def _apply_price_round(data: dict, rule: dict) -> dict:
        decimals = rule.get("decimals", 2)
        if "regular_price" in data and data["regular_price"] is not None:
            data["regular_price"] = round(float(data["regular_price"]), decimals)
        if "sale_price" in data and data["sale_price"] is not None:
            data["sale_price"] = round(float(data["sale_price"]), decimals)
        return data

    @staticmethod
    def _apply_price_markup(data: dict, rule: dict) -> dict:
        markup_pct = rule.get("markup", 0)
        if "regular_price" in data and data["regular_price"] is not None:
            data["regular_price"] = round(float(data["regular_price"]) * (1 + markup_pct / 100), 2)
        return data

    @staticmethod
    def _apply_merge_attributes(data: dict, rule: dict) -> dict:
        separator = rule.get("separator", " | ")
        attrs = data.get("attributes", {})
        if isinstance(attrs, dict):
            parts = [f"{k}: {v}" for k, v in attrs.items() if v]
            data["attributes"] = separator.join(parts)
        elif isinstance(attrs, str):
            pass
        return data

    @staticmethod
    def _apply_sku_prefix(data: dict, rule: dict) -> dict:
        prefix = rule.get("prefix", "")
        if "sku" in data and data["sku"]:
            data["sku"] = f"{prefix}{data['sku']}"
        return data

    @staticmethod
    def _apply_sku_suffix(data: dict, rule: dict) -> dict:
        suffix = rule.get("suffix", "")
        if "sku" in data and data["sku"]:
            data["sku"] = f"{data['sku']}{suffix}"
        return data

    @staticmethod
    def _apply_stock_default(data: dict, rule: dict) -> dict:
        default_val = rule.get("default", 0)
        if "stock" in data and (data["stock"] is None or data["stock"] == ""):
            data["stock"] = default_val
        return data

    @staticmethod
    def _apply_title_trim(data: dict, rule: dict) -> dict:
        import re
        if "post_title" in data and data["post_title"]:
            data["post_title"] = re.sub(r"\s+", " ", str(data["post_title"])).strip()
        return data

    @staticmethod
    def _apply_currency_map(data: dict, rule: dict) -> dict:
        mapping = rule.get("mapping", {})
        if "currency" in data and data["currency"] in mapping:
            data["currency"] = mapping[data["currency"]]
        return data


class FieldMapper:
    def __init__(self, config: Optional[MappingConfig] = None):
        self.config = config or MappingConfig()
        self.rule_engine = RuleEngine(self.config.rules)
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []

    def set_mapping(self, db_field: str, wp_field: str) -> None:
        self.config.field_mapping[db_field] = wp_field
        self._redo_stack.clear()

    def remove_mapping(self, db_field: str) -> None:
        self.config.field_mapping.pop(db_field, None)
        self._redo_stack.clear()

    def get_unmapped_wp_fields(self) -> list[str]:
        mapped = set(self.config.field_mapping.values())
        return [
            wp_field
            for wp_field, meta in WP_ALL_IMPORT_FIELDS.items()
            if meta["required"] and wp_field not in mapped
        ]

    def get_mapped_fields(self) -> dict[str, str]:
        return dict(self.config.field_mapping)

    def transform_product(self, product_data: dict[str, Any]) -> dict[str, Any]:
        self._undo_stack.append(dict(product_data))
        if len(self._undo_stack) > 100:
            self._undo_stack = self._undo_stack[-50:]

        result = {}
        for db_field, wp_field in self.config.field_mapping.items():
            value = product_data.get(db_field)
            result[wp_field] = value

        result = self.rule_engine.apply(result)
        return result

    def validate_product(self, product_data: dict[str, Any], product_id: int) -> list[ValidationIssue]:
        issues = []

        for wp_field, meta in WP_ALL_IMPORT_FIELDS.items():
            if not meta["required"]:
                continue
            value = product_data.get(wp_field)
            if value is None or value == "":
                issues.append(ValidationIssue(
                    product_id=product_id,
                    field=wp_field,
                    message=f"Required field '{meta['label']}' is empty",
                    severity="error",
                ))

            if meta["type"] == "float" and value is not None:
                try:
                    float(value)
                except (ValueError, TypeError):
                    issues.append(ValidationIssue(
                        product_id=product_id,
                        field=wp_field,
                        message=f"Field '{meta['label']}' must be a number, got '{value}'",
                        severity="error",
                    ))

            if meta["type"] == "int" and value is not None:
                try:
                    int(value)
                except (ValueError, TypeError):
                    issues.append(ValidationIssue(
                        product_id=product_id,
                        field=wp_field,
                        message=f"Field '{meta['label']}' must be an integer, got '{value}'",
                        severity="error",
                    ))

        return issues

    def validate_batch(self, products: list[dict[str, Any]]) -> list[ValidationIssue]:
        all_issues = []
        seen_skus: dict[str, int] = {}

        for product in products:
            pid = product.get("id", 0)
            issues = self.validate_product(product, pid)
            all_issues.extend(issues)

            sku = product.get("sku")
            if sku:
                if sku in seen_skus:
                    all_issues.append(ValidationIssue(
                        product_id=pid,
                        field="sku",
                        message=f"Duplicate SKU '{sku}' (also in product {seen_skus[sku]})",
                        severity="error",
                    ))
                else:
                    seen_skus[sku] = pid

        return all_issues

    def save_template(self, db_session, name: str, description: str = "") -> int:
        from src.database.models import MappingTemplate

        template = MappingTemplate(
            name=name,
            description=description,
            field_mapping=json.dumps(self.config.field_mapping, ensure_ascii=False),
            rules=json.dumps(self.config.rules, ensure_ascii=False),
        )
        db_session.add(template)
        db_session.flush()
        logger_mapper.info(f"Mapping template '{name}' saved (id={template.id})")
        return template.id

    def load_template(self, db_session, template_id: int) -> bool:
        from src.database.models import MappingTemplate

        template = db_session.query(MappingTemplate).filter(
            MappingTemplate.id == template_id
        ).first()

        if not template:
            return False

        self.config.field_mapping = template.get_field_mapping()
        self.config.rules = template.get_rules()
        self.config.name = template.name
        self.config.description = template.description or ""
        self.rule_engine = RuleEngine(self.config.rules)
        logger_mapper.info(f"Mapping template '{template.name}' loaded")
        return True

    def list_templates(self, db_session) -> list:
        from src.database.models import MappingTemplate

        return db_session.query(MappingTemplate).order_by(
            MappingTemplate.updated_at.desc()
        ).all()

    def delete_template(self, db_session, template_id: int) -> bool:
        from src.database.models import MappingTemplate

        template = db_session.query(MappingTemplate).filter(
            MappingTemplate.id == template_id
        ).first()

        if template:
            db_session.delete(template)
            logger_mapper.info(f"Mapping template '{template.name}' deleted")
            return True
        return False

    def undo(self) -> Optional[dict]:
        if len(self._undo_stack) < 2:
            return None
        current = self._undo_stack.pop()
        self._redo_stack.append(current)
        return self._undo_stack[-1]

    def redo(self) -> Optional[dict]:
        if not self._redo_stack:
            return None
        state = self._redo_stack.pop()
        self._undo_stack.append(state)
        return state

    def mark_ready_for_export(self, db_session, product_ids: list[int]) -> int:
        from src.database.models import Product

        result = db_session.query(Product).filter(
            Product.id.in_(product_ids)
        ).update(
            {"is_ready_for_export": True, "updated_at": datetime.utcnow()},
            synchronize_session="fetch",
        )
        db_session.flush()
        logger_mapper.info(f"Marked {result} products as ready for export")
        return result

    def mark_not_ready(self, db_session, product_ids: list[int]) -> int:
        from src.database.models import Product

        result = db_session.query(Product).filter(
            Product.id.in_(product_ids)
        ).update(
            {"is_ready_for_export": False, "updated_at": datetime.utcnow()},
            synchronize_session="fetch",
        )
        db_session.flush()
        logger_mapper.info(f"Marked {result} products as not ready for export")
        return result
