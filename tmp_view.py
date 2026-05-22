from pathlib import Path
path = Path('src/ui/pages/archive_page.py')
lines = path.read_text(encoding='utf-8').splitlines()
for i in range(300, 330):
    print(i+1, repr(lines[i]))
