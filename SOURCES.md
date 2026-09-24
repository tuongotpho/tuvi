# Nguồn dữ liệu

Tài liệu này liệt kê mọi nguồn đã dùng để dựng bộ dữ liệu, kèm **tình trạng đối
chiếu** của từng bảng tra. Nguyên tắc: bảng nào tự tính ra được thì phải khớp với
một nguồn độc lập, bảng nào chỉ chép tay thì phải ghi rõ là chưa đối chiếu máy.

---

## A. Mã nguồn mở — dùng để đối chiếu thuật toán

| Mã | Nguồn | Giấy phép | Dùng vào việc gì |
|---|---|---|---|
| S-01 | Hồ Ngọc Đức — *Âm lịch Việt Nam*, `informatik.uni-leipzig.de/~duc/amlich/` | Công bố công khai, được cài lại rộng rãi | Thuật toán đổi âm — dương lịch theo múi giờ UTC+7 trong `tuvi/amlich.py` |
| S-02 | [doanguyen/lasotuvi](https://github.com/doanguyen/lasotuvi) — an sao tử vi bằng Python | MIT | Đối chiếu tự động vị trí 99 sao × 60 lá số trong `tuvi/la_so.py` (`tests/fixtures/lasotuvi_mau.json`, **tái tạo được** từ gói `lasotuvi==0.1.2` trên PyPI bằng `scripts/sinh_fixture_lasotuvi.py` — kiểm lại 22/09/2026: 5.940/5.940 vị trí khớp); trích danh mục sao và ma trận miếu vượng đắc hãm cho `data/tu_vi/sao.json`. Lưu ý S-02 ghi id 38 là "Quan phù" — thực ra là Quan Phủ vòng Lộc Tồn, kho này đã sửa |
| S-03 | [SylarLong/iztro](https://github.com/SylarLong/iztro) — thư viện Tử Vi Đẩu Số đa ngôn ngữ (JS, phái Trung Châu) | MIT | **Nguồn đối chiếu độc lập thứ hai**, không chung dòng mã với S-02: 94 sao + Mệnh, Thân, Cục, Tuần, Triệt × 60 lá số (`tests/fixtures/iztro_mau.json`, sinh bằng `scripts/sinh_fixture_iztro.js` với iztro 2.6.1). Những chỗ kho *khác* S-02 (Khôi Việt, Tứ Hóa can Canh, Phá Toái, Thai — Dưỡng) thì iztro *đồng ý với kho*. 5 sao iztro an theo phái khác ghi ở mục E. Lịch âm của iztro là lịch Trung Quốc (UTC+8): trong 60 mẫu có ca 29/6/1996 lệch kho một ngày, kho đúng theo lịch Việt Nam (xem `TestAnSaoDoiChieuIztro`) |
| S-04 | [airicyu/fortel-ziweidoushu](https://github.com/airicyu/fortel-ziweidoushu) — theo phái Trung Châu | Mã nguồn mở | Tham khảo biến thể trường phái |
| S-05 | [Renhuai123/ziwei-doushu](https://github.com/Renhuai123/ziwei-doushu) — engine kèm kho cổ tịch và hệ tứ hóa | Mã nguồn mở | Tham khảo hệ tứ hóa và kho cách cục |
| S-06 | [ruijayfeng/ziwei](https://github.com/ruijayfeng/ziwei) — ZiweiKnows | Mã nguồn mở | Tham khảo cách trình bày kết quả |
| S-07 | [Wolke/ziwei-doushu](https://github.com/Wolke/ziwei-doushu) — bản Python | Mã nguồn mở | Tham khảo |
| S-08 | [lambiengcode/astro-lens](https://github.com/lambiengcode/astro-lens) — trình đọc lá số dựa trên iztro | Mã nguồn mở | Tham khảo cách gắn luận giải vào từng cung, từng sao |
| S-09 | [kabalavn/La-So-Tu-Vi](https://github.com/kabalavn/La-So-Tu-Vi), [phongyeugame/tuvi321](https://github.com/phongyeugame/tuvi321) | Mã nguồn mở | Tham khảo |
| S-10 | [lehung1109/lich-am-duong](https://github.com/lehung1109/lich-am-duong) | Mã nguồn mở | Tham khảo cài đặt lịch âm dương |
| S-11 | [mivion/ephemeris](https://github.com/mivion/ephemeris) | Mã nguồn mở | Dự phòng nếu cần tính thiên văn chính xác hơn |

## B. Nguồn tiếng Việt trên web — dùng để đối chiếu bảng tra

Các bảng tra dân gian không có "bản chuẩn" duy nhất, nên mỗi bảng được đối chiếu
với nhiều nguồn và ghi lại điểm mâu thuẫn.

| Chủ đề | Nguồn đã tra | Ghi chú |
|---|---|---|
| Tam tai | [wiki.batdongsan.com.vn](https://wiki.batdongsan.com.vn/wiki/tam-tai-la-gi-767904), [dienmayxanh.com](https://www.dienmayxanh.com/kinh-nghiem-hay/tam-tai-la-gi-tuoi-han-tam-tai-nam-nay-1586539), [thuvienphapluat.vn](https://thuvienphapluat.vn/banan/tin-tuc/tam-tai-la-gi-nhung-tuoi-nao-gap-tam-tai-trong-nam-2025-13434), [kenh14.vn](https://kenh14.vn/nam-2026-nhung-tuoi-nao-pham-tam-tai-215251229104354088.chn) | Bốn nguồn khớp nhau hoàn toàn |
| Kim Lâu | [akisa.vn](https://akisa.vn/kim-lau.html), [thuvienphapluat.vn](https://thuvienphapluat.vn/lao-dong-tien-luong/cam-nang-di-lam/cach-tinh-tuoi-kim-lau-chinh-xac-nhat-pham-kim-lau-can-chu-y-gi-trong-cong-viec-1240.html), [luatminhkhue.vn](https://luatminhkhue.vn/tuoi-kim-lau-la-gi.aspx) | Dùng cách chia 9; các nguồn đều nêu còn 2 cách khác |
| Hoang Ốc | [homedy.com](https://homedy.com/news/tam-tai-hoang-oc-kim-lau-ne7098), [kenh14.vn](https://kenh14.vn/bang-tinh-tam-tai-hoang-oc-kim-lau-nam-2026-moi-nhat-215260108102811503.chn) | Danh sách 33 tuổi xấu được dùng làm mốc kiểm thử tự động |
| Sao hạn cửu diệu | [quantrimang.com](https://quantrimang.com/cuoc-song/bang-sao-giai-han-theo-tuoi-169419), [kientrucnamcuong.vn](https://kientrucnamcuong.vn/sao-chieu-menh/), [tuvicaimenh.com](https://tuvicaimenh.com/y-nghia-9-sao-cuu-dieu), [vietlac.net](https://vietlac.net/chi-tiet-9-sao-chieu-menh-tuoi-trong-nam) | Đối chiếu bằng ví dụ "người sinh năm 2000, năm 2024 gặp Kế Đô (nam) / Thái Dương (nữ)" |
| Cung phi bát trạch | [wiki.batdongsan.com.vn](https://wiki.batdongsan.com.vn/wiki/cung-phi-la-gi-768289), [ngayamlich.com](https://ngayamlich.com/cach-tinh-cung-phi-bat-trach/), [meeyland.com](https://meeyland.com/tin-tuc/cach-tinh-cung-phi-bat-tu-00937739870) | Công thức trước/sau năm 2000 khớp nhau |
| Bát trạch — du niên | [phongthuynamviet.com.vn](http://phongthuynamviet.com.vn/phong-thuy-bat-trach-dai-du-nien-bat-bien.html), [xaydung365.com.vn](https://xaydung365.com.vn/y-nghia-8-cung-trong-phong-thuy-bat-trach-n326.html), [kasai.com.vn](https://kasai.com.vn/sinh-khi-thien-y-dien-nien-phuc-vi-la-gi.html) | Ma trận 8×8 được kiểm tra tính đối xứng bằng máy |
| 12 Trực | [ngaydep.io](https://ngaydep.io/blog/thap-nhi-kien-tru), [xemtuong.net](http://xemtuong.net/baiviet.php?id=-12-truc-va-ngay-tot-xau-12-truc-) | Đối chiếu bằng mốc 01/01/2024 là trực Kiến |
| Nhị thập bát tú | [Wikipedia tiếng Việt](https://vi.wikipedia.org/wiki/Nh%E1%BB%8B_th%E1%BA%ADp_b%C3%A1t_t%C3%BA), [dangnho.com](https://dangnho.com/kien-thuc/phong-tuc/cach-tinh-ngay-tiet-ngay-truc-va-ngay-nhi-thap-bat-tu.html), [nghiencuulichsu.com](https://nghiencuulichsu.com/2016/08/10/so-luoc-ve-nhi-thap-bat-tu-trong-tai-lieu-lich-phap-han-nom/), [xemtuong.net](http://xemtuong.net/baiviet.php?id=-cach-tinh-ngay-tiet-ngay-truc-va-ngay-nhi-thap-bat-tu-) | Mốc neo: 01/01/1995 là Chủ nhật, sao Hư (sao thứ 11) |
| Ngày/giờ hoàng đạo | [xemvm.com](https://xemvm.com/kien-thuc-phong-thuy/xem-ngay/ngay-hoang-dao-va-gio-hac-dao-503.html), [hocvienlyso.org](https://hocvienlyso.org/https-sonchu-vn-chon-ngay-tot-theo-hoang-dao-hac-dao.html) | Bảng giờ hoàng đạo được kiểm lại với cả 6 nhóm chi ngày |
| Thuật toán âm lịch | [lyso.vn](https://lyso.vn/co-ban/thuat-toan-tinh-am-lich-ho-ngoc-duc-t2093/), [tuvilyso.org](https://tuvilyso.org/forum/topic/36498-thuat-toan-tinh-am-lich/), [xemamlich.uhm.vn](https://www.xemamlich.uhm.vn/calrules.html) | Bản chép lại thuật toán S-01 |

> **Cảnh báo về chất lượng nguồn web.** Nhiều trang tin thương mại chép lẫn nhau và
> sai cả những chi tiết cơ bản. Ví dụ đã gặp trong quá trình đối chiếu: một trang
> ghi tuổi Ất Mão 1975 là "Thành Đầu Thổ" (đúng phải là **Đại Khê Thủy**) và Canh
> Thân 1980 là "Tuyền Trung Thủy" (đúng phải là **Thạch Lựu Mộc**). Vì vậy bảng
> nạp âm trong kho này lấy từ Lục thập hoa giáp gốc và được kiểm thử tự động.

## C. Sách và cổ tịch — nguồn gốc của tri thức, không tra online được

Các tài liệu dưới đây là gốc của phần lớn bảng tra. Kho này **không** chép nội dung
có bản quyền từ chúng; chỉ dùng phần tri thức truyền thống đã thuộc phạm vi công cộng.

**Tử vi**
- *Tử Vi Đẩu Số Toàn Thư* — tương truyền Trần Đoàn, La Hồng Tiên biên soạn
- *Tử Vi Đẩu Số Tinh Thành* — Vũ Tài Lục
- *Tử Vi Hàm Số* — Nguyễn Phát Lộc
- *Tử Vi Nghiệm Lý* — Thiên Lương (nguồn của biến thể an vòng Tràng Sinh)

**Phong thủy**
- *Bát Trạch Minh Cảnh* — gốc của bảng Đại du niên bát biến
- *Thẩm Thị Huyền Không Học* — gốc của hệ cửu cung phi tinh
- *Dương Trạch Tam Yếu*

**Chọn ngày**
- *Ngọc Hạp Thông Thư*
- *Hiệp Kỷ Biện Phương Thư*
- *Lịch vạn niên* (nhiều bản lưu hành ở Việt Nam, khác nhau ở bảng Sát chủ)

## D. Kết quả đối chiếu chéo hai nguồn mã (22/09/2026)

Cùng 60 lá số (âm lịch, giờ theo chi, giới tính), so `tuvi/la_so.py` với hai bộ mã
độc lập nhau:

| Nguồn | Phạm vi so | Khớp | Lệch | Kết luận |
|---|---|---|---|---|
| S-02 lasotuvi 0.1.2 (Python, Việt Nam) | 99 sao + Tuần Triệt | 5.940 / 5.940 | 0 | Fixture tái tạo được, không phải file chép tay |
| S-03 iztro 2.6.1 (JS, Trung Châu) | 105 mục (sao, Mệnh, Thân, Cục, Tuần, Triệt) | 99 mục khớp 60/60 | 5 sao khác phái + 1 mục ánh xạ sai tên | Toàn bộ 14 chính tinh, Tứ Hóa, Lộc Tồn — Kình Đà, Khôi Việt, Xương Khúc, Tả Hữu, Không Kiếp, ba vòng Tràng Sinh / Bác Sĩ / Thái Tuế khớp cả hai nguồn |

Năm sao lệch với iztro đều là khác trường phái đã tra lại nguồn Việt (mục E), không
phải lỗi tính. Ca 29/6/1996 lệch ngày dương là do lịch Trung Quốc (UTC+8) khác lịch
Việt Nam (UTC+7) đúng tháng đó — kho đúng.

Cách chạy lại (không cần cho CI, fixture đã nằm trong kho):

```bash
pip install --no-deps --target build/lasotuvi lasotuvi==0.1.2
python scripts/sinh_fixture_lasotuvi.py --kiem-tra
npm install --no-save iztro@2.6.1
node scripts/sinh_fixture_iztro.js --kiem-tra
```

## E. Trường phái đang dùng

Khi các trường phái khác nhau, kho này chọn như sau và ghi chú ngay trong mã:

| Vấn đề | Lựa chọn của kho | Biến thể khác |
|---|---|---|
| Kim Lâu | Tuổi mụ chia 9, dư 1/3/6/8 | Theo hàng đơn vị của tuổi; theo bàn tay |
| Thiên Khôi — Thiên Việt | Khẩu quyết "Giáp Mậu Canh ngưu dương..." | S-02 dùng bảng khác cho Đinh, Mậu, Canh |
| Vòng Tràng Sinh | Dương nam / Âm nữ an thuận | Phái Thiên Lương: nam thuận, nữ nghịch |
| Tứ Hóa can Canh | Thái Dương — Vũ Khúc — Thái Âm — Thiên Đồng | Một số phái đổi chỗ Khoa và Kỵ |
| Sát chủ | Không cung cấp | Mỗi cuốn lịch một bảng |
| Hỏa Tinh — Linh Tinh tuổi Tỵ Dậu Sửu | Hỏa khởi Mão, Linh khởi Tuất | S-02 khởi Hỏa Tuất, Linh Mão |
| Phá Toái | Tý Ngọ Mão Dậu tại Tỵ; Dần Thân Tỵ Hợi tại Dậu; Thìn Tuất Sửu Mùi tại Sửu | S-02 đảo hai nhóm đầu |
| Thiên Giải | Khởi Thân là tháng Giêng, đếm thuận từng cung đến tháng sinh | S-02 đếm nhảy hai cung một tháng |
| Thai — Dưỡng | Thứ tự Tuyệt — Thai — Dưỡng — Tràng Sinh | S-02 đặt Dưỡng trước Thai (S-03 khớp kho) |
| Giải Thần | An theo chi năm, đồng cung Phượng Các (S-02 khớp) | S-03 / phái Trung Quốc: an theo tháng sinh, hai tháng một cung (Thân Thân Tuất Tuất Tý Tý…) |
| Thiên Quý | Từ Văn Khúc kể mùng 1 đếm **nghịch** đến ngày sinh rồi lùi lại một cung (S-02 khớp) | S-03: đếm **thuận** rồi lùi một cung |
| Thiên Trù can Quý | Tại **Tuất** (S-02 và các nguồn Việt: phongthuythanhhoa.vn, tuvidonga.com) | Khẩu quyết Trung Quốc "Nhâm kê Quý trư đường" → Hợi; S-03 theo đó |
| Hỏa Tinh — Linh Tinh | Chỉ theo chi năm sinh | S-03 / Trung Châu: theo chi năm **và** giờ sinh, khác kho ở khoảng 40% lá số |
| Sinh giờ Tý (23h—1h) | Là giờ Tý của chính ngày sinh, không đổi sang ngày hôm sau | Một số thầy tính từ 23h là ngày mới; phái khác tách Dạ Tý / Sớm Tý |
| Sinh tháng nhuận | Cả tháng nhuận tính theo số tháng chính khi an Mệnh — Thân | Nửa đầu về tháng trước, nửa sau về tháng sau |

## F. Những gì KHÔNG tìm được

Ghi lại để lần sau khỏi tìm lại:

1. **Không có API miễn phí, ổn định** cho tử vi hoặc lịch vạn niên tiếng Việt.
   Mọi dịch vụ tìm thấy đều là trang web đóng, không có tài liệu API công khai.
2. **Không có bộ dữ liệu mở** dạng CSV/JSON cho 109 sao tử vi kèm luận giải tiếng
   Việt. Phần ý nghĩa trong `data/tu_vi/sao.json` được viết mới cho kho này.
3. **Bảng Sát chủ** có quá nhiều dị bản mâu thuẫn nên đã chủ động bỏ ra khỏi kho
   (xem ghi chú trong `data/lich/ngay_kieng.json`).
4. Trong phiên làm việc dựng kho này, phần lớn tên miền tiếng Việt bị chính sách
   mạng của môi trường chặn, nên việc đối chiếu dựa vào kết quả tìm kiếm và vào mã
   nguồn mở tải được từ GitHub. Khi có điều kiện truy cập đầy đủ, nên tra lại trực
   tiếp các bảng ở mục B.

## G. Xem hợp tuổi — rà lại phần thêm ngày 23/09/2026 (rà 24/09/2026)

Commit `9c9552d` (AI Studio) thêm nhiều nội dung cho tab Hợp tuổi. Từng khẳng định
đã được đối chiếu; cái nào sai hoặc không tìm được nguồn thì đã bỏ.

**Giữ lại (có nguồn):**

| Nội dung | Nguồn | Ghi chú |
|---|---|---|
| Cao Ly Đầu Hình — 120 lời "Nam dụng Can, Nữ dụng Chi" | [xemtuong.net](https://xemtuong.net/caolydauhinh/) (chép), [giadinh.kabala.vn](https://giadinh.kabala.vn/vochong/caolydauhinh/) (đối chiếu) | 119/120 cặp khớp từng chữ giữa hai trang. Cặp Nhâm–Thìn: trang kabala trả nhầm lời của Giáp–Thìn, nên chỉ có một nguồn; lời trên xemtuong tự ghi "Chồng chữ Nhâm cưới vợ tuổi Thìn". Tái tạo bằng `scripts/tai_cao_ly_dau_hinh.py`. Kho không chấm điểm phần này |
| Ngũ hợp thiên can và tên gọi | Tam Mệnh Thông Hội, mục "Luận thập can hợp" ([ctext](https://ctext.org/wiki.pl?if=gb&res=532360), [douban](https://www.douban.com/note/872484995/)) | Giáp Kỷ Trung Chính, Ất Canh Nhân Nghĩa, Bính Tân Uy Chế, **Đinh Nhâm Dâm Nặc, Mậu Quý Vô Tình** |
| Tứ xung thiên can: Giáp Canh, Ất Tân, Bính Nhâm, Đinh Quý | [sohu](https://www.sohu.com/a/820430356_100084723), [163.com](https://c.m.163.com/news/a/HGLS7IBU0553JRPR.html) | Mậu Kỷ không xung |
| Nạp âm "không sợ" hành khắc mình: Kiếm Phong Kim–Hỏa; Thiên Hà Thủy, Đại Hải Thủy–Thổ; Thiên Thượng Hỏa, Tích Lịch Hỏa–Thủy | [lyso.vn](https://lyso.vn/tong-hop/sinh-khac-cua-ngu-hanh-nap-am-tiep-theo-bai-2-t38279/), [a-site.cn](https://www.a-site.cn/article/1847598.html), [tuvikhoahoc.vn](https://tuvikhoahoc.vn/kiem-phong-kim), [tramhuongthuanchay.com](https://tramhuongthuanchay.com/n3761/menh-thien-thuong-hoa-menh-hoa-manh-nhat-khong-can-moc-de-tuong-sinh-cung-khong-bi-thuy-khac-che.html) | Chỉ giữ nạp âm có ít nhất hai nguồn. Chỉ là ghi chú, **không đổi điểm** — Tam Mệnh Thông Hội mục "Luận nạp âm thủ tượng" không có quy tắc này |
| Hành trung gian khi hai mệnh khắc (A khắc B → A sinh C, C sinh B) và chọn năm sinh con mang hành đó | [lichviet.app](https://lichviet.app/xem-tuoi-vo-chong-tot-xau-qua-ngu-hanh) | Điểm xếp năm sinh con là quy ước của kho |

**Đã bỏ:**

| Nội dung bản 23/09 | Vì sao bỏ |
|---|---|
| 120 "cách cục" Cao Ly kèm thơ, luận, đánh giá, điểm | **Tự viết, không phải văn xưa.** So với hai trang tra cứu thì khác hoàn toàn (vd. Quý–Dậu: bản gốc có "chung cuộc phải gặp nạn", bản AI chỉ toàn lời khen). Đánh giá lệch: 102/120 cặp "tốt" hoặc "rất tốt", không cặp nào xấu. Thay bằng lời gốc ở trên |
| Tên ngũ hợp "Nhân Thọ" (Đinh Nhâm), "Đa Lễ" (Mậu Quý) và câu diễn giải từng cặp | Sai tên so với Tam Mệnh Thông Hội; lời diễn giải tự viết |
| "Thiên Thượng Hỏa gặp Thổ không bị ngăn trở"; "Sa Trung Kim gặp Hỏa thành khí" | Gán nhầm nhóm (Thiên Thượng Hỏa là chuyện gặp Thủy). Sa Trung Kim thì các nguồn nói ngược nhau |
| "Chồng sinh vợ là thuận lý âm dương", "vợ sinh chồng vượng phu", "vợ khắc chồng là nghịch lý, vợ nên nhu thuận" | Nguồn ngược nhau: [giangphongthuy.com](https://giangphongthuy.com/menh-vo-menh-chong-the-nao-la-hop-the-nao-la-xung-khac/) cho chồng sinh vợ là "bình thường", lichviet.app lại gọi chồng Kim vợ Thủy là "hòa hợp"; lichviet.app coi chồng Kim vợ Mộc là khắc chứ không "thuận". Lời khuyên cho vợ là tự thêm |
| "Cung sinh" (công thức hai năm liền nhau chung một cung, nam nữ như nhau) | Không tìm được nguồn cho công thức; các nguồn Việt chỉ dùng cung phi theo giới tính |
| Phần "làm ăn": Quý Nhân, Lộc Tồn, Thiên Mã chéo giữa hai người; chia vai theo ngũ hành | Các trang Việt xem tuổi làm ăn ([reatimes](https://reatimes.vn/cach-tu-xem-tuoi-hop-nhau-trong-lam-an-kinh-doanh-20234319.htm), [tuvi.vn](https://tuvi.vn/xem-tuoi-lam-an)) chỉ dùng mệnh, can chi, cung. Bảng tra Quý Nhân, Lộc Tồn thì đúng (trùng bảng lõi) nhưng cách dùng chéo không có nguồn; chia vai là tự nghĩ ra. Ô "Mục đích xem" vẫn giữ: chọn làm ăn thì chỉ xét bốn mặt, bỏ phần riêng của vợ chồng |
| Hóa giải Bát trạch áp vào tuổi vợ chồng, và câu "Phục Vị an Họa Hại" | Sách Bát Trạch Minh Cảnh chỉ có ba câu (Sinh Khí giáng Ngũ Quỷ, Thiên Y chế Tuyệt Mệnh, Diên Niên áp Lục Sát), dùng cho **hướng cửa – hướng bếp của nhà**, không phải cho hai tuổi. Câu thứ tư không có |
| Hóa giải lục xung "đeo linh vật", hóa giải lục hại, "Tứ hành xung… có thể còn là nhị hợp hoặc vô hại" | Không có nguồn; câu cuối còn sai (trong nhóm tứ hành xung có nhiều cặp hình, hại, phá) |
| Thang điểm 10, "tỉ lệ hợp %", xếp loại "Thứ Cát" | Số tự đặt, trông như xác suất nhưng không phải; "Thứ Cát" (cát hạng hai) lại được gắn cho điểm âm |
| Năm sinh con cố định 2026–2031, nhãn "Cầu nối vàng… hóa giải hoàn toàn" | Năm viết cứng; lời hứa "hoàn toàn" không có nguồn. Nay lấy năm hiện tại |
