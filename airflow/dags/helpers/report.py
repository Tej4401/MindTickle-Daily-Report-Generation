"""Report file handling."""

from pathlib import Path

import polars as pl


def write_csv(report_frame: pl.DataFrame, report_path: Path) -> None:
    """Write Polars DataFrame to CSV file."""
    report_frame.write_csv(report_path)
