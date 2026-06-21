from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow.decorators import task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.utils.dates import days_ago
from helpers import (
    assemble_report_frame,
    build_db_connections,
    send_report_email,
    upload_file_to_s3,
    write_csv,
)

from airflow import DAG  # type: ignore[attr-defined]

DEFAULT_ARGS = {
    "owner": "assignment",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@task
def build_report() -> str:
    context = get_current_context()
    params = context["params"]

    if params.get("start_date") and params.get("end_date"):
        start_date = datetime.strptime(
            params["start_date"],
            "%Y-%m-%d",
        ).date()
        end_date = datetime.strptime(
            params["end_date"],
            "%Y-%m-%d",
        ).date()
    else:
        # For a daily DAG, process yesterday's data
        start_date = context["data_interval_start"].date()
        end_date = start_date

    if start_date > end_date:
        raise ValueError("start_date must be less than or equal to end_date")

    postgres_config, mysql_config = build_db_connections()

    report_frame = assemble_report_frame(
        postgres_config=postgres_config,
        mysql_config=mysql_config,
        start_date=start_date,
        end_date=end_date,
    )

    output_dir = Path("/opt/airflow/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / (f"lesson_completion_report_{start_date}_{end_date}.csv")
    write_csv(report_frame, report_path)

    return str(report_path)


@task
def upload_to_s3(report_path: str) -> str:
    return upload_file_to_s3(Path(report_path))


@task
def send_notifications(report_path: str) -> None:
    send_report_email(Path(report_path))


with DAG(
    dag_id="mindtickle_daily_report",
    default_args=DEFAULT_ARGS,
    description=(
        "Build lesson completion reports using data from PostgreSQL and MySQL, "
        "upload to S3, and send via SES."
    ),
    schedule="@daily",
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
    params={
        "start_date": Param(
            default=None,
            type=["null", "string"],
            format="date",
            description="Optional start date (YYYY-MM-DD)",
        ),
        "end_date": Param(
            default=None,
            type=["null", "string"],
            format="date",
            description="Optional end date (YYYY-MM-DD)",
        ),
    },
    tags=["assignment", "aws", "database", "polars"],
) as dag:
    report_file = build_report()
    upload_task = upload_to_s3(report_file)
    email_task = send_notifications(report_file)

    report_file >> [upload_task, email_task]
