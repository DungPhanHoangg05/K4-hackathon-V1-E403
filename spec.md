# AI SPEC - Tóm tắt slide khi trễ bài · Nhóm B2-E403 · Zone 1
Hướng: [x] A - VLearn  [ ] B - Trợ lý Học viên  [ ] C - Làn mở
Loại: [x] Tối ưu tính năng có sẵn  [ ] Tính năng mới

## §1. User & Job
- Job executor + workflow: học viên vào muộn hoặc mất tập trung một đoạn, mở slide/buổi học trên VLearn, gửi câu hỏi như “tóm tắt slide này”, “tóm tắt nội dung chính”, hoặc “tóm tắt phần đang xem”, rồi muốn tiếp tục học ngay mà không phải chờ đọc lại toàn buổi.
- Core JTBD: giúp học viên bắt kịp bài trong vài giây bằng một bản tóm tắt ngắn gọn, đúng phạm vi slide/đoạn đang xem.
- Problem statement: khi học viên trễ bài hoặc mất tập trung, họ cần một cách nhanh để nắm lại ý chính của nội dung đang xem trước khi tiếp tục học, nhưng hệ thống hiện tại thường không tìm thấy hoặc không thể truy cập đúng tài liệu để phục vụ yêu cầu này.
- Evidence (chuẩn A - mining log) - chạy *count_vlearn_evidence.py*:
  - Số liệu mining: n = 128 lượt hỏi “tóm tắt” trong chatlog; 42/128 trường hợp (32.8%) bị tutor trả về not-found hoặc từ chối truy cập tài liệu; 127/128 câu hỏi có phạm vi rõ (trang/slide/đoạn chọn) nhưng vẫn có 41/127 trường hợp (32.3%) thất bại.
  - ≥5 quote/ví dụ nguyên văn + nguồn:
    - “[T0519] HV: ‘Tóm tắt slide pdf day2 cho tôi’ | AI: ‘Rất tiếc, tôi không thể truy cập trực tiếp vào tệp PDF của buổi học để tóm tắt cho bạn.’” - chatlog VLearn.
    - “[T0135] HV: ‘tóm tắt nội dung các giai đoạn được mô tả trên slide các biểu đồ’ | AI: ‘tôi không tìm thấy nội dung nào liên quan…’” - chatlog VLearn.
    - “[T0776] HV: ‘giải thích và tóm tắt nội dung học hôm này’ | AI: ‘tôi không tìm thấy phần tóm tắt tổng quát trong nội dung bài giảng…’” - chatlog VLearn.
    - “[T0938] HV: ‘tóm tắt tất cả nội dung cần note lại đầy đủ’ | AI: ‘tôi không thể truy cập nội dung cụ thể từ slide của ngày hôm nay…’” - chatlog VLearn.
    - “[T0042] HV: ‘Tóm tắt nội dung các ý chính trong slide này cho tôi’ | AI: ‘tôi không thể truy cập nội dung cụ thể của trang 17…’” - chatlog VLearn.

## §2. Impact & quyết định chọn
- Bảng impact:

| Ứng viên | Bao nhiêu người | Tần suất | Tốn gì mỗi lần | Khả thi |
|---|---:|---:|---|---|
| Tóm tắt ngay slide/đoạn đang xem để bắt kịp bài | 128 lượt hỏi “tóm tắt” | Cao | 30–60 giây mất nhịp học | Cao |
| Giải thích một khái niệm riêng lẻ | Nhiều nhưng không nhất quán | Cao | Có thể dùng ngay | Cao |
| Gợi ý câu hỏi ôn tập sau buổi học | Thấp hơn | Trung bình | Ít tác động tức thời | Trung bình |

- Ứng viên ĐÃ LOẠI: “gợi ý câu hỏi ôn tập” vì đáp ứng nhu cầu ít trực tiếp và không giải quyết vấn đề bắt kịp bài ngay trong lúc học.
- Ứng viên CHỌN: “tóm tắt nhanh slide/đoạn đang xem” vì đây là nhu cầu có tần suất cao, rõ ràng, và có thể giải quyết bằng một prototype vừa đủ để demo.

