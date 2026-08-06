from __future__ import annotations

from typing import Any

from core.utils import write_text


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
    lines = ["# Phase 1 Baseline Report", "", "## Source", f"- {source_summary}", "", "## Metrics", f"```json\n{metrics}\n```", "", "## Quality", f"```json\n{quality}\n```", "", "## Freshness", f"```json\n{freshness}\n```"]
    write_text(report_path, "\n".join(lines) + "\n")


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
    keys = ["retrieval_hit_rate", "mean_token_f1", "judge_accuracy", "mean_judge_score"]
    lines = ["# Corruption and Repair Report", "", "| Metric | Baseline | Corrupted | Repaired |", "|---|---:|---:|---:|"]
    for key in keys:
        lines.append(f"| `{key}` | {baseline_metrics.get(key, 'N/A')} | {corrupted_metrics.get(key, 'N/A')} | {repaired_metrics.get(key, 'N/A')} |")
    lines.extend([
        "", "## Observability", "", f"- Baseline: quality assumed from baseline metrics; corrupted quality passed: `{corrupted_quality.get('passed')}`; repaired quality passed: `{repaired_quality.get('passed')}`.",
        f"- Corrupted freshness: `{corrupted_freshness.get('is_fresh')}`; repaired freshness: `{repaired_freshness.get('is_fresh')}`.",
        "", "## Interpretation", "", "The same evaluation set is used for all three states. Interpret metric changes together with the quality and freshness signals.",
    ])
    write_text(report_path, "\n".join(lines) + "\n")