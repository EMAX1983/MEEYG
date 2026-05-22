import asyncio
import sys
import threading
from typing import Optional

from PySide6.QtCore import QAbstractItemModel, QModelIndex, Qt, QThread, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from src.database.models import Category, Supplier
from src.database.session import get_session
from src.modules.discovery.engine import DiscoveryEngine


class DiscoveryWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int, int, str)
    finished_signal = Signal(dict)

    def __init__(
        self,
        supplier_id: int,
        base_url: str,
        max_depth: int = 3,
        delay_min: float = 0.5,
        delay_max: float = 2.0,
        check_robots: bool = True,
        timeout: int = 30,
    ):
        super().__init__()
        self.supplier_id = supplier_id
        self.base_url = base_url
        self.max_depth = max_depth
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.check_robots = check_robots
        self.timeout = timeout
        self._engine: Optional[DiscoveryEngine] = None

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def log_cb(msg):
            self.log_signal.emit(msg)

        def progress_cb(pct, total, msg):
            self.progress_signal.emit(pct, total, msg)

        self._engine = DiscoveryEngine(
            supplier_id=self.supplier_id,
            base_url=self.base_url,
            log_callback=log_cb,
            progress_callback=progress_cb,
            max_depth=self.max_depth,
            delay_range=(self.delay_min, self.delay_max),
            check_robots=self.check_robots,
            timeout=self.timeout,
        )

        async def _run():
            with get_session() as session:
                result = await self._engine.run(session)
            return result

        try:
            result = loop.run_until_complete(_run())
            self.finished_signal.emit(result)
        except Exception as exc:
            self.finished_signal.emit({"success": False, "error": str(exc), "categories_found": 0})
        finally:
            loop.close()

    def cancel(self):
        if self._engine:
            self._engine.cancel()


class CategoryTreeModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels(["Категория", "URL", "Товары", "XPath"])

    def load_categories(self, categories: list) -> None:
        self.removeRows(0, self.rowCount())

        def _add_children(parent_item, cats):
            for cat in cats:
                name_item = QStandardItem(cat.name)
                url_item = QStandardItem(cat.url)
                count_item = QStandardItem(str(cat.product_count))
                xpath_item = QStandardItem(cat.xpath_selector[:60] + "..." if len(cat.xpath_selector) > 60 else cat.xpath_selector)

                parent_item.appendRow([name_item, url_item, count_item, xpath_item])
                if cat.children:
                    _add_children(name_item, cat.children)

        root = self.invisibleRootItem()
        for cat in categories:
            name_item = QStandardItem(cat.name)
            url_item = QStandardItem(cat.url)
            count_item = QStandardItem(str(cat.product_count))
            xpath_item = QStandardItem(cat.xpath_selector[:60] + "..." if len(cat.xpath_selector) > 60 else cat.xpath_selector)

            root.appendRow([name_item, url_item, count_item, xpath_item])
            if cat.children:
                _add_children(name_item, cat.children)

    def load_from_db(self, supplier_id: int) -> None:
        self.removeRows(0, self.rowCount())

        with get_session() as session:
            top_level = session.query(Category).filter(
                Category.supplier_id == supplier_id,
                Category.parent_id.is_(None),
            ).order_by(Category.sort_order, Category.name).all()

            def _build_tree(parent_item, parent_id):
                children = session.query(Category).filter(
                    Category.supplier_id == supplier_id,
                    Category.parent_id == parent_id,
                ).order_by(Category.sort_order, Category.name).all()

                for cat in children:
                    name_item = QStandardItem(cat.name)
                    url_item = QStandardItem(cat.url)
                    count_item = QStandardItem(str(cat.product_count))
                    xpath_item = QStandardItem(cat.xpath_selector[:60] + "..." if cat.xpath_selector and len(cat.xpath_selector) > 60 else (cat.xpath_selector or ""))

                    parent_item.appendRow([name_item, url_item, count_item, xpath_item])
                    _build_tree(name_item, cat.id)

            root = self.invisibleRootItem()
            for cat in top_level:
                name_item = QStandardItem(cat.name)
                url_item = QStandardItem(cat.url)
                count_item = QStandardItem(str(cat.product_count))
                xpath_item = QStandardItem(cat.xpath_selector[:60] + "..." if cat.xpath_selector and len(cat.xpath_selector) > 60 else (cat.xpath_selector or ""))

                root.appendRow([name_item, url_item, count_item, xpath_item])
                _build_tree(name_item, cat.id)


class DiscoveryPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: Optional[DiscoveryWorker] = None
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        ctrl_group = QGroupBox("Управление разведкой")
        ctrl_layout = QVBoxLayout(ctrl_group)

        supplier_row = QHBoxLayout()
        supplier_row.addWidget(QLabel("Поставщик:"))
        self._supplier_combo = QComboBox()
        self._supplier_combo.setMinimumWidth(300)
        supplier_row.addWidget(self._supplier_combo)
        supplier_row.addStretch()
        ctrl_layout.addLayout(supplier_row)

        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Глубина:"))
        self._depth_combo = QComboBox()
        self._depth_combo.addItems(["1", "2", "3", "4", "5"])
        self._depth_combo.setCurrentText("3")
        self._depth_combo.setMaximumWidth(60)
        options_row.addWidget(self._depth_combo)

        options_row.addSpacing(16)
        options_row.addWidget(QLabel("Задержка (с):"))
        self._delay_min_input = QComboBox()
        self._delay_min_input.addItems(["0.2", "0.5", "1.0", "2.0"])
        self._delay_min_input.setCurrentText("0.5")
        self._delay_min_input.setMaximumWidth(70)
        options_row.addWidget(self._delay_min_input)

        options_row.addWidget(QLabel("–"))

        self._delay_max_input = QComboBox()
        self._delay_max_input.addItems(["1.0", "2.0", "3.0", "5.0"])
        self._delay_max_input.setCurrentText("2.0")
        self._delay_max_input.setMaximumWidth(70)
        options_row.addWidget(self._delay_max_input)

        options_row.addSpacing(16)
        self._robots_check = QPushButton("Проверять robots.txt")
        self._robots_check.setCheckable(True)
        self._robots_check.setChecked(True)
        options_row.addWidget(self._robots_check)

        options_row.addStretch()
        ctrl_layout.addLayout(options_row)

        btn_row = QHBoxLayout()
        self._btn_start = QPushButton("Запустить разведку")
        self._btn_start.setMinimumHeight(40)
        self._btn_cancel = QPushButton("Отмена")
        self._btn_cancel.setMinimumHeight(40)
        self._btn_cancel.setEnabled(False)
        self._btn_load_db = QPushButton("Загрузить из БД")
        self._btn_load_db.setMinimumHeight(40)
        btn_row.addWidget(self._btn_start)
        btn_row.addWidget(self._btn_cancel)
        btn_row.addWidget(self._btn_load_db)
        btn_row.addStretch()
        ctrl_layout.addLayout(btn_row)

        layout.addWidget(ctrl_group)

        progress_row = QHBoxLayout()
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimumHeight(20)
        self._progress_label = QLabel("Готово")
        progress_row.addWidget(self._progress_bar, 1)
        progress_row.addWidget(self._progress_label)
        layout.addLayout(progress_row)

        splitter = QSplitter(Qt.Vertical)

        tree_group = QGroupBox("Найденные категории")
        tree_layout = QVBoxLayout(tree_group)
        self._tree = QTreeView()
        self._tree_model = CategoryTreeModel()
        self._tree.setModel(self._tree_model)
        self._tree.setAlternatingRowColors(True)
        self._tree.header().setStretchLastSection(False)
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._tree.header().setSectionResizeMode(3, QHeaderView.Stretch)
        self._tree.setExpandsOnDoubleClick(True)
        tree_layout.addWidget(self._tree)
        splitter.addWidget(tree_group)

        log_group = QGroupBox("Журнал разведки")
        log_layout = QVBoxLayout(log_group)
        self._log_edit = QPlainTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(200)
        log_layout.addWidget(self._log_edit)
        splitter.addWidget(log_group)

        splitter.setSizes([400, 200])
        layout.addWidget(splitter)

        self._btn_start.clicked.connect(self._on_start)
        self._btn_cancel.clicked.connect(self._on_cancel)
        self._btn_load_db.clicked.connect(self._on_load_db)

    def _load_suppliers(self):
        self._supplier_combo.clear()
        try:
            with get_session() as session:
                suppliers = session.query(Supplier).filter(
                    Supplier.is_active == True
                ).order_by(Supplier.name).all()
                for s in suppliers:
                    self._supplier_combo.addItem(s.name, userData=s.id)
        except Exception as exc:
            self._append_log(f"Ошибка загрузки поставщиков: {exc}")

    def _append_log(self, msg: str):
        self._log_edit.appendPlainText(f"[{self._timestamp()}] {msg}")

    @staticmethod
    def _timestamp() -> str:
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def _on_start(self):
        supplier_id = self._supplier_combo.currentData()
        if supplier_id is None:
            QMessageBox.warning(self, "Нет поставщика", "Сначала выберите поставщика.")
            return

        with get_session() as session:
            supplier = session.query(Supplier).filter(Supplier.id == supplier_id).first()
            if not supplier:
                QMessageBox.warning(self, "Ошибка", "Поставщик не найден в базе данных.")
                return
            base_url = supplier.base_url

        self._btn_start.setEnabled(False)
        self._btn_cancel.setEnabled(True)
        self._progress_bar.setValue(0)
        self._progress_label.setText("Запуск...")
        self._log_edit.clear()
        self._append_log(f"Запуск разведки для '{self._supplier_combo.currentText()}' ({base_url})")

        max_depth = int(self._depth_combo.currentText())
        delay_min = float(self._delay_min_input.currentText())
        delay_max = float(self._delay_max_input.currentText())
        check_robots = self._robots_check.isChecked()

        self._worker = DiscoveryWorker(
            supplier_id=supplier_id,
            base_url=base_url,
            max_depth=max_depth,
            delay_min=delay_min,
            delay_max=delay_max,
            check_robots=check_robots,
            timeout=30,
        )
        self._worker.log_signal.connect(self._append_log)
        self._worker.progress_signal.connect(self._on_progress)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.start()

    def _on_cancel(self):
        if self._worker and self._worker.isRunning():
            self._append_log("Отмена разведки...")
            self._worker.cancel()
            self._btn_cancel.setEnabled(False)

    def _on_progress(self, pct: int, total: int, msg: str):
        self._progress_bar.setValue(min(pct, 100))
        self._progress_label.setText(f"{pct}% — {msg}")

    def _on_finished(self, result: dict):
        self._btn_start.setEnabled(True)
        self._btn_cancel.setEnabled(False)

        if result.get("success"):
            count = result.get("categories_found", 0)
            self._progress_bar.setValue(100)
            self._progress_label.setText(f"Готово — найдено {count} категорий")
            self._append_log(f"Разведка завершена: сохранено {count} категорий")

            categories = result.get("categories", [])
            if categories:
                self._tree_model.load_categories(categories)
            else:
                self._tree_model.load_from_db(self._supplier_combo.currentData())

            QMessageBox.information(self, "Успех", f"Разведка завершена.\nСохранено {count} категорий.")
        else:
            error = result.get("error", "Неизвестная ошибка")
            self._progress_label.setText(f"Ошибка: {error}")
            self._append_log(f"Разведка не удалась: {error}")
            QMessageBox.critical(self, "Ошибка разведки", f"Разведка не удалась:\n{error}")

    def _on_load_db(self):
        supplier_id = self._supplier_combo.currentData()
        if supplier_id is None:
            QMessageBox.warning(self, "Нет поставщика", "Сначала выберите поставщика.")
            return

        self._append_log("Загрузка категорий из базы данных...")
        self._tree_model.load_from_db(supplier_id)
        row_count = self._tree_model.rowCount()
        self._append_log(f"Загружено {row_count} категорий верхнего уровня из базы данных")
