#!/usr/bin/env python3
"""Setup script for MEEYG 1.0 environment."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"
PYTHON_MIN = (3, 12)


def print_step(msg: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {msg}")
    print(f"{'=' * 60}")


def check_python_version() -> None:
    print_step("Checking Python version")
    current = sys.version_info
    print(f"  Current Python: {current.major}.{current.minor}.{current.micro}")
    if current < PYTHON_MIN:
        print(f"  ERROR: Python {'.'.join(map(str, PYTHON_MIN))}+ required")
        sys.exit(1)
    print("  OK: Python version meets requirements")


def ensure_uv() -> None:
    print_step("Checking for uv package manager")
    if shutil.which("uv"):
        print("  uv found in PATH")
        return

    print("  uv not found, installing via pip...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "uv", "--quiet"],
        check=True,
    )
    print("  uv installed successfully")


def create_venv() -> None:
    print_step("Creating virtual environment")
    if VENV_DIR.exists():
        print(f"  Removing existing venv at {VENV_DIR}")
        shutil.rmtree(VENV_DIR)

    subprocess.run(
        ["uv", "venv", str(VENV_DIR)],
        check=True,
        cwd=PROJECT_ROOT,
    )
    print(f"  Virtual environment created at {VENV_DIR}")


def install_dependencies() -> None:
    print_step("Installing dependencies")
    venv_python = VENV_DIR / "Scripts" / "python.exe" if os.name == "nt" else VENV_DIR / "bin" / "python"

    subprocess.run(
        ["uv", "pip", "install", "-e", ".", "--python", str(venv_python)],
        check=True,
        cwd=PROJECT_ROOT,
    )
    print("  All dependencies installed successfully")


def create_env_file() -> None:
    print_step("Creating .env file")
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        print(f"  .env already exists at {env_path}, skipping")
        return

    import secrets
    db_key = secrets.token_hex(32)

    env_content = f"""# Database encryption key (32 bytes, hex-encoded)
DB_KEY={db_key}

# Database path
DB_PATH=data/meeyg.db

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Application settings
APP_NAME=MEEYG
APP_VERSION=1.0.0
"""
    env_path.write_text(env_content)
    print(f"  .env file created at {env_path}")
    print("  IMPORTANT: Keep DB_KEY secure and never commit it to version control")


def verify_installation() -> None:
    print_step("Verifying installation")
    venv_python = VENV_DIR / "Scripts" / "python.exe" if os.name == "nt" else VENV_DIR / "bin" / "python"

    required_packages = [
        "sqlalchemy",
        "pandas",
        "pydantic",
        "structlog",
        "aiohttp",
        "beautifulsoup4",
        "lxml",
        "tenacity",
        "tqdm",
        "python-dotenv",
    ]

    failed = []
    for pkg in required_packages:
        result = subprocess.run(
            [str(venv_python), "-c", f"import {pkg.split('-')[0]}"],
            capture_output=True,
        )
        status = "OK" if result.returncode == 0 else "FAILED"
        print(f"  {pkg}: {status}")
        if result.returncode != 0:
            failed.append(pkg)

    if failed:
        print(f"\n  WARNING: Failed to import: {', '.join(failed)}")
    else:
        print("\n  All packages verified successfully")


def main() -> None:
    print("\n" + "=" * 60)
    print("  MEEYG 1.0 - Environment Setup")
    print("=" * 60)

    check_python_version()
    ensure_uv()
    create_venv()
    install_dependencies()
    create_env_file()
    verify_installation()

    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    print(f"\n  Project root: {PROJECT_ROOT}")
    print(f"  Virtual env:  {VENV_DIR}")
    print(f"  Activate:     {'call .venv\\Scripts\\activate.bat' if os.name == 'nt' else 'source .venv/bin/activate'}")
    print()


if __name__ == "__main__":
    main()
