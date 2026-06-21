import os
import sys
from pathlib import Path

# ensure dags/helpers is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "airflow" / "dags"))

from helpers import config  # noqa: E402


def test_get_var_reads_airflow_var_env():
    os.environ.pop("AIRFLOW_VAR_foo", None)
    os.environ["AIRFLOW_VAR_foo"] = "bar"
    assert config.get_var("foo") == "bar"


def test_get_var_reads_plain_env():
    os.environ.pop("AIRFLOW_VAR_baz", None)
    os.environ.pop("baz", None)
    os.environ["baz"] = "qux"
    assert config.get_var("baz") == "qux"


def test_get_connection_returns_env_conn():
    os.environ.pop("AIRFLOW_CONN_TESTCONN", None)
    os.environ["AIRFLOW_CONN_TESTCONN"] = "aws://ak:sk@?region_name=us-east-1"
    result = config.get_connection("testconn")
    # Accept either the raw env string or an Airflow Connection-like object.
    if isinstance(result, str):
        assert result == "aws://ak:sk@?region_name=us-east-1"
    else:
        # Connection objects in Airflow provide `get_uri()` or stringification.
        uri = None
        try:
            uri = result.get_uri()
        except Exception:
            try:
                uri = str(result)
            except Exception:
                uri = None
        assert uri is not None and "aws://ak:sk@" in uri
