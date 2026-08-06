from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest


@pytest.fixture
def clean_fixture() -> pd.DataFrame:
    run_date = datetime.now(UTC).date()
    rows = []
    for index in range(8):
        published = run_date - timedelta(days=index * 30)
        rows.append(
            {
                "paper_id": f"10.1234/paper-{index}",
                "title": f"Retrieval paper {index}",
                "summary": f"This is a sufficiently long scholarly summary for paper {index}.",
                "authors": [f"Author {index}"],
                "categories": ["computer science"],
                "primary_category": "computer science",
                "published": published.isoformat(),
                "updated": published.isoformat(),
                "abs_url": f"https://doi.org/10.1234/paper-{index}",
                "pdf_url": "",
                "comment": "",
                "authors_joined": f"Author {index}",
                "categories_joined": "computer science",
                "summary_chars": 55,
                "age_days": (run_date - published).days,
                "text_for_embedding": f"Retrieval paper {index}. This is a sufficiently long scholarly summary for paper {index}.",
            }
        )
    return pd.DataFrame(rows)
