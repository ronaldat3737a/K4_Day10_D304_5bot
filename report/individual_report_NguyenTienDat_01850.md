# Member Role Report — Day 10: Data Pipeline & Data Observability

> Báo cáo cá nhân vai trò Pipeline Integration & Evidence Owner.

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Nguyễn Tiến Đạt             |
| MSSV               | 2A202601850                |
| Khóa/Lớp         | K4                         |
| Tên nhóm         | 5Bot                       |
| Vai trò chính    | Pipeline integration & evidence owner |
| Repository         | [Đường dẫn repository]     |
| Ngày hoàn thành | 2026-08-06                 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ phụ trách | Input nhận vào | Output bàn giao  | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Orchestration & Pipeline Integration | `script/run_phase1.py`, `script/run_corruption_flow.py` | Nguồn dữ liệu từ Ingestion, Clean schema, Vector Store config | Luồng thực thi tự động hóa End-to-End từ ingestion đến evaluation & report | Hoàn thành |
| Evidence & Comparison Reporting | `src/reports/` / `data/results/comparison_report.md` | Baseline, Corrupted, Repaired metrics & logs | Comparison report, corruption comparison artifacts, evidence logs | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Debug & Tích hợp Vector DB / RAG Evaluation | Tống Tiến Mạnh (Observability), Nguyễn Văn Thắng (Corruption/Repair) | Tích hợp thành công luồng đánh giá tự động và sinh file báo cáo tổng hợp |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Triển khai luồng Pipeline Integration | `script/run_phase1.py`, `script/run_corruption_flow.py` | Chạy toàn bộ luồng E2E từ Ingestion -> Cleaning -> Indexing -> Eval -> Observability -> Corruption -> Repair -> Re-eval | `uv run python script/run_corruption_flow.py` |
| Thu thập evidence & xuất báo cáo so sánh | `data/results/corruption_log.json`, `data/reports/` | Đã tổng hợp đầy đủ chỉ số Baseline, Corrupted, Repaired và sinh ra Báo cáo so sánh | Kiểm tra `data/results/corruption_log.json` và file report |

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Xây dựng pipeline tích hợp (Orchestration) để kết nối các module độc lập (Ingestion, Cleaning, Indexing, Observability, Corruption, Repair) chạy một cách liên tục và tự động. Thu thập các bằng chứng (evidence) và chỉ số để so sánh chính xác chất lượng RAG agent qua 3 giai đoạn: Baseline, Corrupted, và Repaired.

### Cách triển khai
- Viết kịch bản điều phối execution flow trong `script/run_corruption_flow.py` để đảm bảo dữ liệu chạy đúng trình tự.
- Ghi nhận `corruption_log.json` để lưu vết các hành vi gây lỗi dữ liệu.
- Tổng hợp chỉ số từ các bước đánh giá RAG (`judge_accuracy`, `mean_judge_score`, `mean_token_f1`, `retrieval_hit_rate`) và các kiểm tra chất lượng (`Data Quality`, `Freshness`) vào file báo cáo so sánh.

### Input, output và contract

| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Raw records, Clean schema, Test set, Corruption parameters |
| Output                         | `baseline_metrics.json`, `corruption_log.json`, `comparison_report.md` |
| Module phụ thuộc             | Source Ingestion, Cleaning, Observability, Corruption & Repair |
| Module sử dụng output        | Báo cáo chung của nhóm (Group Report), Báo cáo đánh giá cá nhân |
| Điều kiện lỗi cần xử lý | Lỗi mất đồng bộ dữ liệu giữa vector index và metadata, trôi schema khi corrupt |

### Cách xác minh

```bash
uv run python script/run_corruption_flow.py
```

