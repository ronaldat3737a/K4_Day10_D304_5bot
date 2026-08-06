from __future__ import annotations

from typing import Any
from datetime import datetime
import pandas as pd

from core.config import Settings


def _to_native(val: Any) -> Any:
    """Chuyển đổi giá trị thành kiểu Python native để có thể serialize JSON."""
    if hasattr(val, 'item'):  # numpy types
        return val.item()
    if isinstance(val, (bool, int, float, str)) or val is None:
        return val
    # fallback
    return str(val)

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

    """Tạo bộ data quality checks."""
    checks = {}
    # 1. Check row count
    checks["row_count"] = len(df)
    # 2. Check paper_id not null and unique
    checks["paper_id_not_null"] = bool(df["paper_id"].notna().all())
    checks["paper_id_unique"] = bool(df["paper_id"].is_unique)
    # 3. Check title not null
    checks["title_not_null"] = bool(df["title"].notna().all())
    # 4. Check độ dài summary (ví dụ: ít nhất 10 ký tự)
    if "summary" in df.columns:
        checks["summary_min_length_10"] = bool((df["summary"].str.len() >= 10).all())
    else:
        checks["summary_min_length_10"] = False
    # 5. Check freshness bằng age_days (ví dụ: không âm và không quá lớn)
    if "age_days" in df.columns:
        checks["age_days_non_negative"] = bool((df["age_days"] >= 0).all())
        checks["age_days_reasonable"] = bool((df["age_days"] <= 365 * 10).all())  # within 10 years
    else:
        checks["age_days_non_negative"] = False
        checks["age_days_reasonable"] = False
    # Chuyển đổi tất cả giá trị thành native Python types
    return {k: _to_native(v) for k, v in checks.items()}



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
    
    """Tổng hợp freshness report."""
    # Đảm bảo có cột published
    if "published" not in df.columns:
        payload = {
            "latest_published": None,
            "oldest_published": None,
            "stale_rows": 0,
            "total_rows": len(df),
            "is_fresh": False,
            "error": "Missing 'published' column"
        }
    else:
        # Chuyển đổi sang datetime, bỏ lỗi
        df["published_dt"] = pd.to_datetime(df["published"], errors="coerce")
        # Loại bỏ NaT
        valid_dates = df["published_dt"].dropna()
        if valid_dates.empty:
            latest = oldest = None
            stale_rows = len(df)
        else:
            latest = valid_dates.max()
            oldest = valid_dates.min()
            # Xác định stale: older than freshness_threshold_days
            threshold = settings.freshness_threshold_days
            stale = valid_dates < (datetime.now() - pd.Timedelta(days=threshold))
            stale_rows = int(stale.sum())
        total_rows = len(df)
        is_fresh = stale_rows == 0
        payload = {
            "latest_published": latest.isoformat() if latest else None,
            "oldest_published": oldest.isoformat() if oldest else None,
            "stale_rows": stale_rows,
            "total_rows": total_rows,
            "is_fresh": is_fresh,
        }
    # Ghi JSON report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    import json
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return payload