# Member Role Report — Day 10: Data Pipeline & Data Observability

> Mỗi thành viên trong nhóm tự hoàn thành mẫu này để báo cáo đúng vai trò, phần việc và mức hiểu của mình.

---

# 1. Thông tin cá nhân

| Thông tin | Nội dung |
|-----------|----------|
| Họ và tên | **Bùi Thái Sơn** |
| MSSV | **2A202601126** |
| Khóa/Lớp | **K4** |
| Tên nhóm | **5Bot** |
| Vai trò chính | **Cleaning & Test-set Owner** |
| Repository | https://github.com/ronaldat3737a/K4_Day10_5bot.git |
| Ngày hoàn thành | **2026-08-06** |

---

# 2. Vai trò và phạm vi công việc

## Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
|--------------------|--------------------|----------------|-----------------|------------|
| Data Cleaning | `src/ingestion/cleaning.py` | Raw records từ Crossref API, `run_date` | `papers_clean.json`, `papers_clean.csv` chứa dữ liệu đã chuẩn hóa, `text_for_embedding`, `authors_joined`, `age_days` | ✅ Hoàn thành |
| Evaluation Test Set | `src/evaluation/testset.py` | Cleaned dataset | `test_set.json` gồm question, ground_truth, ground_truth_doc_ids, question_type | ✅ Hoàn thành |

Phần việc của tôi tập trung vào việc đảm bảo dữ liệu sau khi thu thập từ Crossref API được chuẩn hóa đúng Data Contract trước khi chuyển sang bước Embedding và Retrieval. Ngoài ra tôi chịu trách nhiệm xây dựng bộ Evaluation Set thống nhất để sử dụng cho cả ba giai đoạn Baseline, Corrupted và Repaired.

## Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
|-----------|-------------------------------|---------|
| Debug pipeline | Toàn bộ nhóm | Kiểm tra dữ liệu sau Cleaning, đối chiếu số lượng records và artifact với các thành viên khác trước khi build ChromaDB |
| Integration testing | Embedding, Evaluation | Kiểm tra dữ liệu đầu vào của module Embedding và Evaluation, đảm bảo format thống nhất |
| Documentation | Nhóm | Hỗ trợ mô tả quy trình Cleaning, Test Set và hoàn thiện báo cáo |

---

# 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
|-----------------------|----------------------------|------------------|---------------|
| Xây dựng Data Cleaning Pipeline | `src/ingestion/cleaning.py`, `data/clean/papers_clean.json`, `data/clean/papers_clean.csv` | Chuẩn hóa dữ liệu Crossref, loại bỏ các bản ghi không hợp lệ, sinh các trường `authors_joined`, `text_for_embedding`, `age_days`; kết quả còn **24 bản ghi hợp lệ** | Chạy `python script/run_phase1.py`, kiểm tra `papers_clean.json`, `papers_clean.csv` |
| Xây dựng Evaluation Test Set | `src/evaluation/testset.py`, `data/eval/test_set.json` | Sinh **30 câu hỏi** đánh giá với đầy đủ `ground_truth_doc_ids` và `question_type`; sử dụng thống nhất cho Baseline, Corrupted và Repaired | Kiểm tra `test_set.json` và pipeline Evaluation chạy thành công |

---

# 4. Giải thích phần kỹ thuật đã thực hiện

## Vấn đề cần giải quyết

Nguồn dữ liệu từ Crossref API chứa nhiều trường dữ liệu không đồng nhất như thiếu DOI, thiếu Title, Abstract chứa thẻ XML và định dạng ngày chưa thống nhất. Nếu đưa trực tiếp vào Embedding sẽ làm giảm chất lượng Retrieval và gây sai lệch kết quả Evaluation. Vì vậy cần xây dựng quy trình Cleaning để chuẩn hóa dữ liệu và tạo bộ Test Set cố định phục vụ đánh giá khách quan.

## Cách triển khai

### Cleaning

- Loại bỏ các bản ghi không có DOI hoặc Title.
- Loại bỏ các thẻ XML/HTML trong trường Summary (ví dụ `<jats:p>`).
- Chuẩn hóa ngày xuất bản về định dạng `YYYY-MM-DD`.
- Ghép danh sách tác giả thành trường `authors_joined`.
- Tạo trường `text_for_embedding` theo cấu trúc:

```text
Title: {title}
Authors: {authors_joined}
Published: {published}
Summary: {summary}
```

- Tính trường `age_days` từ thời điểm chạy pipeline để phục vụ Freshness Monitoring.

