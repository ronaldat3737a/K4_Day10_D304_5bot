from __future__ import annotations

from datetime import datetime
import re
import pandas as pd

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
   # Chuyển records thành list of dict
   rows = []
   for r in records:
      # Chuẩn hóa text: strip whitespace và thay thế nhiều khoảng trắng bằng một space
      title = re.sub(r'\s+', ' ', r.title.strip()) if r.title else ""
      summary = re.sub(r'\s+', ' ', r.summary.strip()) if r.summary else ""
      
      # Chuẩn hóa authors: mỗi author strip và ghép lại
      authors = [re.sub(r'\s+', ' ', a.strip()) for a in r.authors if a.strip()]
      authors_joined = "; ".join(authors)
      
      # Chuẩn hóa categories: mỗi category strip và ghép lại
      categories = [re.sub(r'\s+', ' ', c.strip()) for c in r.categories if c.strip()]
      categories_joined = "; ".join(categories)
      
      # Xác thực và parse ngày
      try:
         published_dt = datetime.strptime(r.published, "%Y-%m-%d")
      except ValueError:
         published_dt = None  # Sẽ bị filtered sau
      try:
         updated_dt = datetime.strptime(r.updated, "%Y-%m-%d")
      except ValueError:
         updated_dt = None
      
      # Tính age_days chỉ nếu published_dt hợp lệ
      age_days = (run_date - published_dt).days if published_dt else None
      
      # Tạo text_for_embedding: kết hợp title và summary
      text_for_embedding = f"{title} {summary}".strip()
      summary_chars = len(summary)
      
      rows.append({
         "paper_id": r.paper_id,
         "title": title,
         "summary": summary,
         "authors": authors,  # Giữ lại list để tiềm năng sử dụng sau
         "authors_joined": authors_joined,
         "categories": categories,  # Giữ lại list
         "categories_joined": categories_joined,
         "primary_category": r.primary_category.strip(),
         "published": r.published,
         "updated": r.updated,
         "published_dt": published_dt,
         "updated_dt": updated_dt,
         "age_days": age_days,
         "abs_url": r.abs_url,
         "pdf_url": r.pdf_url,
         "comment": r.comment,
         "summary_chars": summary_chars,
         "text_for_embedding": text_for_embedding
      })
   
   if not rows:
      return pd.DataFrame()
   
   df = pd.DataFrame(rows)
   
   # Filter bỏ bản ghi không hợp lệ: title rỗng, summary rỗng, hoặc published_dt không hợp lệ
   df = df[
      (df["title"].str.len() > 0) &
      (df["summary"].str.len() > 0) &
      (df["published_dt"].notna())
   ].copy()
   
   # Drop trùng lặp dựa trên paper_id
   df = df.drop_duplicates(subset=["paper_id"], keep="first")
   
   # Sắp xếp theo published_dt giảm dần (mới nhất trước)
   df = df.sort_values("published_dt", ascending=False)
   
   # Đảm bảo các cột helper tồn tại (đã tạo ở trên)
   return df