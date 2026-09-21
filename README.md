# tuvi — cơ sở dữ liệu tri thức tử vi, phong thủy, xem hạn, xem ngày

Kho dữ liệu và bộ máy tính toán để **sản xuất nội dung tiếng Việt** về tử vi, phong
thủy, hạn và chọn ngày giờ. Dữ liệu tách khỏi mã, mọi con số đều tính ra được và
được kiểm thử, nên nội dung sinh ra không phải "chém gió" mà bám vào bảng tra gốc.

```
data/       26 bộ dữ liệu JSON — tri thức thuần, không lẫn mã
tuvi/       gói Python: lịch âm, can chi, hạn, phong thủy, lá số, xem ngày, chọn ngày
web/        giao diện web: máy chủ thư viện chuẩn + trang tra cứu 5 tab
video/      dựng video dọc cho TikTok từ dữ liệu engine
content/    phân loại chủ đề, mẫu bài, prompt cho mô hình ngôn ngữ
scripts/    dựng SQLite, kiểm tra dữ liệu, công cụ tra cứu dòng lệnh
tests/      46 bài kiểm thử, trong đó có các mốc đối chiếu với nguồn ngoài
docs/       mô hình dữ liệu
SOURCES.md  danh mục nguồn và tình trạng đối chiếu từng bảng
```

Không phụ thuộc thư viện ngoài. Chỉ cần Python 3.10 trở lên.
Riêng khâu xuất tệp video cần thêm hai gói, nêu ở mục cuối.

## Giao diện web

```bash
python web/server.py          # mở http://localhost:8000
```

Bốn tab, tất cả gọi thẳng gói `tuvi` nên số trên màn hình luôn khớp phần đã kiểm thử:

- **Lá số** — địa bàn 12 cung theo bố cục truyền thống (Tỵ Ngọ Mùi Thân ở hàng trên,
  thiên bàn ở giữa), tô màu theo chính tinh / cát tinh / sát tinh, hiện đắc tính
  miếu vượng ngay cạnh tên sao, đánh dấu cung Mệnh và cung Thân, kèm đại hạn từng
  cung. Bấm vào tên sao để mở ngăn kéo giải nghĩa. Cuối trang liệt kê cách cục
  nhận ra được từ lá số.
- **Xem hạn** — sao chiếu mệnh, tam tai, Thái Tuế và bộ ba xem tuổi làm nhà.
- **Phong thủy** — cung phi, bốn hướng tốt, bốn hướng xấu, màu sắc vật phẩm hợp
  mệnh, nguyên tắc bố trí từng khu vực; chọn hướng nhà để chấm luôn hướng đó.
- **Xem ngày** — trực, nhị thập bát tú, hoàng đạo, giờ tốt giờ xấu, ngày kiêng.
- **Chọn ngày** — quét một khoảng ngày cho một tuổi cụ thể và một việc cụ thể, loại
  thẳng ngày xung tuổi và ngày kiêng của việc đó, rồi xếp hạng phần còn lại kèm
  giải thích từng khoản cộng trừ.

Máy chủ chỉ dùng `http.server` của thư viện chuẩn, không cài thêm gì. API trả JSON
nên dùng lại được cho ứng dụng khác:

```
GET /api/laso?ngay=20&thang=9&nam=1990&gio=14&gioi_tinh=nam
GET /api/han?nam_sinh=1987&nam_xem=2026&gioi_tinh=nam
GET /api/phongthuy?nam_sinh=1990&gioi_tinh=nam&huong=Đông Nam
GET /api/ngay?ngay=20&thang=9&nam=2026
GET /api/phitinh?nam=2026
GET /api/sao?ten=Tử vi
GET /api/viec
GET /api/chonngay?nam_sinh=1987&tu_ngay=2026-10-10&den_ngay=2026-11-07&viec=dong_tho
```

## Dùng thử trong 30 giây

```bash
python scripts/tra_cuu.py ngay 20/09/2026        # ngày tốt xấu, trực, tú, giờ hoàng đạo
python scripts/tra_cuu.py han 1990 2026 nam      # sao hạn, tam tai, Thái Tuế, Kim Lâu
python scripts/tra_cuu.py nha 1990 2027          # Kim Lâu — Hoang Ốc — Tam Tai
python scripts/tra_cuu.py phongthuy 1990 nam --huong "Đông Nam"
python scripts/tra_cuu.py laso 20/09/1990 14 nam # lá số rút gọn
python scripts/tra_cuu.py phitinh 2026           # cửu cung phi tinh năm
python scripts/tra_cuu.py viec                   # các việc chọn ngày đang hỗ trợ
python scripts/tra_cuu.py chonngay 1987 01/10/2026 30/11/2026 --viec dong_tho
```

Trong Python:

