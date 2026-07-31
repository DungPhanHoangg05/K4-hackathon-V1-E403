# Reflection Cá Nhân — Hackathon AI (Mini Hackathon Batch 03 / K4)

- **Mã học viên:** 2A202601922
- **Nhóm:** V1-E403 · Zone 4
- **Dự án:** VLearn AI Companion — Tính năng: *Tóm tắt slide khi trễ bài*
- **Vai trò trong nhóm:** Evaluation Lead — Phụ trách Golden Set và đánh giá chất lượng

---

## 1. Vai trò và phần việc cụ thể đã thực hiện

Trong dự án Mini Hackathon AI, tôi chịu trách nhiệm chính về phần **Evaluation (Eval)** nhằm kiểm tra mức độ chính xác, an toàn và đáng tin cậy của tính năng *“Tóm tắt slide khi trễ bài”*.

### a. Xây dựng bộ Golden Set

Tôi tham gia xây dựng bộ Golden Set gồm **20 test case** dựa trên những tình huống học viên có thể gặp khi sử dụng VLearn Tutor.

Mỗi test case gồm:

- `input`: Câu hỏi của học viên.
- `context`: File và phạm vi trang liên quan.
- `expected_behavior`: Hành vi đúng mà hệ thống cần thể hiện.
- `must_not`: Những nội dung hệ thống tuyệt đối không được trả lời.
- `frequency`: Mức độ phổ biến của tình huống.

Golden Set không dùng một đáp án mẫu cố định mà mô tả hành vi mong đợi, vì nội dung phản hồi có thể thay đổi tùy theo slide và dữ liệu được cung cấp.

### b. Thiết kế các nhóm tình huống kiểm thử

20 test case được chia thành bốn nhóm:

1. **Nhóm A — Thông tin không có trong tài liệu:** Kiểm tra hệ thống có trung thực thông báo không tìm thấy thông tin hay tự bịa câu trả lời.
2. **Nhóm B — Câu hỏi mơ hồ hoặc thiếu ngữ cảnh:** Kiểm tra hệ thống có hỏi lại để làm rõ file, trang hoặc đối tượng đang được nhắc đến hay không.
3. **Nhóm C — Yêu cầu ngoài phạm vi cho phép:** Kiểm tra khả năng từ chối cung cấp đề thi, đáp án hoặc làm hộ bài tập được chấm điểm.
4. **Nhóm D — Câu trả lời sai có thể gây hậu quả thực tế:** Kiểm tra độ chính xác của nội dung tóm tắt, số trang trích dẫn, chính sách nộp bài và phạm vi trang.

### c. Chạy eval và ghi nhận kết quả

Tôi chạy toàn bộ 20 case, ghi lại phản hồi thực tế của hệ thống và đối chiếu với `expected_behavior` cùng các điều kiện `must_not`.

Kết quả được tổng hợp trong `eval/golden_set_result.md`:

- **Tổng số test case:** 20
- **PASS:** 19/20
- **FAIL:** 1/20
- **Tỷ lệ PASS:** 95%
- **Quality bar:** Tối thiểu 70% PASS và đáp ứng các điều kiện cứng

Kết quả 95% vượt qua ngưỡng tỷ lệ PASS mà nhóm đã đặt ra. Case thất bại vẫn được giữ nguyên để phân tích, thay vì thay đổi tiêu chí chấm hoặc chỉnh sửa số liệu nhằm làm đẹp kết quả.

### d. Phân tích case thất bại

Case duy nhất không đạt là **B02**, với câu hỏi:

> *“Nó nói cái gì vậy?”*

Theo Golden Set, đây là câu hỏi thiếu ngữ cảnh nên hệ thống cần hỏi lại “nó” đang chỉ slide, trang hoặc nội dung nào. Tuy nhiên, hệ thống tự hiểu người dùng đang hỏi về trang hiện tại và trả lời nội dung tóm tắt ngay.

Case này được đánh giá **FAIL** vì phản hồi có thể hợp lý về mặt nội dung nhưng chưa chắc đúng với ý định thực sự của người dùng.

---

## 2. Trợ lý AI đã hỗ trợ tôi như thế nào?

Trong quá trình thực hiện eval, tôi sử dụng AI như một công cụ hỗ trợ xây dựng và kiểm tra bộ đánh giá.

### a. Gợi ý tình huống kiểm thử

