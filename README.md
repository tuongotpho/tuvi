# tuvi — cơ sở dữ liệu tri thức tử vi, phong thủy, xem hạn, xem ngày

Kho dữ liệu và bộ máy tính toán để **sản xuất nội dung tiếng Việt** về tử vi, phong
thủy, hạn và chọn ngày giờ. Dữ liệu tách khỏi mã, mọi con số đều tính ra được và
được kiểm thử, nên nội dung sinh ra không phải "chém gió" mà bám vào bảng tra gốc.

```
data/       25 bộ dữ liệu JSON — tri thức thuần, không lẫn mã
tuvi/       gói Python: lịch âm, can chi, hạn, phong thủy, lá số, xem ngày
content/    phân loại chủ đề, mẫu bài, prompt cho mô hình ngôn ngữ
scripts/    dựng SQLite, kiểm tra dữ liệu, công cụ tra cứu dòng lệnh
tests/      27 bài kiểm thử, trong đó có các mốc đối chiếu với nguồn ngoài
docs/       mô hình dữ liệu
SOURCES.md  danh mục nguồn và tình trạng đối chiếu từng bảng
```

Không phụ thuộc thư viện ngoài. Chỉ cần Python 3.10 trở lên.

## Dùng thử trong 30 giây

```bash
python scripts/tra_cuu.py ngay 20/09/2026        # ngày tốt xấu, trực, tú, giờ hoàng đạo
python scripts/tra_cuu.py han 1990 2026 nam      # sao hạn, tam tai, Thái Tuế, Kim Lâu
python scripts/tra_cuu.py nha 1990 2027          # Kim Lâu — Hoang Ốc — Tam Tai
python scripts/tra_cuu.py phongthuy 1990 nam --huong "Đông Nam"
python scripts/tra_cuu.py laso 20/09/1990 14 nam # lá số rút gọn
python scripts/tra_cuu.py phitinh 2026           # cửu cung phi tinh năm
```

Trong Python:

```python
from tuvi import han, la_so, ngay_gio, phong_thuy

ngay_gio.xem_ngay(20, 9, 2026)["truc"]                  # 'Kiến'
han.sao_han(2000, 2024, "nam")["sao"]                   # 'Kế Đô'
han.tuoi_lam_nha(1990, 2027)["cac_han_pham"]            # ['Hoang Ốc']
phong_thuy.cung_phi(1990, "nam")["cung_phi"]            # 'Khảm'
la_so.lap_la_so(20, 9, 1990, 14, gioi_tinh="nam")["cuc"]
```

## Dựng cơ sở dữ liệu SQLite

```bash
python scripts/build_db.py          # -> build/tuvi.db, 22 bảng, 930 dòng
sqlite3 build/tuvi.db "SELECT ten, nap_am FROM hoa_giap WHERE hanh='Thổ' LIMIT 5"
sqlite3 build/tuvi.db "SELECT huong, du_nien FROM du_nien WHERE cung_phi='Khảm'"
```

## Có những gì trong `data/`

| Nhóm | Bộ dữ liệu | Nội dung |
|---|---|---|
| Nền tảng | `ngu_hanh`, `thien_can`, `dia_chi`, `luc_thap_hoa_giap`, `nap_am` | 5 hành và quan hệ sinh khắc, 10 can, 12 chi với tam hợp — tứ hành xung — lục hợp — lục xung — lục hại, 60 hoa giáp, 30 nạp âm |
| Con giáp | `con_giap` | 12 con giáp: tính cách, sự nghiệp, tình cảm, tài chính, sức khỏe, màu hợp, năm sinh 1924–2044 |
| Tử vi | `tu_vi/sao`, `tu_vi/cung`, `tu_vi/cuc`, `tu_vi/cach_cuc` | 109 sao kèm ngũ hành, loại sao, ý nghĩa và bảng miếu vượng đắc hãm; 12 cung chức; 5 cục; 20 cách cục nổi tiếng |
| Hạn | `han/sao_han`, `han/tam_tai`, `han/kim_lau`, `han/hoang_oc`, `han/han_khac` | 9 sao cửu diệu với bảng tra nam nữ và cách cúng; tam tai; 4 loại Kim Lâu; 6 cung Hoang Ốc; Thái Tuế, tam hình, lục phá |
| Phong thủy | `phong_thuy/bat_trach`, `cuu_cung_phi_tinh`, `huong`, `mau_sac_vat_pham`, `bo_tri_khong_gian` | 8 cung phi và ma trận du niên 8×8; 9 sao phi tinh và Vận 9; 8 hướng, 24 sơn; màu và vật phẩm theo nạp âm; nguyên tắc bố trí 6 khu vực |
| Lịch | `lich/truc`, `nhi_thap_bat_tu`, `tiet_khi`, `ngay_kieng` | 12 Trực, 28 tú, 24 tiết khí, các ngày kiêng dân gian |