```python
from tuvi import chon_ngay, han, la_so, ngay_gio, phong_thuy

ngay_gio.xem_ngay(20, 9, 2026)["truc"]                  # 'Kiến'
han.sao_han(2000, 2024, "nam")["sao"]                   # 'Kế Đô'
han.tuoi_lam_nha(1990, 2027)["cac_han_pham"]            # ['Hoang Ốc']
phong_thuy.cung_phi(1990, "nam")["cung_phi"]            # 'Khảm'
la_so.lap_la_so(20, 9, 1990, 14, gioi_tinh="nam")["cuc"]

# Chọn ngày có lọc xung tuổi
from datetime import date
kq = chon_ngay.chon_ngay(1987, date(2026, 10, 10), date(2026, 11, 7),
                         viec="dong_tho", gioi_tinh="nam")
kq["ngay_tot"][0]["duong_lich"], kq["so_chan_xung_tuoi"]
```

## Dựng cơ sở dữ liệu SQLite

```bash
python scripts/build_db.py          # -> build/tuvi.db, 23 bảng, 941 dòng
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
| Chọn ngày | `lich/viec` | 11 việc thường phải chọn ngày, kèm cụm từ đối chiếu với Trực và 28 tú, và danh sách ngày kiêng đủ sức loại ngày |

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
| Quan hệ địa chi | Bảng 12×12 phải đối xứng; kiểm các cặp đã biết | khớp |
| Lọc xung tuổi | Ngày 20/09/2026 đạt 95 điểm chung vẫn bị loại với tuổi Đinh Mão 1987; kết quả chọn ngày không bao giờ chứa ngày đã loại | khớp |

```bash
python -m unittest discover -s tests -v   # 46 bài kiểm thử
python scripts/validate_data.py           # kiểm tra toàn vẹn dữ liệu, dùng được trong CI
```

Những chỗ các trường phái khác nhau (Kim Lâu, Thiên Khôi — Thiên Việt, vòng Tràng
Sinh, Tứ Hóa can Canh) đều được ghi chú ngay trong mã và liệt kê ở mục E của
[SOURCES.md](SOURCES.md).

## Video dọc cho TikTok

```bash
python video/lam_video.py han 1987 2026 --gioi-tinh nam --thang-am 9
python video/lam_video.py ngay 20/09/2026
python video/lam_video.py --chi-kich-ban han 1987 2026   # chỉ kịch bản, không quay
```

Xuất ra `build/video/`: một tệp **MP4 dọc 1080×1920, 30fps** và một tệp kịch bản
Markdown kèm mốc thời gian từng cảnh, lời thoại và caption có sẵn hashtag.

Cảnh được dựng từ chính các hàm trong gói `tuvi`, nên con số trên màn hình là con
số đã qua kiểm thử — không có khâu gõ tay nào giữa engine và video.

Cách làm: dựng danh sách cảnh → đổ vào `video/mau_video.html` → Playwright quay
màn hình ở khổ dọc → ffmpeg chuyển sang H.264. Bố cục chừa sẵn vùng an toàn cho
thanh nút của TikTok ở đáy và cạnh phải.

**Video không có tiếng.** Môi trường dựng không có bộ đọc giọng nói, nên lời thoại
nằm trong tệp kịch bản với mốc thời gian khớp sẵn, để lồng tiếng hoặc chèn nhạc
trên app.

Hai gói chỉ cần cho khâu xuất tệp (`pip install -r video/requirements.txt`):
`playwright` để quay và `imageio-ffmpeg` để chuyển mã. Thiếu chúng thì lệnh vẫn
chạy, chỉ bỏ bước xuất video và vẫn trả về kịch bản. Máy nào đã có `ffmpeg` trong
PATH thì dùng luôn bản đó.

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
- `xem_ngay` cố ý chỉ chấm ngày một cách chung chung (trực, tú, hoàng đạo, ngày
  kiêng). Muốn xét tuổi thì dùng `chon_ngay.xem_ngay_theo_tuoi` hoặc
  `chon_ngay.chon_ngay`; giao diện có ghi chú nhắc điều này ở tab Xem ngày.
- Bốn việc (nhập trạch, ký kết, chữa bệnh, nhậm chức) chưa có mục nào trong bộ 28
  tú nên điểm chỉ dựa vào 12 Trực. `validate_data.py` in cảnh báo cho từng việc và
  giao diện ghi rõ "chỉ xét theo Trực" ngay trong ô chọn việc.
- Phần luận giải trong dữ liệu là văn bản viết mới, không trích sách có bản quyền.

## Lưu ý

Toàn bộ nội dung là **tri thức văn hóa dân gian và huyền học phương Đông**, dùng để
tham khảo và tìm hiểu văn hóa. Đây không phải khoa học dự báo và không thay thế cho
tư vấn y tế, pháp lý hay tài chính.
