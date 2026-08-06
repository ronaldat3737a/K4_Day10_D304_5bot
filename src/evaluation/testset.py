from __future__ import annotations

from typing import Any
import json
import pandas as pd


def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
   """TODO(student): tao bo evaluation set tu cleaned dataframe.

   Pseudo-code:
   1. Kiem tra so luong document toi thieu.
   2. Chon mot so paper dai dien.
   3. Tao nhieu loai cau hoi:
      - summary
      - authors
      - date
      - categories
   4. Moi row can co:
      - id
      - question_type
      - question
      - ground_truth
      - ground_truth_doc_ids
   5. Ghi file JSON vao output_path.
   """
   # Kiểm tra số lượng document tối thiểu (ví dụ: 5)
   if len(df) < 5:
      raise ValueError("Cần ít nhất 5 bản ghi để tạo test set")
   
   # Chọn 10 paper đại diện (hoặc ít hơn nếu df có fewer than 10)
   sample_size = min(10, len(df))
   sampled_df = df.sample(n=sample_size, random_state=42)  # fixed seed for reproducibility
   
   test_set = []
   question_id = 1
   
   for _, row in sampled_df.iterrows():
      paper_id = row['paper_id']
      title = row['title']
      
      # 1. Câu hỏi về tóm tắt (summary)
      if pd.notna(row['summary']) and row['summary'].strip():
         test_set.append({
               "id": question_id,
               "question_type": "summary",
               "question": f"Tóm tắt của bài viết '{title}' là gì?",
               "ground_truth": row['summary'].strip(),
               "ground_truth_doc_ids": [paper_id]
         })
         question_id += 1
      
      # 2. Câu hỏi về tác giả (authors)
      if pd.notna(row['authors_joined']) and row['authors_joined'].strip():
         test_set.append({
               "id": question_id,
               "question_type": "authors",
               "question": f"Tác giả của bài viết '{title}' là ai?",
               "ground_truth": row['authors_joined'].strip(),
               "ground_truth_doc_ids": [paper_id]
         })
         question_id += 1
      
      # 3. Câu hỏi về ngày xuất bản (date)
      if pd.notna(row['published']) and row['published'].strip():
         test_set.append({
               "id": question_id,
               "question_type": "date",
               "question": f"Bài viết '{title}' được xuất bản khi nào?",
               "ground_truth": row['published'].strip(),
               "ground_truth_doc_ids": [paper_id]
         })
         question_id += 1
      
      # 4. Câu hỏi về chủ đề (categories)
      if pd.notna(row['categories_joined']) and row['categories_joined'].strip():
         test_set.append({
               "id": question_id,
               "question_type": "categories",
               "question": f"Bài viết '{title}' thuộc chủ đề nào?",
               "ground_truth": row['categories_joined'].strip(),
               "ground_truth_doc_ids": [paper_id]
         })
         question_id += 1
   
   # Ghi file JSON
   output_path.parent.mkdir(parents=True, exist_ok=True)
   with open(output_path, 'w', encoding='utf-8') as f:
      json.dump(test_set, f, ensure_ascii=False, indent=2)
   
   return test_set