"""Database operations for querying lesson completion data."""

import mysql.connector
import polars as pl
import psycopg2

REPORT_SCHEMA: dict[str, list] = {
    "Name": [],
    "Number of lessons completed": [],
    "Date": [],
}


def _empty_report_frame() -> pl.DataFrame:
    """Return an empty DataFrame with the report's expected schema."""
    return pl.DataFrame(REPORT_SCHEMA)


def _to_date_str(value) -> str:
    """Normalize a date or date-like string to an ISO 'YYYY-MM-DD' string."""
    return value if isinstance(value, str) else value.isoformat()


def fetch_active_users(postgres_config: dict) -> pl.DataFrame:
    """Query PostgreSQL for active users.

    Returns a DataFrame with columns ["user_id", "user_name"]. Empty if
    no active users are found.
    """
    with psycopg2.connect(**postgres_config) as pg_conn:
        with pg_conn.cursor() as cursor:
            cursor.execute("""
                SELECT user_id, user_name
                FROM mindtickle_users
                WHERE LOWER(active_status) = 'active'
                """)
            active_users_rows = cursor.fetchall()

    if not active_users_rows:
        return pl.DataFrame(schema=["user_id", "user_name"])

    return pl.DataFrame(
        active_users_rows,
        schema=["user_id", "user_name"],
        orient="row",
    )


def fetch_lesson_completions(
    mysql_config: dict,
    user_ids: list,
    start_date,
    end_date,
) -> pl.DataFrame:
    """Query MySQL for lesson completions by the given users within a date range.

    Returns a DataFrame with columns
    ["completion_id", "user_id", "lesson_id", "completion_date"].
    Empty if there are no matching rows or no user_ids are provided.
    """
    if not user_ids:
        return pl.DataFrame(
            schema=["completion_id", "user_id", "lesson_id", "completion_date"]
        )

    placeholders = ",".join(["%s"] * len(user_ids))
    query = f"""
        SELECT completion_id, user_id, lesson_id, completion_date
        FROM lesson_completion
        WHERE completion_date BETWEEN %s AND %s
        AND user_id IN ({placeholders})
    """
    params = [_to_date_str(start_date), _to_date_str(end_date), *user_ids]

    with mysql.connector.connect(**mysql_config) as mysql_conn:
        with mysql_conn.cursor() as cursor:
            cursor.execute(query, params)
            lesson_rows = cursor.fetchall()

    if not lesson_rows:
        return pl.DataFrame(
            schema=["completion_id", "user_id", "lesson_id", "completion_date"]
        )

    return pl.DataFrame(
        lesson_rows,
        schema=["completion_id", "user_id", "lesson_id", "completion_date"],
        orient="row",
    )


def deduplicate_completions(lessons_df: pl.DataFrame) -> pl.DataFrame:
    """Remove duplicate completion records, keeping the latest completion_id
    for each (user_id, lesson_id, completion_date) combination.
    """
    return lessons_df.sort("completion_id").unique(
        subset=["user_id", "lesson_id", "completion_date"],
        keep="last",
    )


def aggregate_completions_by_user_and_date(
    lessons_df: pl.DataFrame,
    user_df: pl.DataFrame,
) -> pl.DataFrame:
    """Join completions with user names and count completions per user per day.

    Returns a DataFrame with columns
    ["Name", "Number of lessons completed", "Date"].
    """
    return (
        lessons_df.join(user_df, on="user_id", how="inner")
        .group_by(["user_name", "completion_date"])
        .agg(pl.len().alias("Number of lessons completed"))
        .sort(["completion_date", "user_name"])
        .with_columns(
            pl.col("completion_date")
            .cast(pl.Date)
            .dt.strftime("%Y-%m-%d")
            .alias("Date")
        )
        .select(
            [
                pl.col("user_name").alias("Name"),
                "Number of lessons completed",
                "Date",
            ]
        )
    )


def assemble_report_frame(
    postgres_config: dict,
    mysql_config: dict,
    start_date,
    end_date,
) -> pl.DataFrame:
    """Query active users and lesson completions, return aggregated report DataFrame."""
    user_df = fetch_active_users(postgres_config)
    if user_df.is_empty():
        return _empty_report_frame()

    user_ids = user_df["user_id"].to_list()

    lessons_df = fetch_lesson_completions(mysql_config, user_ids, start_date, end_date)
    if lessons_df.is_empty():
        return _empty_report_frame()

    deduped_df = deduplicate_completions(lessons_df)

    return aggregate_completions_by_user_and_date(deduped_df, user_df)
