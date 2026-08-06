# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin | Nội dung |
|------------|----------|
| Khóa/Lớp | K4 |
| Tên nhóm | 5Bot |
| Repository | https://github.com/ronaldat3737a/K4_Day10_5bot.git |
| Ngày hoàn thành | 2026-08-06 |

### Thành viên và phân công

| STT | Thành viên | MSSV | Job |
|---:|---|---|---|
| 1 | Nguyễn Công Đạt | 2A202601526 | Source owner |
| 2 | Bùi Thái Sơn | 2A202601126 | Cleaning & test-set owner |
| 3 | Tống Tiến Mạnh | 2A202601614 | Observability owner |
| 4 | Nguyễn Văn Thắng | 2A202601580 | Corruption & repair owner |
| 5 | Nguyễn Tiến Đạt | 2A202601850 | Pipeline integration & evidence owner |

---

## 2. Tóm tắt kết quả

### Tóm tắt của nhóm

Nhóm 5Bot đã hoàn thành trọn vẹn hệ thống **Data Pipeline** và **Data Observability End-to-End** cho bài toán RAG trên tập dữ liệu bài báo khoa học từ **Crossref API**.

### Baseline

- Thu thập **24 bản ghi**
- Làm sạch dữ liệu
- Đánh chỉ mục **ChromaDB**
- Embedding bằng `all-MiniLM-L6-v2`
- Đánh giá trên **30 câu hỏi**

Kết quả:

| Metric | Giá trị |
|---------|---------|
| retrieval_hit_rate | **1.000** |
| judge_accuracy | **0.867** |
| mean_judge_score | **4.133 / 5** |

### Corruption

Thực hiện:

- Xóa 10% bản ghi mới nhất
- Blank Summary
- Inject Noise
- Truncate Title

Kết quả:

| Metric | Baseline | Corrupted |
|---------|-----------|------------|
| retrieval_hit_rate | 1.000 | 0.833 |
| judge_accuracy | 0.867 | 0.433 |
| mean_judge_score | 4.133 | 2.267 |

### Repair

Repair bằng:

- Ingest lại dữ liệu Raw
- Cleaning
- Build lại ChromaDB

Kết quả:

- Khôi phục toàn bộ metrics về mức Baseline
- Chất lượng dữ liệu đạt 100%
- Chỉ còn hạn chế:
  - Ragas phải chạy `max_workers=1`
  - Tránh lỗi Rate Limit (429)

---

# 3. Kiến trúc và luồng dữ liệu

## Luồng End-to-End

```text
Crossref API
    ↓
raw response/raw records
(data/raw/papers_raw.json)

    ↓
cleaning + data modeling
(data/clean/papers_clean.json)

    ↓
embedding + ChromaDB
(data/embeddings)

    ↓
evaluation
(data/results/baseline_metrics.json)

    ↓
quality / freshness
(data/quality/baseline_quality.json)

    ↓
corruption
(data/corrupted)

    ↓
re-evaluate
(data/eval/corrupted_metrics.json)

    ↓
repair
(data/repaired)

    ↓
comparison report
(data/reports/corruption_comparison.md)
```

### Phân công từng module

| Khối | Input | Xử lý | Output | Owner |
|------|-------|--------|--------|-------|
| Ingestion | Crossref REST API | Fetch API, retry, parse | papers_raw.json | Nguyễn Công Đạt |
| Cleaning | papers_raw.json | Chuẩn hóa dữ liệu | papers_clean.json | Bùi Thái Sơn |
| Embedding | papers_clean.json | MiniLM + ChromaDB | embeddings.json | Bùi Thái Sơn & Nguyễn Tiến Đạt |
| Evaluation | ChromaDB | Retrieval + LLM Judge + Ragas | baseline_metrics.json | Bùi Thái Sơn |
| Observability | papers_clean.json | Quality & Freshness | baseline_quality.json | Tống Tiến Mạnh |
| Corruption | papers_clean.json | Drop, Blank, Noise | corrupted/ | Nguyễn Văn Thắng |
| Orchestration | Terminal | Pipeline | reports/ | Nguyễn Tiến Đạt |

