import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "airflow" / "dags"))
from helpers import storage  # noqa: E402


class DummyS3:
    def __init__(self):
        self.uploaded = None

    def upload_file(self, filename, bucket, key):
        self.uploaded = (filename, bucket, key)


def test_upload_file_to_s3_uses_env_and_calls_boto3(monkeypatch, tmp_path):
    p = tmp_path / "report.csv"
    p.write_text("a,b,c")

    os.environ["S3_REPORT_BUCKET"] = "mybucket"
    os.environ["S3_REPORT_PREFIX"] = "myprefix"
    os.environ.pop("AIRFLOW_VAR_bucket", None)
    os.environ.pop("AIRFLOW_VAR_prefix", None)

    dummy = DummyS3()

    # ensure get_connection fallback to None
    monkeypatch.setattr(storage, "get_connection", lambda conn_id: None)
    monkeypatch.setattr(storage.boto3, "client", lambda *args, **kwargs: dummy)

    key = storage.upload_file_to_s3(p)

    assert dummy.uploaded is not None
    filename, bucket, s3key = dummy.uploaded
    assert filename == str(p)
    assert bucket == "mybucket"
    assert s3key.endswith("/report.csv")
    assert "myprefix" in s3key
    assert key == s3key