- **Kết quả mong đợi:** Tự động thực hiện toàn bộ luồng, xuất dữ liệu so sánh 3 trạng thái và sinh artifact trong `data/results/`.
- **Kết quả thực tế:** Tất cả 30 samples được đánh giá thành công, các tệp log và báo cáo so sánh được tạo chính xác tại `data/results/` và `data/reports/`.
- **Artifact/log:** `data/results/corruption_log.json`, `data/results/comparison_report.md`.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Cần đảm bảo tính nhất quán tuyệt đối của việc đánh giá RAG Agent qua các bước Baseline, Corrupted và Repaired.
- **Các phương án đã cân nhắc:**
  1. Sinh ngẫu nhiên câu hỏi đánh giá mới cho mỗi giai đoạn.
  2. Cố định duy nhất một bộ Test Set (30 samples) dùng chung cho cả 3 trạng thái.
- **Phương án đã chọn:** Phương án 2 - Cố định duy nhất 1 bộ Test Set cho cả 3 giai đoạn.
- **Lý do:** Giúp loại bỏ nhiễu từ biến số câu hỏi, đảm bảo sự thay đổi của các chỉ số (`judge_accuracy`, `mean_token_f1`, `mean_judge_score`) phản ánh chính xác 100% tác động của Data Quality và Repair.
- **Bằng chứng quyết định phù hợp:** Kết quả so sánh minh bạch với cùng sample count (30 samples) giúp chỉ ra trực diện sự suy giảm của `judge_accuracy` từ 1.0000 xuống 0.9000 khi corrupt và hồi phục về 1.0000 sau repair.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** Lỗi trôi Vector Index khi re-index dữ liệu bị corrupt/repaired làm kết quả retrieval bị lệch hoặc trả về document ID cũ.
- **Lệnh hoặc bước tái hiện:** Chạy `run_corruption_flow.py` khi chưa xóa/reset ChromaDB collection cũ.
- **Nguyên nhân gốc:** ChromaDB vẫn lưu các vector embedding của các record cũ/bị xoá làm ảnh hưởng đến bước Retrieval `top_k`.
- **Cách xử lý:** Thêm bước Reset / Re-create ChromaDB collection trước mỗi lần Re-indexing trong pipeline script.
- **Cách xác minh sau khi sửa:** Chạy lại `uv run python script/run_corruption_flow.py`, kiểm tra `retrieval_hit_rate` giữ vững 1.0000 qua các bước.
- **Điều học được:** Khi xây dựng data pipeline có trạng thái (stateful storage như Vector DB), việc quản lý lifecycle và reset state ở từng bước test/evaluation là rất quan trọng.

## 7. Hiểu biết về luồng end-to-end

**Câu trả lời:**

