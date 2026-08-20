"""Oracle connection handling.

A single place responsible for opening/closing connections so that no
other module needs to know about ``oracledb`` directly. Connections are
short-lived (opened per query, closed immediately after) since Streamlit
reruns the whole script on every interaction — a connection pool would be
the next step if query volume grows, but is not needed at this scale.
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

from src.config.settings import OracleSettings

logger = logging.getLogger(__name__)


class OracleConnectionError(RuntimeError):
    """Raised when Oracle cannot be reached or the driver is missing."""


@contextmanager
def oracle_connection(settings: OracleSettings) -> Iterator["oracledb.Connection"]:  # noqa: F821
    """Open an Oracle connection for the duration of the ``with`` block.

    Raises:
        OracleConnectionError: if the ``oracledb`` driver is not installed,
            or if the connection attempt fails for any reason.
    """
    try:
        import oracledb
    except ImportError as exc:
        raise OracleConnectionError(
            "oracledb package not installed. Run: pip install oracledb"
        ) from exc

    if not settings.is_configured:
        raise OracleConnectionError("Oracle credentials are not fully configured.")

    conn = None
    try:
        conn = oracledb.connect(
            user=settings.user,
            password=settings.password,
            dsn=settings.dsn,
        )
        yield conn
    except OracleConnectionError:
        raise
    except Exception as exc:  # noqa: BLE001 - surface any driver error uniformly
        logger.exception("Oracle connection/query failed")
        raise OracleConnectionError(str(exc)) from exc
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:  # noqa: BLE001 - never fail on cleanup
                logger.warning("Failed to cleanly close Oracle connection", exc_info=True)
