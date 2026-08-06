import json

from ingestion.corruption import corrupt_clean_dataframe


def test_corruption_does_not_mutate_input_and_records_changes(clean_fixture, tmp_path):
    original = clean_fixture.copy(deep=True)
    log_path = tmp_path / "corruption_log.json"

    corrupted = corrupt_clean_dataframe(clean_fixture, log_path)

    assert clean_fixture.equals(original)
    assert len(corrupted) != 0
    assert len(corrupted) != len(original) or not corrupted.equals(original)
    payload = json.loads(log_path.read_text())
    assert payload["seed"] == 42
    assert payload["input_rows"] == len(original)
    assert payload["output_rows"] == len(corrupted)
    assert payload["changes"]


def test_corruption_is_deterministic(clean_fixture, tmp_path):
    first = corrupt_clean_dataframe(clean_fixture, tmp_path / "first.json")
    second = corrupt_clean_dataframe(clean_fixture, tmp_path / "second.json")

    assert first.equals(second)
