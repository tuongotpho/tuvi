# -*- coding: utf-8 -*-
"""Kiểm thử các phép tính lõi.

    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tuvi import chon_ngay, han, la_so, ngay_gio, phong_thuy  # noqa: E402
from tuvi.amlich import lunar_to_solar, solar_to_lunar  # noqa: E402
from tuvi.canchi import (DIA_CHI, can_chi_ngay, can_chi_nam,  # noqa: E402
                         can_chi_thang, chi_gio_tu_gio_phut, luc_thap_hoa_giap,
                         luc_xung, quan_he_chi)
from tuvi.store import all_datasets, load  # noqa: E402


class TestAmLich(unittest.TestCase):
    def test_doi_ngay_da_biet(self):
        self.assertEqual(solar_to_lunar(1, 1, 2024)[:3], (20, 11, 2023))
        self.assertEqual(tuple(lunar_to_solar(1, 1, 2026)), (17, 2, 2026))
        self.assertEqual(tuple(lunar_to_solar(1, 1, 2024)), (10, 2, 2024))

    def test_khu_hoi(self):
        """Đổi xuôi rồi đổi ngược phải ra đúng ngày ban đầu."""
        for y in range(1950, 2051, 7):
            for m, d in ((1, 15), (5, 3), (9, 28), (12, 31)):
                am = solar_to_lunar(d, m, y)
                lai = lunar_to_solar(am.day, am.month, am.year, am.leap)
                self.assertEqual(tuple(lai), (d, m, y), f"{d}/{m}/{y}")


class TestCanChi(unittest.TestCase):
    def test_can_chi_nam(self):
        self.assertEqual(can_chi_nam(2026).ten, "Bính Ngọ")
        self.assertEqual(can_chi_nam(1990).ten, "Canh Ngọ")
        self.assertEqual(can_chi_nam(1945).ten, "Ất Dậu")

    def test_nap_am(self):
        self.assertEqual(can_chi_nam(1990).nap_am, "Lộ Bàng Thổ")
        self.assertEqual(can_chi_nam(1975).nap_am, "Đại Khê Thủy")
        self.assertEqual(can_chi_nam(1980).nap_am, "Thạch Lựu Mộc")

    def test_hoa_giap_day_du(self):
        bang = luc_thap_hoa_giap()
        self.assertEqual(len(bang), 60)
        self.assertEqual(len({r["ten"] for r in bang}), 60)
        self.assertEqual(len({r["nap_am"] for r in bang}), 30)

    def test_can_chi_ngay_va_thang(self):
        jd = solar_to_lunar(1, 1, 2024).jd
        self.assertEqual(can_chi_ngay(jd).ten, "Giáp Tý")
        self.assertEqual(can_chi_thang(2024, 1).ten, "Bính Dần")

    def test_chi_gio(self):
        self.assertEqual(chi_gio_tu_gio_phut(23, 30), 0)   # giờ Tý
        self.assertEqual(chi_gio_tu_gio_phut(0, 30), 0)
        self.assertEqual(chi_gio_tu_gio_phut(12, 0), 6)    # giờ Ngọ
        self.assertEqual(chi_gio_tu_gio_phut(16, 0), 8)    # giờ Thân


class TestNgayGio(unittest.TestCase):
    def test_truc_va_tu(self):
        self.assertEqual(ngay_gio.xem_ngay(1, 1, 2024)["truc"], "Kiến")
        self.assertEqual(ngay_gio.xem_ngay(1, 1, 1995)["nhi_thap_bat_tu"], "Hư")
        # Vòng 28 tú khớp với thứ trong tuần: Giác luôn rơi vào thứ Năm.
        tu = load("lich/nhi_thap_bat_tu")
        thu = {r["ten"]: r["thu_trong_tuan"] for r in tu}
        import datetime
        for i in range(0, 400, 13):
            d = datetime.date(2026, 1, 1) + datetime.timedelta(days=i)
            r = ngay_gio.xem_ngay(d.day, d.month, d.year)
            ten_thu = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu",
                       "Thứ Bảy", "Chủ nhật"][d.weekday()]
            self.assertEqual(thu[r["nhi_thap_bat_tu"]], ten_thu, str(d))

    def test_gio_hoang_dao_luon_sau_khung(self):
        for d, m, y in [(1, 1, 2024), (15, 6, 2025), (20, 9, 2026)]:
            r = ngay_gio.xem_ngay(d, m, y)
            self.assertEqual(len(r["gio_hoang_dao"]), 6)
            self.assertEqual(len(r["gio_hac_dao"]), 6)

    def test_ngay_kieng(self):
        # Mùng 5 âm lịch luôn phạm nguyệt kỵ.
        from tuvi.amlich import lunar_to_solar
        d, m, y = lunar_to_solar(5, 3, 2026)
        self.assertIn("Nguyệt kỵ", ngay_gio.xem_ngay(d, m, y)["ngay_kieng"])


class TestHan(unittest.TestCase):
    def test_sao_han_doi_chieu_nguon(self):
        self.assertEqual(han.sao_han(2000, 2024, "nam")["sao"], "Kế Đô")
        self.assertEqual(han.sao_han(2000, 2024, "nu")["sao"], "Thái Dương")

    def test_sao_han_lap_sau_9_nam(self):
        for t in range(10, 90):
            a = han.sao_han(1990, 1990 + t - 1, "nam")["sao"]
            b = han.sao_han(1990, 1990 + t - 1 + 9, "nam")["sao"]
            self.assertEqual(a, b)

    def test_hoang_oc_khop_bang_cong_bo(self):
        cong_bo = load("han/hoang_oc")["tuoi_xau_tham_khao"]
        tinh = [t for t in range(10, 76) if han.hoang_oc(t)["pham"]]
        self.assertEqual(tinh, cong_bo)

    def test_kim_lau(self):
        self.assertEqual(han.kim_lau(37)["ten"], "Kim Lâu Thân")    # 37 % 9 = 1
        self.assertEqual(han.kim_lau(33)["ten"], "Kim Lâu Tử")      # 33 % 9 = 6
        self.assertFalse(han.kim_lau(38)["pham"])                   # 38 % 9 = 2

    def test_tam_tai(self):
        # Tuổi Thân Tý Thìn gặp tam tai vào các năm Dần, Mão, Thìn.
        r = han.tam_tai("Tý", "Dần")
        self.assertTrue(r["pham"])
        self.assertEqual(r["nam_thu"], 1)
        self.assertFalse(han.tam_tai("Tý", "Ngọ")["pham"])

    def test_thai_tue_nam_tuoi(self):
        r = han.thai_tue("Ngọ", "Ngọ")
        self.assertIn("Bản mệnh Thái Tuế (năm tuổi)", r["cac_dang"])
        self.assertIn("Xung Thái Tuế", han.thai_tue("Ngọ", "Tý")["cac_dang"])


class TestPhongThuy(unittest.TestCase):
    def test_cung_phi(self):
        for nam, gt, mong_doi in [(1990, "nam", "Khảm"), (1990, "nu", "Cấn"),
                                  (1985, "nam", "Càn"), (1985, "nu", "Ly"),
                                  (2000, "nam", "Ly"), (2000, "nu", "Càn")]:
            self.assertEqual(phong_thuy.cung_phi(nam, gt)["cung_phi"], mong_doi,
                             f"{gt} {nam}")

    def test_bon_huong_tot_bon_huong_xau(self):
        for cung in ["Khảm", "Ly", "Chấn", "Tốn", "Càn", "Khôn", "Cấn", "Đoài"]:
            r = phong_thuy.huong_theo_cung(cung)
            self.assertEqual(len(r["huong_tot"]), 4)
            self.assertEqual(len(r["huong_xau"]), 4)

    def test_du_nien_doi_xung(self):
        bt = load("phong_thuy/bat_trach")
        huong = {c["ten"]: c["huong"] for c in bt["cung"]}
        bang = {c["ten"]: c["du_nien"] for c in bt["cung"]}
        for a in bang:
            for b in bang:
                self.assertEqual(bang[a][huong[b]], bang[b][huong[a]],
                                 f"{a} <-> {b}")

    def test_phi_tinh_nam(self):
        for nam, so in [(2024, 3), (2025, 2), (2026, 1), (2027, 9)]:
            self.assertEqual(
                phong_thuy.phi_tinh_nam(nam)["sao_nhap_trung_cung"], so)


class TestLaSo(unittest.TestCase):
    def test_moi_chinh_tinh_mot_lan(self):
        for d, m, y, g, gt in [(20, 9, 1990, 14, "nam"), (1, 1, 2000, 2, "nu"),
                               (29, 2, 2004, 23, "nam"), (7, 7, 2003, 12, "nam")]:
            ls = la_so.lap_la_so(d, m, y, g, gioi_tinh=gt)
            dem = {}
            for c in ls["cac_cung"]:
                for s in c["sao"]:
                    if s["nhom"] == "Chính tinh":
                        dem[s["ten"]] = dem.get(s["ten"], 0) + 1
            self.assertEqual(len(dem), 14)
            self.assertEqual(set(dem.values()), {1})

    def test_du_12_cung(self):
        ls = la_so.lap_la_so(20, 9, 1990, 14, gioi_tinh="nam")
        self.assertEqual(len(ls["cac_cung"]), 12)
        self.assertEqual({c["ten_cung"] for c in ls["cac_cung"]},
                         set(la_so.TEN_CUNG))
        self.assertEqual(len({c["chi"] for c in ls["cac_cung"]}), 12)

    def test_can_cung_theo_ngu_ho_don(self):
        # Năm Canh: tháng Giêng là Mậu Dần, nên cung Sửu phải là Kỷ Sửu.
        ls = la_so.lap_la_so(20, 9, 1990, 16, gioi_tinh="nam")
        cung_suu = next(c for c in ls["cac_cung"] if c["chi"] == "Sửu")
        self.assertEqual(cung_suu["can"], "Kỷ")
        self.assertEqual(ls["cuc"], "Hỏa 6 cục")

    def test_tu_hoa_du_bon(self):
        ls = la_so.lap_la_so(20, 9, 1990, 14, gioi_tinh="nam")
        self.assertEqual(set(ls["tu_hoa"]),
                         {"Hóa Lộc", "Hóa Quyền", "Hóa Khoa", "Hóa Kỵ"})


class TestQuanHeChi(unittest.TestCase):
    def test_luc_xung(self):
        for a, b in [("Tý", "Ngọ"), ("Sửu", "Mùi"), ("Dần", "Thân"),
                     ("Mão", "Dậu"), ("Thìn", "Tuất"), ("Tỵ", "Hợi")]:
            self.assertEqual(luc_xung(a), b)
            self.assertEqual(luc_xung(b), a)

    def test_doi_xung(self):
        """Quan hệ giữa hai chi phải như nhau khi nhìn từ hai phía."""
        for a in DIA_CHI:
            for b in DIA_CHI:
                self.assertEqual(sorted(quan_he_chi(a, b)),
                                 sorted(quan_he_chi(b, a)), f"{a} <-> {b}")

    def test_cac_cap_da_biet(self):
        self.assertIn("Tam hợp", quan_he_chi("Thân", "Tý"))
        self.assertIn("Lục hợp", quan_he_chi("Mão", "Tuất"))
        self.assertIn("Lục xung", quan_he_chi("Mão", "Dậu"))
        self.assertIn("Lục hại", quan_he_chi("Tý", "Mùi"))
        self.assertIn("Tương hình", quan_he_chi("Dần", "Tỵ"))
        # Dần và Hợi vừa lục hợp vừa lục phá — phải nêu cả hai.
        self.assertEqual(set(quan_he_chi("Dần", "Hợi")), {"Lục hợp", "Lục phá"})
        self.assertEqual(quan_he_chi("Ngọ", "Ngọ"), ["Trùng chi", "Tự hình"])
        self.assertEqual(quan_he_chi("Tý", "Tý"), ["Trùng chi"])

    def test_chi_khong_hop_le(self):
        with self.assertRaises(ValueError):
            quan_he_chi("Tí", "Ngọ")


class TestChonNgay(unittest.TestCase):
    def test_ngay_xung_tuoi_bi_chan(self):
        """20/09/2026 chấm 95 điểm chung nhưng là ngày Dậu, xung tuổi Mão."""
        r = chon_ngay.xem_ngay_theo_tuoi(20, 9, 2026, 1987, "nam")
        self.assertEqual(r["diem_chung"], 95)
        self.assertTrue(r["bi_chan"])
        self.assertEqual(r["diem_ca_nhan"], 0)
        self.assertIn("xung tuổi", r["nhom_chan"])

    def test_thien_khac_dia_xung(self):
        """26/10/2026 là ngày Quý Dậu: Quý khắc Đinh, Dậu xung Mão."""
        r = chon_ngay.xem_ngay_theo_tuoi(26, 10, 2026, 1987, "nam")
        self.assertTrue(r["bi_chan"])
        self.assertTrue(any("Thiên khắc địa xung" in x for x in r["ly_do_chan"]))

    def test_ket_qua_khong_chua_ngay_bi_chan(self):
        r = chon_ngay.chon_ngay(1987, date(2026, 10, 10), date(2026, 11, 7),
                                "dong_tho", "nam", 20)
        self.assertTrue(r["ngay_tot"])
        for x in r["ngay_tot"]:
            self.assertFalse(x["bi_chan"], x["duong_lich"])
            self.assertNotIn("Lục xung", x["quan_he_voi_tuoi"])
            # Không ngày nào trong kết quả được phạm ngày kiêng của việc đó.
            self.assertFalse(set(x["ngay_kieng"]) & set(r["ngay_kieng_cua_viec"]),
                             x["duong_lich"])
        # so_luong=20 lớn hơn số ngày dùng được nên danh sách trả về là đầy đủ:
        # số ngày dùng được cộng số ngày bị loại phải bằng tổng số ngày quét.
        self.assertLess(len(r["ngay_tot"]), 20)
        self.assertEqual(len(r["ngay_tot"]) + r["so_ngay_bi_chan"],
                         r["tong_so_ngay"])

    def test_xep_hang_giam_dan(self):
        r = chon_ngay.chon_ngay(1987, date(2026, 10, 10), date(2026, 11, 7),
                                "cuoi_hoi", "nam", 20)
        diem = [x["diem_ca_nhan"] for x in r["ngay_tot"]]
        self.assertEqual(diem, sorted(diem, reverse=True))

    def test_chua_benh_khong_chan_ngay_kieng(self):
        """Sức khỏe không chờ ngày tốt: việc này chỉ chặn ngày xung tuổi."""
        r = chon_ngay.chon_ngay(1987, date(2026, 10, 10), date(2026, 11, 7),
                                "chua_benh", "nam", 40)
        self.assertEqual(r["so_chan_ngay_kieng"], 0)
        self.assertEqual(r["ngay_kieng_cua_viec"], [])

    def test_gio_tot_loai_gio_xung_tuoi(self):
        r = chon_ngay.xem_ngay_theo_tuoi(28, 10, 2026, 1987, "nam")
        self.assertEqual(r["gio_xung_tuoi"], "Dậu")
        self.assertNotIn("Dậu", [g["chi"] for g in r["gio_tot"]])
        for g in r["gio_tot"]:
            self.assertTrue(g["hoang_dao"])

    def test_cum_tu_viec_deu_co_that(self):
        """Mọi cụm từ của việc phải khớp chính xác dữ liệu Trực hoặc 28 tú."""
        kho = set()
        for r in load("lich/truc"):
            kho |= set(r["nen"]) | set(r["ky"])
        for r in load("lich/nhi_thap_bat_tu"):
            kho |= set(r["nen"]) | set(r["ky"])
        for v in load("lich/viec")["viec"]:
            for c in v["cum_tu"]:
                self.assertIn(c, kho, f"{v['ma']}: {c}")

    def test_viec_khong_ton_tai(self):
        with self.assertRaises(ValueError):
            chon_ngay.xem_ngay_theo_tuoi(1, 1, 2026, 1987, "nam", "khong_co")

    def test_khoang_ngay_nguoc(self):
        with self.assertRaises(ValueError):
            chon_ngay.chon_ngay(1987, date(2026, 5, 1), date(2026, 4, 1))


class TestKichBanVideo(unittest.TestCase):
    """Kịch bản video phải bám đúng số liệu engine, không được tự chế."""

    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from video import lam_video
        self.lv = lam_video

    def test_canh_day_du(self):
        kb = self.lv.kich_ban_han(1987, 2026, "nam", 9)
        self.assertTrue(kb["canh"])
        self.assertTrue(kb["caption"].strip())
        for c in kb["canh"]:
            self.assertTrue(c["loi_thoai"].strip())
            self.assertGreater(c["giay"], 0)
            self.assertLessEqual(c["giay"], self.lv.GIAY_TOI_DA)

    def test_thoi_luong_hop_ly(self):
        tong = sum(c["giay"] for c in self.lv.kich_ban_han(1987, 2026, "nam", 9)["canh"])
        self.assertTrue(20 <= tong <= 90, f"{tong} giây")

    def test_so_ngay_dung_duoc_dung_thuc_te(self):
        """Chân cảnh từng ghi nhầm số ngày HIỂN THỊ thành số ngày DÙNG ĐƯỢC."""
        from datetime import date as _d
        from tuvi.amlich import lunar_to_solar
        kb = self.lv.kich_ban_han(1987, 2026, "nam", 9)
        chan = next(c["chan"] for c in kb["canh"] if c.get("nhan") == "Ngày nên chọn")
        d1, d2 = lunar_to_solar(1, 9, 2026), lunar_to_solar(30, 9, 2026)
        kq = chon_ngay.chon_ngay(1987, _d(d1.year, d1.month, d1.day),
                                 _d(d2.year, d2.month, d2.day), "cau_tai", "nam", 3)
        that = kq["tong_so_ngay"] - kq["so_ngay_bi_chan"]
        self.assertEqual(chan, f"{that}/{kq['tong_so_ngay']} ngày dùng được")
        self.assertNotEqual(that, len(kq["ngay_tot"]),
                            "Ca kiểm thử này chỉ có nghĩa khi hai số khác nhau")

    def test_ngay_trong_canh_khong_phai_ngay_bi_chan(self):
        kb = self.lv.kich_ban_han(1987, 2026, "nam", 9)
        tot = next(c for c in kb["canh"] if c.get("nhan") == "Ngày nên chọn")
        tranh = next(c for c in kb["canh"] if c.get("nhan") == "Ngày phải tránh")
        ngay_tot = {d["chinh"] for d in tot["dong"]}
        ngay_tranh = {d["chinh"] for d in tranh["dong"]}
        self.assertFalse(ngay_tot & ngay_tranh)

    def test_kich_ban_ngay(self):
        kb = self.lv.kich_ban_ngay(20, 9, 2026)
        self.assertIn("20/09/2026", kb["canh"][0]["tieu_de"])
        self.assertTrue(all(c["giay"] > 0 for c in kb["canh"]))

    def test_luon_co_canh_mien_tru(self):
        for kb in (self.lv.kich_ban_han(1987, 2026, "nam", 9),
                   self.lv.kich_ban_ngay(20, 9, 2026)):
            cuoi = kb["canh"][-1]
            self.assertIn("tham khảo", (cuoi.get("phu", "") + cuoi["loi_thoai"]).lower())


class TestDuLieu(unittest.TestCase):
    def test_moi_tep_json_doc_duoc(self):
        for ten in all_datasets():
            self.assertIsNotNone(load(ten), ten)

    def test_so_luong_ban_ghi(self):
        self.assertEqual(len(load("tu_vi/sao")), 109)
        self.assertEqual(len(load("lich/nhi_thap_bat_tu")), 28)
        self.assertEqual(len(load("lich/truc")), 12)
        self.assertEqual(len(load("con_giap")), 12)
        self.assertEqual(len(load("nap_am")), 30)
        self.assertEqual(len(load("luc_thap_hoa_giap")), 60)
        self.assertEqual(len(load("phong_thuy/bat_trach")["cung"]), 8)
        self.assertEqual(len(load("han/sao_han")["sao"]), 9)
        self.assertEqual(len(load("lich/viec")["viec"]), 11)

    def test_sao_deu_co_y_nghia(self):
        for s in load("tu_vi/sao"):
            self.assertTrue(s["y_nghia"].strip(), s["ten"])


if __name__ == "__main__":
    unittest.main()
