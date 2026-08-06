# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Tổng Tiến Mạnh |
| MSSV | 2A202601614 |
| Khóa/Lớp | K4 |
| Tên nhóm | 5Bot |
| Vai trò chính | Observability Owner |
| Repository | https://github.com/ronaldat3737a/K4_Day10_D304_5bot.git |
| Ngày hoàn thành | 2026-08-06 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Data quality checks | src/observability/quality.py -> run_data_quality_checks | DataFrame cleaned/corrupted/repaired và Settings | JSON quality report trong data/quality | Hoàn thành |
| Freshness monitoring | src/observability/quality.py -> build_freshness_report | DataFrame và freshness threshold | JSON freshness report trong data/quality | Hoàn thành |
| Baseline và comparison reporting | src/observability/reporting.py -> generate_phase1_report, generate_corruption_report | Metrics, quality checks, freshness payload | Markdown report trong data/reports | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --- | --- | --- |
| Kiểm tra tích hợp với pipeline | src/pipelines/corruption_flow.py | Đảm bảo observability output được sinh đúng cho baseline, corrupted và repaired |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Triển khai checks chất lượng dữ liệu | src/observability/quality.py | data/quality/baseline_quality.json, corrupted_quality.json, repaired_quality.json | Đọc trực tiếp các file JSON đầu ra |
| Triển khai freshness monitoring | src/observability/quality.py | data/quality/freshness_report.json, corrupted_freshness.json, repaired_freshness.json | Đọc trực tiếp các file JSON đầu ra |
| Tạo báo cáo baseline và so sánh corruption | src/observability/reporting.py | data/reports/phase1_report.md, data/reports/corruption_comparison.md | Đọc các file markdown đã sinh |

Output cụ thể mà phần việc của mình tạo ra là các artifact observability phục vụ cho đánh giá ảnh hưởng của data corruption đến agent và việc repair dữ liệu.

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Cần có một lớp observability để biết dữ liệu có đủ sạch, có duy nhất, có đủ thông tin và có còn mới không trước khi dùng cho RAG. Ngoài ra, cần có báo cáo để chứng minh corruption có làm suy giảm chất lượng dữ liệu và agent như thế nào.

### Cách triển khai

Tôi triển khai các check dựa trên dữ liệu DataFrame và cấu hình settings. Các rule chính gồm:
- kiểm tra số dòng dữ liệu;
- kiểm tra paper_id không null và unique;
- kiểm tra title không null;
- kiểm tra summary có đủ dài (độ dài tối thiểu 10 ký tự);
- kiểm tra age_days không âm và nằm trong khoảng hợp lý;
- tính freshness theo published date và freshness_threshold_days để xác định stale record.

Sau đó, các kết quả này được lưu sang JSON để dễ dùng cho pipeline tiếp theo và được tổng hợp thành markdown report cho baseline và compare phase.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | DataFrame đã được clean/corrupted/repaired, Settings chứa freshness threshold |
| Output | JSON quality/freshness reports và markdown report |
| Module phụ thuộc | src/core/config.py, src/ingestion/cleaning.py, src/pipelines/corruption_flow.py |
| Module sử dụng output | src/pipelines/phase1.py, src/pipelines/corruption_flow.py |
| Điều kiện lỗi cần xử lý | Giá trị pandas/numpy không thể serialize trực tiếp sang JSON; cần chuyển về Python native type |

### Cách xác minh

```bash
# Kiểm tra artifact đã sinh
ls data/quality
ls data/reports
```

- Kết quả mong đợi: có các file JSON/Markdown được tạo.
- Kết quả thực tế: đã có các file baseline_quality.json, corrupted_quality.json, repaired_quality.json, freshness_report.json, corrupted_freshness.json, repaired_freshness.json, phase1_report.md và corruption_comparison.md.
- Artifact/log: data/quality và data/reports.

## 5. Một quyết định kỹ thuật quan trọng

- Bối cảnh: cần đánh giá data quality và freshness một cách nhất quán giữa baseline, corrupted và repaired.
- Các phương án đã cân nhắc: chỉ dùng report thủ công, hoặc dùng một lớp checks chuẩn hóa và lưu thành artifact.
- Phương án đã chọn: dùng một bộ checks chuẩn hóa và xuất JSON/Markdown để làm đầu ra reproducible.
- Lý do: cách này dễ so sánh giữa các trạng thái, phù hợp với lab observability, và không phụ thuộc vào việc chạy thủ công bằng tay.
- Bằng chứng quyết định phù hợp: các artifact ở data/quality và data/reports cho thấy baseline và repaired đều đạt quality tốt hơn corrupted.

## 6. Một lỗi hoặc blocker đã xử lý

