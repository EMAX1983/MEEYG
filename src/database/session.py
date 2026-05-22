from contextlib import contextmanager

from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

from src.database.engine import create_engine

engine = create_engine()
SessionFactory = sessionmaker(bind=engine)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-64000")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()


@contextmanager
def get_session():
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_session_sync():
    """Синхронный контекстный менеджер для получения сессии БД.
    
    Аналогичен get_session(), но явно помечен как контекстный менеджер
    для предотвращения путаницы при использовании.
    """
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
