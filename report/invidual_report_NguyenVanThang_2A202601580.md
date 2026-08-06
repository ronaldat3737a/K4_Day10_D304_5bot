# Individual Report — Corruption & Repair Owner

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | [Nguyễn Văn Thắng] |
| MSSV | [2A202601580] |
| Khóa/Lớp | K4 |
| Tên nhóm | [Tên hoặc mã nhóm] |
| Vai trò chính | Corruption & repair owner |
| Repository | `K4_Day10_5bot` |
| Ngày hoàn thành | 2026-08-06 |

## 2. Phạm vi công việc sở hữu

| Module/deliverable | File chính | Input | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Data corruption engine | `src/ingestion/corruption.py` | Baseline clean dataframe | Corrupted dataframe và `data/corruption_log.json` | Đã triển khai và xác minh runtime |
| Repair từ dữ liệu nguồn | `src/ingestion/crossref.py`, `src/ingestion/cleaning.py` | `data/raw/crossref_records.json` | Repaired dataframe được tạo lại bằng cleaning | Đã tích hợp và xác minh runtime |
| Corruption/repair orchestration | `src/pipelines/corruption_flow.py` | Baseline artifacts, raw records, evaluation set | Corrupted/repaired datasets, indexes, metrics, answers và comparison report | Đã triển khai và chạy end-to-end |
| Observability comparison | `src/observability/quality.py`, `src/observability/reporting.py` | Corrupted/repaired data và metrics | Quality, freshness và `corruption_comparison.md` | Đã triển khai và xác minh runtime |

## 3. Những việc đã thực hiện

### 3.1. Tạo các kịch bản corruption có tính tái lập

Trong `corrupt_clean_dataframe()` đã triển khai các thay đổi theo thứ tự deterministic, với seed cố định `42`:

1. Xóa record mới nhất.
2. Làm rỗng summary của một record.
3. Chèn noise vào summary.
4. Cắt ngắn title.
5. Làm cũ publication date và cập nhật `age_days`.
6. Nhân đôi một record.
7. Tạo lại `summary_chars` và `text_for_embedding` sau corruption.
8. Ghi `seed`, số dòng đầu vào/đầu ra và `paper_id` bị tác động vào corruption log.

Hàm dùng `df.copy(deep=True)`, vì vậy không thay đổi baseline dataframe ban đầu.

### 3.2. Xây dựng repair từ raw source

Repair không sửa trực tiếp corrupted dataframe để che lỗi. Flow đọc lại raw records bằng `load_raw_records()` rồi gọi:

```python
build_clean_dataframe(load_raw_records(paths.raw_records_json), datetime.now(UTC))
```

Cách này khôi phục dữ liệu theo cùng contract cleaning và tạo lại các trường chuẩn trước khi build repaired index.

### 3.3. Điều phối flow corrupted/repaired

`run_flow()` đã được bổ sung để:

- kiểm tra các baseline artifacts bắt buộc trước khi chạy;
- ghi corrupted CSV/JSON và corrupted embedding manifest riêng;
- đánh giá corrupted trên `paths.eval_testset`;
- chạy quality check và freshness cho corrupted;
- tạo repaired dataset từ raw source;
- build repaired index và đánh giá trên cùng evaluation set;
- chạy quality/freshness cho repaired;
- sinh comparison report từ baseline, corrupted và repaired metrics.

Các đường dẫn corrupted/repaired được tách khỏi baseline, tránh ghi đè `papers_clean.csv`, embedding baseline và `baseline_metrics.json`.

## 4. Kết quả và bằng chứng

| Hạng mục | Bằng chứng | Kết quả xác minh |
| --- | --- | --- |
| Corruption không mutate input | `tests/test_corruption.py` | Có test kiểm tra dataframe gốc không đổi |
| Corruption deterministic | `tests/test_corruption.py` | Có test chạy hai lần và so sánh kết quả |
| Baseline artifacts bắt buộc | `tests/test_corruption_flow.py` | Có test kiểm tra `FileNotFoundError` khi thiếu baseline |
| Repair contract | `tests/test_repair_contract.py` | Có test contract trong repository |
| Comparison report | `src/observability/reporting.py` | Có bảng 4 metric và trạng thái quality/freshness |
| Runtime artifacts | `data/` | Có corrupted/repaired datasets, metrics, quality/freshness và comparison report |

