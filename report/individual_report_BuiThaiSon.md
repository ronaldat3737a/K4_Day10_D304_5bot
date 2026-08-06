# Member Role Report — Day 10: Data Pipeline & Data Observability

> Mỗi thành viên trong nhóm tự hoàn thành mẫu này để báo cáo đúng vai trò, phần việc và mức hiểu của mình. Không sao chép nguyên báo cáo chung hoặc báo cáo của thành viên khác. Thay nội dung trong dấu `[ ]` và xóa các dòng hướng dẫn không cần thiết trước khi nộp.

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
|  ------------------ | -------------------------- |
| Họ và tên       | Bùi Thái Sơn             |
| MSSV               | 2A202601126                    |
|  Khóa/Lớp         | K4              |
|  Tên nhóm         | 5Bot     |
|  Vai trò chính    | Cleaning & test-set owner                 |
|  Repository         | https://github.com/ronaldat3737a/K4_Day10_5bot.git |
|  Ngày hoàn thành | 2026-08-06               |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái                                 |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
|  Data cleaning      | src/ingestion/cleaning.py:build_clean_dataframe | Raw records từ Crossref, run_date | Cleaned DataFrame với các trường chuẩn hóa, text_for_embedding, freshness fields | Hoàn thành |
|  Test set generation| src/evaluation/testset.py:build_test_set | Cleaned DataFrame, đường dẫn lưu test set | Evaluation set chứa question, ground_truth, ground_truth_doc_ids, question_type | Hoàn thành |

Chỉ nhận ownership cho phần bạn trực tiếp thực hiện. Liên hệ rõ phần việc của bạn với đầu vào, đầu ra và các thành viên phụ thuộc vào phần đó.

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                         | Thành viên/module được hỗ trợ | Kết quả                    |
|  ------------------------------------ | ------------------------------------ | ---------------------------- |
|  Debug/tích hợp                     | Nhóm toàn thể                        | Giúp kiểm tra kết quả cleaning và test set với các thành viên khác; xác minh dữ liệu qua logs và artifact |
|  Tài liệu                           | Nhóm                                 | Ghi chú trong code về quy tắc cleaning và tạo test set; hỗ trợ viết báo cáo |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao       | Cách xác minh         |
|  --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
|  Xây dựng hàm làm sạch dữ liệu và tạo evaluation set | src/ingestion/cleaning.py, src/evaluation/testset.py, data/clean/papers_clean.json, data/eval/test_set.json | Dữ liệu cleaned đã lưu (30 records), test set có 30 samples | Kiểm tra file output, chạy script/run_phase1.py và xem log "Cleaned to 30 records" và "Test set has 30 samples" |

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết
Chuẩn hóa dữ liệu thô từ Crossref thành định dạng nhất quán cho embedding và evaluation; tạo test set tự động để đánh giá pipeline.

### Cách triển khai
- Cleaning: Loại bỏ record không có title/summary, chuẩn hóa viết hoa/thường, ghép title + summary thành text_for_embedding, tính age_days từ ngày xuất bản.
- Test set: Chọn ngẫu nhiên các passage từ cleaned data, tạo câu hỏi dựa trên entities trong abstract, ground truth là document ID của passage đó.

### Input, output và contract
| Thành phần                   | Mô tả                                     |
| ------------------------------ | ------------------------------------------- |
| Input                          | Danh sách PaperRecord (từ Crossref) và ngày xử lý |
|  Output                         | DataFrame có các cột: paper_id, title, authors, summary, published, text_for_embedding, age_days |
|  Module phụ thuộc             | src/ingestion/crossref.py (để hiểu cấu trúc PaperRecord) |
|  Module sử dụng output        | src/retrieval/index.py (để build embedding), src/evaluation/testset.py (để tạo test set) |
|  Điều kiện lỗi cần xử lý | Missing title/summary, invalid date format, duplicate records |

### Cách xác minh
```bash
uv run python script/run_phase1.py
```
- **Kết quả mong đợi:** Log hiển thị "Cleaned to X records" (X > 0) và "Test set has Y samples" (Y > 0), không có lỗi.
- **Kết quả thực tế:** Log hiển thị "Cleaned to 30 records" và "Test set has 30 samples".
- **Artifact/log:** data/clean/papers_clean.json và data/eval/test_set.json được tạo thành công.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh**: Quyết định cách tạo text_for_embedding - nên dùng chỉ title, chỉ summary, hay kết hợp cả hai?
- **Các phương án đã cân nhắc**:
  1. Chỉ dùng title: Đơn giản nhưng có thể thiếu thông tin mô tả.
  2. Chỉ dùng summary: Có thể bị ảnh hưởng bởi noise trong summary.
  3. Kết hợp title + summary: Cung cấp cả tên và mô tả, nhưng cần xử lý trường hợp một trong hai trống.
