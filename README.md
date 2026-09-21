# tuvi — cơ sở dữ liệu tri thức tử vi, phong thủy, xem hạn, xem ngày

Kho dữ liệu và bộ máy tính toán để **sản xuất nội dung tiếng Việt** về tử vi, phong
thủy, hạn và chọn ngày giờ. Dữ liệu tách khỏi mã, mọi con số đều tính ra được và
được kiểm thử, nên nội dung sinh ra không phải "chém gió" mà bám vào bảng tra gốc.

```
data/       26 bộ dữ liệu JSON — tri thức thuần, không lẫn mã
tuvi/       gói Python: lịch âm, can chi, hạn, phong thủy, lá số, luận giải, xem ngày, chọn ngày
web/        giao diện web: máy chủ thư viện chuẩn + trang tra cứu 5 tab
video/      dựng video dọc cho TikTok từ dữ liệu engine
content/    phân loại chủ đề, mẫu bài, prompt cho mô hình ngôn ngữ
scripts/    dựng SQLite, kiểm tra dữ liệu, công cụ tra cứu dòng lệnh
tests/      84 bài kiểm thử, trong đó có các mốc đối chiếu với nguồn ngoài
docs/       mô hình dữ liệu
SOURCES.md  danh mục nguồn và tình trạng đối chiếu từng bảng
```

Không phụ thuộc thư viện ngoài. Chỉ cần Python 3.10 trở lên.
Riêng khâu xuất tệp video cần thêm hai gói, nêu ở mục cuối.

## Giao diện web

```bash
python web/server.py          # mở http://localhost:8000
```

Năm tab, tất cả gọi thẳng gói `tuvi` nên số trên màn hình luôn khớp phần đã kiểm thử:

- **Lá số** — an đủ 109 sao, Tuần — Triệt; địa bàn 12 cung theo bố cục truyền thống (Tỵ Ngọ Mùi Thân ở hàng trên,
  thiên bàn ở giữa), tô màu theo chính tinh / cát tinh / sát tinh, hiện đắc tính
  miếu vượng ngay cạnh tên sao, đánh dấu cung Mệnh và cung Thân, kèm đại hạn từng
  cung. Bấm vào tên sao để mở ngăn kéo giải nghĩa. Cuối trang liệt kê cách cục
  nhận ra được từ lá số. Nút **Luận giải chi tiết** mở bản đọc đầy đủ: bản mệnh nạp âm, Cục và
  quan hệ Mệnh — Cục, âm dương thuận/nghịch lý, Thân cư cung nào, Tứ Hóa rơi vào cung nào, 12 cung
  theo thứ tự đọc (chính tinh kèm đắc tính, cát — sát tinh, tam hợp — xung chiếu, vô chính diệu thì
  mượn sao), bảng 12 đại hạn có đánh dấu hạn đang đi theo năm xem. Mỗi cung có điểm gợi ý kèm
  từng khoản cộng trừ để kiểm lại được; điểm chỉ để xếp thứ tự đáng chú ý.
- **Xem hạn** — sao chiếu mệnh, tam tai, Thái Tuế và bộ ba xem tuổi làm nhà. Ba tab theo tuổi
  (Xem hạn, Phong thủy, Chọn ngày) nhận ngày sinh dương lịch và tự đổi ra năm âm, vì người
  sinh tháng 1–2 dương trước Tết hay gõ nhầm năm âm.
- **Phong thủy** — cung phi, bốn hướng tốt, bốn hướng xấu, màu sắc vật phẩm hợp
  mệnh, nguyên tắc bố trí từng khu vực; chọn hướng nhà để chấm luôn hướng đó.
- **Xem ngày** — trực, nhị thập bát tú, hoàng đạo, giờ tốt giờ xấu, ngày kiêng.
- **Chọn ngày** — quét một khoảng ngày cho một tuổi cụ thể và một việc cụ thể, loại
  thẳng ngày xung tuổi và ngày kiêng của việc đó, rồi xếp hạng phần còn lại kèm
  giải thích từng khoản cộng trừ.

Máy chủ chỉ dùng `http.server` của thư viện chuẩn, không cài thêm gì. API trả JSON
nên dùng lại được cho ứng dụng khác. Đầu vào sai (ngày không có thật, giờ ngoài 0–23,
năm ngoài 1800–2199, giới tính lạ...) bị chặn ở tầng thư viện `tuvi.kiem_tra` và trả
mã 400 kèm câu báo tiếng Việt; các API theo tuổi nhận `ngay_sinh=yyyy-mm-dd` dương lịch
để máy tự đổi ra năm âm:

