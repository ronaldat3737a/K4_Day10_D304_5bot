import json

from ingestion.crossref import load_raw_records, parse_crossref_payload


def test_parse_crossref_payload_maps_metadata():
    payload = {
        "message": {
            "items": [
                {
                    "DOI": "10.5555/example",
                    "title": [" Example title "],
                    "abstract": "<jats:p>Example abstract.</jats:p>",
                    "author": [{"given": "Ada", "family": "Lovelace"}],
                    "subject": ["AI"],
                    "published": {"date-parts": [[2026, 7, 1]]},
                    "updated": {"date-time": "2026-07-02T00:00:00Z"},
                    "URL": "https://doi.org/10.5555/example",
                    "link": [{"URL": "https://example.org/paper.pdf", "content-type": "application/pdf"}],
                    "note": "demo",
                }
            ]
        }
    }

    records = parse_crossref_payload(payload)

    assert len(records) == 1
    assert records[0].paper_id == "10.5555/example"
    assert records[0].title == "Example title"
    assert records[0].summary == "Example abstract."
    assert records[0].authors == ["Ada Lovelace"]
    assert records[0].published == "2026-07-01"


def test_load_raw_records_reads_snapshot(tmp_path):
    path = tmp_path / "records.json"
    path.write_text(json.dumps([{
        "paper_id": "10.5555/example",
        "title": "Example",
        "summary": "Summary",
        "authors": ["Ada"],
        "categories": ["AI"],
        "primary_category": "AI",
        "published": "2026-07-01",
        "updated": "2026-07-01",
        "abs_url": "https://doi.org/10.5555/example",
        "pdf_url": "",
        "comment": "",
    }]))

    records = load_raw_records(path)

    assert records[0].paper_id == "10.5555/example"
