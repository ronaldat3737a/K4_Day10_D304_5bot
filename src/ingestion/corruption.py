from __future__ import annotations

import pandas as pd

from core.utils import normalize_whitespace, write_json


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path) -> pd.DataFrame:
    """TODO(student): simulate nhieu dang data corruption.

    Pseudo-code:
    1. Drop mot so latest records.
    2. Blank summary o mot so dong.
    3. Inject noise vao text.
    4. Lam title bi truncate.
    5. Lam published date cu di.
    6. Add duplicate rows.
    7. Rebuild `text_for_embedding`.
    8. Ghi corruption log vao output_log_path.
    """
    seed = 42
    corrupted = df.copy(deep=True).reset_index(drop=True)
    changes: list[dict] = []

    if len(corrupted) >= 6:
        latest_ids = corrupted.sort_values("published", ascending=False).head(1)["paper_id"].tolist()
        corrupted = corrupted[~corrupted["paper_id"].isin(latest_ids)].reset_index(drop=True)
        changes.append({"type": "drop_latest_records", "paper_ids": latest_ids})

    if len(corrupted) >= 4:
        blank_id = corrupted.iloc[1]["paper_id"]
        corrupted.loc[corrupted["paper_id"] == blank_id, "summary"] = ""
        changes.append({"type": "blank_summary", "paper_ids": [blank_id]})

    if len(corrupted) >= 3:
        noise_id = corrupted.iloc[2]["paper_id"]
        corrupted.loc[corrupted["paper_id"] == noise_id, "summary"] = (
            corrupted.loc[corrupted["paper_id"] == noise_id, "summary"].iloc[0]
            + " [CORRUPTED_NOISE] unrelated noise."
        )
        changes.append({"type": "inject_summary_noise", "paper_ids": [noise_id]})

    if len(corrupted) >= 2:
        title_id = corrupted.iloc[0]["paper_id"]
        old_title = corrupted.loc[corrupted["paper_id"] == title_id, "title"].iloc[0]
        corrupted.loc[corrupted["paper_id"] == title_id, "title"] = old_title[: max(8, len(old_title) // 2)]
        changes.append({"type": "truncate_title", "paper_ids": [title_id]})

    if len(corrupted) >= 2:
        stale_id = corrupted.iloc[-1]["paper_id"]
        stale_date = pd.to_datetime(corrupted.loc[corrupted["paper_id"] == stale_id, "published"].iloc[0]) - pd.Timedelta(value=365, unit="D")
        corrupted.loc[corrupted["paper_id"] == stale_id, "published"] = stale_date.date().isoformat()
        corrupted.loc[corrupted["paper_id"] == stale_id, "age_days"] = int(corrupted.loc[corrupted["paper_id"] == stale_id, "age_days"].iloc[0]) + 365
        changes.append({"type": "stale_publication_date", "paper_ids": [stale_id]})

    if not corrupted.empty:
        duplicate_id = corrupted.iloc[-1]["paper_id"]
        corrupted = pd.concat([corrupted, corrupted.iloc[[-1]]], ignore_index=True)
        changes.append({"type": "duplicate_rows", "paper_ids": [duplicate_id]})

    def rebuild_text(row):
        return normalize_whitespace(
            f"{row['title']}. {row['summary']} Authors: {row.get('authors_joined', '')}. "
            f"Categories: {row.get('categories_joined', '')}."
        )

    corrupted["summary_chars"] = corrupted["summary"].fillna("").map(len)
    corrupted["text_for_embedding"] = corrupted.apply(rebuild_text, axis=1)
    write_json(
        output_log_path,
        {"seed": seed, "input_rows": len(df), "output_rows": len(corrupted), "changes": changes},
    )
    return corrupted