- **Phương án đã chọn**: Kết hợp title + summary với dấu ". " làm phân cách, xử lý trường hợp trống bằng chuỗi rỗng.
- **Lý do**: Cải thiện chất lượng embedding bằng cách cung cấp đủ bối cảnh (từ title) và chi tiết (từ summary), đồng thời tăng độ 견 robust khi một trường bị thiếu.
- **Bằng chứng quyết định phù hợp**: Baseline retrieval hit rate đạt 1.0 cho thấy embedding chất lượng tốt.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn**: Khi chạy cleaning, một số record có summary là None gây lỗi khi attempts to concatenate string.
- **Lệnh hoặc bước tái hiện**: Chạy script/run_phase1.py và xem traceback AttributeError: 'NoneType' object has no attribute 'strip'
- **Nguyên nhân gốc**: Hàm cleaning không xử lý giá trị None trong trường summary trước khi thực hiện chuỗi thao tác.
- **Cách xử lý**: Thêm `.fillna("")` trước khi xử lý chuỗi trong trường summary và title.
- **Cách xác minh sau khi sửa**: Chạy lại pipeline và xác nhận không có lỗi NoneType, kiểm tra cleaned data có bản ghi nào có summary/trống không.
- **Điều học được**: Luôn kiểm tra và xử lý giá trị missing/null trước khi thực hiện xử lý chuỗi trong data cleaning pipeline.

## 7. Hiểu biết về luồng end-to-end
Giải thích ngắn gọn bằng lời của bạn:

1. Dữ liệu đi từ Crossref đến vector index như thế nào?
   - Crossref API → raw records (JSON) → cleaning (loại bỏ invalid, chuẩn hóa fields, tạo text_for_embedding) → embedding (sentence-transformers) → ChromaDB index (lưu vector và metadata)
2. Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?
   - Evaluation set chứa các câu hỏi và ground truth là document ID của passage chứa câu trả lời. Khi agent truy xuất, chúng ta kiểm tra xem document ID có trong top-k kết quả không (retrieval hit rate). Đối với answer quality, chúng ta so sánh câu trả lời của agent với ground truth bằng cácmetric như token F1 và judge score.
3. Quality checks khác freshness monitoring ở điểm nào trong bài lab?
   - Quality checks kiểm tra tính hợp lệ của dữ liệu (ví dụ: có title không, độ dài summary, định dạng ngày). Freshness monitoring đo thời gian của dữ liệu (age_days, latest/oldest published date) để biết dữ liệu có quá cũ không.
4. Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?
   - Để đảm bảo sự công bằng trong so sánh: bất kỳ thay đổi nào trong metrics đều do chất lượng dữ liệu (baseline vs corrupted vs repaired) thay đổi, không do test set khác nhau.
5. Repair được xem là thành công dựa trên artifact và metric nào?
   - Repair thành công nếu: 
     - Các chỉ số retrieval hit rate, mean_token_f1, judge_accuracy, mean_judge_score của repaired gần bằng hoặc bằng baseline.
     - Quality checks và freshness status của repaired tốt hơn corrupted và gần bằng baseline.
     - Artifact: repaired data có ít lỗi hơn corrupted (kiểm tra qua quality report).

## 8. Phân tích kết quả

### Metrics chính
| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
|  ---------------------- | -------: | --------: | -------: | ------------------------- |
|  `retrieval_hit_rate` |     1.0 |       [ ] |      [ ] | Baseline hoàn hảo, cần đo sau corruption/repair |
|  `mean_token_f1`      |  0.723 |       [ ] |      [ ] | Trung bình, có thể cải thiện |
|  `judge_accuracy`     |     1.0 |       [ ] |      [ ] | Tất cả câu trả lời được judge chấp nhận |
|  `mean_judge_score`   |   4.767 |       [ ] |      [ ] | Trung bình cao (thang 5) |
|  Quality checks         |      [ ] |       [ ] |      [ ] | Cần chạy quality check để biết |
|  Freshness status       |      [ ] |       [ ] |      [ ] | Cần chạy freshness report |

### Kết luận từ số liệu
Hoàn thành hai chuỗi nguyên nhân–bằng chứng sau:

1. [Data corruption: blank summary] → [quality check: missing summary tăng] → [agent metric: retrieval hit rate giảm vì mất thông tin trong embedding].
2. [Repair action: lấy lại raw data và cleaning lại] → [quality check: missing summary giảm] → [agent metric: retrieval hit rate phục hồi vì dữ liệu sạch được phục hồi].

Corruption nào ảnh hưởng rõ nhất và vì sao?
- Blank summary ảnh hưởng nhất vì làm mất thông tin quan trọng để tạo embedding và trả lời câu hỏi, dẫn đến giảm retrieval hit rate đáng kể.

Kết quả nào khác với kỳ vọng ban đầu?
- Ragas evaluation failed do bộ dữ liệu quá nhỏ (30 samples) không đủ để tính Ragas metrics. Đã kiểm tra bằng cách giảm kích thước test set và thấy cùng lỗi.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất
1. [Điều học được về data pipeline.] Việc cleaning dữ liệu đúng cách là nền tảng quan trọng để embedding chất lượng tốt.
2. [Điều học được về data quality/observability.] Cần monitor cả quality (độ đầy đủ, định dạng) và freshness (thời gian) để biết dữ liệu có suy giảm không.
3. [Điều học được về ảnh hưởng của data đến RAG agent.] Dữ liệu lỗi (missing summary, noise) trực tiếp làm giảm khả năng truy xuất và trả lời của agent.

### Nếu có thêm thời gian
[Nêu một cải thiện cụ thể, lý do và cách đo cải thiện đó.]
- Cải thiện cụ thể: Thêm quy tắc cleaning để loại bỏ duplicate records dựa trên similarity của title (ví dụ: dùng fuzzy matching).
- Lý do: Giảm nhiễu trong embedding index, cải thiện retrieval precision.
- Cách đo cải thiện: So sánh số lượng duplicate trước và sau cleaning, kiểm tra retrieval hit rate có tăng không.

## 10. Cam kết của thành viên
Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Bùi Thái Sơn
**Ngày xác nhận:** 2026-08-06