- Triệu chứng/lỗi nguyên văn: khi ghi JSON report, các giá trị kiểu pandas/numpy hoặc datetime có thể gây lỗi serialize.
- Lệnh hoặc bước tái hiện: chạy pipeline sinh report observability.
- Nguyên nhân gốc: dữ liệu từ DataFrame chưa được chuyển về kiểu Python native trước khi dump sang JSON.
- Cách xử lý: thêm bước convert giá trị sang native type trước khi ghi JSON.
- Cách xác minh sau khi sửa: kiểm tra các file JSON trong data/quality có thể đọc và mở bình thường.
- Điều học được: observability output phải được chuẩn hóa ngay từ đầu để tránh lỗi ở bước downstream.

## 7. Hiểu biết về luồng end-to-end

1. Dữ liệu đi từ Crossref đến vector index như thế nào? Dữ liệu raw được fetch từ Crossref, parse thành PaperRecord, sau đó được clean thành DataFrame, tạo text_for_embedding và lưu vào clean dataset. Từ đó, dữ liệu được dùng để build local embedding index cho retrieval.
2. Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao? Evaluation set chứa các câu hỏi và ground_truth_doc_ids; trong quá trình evaluate, hệ thống lấy câu trả lời từ index và so sánh với ground truth để tính retrieval_hit_rate, token F1, judge accuracy và judge score.
3. Quality checks khác freshness monitoring ở điểm nào trong bài lab? Quality checks đánh giá tính đầy đủ và nhất quán của dữ liệu, còn freshness monitoring đánh giá độ mới của published date so với threshold thời gian.
4. Vì sao phải dùng cùng test set cho baseline, corrupted và repaired? Vì muốn so sánh apples-to-apples: cùng một tập câu hỏi và cùng một ground truth để thấy corruption và repair ảnh hưởng như thế nào đến hiệu năng.
5. Repair được xem là thành công dựa trên artifact và metric nào? Repair được xem là thành công khi dữ liệu repaired phục hồi lại các quality checks, freshness report và các metric evaluation gần về baseline, cụ thể là row_count, paper_id_unique, summary_min_length_10 và các metric như mean_token_f1, judge_accuracy.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| --- | ---: | ---: | ---: | --- |
| retrieval_hit_rate | 1.0000 | 1.0000 | 1.0000 | Retrieval hit rate không bị ảnh hưởng lớn về mặt top-k retrieval trong trường hợp này. |
| mean_token_f1 | 0.7234 | 0.6761 | 0.7214 | Corruption làm giảm token F1, repaired gần như khôi phục về baseline. |
| judge_accuracy | 1.0000 | 0.9000 | 1.0000 | Judge accuracy giảm trong corrupted và được phục hồi sau repair. |
| mean_judge_score | 4.7667 | 4.4000 | 4.8000 | Điểm chấm của judge cũng phản ánh đúng sự suy giảm và phục hồi. |
| Quality checks | All pass | Partial fail | All pass | Corrupted bị lỗi ở uniqueness và summary length; repair khôi phục lại. |
| Freshness status | True | True | True | Freshness không bị lỗi rõ rệt trong dữ liệu này, nhưng repaired vẫn cho thấy dữ liệu đầy đủ hơn. |

### Kết luận từ số liệu

1. Corruption → quality/freshness signal thay đổi → agent metric thay đổi. Khi dữ liệu bị corrupt, paper_id_unique trở thành false và summary_min_length_10 fail, đồng thời mean_token_f1 và judge_accuracy giảm.
2. Repair action → quality/freshness signal phục hồi → agent metric phục hồi. Sau repair, quality checks lại pass và mean_token_f1, judge_accuracy, mean_judge_score đều quay về gần baseline.

Corruption nào ảnh hưởng rõ nhất và vì sao? Corruption làm blank summary và duplicate rows có tác động rõ nhất vì nó trực tiếp làm giảm độ đầy đủ của dữ liệu và làm giảm chất lượng câu trả lời.

Kết quả nào khác với kỳ vọng ban đầu? Ban đầu có thể kỳ vọng retrieval_hit_rate cũng giảm mạnh, nhưng thực tế metric này vẫn giữ ở 1.0000. Điều này cho thấy retrieval hit rate không phải chỉ dấu nhạy nhất trong tình huống này; token F1 và judge accuracy phản ánh rõ hơn.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. Data quality và observability là lớp kiểm soát cần thiết trước khi dùng dữ liệu cho RAG, vì lỗi nhỏ ở dữ liệu có thể làm giảm chất lượng câu trả lời.
2. Metrics đánh giá bằng human/judge thường nhạy hơn so với retrieval hit rate đơn thuần.
3. Repair không chỉ làm dữ liệu trở lại đúng cấu trúc mà còn cần khôi phục các quality signal để agent có thể hoạt động tốt hơn.

### Nếu có thêm thời gian

Có thể bổ sung thêm các checks như missing values, duplicate content ratio, empty abstract rate, và đưa các threshold này vào dashboard để quan sát liên tục.

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Tổng Tiến Mạnh
**Ngày xác nhận:** 2026-08-06
