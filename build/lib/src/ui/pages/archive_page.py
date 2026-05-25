import json
from datetime import datetime
from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QSortFilterProxyModel, QSize, Signal
from PySide6.QtGui import QAction, QColor, QKeySequence
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from src.database.models import Category, Product, Supplier
from src.database.session import get_session
from src.modules.import_prep.mapper import (
    DB_FIELDS,
    FieldMapper,
    MappingConfig,
    RuleEngine,
    WP_ALL_IMPORT_FIELDS,
)

PAGE_SIZE = 200


class ProductTableModel(QAbstractTableModel):
    _headers = ["ID", "SKU", "Название", "Цена", "Валюта", "Категория", "Доступен", "Готов", "Поставщик"]

    def __init__(self):
        super().__init__()
        self._products: list[dict] = []
        self._total_count = 0
        self._modified_cells: set[tuple[int, int]] = set()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._products)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        product = self._products[row]
        keys = ["id", "external_sku", "title", "price", "currency", "category_name", "is_available", "is_ready_for_export", "supplier_name"]

        if role == Qt.DisplayRole:
            key = keys[col]
            val = product.get(key)
            if key == "price":
                return f"{val:.2f}" if val is not None else ""
            if key == "is_available":
                return "Да" if val else "Нет"
            if key == "is_ready_for_export":
                return "Да" if val else "Нет"
            if val is None:
                return ""
            return str(val)

        if role == Qt.BackgroundRole:
            if (row, col) in self._modified_cells:
                return QColor(255, 255, 200)

        if role == Qt.TextAlignmentRole:
            if col in (0, 3):
                return Qt.AlignRight | Qt.AlignVCenter

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def load_page(self, supplier_id: Optional[int] = None, category_id: Optional[int] = None,
                  available_only: bool = False, search: str = "", page: int = 0) -> int:
        self._products.clear()
        self._modified_cells.clear()

        with get_session() as session:
            query = session.query(
                Product.id,
                Product.external_sku,
                Product.title,
                Product.price,
                Product.currency,
                Product.is_available,
                Product.is_ready_for_export,
                Category.name.label("category_name"),
                Supplier.name.label("supplier_name"),
            ).outerjoin(Category, Product.category_id == Category.id).outerjoin(
                Supplier, Product.supplier_id == Supplier.id
            )

            if supplier_id:
                query = query.filter(Product.supplier_id == supplier_id)
            if category_id:
                query = query.filter(Product.category_id == category_id)
            if available_only:
                query = query.filter(Product.is_available == True)
            if search:
                search_pattern = f"%{search}%"
                query = query.filter(
                    (Product.title.ilike(search_pattern)) |
                    (Product.external_sku.ilike(search_pattern))
                )

            self._total_count = query.count()

            products = query.order_by(Product.id).offset(page * PAGE_SIZE).limit(PAGE_SIZE).all()

            for p in products:
                self._products.append({
                    "id": p.id,
                    "external_sku": p.external_sku,
                    "title": p.title,
                    "price": p.price,
                    "currency": p.currency,
                    "is_available": p.is_available,
                    "is_ready_for_export": p.is_ready_for_export,
                    "category_name": p.category_name,
                    "supplier_name": p.supplier_name,
                })

        self.layoutChanged.emit()
        return self._total_count

    def get_product(self, row: int) -> Optional[dict]:
        if 0 <= row < len(self._products):
            return self._products[row]
        return None

    def get_selected_ids(self, rows: list[int]) -> list[int]:
        ids = []
        for row in rows:
            p = self.get_product(row)
            if p:
                ids.append(p["id"])
        return ids

    def mark_modified(self, row: int, col: int) -> None:
        self._modified_cells.add((row, col))
        idx = self.index(row, col)
        self.dataChanged.emit(idx, idx, [Qt.BackgroundRole])

    @property
    def total_count(self) -> int:
        return self._total_count

    @property
    def page_count(self) -> int:
        return (self._total_count + PAGE_SIZE - 1) // PAGE_SIZE


