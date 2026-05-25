from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MEEYG 1.0")
        self.setMinimumSize(1200, 800)

        self._nav_buttons: list[QPushButton] = []
        self._pages: list[QWidget] = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        root_layout.addWidget(sidebar)

        self._stack = QStackedWidget()
        self._stack.setObjectName("contentArea")
        root_layout.addWidget(self._stack, 1)

        self.statusBar().showMessage("Готово")

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar.setFrameShape(QFrame.NoFrame)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 24, 16, 16)
        layout.setSpacing(8)

        title = QLabel("MEEYG")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Разведка поставщиков")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(16)

        nav_items = [
            ("Главная", 0),
            ("Поставщики", 1),
            ("Разведка", 2),
            ("Парсинг", 3),
            ("Архив", 4),
            ("Аналитика", 5),
            ("Экспорт", 6),
        ]

        for label, index in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setMinimumHeight(44)
            btn.clicked.connect(lambda _, idx=index: self.switch_page(idx))
            layout.addWidget(btn)
            self._nav_buttons.append(btn)

        layout.addStretch()

        self._nav_buttons[0].setChecked(True)

        return sidebar

    def register_page(self, page: QWidget) -> int:
        index = self._stack.addWidget(page)
        self._pages.append(page)
        return index

    def switch_page(self, index: int) -> None:
        for btn in self._nav_buttons:
            btn.setChecked(False)
        if 0 <= index < len(self._nav_buttons):
            self._nav_buttons[index].setChecked(True)
        self._stack.setCurrentIndex(index)
        page_names = ["Главная", "Поставщики", "Разведка", "Парсинг", "Архив", "Аналитика", "Экспорт"]
        if 0 <= index < len(page_names):
            self.statusBar().showMessage(f"Страница: {page_names[index]}")
