import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "airflow" / "dags"))
from helpers import notifications


class DummySES:
    def __init__(self):
        self.sent = None

    def send_raw_email(self, Source, Destinations, RawMessage):
        self.sent = {"Source": Source, "Destinations": Destinations, "RawMessage": RawMessage}


def test_send_report_email_calls_boto3(monkeypatch, tmp_path):
    # Prepare env fallbacks
    os.environ["SES_SENDER"] = "sender@example.com"
    os.environ["SES_RECIPIENTS"] = "a@example.com,b@example.com"
    os.environ.pop("AIRFLOW_VAR_senders", None)
    os.environ.pop("AIRFLOW_VAR_recipients", None)

    report = tmp_path / "r.csv"
    report.write_text("x")

    dummy = DummySES()
    monkeypatch.setattr(notifications, "get_connection", lambda conn_id: None)
    monkeypatch.setattr(notifications.boto3, "client", lambda *args, **kwargs: dummy)

    notifications.send_report_email(report)

    assert dummy.sent is not None
    assert dummy.sent["Source"] == "sender@example.com"
    assert set(dummy.sent["Destinations"]) == {"a@example.com", "b@example.com"}