### Test Set

- Sinh bộ gồm **30 câu hỏi** đánh giá.
- Mỗi câu hỏi gồm:
  - `question`
  - `ground_truth`
  - `ground_truth_doc_ids`
  - `question_type`
- Giữ nguyên bộ Test Set cho Baseline, Corrupted và Repaired nhằm đảm bảo mọi thay đổi về metric đều xuất phát từ chất lượng dữ liệu thay vì thay đổi dữ liệu đánh giá.

## Input, Output và Contract

| Thành phần | Mô tả |
|------------|------|
| Input | Raw records từ Crossref API và `run_date` |
| Output | `papers_clean.json`, `papers_clean.csv`, `test_set.json` |
| Module phụ thuộc | Module Ingestion |
| Module sử dụng Output | Embedding, Retrieval, Evaluation, Observability |
| Điều kiện lỗi cần xử lý | Thiếu DOI, thiếu Title, XML trong Summary, sai định dạng ngày, dữ liệu trùng lặp |

## Cách xác minh

```bash
python script/run_phase1.py
```

**Kết quả mong đợi**

- Sinh thành công `papers_clean.json`.
- Sinh thành công `papers_clean.csv`.
- Sinh thành công `test_set.json`.
- Không phát sinh exception.

**Kết quả thực tế**

- Pipeline chạy thành công.
- Thu được **24 bản ghi** sau Cleaning.
- Sinh **30 câu hỏi** trong Evaluation Set.

**Artifact**

- `data/clean/papers_clean.json`
- `data/clean/papers_clean.csv`
- `data/eval/test_set.json`

---

# 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Trong quá trình xây dựng Data Cleaning, nhóm cần quyết định nội dung nào sẽ được sử dụng để tạo trường `text_for_embedding`. Đây là trường đầu vào trực tiếp của mô hình Embedding nên ảnh hưởng lớn đến chất lượng Retrieval.

- **Các phương án đã cân nhắc:**
  1. Chỉ sử dụng **Title**.
  2. Kết hợp **Title + Summary**.
  3. Kết hợp **Title + Authors + Published + Summary**.

- **Phương án đã chọn:** Kết hợp **Title + Authors + Published + Summary**.

- **Lý do:**  
  - Title giúp mô hình nhận diện chủ đề chính của bài báo.
  - Authors và Published bổ sung metadata quan trọng cho các truy vấn theo tác giả hoặc thời gian.
  - Summary cung cấp phần lớn thông tin ngữ nghĩa của tài liệu.
  - Việc kết hợp cả metadata và nội dung giúp Vector Embedding biểu diễn tài liệu đầy đủ hơn so với chỉ sử dụng một trường riêng lẻ.

- **Bằng chứng quyết định phù hợp:**  
  Sau khi xây dựng dữ liệu theo cấu trúc trên, hệ thống Baseline đạt:

  - `retrieval_hit_rate = 1.000`
  - `judge_accuracy = 0.867`
  - `mean_judge_score = 4.133`

  Điều này cho thấy dữ liệu sau Cleaning đáp ứng tốt yêu cầu Retrieval và Question Answering.

---

# 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:**

```text
AttributeError: 'str' object has no attribute 'embed_query'

ValidationError

RateLimitError: 429 Too Many Requests
```

- **Lệnh hoặc bước tái hiện:**

```bash
python script/run_corruption_flow.py
```

- **Nguyên nhân gốc:**

  Trong quá trình tích hợp Ragas Evaluation, lớp Embedding chưa hoàn toàn tương thích với interface của LangChain Embeddings. Đồng thời Ragas mặc định chạy đa luồng nên gửi nhiều request đồng thời tới LLM API công cộng, dẫn đến vượt giới hạn Rate Limit.

- **Cách xử lý:**

  - Đổi biến lưu mô hình SentenceTransformer từ

    ```python
    self.model
    ```

    thành

    ```python
    self._model
    ```

    và khai báo

    ```python
    self.model = model_name
    ```

  - Cấu hình Ragas chạy đơn luồng:

    ```python
    RunConfig(
        max_workers=1,
        max_retries=15
    )
    ```

- **Cách xác minh sau khi sửa:**

  - Chạy lại:

    ```bash
    python script/run_corruption_flow.py
    ```

  - Pipeline hoàn thành thành công.
  - Sinh đầy đủ các báo cáo:
    - `baseline_metrics.json`
    - `corrupted_metrics.json`
    - `corruption_comparison.md`
  - Không còn xuất hiện lỗi `embed_query` hoặc `429 Too Many Requests`.

