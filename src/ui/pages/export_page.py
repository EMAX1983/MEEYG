import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from src.core.config import settings
from src.database.models import Category, Supplier
from src.database.session import get_session
from src.modules.export.generator import ExportConfig, ExportEngine


class ExportWorker(QThread):
    log_signal = Signal(str)
    progress_signal = Signal(int, int, str)
    finished_signal = Signal(dict)

    def __init__(self, config: ExportConfig):
        super().__init__()
        self.config = config

    def run(self):
        def log_cb(msg):
            self.log_signal.emit(msg)

        def progress_cb(pct, total, msg):
            self.progress_signal.emit(pct, total, msg)

        engine = ExportEngine(
            config=self.config,
            log_callback=log_cb,
            progress_callback=progress_cb,
        )

        try:
            with get_session() as session:
                result = engine.run(session)
            self.finished_signal.emit(result)
        except Exception as exc:
            self.finished_signal.emit({"success": False, "error": str(exc)})


class ValidationModel(QAbstractTableModel):
    _headers = ["Предупреждение"]

    def __init__(self):
        super().__init__()
        self._warnings: list[str] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._warnings)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return self._warnings[index.row()]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._headers[section]
        return None

    def set_warnings(self, warnings: list[str]):
        self._warnings = warnings
        self.layoutChanged.emit()