---

# 4. Cách tái hiện kết quả

## Cấu hình

| Biến | Giá trị |
|------|----------|
| LLM_PROVIDER | custom |
| LLM_MODEL | gpt-4o-mini |
| Embedding | all-MiniLM-L6-v2 |
| Crossref records | 24 |
| top_k | 4 |
| Freshness threshold | 180 days |
| Random Seed | 42 |

## Cài đặt

```bash
python -m pip install -e .
```

## Chạy Baseline

```bash
python script/run_phase1.py
```

## Chạy Corruption

```bash
python script/run_corruption_flow.py
```

---

# 5. Ingestion, Cleaning và Data Contract

## Nguồn dữ liệu

| Thuộc tính | Giá trị |
|-------------|----------|
| Source | Crossref REST API |
| Query | Retrieval Augmented Generation |
| Records | 24 |

### Schema

| Field | Required | Ý nghĩa |
|-------|----------|----------|
| paper_id | ✓ | DOI |
| title | ✓ | Tiêu đề |
| summary | | Abstract |
| published | ✓ | ISO Date |
| authors_joined | | Danh sách tác giả |
| text_for_embedding | ✓ | Chuỗi embedding |
| age_days | ✓ | Tuổi bản ghi |

---

# 6. Evaluation Setup

| Thành phần | Giá trị |
|------------|----------|
| Questions | 30 |
| Embedding | all-MiniLM-L6-v2 |
| Vector Store | ChromaDB |
| top_k | 4 |
| Model | gpt-4o-mini |

---

# 7. Baseline Metrics

| Metric | Giá trị |
|---------|---------|
| retrieval_hit_rate | 1.000 |
| mean_token_f1 | 0.145 |
| judge_accuracy | 0.867 |
| mean_judge_score | 4.133 |
| faithfulness | 0.892 |
| answer_relevancy | 0.854 |

---

# 8. Data Quality

| Check | Baseline |
|--------|----------|
| Completeness | Pass |
| Uniqueness | Pass |
| Date Validity | Pass |
| Text Embedding | Pass |

Freshness:

- Threshold: 180 days
- Status: Fresh

---

# 9. Corruption & Repair

| Corruption | Repair |
|------------|--------|
| Drop Latest Records | Re-fetch API |
| Blank Summary | Restore summary |
| Truncate Title | Restore title |
| Inject Noise | Clean Regex |

Repair thực hiện:

- Ingest lại từ Raw
- Cleaning
- Build lại ChromaDB

---

# 10. So sánh Baseline / Corrupted / Repaired

| Metric | Baseline | Corrupted | Repaired |
|---------|-----------|------------|------------|
| retrieval_hit_rate | 1.000 | 0.833 | 1.000 |
| mean_token_f1 | 0.145 | 0.082 | 0.145 |
| judge_accuracy | 0.867 | 0.433 | 0.867 |
| mean_judge_score | 4.133 | 2.267 | 4.133 |

---

# 11. Vấn đề tích hợp

## Lỗi

```
AttributeError
ValidationError
RateLimitError (429)
```

### Nguyên nhân

- Sai kiểu `self.model`
- Ragas chạy đa luồng

### Cách xử lý

- Đổi:

```python
self.model
```

thành

```python
self._model
```

- Thêm:

```python
RunConfig(
    max_workers=1,
    max_retries=15
)
```

---

# 12. Giới hạn

| Giới hạn | Hướng cải thiện |
|----------|-----------------|
| Token F1 thấp | BERTScore |
| Rate Limit | Ollama / vLLM |

---

# 13. Checklist

- [x] Thông tin nhóm chính xác
- [x] Phân công đầy đủ
- [x] Chạy lại pipeline
- [x] Dùng cùng Evaluation Set
- [x] Metrics khớp
- [x] Quality khớp
- [x] Artifact đầy đủ
- [x] Báo cáo từng thành viên
- [x] Không chứa API Key / Secret