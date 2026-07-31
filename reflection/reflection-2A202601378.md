# Reflection Cá Nhân — Hackathon AI (Mini Hackathon Batch 03 / K4)

- **Họ và tên:** Phạm Duy Hoàn
- **Mã học viên:** 2A202601378
- **Nhóm:** V1-E403 · Zone 3
- **Dự án:** VLearn AI Companion — Tính năng: *Tóm tắt slide khi trễ bài*
- **Vai trò trong nhóm:** Prompt Engineer & User Feedback

---

## 1. Vai trò và phần việc cụ thể đã thực hiện

Trong dự án Mini Hackathon AI, tôi đảm nhận vai trò chính về khâu thiết kế prompt và thu thập phản hồi người dùng cho tính năng tóm tắt slide khi học viên trễ bài.

### a. Xây dựng prompt cho hệ thống AI
Tôi đóng góp vào việc viết và chỉnh sửa prompt cho chatbot VLearn nhằm đảm bảo hệ thống:
- hiểu đúng mục tiêu của người dùng khi họ hỏi về “tóm tắt slide”, “tóm tắt trang X”, hoặc “tóm tắt buổi hôm nay”;
- ưu tiên trả lời ngắn gọn, có cấu trúc và có căn cứ từ nội dung slide;
- tránh bịa đặt thông tin khi không tìm thấy dữ liệu trong ngữ cảnh được cấp;
- hỏi lại đúng khi câu hỏi mơ hồ về đối tượng, thay vì trả lời theo suy đoán.

Prompt này được thể hiện rõ trong file prompt chính của nhóm và là nền tảng cho phần prototype demo.

### b. Thu thập và chuyển hóa feedback từ người dùng
Tôi cũng tham gia vào việc ghi nhận phản hồi từ người dùng trong quá trình validation. Những phản hồi này giúp nhóm nhận ra các điểm còn thiếu như:
- người dùng muốn hệ thống hiểu được câu hỏi dạng “tóm tắt từ trang X đến trang Y” mà không cần phải chọn trang thủ công trên UI;
- câu hỏi mơ hồ như “Nó nói cái gì vậy?” cần được làm rõ thay vì trả lời theo slide hiện tại;
- giao diện và trải nghiệm chat cần được cải thiện để dễ theo dõi lịch sử trò chuyện hơn.

Tôi đã chuyển những phản hồi này thành yêu cầu thiết kế và góp phần điều chỉnh hướng phát triển của prototype.

---

## 2. Trợ lý AI đã hỗ trợ tôi như thế nào?

Trong quá trình làm việc, tôi sử dụng AI như một công cụ hỗ trợ tư duy và tăng tốc độ iterating, đặc biệt ở ba khía cạnh:

1. **Đề xuất và rà soát prompt nhanh**: AI giúp tôi viết nhiều phiên bản prompt khác nhau, rồi so sánh cách mỗi phiên bản xử lý các tình huống như phạm vi mơ hồ, câu hỏi thiếu ngữ cảnh, và yêu cầu tóm tắt ngắn gọn.
2. **Kiểm thử các edge case**: Tôi dùng AI để thử các câu hỏi thực tế như “tóm tắt trang 17”, “tóm tắt slide đầu tiên”, hoặc “tóm tắt buổi hôm nay” để thấy prompt có xử lý đúng hay không.
3. **Chuyển feedback thành hành động**: Sau khi có feedback từ người dùng, AI giúp tôi tóm gọn các phản hồi và đề xuất cách điều chỉnh prompt hoặc trải nghiệm sản phẩm để giải quyết vấn đề hiệu quả hơn.

Điều quan trọng nhất là AI không thay thế việc hiểu người dùng, mà giúp tôi làm nhanh hơn, thử nhiều giả định hơn và sớm phát hiện lỗi trong logic phản hồi.

---

## 3. Bài học sâu sắc từ case fail của chính nhóm

Một case fail ban đầu của nhóm là khi hệ thống thử trả lời cho một yêu cầu quá rộng hoặc thiếu ngữ cảnh rõ ràng. Ví dụ, khi người dùng hỏi với phạm vi mơ hồ, hệ thống có thể trả lời quá chung chung hoặc thậm chí suy đoán nội dung không đủ căn cứ.

### Nguyên nhân cốt lõi
Lỗi không nằm ở việc AI “không biết trả lời”, mà ở chỗ prompt chưa đủ chặt về hai điểm:
- **phạm vi câu hỏi** phải được làm rõ trước khi trả lời;
- **nội dung trả về phải dựa trên slide thật**, không được bịa thêm suy diễn.

### Bài học rút ra
Tôi học được rằng trong sản phẩm AI, điều quan trọng không phải là “để AI nói nhiều”, mà là “để AI biết khi nào nên nói ngắn, khi nào nên hỏi lại, và khi nào nên nói rõ rằng mình không có đủ thông tin”.

Bài học lớn nhất của tôi là: một prompt tốt không chỉ làm AI “trả lời” được, mà còn làm AI “biết giới hạn mình” để tránh làm người dùng tin vào một câu trả lời sai hoặc thiếu căn cứ.

---

## 4. Tự đánh giá theo Vibe-Coding Rule

Tôi có thể giải thích rõ được phần việc của mình liên quan đến prompt và feedback người dùng, bao gồm logic xử lý phạm vi câu hỏi, cách làm rõ ngữ cảnh, và cách chuyển feedback thành thay đổi trong prototype. Vì vậy, tôi tự tin có thể trả lời được các câu hỏi tại vòng CP5 và CP6 về phần mình đảm nhận.
