# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin       | Nội dung                                            |
| --------------- | --------------------------------------------------- |
| Họ và tên       | Nguyễn Công Đạt                                     |
| MSSV            | 2A202601526                                         |
| Khóa/Lớp        | K4                                                  |
| Tên nhóm        | 5bot                                                |
| Vai trò chính   | Source Owner (Thành viên 1)                         |
| Repository      | https://github.com/ronaldat3737a/K4_Day10_D304_5bot |
| Ngày hoàn thành | 2026-08-06                                          |

---

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable                    | File/hàm phụ trách                                     | Input nhận vào                                          | Output bàn giao                                          | Trạng thái |
| ------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------- | -------------------------------------------------------- | ---------- |
| Giao tiếp API Crossref và tải dữ liệu | `src/ingestion/crossref.py` (`fetch_source_records`)   | `settings.source_query`, `source_filter`, `max_results` | File JSON `data/raw/raw_api_response.json`               | Hoàn thành |
| Trích xuất và chuẩn hóa Schema gốc    | `src/ingestion/crossref.py` (`parse_crossref_payload`) | Payload JSON từ API                                     | File `data/raw/raw_records.json` chứa list `PaperRecord` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động                      | Thành viên/module được hỗ trợ | Kết quả                                                                                                          |
| ------------------------------ | ----------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Thống nhất Contract Schema gốc | Thành viên 2 (`cleaning.py`)  | Chốt cấu trúc `PaperRecord`, xử lý fallback các trường thiếu (như `abstract`, ngày tháng mặc định `0000-01-01`). |