class ProductFilterProxy(QSortFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterKeyColumn(-1)


class EditProductDialog(QDialog):
    def __init__(self, product: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Редактирование товара #{product['id']}")
        self.setMinimumWidth(500)
        self._product = product
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._title_input = QLineEdit(self._product.get("title", ""))
        form.addRow("Название:", self._title_input)

        self._sku_input = QLineEdit(self._product.get("external_sku") or "")
        form.addRow("Артикул:", self._sku_input)

        self._price_input = QLineEdit(str(self._product.get("price") or ""))
        form.addRow("Цена:", self._price_input)

        self._currency_input = QLineEdit(self._product.get("currency") or "")
        form.addRow("Валюта:", self._currency_input)

        self._available_check = QCheckBox()
        self._available_check.setChecked(self._product.get("is_available", True))
        form.addRow("Доступен:", self._available_check)

        self._ready_check = QCheckBox()
        self._ready_check.setChecked(self._product.get("is_ready_for_export", False))
        form.addRow("Готов к экспорту:", self._ready_check)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Отмена")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_data(self) -> dict:
        return {
            "title": self._title_input.text().strip(),
            "external_sku": self._sku_input.text().strip() or None,
            "price": float(self._price_input.text()) if self._price_input.text() else None,
            "currency": self._currency_input.text().strip() or None,
            "is_available": self._available_check.isChecked(),
            "is_ready_for_export": self._ready_check.isChecked(),
        }


class MappingDialog(QDialog):
    def __init__(self, mapper: FieldMapper, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сопоставление полей — WP All Import")
        self.setMinimumSize(600, 500)
        self._mapper = mapper
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        tpl_row = QHBoxLayout()
        tpl_row.addWidget(QLabel("Шаблон:"))
        self._template_combo = QComboBox()
        self._load_templates()
        tpl_row.addWidget(self._template_combo)
        self._btn_load_tpl = QPushButton("Загрузить")
        self._btn_save_tpl = QPushButton("Сохранить")
        tpl_row.addWidget(self._btn_load_tpl)
        tpl_row.addWidget(self._btn_save_tpl)
        layout.addLayout(tpl_row)

        form = QFormLayout()
        self._mapping_widgets = {}
        for db_field, db_label in DB_FIELDS.items():
            combo = QComboBox()
            combo.addItem("— Не сопоставлено —")
            for wp_field, meta in WP_ALL_IMPORT_FIELDS.items():
                combo.addItem(f"{wp_field} ({meta['label']})", userData=wp_field)
            current_wp = self._mapper.config.field_mapping.get(db_field)
            if current_wp:
                idx = combo.findData(current_wp)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            form.addRow(f"{db_label} ({db_field}):", combo)
            self._mapping_widgets[db_field] = combo

        layout.addLayout(form)

        rules_group = QGroupBox("Правила")
        rules_layout = QVBoxLayout(rules_group)
        self._rules_list = QListWidget()
        for rule in self._mapper.config.rules:
            item = QListWidgetItem(f"{rule['type']}: {json.dumps({k:v for k,v in rule.items() if k != 'type'})}")
            self._rules_list.addItem(item)
        rules_layout.addWidget(self._rules_list)

        rules_btn_row = QHBoxLayout()
        self._btn_add_rule = QPushButton("Добавить правило")
        self._btn_remove_rule = QPushButton("Удалить правило")
        rules_btn_row.addWidget(self._btn_add_rule)
        rules_btn_row.addWidget(self._btn_remove_rule)
        rules_layout.addLayout(rules_btn_row)
        layout.addWidget(rules_group)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Сохранить сопоставление")
        cancel_btn = QPushButton("Отмена")
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self._btn_load_tpl.clicked.connect(self._on_load_template)
        self._btn_save_tpl.clicked.connect(self._on_save_template)
        self._btn_add_rule.clicked.connect(self._on_add_rule)
        self._btn_remove_rule.clicked.connect(self._on_remove_rule)
        save_btn.clicked.connect(self._on_save)
        cancel_btn.clicked.connect(self.reject)

    def _load_templates(self):
        self._template_combo.clear()
        try:
            with get_session() as session:
                templates = self._mapper.list_templates(session)
                for t in templates:
                    self._template_combo.addItem(t.name, userData=t.id)
        except Exception:
            pass

    def _on_load_template(self):
        tpl_id = self._template_combo.currentData()
        if tpl_id is None:
            return
        with get_session() as session:
            if self._mapper.load_template(session, tpl_id):
                self.accept()

    def _on_save_template(self):
        name, ok = QLineEdit.getText(self, "Сохранить шаблон", "Имя шаблона:")
        if ok and name:
            self._apply_mapping_from_ui()
            with get_session() as session:
                self._mapper.save_template(session, name)
            self._load_templates()

    def _on_add_rule(self):
        rule_type, ok = QLineEdit.getText(self, "Добавить правило", "Тип правила (например, null_replacement, price_round, price_markup):")
        if ok and rule_type:
            self._mapper.config.add_rule(rule_type)
            self._rules_list.addItem(rule_type)

    def _on_remove_rule(self):
        row = self._rules_list.currentRow()
        if row >= 0 and row < len(self._mapper.config.rules):
            self._mapper.config.rules.pop(row)
            self._rules_list.takeItem(row)

    def _apply_mapping_from_ui(self):
        self._mapper.config.field_mapping.clear()
        for db_field, combo in self._mapping_widgets.items():
            wp_field = combo.currentData()
            if wp_field:
                self._mapper.config.field_mapping[db_field] = wp_field

    def _on_save(self):
        self._apply_mapping_from_ui()
        self.accept()


class ArchivePage(QWidget):
    def __init__(self):
        super().__init__()
        self._mapper = FieldMapper()
        self._current_page = 0
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        filter_group = QGroupBox("Фильтры")
        filter_layout = QVBoxLayout(filter_group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Поставщик:"))
        self._supplier_combo = QComboBox()
        self._supplier_combo.setMinimumWidth(200)
        row1.addWidget(self._supplier_combo)

        row1.addSpacing(16)
        row1.addWidget(QLabel("Категория:"))
        self._category_combo = QComboBox()
        self._category_combo.setMinimumWidth(200)
        row1.addWidget(self._category_combo)

        row1.addSpacing(16)
        self._avail_check = QCheckBox("Только доступные")
        row1.addWidget(self._avail_check)

        row1.addStretch()
        filter_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Поиск:"))
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Поиск по названию или артикулу...")
        self._search_input.setMinimumWidth(250)
        row2.addWidget(self._search_input)

        row2.addSpacing(16)
        self._btn_filter = QPushButton("Применить фильтры")
        row2.addWidget(self._btn_filter)
        self._btn_reset = QPushButton("Сбросить")
        row2.addWidget(self._btn_reset)
        row2.addStretch()
        filter_layout.addLayout(row2)

        layout.addWidget(filter_group)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))

        self._btn_edit = QAction("Редактировать", self)
        self._btn_delete = QAction("Удалить", self)
        self._btn_mark_ready = QAction("Отметить готовым", self)
        self._btn_mark_not_ready = QAction("Отметить не готовым", self)
        self._btn_mapping = QAction("Сопоставление полей", self)
        self._btn_validate = QAction("Проверить", self)
        self._btn_export_preview = QAction("Предпросмотр экспорта", self)

        toolbar.addAction(self._btn_edit)
        toolbar.addAction(self._btn_delete)
        toolbar.addSeparator()
        toolbar.addAction(self._btn_mark_ready)
        toolbar.addAction(self._btn_mark_not_ready)
        toolbar.addSeparator()
        toolbar.addAction(self._btn_mapping)
        toolbar.addAction(self._btn_validate)
        toolbar.addAction(self._btn_export_preview)

        layout.addWidget(toolbar)

        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableView()
        self._model = ProductTableModel()
        self._proxy = ProductFilterProxy()
        self._proxy.setSourceModel(self._model)
        self._table.setModel(self._proxy)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        left_layout.addWidget(self._table)

        pagination = QHBoxLayout()
        self._btn_prev = QPushButton("Предыдущая")
        self._btn_next = QPushButton("Следующая")
        self._page_label = QLabel("Страница 1 / 1")
        self._page_label.setAlignment(Qt.AlignCenter)
        pagination.addWidget(self._btn_prev)
        pagination.addWidget(self._page_label)
        pagination.addWidget(self._btn_next)
        pagination.addStretch()
        self._count_label = QLabel("0 товаров")
        pagination.addWidget(self._count_label)
        left_layout.addLayout(pagination)

        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        form_group = QGroupBox("Быстрое редактирование")
        form_layout = QFormLayout(form_group)

        self._edit_title = QLineEdit()
        self._edit_sku = QLineEdit()
        self._edit_price = QLineEdit()
        self._edit_currency = QLineEdit()
        self._edit_available = QCheckBox()
        self._edit_ready = QCheckBox()

        form_layout.addRow("Название:", self._edit_title)
        form_layout.addRow("Артикул:", self._edit_sku)
        form_layout.addRow("Цена:", self._edit_price)
        form_layout.addRow("Валюта:", self._edit_currency)
        form_layout.addRow("Доступен:", self._edit_available)
        form_layout.addRow("Готов к экспорту:", self._edit_ready)

        self._btn_save_edit = QPushButton("Сохранить изменения")
        self._btn_save_edit.setMinimumHeight(36)
        form_layout.addRow(self._btn_save_edit)

        right_layout.addWidget(form_group)

        preview_group = QGroupBox("Предпросмотр WP All Import")
        preview_layout = QVBoxLayout(preview_group)
        self._preview_edit = QPlainTextEdit()
        self._preview_edit.setReadOnly(True)
        preview_layout.addWidget(self._preview_edit)
        right_layout.addWidget(preview_group)

        splitter.addWidget(right_widget)
        splitter.setSizes([700, 400])
        layout.addWidget(splitter)

        self._btn_filter.clicked.connect(self._on_filter)
        self._btn_reset.clicked.connect(self._on_reset)
        self._btn_prev.clicked.connect(self._on_prev_page)
        self._btn_next.clicked.connect(self._on_next_page)
        self._btn_edit.triggered.connect(self._on_edit)
        self._btn_delete.triggered.connect(self._on_delete)
        self._btn_mark_ready.triggered.connect(self._on_mark_ready)
        self._btn_mark_not_ready.triggered.connect(self._on_mark_not_ready)
        self._btn_mapping.triggered.connect(self._on_mapping)
        self._btn_validate.triggered.connect(self._on_validate)
        self._btn_export_preview.triggered.connect(self._on_export_preview)
        self._btn_save_edit.clicked.connect(self._on_save_edit)
        self._search_input.returnPressed.connect(self._on_filter)
        self._table.customContextMenuRequested.connect(self._on_context_menu)
        self._table.clicked.connect(self._on_row_clicked)
        self._supplier_combo.currentIndexChanged.connect(self._on_supplier_changed)

    def _load_suppliers(self):
        self._supplier_combo.clear()
        self._category_combo.clear()
        try:
            with get_session() as session:
                suppliers = session.query(Supplier).filter(
                    Supplier.is_active == True
                ).order_by(Supplier.name).all()
                self._supplier_combo.addItem("Все поставщики", userData=None)
                for s in suppliers:
                    self._supplier_combo.addItem(s.name, userData=s.id)
        except Exception:
            pass

    def _on_supplier_changed(self):
        self._category_combo.clear()
        supplier_id = self._supplier_combo.currentData()
        if supplier_id:
            try:
                with get_session() as session:
                    categories = session.query(Category).filter(
                        Category.supplier_id == supplier_id
                    ).order_by(Category.name).all()
                    self._category_combo.addItem("Все категории", userData=None)
                    for c in categories:
                        self._category_combo.addItem(c.name, userData=c.id)
            except Exception:
                pass
        else:
            self._category_combo.addItem("Все категории", userData=None)

    def _on_filter(self):
        self._current_page = 0
        self._load_products()

    def _on_reset(self):
        self._supplier_combo.setCurrentIndex(0)
        self._category_combo.setCurrentIndex(0)
        self._avail_check.setChecked(False)
        self._search_input.clear()
        self._current_page = 0
        self._load_products()

    def _load_products(self):
        supplier_id = self._supplier_combo.currentData()
        category_id = self._category_combo.currentData()
        available_only = self._avail_check.isChecked()
        search = self._search_input.text().strip()

        total = self._model.load_page(
            supplier_id=supplier_id,
            category_id=category_id,
            available_only=available_only,
            search=search,
            page=self._current_page,
        )

        page_count = self._model.page_count or 1
        self._page_label.setText(f"Страница {self._current_page + 1} / {page_count}")
        self._count_label.setText(f"{total} товаров")
        self._btn_prev.setEnabled(self._current_page > 0)
        self._btn_next.setEnabled(self._current_page < page_count - 1)

    def _on_prev_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self._load_products()

    def _on_next_page(self):
        if self._current_page < self._model.page_count - 1:
            self._current_page += 1
            self._load_products()

    def _on_row_clicked(self, index):
        src_index = self._proxy.mapToSource(index)
        product = self._model.get_product(src_index.row())
        if product:
            self._edit_title.setText(product.get("title", ""))
            self._edit_sku.setText(product.get("external_sku") or "")
            self._edit_price.setText(str(product.get("price") or ""))
            self._edit_currency.setText(product.get("currency") or "")
            self._edit_available.setChecked(product.get("is_available", True))
            self._edit_ready.setChecked(product.get("is_ready_for_export", False))
            self._update_preview(product)

    def _update_preview(self, product: dict):
        product_data = {
            "id": product.get("id"),
            "post_title": product.get("title"),
            "sku": product.get("external_sku"),
            "regular_price": product.get("price"),
            "stock": 1 if product.get("is_available") else 0,
            "stock_status": "instock" if product.get("is_available") else "outofstock",
            "categories": product.get("category_name"),
            "description": "",
            "images": product.get("image_urls", ""),
        }
        transformed = self._mapper.transform_product(product_data)
        self._preview_edit.setPlainText(json.dumps(transformed, indent=2, ensure_ascii=False))

    def _on_save_edit(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            QMessageBox.warning(self, "Ничего не выбрано", "Выберите товар для редактирования.")
            return

        src_index = self._proxy.mapToSource(src_rows[0])
        product = self._model.get_product(src_index.row())
        if not product:
            return

        try:
            with get_session() as session:
                from src.database.models import Product as ProductModel
                p = session.query(ProductModel).filter(ProductModel.id == product["id"]).first()
                if p:
                    p.title = self._edit_title.text().strip()
                    p.external_sku = self._edit_sku.text().strip() or None
                    p.price = float(self._edit_price.text()) if self._edit_price.text() else None
                    p.currency = self._edit_currency.text().strip() or None
                    p.is_available = self._edit_available.isChecked()
                    p.is_ready_for_export = self._edit_ready.isChecked()

            self._model.mark_modified(src_index.row(), 1)
            self._model.mark_modified(src_index.row(), 2)
            self._load_products()
            QMessageBox.information(self, "Успех", "Товар обновлён.")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить товар:\n{exc}")

    def _on_edit(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            QMessageBox.warning(self, "Ничего не выбрано", "Выберите товар для редактирования.")
            return

        src_index = self._proxy.mapToSource(src_rows[0])
        product = self._model.get_product(src_index.row())
        if not product:
            return

        dialog = EditProductDialog(product, self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                with get_session() as session:
                    from src.database.models import Product as ProductModel
                    p = session.query(ProductModel).filter(ProductModel.id == product["id"]).first()
                    if p:
                        p.title = data["title"]
                        p.external_sku = data["external_sku"]
                        p.price = data["price"]
                        p.currency = data["currency"]
                        p.is_available = data["is_available"]
                        p.is_ready_for_export = data["is_ready_for_export"]
                self._load_products()
                QMessageBox.information(self, "Успех", "Товар обновлён.")
            except Exception as exc:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить:\n{exc}")

    def _on_delete(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            QMessageBox.warning(self, "Ничего не выбрано", "Выберите товары для удаления.")
            return

        ids = self._model.get_selected_ids([self._proxy.mapToSource(r).row() for r in src_rows])
        reply = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Удалить {len(ids)} товар(ов)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            with get_session() as session:
                from src.database.models import Product as ProductModel
                session.query(ProductModel).filter(ProductModel.id.in_(ids)).delete(synchronize_session="fetch")
            self._load_products()
            QMessageBox.information(self, "Успех", f"Удалено {len(ids)} товар(ов).")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{exc}")

    def _on_mark_ready(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            return
        ids = self._model.get_selected_ids([self._proxy.mapToSource(r).row() for r in src_rows])
        with get_session() as session:
            self._mapper.mark_ready_for_export(session, ids)
        self._load_products()

    def _on_mark_not_ready(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            return
        ids = self._model.get_selected_ids([self._proxy.mapToSource(r).row() for r in src_rows])
        with get_session() as session:
            self._mapper.mark_not_ready(session, ids)
        self._load_products()

    def _on_mapping(self):
        dialog = MappingDialog(self._mapper, self)
        if dialog.exec() == QDialog.Accepted:
            self._load_products()

    def _on_validate(self):
        supplier_id = self._supplier_combo.currentData()
        issues = []
        with get_session() as session:
            from src.database.models import Product as ProductModel, Category, Supplier
            query = session.query(
                ProductModel.id, ProductModel.external_sku, ProductModel.title,
                ProductModel.price, ProductModel.currency, ProductModel.is_available,
                Category.name.label("category_name"),
            ).outerjoin(Category, ProductModel.category_id == Category.id)
            if supplier_id:
                query = query.filter(ProductModel.supplier_id == supplier_id)

            products = query.all()
            for p in products:
                product_data = {
                    "id": p.id,
                    "post_title": p.title,
                    "sku": p.external_sku,
                    "regular_price": p.price,
                    "stock": 1 if p.is_available else 0,
                    "stock_status": "instock" if p.is_available else "outofstock",
                    "categories": p.category_name,
                }
                transformed = self._mapper.transform_product(product_data)
                issues.extend(self._mapper.validate_product(transformed, p.id))

        if not issues:
            QMessageBox.information(self, "Валидация", "Все товары проходят валидацию.")
        else:
            errors = [i for i in issues if i.severity == "error"]
            warnings = [i for i in issues if i.severity == "warning"]
            msg = f"Ошибок: {len(errors)}\nПредупреждений: {len(warnings)}\n\n"
            for issue in issues[:20]:
                msg += f"[{issue.severity.upper()}] Товар {issue.product_id}: {issue.field} — {issue.message}\n"
            if len(issues) > 20:
                msg += f"\n... и ещё {len(issues) - 20} проблем"
            QMessageBox.warning(self, "Результаты валидации", msg)

    def _on_export_preview(self):
        src_rows = self._table.selectionModel().selectedRows()
        if not src_rows:
            QMessageBox.warning(self, "Ничего не выбрано", "Выберите товары для предпросмотра.")
            return

        rows = [self._proxy.mapToSource(r).row() for r in src_rows[:10]]
        preview_lines = []
        for row in rows:
            product = self._model.get_product(row)
            if product:
                product_data = {
                    "id": product.get("id"),
                    "post_title": product.get("title"),
                    "sku": product.get("external_sku"),
                    "regular_price": product.get("price"),
                    "stock": 1 if product.get("is_available") else 0,
                    "stock_status": "instock" if product.get("is_available") else "outofstock",
                    "categories": product.get("category_name"),
                }
                transformed = self._mapper.transform_product(product_data)
                preview_lines.append(json.dumps(transformed, ensure_ascii=False))

        dialog = QDialog(self)
        dialog.setWindowTitle("Предпросмотр экспорта (первые 10 выбранных)")
        dialog.setMinimumSize(600, 400)
        layout = QVBoxLayout(dialog)
        edit = QPlainTextEdit()
        edit.setReadOnly(True)
        edit.setPlainText("\n".join(preview_lines))
        layout.addWidget(edit)
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec()

    def _on_context_menu(self, pos):
        menu = self._table.contextMenuPolicy()
        from PySide6.QtWidgets import QMenu
        qmenu = QMenu(self)

        edit_action = qmenu.addAction("Редактировать")
        delete_action = qmenu.addAction("Удалить")
        qmenu.addSeparator()
        ready_action = qmenu.addAction("Отметить готовым к экспорту")
        not_ready_action = qmenu.addAction("Отметить не готовым")
        qmenu.addSeparator()
        export_action = qmenu.addAction("Предпросмотр экспорта")

        action = qmenu.exec_(self._table.mapToGlobal(pos))
        if action == edit_action:
            self._on_edit()
        elif action == delete_action:
            self._on_delete()
        elif action == ready_action:
            self._on_mark_ready()
        elif action == not_ready_action:
            self._on_mark_not_ready()
        elif action == export_action:
            self._on_export_preview()
