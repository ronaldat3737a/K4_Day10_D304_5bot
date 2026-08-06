from __future__ import annotations
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from dataclasses import dataclass
from pathlib import Path
import sys


from core.config import Settings

import json
import time
import requests

# Constant for Crossref API
CROSSREF_API_URL = "https://api.crossref.org/works"


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """TODO(student): parse Crossref payload thanh list PaperRecord.

    Pseudo-code:
    1. Duyet `payload["message"]["items"]`.
    2. Lay DOI, title, abstract, authors, subject, dates, URLs.
    3. Chuan hoa text va bo record khong hop le.
    4. Tra ve list `PaperRecord`.
    """
    records = []
    items = payload.get("message", {}).get("items", [])
    for item in items:
        doi = item.get("DOI")
        if not doi:
            continue
        title = item.get("title", [""])[0] if item.get("title") else ""
        abstract = item.get("abstract", "")
        authors = []
        for author in item.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            name = f"{given} {family}".strip()
            if name:
                authors.append(name)
        subjects = item.get("subject", [])
        primary_category = subjects[0] if subjects else ""
        # Xử lý ngày
        date_parts = None
        for date_key in ["published-print", "published-online", "created"]:
            if date_key in item and "date-parts" in item[date_key]:
                date_parts = item[date_key]["date-parts"][0]
                break
        if date_parts:
            year = str(date_parts[0]) if len(date_parts) > 0 else "0000"
            month = f"{date_parts[1]:02d}" if len(date_parts) > 1 and date_parts[1] else "01"
            day = f"{date_parts[2]:02d}" if len(date_parts) > 2 and date_parts[2] else "01"
            published = f"{year}-{month}-{day}"
            updated = published  # giả sử cùng ngày
        else:
            published = "0000-01-01"
            updated = "0000-01-01"
        abs_url = item.get("URL", "")
        pdf_url = ""  # Crossref không cung cấp PDF trực tiếp
        comment = ""
        records.append(PaperRecord(
            paper_id=doi,
            title=title,
            summary=abstract,
            authors=authors,
            categories=subjects,
            primary_category=primary_category,
            published=published,
            updated=updated,
            abs_url=abs_url,
            pdf_url=pdf_url,
            comment=comment
        ))
    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """TODO(student): goi source API, luu raw response, parse thanh records.

    Pseudo-code:
    1. Tao params tu `settings.source_query`, `settings.source_filter`, `settings.max_results`.
    2. Goi API voi retry cho cac status code nhu 429/503.
    3. Luu raw response vao `settings.paths.raw_api_response`.
    4. Parse payload bang `parse_crossref_payload`.
    5. Luu records vao `settings.paths.raw_records_json`.
    """
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results
    }
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 503],
        allowed_methods=["GET"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    try:
        response = session.get(CROSSREF_API_URL, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        # Lưu raw response vào data/raw/
        settings.paths.raw_api_response.parent.mkdir(parents=True, exist_ok=True)
        with open(settings.paths.raw_api_response, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        # Parse và lưu records đã parse vào data/raw/
        records = parse_crossref_payload(payload)
        settings.paths.raw_records_json.parent.mkdir(parents=True, exist_ok=True)
        with open(settings.paths.raw_records_json, "w", encoding="utf-8") as f:
            json.dump([r.__dict__ for r in records], f, ensure_ascii=False, indent=2)
        return records
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch from Crossref API: {e}")


def load_raw_records(path: Path) -> list[PaperRecord]:
    """TODO(student): doc JSON snapshot va map thanh `PaperRecord`."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = []
    for item in data:
        records.append(PaperRecord(**item))
    return records