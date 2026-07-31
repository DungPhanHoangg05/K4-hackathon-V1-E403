## Phản hồi từ người dùng

- **Trần An Thắng - 2A202601756:** Hiện tại mình phải chọn khoảng trang trên UI thì AI mới trả lời. Nếu mình nhập luôn **"Tóm tắt từ trang X đến trang Y"** thì AI nên tự hiểu và trả lời, không cần hỏi lại chọn trang.
- **Trần Kiều Hạnh - 2A202601760:** Giao diện chưa thân thiện với người dùng, chưa lưu lịch sử trò chuyện.
- **Lương Bảo Long - 2A202601682:** Khi hỏi câu có chủ ngữ mơ hồ như **"Nó nói cái gì vậy?"**, hệ thống không hỏi lại **"nó"** là gì mà trả lời ngay theo slide hiện tại.
- **Trần Bình Minh - 2A202601434:** Hệ thống đã giúp tôi tóm tắt được slide để học nhanh hơn nhưng còn cần cải thiện UI đẹp hơn.
- **Tạ Đăng Đức - 2A202601772:** Slide xem trên hệ thống hơi mờ nên việc bôi đen hơi khó thao tác.

## Nhóm đã sửa gì từ phản hồi đó?

- Hệ thống được cập nhật để **tự nhận diện khoảng trang trong câu hỏi** (ví dụ: *"Tóm tắt từ trang 10 đến trang 15"*) và tự truy xuất nội dung mà không cần người dùng chọn trang trên UI.
- **Cải thiện giao diện chatbot** trực quan hơn và **bổ sung lưu lịch sử trò chuyện** để người dùng dễ theo dõi các trao đổi trước đó.
- Bổ sung **xử lý câu hỏi mơ hồ**: khi người dùng sử dụng các đại từ như *"nó"*, *"cái này"*, *"phần đó"* mà không đủ ngữ cảnh, AI sẽ **hỏi lại để làm rõ** thay vì tự suy đoán và trả lời theo slide hiện tại.