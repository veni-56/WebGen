"""
SQLite connection pool with WAL mode, foreign keys, and busy timeout.

Provides thread-local connection reuse backed by a semaphore-based pool
(max 10 concurrent connections).  Each connection is configured with:
  - row_factory = sqlite3.Row
  - PRAGMA journal_mode = WAL
  - PRAGMA foreign_keys = ON
  - PRAGMA busy_timeout = 5000
"""

from __future__ import annotations

import os
import sqlite3
import threading
from contextlib import contextmanager
from typing import Generator

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DB_PATH: str = os.environ.get("DB_PATH", "./projects.db")

_MAX_CONNECTIONS = 10

# Semaphore limits the total number of open connections across all threads.
_pool_semaphore: threading.Semaphore = threading.Semaphore(_MAX_CONNECTIONS)

# Thread-local storage holds one connection per thread.
_local: threading.local = threading.local()

# Lock protecting pool-level state changes (e.g. init_pool).
_pool_lock: threading.Lock = threading.Lock()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _open_connection(db_path: str) -> sqlite3.Connection:
    """Open and configure a new SQLite connection."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def _get_db_path() -> str:
    return _local.__dict__.get("_db_path", DB_PATH)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def init_pool(db_path: str) -> None:
    """
    Configure the pool to use *db_path* for all subsequent connections.

    Call this once at application startup before any call to get_conn().
    Existing thread-local connections are NOT closed; they will be replaced
    the next time a thread calls get_conn() after its current connection is
    released.
    """
    global DB_PATH
    with _pool_lock:
        DB_PATH = db_path
    # Propagate to the current thread immediately.
    _local._db_path = db_path


def get_conn() -> sqlite3.Connection:
    """
    Return the thread-local SQLite connection, creating one if necessary.

    Acquires a slot from the semaphore on first acquisition for this thread.
    The semaphore slot is held until release_conn() is called.
    """
    conn: sqlite3.Connection | None = getattr(_local, "conn", None)
    if conn is not None:
        # Already holding a connection on this thread — reuse it.
        return conn

    # Acquire a pool slot (blocks if all 10 are in use).
    _pool_semaphore.acquire()
    try:
        db_path = _get_db_path()
        conn = _open_connection(db_path)
        _local.conn = conn
        _local._semaphore_held = True
    except Exception:
        _pool_semaphore.release()
        raise
    return conn


def release_conn(conn: sqlite3.Connection) -> None:  # noqa: ARG001
    """
    Release the thread-local connection back to the pool.

    The connection is closed and the semaphore slot is freed so another
    thread can acquire it.  Passing a connection that does not belong to
    the current thread is a no-op (safe to call from finally blocks).
    """
    local_conn: sqlite3.Connection | None = getattr(_local, "conn", None)
    if local_conn is None:
        return

    try:
        local_conn.close()
    finally:
        _local.conn = None
        if getattr(_local, "_semaphore_held", False):
            _local._semaphore_held = False
            _pool_semaphore.release()


@contextmanager
def transaction(conn: sqlite3.Connection) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager that wraps work in an explicit transaction.

    Commits on clean exit; rolls back on any exception and re-raises.

    Usage::

        with transaction(conn) as c:
            c.execute("INSERT INTO ...")
    """
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
