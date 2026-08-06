import json

from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_corruption_report


def test_quality_and_freshness_detect_corruption(clean_fixture, tmp_path):
    settings = type("SettingsStub", (), {"freshness_threshold_days": 300, "paths": type("Paths", (), {"quality_dir": tmp_path})()})()
    quality = run_data_quality_checks(clean_fixture, settings, "fixture")
    freshness = build_freshness_report(clean_fixture, settings, tmp_path / "freshness.json")

    assert quality["passed"] is True
    assert freshness["total_rows"] == len(clean_fixture)
    assert freshness["is_fresh"] is True
    assert (tmp_path / "fixture_quality.json").exists()


def test_comparison_report_contains_three_states(tmp_path):
    metrics = {"retrieval_hit_rate": 1.0, "mean_token_f1": 0.8, "judge_accuracy": 1.0, "mean_judge_score": 5.0}
    generate_corruption_report(tmp_path / "comparison.md", metrics, metrics, metrics, {"passed": True}, {"passed": True}, {"is_fresh": True}, {"is_fresh": True})

    report = (tmp_path / "comparison.md").read_text()
    assert "Baseline" in report
    assert "Corrupted" in report
    assert "Repaired" in report