## Độ tin cậy

Mỗi phép tính đều có ít nhất một mốc đối chiếu độc lập, chạy tự động trong `tests/`:

| Phép tính | Cách đối chiếu | Kết quả |
|---|---|---|
| Đổi âm — dương lịch | 01/01/2024 = 20/11 Quý Mão; Tết Bính Ngọ = 17/02/2026; đổi xuôi rồi ngược qua các năm 1950–2050 | khớp |
| Vị trí sao trên lá số | So 15 sao trên 10 lá số với thư viện MIT `doanguyen/lasotuvi` | khớp hoàn toàn |
| Hoang Ốc | Danh sách 33 tuổi xấu được các trang phong thủy công bố | khớp từng tuổi |
| Sao hạn cửu diệu | Ví dụ "sinh năm 2000, năm 2024 gặp Kế Đô (nam) / Thái Dương (nữ)" | khớp |
| 12 Trực | 01/01/2024 là trực Kiến | khớp |
| Nhị thập bát tú | Neo 01/01/1995 (sao Hư) và kiểm chéo: sao Giác luôn rơi vào thứ Năm suốt hơn một năm | khớp |
| Bát trạch | Ma trận du niên 8×8 phải đối xứng | khớp |
| Phi tinh năm | 2024 Tam Bích, 2025 Nhị Hắc, 2026 Nhất Bạch | khớp |

```bash
python -m unittest discover -s tests -v   # 27 bài kiểm thử
python scripts/validate_data.py           # kiểm tra toàn vẹn dữ liệu, dùng được trong CI
```

Những chỗ các trường phái khác nhau (Kim Lâu, Thiên Khôi — Thiên Việt, vòng Tràng
Sinh, Tứ Hóa can Canh) đều được ghi chú ngay trong mã và liệt kê ở mục E của
[SOURCES.md](SOURCES.md).

## Làm content từ kho này

1. Chọn chủ đề trong `content/taxonomy.json` (16 chủ đề chia theo 4 trụ cột:
   tử vi, phong thủy, hạn, xem ngày).
2. Gọi hàm ghi ở trường `ham` để lấy dữ liệu thật cho trường hợp cụ thể.
3. Đổ vào mẫu tương ứng trong `content/templates/`.
4. Nếu dùng mô hình ngôn ngữ để viết phần văn xuôi, dùng prompt trong
   `content/prompts/` — trong đó có sẵn prompt kiểm duyệt trước khi xuất bản.

Quy tắc biên tập bắt buộc nằm ở cuối `content/taxonomy.json`: nói rõ đây là tri
thức dân gian, không hứa hẹn kết quả, không dọa nạt để bán vật phẩm giải hạn, và
mọi con số phải sinh từ hàm tính toán chứ không gõ tay.

## Giới hạn đã biết

- `tuvi/la_so.py` an 55 sao cốt lõi, chưa an đủ 109 sao. Muốn đủ, dùng
  `doanguyen/lasotuvi` (MIT) — dữ liệu sao trong kho này tương thích với nó.
- Thuật toán âm lịch chính xác trong khoảng 1800–2199.
- Chưa có phần Tử Bình (bát tự), Kinh Dịch, nhân tướng học.
- Phần luận giải trong dữ liệu là văn bản viết mới, không trích sách có bản quyền.

## Lưu ý

Toàn bộ nội dung là **tri thức văn hóa dân gian và huyền học phương Đông**, dùng để
tham khảo và tìm hiểu văn hóa. Đây không phải khoa học dự báo và không thay thế cho
tư vấn y tế, pháp lý hay tài chính.