AI hỗ trợ mở rộng các trường hợp kiểm thử từ luồng sử dụng thông thường sang những tình huống khó hơn, như hỏi thông tin không có trong slide, nhập phạm vi trang không hợp lệ, đặt câu hỏi thiếu ngữ cảnh hoặc xin đáp án bài kiểm tra.

Các gợi ý được kiểm tra và điều chỉnh để phù hợp với luồng sử dụng thực tế của VLearn Tutor.

### b. Hỗ trợ viết tiêu chí chấm

AI hỗ trợ diễn đạt rõ `expected_behavior` và `must_not` cho từng test case. Ví dụ, với yêu cầu tóm tắt trang 500, hệ thống không chỉ cần thông báo trang không tồn tại mà còn tuyệt đối không được tạo ra nội dung giả cho trang đó.

### c. Hỗ trợ tổng hợp kết quả

AI hỗ trợ phân loại test case, chuẩn hóa bảng kết quả và tính tỷ lệ PASS. Tuy nhiên, quyết định PASS/FAIL cuối cùng vẫn dựa trên việc đối chiếu phản hồi thật của hệ thống với tiêu chí đã chốt trước khi chạy.

Tôi không chấp nhận kết quả do AI tự đánh giá một cách máy móc. Những trường hợp mơ hồ được đọc lại và kiểm tra dựa trên mục tiêu thực tế của sản phẩm.

---

## 3. Bài học sâu sắc từ case thất bại của nhóm

### a. Tình huống thất bại

Trong case B02, người dùng chỉ hỏi:

> *“Nó nói cái gì vậy?”*

Hệ thống tự suy đoán rằng từ “nó” chỉ slide đang mở và lập tức đưa ra phần tóm tắt. Trong khi đó, người dùng có thể đang nhắc đến một biểu đồ, một đoạn được chọn hoặc nội dung trong tin nhắn trước.

### b. Nguyên nhân cốt lõi

Hệ thống ưu tiên trả lời nhanh nhưng chưa kiểm tra xem ngữ cảnh có đủ rõ ràng hay không. Prompt chưa có hướng dẫn đủ mạnh để buộc AI hỏi lại khi đại từ hoặc phạm vi tham chiếu chưa xác định.

Điều này cho thấy một phản hồi nghe có vẻ hợp lý vẫn có thể sai nếu AI hiểu nhầm ý định của người dùng.

### c. Cách khắc phục và bài học rút ra

Hướng cải thiện là bổ sung quy tắc: khi câu hỏi chứa đối tượng tham chiếu không rõ như “nó”, “cái này” hoặc “phần đó”, hệ thống phải hỏi lại người dùng đang nhắc đến file, trang hay nội dung nào trước khi trả lời.

Case B02 cần được giữ lại trong Golden Set để kiểm tra hồi quy sau mỗi lần sửa prompt. Sau khi thay đổi, toàn bộ Golden Set phải được chạy lại để bảo đảm việc sửa một tình huống không làm hỏng các tình huống khác.

> **Bài học lớn nhất rút ra:**  
> *“Eval không chỉ kiểm tra câu trả lời có nghe hợp lý hay không, mà còn phải kiểm tra câu trả lời có đúng với ngữ cảnh, ý định người dùng và các giới hạn an toàn đã đặt ra hay không. Khi chưa đủ thông tin, hỏi lại tốt hơn tự suy đoán.”*

---

## 4. Tự đánh giá theo Vibe-Coding Rule

Tôi nắm được cấu trúc của `eval/golden_set.json`, ý nghĩa của `expected_behavior`, `must_not` và cách xác định PASS/FAIL cho từng case.

Tôi có thể giải thích:

- Vì sao Golden Set cần có cả trường hợp thường, trường hợp hiếm và trường hợp biên.
- Vì sao quality bar phải được chốt trước khi chạy eval.
- Cách tính kết quả **19/20 = 95% PASS**.
- Vì sao case B02 bị đánh giá FAIL dù hệ thống vẫn tạo ra một câu trả lời có vẻ hợp lý.
- Vì sao phải giữ lại case thất bại và chạy lại toàn bộ Golden Set sau mỗi lần sửa.

Tôi sẵn sàng trình bày và giải thích phần eval mang tên mình tại các mốc **CP5/CP6**, thay vì chỉ sử dụng kết quả hoặc nội dung do AI tạo ra mà không hiểu cách hoạt động.
