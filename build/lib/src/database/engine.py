import ctypes
import os
import secrets
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine as _sa_create_engine

from src.core.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROTECTED_KEY_PATH = PROJECT_ROOT / "data" / ".db_key.protected"


class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", ctypes.c_ulong), ("pbData", ctypes.POINTER(ctypes.c_ubyte))]


def _generate_key() -> str:
    return secrets.token_hex(32)


def _protect_key_dpapi(key: str) -> bytes:
    key_bytes = key.encode("utf-16-le")
    blob_in = DATA_BLOB()
    blob_in.cbData = len(key_bytes)
    buf = (ctypes.c_ubyte * len(key_bytes)).from_buffer_copy(key_bytes)
    blob_in.pbData = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))

    blob_out = DATA_BLOB()

    result = ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(blob_in),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(blob_out),
    )
    if not result:
        raise RuntimeError("DPAPI CryptProtectData failed")

    protected = bytes(
        ctypes.string_at(
            ctypes.cast(blob_out.pbData, ctypes.POINTER(ctypes.c_ubyte)),
            blob_out.cbData,
        )
    )
    ctypes.windll.kernel32.LocalFree(blob_out.pbData)
    return protected


def _unprotect_key_dpapi(protected: bytes) -> str:
    blob_in = DATA_BLOB()
    blob_in.cbData = len(protected)
    buf = (ctypes.c_ubyte * len(protected)).from_buffer_copy(protected)
    blob_in.pbData = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))

    blob_out = DATA_BLOB()

    result = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(blob_in),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(blob_out),
    )
    if not result:
        raise RuntimeError("DPAPI CryptUnprotectData failed")

    decrypted = bytes(
        ctypes.string_at(
            ctypes.cast(blob_out.pbData, ctypes.POINTER(ctypes.c_ubyte)),
            blob_out.cbData,
        )
    )
    ctypes.windll.kernel32.LocalFree(blob_out.pbData)
    return decrypted.decode("utf-16-le").rstrip("\x00")


def _get_or_create_key() -> str:
    db_key = os.environ.get("DB_KEY", "").strip()

    if db_key:
        return db_key

    if PROTECTED_KEY_PATH.exists():
        try:
            protected = PROTECTED_KEY_PATH.read_bytes()
            return _unprotect_key_dpapi(protected)
        except Exception:
            pass

    new_key = _generate_key()
    protected = _protect_key_dpapi(new_key)
    PROTECTED_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROTECTED_KEY_PATH.write_bytes(protected)
    return new_key


def create_engine():
    key = _get_or_create_key()
    encoded_key = quote_plus(key)
    db_path = str(settings.db_path)
    engine_url = f"sqlite+pysqlcipher://:{encoded_key}@/{db_path}?cipher=aes-256-cfb"
    return _sa_create_engine(engine_url, echo=False)
