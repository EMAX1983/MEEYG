import re
from datetime import datetime
from pathlib import Path
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QWidget,
    QMessageBox,
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QHeaderView,
    QAbstractItemView,
    QScrollArea,
)
from src.core.config import settings
from src.database.models import Product, ProductAttribute, Supplier, Category
from src.database.session import get_session
from src.modules.archive.exporter import ArchiveExportConfig, ArchiveExporter


CHECK_COL = 0
ID_COL = 1
SKU_COL = 2
PARENTAL_COL = 3
TITLE_COL = 4
SIZE_COL = 5
COLOR_COL = 6
TYPE_COL = 7
DIRECTION_COL = 8
PRICE_COL = 9
CURRENCY_COL = 10
CATEGORY_COL = 11
AVAILABLE_COL = 12
READY_COL = 13
SUPPLIER_COL = 14
IMAGE_COL = 15

_HEADERS = ["", "ID", "SKU", "Parental", "Название", "Размер", "Цвет", "Тип", "Направление", "Цена", "Валюта", "Категория", "Доступен", "Готов", "Поставщик", "Фото"]
_KEYS = ["id", "external_sku", "parental", "title", "size", "color", "product_type", "direction", "price", "currency", "category_name", "is_available", "is_ready_for_export", "supplier_name", "image_url"]

_COLUMN_MIN_WIDTHS = {
    CHECK_COL: 30,
    ID_COL: 50,
    SKU_COL: 180,
    PARENTAL_COL: 180,
    TITLE_COL: 200,
    SIZE_COL: 90,
    COLOR_COL: 100,
    TYPE_COL: 80,
    DIRECTION_COL: 130,
    PRICE_COL: 90,
    CURRENCY_COL: 70,
    CATEGORY_COL: 250,
    AVAILABLE_COL: 80,
    READY_COL: 60,
    SUPPLIER_COL: 100,
    IMAGE_COL: 250,
}


def clean_product_title(raw_title: str) -> str:
    """
    Очищает название товара от лишних префиксов и размеров.
    Например: "Входная дверь Валенсия Белый матовый 950x2030" -> "Валенсия Белый матовый"
    """
    if not raw_title:
        return ""
    title = raw_title.strip()
    # Remove common prefixes
    prefixes = [
        "Входная дверь ",
        "Входная дверь",
        "Дверь входная ",
        "Дверь ",
    ]
    for prefix in prefixes:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
            break
    # Remove size patterns at the end like " 950x2030", " 860x2050", "950Х2030"
    title = re.sub(r'\s*\d{3,4}[xXх]\d{3,4}\s*$', '', title)
    # Clean up multiple spaces
    title = re.sub(r'\s+', ' ', title).strip()
    return title


class ProductTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._products = []
        self._filtered = []
        self._sort_column = -1
        self._sort_order = Qt.AscendingOrder
        self._filter_text = ""
        self._check_states = {}

    def rowCount(self, parent=QModelIndex()):
        return len(self._filtered)

    def columnCount(self, parent=QModelIndex()):
        return len(_HEADERS)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return _HEADERS[section]
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        row = self._filtered[index.row()]
        if index.column() == CHECK_COL:
            if role == Qt.CheckStateRole:
                return self._check_states.get(row["id"], Qt.Unchecked)
            if role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            return None
        if role == Qt.DisplayRole:
            col_idx = index.column() - 1
            if 0 <= col_idx < len(_KEYS):
                return str(row.get(_KEYS[col_idx], ""))
        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        if index.column() == CHECK_COL and role == Qt.CheckStateRole:
            row_id = self._filtered[index.row()]["id"]
            self._check_states[row_id] = value
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        return super().setData(index, value, role)

    def flags(self, index):
        base_flags = super().flags(index)
        if index.column() == CHECK_COL:
            return base_flags | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        return base_flags

    def set_products(self, data):
        self.beginResetModel()
        self._products = data
        self._apply_filter()
        self.endResetModel()

    def _apply_filter(self):
        self._filtered = list(self._products)
        if self._filter_text:
            ft = self._filter_text.lower()
            self._filtered = [
                p for p in self._filtered
                if any(ft in str(v).lower() for v in p.values())
            ]
        if self._sort_column >= 0:
            key = _KEYS[self._sort_column - 1] if self._sort_column > 0 else _KEYS[0]
            reverse = self._sort_order == Qt.DescendingOrder

            def sort_key(item):
                val = item.get(key, "")
                if key == "price":
                    try:
                        return float(val)
                    except (ValueError, TypeError):
                        return 0.0
                if key == "id":
                    try:
                        return int(val)
                    except (ValueError, TypeError):
                        return 0
                return str(val).lower()

            self._filtered.sort(key=sort_key, reverse=reverse)

    def set_filter(self, text):
        self._filter_text = text
        self.beginResetModel()
        self._apply_filter()
        self.endResetModel()

    def sort(self, column, order=Qt.AscendingOrder):
        if column == CHECK_COL:
            return
        self._sort_column = column
        self._sort_order = order
        self.beginResetModel()
        self._apply_filter()
        self.endResetModel()

    def get_selected_ids(self):
        return [pid for pid, state in self._check_states.items() if state == Qt.Checked]

    def select_all(self):
        for p in self._filtered:
            self._check_states[p["id"]] = Qt.Checked
        self.dataChanged.emit(
            self.index(0, CHECK_COL),
            self.index(self.rowCount() - 1, CHECK_COL),
            [Qt.CheckStateRole]
        )

    def deselect_all(self):
        for p in self._filtered:
            self._check_states[p["id"]] = Qt.Unchecked
        self.dataChanged.emit(
            self.index(0, CHECK_COL),
            self.index(self.rowCount() - 1, CHECK_COL),
            [Qt.CheckStateRole]
        )

    def invert_selection(self):
        for p in self._filtered:
            pid = p["id"]
            self._check_states[pid] = Qt.Unchecked if self._check_states.get(pid) == Qt.Checked else Qt.Checked
        self.dataChanged.emit(
            self.index(0, CHECK_COL),
            self.index(self.rowCount() - 1, CHECK_COL),
            [Qt.CheckStateRole]
        )

    def get_checked_count(self):
        return sum(1 for s in self._check_states.values() if s == Qt.Checked)

    def get_product_by_id(self, product_id):
        for p in self._filtered:
            if p["id"] == product_id:
                return p
        return None


