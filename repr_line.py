from pathlib import Path
line = Path('src/ui/pages/archive_page.py').read_text(encoding='cp1251').splitlines()[320]
print(repr(line))