- **Điều học được:**

  Khi tích hợp nhiều framework khác nhau, cần tuân thủ đúng interface mà framework yêu cầu. Ngoài ra cần kiểm soát số lượng request gửi tới LLM API để tránh lỗi Rate Limit trong các pipeline đánh giá tự động.

---

# 7. Hiểu biết về luồng end-to-end

Giải thích ngắn gọn bằng lời của bạn:

### 1. Dữ liệu đi từ Crossref đến Vector Index như thế nào?

Crossref API được sử dụng để thu thập dữ liệu bài báo khoa học và lưu thành dữ liệu Raw. Sau đó module Cleaning chuẩn hóa dữ liệu, loại bỏ bản ghi không hợp lệ, tạo các trường `authors_joined`, `text_for_embedding` và `age_days`. Dữ liệu đã làm sạch được đưa vào mô hình `all-MiniLM-L6-v2` để tạo Vector Embedding và lưu vào ChromaDB phục vụ Retrieval.

### 2. Evaluation Set và Ground Truth Document IDs dùng để đo Retrieval/Answer Quality như thế nào?

Evaluation Set gồm 30 câu hỏi cùng với `ground_truth_doc_ids` tương ứng. Khi hệ thống Retrieval trả về Top-K tài liệu, chỉ số `retrieval_hit_rate` được tính dựa trên việc tài liệu đúng có xuất hiện trong kết quả hay không. Sau đó câu trả lời của Agent được đánh giá bằng Token F1, LLM Judge và Ragas để đo chất lượng Answer.

### 3. Quality Checks khác Freshness Monitoring ở điểm nào?

Quality Checks đánh giá chất lượng nội tại của dữ liệu như Completeness, Validity, Uniqueness và Text Quality. Freshness Monitoring chỉ tập trung đánh giá mức độ cập nhật của dữ liệu thông qua thời gian xuất bản và `age_days` để xác định trạng thái Fresh hoặc Stale.

### 4. Vì sao phải dùng cùng Test Set cho Baseline, Corrupted và Repaired?

Việc sử dụng cùng một Test Set giúp đảm bảo mọi thay đổi về Metric đều đến từ chất lượng dữ liệu chứ không phải do thay đổi câu hỏi đánh giá. Điều này giúp việc so sánh giữa ba trạng thái khách quan và có ý nghĩa.

### 5. Repair được xem là thành công dựa trên Artifact và Metric nào?

Repair được xem là thành công khi:

- Retrieval Hit Rate phục hồi từ **0.833** lên **1.000**.
- Judge Accuracy phục hồi từ **0.433** lên **0.867**.
- Mean Judge Score phục hồi từ **2.267** lên **4.133**.
- Quality Checks trở lại **Pass (4/4)**.
- Freshness chuyển từ **Stale** về **Fresh**.
- Các artifact như `papers_clean.json`, `baseline_quality.json` và `corruption_comparison.md` được tạo đầy đủ.

---

# 8. Phân tích kết quả

## Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
|----------------------|---------:|----------:|---------:|-----------------------------|
| `retrieval_hit_rate` | **1.000** | **0.833** | **1.000** | Corruption làm mất một phần tài liệu nên khả năng truy xuất giảm; sau Repair chỉ số phục hồi hoàn toàn. |
| `mean_token_f1` | **0.145** | **0.082** | **0.145** | F1 giảm do dữ liệu bị thiếu và chứa nhiễu; sau Repair trở về mức ban đầu. |
| `judge_accuracy` | **0.867** | **0.433** | **0.867** | Chất lượng câu trả lời giảm gần một nửa khi dữ liệu bị hỏng và phục hồi hoàn toàn sau Repair. |
| `mean_judge_score` | **4.133** | **2.267** | **4.133** | LLM Judge đánh giá thấp khi dữ liệu bị Corruption, sau Repair trở lại mức Baseline. |
| Quality checks | **Pass (4/4)** | **Fail (1/4)** | **Pass (4/4)** | Corruption làm vi phạm Completeness, Validity và Freshness; Repair khôi phục toàn bộ. |
| Freshness status | **Fresh** | **Stale** | **Fresh** | Xóa các bản ghi mới nhất khiến dữ liệu trở nên Stale; Repair khôi phục trạng thái Fresh. |

---

## Kết luận từ số liệu

