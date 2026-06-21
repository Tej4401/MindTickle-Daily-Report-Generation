"""Email notification operations using AWS SES."""

import json
import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import boto3

from .config import get_connection, get_var


def _parse_json_or_csv_list(value: str) -> list[str]:
    try:
        return (
            list(json.loads(value))
            if value.strip().startswith("[")
            else [s.strip() for s in value.split(",")]
        )
    except Exception:
        return [s.strip() for s in value.split(",")]


def _build_boto3_kwargs(aws_region: str | None, aws_conn: object | None) -> dict:
    boto3_kwargs: dict = {"region_name": aws_region} if aws_region else {}
    if aws_conn is not None:
        access_key = getattr(aws_conn, "login", None)
        secret_key = getattr(aws_conn, "password", None)
        if access_key and secret_key:
            boto3_kwargs.update(
                {"aws_access_key_id": access_key, "aws_secret_access_key": secret_key}
            )
    return boto3_kwargs


def send_report_email(report_path: Path) -> None:
    """Send report file as email attachment via AWS SES."""
    aws_region = get_var(
        "aws_region", default=os.environ.get("AWS_REGION", "us-east-1"), required=False
    )

    # sender(s) and recipients are stored as Airflow Variables named
    # `senders` and `recipients` (comma-separated or JSON list). Fall back
    # to legacy env vars `SES_SENDER` / `SES_RECIPIENTS` if not set.
    senders_val = None
    try:
        senders_val = get_var("senders", default=None, required=False)
    except Exception:
        senders_val = None

    if senders_val:
        senders_list = _parse_json_or_csv_list(senders_val)
    else:
        sender_env = os.environ.get("SES_SENDER")
        senders_list = [sender_env] if sender_env else []

    if not senders_list or not senders_list[0]:
        raise ValueError(
            "Missing sender address: set Airflow Variable 'senders' or env SES_SENDER"
        )

    sender = senders_list[0]

    recipients_val = None
    try:
        recipients_val = get_var("recipients", default=None, required=False)
    except Exception:
        recipients_val = None

    if recipients_val:
        recipients = _parse_json_or_csv_list(recipients_val)
    else:
        recipients_env = os.environ.get("SES_RECIPIENTS")
        if not recipients_env:
            raise ValueError(
                (
                    "Missing required recipients: set Airflow Variable 'recipients' "
                    "or env SES_RECIPIENTS"
                )
            )
        recipients = [r.strip() for r in recipients_env.split(",") if r.strip()]

    subject = os.environ.get("SES_SUBJECT", "Lesson Completion Report")

    with report_path.open("rb") as attachment_file:
        attachment_data = attachment_file.read()

    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.attach(
        MIMEText(
            "Please find attached the lesson completion report.",
            "plain",
        )
    )

    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(attachment_data)
    encoders.encode_base64(attachment)
    attachment.add_header(
        "Content-Disposition",
        f"attachment; filename={report_path.name}",
    )
    message.attach(attachment)

    # Use AWS credentials from an Airflow connection (aws_default) when
    # available, otherwise rely on environment / IAM role.
    aws_conn = get_connection("aws_default")
    boto3_kwargs = _build_boto3_kwargs(aws_region, aws_conn)

    client = boto3.client("ses", **boto3_kwargs)
    client.send_raw_email(
        Source=sender,
        Destinations=recipients,
        RawMessage={"Data": message.as_string()},
    )
