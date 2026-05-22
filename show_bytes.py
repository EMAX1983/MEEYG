from pathlib import Path
text = Path('src/ui/pages/archive_page.py').read_bytes()
pattern = b'self.btn_export_archive ='
idx = text.index(pattern)
print(text[idx-30:idx+90])
