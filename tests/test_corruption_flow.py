import json

import pandas as pd

from pipelines import corruption_flow


def test_corruption_flow_requires_baseline_artifacts(tmp_path):
    settings = type("SettingsStub", (), {"paths": type("Paths", (), {
        "clean_csv": tmp_path / "missing.csv",
        "baseline_metrics": tmp_path / "baseline.json",
        "eval_testset": tmp_path / "test_set.json",
        "raw_records_json": tmp_path / "raw.json",
        "embeddings_json": tmp_path / "embeddings.json",
    })()})()

    try:
        corruption_flow.run_flow(settings)
    except FileNotFoundError as exc:
        assert "baseline" in str(exc).lower()
    else:
        raise AssertionError("expected a missing baseline artifact error")
