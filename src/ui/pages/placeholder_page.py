from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PlaceholderPage(QWidget):
    def __init__(self, title: str, description: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setObjectName("subtitle")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
