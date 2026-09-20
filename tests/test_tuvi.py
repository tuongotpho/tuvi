# -*- coding: utf-8 -*-
"""Kiểm thử các phép tính lõi.

    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tuvi import han, la_so, ngay_gio, phong_thuy  # noqa: E402
from tuvi.amlich import lunar_to_solar, solar_to_lunar  # noqa: E402
from tuvi.canchi import (can_chi_ngay, can_chi_nam, can_chi_thang,  # noqa: E402
                         chi_gio_tu_gio_phut, luc_thap_hoa_giap)
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

    def test_sao_deu_co_y_nghia(self):
        for s in load("tu_vi/sao"):
            self.assertTrue(s["y_nghia"].strip(), s["ten"])


if __name__ == "__main__":
    unittest.main()
