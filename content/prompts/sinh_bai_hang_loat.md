# Prompt: sinh hàng loạt bài theo mẫu

## Mục đích
Dựng nhanh một kho bài cho các chủ đề lặp lại (12 con giáp × 12 tháng,
60 hoa giáp × hướng nhà, 109 sao...) mà vẫn giữ được chất lượng.

## Quy trình
1. Chọn mã chủ đề trong `content/taxonomy.json`.
2. Gọi hàm nêu ở trường `ham` để lấy dữ liệu thật cho từng biến thể.
3. Nạp template tương ứng trong `content/templates/`.
4. Yêu cầu mô hình viết phần văn xuôi, giữ nguyên mọi con số từ bước 2.

## Quy tắc chống trùng lặp
- Mỗi bài phải có ít nhất ba chi tiết chỉ đúng với trường hợp đó
  (tên sao hạn, số dư Kim Lâu, tên cung phi, tên trực...).
- Không dùng chung câu mở bài giữa các bài cùng loạt.
- Đoạn "lời khuyên" phải bám vào tính chất dữ liệu, không phải lời khuyên chung chung.

## Kiểm tra trước khi xuất bản
- [ ] Mọi con số khớp với đầu ra của hàm tính toán (chạy lại để đối chiếu)
- [ ] Có nêu trường phái khi bảng tra có nhiều biến thể
- [ ] Có câu miễn trừ ở cuối bài
- [ ] Không có lời hứa về kết quả tài chính, sức khỏe
