import asyncio
from typing import Optional, Tuple

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    QThread,
    Signal,
    Slot,
)
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
    QTableView,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from src.database.models import Category, Supplier
from src.database.session import SessionFactory, get_session
from src.modules.parsing.tandoor_playwright_parser import TandoorPlaywrightParser


class CategoryCheckModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels(["Категория", "URL", "Товары"])

    def load_categories(self, supplier_id: int) -> int:
        self.removeRows(0, self.rowCount())

        with get_session() as session:
            top_level = (
                session.query(Category)
                .filter(
                    Category.supplier_id == supplier_id,
                    Category.parent_id.is_(None),
                )
                .order_by(Category.sort_order, Category.name)
                .all()
            )

            def _build_tree(parent_item, parent_id):
                children = (
                    session.query(Category)
                    .filter(
                        Category.supplier_id == supplier_id,
                        Category.parent_id == parent_id,
                    )
                    .order_by(Category.sort_order, Category.name)
                    .all()
                )

                for cat in children:
                    name_item = QStandardItem(cat.name)
                    name_item.setCheckable(True)
                    name_item.setCheckState(Qt.Unchecked)
                    name_item.setData(cat.id, Qt.UserRole)

                    url_item = QStandardItem(cat.url)
                    count_item = QStandardItem(str(cat.product_count))

                    parent_item.appendRow([name_item, url_item, count_item])
                    _build_tree(name_item, cat.id)

            root = self.invisibleRootItem()
            for cat in top_level:
                name_item = QStandardItem(cat.name)
                name_item.setCheckable(True)
                name_item.setCheckState(Qt.Unchecked)
                name_item.setData(cat.id, Qt.UserRole)

                url_item = QStandardItem(cat.url)
                count_item = QStandardItem(str(cat.product_count))

                root.appendRow([name_item, url_item, count_item])
                _build_tree(name_item, cat.id)

            return len(top_level)

    def get_checked_ids(self) -> list[int]:
        ids = []

        def _collect(item):
            if item.isCheckable() and item.checkState() == Qt.Checked:
                cat_id = item.data(Qt.UserRole)
                if cat_id is not None:
                    ids.append(cat_id)
            for i in range(item.rowCount()):
                _collect(item.child(i, 0))

        for i in range(self.rowCount()):
            _collect(self.item(i, 0))
        return ids

    def check_all(self) -> None:
        def _set_checked(item):
            if item.isCheckable():
                item.setCheckState(Qt.Checked)
            for i in range(item.rowCount()):
                _set_checked(item.child(i, 0))

        for i in range(self.rowCount()):
            _set_checked(self.item(i, 0))

    def uncheck_all(self) -> None:
        def _set_unchecked(item):
            if item.isCheckable():
                item.setCheckState(Qt.Unchecked)
            for i in range(item.rowCount()):
                _set_unchecked(item.child(i, 0))

        for i in range(self.rowCount()):
            _set_unchecked(self.item(i, 0))


class TaskStatusModel(QAbstractTableModel):
    _headers = ["Задача", "Статус", "Товары", "Ошибки", "Время"]

    def __init__(self):
        super().__init__()
        self._rows: list[dict] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        row = self._rows[index.row()]
        col = index.column()
        keys = ["task", "status", "products", "errors", "time"]
        return row.get(keys[col], "")

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def add_task(
        self,
        task: str,
        status: str = "Выполняется",
        products: int = 0,
        errors: int = 0,
        elapsed: str = "",
    ):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._rows.append(
            {
                "task": task,
                "status": status,
                "products": str(products),
                "errors": str(errors),
                "time": elapsed,
            }
        )
        self.endInsertRows()

    def update_last(self, **kwargs):
        if self._rows:
            self._rows[-1].update({str(k): str(v) for k, v in kwargs.items()})
            last_row_index = self.index(self.rowCount() - 1, 0)
            last_col_index = self.index(self.rowCount() - 1, self.columnCount() - 1)
            self.dataChanged.emit(last_row_index, last_col_index)

    def clear(self):
        self.beginResetModel()
        self._rows.clear()
        self.endResetModel()


