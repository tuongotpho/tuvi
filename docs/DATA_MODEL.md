# Mô hình dữ liệu

## Nguyên tắc

1. **JSON là nguồn sự thật.** SQLite chỉ là bản dựng lại, xóa đi dựng lại lúc nào cũng được.
2. **Dữ liệu không chứa logic.** Mọi phép tính nằm trong gói `tuvi/`, dữ liệu chỉ mô tả.
3. **Khóa tiếng Việt không dấu.** Tên trường dùng chữ thường, không dấu, nối bằng gạch dưới
   (`nap_am`, `tinh_chat`); giá trị thì giữ nguyên dấu tiếng Việt.
4. **Chỗ nào có nhiều trường phái thì phải có trường ghi chú.** Không im lặng chọn một bản.

## Sơ đồ phụ thuộc

```
amlich.py            đổi âm - dương lịch (thuật toán Hồ Ngọc Đức)
   |
canchi.py            can chi năm/tháng/ngày/giờ, nạp âm, tiết khí
   |
   +-- ngay_gio.py   12 Trực, 28 tú, hoàng đạo, ngày kiêng
   |      |
   |      +-- chon_ngay.py  lọc xung tuổi, chấm điểm theo việc
   +-- han.py        sao hạn, tam tai, Kim Lâu, Hoang Ốc, Thái Tuế
   +-- phong_thuy.py cung phi, du niên, phi tinh
   +-- la_so.py      lập lá số tử vi rút gọn
   |
store.py             nạp JSON trong data/, có cache
```

## Quy ước chỉ số

| Đại lượng | Quy ước | Ví dụ |
|---|---|---|
| Địa chi | 0-based, Tý = 0 | Dần = 2, Hợi = 11 |
| Thiên can | 0-based, Giáp = 0 | Canh = 6 |
| Lục thập hoa giáp | 0-based, Giáp Tý = 0 | Quý Hợi = 59 |
| Giờ | Chỉ số địa chi, giờ Tý là 23:00–00:59 | 16:00 -> chi 8 (Thân) |
| Tháng âm lịch | 1–12, tháng Giêng là tháng Dần | |
| Tuổi | **Tuổi mụ** = năm xem − năm sinh + 1 | dùng cho mọi phép xem hạn |
| Năm sinh | Luôn là **năm âm lịch** | sinh trước Tết thì thuộc năm trước |

Sai lầm hay gặp nhất khi dùng kho này: đưa vào năm dương lịch của người sinh trong
tháng 1 hoặc đầu tháng 2. Hãy đổi sang năm âm lịch bằng `solar_to_lunar` trước.

## Các bộ dữ liệu

### Nền tảng

- **`ngu_hanh.json`** — mảng 5 phần tử. Khóa chính `hanh`. Có `sinh`, `khac`,
  `duoc_sinh_boi`, `bi_khac_boi` để dựng quan hệ; kèm màu, hướng, mùa, số, tạng phủ,
  tính cách, nghề nghiệp phục vụ viết bài.
- **`thien_can.json`** — 10 can, kèm `hop` (ngũ hợp) và `xung`. Mậu và Kỷ có
  `xung = null` vì thuộc Thổ ở trung cung, không kể tương xung.
- **`dia_chi.json`** — 12 chi, kèm `tam_hop`, `tu_hanh_xung`, `luc_hop`, `luc_xung`,
  `luc_hai`, giờ, tháng âm lịch, hướng.
- **`luc_thap_hoa_giap.json`** — 60 bản ghi, sinh ra từ `tuvi.canchi.luc_thap_hoa_giap()`.
- **`nap_am.json`** — 30 hành nạp âm, mỗi hành gắn với đúng 2 cặp can chi.

### Tử vi

- **`tu_vi/sao.json`** — 109 sao. `id` khớp với id trong `doanguyen/lasotuvi` (riêng id 38
  bên đó ghi nhầm "Quan phù", kho này là Quan Phủ vòng Lộc Tồn) nên
  ghép được với bộ an sao đầy đủ của thư viện đó. Trường `mieu_vuong_dac_ham` là
  dict `{chi: "Miếu"|"Vượng"|"Đắc"|"Bình"|"Hãm"}`, chỉ 29 sao có bảng này.
  Tên "Quan phù" xuất hiện ở hai vòng sao khác nhau nên có thêm `ten_hien_thi`.
- **`tu_vi/cung.json`** — 12 cung chức theo thứ tự ngược chiều kim đồng hồ kể từ Mệnh.
- **`tu_vi/cach_cuc.json`** — 20 cách cục, mỗi cách có `dieu_kien` viết bằng lời để
  người biên tập tự đối chiếu (chưa mã hóa thành luật máy).

### Hạn

- **`han/sao_han.json`** — `thu_tu_nam` và `thu_tu_nu` là hai mảng 9 phần tử, tra
  bằng `(tuoi_mu - 10) % 9`. Hai giới dùng chung mốc tuổi, chỉ khác thứ tự sao.
- **`han/hoang_oc.json`** — `tuoi_xau_tham_khao` là danh sách 33 tuổi do các nguồn
  công bố; `tests/` dùng chính danh sách này để kiểm công thức, nên đừng sửa tay.