## 5. Luồng kỹ thuật

```text
baseline clean dataframe
    -> deterministic corruption + corruption log
    -> corrupted index/evaluation/quality/freshness
raw Crossref records
    -> cleaning lại từ nguồn gốc
    -> repaired index/evaluation/quality/freshness
baseline + corrupted + repaired
    -> comparison report
```

Ba trạng thái dùng cùng `data/eval/test_set.json` để metric thay đổi phản ánh tác động của corruption/repair thay vì khác evaluation set. Repair thành công khi dữ liệu được dựng lại từ raw source, các artifact repaired được tạo riêng và các quality/freshness/agent metrics được ghi nhận để so sánh.

## 6. Lỗi hoặc blocker đã xử lý

- **Vấn đề:** cần mô phỏng nhiều dạng hỏng dữ liệu nhưng vẫn giữ nguyên baseline và có thể tái lập.
- **Cách xử lý:** dùng deep copy, seed cố định, danh sách thay đổi theo `paper_id`, output path riêng và rebuild text sau khi chỉnh dữ liệu.
- **Vấn đề runtime:** model Gemini cấu hình ban đầu không khả dụng cho API key mới, gây lỗi `404 NOT_FOUND`.
- **Cách xử lý:** cập nhật `LLM_MODEL` trong `.env` sang model Gemini mới hơn và chạy lại corruption flow.

## 7. Phân tích kết quả

### Metrics thực tế

| Metric | Baseline | Corrupted | Repaired |
| --- | ---: | ---: | ---: |
| `judge_accuracy` | 1.0000 | 0.9000 | 1.0000 |
| `mean_judge_score` | 4.7667 | 4.4000 | 4.8000 |
| `mean_token_f1` | 0.7234 | 0.6761 | 0.7214 |
| `retrieval_hit_rate` | 1.0000 | 1.0000 | 1.0000 |
| `samples` | 30 | 30 | 30 |

Corruption làm giảm chất lượng câu trả lời nhưng không làm giảm `retrieval_hit_rate`: `judge_accuracy` giảm 10%, `mean_judge_score` giảm từ 4.7667 xuống 4.4000 và `mean_token_f1` giảm từ 0.7234 xuống 0.6761. Sau repair, các chỉ số được phục hồi gần như hoàn toàn.

### Data quality và freshness

| Check | Corrupted | Repaired |
| --- | --- | --- |
| `paper_id_unique` | False | True |
| `summary_min_length_10` | False | True |
| `row_count` | 23 | 24 |
| `stale_rows` | 0 | 0 |

Kết quả xác nhận corrupted dataset có duplicate và summary không đạt độ dài tối thiểu; repaired dataset khôi phục được tính duy nhất của `paper_id`, summary hợp lệ và số dòng về 24.

## 8. Điều học được và hướng cải thiện

1. Corruption cần có log chi tiết và seed cố định để kết quả có thể tái hiện.
2. Repair đáng tin cậy hơn khi lấy lại dữ liệu từ raw source thay vì chỉnh ngược corrupted data.
3. Data quality/freshness signal cần được đọc cùng agent metrics để giải thích nguyên nhân thay đổi chất lượng retrieval/answer.

Nếu có thêm thời gian, có thể bổ sung baseline quality/freshness trực tiếp vào comparison report thay vì để `N/A`, đồng thời thêm kiểm tra checksum baseline sau mỗi lần chạy flow.

## 9. Cam kết

- [x] Báo cáo chỉ mô tả phần việc thuộc Corruption & repair owner.
- [x] Các kết quả runtime đều dựa trên artifact và comparison report thực tế.
- [x] Không chứa API key, token hoặc secret.
- [x] Đã hoàn thành xác minh end-to-end.

**Họ và tên:** [Nguyễn Văn Thắng]  
**Ngày xác nhận:** 2026-08-06