class ParsingWorker(QObject):
    """
    Worker object that performs parsing in a separate thread.
    Inherits from QObject to be movable to a QThread.
    """

    log_signal = Signal(str)
    progress_signal = Signal(int, int, str)
    stats_signal = Signal(dict)
    finished_signal = Signal(dict)

    def __init__(
        self,
        supplier_id: int,
        base_url: str,
        category_ids: list[int],
        headless: bool = True,
        debug_mode: bool = False,
    ):
        super().__init__()
        self.supplier_id = supplier_id
        self.base_url = base_url
        self.category_ids = category_ids
        self.headless = headless
        self.debug_mode = debug_mode
        self._engine: Optional[TandoorPlaywrightParser] = None

    @Slot()
    def run_task(self):
        """
        Main entry point for the worker. Runs the async logic and handles results.
        This method is executed in the worker thread.
        """
        result = {}
        try:
            result = asyncio.run(self._run_async_parsing())
            stats = result.get("stats", {})
            if stats:
                elapsed = 0.0
                if "start_time" in stats and "end_time" in stats:
                    try:
                        elapsed = (stats["end_time"] - stats["start_time"]).total_seconds()
                    except Exception:
                        elapsed = 0.0
                self.stats_signal.emit(
                    {
                        "total_products": stats.get("products_parsed", 0),
                        "total_pages": stats.get("products_parsed", 0),
                        "successful_pages": stats.get("products_parsed", 0),
                        "failed_pages": len(stats.get("errors", [])),
                        "total_attributes": stats.get("variations_created", 0),
                        "errors": stats.get("errors", []),
                        "elapsed": elapsed,
                    }
                )
        except Exception as exc:
            result = {"success": False, "error": str(exc)}
        finally:
            self.finished_signal.emit(result)

    async def _run_async_parsing(self) -> dict:
        """Core asynchronous parsing logic."""
        from playwright.async_api import async_playwright
        from urllib.parse import urljoin
        from bs4 import BeautifulSoup

        def log_cb(msg):
            self.log_signal.emit(msg)

        def progress_cb(done, total, msg):
            pct = int((done / max(total, 1)) * 100)
            self.progress_signal.emit(pct, total, msg)

        # 1. Получаем URL категорий из БД (извлекаем данные, пока сессия активна)
        category_data = []  # list of (url, category_id)
        with get_session() as session:
            categories = session.query(Category).filter(
                Category.id.in_(self.category_ids)
            ).all()
            for cat in categories:
                category_data.append((cat.url, cat.id))

        if not category_data:
            self.log_signal.emit("Нет URL категорий для парсинга.")
            return {"success": False, "error": "Нет URL категорий", "stats": {}}

        # 2. Собираем URL продуктов со страниц категорий через Playwright
        # Если выбранная категория содержит подкатегории, рекурсивно парсим все leaf-категории
        from urllib.parse import urlparse
        
        def find_leaf_category_urls(categories_map: dict, visited: set = None) -> dict:
            """Для каждой выбранной категории находит все leaf-подкатегории (конечные, без дочерних).
            
            Аргумент visited защищает от бесконечной рекурсии при циклической иерархии категорий.
            """
            if visited is None:
                visited = set()
            
            url_to_cat_id: dict[str, Tuple[int, str]] = {}
            for cat_url, cat_id in categories_map.items():
                # Защита от циклических ссылок
                if cat_id in visited:
                    continue
                visited.add(cat_id)
                
                full_url = urljoin(self.base_url, cat_url) if not cat_url.startswith("http") else cat_url
                cat_path = urlparse(full_url).path.rstrip("/")
                
                # Получаем все подкатегории из БД
                sub_cats = []
                with get_session() as session:
                    sub_cats = session.query(Category).filter(
                        Category.supplier_id == self.supplier_id,
                        Category.parent_id == cat_id
                    ).all()
                
                if not sub_cats:
                    # Нет дочерних категорий — это leaf-категория, парсим продукты напрямую
                    url_to_cat_id[full_url] = (cat_id, cat_path)
                else:
                    # Есть дочерние категории — рекурсивно находит leaf-категории
                    sub_map = {c.url: c.id for c in sub_cats if c.url}
                    sub_result = find_leaf_category_urls(sub_map, visited)
                    url_to_cat_id.update(sub_result)
            
            return url_to_cat_id
        
        # Находим leaf-категории для парсинга
        cat_data_map = {cat_url: cat_id for cat_url, cat_id in category_data}
        leaf_urls = find_leaf_category_urls(cat_data_map)
        
        self.log_signal.emit(f"Найдено leaf-категорий для парсинга: {len(leaf_urls)}")
        
        url_to_category: dict[str, int] = {}
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            page = await browser.new_page()
            try:
                for full_url, (cat_id, cat_path) in leaf_urls.items():
                    if self._engine and self._engine._cancelled:
                        break
                    self.log_signal.emit(f"Сбор URL с: {full_url}")
                    
                    try:
                        await page.goto(full_url, wait_until="domcontentloaded", timeout=30000)
                        # Ждём появления ссылок на товары
                        try:
                            await page.wait_for_selector('a[href*="/catalog/product/"]', timeout=10000)
                        except Exception:
                            self.log_signal.emit(f"  ⚠️ Ссылки на товары не появились через 10с, пробуем всё равно")
                        
                        # Скроллим для lazy-load
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await asyncio.sleep(2)
                        await page.evaluate("window.scrollTo(0, 0)")
                        
                        html = await page.content()
                        
                        # Отладка через regex
                        import re
                        links = re.findall(r'href=["\']([^"\']*?/catalog/product/[^"\']*?)["\']', html)
                        self.log_signal.emit(f"  Отладка: найдено через regex {len(links)} ссылок")
                        if links:
                            self.log_signal.emit(f"  Примеры ссылок: {links[:3]}")
                        
                        soup = BeautifulSoup(html, "lxml")
                        found_on_page = 0
                        for a in soup.find_all("a", href=True):
                            href = a["href"].strip()
                            if "/catalog/product/" in href:
                                full = urljoin(full_url, href)
                                clean = full.split("#")[0].split("?")[0].rstrip("/")
                                # Сохраняем category_id для каждого URL (первая найденная категория)
                                if clean not in url_to_category:
                                    url_to_category[clean] = cat_id
                                    found_on_page += 1
                        self.log_signal.emit(f"  → найдено {found_on_page} URL продуктов")
                    except Exception as e:
                        self.log_signal.emit(f"  Ошибка загрузки категории: {e}")
            finally:
                await browser.close()

        product_urls = list(url_to_category.keys())
        self.log_signal.emit(f"Всего URL продуктов для парсинга: {len(product_urls)}")

        if not product_urls:
            return {"success": False, "error": "URL продуктов не найдены", "stats": {}}

        # 3. Запускаем TandoorPlaywrightParser
        self._engine = TandoorPlaywrightParser(
            supplier_id=self.supplier_id,
            headless=self.headless,
            debug_mode=self.debug_mode,
            log_callback=log_cb,
            progress_callback=progress_cb,
        )

        # Создаём сессию напрямую, чтобы парсер управлял commit/rollback сам.
        # get_session() делает автоматический commit, что конфликтует с commit внутри парсера.
        session = SessionFactory()
        try:
            result = await self._engine.run(session, urls=product_urls, url_to_category=url_to_category)
        finally:
            session.close()

        return {
            "success": True,
            "products_parsed": result.get("products_parsed", 0),
            "variations_created": result.get("variations_created", 0),
            "stats": result,
        }

    def cancel(self):
        if self._engine:
            self._engine.cancel()

    def pause(self):
        if self._engine:
            self._engine.pause()

    def resume(self):
        if self._engine:
            self._engine.resume()


class ParsingPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: Optional[ParsingWorker] = None
        self._thread: Optional[QThread] = None
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        ctrl_group = QGroupBox("Управление парсингом")
        ctrl_layout = QVBoxLayout(ctrl_group)

        supplier_row = QHBoxLayout()
        supplier_row.addWidget(QLabel("Поставщик:"))
        self._supplier_combo = QComboBox()
        self._supplier_combo.setMinimumWidth(300)
        supplier_row.addWidget(self._supplier_combo)
        supplier_row.addStretch()
        ctrl_layout.addLayout(supplier_row)

        options_row = QHBoxLayout()
        options_row.addWidget(QLabel("Параллелизм:"))
        self._concurrency_combo = QComboBox()
        self._concurrency_combo.addItems(["3", "5", "8", "10", "15"])
        self._concurrency_combo.setCurrentText("5")
        self._concurrency_combo.setMaximumWidth(60)
        options_row.addWidget(self._concurrency_combo)

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
        options_row.addWidget(QLabel("Таймаут (с):"))
        self._timeout_combo = QComboBox()
        self._timeout_combo.addItems(["15", "30", "60", "120"])
        self._timeout_combo.setCurrentText("30")
        self._timeout_combo.setMaximumWidth(70)
        options_row.addWidget(self._timeout_combo)

        options_row.addStretch()
        ctrl_layout.addLayout(options_row)

        btn_row = QHBoxLayout()
        self._btn_start = QPushButton("Запустить парсинг")
        self._btn_start.setMinimumHeight(40)
        self._btn_pause = QPushButton("Пауза")
        self._btn_pause.setMinimumHeight(40)
        self._btn_pause.setEnabled(False)
        self._btn_stop = QPushButton("Стоп")
        self._btn_stop.setMinimumHeight(40)
        self._btn_stop.setEnabled(False)
        self._btn_select_all = QPushButton("Выбрать все")
        self._btn_select_all.setMinimumHeight(40)
        self._btn_select_none = QPushButton("Снять выбор")
        self._btn_select_none.setMinimumHeight(40)
        btn_row.addWidget(self._btn_start)
        btn_row.addWidget(self._btn_pause)
        btn_row.addWidget(self._btn_stop)
        btn_row.addSpacing(16)
        btn_row.addWidget(self._btn_select_all)
        btn_row.addWidget(self._btn_select_none)
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

        cat_group = QGroupBox("Категории (отметьте для парсинга)")
        cat_layout = QVBoxLayout(cat_group)
        self._cat_tree = QTreeView()
        self._cat_model = CategoryCheckModel()
        self._cat_tree.setModel(self._cat_model)
        self._cat_tree.setAlternatingRowColors(True)
        self._cat_tree.header().setStretchLastSection(False)
        self._cat_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._cat_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self._cat_tree.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        cat_layout.addWidget(self._cat_tree)
        splitter.addWidget(cat_group)

        stats_group = QGroupBox("Статус задач")
        stats_layout = QVBoxLayout(stats_group)
        self._task_table = QTableView()
        self._task_model = TaskStatusModel()
        self._task_table.setModel(self._task_model)
        self._task_table.setAlternatingRowColors(True)
        self._task_table.horizontalHeader().setStretchLastSection(True)
        stats_layout.addWidget(self._task_table)
        splitter.addWidget(stats_group)

        log_group = QGroupBox("Журнал парсинга")
        log_layout = QVBoxLayout(log_group)
        self._log_edit = QPlainTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(180)
        log_layout.addWidget(self._log_edit)
        splitter.addWidget(log_group)

        stats_row = QHBoxLayout()
        self._stat_products = QLabel("Товаров: 0")
        self._stat_pages = QLabel("Страниц: 0")
        self._stat_errors = QLabel("Ошибок: 0")
        self._stat_time = QLabel("Время: 0.0с")
        self._stat_attrs = QLabel("Атрибутов: 0")
        stats_row.addWidget(self._stat_products)
        stats_row.addWidget(self._stat_pages)
        stats_row.addWidget(self._stat_errors)
        stats_row.addWidget(self._stat_time)
        stats_row.addWidget(self._stat_attrs)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        splitter.setSizes([250, 150, 180])
        layout.addWidget(splitter)

        self._btn_start.clicked.connect(self._on_start)
        self._btn_pause.clicked.connect(self._on_pause)
        self._btn_stop.clicked.connect(self._on_stop)
        self._btn_select_all.clicked.connect(self._cat_model.check_all)
        self._btn_select_none.clicked.connect(self._cat_model.uncheck_all)
        self._supplier_combo.currentIndexChanged.connect(self._on_supplier_changed)

    def _load_suppliers(self):
        self._supplier_combo.clear()
        try:
            with get_session() as session:
                suppliers = (
                    session.query(Supplier)
                    .filter(Supplier.is_active == True)
                    .order_by(Supplier.name)
                    .all()
                )
                for s in suppliers:
                    self._supplier_combo.addItem(s.name, userData=s.id)
        except Exception as exc:
            self._append_log(f"Ошибка загрузки поставщиков: {exc}")

    def _on_supplier_changed(self):
        supplier_id = self._supplier_combo.currentData()
        if supplier_id:
            count = self._cat_model.load_categories(supplier_id)
            self._append_log(f"Загружено {count} категорий верхнего уровня")

    def _append_log(self, msg: str):
        from datetime import datetime

        ts = datetime.now().strftime("%H:%M:%S")
        self._log_edit.appendPlainText(f"[{ts}] {msg}")

    def _on_start(self):
        if self._thread and self._thread.isRunning():
            QMessageBox.warning(self, "Внимание", "Парсинг уже запущен.")
            return

        supplier_id = self._supplier_combo.currentData()
        if supplier_id is None:
            QMessageBox.warning(self, "Нет поставщика", "Сначала выберите поставщика.")
            return

        category_ids = self._cat_model.get_checked_ids()
        if not category_ids:
            QMessageBox.warning(
                self, "Нет категорий", "Выберите хотя бы одну категорию для парсинга."
            )
            return

        with get_session() as session:
            supplier = session.query(Supplier).filter(Supplier.id == supplier_id).first()
            if not supplier:
                QMessageBox.warning(self, "Ошибка", "Поставщик не найден.")
                return
            base_url = supplier.base_url

        self._btn_start.setEnabled(False)
        self._btn_pause.setEnabled(True)
        self._btn_stop.setEnabled(True)
        self._progress_bar.setValue(0)
        self._progress_label.setText("Запуск...")
        self._log_edit.clear()
        self._task_model.clear()
        self._reset_stats()

        self._append_log(f"Запуск парсинга для '{self._supplier_combo.currentText()}'")
        self._append_log(f"Выбрано категорий: {len(category_ids)}")

        concurrency = int(self._concurrency_combo.currentText())
        delay_min = float(self._delay_min_input.currentText())
        delay_max = float(self._delay_max_input.currentText())
        timeout = int(self._timeout_combo.currentText())

        self._thread = QThread()
        self._worker = ParsingWorker(
            supplier_id=supplier_id,
            base_url=base_url,
            category_ids=category_ids,
            headless=True,
            debug_mode=False,
        )
        self._worker.moveToThread(self._thread)

        self._worker.log_signal.connect(self._append_log)
        self._worker.progress_signal.connect(self._on_progress)
        self._worker.stats_signal.connect(self._on_stats)
        self._worker.finished_signal.connect(self._on_finished)

        # Связываем сигналы потока и воркера для корректного запуска и остановки
        self._thread.started.connect(self._worker.run_task)
        self._worker.finished_signal.connect(self._thread.quit)  # <--- ДОБАВЛЕНО: Говорим потоку завершиться
        self._thread.finished.connect(self._worker.deleteLater) # Очищаем воркер после потока
        self._thread.finished.connect(self._thread.deleteLater)  # Очищаем сам поток

        self._thread.start()

    def _on_pause(self):
        if not (self._thread and self._thread.isRunning()):
            return
        if self._btn_pause.text() == "Пауза":
            self._worker.pause()
            self._btn_pause.setText("Продолжить")
            self._append_log("Парсинг приостановлен")
        else:
            self._worker.resume()
            self._btn_pause.setText("Пауза")
            self._append_log("Парсинг возобновлён")

    def _on_stop(self):
        if self._thread and self._thread.isRunning():
            self._append_log("Остановка парсинга...")
            if self._worker:
                self._worker.cancel()
            self._btn_stop.setEnabled(False)
            self._btn_pause.setEnabled(False)

    def _on_progress(self, pct: int, total: int, msg: str):
        self._progress_bar.setValue(min(pct, 100))
        self._progress_label.setText(f"{pct}% — {msg}")

    def _on_stats(self, stats: dict):
        self._stat_products.setText(f"Товаров: {stats.get('total_products', 0)}")
        self._stat_pages.setText(f"Страниц: {stats.get('total_pages', 0)}")
        self._stat_errors.setText(f"Ошибок: {stats.get('failed_pages', 0)}")
        self._stat_time.setText(f"Время: {stats.get('elapsed', 0):.1f}с")
        self._stat_attrs.setText(f"Атрибутов: {stats.get('total_attributes', 0)}")

    def _on_finished(self, result: dict):
        self._btn_start.setEnabled(True)
        self._btn_pause.setEnabled(False)
        self._btn_stop.setEnabled(False)
        self._btn_pause.setText("Пауза")

        if result.get("success", True):
            count = result.get("products_parsed", 0)
            self._progress_bar.setValue(100)
            self._progress_label.setText(f"Готово — {count} товаров обработано")
            self._append_log(f"Парсинг завершён: {count} товаров")
            QMessageBox.information(
                self, "Успех", f"Парсинг завершён.\nСохранено {count} товаров."
            )
        else:
            error = result.get("error", "Неизвестная ошибка")
            self._progress_label.setText(f"Ошибка: {error}")
            self._append_log(f"Парсинг не удался: {error}")
            QMessageBox.critical(
                self, "Ошибка парсинга", f"Парсинг не удался:\n{error}"
            )
        
        self._thread = None
        self._worker = None


    def _reset_stats(self):
        self._stat_products.setText("Товаров: 0")
        self._stat_pages.setText("Страниц: 0")
        self._stat_errors.setText("Ошибок: 0")
        self._stat_time.setText("Время: 0.0с")
        self._stat_attrs.setText("Атрибутов: 0")