1. **Dữ liệu đi từ Crossref đến vector index:** Khối Ingestion fetch raw records từ API Crossref -> Data Cleaning chuẩn hóa schema, xử lý thiếu/lỗi và tạo `text_for_embedding` -> Embedding model chuyển đổi văn bản thành vector -> Lưu vào ChromaDB index.
2. **Evaluation set và ground-truth document IDs:** Bộ câu hỏi kiểm thử chứa các `ground_truth` document ID. Khi RAG agent thực hiện retrieval, hệ thống đối chiếu top_k kết quả trả về với `ground_truth` ID để tính `retrieval_hit_rate` và gửi context cho LLM sinh câu trả lời để chấm điểm (`mean_token_f1`, `judge_accuracy`, `mean_judge_score`).
3. **Quality checks vs Freshness monitoring:** Quality checks tập trung vào tính toàn vẹn và hợp lệ của schema (ví dụ: `paper_id_unique`, `paper_id_not_null`, `summary_min_length_10`). Trong khi Freshness monitoring đo độ mới của dữ liệu dựa trên timestamp (`latest_published`, `oldest_published`, `stale_rows`).
4. **Lý do dùng cùng test set:** Để đảm bảo tính công bằng và có thể so sánh trực tiếp (apples-to-apples comparison). Bất kỳ sự thay đổi nào về metric đều hoàn toàn do sự thay đổi của chất lượng dữ liệu chứ không phải do độ khó của câu hỏi.
5. **Dấu hiệu Repair thành công:** Repair thành công khi các Quality checks bị Fail ở bước Corrupted (`paper_id_unique`, `summary_min_length_10`, `row_count`) khôi phục về trạng thái `Pass/True`, đồng thời các chỉ số của Agent (`judge_accuracy` phục hồi từ 0.9000 lên 1.0000, `mean_judge_score` khôi phục từ 4.4000 lên 4.8000).

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` |   1.0000 |    1.0000 |   1.0000 | Tỷ lệ tìm kiếm chính xác giữ vững 100% nhờ cấu trúc context không mất hẳn ID chính |
| `mean_token_f1`      |   0.7234 |    0.6761 |   0.7214 | F1 score giảm từ 0.7234 xuống 0.6761 khi bị corrupt và phục hồi gần như hoàn toàn (0.7214) |
| `judge_accuracy`     |   1.0000 |    0.9000 |   1.0000 | Tỷ lệ câu trả lời đạt chuẩn giảm 10% do dữ liệu rác/thiếu summary, sau repair phục hồi về 100% |
| `mean_judge_score`   |   4.7667 |    4.4000 |   4.8000 | Điểm đánh giá trung bình bị sụt giảm đáng kể (từ 4.7667 -> 4.4000) và khôi phục đạt 4.8000 |
| Quality checks         |     Pass | 2 Checks Failed (`paper_id_unique`, `summary_min_length_10`) | All Passed | Khôi phục hoàn toàn các vi phạm chất lượng dữ liệu |
| Freshness status       |     Fresh |     Fresh |    Fresh | Mặc dù mốc thời gian không bị trôi stale nhưng row count giảm từ 24 -> 23 ở bước corrupt |

### Kết luận từ số liệu

1. **Chuỗi 1:** Data corruption (Drop 2 records, blank/noise summary, thêm duplicate row) → Quality checks thất bại ở `paper_id_unique` (False) và `summary_min_length_10` (False) → Agent metrics sụt giảm rõ rệt: `judge_accuracy` giảm từ 1.0000 xuống 0.9000, `mean_judge_score` giảm từ 4.7667 xuống 4.4000, `mean_token_f1` giảm từ 0.7234 xuống 0.6761.
2. **Chuỗi 2:** Repair action (Fetch & bổ sung lại record chuẩn từ nguồn, loại bỏ duplicate, khôi phục summary) → Quality signals phục hồi hoàn toàn (`paper_id_unique` = True, `summary_min_length_10` = True, `row_count` trở lại 24) → Agent metrics phục hồi ấn tượng (`judge_accuracy` trở lại 1.0000, `mean_judge_score` tăng lên 4.8000, `mean_token_f1` phục hồi lên 0.7214).

**Corruption nào ảnh hưởng rõ nhất và vì sao?**
Việc **Blank summary** và **Noise injected into summary** ảnh hưởng rõ nhất đến chất lượng đầu ra của LLM Agent. Nguyên nhân do Retrieval vẫn lấy đúng document (`retrieval_hit_rate` = 1.0000), nhưng nội dung trong document bị thiếu hụt hoặc lẫn nhiễu, khiến LLM sinh ra câu trả lời thiếu chính xác hoặc mơ hồ, dẫn đến `judge_accuracy` và `mean_judge_score` bị giảm mạnh.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. **Quản lý Pipeline Tự động hóa:** Tầm quan trọng của việc kết nối các bước end-to-end giúp việc đo đạc và tái hiện thí nghiệm dữ liệu nhanh chóng và đáng tin cậy.
2. **Data Observability đóng vai trò sống còn:** Các chỉ số Quality Check và Freshness là tín hiệu cảnh báo sớm trước khi chất lượng của RAG Agent bị ảnh hưởng tiêu cực trên thực tế.
3. **Đánh giá RAG đa khía cạnh:** `retrieval_hit_rate` cao không đồng nghĩa với câu trả lời của Agent sẽ tốt nếu chất lượng thông tin (summary/content) bên trong dữ liệu bị biến dạng.

### Nếu có thêm thời gian
Tự động hóa hoàn toàn bước **Automated Circuit Breaker** trong pipeline: Khi phát hiện bất kỳ Quality Check nào bị Thất bại (`False`), pipeline sẽ tự động tạm dừng luồng Indexing/RAG và kích hoạt module Repair từ nguồn trước khi cho phép re-evaluate.

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Tiến Đạt  
**Ngày xác nhận:** 2026-08-06
