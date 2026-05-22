from pathlib import Path
path = Path('src/ui/pages/archive_page.py')
text = path.read_text(encoding='latin-1')
needle = '        self.btn_export_archive = QPushButton('
idx = text.index(needle)
end = text.index('\n', idx)
new_line = '        self.btn_export_archive = QPushButton( Сохранить архив)'
text = text[:idx] + new_line + text[end:]
path.write_text(text, encoding='latin-1')