- **`han/tam_tai.json`** — 4 nhóm tam hợp phủ đúng 12 chi.

### Phong thủy

- **`phong_thuy/bat_trach.json`** — `cung[].du_nien` là dict 8 hướng cho mỗi cung phi,
  tổng cộng ma trận 8×8. Ma trận này **phải đối xứng**: quan hệ giữa hai cung nhìn từ
  hai phía phải cho cùng một du niên. `scripts/validate_data.py` kiểm điều này.
- **`phong_thuy/cuu_cung_phi_tinh.json`** — `lac_thu` là bản đồ hướng sang số Lạc thư,
  dùng để bay sao: `sao_tai_huong = (so_lac_thu + sao_trung_cung - 5 - 1) % 9 + 1`.

### Lịch

- **`lich/truc.json`** — 12 Trực. Trực tính bằng khoảng cách giữa chi ngày và nguyệt
  kiến (tháng theo tiết khí, không phải tháng âm lịch).
- **`lich/nhi_thap_bat_tu.json`** — 28 tú. Trường `thu_trong_tuan` là bất biến kiểm
  chứng được: vòng 28 tú khớp cứng với thứ trong tuần.
- **`lich/ngay_kieng.json`** — có mục Sát chủ nhưng cố ý không kèm bảng, kèm cảnh báo.
- **`lich/viec.json`** — 11 việc phải chọn ngày. Mỗi việc có `cum_tu` (các cụm từ
  dùng để đối chiếu) và `kieng` (loại ngày xấu đủ sức loại thẳng ngày đó).
  Đối chiếu dùng so khớp **chính xác**, không dùng chuỗi con: `"động thổ"` và
  `"động thổ đào huyệt"` là hai việc khác hẳn nhau, so khớp chuỗi con sẽ làm ngày
  kỵ đào huyệt bị tính nhầm thành ngày kỵ xây nhà. `validate_data.py` bắt buộc mọi
  cụm từ phải tồn tại trong `lich/truc.json` hoặc `lich/nhi_thap_bat_tu.json`.

## Cách chấm điểm khi chọn ngày

`chon_ngay` không gộp mọi thứ vào một con số mờ mịt: mỗi khoản cộng trừ đều được
trả về kèm lý do trong `khoan_cong_tru`, để người đọc tự kiểm.

Điểm nền là `diem_tong_hop` của `xem_ngay` (trực, 28 tú, hoàng đạo, ngày kiêng).
Trên nền đó cộng trừ theo `trong_so` trong `lich/viec.json`:

| Khoản | Điểm |
|---|---|
| Trực hợp việc / kỵ việc | +12 / −18 |
| Sao 28 tú hợp việc / kỵ việc | +12 / −18 |
| Ngày tam hợp hoặc lục hợp với tuổi | +8 |
| Ngày trùng chi tuổi | −6 |
| Tự hình | −10 |
| Lục hại, lục phá | −12 |
| Tương hình | −15 |
| Tháng âm lịch là tháng kỵ của sao hạn năm đó | −12 |

Hai trường hợp **không tính điểm mà loại thẳng**, vì lệ cũ không dùng những ngày
này dù mọi yếu tố khác có đẹp:

1. Ngày lục xung với chi tuổi, hoặc thiên khắc địa xung (can ngày khắc can tuổi
   **và** chi ngày xung chi tuổi).
2. Ngày nằm trong danh sách `kieng` của chính việc đó.

Danh sách `kieng` khác nhau theo việc và điều đó là có chủ ý: việc dương như cưới
hỏi hay động thổ kiêng cả bốn loại ngày xấu, an táng chỉ kiêng Thọ tử và Dương công
kỵ nhật, còn chữa bệnh không kiêng ngày nào — sức khỏe không chờ ngày tốt.

## Bảng SQLite

`scripts/build_db.py` dựng 22 bảng. Trường nào vốn là mảng hoặc dict thì lưu dưới
dạng chuỗi JSON, truy vấn bằng `json_extract` hoặc `json_each`:

```sql
SELECT ten FROM con_giap
WHERE EXISTS (SELECT 1 FROM json_each(con_giap.mau_hop) WHERE value = 'xanh lá');

SELECT tuoi_mu, sao FROM sao_han_theo_tuoi WHERE gioi_tinh = 'nu' AND sao = 'Thái Bạch';
```

Bảng `sao_han_theo_tuoi` là bảng dựng sẵn cho tuổi mụ 10–100, tiện khi cần tra nhanh
mà không muốn chạy Python.

## Thêm dữ liệu mới

1. Thêm tệp JSON vào `data/`, đặt tên theo nhóm thư mục sẵn có.
2. Nếu cần lên SQLite thì thêm bảng trong `SCHEMA` và phần chèn dữ liệu ở
   `scripts/build_db.py`.
3. Thêm kiểm tra vào `scripts/validate_data.py` — ít nhất là số lượng bản ghi và
   một mốc đối chiếu bên ngoài.
4. Ghi nguồn vào `SOURCES.md`, kèm tình trạng đối chiếu.
