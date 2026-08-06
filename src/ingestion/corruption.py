from __future__ import annotations

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import random

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

    """Simulate nhiều dạng data corruption."""
    # Tạo bản sao để không thay đổi DataFrame gốc
    corrupted_df = df.copy()
    
    # Initialize corruption log
    corruption_log = {
        "timestamp": datetime.now().isoformat(),
        "operations": [],
        "original_row_count": len(df),
        "corrupted_row_count": 0,
        "changes": {}
    }
    
    # 1. Drop một số latest records (ví dụ: 10% của bản ghi cuối cùng)
    n_drop = max(1, len(corrupted_df) // 10)
    if len(corrupted_df) > n_drop:
        # Lấy indices của n_drop bản ghi cuối cùng
        drop_indices = corrupted_df.tail(n_drop).index
        corrupted_df = corrupted_df.drop(index=drop_indices)
        corruption_log["operations"].append(f"Dropped {n_drop} latest records")
        corruption_log["changes"]["dropped_latest_count"] = n_drop
    
    # 2. Blank summary ở một số dòng (ví dụ: 15% của bản ghi)
    n_blank = max(1, len(corrupted_df) // 7)
    if len(corrupted_df) > 0 and "summary" in corrupted_df.columns:
        blank_indices = corrupted_df.sample(n=min(n_blank, len(corrupted_df)), random_state=42).index
        corrupted_df.loc[blank_indices, "summary"] = ""
        corruption_log["operations"].append(f"Blanked summary for {len(blank_indices)} rows")
        corruption_log["changes"]["blanked_summary_count"] = len(blank_indices)
    
    # 3. Inject noise vào text (ví dụ: thêm ký tự ngẫu nhiên vào summary)
    n_noise = max(1, len(corrupted_df) // 8)
    if len(corrupted_df) > 0 and "summary" in corrupted_df.columns:
        noise_indices = corrupted_df.sample(n=min(n_noise, len(corrupted_df)), random_state=43).index
        for idx in noise_indices:
            original = str(corrupted_df.at[idx, "summary"])
            # Thêm noise: chèn một số ký tự đặc biệt ngẫu nhiên
            if len(original) > 5:
                pos = random.randint(0, len(original))
                noise = "!!!"
                corrupted_df.at[idx, "summary"] = original[:pos] + noise + original[pos:]
            else:
                corrupted_df.at[idx, "summary"] = original + "!!!"
        corruption_log["operations"].append(f"Injected noise into summary for {len(noise_indices)} rows")
        corruption_log["changes"]["noise_injected_count"] = len(noise_indices)
    
    # 4. Làm title bị truncate (cắt ngắn title xuống 50% độ dài gốc)
    n_truncate = max(1, len(corrupted_df) // 9)
    if len(corrupted_df) > 0 and "title" in corrupted_df.columns:
        truncate_indices = corrupted_df.sample(n=min(n_truncate, len(corrupted_df)), random_state=44).index
        for idx in truncate_indices:
            original = str(corrupted_df.at[idx, "title"])
            if len(original) > 3:
                new_length = max(1, len(original) // 2)
                corrupted_df.at[idx, "title"] = original[:new_length]
            else:
                corrupted_df.at[idx, "title"] = original  # giữ nguyên nếu quá ngắn
        corruption_log["operations"].append(f"Truncated title for {len(truncate_indices)} rows")
        corruption_log["changes"]["truncated_title_count"] = len(truncate_indices)
    
    # 5. Làm published date cũ đi (trừ đi một số ngày ngẫu nhiên)
    n_date_corrupt = max(1, len(corrupted_df) // 10)
    if len(corrupted_df) > 0 and "published" in corrupted_df.columns:
        date_indices = corrupted_df.sample(n=min(n_date_corrupt, len(corrupted_df)), random_state=45).index
        for idx in date_indices:
            original = corrupted_df.at[idx, "published"]
            try:
                # Nếu là string, chuyển sang datetime
                if isinstance(original, str):
                    dt = datetime.fromisoformat(original.replace('Z', '+00:00'))
                else:
                    dt = original
                # Trừ đi giữa 30 và 365 ngày
                days_to_subtract = random.randint(30, 365)
                new_dt = dt - timedelta(days=days_to_subtract)
                corrupted_df.at[idx, "published"] = new_dt.isoformat()
            except Exception:
                # Nếu lỗi, giữ nguyên
                pass
        corruption_log["operations"].append(f"Made published date older for {len(date_indices)} rows")
        corruption_log["changes"]["date_corrupted_count"] = len(date_indices)
    
    # 6. Thêm bản ghi trùng lặp (ví dụ: sao chép 5% bản ghi)
    n_dup = max(1, len(corrupted_df) // 20)
    if len(corrupted_df) > 0 and n_dup > 0:
        dup_indices = corrupted_df.sample(n=min(n_dup, len(corrupted_df)), random_state=46).index
        dup_rows = corrupted_df.loc[dup_indices].copy()
        corrupted_df = pd.concat([corrupted_df, dup_rows], ignore_index=True)
        corruption_log["operations"].append(f"Added {len(dup_rows)} duplicate rows")
        corruption_log["changes"]["duplicate_rows_added"] = len(dup_rows)
    
    # 7. Rebuild `text_for_embedding` (giả sử là kết hợp title và summary)
    if "title" in corrupted_df.columns and "summary" in corrupted_df.columns:
        corrupted_df["text_for_embedding"] = (
            corrupted_df["title"].fillna("") + ". " + corrupted_df["summary"].fillna("")
        ).str.strip()
        corruption_log["operations"].append("Rebuilt text_for_embedding column")
    
    # 8. Ghi corruption log vào output_log_path
    corruption_log["corrupted_row_count"] = len(corrupted_df)
    # Đảm bảo thư mục tồn tại
    output_log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_log_path, "w", encoding="utf-8") as f:
        json.dump(corruption_log, f, ensure_ascii=False, indent=2)
    
    return corrupted_df