class EditProductDialog(QDialog):
    def __init__(self, product_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактирование товара")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)

        self.title_edit = QLineEdit(product_data.get("title", ""))
        self.price_edit = QLineEdit(str(product_data.get("price", "0.00")))
        self.size_edit = QLineEdit(product_data.get("size", ""))

        layout.addRow("Название:", self.title_edit)
        layout.addRow("Цена:", self.price_edit)
        layout.addRow("Размер:", self.size_edit)

        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setObjectName("primaryButton")
        self.cancel_btn = QPushButton("Отмена")
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addRow(buttons_layout)

        self.save_btn.clicked.connect(self.on_save)
        self.cancel_btn.clicked.connect(self.reject)

        self.data = product_data
        self.result_values = None

    def on_save(self):
        try:
            price = float(self.price_edit.text())
            self.result_values = {
                "title": self.title_edit.text().strip(),
                "price": price,
                "size": self.size_edit.text().strip(),
            }
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректное значение цены")

    def get_values(self):
        return self.result_values


class ArchivePage(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        search_layout = QHBoxLayout()
        search_label = QLabel("Поиск:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по ID, SKU, названию, размеру...")
        self.search_input.textChanged.connect(self.on_search)
        self.btn_search_clear = QPushButton("Очистить")
        self.btn_search_clear.clicked.connect(self.clear_search)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.btn_search_clear)
        main_layout.addLayout(search_layout)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.setMinimumHeight(36)
        self.btn_refresh.clicked.connect(self.load_data)

        self.btn_select_all = QPushButton("Выбрать все")
        self.btn_select_all.setMinimumHeight(36)
        self.btn_select_all.clicked.connect(self.on_select_all)

        self.btn_deselect_all = QPushButton("Снять все")
        self.btn_deselect_all.setMinimumHeight(36)
        self.btn_deselect_all.clicked.connect(self.on_deselect_all)

        self.btn_invert = QPushButton("Инвертировать")
        self.btn_invert.setMinimumHeight(36)
        self.btn_invert.clicked.connect(self.on_invert_selection)

        self.btn_edit = QPushButton("Редактировать")
        self.btn_edit.setMinimumHeight(36)
        self.btn_edit.clicked.connect(self.on_edit)

        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.setMinimumHeight(36)
        self.btn_delete.clicked.connect(self.on_delete)

        self.btn_export_archive = QPushButton("Сохранить архив")
        self.btn_export_archive.setMinimumHeight(36)
        self.btn_export_archive.clicked.connect(self.on_export_archive)

        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_select_all)
        btn_layout.addWidget(self.btn_deselect_all)
        btn_layout.addWidget(self.btn_invert)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_export_archive)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.status_label = QLabel("Загрузка...")
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        main_layout.addWidget(self.status_label)

        self.table = QTableView()
        self.model = ProductTableModel()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(False)
        self.table.horizontalHeader().setStretchLastSection(False)

        hh = self.table.horizontalHeader()
        for col, min_w in _COLUMN_MIN_WIDTHS.items():
            hh.setSectionResizeMode(col, QHeaderView.Interactive)
            self.table.setColumnWidth(col, min_w)

        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(300)
        self.table.doubleClicked.connect(self.on_double_click)
        main_layout.addWidget(self.table)

    def on_search(self, text):
        self.model.set_filter(text)
        self._update_status()

    def clear_search(self):
        self.search_input.clear()

    def _update_status(self):
        total = len(self.model._filtered)
        checked = self.model.get_checked_count()
        if total == 0:
            self.status_label.setText("Нет товаров в архиве")
        elif checked > 0:
            self.status_label.setText(f"Найдено товаров: {total}, выбрано: {checked}")
        else:
            self.status_label.setText(f"Найдено товаров: {total}")

    def _get_attr_value(self, session, product_id, attr_name):
        """Вспомогательный метод для получения значения атрибута."""
        attr = session.query(ProductAttribute).filter_by(
            product_id=product_id, name=attr_name
        ).first()
        return attr.value if attr else "-"

    def _get_full_category_path(self, session, category_id):
        """Возвращает полную иерархию категории: 'Каталог > Входные двери > по конструкции'."""
        if not category_id:
            return "Без категории"
        
        path_parts = []
        cat = session.get(Category, category_id)
        while cat is not None:
            path_parts.append(cat.name)
            cat = session.get(Category, cat.parent_id) if cat.parent_id else None
        
        return " > ".join(reversed(path_parts)) if path_parts else "Без категории"

    def _clean_sku(self, raw_sku: str, supplier_name: str = "") -> str:
        """Очищает SKU от лишних префиксов: 'Входная дверь', размеров.
        Формат: '{supplier} {clean_title} {number}'
        Например: 'Входная дверь Валенсия Белый матовый 950x2030 000001' -> 'Тандор Валенсия Белый матовый 000001'
        """
        if not raw_sku or raw_sku == "-":
            return raw_sku or "-"
        sku = raw_sku.strip()
        # Remove common prefixes
        for prefix in ["Входная дверь ", "Дверь входная ", "Дверь "]:
            if sku.startswith(prefix):
                sku = sku[len(prefix):].strip()
                break
        # Remove size patterns like " 950x2030"
        sku = re.sub(r'\s+\d{2,4}[xXх]\d{3,4}', '', sku)
        # Clean multiple spaces
        sku = re.sub(r'\s+', ' ', sku).strip()
        # If supplier name provided and not already in SKU, prepend it
        if supplier_name and supplier_name not in sku:
            sku = f"{supplier_name} {sku}"
        return sku

    def load_data(self):
        data = []
        parents_map = {}  # parent_id -> list of child records
        
        try:
            with get_session() as session:
                products = session.query(Product).all()
                total_count = len(products)
                
                # Создаем промежуточные данные с parent_product_id
                raw_items = []
                for p in products:
                    sup = session.get(Supplier, p.supplier_id) if p.supplier_id else None
                    supplier_name = sup.name if sup else "Тандор"
                    
                    parental_sku = self._get_attr_value(session, p.id, "ParentSKU")
                    display_title = clean_product_title(p.title)
                    
                    # Берём первое изображение из коллекции фото товара
                    product_images = p.get_image_urls() if p.image_urls else []
                    image_url = product_images[0] if product_images else ""

                    item = {
                        "id": p.id,
                        "external_sku": self._clean_sku(p.external_sku or "-", supplier_name),
                        "parental": self._clean_sku(parental_sku, supplier_name) if parental_sku != "-" else "-",
                        "title": display_title,
                        "size": self._get_attr_value(session, p.id, "Размер"),
                        "color": self._get_attr_value(session, p.id, "Цвет"),
                        "product_type": self._get_attr_value(session, p.id, "Тип"),
                        "direction": self._get_attr_value(session, p.id, "Направление"),
                        "price": f"{p.price:.2f}" if p.price else "0.00",
                        "currency": p.currency or "RUB",
                        "category_name": self._get_full_category_path(session, p.category_id),
                        "is_available": "Да" if p.is_available else "Нет",
                        "is_ready_for_export": "Да" if p.is_ready_for_export else "Нет",
                        "supplier_name": supplier_name,
                        "image_url": image_url,
                        "_parent_product_id": p.parent_product_id,  # Для сортировки
                    }
                    raw_items.append(item)
                
                # Сортируем: сначала родители, потом дети строго под своим родителем
                parents_list = [i for i in raw_items if i["_parent_product_id"] is None]
                children_list = [i for i in raw_items if i["_parent_product_id"] is not None]
                
                # Составляем список: родитель -> его дети -> следующий родитель -> его дети
                children_by_parent = {}
                for child in children_list:
                    pid = child["_parent_product_id"]
                    if pid not in children_by_parent:
                        children_by_parent[pid] = []
                    children_by_parent[pid].append(child)
                
                for parent in parents_list:
                    # Удаляем временное поле из финальных данных
                    final_item = {k: v for k, v in parent.items() if not k.startswith("_")}
                    data.append(final_item)
                    # Добавляем детей этого родителя
                    for child in children_by_parent.get(parent["id"], []):
                        final_child = {k: v for k, v in child.items() if not k.startswith("_")}
                        data.append(final_child)
                
                print(f"[Archive] Загружено товаров: {total_count}, добавлено в модель: {len(data)}")
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка загрузки данных", str(e))

        self.model.set_products(data)
        self._update_status()

    def on_select_all(self):
        self.model.select_all()
        self._update_status()

    def on_deselect_all(self):
        self.model.deselect_all()
        self._update_status()

    def on_invert_selection(self):
        self.model.invert_selection()
        self._update_status()

    def on_delete(self):
        ids = self.model.get_selected_ids()
        if not ids:
            QMessageBox.warning(self, "Нет выбора", "Отметьте записи чекбоксами для удаления.")
            return
        if QMessageBox.question(
            self, "Подтверждение", f"Удалить {len(ids)} записей?"
        ) != QMessageBox.Yes:
            return
        try:
            with get_session() as session:
                session.query(Product).filter(Product.id.in_(ids)).delete(
                    synchronize_session="fetch"
                )
                session.commit()
            self.load_data()
            QMessageBox.information(self, "Успех", f"Удалено {len(ids)} записей.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка удаления", str(e))

    def on_export_archive(self):
        checked = self.model.get_selected_ids()
        if checked:
            id_set = set(checked)
            ids = [p["id"] for p in self.model._filtered if p["id"] in id_set]
        else:
            ids = [p["id"] for p in self.model._filtered]
        if not ids:
            QMessageBox.warning(
                self,
                "Экспорт",
                "Нет строк для экспорта (пустой список или фильтр).",
            )
            return
        exports_dir = settings.data_dir / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)
        default = exports_dir / f"archive_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        path_str, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Сохранить архив",
            str(default),
            "Excel — колонки как в таблице (*.xlsx);;"
            "CSV для WP All Import, разделитель | (*.csv);;"
            "Все файлы (*)",
        )
        if not path_str:
            return
        out_path = Path(path_str)
        suf = out_path.suffix.lower()
        if suf not in (".csv", ".xlsx"):
            if "xlsx" in selected_filter.lower():
                out_path = out_path.with_suffix(".xlsx")
            else:
                out_path = out_path.with_suffix(".csv")
        try:
            n, fmt = ArchiveExporter.export(
                ArchiveExportConfig(output_path=out_path, product_ids=ids)
            )
            msg = f"Сохранено: {out_path}\nСтрок товаров: {n}"
            if fmt == "csv_pipe":
                msg += (
                    "\n\nЕсли открываете в Excel двойным щелчком, колонки «съезжают»: "
                    "Excel ждёт «;» или «,», а не «|». "
                    "Сделайте: «Данные» → «Из текстового/CSV-файла» → файл → разделитель «|»."
                )
            QMessageBox.information(self, "Экспорт", msg)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка экспорта", str(e))

    def on_edit(self):
        ids = self.model.get_selected_ids()
        if not ids:
            QMessageBox.warning(self, "Нет выбора", "Отметьте товар чекбоксом для редактирования.")
            return
        product = self.model.get_product_by_id(ids[0])
        dlg = EditProductDialog(product, self)
        if dlg.exec():
            new_data = dlg.get_values()
            if new_data:
                try:
                    with get_session() as session:
                        p = session.get(Product, product["id"])
                        if p:
                            p.title = new_data["title"]
                            p.price = new_data["price"]
                            size_val = new_data["size"]
                            attr = session.query(ProductAttribute).filter_by(
                                product_id=p.id, name="Размер"
                            ).first()
                            if size_val:
                                if attr:
                                    attr.value = size_val
                                else:
                                    attr = ProductAttribute(
                                        product_id=p.id, name="Размер", value=size_val
                                    )
                                    session.add(attr)
                            elif attr:
                                session.delete(attr)
                            session.commit()
                    self.load_data()
                    QMessageBox.information(self, "Успех", "Товар обновлён.")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка сохранения", str(e))

    def on_double_click(self, index):
        if index.column() == CHECK_COL:
            current = self.model.data(index, Qt.CheckStateRole)
            new_val = Qt.Unchecked if current == Qt.Checked else Qt.Checked
            self.model.setData(index, new_val, Qt.CheckStateRole)
            self._update_status()
        else:
            row = index.row()
            product = self.model._filtered[row]
            dlg = EditProductDialog(product, self)
            if dlg.exec():
                new_data = dlg.get_values()
                if new_data:
                    try:
                        with get_session() as session:
                            p = session.get(Product, product["id"])
                            if p:
                                p.title = new_data["title"]
                                p.price = new_data["price"]
                                size_val = new_data["size"]
                                attr = session.query(ProductAttribute).filter_by(
                                    product_id=p.id, name="Размер"
                                ).first()
                                if size_val:
                                    if attr:
                                        attr.value = size_val
                                    else:
                                        attr = ProductAttribute(
                                            product_id=p.id, name="Размер", value=size_val
                                        )
                                        session.add(attr)
                                elif attr:
                                    session.delete(attr)
                                session.commit()
                        self.load_data()
                        QMessageBox.information(self, "Успех", "Товар обновлён.")
                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка сохранения", str(e))