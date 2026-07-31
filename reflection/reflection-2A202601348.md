# Reflection cá nhân

**Họ và tên:** Phan Hoàng Dũng - 2A202601348
**Vai trò:** Phụ trách AI Spec và hoàn thiện phiên bản Working Final

## Vai trò và phần mình thực hiện

Trong dự án, mình đảm nhận vai trò xây dựng và hoàn thiện tài liệu **AI Spec**, đồng thời phụ trách tích hợp và hoàn thiện phiên bản **Working Final** của hệ thống trước khi demo. Công việc của mình bắt đầu từ việc phân tích yêu cầu của đề bài, đọc và khai thác dữ liệu chatlog để xác định đúng vấn đề mà nhóm cần giải quyết. Sau khi thống nhất hướng đi, mình chịu trách nhiệm biên soạn toàn bộ AI Spec, bao gồm mô tả bài toán, bằng chứng từ dữ liệu, phân tích tác động, thiết kế giải pháp, các tình huống khó, quy trình trải nghiệm người dùng, kế hoạch kiểm thử và quality bar.

Bên cạnh phần tài liệu, mình cũng tham gia hoàn thiện prototype để đảm bảo luồng hoạt động thống nhất với AI Spec. Mình chỉnh sửa prompt, cập nhật logic xử lý một số trường hợp đặc biệt và kiểm tra lại toàn bộ workflow trước khi nhóm tiến hành demo. Sau mỗi lần nhận phản hồi từ người dùng thử nghiệm, mình cập nhật lại đặc tả và điều chỉnh prototype để hai phần luôn đồng bộ.

## AI đã hỗ trợ mình như thế nào

AI hỗ trợ mình chủ yếu ở các công việc mang tính tăng năng suất thay vì thay thế quyết định. Trong quá trình viết AI Spec, mình sử dụng AI để gợi ý cấu trúc tài liệu, diễn đạt lại các ý theo đúng template của môn học, rà soát lỗi trình bày và chuẩn hóa cách viết giữa các mục. AI cũng hỗ trợ tạo các phiên bản prompt, viết prototype HTML để minh họa luồng trải nghiệm và gợi ý các trường hợp kiểm thử cho golden set.

Tuy nhiên, toàn bộ các quyết định quan trọng như lựa chọn bài toán, phân tích số liệu từ chatlog, xây dựng quality bar, xác định các nhóm tình huống khó hay quyết định thay đổi hệ thống đều do mình và nhóm thực hiện. Mình luôn kiểm tra lại các nội dung AI sinh ra, đối chiếu với dữ liệu thực tế và chỉnh sửa trước khi đưa vào sản phẩm cuối cùng.

## Bài học từ case fail của nhóm
Qua quá trình kiểm thử với người dùng, nhóm nhận được nhiều phản hồi giúp phát hiện các vấn đề chưa được nghĩ tới trong quá trình thiết kế. Trường hợp đáng chú ý nhất là hệ thống chỉ có thể tóm tắt khi người dùng chọn khoảng trang trên giao diện. Nếu người dùng nhập trực tiếp câu hỏi như **"Tóm tắt từ trang 10 đến trang 15"**, hệ thống vẫn yêu cầu chọn lại trang thay vì tự nhận diện phạm vi trong câu hỏi. Sau khi phân tích nguyên nhân, nhóm đã bổ sung cơ chế nhận diện khoảng trang từ ngôn ngữ tự nhiên để AI có thể truy xuất đúng nội dung mà không cần thao tác thêm trên giao diện.

Ngoài ra, nhóm cũng phát hiện hệ thống xử lý chưa tốt các câu hỏi mơ hồ như **"Nó nói cái gì vậy?"**. Trước đây AI tự suy đoán rằng người dùng đang hỏi về slide hiện tại và trả lời ngay, dẫn đến nguy cơ trả lời sai ngữ cảnh. Sau khi sửa, hệ thống sẽ hỏi lại để làm rõ đối tượng trước khi trả lời. Nhóm cũng cải thiện giao diện, bổ sung lưu lịch sử trò chuyện và chỉnh sửa phần hiển thị để chỉ hiển thị câu trả lời cuối cùng thay vì toàn bộ nội dung tài liệu truy xuất.

Qua dự án này, bài học lớn nhất mình rút ra là **không nên chỉ dựa vào giả định của nhóm phát triển**. Một giải pháp có thể đúng về mặt kỹ thuật nhưng vẫn chưa mang lại trải nghiệm tốt nếu chưa được kiểm thử với người dùng thật. Việc liên tục nhận phản hồi, phân tích nguyên nhân và cập nhật cả AI Spec lẫn prototype giúp sản phẩm hoàn thiện hơn và bám sát nhu cầu thực tế của người học.