```
GET /api/laso?ngay=20&thang=9&nam=1990&gio=14&gioi_tinh=nam
GET /api/laso?ngay=20&thang=9&nam=1990&canh=Mùi&gioi_tinh=nam   # chỉ nhớ canh giờ
GET /api/luangiai?ngay=20&thang=9&nam=1990&gio=14&gioi_tinh=nam&nam_xem=2026
GET /api/han?nam_sinh=1987&nam_xem=2026&gioi_tinh=nam
GET /api/han?ngay_sinh=1990-01-15&nam_xem=2026&gioi_tinh=nam   # tự đổi ra Kỷ Tỵ 1989
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
python scripts/tra_cuu.py laso 20/09/1990 14 nam # lá số (giờ đồng hồ)
python scripts/tra_cuu.py laso 20/09/1990 Mùi nam # lá số (canh giờ)
python scripts/tra_cuu.py luangiai 20/09/1990 14 nam --nam-xem 2026  # luận giải chi tiết
python scripts/tra_cuu.py phitinh 2026           # cửu cung phi tinh năm
python scripts/tra_cuu.py viec                   # các việc chọn ngày đang hỗ trợ
python scripts/tra_cuu.py chonngay 1987 01/10/2026 30/11/2026 --viec dong_tho
```

Trong Python:

```python
from tuvi import chon_ngay, han, la_so, luan_giai, ngay_gio, phong_thuy

ngay_gio.xem_ngay(20, 9, 2026)["truc"]                  # 'Kiến'
han.sao_han(2000, 2024, "nam")["sao"]                   # 'Kế Đô'
han.tuoi_lam_nha(1990, 2027)["cac_han_pham"]            # ['Hoang Ốc']
phong_thuy.cung_phi(1990, "nam")["cung_phi"]            # 'Khảm'
la_so.lap_la_so(20, 9, 1990, 14, gioi_tinh="nam")["cuc"]
luan_giai.luan_giai_la_so(la_so.lap_la_so(20, 9, 1990, 14), 2026)["dai_han"]["hien_tai"]

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
| Tử vi | `tu_vi/sao`, `tu_vi/cung`, `tu_vi/cuc`, `tu_vi/cach_cuc` | 109 sao kèm ngũ hành, loại sao, ý nghĩa và bảng miếu vượng đắc hãm; 12 cung chức; 5 cục; 92 cách cục kèm quy tắc nhận diện máy đọc được |
| Hạn | `han/sao_han`, `han/tam_tai`, `han/kim_lau`, `han/hoang_oc`, `han/han_khac` | 9 sao cửu diệu với bảng tra nam nữ và cách cúng; tam tai; 4 loại Kim Lâu; 6 cung Hoang Ốc; Thái Tuế, tam hình, lục phá |
| Phong thủy | `phong_thuy/bat_trach`, `cuu_cung_phi_tinh`, `huong`, `mau_sac_vat_pham`, `bo_tri_khong_gian` | 8 cung phi và ma trận du niên 8×8; 9 sao phi tinh và Vận 9; 8 hướng, 24 sơn; màu và vật phẩm theo nạp âm; nguyên tắc bố trí 6 khu vực |
| Lịch | `lich/truc`, `nhi_thap_bat_tu`, `tiet_khi`, `ngay_kieng` | 12 Trực, 28 tú, 24 tiết khí, các ngày kiêng dân gian |
| Chọn ngày | `lich/viec` | 11 việc thường phải chọn ngày, kèm cụm từ đối chiếu với Trực và 28 tú, và danh sách ngày kiêng đủ sức loại ngày |

## Độ tin cậy

Mỗi phép tính đều có ít nhất một mốc đối chiếu độc lập, chạy tự động trong `tests/`:

| Phép tính | Cách đối chiếu | Kết quả |
|---|---|---|
| Đổi âm — dương lịch | Đối chiếu từng ngày 1800–2199 (146.097 ngày) với bản JavaScript gốc của Hồ Ngọc Đức: khớp 100%; bộ test giữ 4.630 mẫu (mỗi 37 ngày, mọi Tết, mọi tháng nhuận); thêm mốc Tết 1982–2026 và ngày 22/08/1987 = 28/7 Đinh Mão | khớp |
| Vị trí sao trên lá số | 99 sao × 60 lá số ngẫu nhiên 1930–2030 so với thư viện MIT `doanguyen/lasotuvi` (bộ mẫu lưu trong `tests/fixtures/`); Tuần — Triệt so cùng lúc. 8 sao khác trường phái và cặp Thai — Dưỡng (thư viện kia đảo) bỏ ra khỏi phép so và ghi ở SOURCES.md mục E | khớp 100% |
| Hoang Ốc | Danh sách 33 tuổi xấu được các trang phong thủy công bố | khớp từng tuổi |
| Sao hạn cửu diệu | Ví dụ "sinh năm 2000, năm 2024 gặp Kế Đô (nam) / Thái Dương (nữ)" | khớp |
| 12 Trực | 01/01/2024 là trực Kiến | khớp |
| Nhị thập bát tú | Neo 01/01/1995 (sao Hư) và kiểm chéo: sao Giác luôn rơi vào thứ Năm suốt hơn một năm | khớp |
| Bát trạch | Ma trận du niên 8×8 phải đối xứng | khớp |
| Phi tinh năm | 2024 Tam Bích, 2025 Nhị Hắc, 2026 Nhất Bạch | khớp |
| Quan hệ địa chi | Bảng 12×12 phải đối xứng; kiểm các cặp đã biết | khớp |
| Cách cục | 92 quy tắc quét trên 1.500 lá số ngẫu nhiên: cách nào không khớp lần nào là test đỏ (bắt quy tắc viết sai); bộ đọc quy tắc có test từng khóa | khớp |
| Lọc xung tuổi | Ngày 20/09/2026 đạt 95 điểm chung vẫn bị loại với tuổi Đinh Mão 1987; kết quả chọn ngày không bao giờ chứa ngày đã loại | khớp |

```bash
python -m unittest discover -s tests -v   # 84 bài kiểm thử
python scripts/validate_data.py           # kiểm tra toàn vẹn dữ liệu
```

GitHub Actions (`.github/workflows/kiem-thu.yml`) chạy pyflakes, validate_data, toàn bộ
kiểm thử, dựng SQLite và kịch bản video trên Python 3.10 và 3.13 mỗi lần push.

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

### Lồng tiếng

Giọng đọc lấy từ **edge-tts** (bộ đọc của Microsoft Edge, giọng tiếng Việt, không
cần khóa API). Mặc định dùng giọng nữ `vi-VN-HoaiMyNeural`; giọng nam là
`vi-VN-NamMinhNeural`.

```bash
python video/lam_video.py han 1987 2026 --thang-am 9 --giong vi-VN-NamMinhNeural
python video/lam_video.py han 1987 2026 --thang-am 9 --toc-do +12% --cao-do -2Hz
python video/lam_video.py han 1987 2026 --thang-am 9 --khong-giong   # xuất câm
```

Khi có giọng đọc, **độ dài thật của câu đọc quyết định độ dài cảnh** (cộng một
nhịp đệm 0,7 giây), thay cho cách ước lượng theo số chữ — chữ và tiếng khớp nhau
thay vì lệch dần. Âm thanh từng cảnh được đệm im lặng cho đủ độ dài cảnh rồi mới
ghép, nên tiếng của cảnh nào bắt đầu đúng lúc cảnh đó hiện lên.

Nếu máy chạy sau proxy có TLS re-terminate, edge-tts sẽ báo
`CERTIFICATE_VERIFY_FAILED` vì nó ghim cứng bộ CA của certifi. Đặt
`TUVI_CA_BUNDLE` trỏ tới tệp CA của proxy là xong — kho này nạp thêm CA đó vào,
không tắt xác thực chứng chỉ.

Thiếu edge-tts, hoặc mạng không ra được `speech.platform.bing.com`, thì lệnh vẫn
chạy và xuất video câm, có in rõ lý do; lời thoại nằm sẵn trong tệp kịch bản.

### Phần phụ thuộc

Ba gói chỉ cần cho khâu xuất tệp và lồng tiếng
(`pip install -r video/requirements.txt`): `playwright` để quay,
`imageio-ffmpeg` để chuyển mã, `edge-tts` để đọc. Thiếu gói nào thì bỏ đúng khâu
đó chứ không hỏng cả lệnh. Máy nào đã có `ffmpeg` trong PATH thì dùng luôn bản đó.

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

- Lá số an đủ 109 sao và Tuần — Triệt nhưng chưa có tiểu hạn, lưu niên và các sao lưu
  (Lưu Kình, Lưu Đà, Lưu Khốc, Lưu Hư...).
- Thuật toán âm lịch chính xác trong khoảng 1800–2199.
- Sinh giờ Tý (23h–1h): tính là giờ Tý của chính ngày sinh, không chuyển sang ngày hôm sau
  (SOURCES.md mục E). Giao diện, API (`canh=`) và dòng lệnh nhận cả canh giờ lẫn giờ đồng hồ.
- Sinh vào tháng nhuận: an Mệnh theo số tháng chính (cả tháng nhuận coi là tháng đó); giao
  diện có ghi chữ "nhuận" cạnh ngày âm. Trường phái chia đôi tháng nhuận chưa hỗ trợ.
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