Hoàn thành hai chuỗi nguyên nhân – bằng chứng sau:

### 1.

**Data corruption:** Xóa các bản ghi mới nhất và làm rỗng trường Summary

↓

**Quality check:** Completeness thất bại, Freshness chuyển từ Fresh sang Stale

↓

**Agent metric:** `retrieval_hit_rate` giảm từ **1.000** xuống **0.833**, `judge_accuracy` giảm từ **0.867** xuống **0.433**.

---

### 2.

**Repair action:** Thực hiện Re-Ingest từ dữ liệu Raw, áp dụng lại toàn bộ quy tắc Cleaning và Build lại ChromaDB

↓

**Quality check:** Toàn bộ Quality Checks đạt **Pass (4/4)**, Freshness trở lại trạng thái Fresh

↓

**Agent metric:** `retrieval_hit_rate`, `judge_accuracy` và `mean_judge_score` phục hồi hoàn toàn về mức Baseline.

---

### Corruption nào ảnh hưởng rõ nhất và vì sao?

Theo mình, **Drop Latest Records** là kịch bản ảnh hưởng mạnh nhất vì làm mất trực tiếp các tài liệu mới nhất trong Vector Store. Khi tài liệu nguồn không còn tồn tại, Retrieval không thể trả về đúng tài liệu cho một số câu hỏi, dẫn đến `retrieval_hit_rate` giảm từ **1.000** xuống **0.833**. Điều này kéo theo chất lượng câu trả lời giảm mạnh và làm `judge_accuracy` chỉ còn **0.433**.

---

### Kết quả nào khác với kỳ vọng ban đầu?

Ban đầu mình dự đoán Corruption chỉ làm giảm nhẹ chất lượng Retrieval. Tuy nhiên kết quả thực tế cho thấy chất lượng Answer giảm mạnh hơn mong đợi khi `judge_accuracy` giảm gần 50% và `mean_judge_score` giảm từ **4.133** xuống **2.267**. Điều này cho thấy chất lượng dữ liệu đầu vào ảnh hưởng trực tiếp đến hiệu quả của toàn bộ hệ thống RAG. Sau khi thực hiện Repair, tất cả các chỉ số đều phục hồi về đúng mức Baseline, chứng minh quy trình Repair hoạt động hiệu quả.

---

# 9. Điều học được và hướng cải thiện

## Ba điều quan trọng nhất

### 1. Điều học được về Data Pipeline

Một Data Pipeline tốt không chỉ thu thập dữ liệu mà còn phải chuẩn hóa, kiểm tra chất lượng và xây dựng Data Contract rõ ràng. Nếu dữ liệu đầu vào không được làm sạch thì toàn bộ các bước Embedding, Retrieval và Evaluation đều bị ảnh hưởng.

### 2. Điều học được về Data Quality và Observability

Data Quality và Data Observability giúp phát hiện sớm các vấn đề như thiếu dữ liệu, dữ liệu lỗi hoặc dữ liệu quá cũ trước khi chúng ảnh hưởng đến chất lượng của hệ thống AI. Việc theo dõi đồng thời Completeness, Validity, Uniqueness và Freshness giúp quá trình vận hành ổn định hơn.

### 3. Điều học được về ảnh hưởng của Data đến RAG Agent

Hiệu năng của RAG Agent phụ thuộc trực tiếp vào chất lượng dữ liệu. Khi dữ liệu bị Corruption, các chỉ số Retrieval và Answer Quality đều giảm đáng kể. Ngược lại, khi dữ liệu được Repair đúng cách, toàn bộ hiệu năng của hệ thống có thể phục hồi về mức ban đầu.

---

## Nếu có thêm thời gian

Nếu có thêm thời gian, mình muốn bổ sung cơ chế **Data Drift Monitoring** và **Automatic Quality Alert** để hệ thống tự động phát hiện dữ liệu bất thường trong quá trình Ingestion. Khi một Quality Check vượt ngưỡng cho phép hoặc Freshness chuyển sang trạng thái Stale, hệ thống sẽ gửi cảnh báo và kích hoạt quy trình Repair tự động. Hiệu quả của cải tiến này có thể được đánh giá bằng thời gian phát hiện lỗi, thời gian khôi phục hệ thống và mức độ ổn định của các chỉ số Retrieval sau nhiều lần cập nhật dữ liệu.

---

# 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi "đã chạy thành công" cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

---

**Họ và tên:** **Bùi Thái Sơn**

**Ngày xác nhận:** **2026-08-06**