## §3. Giải pháp tương tự đã nghiên cứu
- Notion AI / Copilot trong tài liệu: mạnh ở việc tóm tắt nội dung đã được mở, nhưng thường cần file đã được tải/được truy cập trực tiếp và không tự động bám vào ngữ cảnh bài giảng trên VLearn.
- ChatGPT + PDF upload: có thể tóm tắt tốt nếu người dùng upload file, nhưng workflow thủ công và không phù hợp với trải nghiệm học tập tức thời trong LMS.
- Khác biệt của mình: tích hợp vào flow “học viên trễ bài → xin tóm tắt slide đang xem → AI trả 3–5 ý chính kèm số trang/đoạn trích” và hỏi lại khi phạm vi chưa rõ.

## §4. Thiết kế
- Lát cắt MỘT CÂU: Học viên trễ bài trên VLearn xin tóm tắt slide đang xem, AI tổng hợp 3–5 ý chính kèm số trang, học viên nắm bài trong 15 giây và học tiếp.
- Non-goals (không build): toàn bộ ghi chú buổi học, tự đọc và tóm tắt cả một buổi dài, trả lời vượt ngoài tài liệu được cung cấp, thay thế giảng viên/TA.
- Mức prototype nhắm tới: [x] Working - phần truy xuất nội dung từ slide/transcript đã có là thật; phần tích hợp trực tiếp với VLearn UI là mock.
- Automation: [x] conditional - nếu phạm vi rõ (trang/slide/đoạn chọn), AI tóm tắt ngay; nếu phạm vi mơ hồ (“tóm tắt buổi hôm nay”), AI hỏi lại chốt phạm vi trước để tránh tóm tắt sai.
- §4b. Nguyên tắc đã áp dụng:

| Nguyên tắc | Áp cụ thể vào đâu trong prototype |
|---|---|
| Chốt phạm vi trước khi trả lời | Nếu user không nêu trang/slide/đoạn, hệ thống hỏi lại 1 câu ngắn thay vì tự suy đoán |
| Trả lời ngắn, có cấu trúc | Format 3–5 bullet + “ý chính” + “điểm cần chú ý” |
| Cho thấy căn cứ | Có thể trích dẫn số trang/đoạn liên quan trong câu trả lời |
| Dễ sửa sai | Nếu user chỉnh phạm vi, AI cập nhật summary thay vì chỉ lặp lại câu cũ |

## §5. Kiểu lỗi - 4 lớp chỗ khó + kịch bản

| Lớp chỗ khó | Kịch bản lỗi | Cách phản ứng |
|---|---|---|
| 1. Scope ambiguity | User nói “tóm tắt buổi hôm nay” nhưng không nêu slide/trang | Hỏi lại 1 câu: “Bạn muốn tóm tắt trang nào / slide nào?” |
| 2. Retrieval mismatch | User hỏi trang 46 nhưng hệ thống tìm thấy trang khác hoặc không thấy nội dung | Trả lời trung thực: “Mình chưa tìm thấy đúng trang này” và đề xuất chọn lại phạm vi |
| 3. Overly broad summary | AI trả lời quá dài, giống toàn bộ bài giảng | Tóm ngắn lại thành 3–5 ý chính và giữ ngôn ngữ đơn giản |
| 4. Hallucinated grounding | AI nêu số trang/khái niệm không có căn cứ | Chỉ trả lời khi có căn cứ từ slide/transcript; nếu không chắc thì nói rõ |
| 5. Low-context user input | User chỉ viết “tóm tắt slide” | Gợi ý 1 câu hỏi tiếp theo để chốt phạm vi |
| 6. Out-of-scope request | User yêu cầu tóm tắt cả buổi hoặc cả khóa | Đưa ra summary ở mức cao và nhấn mạnh phạm vi bị giới hạn |
| 7. Language mismatch | User dùng tiếng Việt lẫn tiếng Anh, câu hỏi ngắn | Dùng tiếng Việt chuẩn và hỏi lại nếu cần |
| 8. Trust erosion | User bị tutor từ chối nhiều lần | Cải thiện bằng một phản hồi thân thiện: “Mình chưa tìm thấy đúng phạm vi, bạn cho mình biết trang nào để tóm tắt ngay” |

