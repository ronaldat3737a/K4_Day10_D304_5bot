from __future__ import annotations

from typing import Any
import json
from datetime import datetime

def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """TODO(student): viet markdown report cho baseline phase.

    Pseudo-code:
    1. Gom source summary.
    2. In metrics retrieval/evaluation.
    3. In data quality va freshness.
    4. Ghi markdown vao report_path.
    """

    """Viet markdown report cho baseline phase."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Baseline Phase 1 Report\n\n")
        f.write(f"**Timestamp**: {datetime.now().isoformat()}\n\n")
        
        # 1. Gom source summary
        f.write("## Source Summary\n\n")
        for key, value in source_summary.items():
            f.write(f"- **{key}**: {value}\n")
        f.write("\n")
        
        # 2. In metrics retrieval/evaluation
        f.write("## Retrieval and Evaluation Metrics\n\n")
        for key, value in metrics.items():
            if key != "ragas":  # Xử lý riêng cho ragas
                if isinstance(value, float):
                    f.write(f"- **{key}**: {value:.4f}\n")
                else:
                    f.write(f"- **{key}**: {value}\n")
        
        # Xử lý riêng cho RAGAS nếu có
        if "ragas" in metrics and isinstance(metrics["ragas"], dict):
            ragas_info = metrics["ragas"]
            if ragas_info.get("skipped"):
                f.write(f"- **RAGAS**: {ragas_info['skipped']}\n")
            elif "error" in ragas_info:
                f.write(f"- **RAGAS Error**: {ragas_info['error']}\n")
            else:
                f.write("### RAGAS Metrics\n\n")
                for key, value in ragas_info.items():
                    if isinstance(value, float):
                        f.write(f"- **{key}**: {value:.4f}\n")
                    else:
                        f.write(f"- **{key}**: {value}\n")
        f.write("\n")
        
        # 3. In data quality va freshness
        f.write("## Data Quality Checks\n\n")
        for check, result in quality.items():
            f.write(f"- **{check}**: {result}\n")
        f.write("\n")
        
        f.write("## Freshness Report\n\n")
        for key, value in freshness.items():
            if key in ["latest_published", "oldest_published"] and value:
                f.write(f"- **{key}**: {value}\n")
            else:
                f.write(f"- **{key}**: {value}\n")
        f.write("\n")


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    """TODO(student): viet markdown report so sanh baseline/corrupted/repaired."""
    """Viet markdown report so sanh baseline/corrupted/repaired."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Corruption Comparison Report\n\n")
        f.write(f"**Timestamp**: {datetime.now().isoformat()}\n\n")
        
        # So sánh metrics
        f.write("## Metrics Comparison\n\n")
        f.write("| Metric | Baseline | Corrupted | Repaired |\n")
        f.write("|--------|----------|-----------|----------|\n")
        
        # Lấy tất cả các khóa metrics từ baseline (loại bỏ ragas đặc biệt)
        all_metric_keys = set()
        for m in [baseline_metrics, corrupted_metrics, repaired_metrics]:
            all_metric_keys.update(k for k in m.keys() if k != "ragas")
        
        for key in sorted(all_metric_keys):
            base_val = baseline_metrics.get(key, "N/A")
            corr_val = corrupted_metrics.get(key, "N/A")
            rep_val = repaired_metrics.get(key, "N/A")
            
            # Định dạng giá trị float
            def format_val(val):
                if isinstance(val, float):
                    return f"{val:.4f}"
                return str(val)
            
            f.write(f"| {key} | {format_val(base_val)} | {format_val(corr_val)} | {format_val(rep_val)} |\n")
        
        # So sánh RAGAS nếu có
        has_ragas = any("ragas" in m and isinstance(m["ragas"], dict) and not m["ragas"].get("skipped") 
                       for m in [baseline_metrics, corrupted_metrics, repaired_metrics])
        if has_ragas:
            f.write("\n### RAGAS Metrics Comparison\n\n")
            f.write("| Metric | Baseline | Corrupted | Repaired |\n")
            f.write("|--------|----------|-----------|----------|\n")
            
            # Lấy các khóa RAGAS
            ragas_keys = set()
            for m in [baseline_metrics, corrupted_metrics, repaired_metrics]:
                if "ragas" in m and isinstance(m["ragas"], dict):
                    ragas_keys.update(k for k in m["ragas"].keys() if k not in ["skipped", "error"])
            
            for key in sorted(ragas_keys):
                base_val = baseline_metrics.get("ragas", {}).get(key, "N/A")
                corr_val = corrupted_metrics.get("ragas", {}).get(key, "N/A")
                rep_val = repaired_metrics.get("ragas", {}).get(key, "N/A")
                
                def format_val(val):
                    if isinstance(val, float):
                        return f"{val:.4f}"
                    return str(val)
                
                f.write(f"| {key} | {format_val(base_val)} | {format_val(corr_val)} | {format_val(rep_val)} |\n")
        f.write("\n")
        
        # So sánh data quality
        f.write("## Data Quality Comparison\n\n")
        f.write("| Check | Baseline | Corrupted | Repaired |\n")
        f.write("|-------|----------|-----------|----------|\n")
        
        all_quality_keys = set()
        for q in [corrupted_quality, repaired_quality]:
            all_quality_keys.update(q.keys())
        # Thêm baseline quality nếu có (trong trường hợp này chúng ta không có trực tiếp, nhưng có thể tính từ source)
        # Đối báo cáo này, chúng ta chỉ có corrupted và repaired quality
        
        for key in sorted(all_quality_keys):
            corr_val = corrupted_quality.get(key, "N/A")
            rep_val = repaired_quality.get(key, "N/A")
            f.write(f"| {key} | N/A | {corr_val} | {rep_val} |\n")
        f.write("\n")
        
        # So sánh freshness
        f.write("## Freshness Comparison\n\n")
        f.write("| Metric | Baseline | Corrupted | Repaired |\n")
        f.write("|--------|----------|-----------|----------|\n")
        
        all_freshness_keys = set()
        for fr in [corrupted_freshness, repaired_freshness]:
            all_freshness_keys.update(fr.keys())
        
        for key in sorted(all_freshness_keys):
            corr_val = corrupted_freshness.get(key, "N/A")
            rep_val = repaired_freshness.get(key, "N/A")
            # Baseline freshness không được truyền vào hàm này, nên để trống hoặc N/A
            f.write(f"| {key} | N/A | {corr_val} | {rep_val} |\n")
        f.write("\n")