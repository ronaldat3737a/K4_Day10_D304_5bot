from __future__ import annotations

from datetime import datetime

import pandas as pd

from core.utils import compact_join, normalize_whitespace, write_json
from ingestion.crossref import PaperRecord


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """TODO(student): clean raw records thanh dataframe san sang de embed.

    Pseudo-code:
    1. Normalize title, summary, authors, categories.
    2. Parse published/updated date.
    3. Tinh age_days.
    4. Tao cot helper:
       - authors_joined
       - categories_joined
       - summary_chars
       - text_for_embedding
    5. Drop duplicates va filter row xau.
    6. Sort dataframe va return.
    """
    rows: list[dict] = []
    run_day = run_date.date()
    for record in records:
        paper_id = normalize_whitespace(record.paper_id)
        title = normalize_whitespace(record.title)
        summary = normalize_whitespace(record.summary)
        if not paper_id or not title:
            continue
        published = pd.to_datetime(record.published, errors="coerce", utc=True)
        updated = pd.to_datetime(record.updated, errors="coerce", utc=True)
        if pd.isna(published):
            continue
        published_text = published.date().isoformat()
        updated_text = updated.date().isoformat() if not pd.isna(updated) else published_text
        authors = [normalize_whitespace(item) for item in (record.authors or []) if normalize_whitespace(item)]
        categories = [normalize_whitespace(item) for item in (record.categories or []) if normalize_whitespace(item)]
        authors_joined = compact_join(authors)
        categories_joined = compact_join(categories)
        text_for_embedding = normalize_whitespace(
            f"{title}. {summary} Authors: {authors_joined}. Categories: {categories_joined}."
        )
        rows.append(
            {
                "paper_id": paper_id,
                "title": title,
                "summary": summary,
                "authors": authors,
                "categories": categories,
                "primary_category": normalize_whitespace(record.primary_category),
                "published": published_text,
                "updated": updated_text,
                "abs_url": normalize_whitespace(record.abs_url),
                "pdf_url": normalize_whitespace(record.pdf_url),
                "comment": normalize_whitespace(record.comment),
                "authors_joined": authors_joined,
                "categories_joined": categories_joined,
                "summary_chars": len(summary),
                "age_days": max(0, (run_day - published.date()).days),
                "text_for_embedding": text_for_embedding,
            }
        )
    if not rows:
        return pd.DataFrame(columns=["paper_id", "title", "summary", "published", "age_days", "text_for_embedding"])
    frame = pd.DataFrame(rows).drop_duplicates(subset=["paper_id"], keep="first")
    return frame.sort_values(["published", "paper_id"], ascending=[False, True]).reset_index(drop=True)
