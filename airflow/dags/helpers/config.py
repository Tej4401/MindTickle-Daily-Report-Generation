"""Configuration helpers for Airflow Variables / Connections with env fallbacks."""
from __future__ import annotations

import json
import os
from typing import Any, Optional, Tuple


def _try_airflow_imports() -> Tuple[Optional[object], Optional[object]]:
    try:
        from airflow.models import Variable  # type: ignore
        from airflow.hooks.base import BaseHook  # type: ignore

        return Variable, BaseHook
    except Exception:
        return None, None


def get_var(name: str, default: Optional[str] = None, required: bool = True) -> str:
    """Get a setting first from Airflow Variable, then fall back to env.

    Variable names expected exactly as provided (e.g. 'bucket', 'prefix',
    'senders', 'recipients'). When running outside Airflow the function
    falls back to environment variables (checks `AIRFLOW_VAR_<NAME>` then
    `<NAME>`).
    """
    Variable, _ = _try_airflow_imports()
    value: Optional[str] = None
    if Variable is not None:
        try:
            value = Variable.get(name, default_var=None)
        except Exception:
            value = None

    if value is None:
        # env fallback: AIRFLOW_VAR_<name> then plain <NAME>
        value = os.environ.get(f"AIRFLOW_VAR_{name}") or os.environ.get(name) or default

    if value is None and required:
        raise ValueError(f"Missing required configuration variable: {name}")
    return value  # type: ignore


def get_connection(conn_id: str):
    """Return an Airflow Connection-like object or None.

    When Airflow is available this returns the real Connection instance from
    `BaseHook.get_connection`. Otherwise it attempts to read `AIRFLOW_CONN_<ID>`
    from the environment and returns it as a simple string.
    """
    _, BaseHook = _try_airflow_imports()
    if BaseHook is not None:
        try:
            return BaseHook.get_connection(conn_id)
        except Exception:
            return None

    # fallback: return raw connection URI from env if present
    env_key = f"AIRFLOW_CONN_{conn_id.upper()}"
    return os.environ.get(env_key)


def build_db_connections() -> tuple[dict, dict]:
    """Build PostgreSQL and MySQL connection configurations."""
    postgres_config = {
        "host": os.environ.get("MT_POSTGRES_HOST"),
        "port": int(os.environ.get("MT_POSTGRES_PORT", "5432")),
        "dbname": os.environ.get("POSTGRES_DB"),
        "user": os.environ.get("POSTGRES_USER"),
        "password": os.environ.get("POSTGRES_PASSWORD"),
    }
    mysql_config = {
        "host": os.environ.get("MT_MYSQL_HOST"),
        "port": int(os.environ.get("MT_MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_ROOT_PASSWORD"),
        "database": os.environ.get("MYSQL_DATABASE"),
    }
    return postgres_config, mysql_config

