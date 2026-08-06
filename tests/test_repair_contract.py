from datetime import UTC, datetime

from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import PaperRecord


def test_repair_rebuilds_clean_schema_from_raw_records():
    records = [
        PaperRecord(
            paper_id="10.1234/repaired",
            title="  A repaired title  ",
            summary="A repaired summary with enough content for the clean dataset.",
            authors=["Ada Lovelace"],
            categories=["AI"],
            primary_category="AI",
            published="2026-07-01",
            updated="2026-07-02",
            abs_url="https://doi.org/10.1234/repaired",
            pdf_url="",
            comment="",
        )
    ]

    repaired = build_clean_dataframe(records, datetime(2026, 8, 6, tzinfo=UTC))

    assert list(repaired["paper_id"]) == ["10.1234/repaired"]
    assert repaired.iloc[0]["title"] == "A repaired title"
    assert repaired.iloc[0]["summary"] == records[0].summary
    assert "A repaired summary" in repaired.iloc[0]["text_for_embedding"]
