from pathlib import Path
path = Path('src/ui/pages/archive_page.py')
lines = path.read_text(encoding='utf-8').splitlines()
start_marker = '        self.btn_refresh = QPushButton( Обновить)'
end_marker = '        self.status_label = QLabel(Загрузка...)'
start = lines.index(start_marker)
end = lines.index(end_marker)
new_block = '''        self.btn_refresh = QPushButton(Обновить)
        self.btn_refresh.setMinimumHeight(36)
        self.btn_refresh.clicked.connect(self.load_data)

        self.btn_select_all = QPushButton(Выбрать все)
        self.btn_select_all.setMinimumHeight(36)
        self.btn_select_all.clicked.connect(self.on_select_all)

        self.btn_deselect_all = QPushButton(Снять все)
        self.btn_deselect_all.setMinimumHeight(36)
        self.btn_deselect_all.clicked.connect(self.on_deselect_all)

        self.btn_invert = QPushButton(Инвертировать)
        self.btn_invert.setMinimumHeight(36)
        self.btn_invert.clicked.connect(self.on_invert_selection)

        self.btn_edit = QPushButton(Редактировать)
        self.btn_edit.setMinimumHeight(36)
        self.btn_edit.clicked.connect(self.on_edit)

        self.btn_delete = QPushButton(Удалить)
        self.btn_delete.setMinimumHeight(36)
        self.btn_delete.clicked.connect(self.on_delete)

        self.btn_export_archive = QPushButton(Сохранить архив)
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
        main_layout.addLayout(btn_layout)'''.splitlines()
lines[start:end] = new_block
path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
