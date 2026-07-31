# Reflection Cá Nhân — Hackathon AI (Mini Hackathon Batch 03 / K4)

- **Họ và tên:** Ngô Nguyễn Khải Hưng  
- **Mã học viên:** 2A202601216  
- **Nhóm:** V1-E403 · Zone 4  
- **Dự án:** VLearn AI Companion — Tính năng: *Tóm tắt slide khi trễ bài*  
- **Vai trò trong nhóm:** Evidence Lead & Data Mining Engineer  

---

## 1. Vai trò và phần việc cụ thể đã thực hiện

Trong dự án Mini Hackathon AI, tôi chịu trách nhiệm chính về khối **Bằng chứng & Impact (chuẩn B)** cho tính năng *"Tóm tắt slide khi trễ bài"* trên hệ thống VLearn:

### a. Khai thác dữ liệu thực tế (Data Mining):
* Viết script Python `count_vlearn_evidence.py` để phân tích tự động **2.522 dòng dữ liệu hội thoại thật** đã ẩn danh trong `data/vlearn-pack/chatlog/chat_history_anonymized_for_hackathon.csv`.
* Phân loại và đo lường tần suất nhu cầu học viên:
  - **128 lượt hỏi "tóm tắt"** slide/bài giảng trong lịch sử chat.
  - **42/128 trường hợp (32.8%)** bị hệ thống AI Tutor cũ trả về phản hồi thất bại (`not-found` hoặc từ chối truy cập file PDF/slide bài giảng).
  - **41/127 câu hỏi (32.3%)** có phạm vi trang rõ ràng nhưng vẫn bị AI cũ từ chối/bị lỗi trích xuất.

### b. Trích xuất bằng chứng nguyên văn:
Rà soát dữ liệu và trích dẫn 5 ví dụ nguyên văn chứng minh điểm đau (Pain Point) thực tế của học viên khi bị trễ bài:
1. `[T0519]` *HV: "Tóm tắt slide pdf day2 cho tôi" $\rightarrow$ AI: "Rất tiếc, tôi không thể truy cập trực tiếp vào tệp PDF của buổi học..."*
2. `[T0042]` *HV: "Tóm tắt nội dung các ý chính trong slide này cho tôi" $\rightarrow$ AI: "Tôi không thể truy cập nội dung cụ thể của trang 17..."*
3. `[T0135]` *HV: "Tóm tắt nội dung các giai đoạn được mô tả trên slide" $\rightarrow$ AI: "Tôi không tìm thấy nội dung..."*
4. `[T0776]` *HV: "Giải thích và tóm tắt nội dung học hôm nay" $\rightarrow$ AI: "Tôi không tìm thấy phần tóm tắt tổng quát..."*
5. `[T0938]` *HV: "Tóm tắt tất cả nội dung cần note lại đầy đủ" $\rightarrow$ AI: "Tôi không thể truy cập nội dung từ slide..."*

### c. Đóng góp vào bộ tài liệu dự án:
- Cung cấp toàn bộ con số đếm và quote chứng minh cho Mục §1 (*User & Job*) và Mục §2 (*Impact*) trong `spec.md`.
- Xây dựng nội dung Slide 1 (*User & Job*) và Slide 2 (*Impact & Quyết định chọn*) cho bộ slide nộp bài `demo-slides.pdf`.

---

## 2. Trợ lý AI đã hỗ trợ tôi như thế nào?

Trong suốt 1.5 ngày làm Hackathon, tôi đã tận dụng các công cụ AI trợ lý (Cursor / Claude Code / Gemini) như một người đồng hành pair-programming:

1. **Sinh script khai thác dữ liệu nhanh:** AI giúp tôi viết cấu trúc script Python bằng `pandas` và `re` để tìm kiếm và nhóm các biến thể từ khoá (`tóm tắt`, `summary`, `tóm ý`, `nội dung chính`) từ file CSV lớn.
2. **Kiểm tra chéo tính chính xác (Verification):** Dùng AI viết unit test để xác minh phương pháp đếm không bị trùng lặp hay bỏ sót hội thoại, đảm bảo phương pháp đếm hoàn toàn kiểm lại được (Reproductory).
3. **Đẩy nhanh tiến độ:** Nhờ AI hỗ trợ lập trình, tôi hoàn thành toàn bộ khối bằng chứng chuẩn B chỉ trong gần 1.5 giờ, dành thời gian còn lại phối hợp cùng nhóm xây dựng bộ Golden Set 22 cases và làm slide demo.

---

## 3. Bài học sâu sắc từ ca thất bại (Failure Case) của nhóm

### a. Tình huống thất bại ban đầu:
Ở phiên chạy thử đầu tiên (Baseline Run), nhóm định hướng làm một tính năng rất rộng: *"AI tự động đọc toàn bộ bài giảng 50-60 trang và tạo bản tổng hợp kiến thức toàn buổi"*. Kết quả thử nghiệm thất bại nặng nề:
- AI bị trôi ngữ cảnh (lost-in-the-middle) và bịa ra các trang slide không hề có thật.
- Phản hồi trả về dài tới 3 trang màn hình — hoàn toàn vô dụng đối với một học viên đang bị trễ bài 15 phút và cần bắt kịp lớp ngay lập tức.

### b. Nguyên nhân cốt lõi (Root Cause):
Phạm vi quá rộng, cost-of-error quá cao và không bám sát bức tranh thực tế của người dùng: **Học viên trễ bài chỉ cần 3-5 ý chính của slide đang học để tiếp tục nghe giảng cùng lớp, chứ không cần một cuốn sách giáo khoa tổng hợp.**

### c. Cách nhóm khắc phục & Bài học rút ra:
Nhóm tôi đã họp gấp và tái cấu trúc sản phẩm về đúng **Lát cắt MỘT CÂU**: *"Học viên trễ bài trên VLearn xin tóm tắt slide đang xem, AI tổng hợp 3–5 ý chính kèm số trang trích dẫn `(Trang N)`, học viên nắm bài trong 15 giây và tiếp tục học."*

> 💡 **Bài học lớn nhất rút ra:**  
> *"Một sản phẩm AI nhỏ, giải quyết DỨT ĐIỂM một điểm đau thật có bằng chứng (32.8% thất bại) và KHÔNG BỊA ĐẶT có giá trị lớn hơn rất nhiều một hệ thống phức tạp nhưng đoán mò và không thể tin cậy."*

---

## 4. Tự đánh giá theo Vibe-Coding Rule

Tôi hoàn toàn nắm vững logic phân tích dữ liệu trong script `count_vlearn_evidence.py`, giải thích được con số bằng chứng **32.8%** thất bại và sẵn sàng trả lời tự tin mọi câu hỏi phản biện của Ban Giám Khảo tại vòng Q&A mốc **CP5** và **CP6**.