## §6. Bốn đường đi của trải nghiệm
- Happy path: học viên nhập “tóm tắt trang 17”, AI trả 3–5 ý chính, kèm số trang/đoạn trích, học viên hiểu ngay rồi tiếp tục học.
- Failure/không căn cứ (①): nếu không tìm thấy đúng nội dung, AI nói rõ “mình chưa tìm thấy đúng phạm vi này” thay vì bịa.
- Low-confidence (②): học viên hỏi “tóm tắt slide đầu tiên”, AI nhận diện phạm vi chưa đủ rõ và hỏi lại 1 câu để chốt trước.
- Correction (user sửa): học viên sửa lại “trang 17” thành “trang 27”, AI cập nhật lại summary theo phạm vi mới.
- Khi bị đòi ngoài phạm vi (③): nếu user yêu cầu tóm tắt toàn buổi dài, AI trả summary mức cao và nhắc giới hạn phạm vi.
- Case đặc thù domain (④): nếu câu hỏi liên quan đến thuật ngữ chuyên môn khó, AI cho thêm 1 dòng giải thích ngắn hoặc gợi ý đọc thêm ở slide liên quan.

## §7. Kiểm thử
- Chiều chất lượng: độ đúng phạm vi, độ ngắn gọn, có trích dẫn/đúng số trang, và không “bịa” nội dung.
- Định nghĩa kiểm chứng được: “Đạt khi summary đúng phạm vi trong ≥70% case, có ít nhất 1 căn cứ/đề cập trang hoặc đoạn trong ≥80% case, và phản hồi không vượt quá 5 bullet trong ≥75% case.”
- Golden set: 21 case sẽ lưu trong eval/ gồm 8 case “tóm tắt theo trang/slide”, 6 case “tóm tắt theo đoạn chọn”, 3 case “phạm vi mơ hồ”, 3 case “out-of-scope”.
- Quality bar: “Đạt khi ≥70% case đúng phạm vi và ≥80% case có căn cứ rõ ràng.”
- Kết quả các lượt chạy: sẽ cập nhật trước CP6 trong eval/.

## §8. Phân công & kế hoạch
- Phân công có tên:
  - Dũng: spec 
  - Tiến: demo
  - Hoàn: prompt
  - Hưng: evidence
  - Mạnh: eval
- Kế hoạch vòng validation CP5: 3 câu hỏi sẽ được thử với 3 người, gồm 1. “tóm tắt trang 17”, 2. “tóm tắt slide đầu tiên”, 3. “tóm tắt buổi hôm nay”; Hoàn log phản hồi và ghi lại trường hợp AI đúng/không đúng phạm vi.
- Multi-prototype: nếu làm 2 phương án, trục khác biệt là “summary ngay khi phạm vi rõ” vs “luôn hỏi lại trước” - phương án thứ hai được chọn vì cost-of-error cao khi tóm tắt sai phạm vi.

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| N1 | Chốt problem: học viên trễ bài cần tóm tắt nhanh slide/đoạn đang xem | Từ mining 128 lượt hỏi tóm tắt và 42/128 not-found |
| N1 | Chọn conditional automation thay vì fully automate | Vì phạm vi mơ hồ và cost-of-error cao |
| N1 | Chốt format: 3–5 ý chính + số trang/đoạn trích | Để phản hồi ngắn, dễ dùng ngay trong lúc học |
