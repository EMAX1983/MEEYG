from pathlib import Path
path = Path( src/ui/pages/archive_page.py)
text = path.read_text(encoding=utf-8)
old = '''        self.btn_delete = QPushButton(Удалить)
        self.btn_delete.setMinimumHeight(36)
        self.btn_delete.clicked.connect(self.on_delete)

        btn_layout.addWidget(self.btn_refresh)'''
new = '''        self.btn_delete = QPushButton(Удалить)
        self.btn_delete.setMinimumHeight(36)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_export_archive = QPushButton(Сохранить архив)
        self.btn_export_archive.setMinimumHeight(36)
        self.btn_export_archive.clicked.connect(self.on_export_archive)

        btn_layout.addWidget(self.btn_refresh)'''
path.write_text(text.replace(old, new, 1), encoding=utf-8)