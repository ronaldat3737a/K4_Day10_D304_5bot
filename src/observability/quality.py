from __future__ import annotations

from typing import Any

import pandas as pd

from core.config import Settings
from core.utils import write_json


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """TODO(student): tao bo data quality checks.

    Pseudo-code:
    1. Check row count.
    2. Check `paper_id` not null va unique.
    3. Check `title` not null.
    4. Check do dai `summary`.
    5. Check freshness bang `age_days`.
    6. Ghi ket qua vao `data/quality/`.
    """
    checks = {
        "row_count_positive": {"passed": len(df) > 0, "value": len(df)},
        "paper_id_not_null": {"passed": bool(df["paper_id"].notna().all()) if "paper_id" in df else False},
        "paper_id_unique": {"passed": bool(df["paper_id"].is_unique) if "paper_id" in df else False},
        "title_not_null": {"passed": bool(df["title"].fillna("").str.strip().ne("").all()) if "title" in df else False},
        "summary_minimum_length": {"passed": bool(df["summary"].fillna("").str.len().ge(20).all()) if "summary" in df else False},
        "age_days_non_negative": {"passed": bool(df["age_days"].ge(0).all()) if "age_days" in df else False},
    }
    result = {"report_name": report_name, "total_rows": len(df), "passed": all(item["passed"] for item in checks.values()), "checks": checks}
    write_json(settings.paths.quality_dir / f"{report_name}_quality.json", result)
    return result


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    """TODO(student): tong hop freshness report.

    Pseudo-code:
    1. Tim latest va oldest published date.
    2. Dem so dong stale.
    3. Tao payload:
       - latest_published
       - oldest_published
       - stale_rows
       - total_rows
       - is_fresh
    4. Ghi JSON report.
    """
    if df.empty or "published" not in df:
        payload = {"latest_published": None, "oldest_published": None, "stale_rows": 0, "total_rows": len(df), "is_fresh": False}
    else:
        dates = pd.to_datetime(df["published"], errors="coerce", utc=True).dropna()
        stale_rows = int(df["age_days"].gt(settings.freshness_threshold_days).sum()) if "age_days" in df else len(df)
        payload = {
            "latest_published": dates.max().date().isoformat() if not dates.empty else None,
            "oldest_published": dates.min().date().isoformat() if not dates.empty else None,
            "stale_rows": stale_rows,
            "total_rows": len(df),
            "is_fresh": bool(not dates.empty and stale_rows == 0),
        }
    write_json(report_path, payload)
    return payload