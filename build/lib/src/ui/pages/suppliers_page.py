from datetime import datetime
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from src.database.models import Supplier
from src.database.session import get_session
from src.database.supplier_crud import (
    create_supplier,
    delete_supplier,
    get_all_suppliers,
    update_supplier,
)


class SupplierTableModel(QAbstractTableModel):
    _headers = [
        "ID",
        "Название",
        "Базовый URL",
        "Статус",
        "Последняя разведка",
        "Последний парсинг",
        "Создан",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._data: list[dict] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        row = self._data[index.row()]
        col = index.column()

        keys = ["id", "name", "base_url", "is_active", "last_discovery_run", "last_scrape_run", "created_at"]
        key = keys[col]
        val = row.get(key)

        if col == 0:
            return val
        if col == 3:
            return "Активен" if val else "Неактивен"
        if col in (4, 5, 6):
            return val.strftime("%Y-%m-%d %H:%M") if val else "—"
        return str(val) if val is not None else ""

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def get_supplier(self, row: int) -> dict | None:
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def refresh(self) -> None:
        self.beginResetModel()
        with get_session() as session:
            suppliers = get_all_suppliers(session, active_only=False)
            self._data = []
            for s in suppliers:
                self._data.append({
                    "id": s.id,
                    "name": s.name,
                    "base_url": s.base_url,
                    "is_active": s.is_active,
                    "last_discovery_run": s.last_discovery_run,
                    "last_scrape_run": s.last_scrape_run,
                    "created_at": s.created_at,
                })
        self.endResetModel()


class SuppliersPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._selected_supplier_id: int | None = None
        self._setup_ui()
        self._connect_signals()
        self._refresh_table()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self._table = QTableView()
        self._model = SupplierTableModel()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.setSelectionMode(QTableView.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setMinimumHeight(300)
        layout.addWidget(self._table)

        form_frame = QWidget()
        form_layout = QFormLayout(form_frame)
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(0, 8, 0, 0)

        self._name_input = QLineEdit()
        self._name_input.setMaxLength(255)
        self._name_input.setPlaceholderText("Название поставщика (обязательно, мин. 2 символа)")
        form_layout.addRow("Название:", self._name_input)

        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://example.com")
        url_validator = QRegularExpressionValidator(
            QRegularExpression(r"^https?://.+")
        )
        self._url_input.setValidator(url_validator)
        form_layout.addRow("Базовый URL:", self._url_input)

        layout.addWidget(form_frame)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self._btn_add = QPushButton("Добавить")
        self._btn_update = QPushButton("Обновить")
        self._btn_delete = QPushButton("Удалить")
        self._btn_refresh = QPushButton("Обновить таблицу")

        for btn in (self._btn_add, self._btn_update, self._btn_delete, self._btn_refresh):
            btn.setMinimumHeight(36)
            btn_layout.addWidget(btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def _connect_signals(self) -> None:
        self._btn_add.clicked.connect(self._on_add)
        self._btn_update.clicked.connect(self._on_update)
        self._btn_delete.clicked.connect(self._on_delete)
        self._btn_refresh.clicked.connect(self._refresh_table)
        self._table.doubleClicked.connect(self._on_row_double_click)

    def _refresh_table(self) -> None:
        self._model.refresh()

    def _validate_name(self) -> str | None:
        name = self._name_input.text().strip()
        if not name:
            QMessageBox.critical(self, "Ошибка валидации", "Название обязательно.")
            return None
        if len(name) < 2:
            QMessageBox.critical(self, "Ошибка валидации", "Название должно содержать минимум 2 символа.")
            return None
        if len(name) > 255:
            QMessageBox.critical(self, "Ошибка валидации", "Название не должно превышать 255 символов.")
            return None
        return name

    def _validate_url(self) -> str | None:
        url = self._url_input.text().strip()
        if not url:
            QMessageBox.critical(self, "Ошибка валидации", "Базовый URL обязателен.")
            return None
        if not url.startswith(("http://", "https://")):
            QMessageBox.critical(
                self, "Ошибка валидации", "Базовый URL должен начинаться с http:// или https://"
            )
            return None
        return url

    def _on_add(self) -> None:
        name = self._validate_name()
        url = self._validate_url()
        if not name or not url:
            return

        try:
            with get_session() as session:
                create_supplier(session, name, url)
            QMessageBox.information(self, "Успех", f"Поставщик '{name}' создан.")
            self._name_input.clear()
            self._url_input.clear()
            self._refresh_table()
        except ValueError as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось создать поставщика:\n{exc}")

    def _on_update(self) -> None:
        if self._selected_supplier_id is None:
            QMessageBox.warning(self, "Нет выбора", "Выберите поставщика из таблицы для обновления.")
            return

        name = self._validate_name()
        url = self._validate_url()
        if not name or not url:
            return

        try:
            with get_session() as session:
                result = update_supplier(
                    session,
                    self._selected_supplier_id,
                    name=name,
                    base_url=url,
                )
            if result:
                QMessageBox.information(self, "Успех", f"Поставщик '{name}' обновлён.")
                self._name_input.clear()
                self._url_input.clear()
                self._selected_supplier_id = None
                self._refresh_table()
            else:
                QMessageBox.warning(self, "Ошибка", "Поставщик не найден.")
        except ValueError as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось обновить поставщика:\n{exc}")

    def _on_delete(self) -> None:
        if self._selected_supplier_id is None:
            QMessageBox.warning(self, "Нет выбора", "Выберите поставщика из таблицы для удаления.")
            return

        supplier = self._model.get_supplier(self._table.currentIndex().row())
        supplier_name = supplier["name"] if supplier else "этот поставщик"

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите деактивировать '{supplier_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            with get_session() as session:
                found = delete_supplier(session, self._selected_supplier_id)
            if found:
                QMessageBox.information(self, "Успех", f"Поставщик '{supplier_name}' деактивирован.")
                self._name_input.clear()
                self._url_input.clear()
                self._selected_supplier_id = None
                self._refresh_table()
            else:
                QMessageBox.warning(self, "Ошибка", "Поставщик не найден.")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось удалить поставщика:\n{exc}")

    def _on_row_double_click(self, index: QModelIndex) -> None:
        row = index.row()
        supplier = self._model.get_supplier(row)
        if supplier:
            self._selected_supplier_id = supplier["id"]
            self._name_input.setText(supplier["name"])
            self._url_input.setText(supplier["base_url"])