---

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện           | File/hàm/artifact liên quan | Kết quả bàn giao                 | Cách xác minh                                                                                                         |
| ------------------------------- | --------------------------- | -------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Lấy dữ liệu API có cơ chế Retry | `src/ingestion/crossref.py` | `data/raw/raw_api_response.json` | [Commit 976f617](https://github.com/ronaldat3737a/K4_Day10_D304_5bot/commit/976f6176c691d385596854d9fe9d1a6cef472cdb) |
| Parse metadata từ JSON lộn xộn  | `src/ingestion/crossref.py` | `data/raw/raw_records.json`      | Chạy pipeline không lỗi, ra đúng định dạng `YYYY-MM-DD`.                                                              |

### Output cụ thể

Pipeline đã tự động tải thành công dữ liệu từ hệ thống Crossref và lưu dưới dạng list các đối tượng trong `data/raw/raw_records.json`.

Đây là artifact nền tảng, tạo đầu vào đạt chuẩn Schema (với các trường ID, Title, Summary, Date) để module `cleaning.py` thực hiện tiền xử lý.

Toàn bộ code xử lý đã được push tại [commit 976f617](https://github.com/ronaldat3737a/K4_Day10_D304_5bot/commit/976f6176c691d385596854d9fe9d1a6cef472cdb).

---

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Lấy dữ liệu từ nguồn API Crossref rất dễ bị ngắt kết nối hoặc từ chối phục vụ (Rate Limit).

Ngoài ra, cấu trúc JSON trả về của Crossref rất sâu, nhiều biến thể (ví dụ: ngày tháng có thể nằm ở `published-print`, `published-online` hoặc `created`), đòi hỏi phải viết logic fallback cẩn thận để không bị mất dữ liệu metadata quan trọng của bài báo.

### Cách triển khai

- **Về gọi API:** Tôi khởi tạo một `requests.Session()` và mount cấu hình `urllib3.util.retry.Retry` vào session này. Cấu hình sẽ tự động retry tối đa 3 lần với `backoff_factor=1` khi gặp đúng mã lỗi 429 hoặc 503, giúp vượt qua rào cản Rate Limit an toàn.
- **Về Parsing:** Quét qua `payload["message"]["items"]`. Bỏ qua các record không có `DOI`. Ở trường tác giả, thực hiện ghép chuỗi `given` và `family`. Với ngày tháng, tôi viết vòng lặp kiểm tra theo thứ tự ưu tiên (`published-print`, `published-online`, `created`) và format chặt chẽ về định dạng `YYYY-MM-DD` bằng cú pháp format string `{:02d}`.

### Input, output và contract

| Thành phần              | Mô tả                                                                                                           |
| ----------------------- | --------------------------------------------------------------------------------------------------------------- |
| Input                   | `Settings` object cấu hình các tham số tìm kiếm API.                                                            |
| Output                  | Danh sách các đối tượng `PaperRecord` đã parse sơ bộ.                                                           |
| Module phụ thuộc        | `core/config.py`.                                                                                               |
| Module sử dụng output   | `src/ingestion/cleaning.py` (Làm sạch tag HTML trong abstract).                                                 |
| Điều kiện lỗi cần xử lý | Bắt HTTP Error 429, 503; bỏ qua bản ghi nếu thiếu `DOI`; xử lý lỗi `KeyError` khi API trả thiếu trường dữ liệu. |

### Cách xác minh

```bash
uv run python script/run_phase1.py
```

**Kết quả mong đợi:**

Code chạy không bị gián đoạn, sinh ra 2 file JSON lưu trong `data/raw/`.

**Kết quả thực tế:**

Dữ liệu được fetch thành công, cơ chế retry hoạt động ngầm. Các ngày tháng của báo được chuẩn hóa đúng `YYYY-MM-DD`.

**Artifact/log:**

File `data/raw/raw_records.json` có dữ liệu hợp lệ.

**Tham chiếu:** Commit `976f617`.

---

## 5. Một quyết định kỹ thuật quan trọng

### Bối cảnh

Cần xử lý tình trạng API Crossref trả về lỗi `429 Too Many Requests`.

### Các phương án đã cân nhắc

1. Bọc hàm `requests.get` trong vòng lặp `while/try-except` và dùng `time.sleep()`.
2. Sử dụng `urllib3.util.retry.Retry` gắn vào `requests.Session()`.

### Phương án đã chọn

**Phương án 2.**

### Lý do

Trade-off về độ phức tạp và correctness.

Sử dụng bộ Retry tích hợp sẵn của urllib3 mang lại code sạch, an toàn hơn và quản lý exponential backoff tự động chuẩn xác mà không cần quản lý biến đếm số lần lặp thủ công.

### Bằng chứng quyết định phù hợp

Code chạy ổn định qua nhiều lần test liên tục, không bị crash giữa chừng.

---

## 6. Một lỗi hoặc blocker đã xử lý

### Triệu chứng/lỗi nguyên văn

Lỗi rỗng dữ liệu ngày tháng hoặc lỗi `KeyError` khi parsing một số bài báo không có ngày xuất bản bản in.

### Lệnh hoặc bước tái hiện

Chạy hàm parse trên một tập dữ liệu lớn lấy ngẫu nhiên từ Crossref.

### Nguyên nhân gốc

Crossref không nhất quán định dạng ngày. Có bài dùng `published-print`, có bài chỉ có `published-online` hoặc `created`.

### Cách xử lý

Thêm logic fallback lặp qua một list các key:

```python
for date_key in ["published-print", "published-online", "created"]:
```

Nếu có `date-parts`, bóc tách năm, tháng, ngày và tự động format `{:02d}` (chèn số 0 nếu là 1 chữ số).

Nếu thiếu tất cả, mặc định là `"0000-01-01"`.

### Cách xác minh sau khi sửa

Check lại file `raw_records.json`, các giá trị `published` và `updated` đều có định dạng chuỗi hợp lệ.

### Điều học được

Không bao giờ tin tưởng hoàn toàn vào Schema của External API; luôn phải chuẩn bị sẵn fallback values.

---

## 7. Hiểu biết về luồng end-to-end

### Dữ liệu đi từ Crossref đến vector index như thế nào?

```text
API
→ Raw JSON
→ Parse lấy các trường cơ bản (DOI, title, abstract...)
→ Làm sạch HTML và null
→ Ghép chuỗi tạo text đại diện
→ Chạy qua Embedding model
→ Index vào ChromaDB
```

### Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?

Hệ thống dùng các bộ câu hỏi chuẩn so khớp với kết quả truy xuất.

Nếu hệ thống RAG tìm đúng `paper_id` của ground-truth, điểm Retrieval tăng.

Dựa trên tài liệu đó, nếu LLM sinh câu trả lời đúng nội dung ground-truth, điểm Answer/Judge Quality tăng.

### Quality checks khác freshness monitoring ở điểm nào trong bài lab?

Quality check soi tính toàn vẹn (Completeness/Validity) như dữ liệu có bị rỗng, null hay sai kiểu không.

Freshness kiểm tra yếu tố thời gian (Currency), ví dụ bài báo có xuất bản quá cũ (trước 5 năm) hay không.

### Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?

Để kiểm soát biến số độc lập.

Nếu dùng test set khác nhau, ta không thể chứng minh sự sụt giảm/tăng lên của metric là do chất lượng dữ liệu hay do câu hỏi thay đổi độ khó.

### Repair được xem là thành công dựa trên artifact và metric nào?

Repair thành công khi dữ liệu được khôi phục từ nguồn raw, đi qua toàn bộ pipeline và tạo ra tập metrics (`repaired_metrics.json`) có các chỉ số tương đương hoặc khôi phục hoàn toàn so với baseline.

---

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
|---|---:|---:|---:|---|
| `retrieval_hit_rate` | **1.000** | **0.833** | **1.000** | Corruption làm mất một phần tài liệu nên khả năng truy xuất giảm; sau Repair chỉ số phục hồi hoàn toàn. |
| `mean_token_f1` | **0.145** | **0.082** | **0.145** | F1 giảm do dữ liệu bị thiếu và chứa nhiễu; sau Repair trở về mức ban đầu. |
| `judge_accuracy` | **0.867** | **0.433** | **0.867** | Chất lượng câu trả lời giảm gần một nửa khi dữ liệu bị hỏng và phục hồi hoàn toàn sau Repair. |
| `mean_judge_score` | **4.133** | **2.267** | **4.133** | LLM Judge đánh giá thấp khi dữ liệu bị Corruption, sau Repair trở lại mức Baseline. |
| Quality checks | **Pass (4/4)** | **Fail (1/4)** | **Pass (4/4)** | Corruption làm vi phạm Completeness, Validity và Freshness; Repair khôi phục toàn bộ. |
| Freshness status | **Fresh** | **Stale** | **Fresh** | Xóa các bản ghi mới nhất khiến dữ liệu trở nên Stale; Repair khôi phục trạng thái Fresh. |

---

### Kết luận từ số liệu

Hoàn thành hai chuỗi nguyên nhân – bằng chứng sau:

#### 1. Data corruption → Quality check → Agent metric

**Data corruption:** Xóa các bản ghi mới nhất và làm rỗng trường `Summary`

↓

**Quality check:** `Completeness` thất bại, `Freshness` chuyển từ `Fresh` sang `Stale`

↓

**Agent metric:** `retrieval_hit_rate` giảm từ **1.000** xuống **0.833**, `judge_accuracy` giảm từ **0.867** xuống **0.433**.

---

#### 2. Repair action → Quality check → Agent metric

**Repair action:** Thực hiện Re-Ingest từ dữ liệu Raw, áp dụng lại toàn bộ quy tắc Cleaning và Build lại ChromaDB

↓

**Quality check:** Toàn bộ Quality Checks đạt **Pass (4/4)**, `Freshness` trở lại trạng thái `Fresh`

↓

**Agent metric:** `retrieval_hit_rate`, `judge_accuracy` và `mean_judge_score` phục hồi hoàn toàn về mức Baseline.

---

### Corruption nào ảnh hưởng rõ nhất và vì sao?

Theo mình, **Drop Latest Records** là kịch bản ảnh hưởng mạnh nhất vì làm mất trực tiếp các tài liệu mới nhất trong Vector Store.

Khi tài liệu nguồn không còn tồn tại, Retrieval không thể trả về đúng tài liệu cho một số câu hỏi, dẫn đến `retrieval_hit_rate` giảm từ **1.000** xuống **0.833**.

Điều này kéo theo chất lượng câu trả lời giảm mạnh và làm `judge_accuracy` chỉ còn **0.433**.

---

### Kết quả nào khác với kỳ vọng ban đầu?

Ban đầu mình dự đoán Corruption chỉ làm giảm nhẹ chất lượng Retrieval. Tuy nhiên, kết quả thực tế cho thấy chất lượng Answer giảm mạnh hơn mong đợi khi `judge_accuracy` giảm gần 50% và `mean_judge_score` giảm từ **4.133** xuống **2.267**.

Điều này cho thấy chất lượng dữ liệu đầu vào ảnh hưởng trực tiếp đến hiệu quả của toàn bộ hệ thống RAG.

Sau khi thực hiện Repair, tất cả các chỉ số đều phục hồi về đúng mức Baseline, chứng minh quy trình Repair hoạt động hiệu quả.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

**Về data pipeline:**
Lấy API phải luôn đi kèm cơ chế Retry/Backoff (như `urllib3.util.retry`) vì network error là điều luôn xảy ra.

**Về data quality/observability:**
Xử lý và bắt lỗi từ khâu JSON sơ cấp (như việc bắt lỗi `KeyError` cho ngày tháng) giúp tiết kiệm cực nhiều rủi ro ở các khâu sau.

**Về ảnh hưởng của data đến RAG agent:**
RAG tuân thủ quy tắc "Garbage in, Garbage out". Dữ liệu gốc (Source Data) chính là mạch máu quyết định độ thông minh của LLM.

### Nếu có thêm thời gian

Tôi sẽ cấu hình thêm parameter:

```python
headers={
    "User-Agent": "mailto:email_cua_nhom@example.com"
}
```

truyền vào `requests.Session()`.

Crossref có chính sách Polite Pool ưu tiên băng thông cho các request có khai báo danh tính. Thêm thông tin này sẽ giảm đáng kể tỷ lệ gặp mã lỗi 429 và tăng tốc độ Fetch Pipeline.

---

## 10. Cam kết của thành viên

### Đánh dấu sau khi tự kiểm tra

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Công Đạt

**Ngày xác nhận:** 2026-08-06
