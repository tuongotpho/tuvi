# Prompt: kiểm duyệt nội dung trước khi xuất bản

Đọc bài và trả về danh sách vấn đề theo bốn nhóm:

## 1. Sai dữ liệu
So từng con số, tên sao, tên cung, ngày tháng trong bài với đầu ra của các hàm trong
gói `tuvi`. Bất kỳ sai lệch nào cũng là lỗi chặn xuất bản.

## 2. Vượt giới hạn đạo đức
Đánh dấu nếu bài:
- khẳng định chắc chắn về tai họa, bệnh tật, cái chết
- dọa người đọc để bán vật phẩm, khóa học, lễ giải hạn
- phán về người thứ ba mà người đó không yêu cầu
- khuyên bỏ điều trị y tế, bỏ học, bỏ việc dựa trên lá số
- phân biệt đối xử theo tuổi, giới tính, mệnh

## 3. Thiếu minh bạch trường phái
Đánh dấu chỗ dùng bảng tra có nhiều biến thể (Kim Lâu, Thiên Khôi — Thiên Việt,
vòng Tràng Sinh, Tứ Hóa can Canh) mà không nói rõ đang dùng bản nào.

## 4. Chất lượng viết
- Câu sáo rỗng lặp lại giữa các bài
- Đoạn không có thông tin mới
- Thuật ngữ dùng sai nghĩa

Trả kết quả dạng bảng: nhóm lỗi | trích dẫn | đề xuất sửa.
