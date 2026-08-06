from core.config import load_settings


def test_corrupted_and_repaired_paths_are_distinct_from_baseline():
    paths = load_settings().paths

    assert paths.corrupted_clean_csv != paths.clean_csv
    assert paths.repaired_clean_csv != paths.clean_csv
    assert paths.corrupted_embeddings_json != paths.embeddings_json
    assert paths.repaired_embeddings_json != paths.embeddings_json
