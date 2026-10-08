"""Database Connection and Transaction Management."""

import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional
from app.config import settings


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> Dict[str, Any]:
    """Converts a database row into a Python dictionary."""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager providing a SQLite database connection with:
    - Foreign key constraints enabled
    - WAL journal mode for concurrent reads/writes
    - Row dictionary factory enabled
    """
    conn = sqlite3.connect(
        settings.DATABASE_FILE,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        timeout=15.0
    )
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_one(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Helper to fetch a single record as a dictionary."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None


def fetch_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Helper to fetch all records as a list of dictionaries."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def execute_query(query: str, params: tuple = ()) -> int:
    """Helper to execute an INSERT, UPDATE, or DELETE and return affected rows."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.rowcount