class ExportPage(QWidget):
    def __init__(self):
        super().__init__()
        self._worker: Optional[ExportWorker] = None
        self._setup_ui()
        self._load_suppliers()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        filter_group = QGroupBox("Фильтры экспорта")
        filter_layout = QVBoxLayout(filter_group)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Поставщик:"))
        self._supplier_list = QListWidget()
        self._supplier_list.setMaximumHeight(100)
        row1.addWidget(self._supplier_list)
        filter_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Категория:"))
        self._category_list = QListWidget()
        self._category_list.setMaximumHeight(100)
        row2.addWidget(self._category_list)
        filter_layout.addLayout(row2)

        row3 = QHBoxLayout()
        self._ready_check = QCheckBox("Только готовые к экспорту")
        self._ready_check.setChecked(True)
        row3.addWidget(self._ready_check)
        self._available_check = QCheckBox("Только доступные")
        row3.addWidget(self._available_check)
        row3.addStretch()
        filter_layout.addLayout(row3)

        layout.addWidget(filter_group)

        settings_group = QGroupBox("Настройки экспорта")
        settings_layout = QVBoxLayout(settings_group)

        s_row1 = QHBoxLayout()
        s_row1.addWidget(QLabel("Формат:"))
        self._format_combo = QComboBox()
        self._format_combo.addItems(["Excel (.xlsx)", "CSV (.csv)"])
        self._format_combo.setMaximumWidth(150)
        s_row1.addWidget(self._format_combo)

        s_row1.addSpacing(24)
        s_row1.addWidget(QLabel("Кодировка:"))
        self._encoding_combo = QComboBox()
        self._encoding_combo.addItems(["UTF-8 с BOM", "UTF-8", "Windows-1251"])
        self._encoding_combo.setMaximumWidth(180)
        s_row1.addWidget(self._encoding_combo)

        s_row1.addSpacing(24)
        s_row1.addWidget(QLabel("Разделитель изображений:"))
        self._img_sep_combo = QComboBox()
        self._img_sep_combo.addItems(["|", ",", ";"])
        self._img_sep_combo.setMaximumWidth(60)
        s_row1.addWidget(self._img_sep_combo)

        s_row1.addStretch()
        settings_layout.addLayout(s_row1)

        s_row2 = QHBoxLayout()
        s_row2.addWidget(QLabel("Папка вывода:"))
        self._output_input = QLineEdit(str(settings.data_dir / "exports"))
        self._output_input.setMinimumWidth(300)
        s_row2.addWidget(self._output_input)
        self._btn_browse = QPushButton("Обзор...")
        s_row2.addWidget(self._btn_browse)
        s_row2.addStretch()
        settings_layout.addLayout(s_row2)

        layout.addWidget(settings_group)

        btn_row = QHBoxLayout()
        self._btn_validate = QPushButton("Проверить")
        self._btn_validate.setMinimumHeight(40)
        self._btn_export = QPushButton("Сгенерировать файл")
        self._btn_export.setMinimumHeight(40)
        self._btn_export.setStyleSheet(
            "background-color: #e94560; color: white; font-weight: bold;"
        )
        self._btn_open_folder = QPushButton("Открыть папку экспорта")
        self._btn_open_folder.setMinimumHeight(40)
        btn_row.addWidget(self._btn_validate)
        btn_row.addWidget(self._btn_export)
        btn_row.addWidget(self._btn_open_folder)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        progress_row = QHBoxLayout()
        self._progress_bar = QProgressBar()
        self._progress_bar.setMinimumHeight(20)
        self._progress_label = QLabel("Готово")
        progress_row.addWidget(self._progress_bar, 1)
        progress_row.addWidget(self._progress_label)
        layout.addLayout(progress_row)

        splitter = QSplitter(Qt.Vertical)

        warn_group = QGroupBox("Предупреждения валидации")
        warn_layout = QVBoxLayout(warn_group)
        self._warn_table = QTableView()
        self._warn_model = ValidationModel()
        self._warn_table.setModel(self._warn_model)
        self._warn_table.horizontalHeader().setStretchLastSection(True)
        self._warn_table.setMaximumHeight(120)
        warn_layout.addWidget(self._warn_table)
        splitter.addWidget(warn_group)

        log_group = QGroupBox("Журнал экспорта")
        log_layout = QVBoxLayout(log_group)
        self._log_edit = QPlainTextEdit()
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumHeight(200)
        log_layout.addWidget(self._log_edit)
        splitter.addWidget(log_group)

        layout.addWidget(splitter)

        stats_row = QHBoxLayout()
        self._stat_total = QLabel("Всего: 0")
        self._stat_exported = QLabel("Экспортировано: 0")
        self._stat_duplicates = QLabel("Дубликаты: 0")
        self._stat_size = QLabel("Размер: 0 КБ")
        self._stat_time = QLabel("Время: 0.0с")
        stats_row.addWidget(self._stat_total)
        stats_row.addWidget(self._stat_exported)
        stats_row.addWidget(self._stat_duplicates)
        stats_row.addWidget(self._stat_size)
        stats_row.addWidget(self._stat_time)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        self._btn_validate.clicked.connect(self._on_validate)
        self._btn_export.clicked.connect(self._on_export)
        self._btn_open_folder.clicked.connect(self._on_open_folder)
        self._btn_browse.clicked.connect(self._on_browse)
        self._supplier_list.itemChanged.connect(self._on_supplier_changed)

    def _load_suppliers(self):
        self._supplier_list.clear()
        self._category_list.clear()
        try:
            with get_session() as session:
                suppliers = session.query(Supplier).filter(
                    Supplier.is_active == True
                ).order_by(Supplier.name).all()
                for s in suppliers:
                    item = self._supplier_list.item(self._supplier_list.count())
                    from PySide6.QtWidgets import QListWidgetItem
                    item = QListWidgetItem(s.name)
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)
                    item.setData(Qt.UserRole, s.id)
                    self._supplier_list.addItem(item)
        except Exception as exc:
            self._append_log(f"Ошибка загрузки поставщиков: {exc}")

    def _on_supplier_changed(self, item):
        self._category_list.clear()
        checked_ids = self._get_checked_supplier_ids()
        if checked_ids:
            try:
                with get_session() as session:
                    categories = session.query(Category).filter(
                        Category.supplier_id.in_(checked_ids)
                    ).order_by(Category.name).all()
                    for c in categories:
                        from PySide6.QtWidgets import QListWidgetItem
                        cat_item = QListWidgetItem(c.name)
                        cat_item.setFlags(cat_item.flags() | Qt.ItemIsUserCheckable)
                        cat_item.setCheckState(Qt.Unchecked)
                        cat_item.setData(Qt.UserRole, c.id)
                        self._category_list.addItem(cat_item)
            except Exception:
                pass

    def _get_checked_supplier_ids(self) -> list[int]:
        ids = []
        for i in range(self._supplier_list.count()):
            item = self._supplier_list.item(i)
            if item.checkState() == Qt.Checked:
                ids.append(item.data(Qt.UserRole))
        return ids or None

    def _get_checked_category_ids(self) -> list[int]:
        ids = []
        for i in range(self._category_list.count()):
            item = self._category_list.item(i)
            if item.checkState() == Qt.Checked:
                ids.append(item.data(Qt.UserRole))
        return ids or None

    def _append_log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_edit.appendPlainText(f"[{ts}] {msg}")

    def _get_config(self) -> ExportConfig:
        fmt = "xlsx" if self._format_combo.currentText().startswith("Excel") else "csv"

        encoding_map = {
            "UTF-8 with BOM": "utf-8-sig",
            "UTF-8": "utf-8",
            "Windows-1251": "cp1251",
        }
        encoding = encoding_map.get(self._encoding_combo.currentText(), "utf-8-sig")

        return ExportConfig(
            supplier_ids=self._get_checked_supplier_ids(),
            category_ids=self._get_checked_category_ids(),
            ready_only=self._ready_check.isChecked(),
            available_only=self._available_check.isChecked(),
            format=fmt,
            encoding=encoding,
            image_separator=self._img_sep_combo.currentText(),
            output_dir=Path(self._output_input.text()),
        )

    def _on_validate(self):
        config = self._get_config()
        engine = ExportEngine(config=config)

        with get_session() as session:
            warnings = engine.validate_before_export(session)

        self._warn_model.set_warnings(warnings)

        if not warnings:
            QMessageBox.information(self, "Валидация", "Проблем не найдено. Готово к экспорту.")
        else:
            errors = [w for w in warnings if "No products" in w]
            if errors:
                QMessageBox.warning(self, "Валидация", "\n".join(warnings))
            else:
                QMessageBox.information(self, "Валидация", "\n".join(warnings))

    def _on_export(self):
        config = self._get_config()
        engine = ExportEngine(config=config)

        with get_session() as session:
            warnings = engine.validate_before_export(session)

        critical = [w for w in warnings if "No products" in w]
        if critical:
            QMessageBox.warning(self, "Невозможно экспортировать", "\n".join(critical))
            return

        if warnings:
            reply = QMessageBox.question(
                self,
                "Предупреждения валидации",
                f"Найдено предупреждений: {len(warnings)}:\n\n"
                + "\n".join(warnings[:5])
                + ("\n..." if len(warnings) > 5 else "")
                + "\n\nПродолжить экспорт?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        self._btn_export.setEnabled(False)
        self._btn_validate.setEnabled(False)
        self._progress_bar.setValue(0)
        self._progress_label.setText("Запуск экспорта...")
        self._log_edit.clear()
        self._reset_stats()
        self._append_log(f"Запуск экспорта (формат={config.format})")

        self._worker = ExportWorker(config=config)
        self._worker.log_signal.connect(self._append_log)
        self._worker.progress_signal.connect(self._on_progress)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.start()

    def _on_progress(self, pct: int, total: int, msg: str):
        self._progress_bar.setValue(min(pct, 100))
        self._progress_label.setText(f"{pct}% — {msg}")

    def _on_finished(self, result: dict):
        self._btn_export.setEnabled(True)
        self._btn_validate.setEnabled(True)

        if result.get("success"):
            stats = result.get("stats")
            self._progress_bar.setValue(100)
            self._progress_label.setText("Экспорт завершён!")
            self._append_log(f"Экспорт завершён: {stats.exported_products} товаров")
            self._append_log(f"Результат: {stats.output_path}")

            self._stat_total.setText(f"Всего: {stats.total_products}")
            self._stat_exported.setText(f"Экспортировано: {stats.exported_products}")
            self._stat_duplicates.setText(f"Дубликаты: {stats.duplicate_skus}")
            self._stat_size.setText(f"Размер: {stats.file_size / 1024:.1f} КБ")
            self._stat_time.setText(f"Время: {stats.elapsed:.1f}с")

            QMessageBox.information(
                self,
                "Экспорт завершён",
                f"Экспортировано {stats.exported_products} товаров.\n"
                f"Файл: {stats.output_path}\n"
                f"Размер: {stats.file_size / 1024:.1f} КБ\n"
                f"Время: {stats.elapsed:.1f}с",
            )
        else:
            error = result.get("error", "Неизвестная ошибка")
            self._progress_label.setText(f"Ошибка: {error}")
            self._append_log(f"Экспорт не удался: {error}")
            if error != "cancelled":
                QMessageBox.critical(self, "Ошибка экспорта", f"Экспорт не удался:\n{error}")

    def _on_open_folder(self):
        folder = Path(self._output_input.text())
        if folder.exists():
            os.startfile(str(folder))
        else:
            QMessageBox.warning(self, "Папка не найдена", f"Папка не существует:\n{folder}")

    def _on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку вывода")
        if folder:
            self._output_input.setText(folder)

    def _reset_stats(self):
        self._stat_total.setText("Всего: 0")
        self._stat_exported.setText("Экспортировано: 0")
        self._stat_duplicates.setText("Дубликаты: 0")
        self._stat_size.setText("Размер: 0 КБ")
        self._stat_time.setText("Время: 0.0с")
