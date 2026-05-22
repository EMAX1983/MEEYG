import os
import fnmatch
from pathlib import Path

# --- НАСТРОЙКИ ---
OUTPUT_FILE = "project_info.md"
MAX_FILE_SIZE = 100 * 1024  # 100 КБ (чтобы не перегружать контекст)

EXCLUDE_DIRS = {
    "__pycache__", ".git", ".venv", "venv", ".idea", ".vscode", 
    "node_modules", "backups", ".pytest_cache", ".mypy_cache"
}

EXCLUDE_PATTERNS = [
    "*.pyc", "*.pyo", "*.so", "*.dll", "*.exe", "*.db", "*.sqlite",
    "*.log", "*.tmp", "*.xlsx", "*.csv", "*.png", "*.jpg", "*.jpeg",
    "*.webp", "*.svg", "*.ico", "*.zip", "*.rar", "*.tar", "*.gz"
]

def should_exclude_dir(name):
    return name in EXCLUDE_DIRS or name.startswith(".")

def should_exclude_file(name):
    return any(fnmatch.fnmatch(name, pattern) for pattern in EXCLUDE_PATTERNS)

def get_tree(root, prefix=""):
    tree = []
    try:
        items = sorted(os.listdir(root))
        dirs, files = [], []
        for item in items:
            path = os.path.join(root, item)
            if os.path.isdir(path):
                if not should_exclude_dir(item):
                    dirs.append(item)
            else:
                if not should_exclude_file(item):
                    files.append(item)

        for i, d in enumerate(dirs):
            is_last = (i == len(dirs) - 1) and (len(files) == 0)
            tree.append(f"{prefix}{'└── ' if is_last else '├── '}{d}/")
            ext = "    " if is_last else "│   "
            tree.extend(get_tree(os.path.join(root, d), prefix + ext))

        for i, f in enumerate(files):
            is_last = (i == len(files) - 1)
            tree.append(f"{prefix}{'└── ' if is_last else '├── '}{f}")
    except PermissionError:
        tree.append(f"{prefix}[Permission Denied]")
    return tree

def collect_files(root):
    contents = []
    output_abs = os.path.abspath(OUTPUT_FILE)
    
    for current_root, dirs, files in os.walk(root):
        # Фильтрация папок на лету, чтобы не заходить в них
        dirs[:] = [d for d in dirs if not should_exclude_dir(d)]
        
        for file in sorted(files):
            if should_exclude_file(file):
                continue
                
            file_path = os.path.join(current_root, file)
            rel_path = os.path.relpath(file_path, root)
            
            # Пропускаем сам файл отчёта
            if os.path.abspath(file_path) == output_abs:
                continue
                
            # Пропускаем слишком большие файлы
            try:
                if os.path.getsize(file_path) > MAX_FILE_SIZE:
                    contents.append(f"### `{rel_path}`\n*(Пропущен: размер > {MAX_FILE_SIZE//1024} КБ)*\n")
                    continue
            except Exception:
                continue

            # Читаем текст
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()
                    # Определяем язык для подсветки
                    ext = os.path.splitext(file)[1].lower()
                    lang_map = {".py": "python", ".js": "javascript", ".json": "json", 
                                ".md": "markdown", ".yml": "yaml", ".yaml": "yaml", 
                                ".txt": "text", ".cfg": "ini", ".ini": "ini"}
                    lang = lang_map.get(ext, "text")
                    contents.append(f"### `{rel_path}`\n```{lang}\n{code}\n```\n")
            except UnicodeDecodeError:
                contents.append(f"### `{rel_path}`\n*(Пропущен: бинарный файл)*\n")
            except Exception as e:
                contents.append(f"### `{rel_path}`\n*(Ошибка чтения: {e})*\n")
                
    return contents

def main():
    print("🔍 Сканер проекта MEEYG 2.0")
    project_dir = os.path.abspath(".")
    print(f"📁 Сканирую: {project_dir}")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("# 📦 Структура и содержимое проекта MEEYG 2.0\n\n")
        
        out.write("## 🌳 Дерево папок\n```text\n")
        tree = get_tree(project_dir)
        out.write("\n".join(tree))
        out.write("\n```\n\n")
        
        out.write("## 📄 Содержимое файлов\n")
        file_contents = collect_files(project_dir)
        out.write("\n".join(file_contents))
        
    print(f"✅ Готово! Файл сохранён: {os.path.abspath(OUTPUT_FILE)}")
    print(f"📤 Теперь загрузи `{OUTPUT_FILE}` в чат, и я проверю структуру, импорты и логику.")

if __name__ == "__main__":
    main()
