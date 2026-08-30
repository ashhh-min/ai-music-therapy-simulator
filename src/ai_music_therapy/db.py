"""Database connection management for multi-user deployment.

Replaces the fresh per-operation connections used through S17 (fine for a
local single-user demo) with a pooled engine suitable for concurrent
multi-user deployment (Streamlit Community Cloud + Neon). Layers, in the
order the S18 hardening task prescribed:

1. ``ConnectionFactory`` - builds configured psycopg connections
   (row factory + connect timeout) so connection settings live in one place.
2. ``PooledConnectionManager`` - lazy, thread-safe wrapper around
   ``psycopg_pool.ConnectionPool`` with bounded checkout timeout and
   connection recycling (``max_lifetime``).
3. ``transaction`` - pooled connection plus an explicit BEGIN/COMMIT/ROLLBACK
   block; the connection returns to the pool afterwards.
4. ``run`` - retry + timeout handling: bounded attempts with exponential
   backoff on transient connection errors (``OperationalError``), while
   integrity errors (e.g. duplicate ids) propagate immediately.

The pool is opened lazily on first use, so constructing a ``Repository``
never requires a reachable database (importing Streamlit pages stays safe).
"""

from __future__ import annotations

import atexit
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any, TypeVar

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

T = TypeVar("T")

#: Transient connection-level failures worth retrying with a fresh checkout.
RETRYABLE_ERRORS: tuple[type[Exception], ...] = (psycopg.OperationalError,)


class ConnectionFactory:
    """Creates configured psycopg connections for one database URL."""

    def __init__(self, database_url: str, connect_timeout: int = 5):
        self.database_url = database_url
        self.connect_timeout = connect_timeout
        self.connections_opened = 0

    def connect(self) -> psycopg.Connection:
        self.connections_opened += 1
        return psycopg.connect(
            self.database_url,
            row_factory=dict_row,
            connect_timeout=self.connect_timeout,
        )


class PooledConnectionManager:
    """Bounded connection pool with transaction wrapper and retry handling.

    Parameters sized for a small multi-user deployment: a handful of Streamlit
    sessions sharing a Neon database. All time parameters are in seconds.
    """

    def __init__(
        self,
        database_url: str,
        min_size: int = 1,
        max_size: int = 8,
        checkout_timeout: float = 10.0,
        max_lifetime: float = 1800.0,
        connect_timeout: int = 5,
        max_attempts: int = 3,
        retry_backoff: float = 0.2,
        factory: ConnectionFactory | None = None,
        name: str = "mt-pool",
    ):
        self._factory = factory or ConnectionFactory(database_url, connect_timeout)
        self._min_size = min_size
        self._max_size = max_size
        self._checkout_timeout = checkout_timeout
        self._max_lifetime = max_lifetime
        self._max_attempts = max_attempts
        self._retry_backoff = retry_backoff
        self._name = name
        self._pool: ConnectionPool | None = None
        self._lock = threading.Lock()

    @property
    def pool(self) -> ConnectionPool:
        """The lazily opened pool (thread-safe first open)."""
        if self._pool is None:
            with self._lock:
                if self._pool is None:
                    factory = self._factory

                    class _PooledConnection(psycopg.Connection):
                        """Connection class routed through the factory (counted)."""

                        @classmethod
                        def connect(cls, conninfo, **kwargs):
                            return factory.connect()

                    self._pool = ConnectionPool(
                        conninfo=factory.database_url,
                        connection_class=_PooledConnection,
                        kwargs={"connect_timeout": factory.connect_timeout},
                        min_size=self._min_size,
                        max_size=self._max_size,
                        timeout=self._checkout_timeout,
                        max_lifetime=self._max_lifetime,
                        name=self._name,
                        open=True,
                    )
        return self._pool

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection]:
        """Check out a pooled connection; commit/rollback and return it after."""
        with self.pool.connection() as conn:
            yield conn

    @contextmanager
    def transaction(self) -> Iterator[psycopg.Connection]:
        """Check out a pooled connection inside an explicit transaction."""
        with self.pool.connection() as conn:
            with conn.transaction():
                yield conn

    def run(self, operation: Callable[[psycopg.Connection], T]) -> T:
        """Run ``operation(conn)`` in a transaction, retrying transient failures.

        Each attempt checks out a connection, opens a transaction, runs the
        operation, and commits. ``OperationalError`` (connection lost, pool
        timeout while reconnecting, server restart) is retried up to
        ``max_attempts`` times with exponential backoff; any other error -
        including integrity violations - propagates immediately so callers
        keep their exact semantics.
        """
        last_error: Exception | None = None
        for attempt in range(self._max_attempts):
            try:
                with self.transaction() as conn:
                    return operation(conn)
            except RETRYABLE_ERRORS as error:
                last_error = error
                if attempt < self._max_attempts - 1:
                    time.sleep(self._retry_backoff * (2**attempt))
        assert last_error is not None  # only reachable when attempts > 0
        raise last_error

    def stats(self) -> dict[str, Any]:
        """Pool statistics (useful in deployment checks)."""
        return dict(self.pool.get_stats())

    def close(self) -> None:
        """Close the pool; a later use opens a fresh one (used by tests)."""
        with self._lock:
            if self._pool is not None:
                self._pool.close()
                self._pool = None


# Process-wide manager registry: one pool per database URL for the whole
# process. Streamlit reruns page scripts on every interaction, so a
# Repository-per-rerun must not open its own pool each time - all pages,
# reruns, and threads share the cached manager below.
_MANAGERS: dict[str, PooledConnectionManager] = {}
_MANAGERS_LOCK = threading.Lock()


def get_manager(database_url: str) -> PooledConnectionManager:
    """Return the process-wide pooled manager for ``database_url`` (cached)."""
    with _MANAGERS_LOCK:
        if database_url not in _MANAGERS:
            _MANAGERS[database_url] = PooledConnectionManager(database_url)
        return _MANAGERS[database_url]


@atexit.register
def _close_cached_managers() -> None:
    """Close cached pools at interpreter exit so worker threads stop cleanly."""
    with _MANAGERS_LOCK:
        managers = list(_MANAGERS.values())
        _MANAGERS.clear()
    for manager in managers:
        try:
            manager.close()
        except Exception:  # noqa: BLE001 - best-effort shutdown hook
            pass
