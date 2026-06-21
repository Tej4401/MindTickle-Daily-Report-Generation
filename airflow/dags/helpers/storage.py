"""S3 storage operations."""
from pathlib import Path
import os
from datetime import datetime, timezone as _tz
import re

import boto3

from .config import get_var, get_connection


def upload_file_to_s3(report_path: Path) -> str:
    """Upload report file to S3 and return the S3 key.

    The upload will place the file under a date prefix (folder) so the S3
    object key looks like: <prefix>/<YYYY-MM-DD>/<filename>.
    The date is extracted from the report filename (expects
    `lesson_completion_report_{start}_{end}.csv`). If no date is found, the
    current date is used.
    """
    # read from Airflow Variables `bucket` and `prefix` per request; fall
    # back to legacy env names `S3_REPORT_BUCKET` / `S3_REPORT_PREFIX`.
    bucket = None
    try:
        bucket = get_var("bucket", default=None, required=False)
    except Exception:
        bucket = None
    bucket = bucket or os.environ.get("S3_REPORT_BUCKET")

    prefix = None
    try:
        prefix = get_var("prefix", default=None, required=False)
    except Exception:
        prefix = None
    prefix = prefix or os.environ.get("S3_REPORT_PREFIX", "reports")

    # use timezone-aware UTC datetime to avoid deprecation warnings
    date_prefix = datetime.now(_tz.utc).strftime("%Y-%m-%d")

    s3_key = f"{prefix.rstrip('/')}/{date_prefix}/{report_path.name}"

    # Use AWS creds from Airflow connection `aws_default` when available.
    aws_conn = get_connection("aws_default")
    boto3_kwargs = {}
    aws_region = os.environ.get("AWS_REGION")
    if aws_region:
        boto3_kwargs["region_name"] = aws_region
    if aws_conn is not None:
        access_key = getattr(aws_conn, "login", None)
        secret_key = getattr(aws_conn, "password", None)
        if access_key and secret_key:
            boto3_kwargs.update({"aws_access_key_id": access_key, "aws_secret_access_key": secret_key})

    s3 = boto3.client("s3", **boto3_kwargs)
    s3.upload_file(str(report_path), bucket, s3_key)
    return s3_key
