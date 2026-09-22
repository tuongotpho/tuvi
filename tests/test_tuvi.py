# -*- coding: utf-8 -*-
"""Kiểm thử các phép tính lõi.

    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tuvi import chon_ngay, han, la_so, luan_giai, ngay_gio, phong_thuy  # noqa: E402
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


class TestAmLichDoiChieuGoc(unittest.TestCase):
    """Khóa lỗi int() thay cho floor(): trước năm 2000 kinh độ mặt trời âm,
    int() làm sai tháng nhuận, lệch nguyên một tháng ở 29% số ngày 1800–1999."""

    MAU = Path(__file__).parent / "fixtures" / "amlich_hongocduc_mau.txt"

    def test_khop_ban_javascript_goc(self):
        so = 0
        for dong in self.MAU.read_text(encoding="utf-8").splitlines():
            if not dong or dong.startswith("#"):
                continue
            trai, phai = dong.split("|")
            d, m, y = (int(x) for x in trai.split("/"))
            ld, lm, ly, leap = (int(x) for x in phai.split("/"))
            r = solar_to_lunar(d, m, y)
            self.assertEqual((r.day, r.month, r.year, r.leap), (ld, lm, ly, bool(leap)), trai)
            so += 1
        self.assertGreater(so, 4000)

    def test_tet_1980_2026(self):
        tet = {1982: (25, 1), 1985: (21, 1), 1987: (29, 1), 1990: (27, 1), 1993: (23, 1),
               1998: (28, 1), 2000: (5, 2), 2024: (10, 2), 2025: (29, 1), 2026: (17, 2)}
        for nam, (d, m) in tet.items():
            s = lunar_to_solar(1, 1, nam)
            self.assertEqual((s.day, s.month), (d, m), nam)

    def test_ngay_22_8_1987_la_28_7_am(self):
        # Trước khi sửa cho ra 28/6 — người dùng đối chiếu nhiều lịch đều thấy 28/7.
        r = solar_to_lunar(22, 8, 1987)
        self.assertEqual((r.day, r.month, r.year, r.leap), (28, 7, 1987, False))

    def test_thang_nhuan_theo_mui_gio_viet_nam(self):
        # 1985 nhuận tháng 2 (lịch Việt Nam khác lịch Trung Quốc năm này), 1987 nhuận tháng 7.
        self.assertTrue(solar_to_lunar(21, 3, 1985).leap)
        self.assertEqual(solar_to_lunar(21, 3, 1985).month, 2)
        r = solar_to_lunar(24, 8, 1987)
        self.assertEqual((r.day, r.month, r.leap), (1, 7, True))
        # Đổi ngược: tháng nhuận phải quay về đúng ngày dương.
        self.assertEqual(tuple(lunar_to_solar(1, 7, 1987, True)), (24, 8, 1987))


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


class TestAnSaoDoiChieuLasotuvi(unittest.TestCase):
    """99 sao × 60 lá số phải trùng vị trí với doanguyen/lasotuvi (MIT).

    Bộ mẫu sinh sẵn ở tests/fixtures/lasotuvi_mau.json; 8 sao khác trường phái
    và cặp Thai — Dưỡng (lasotuvi đảo) được ghi trong tệp đó và SOURCES.md.
    """

    MAU = Path(__file__).parent / "fixtures" / "lasotuvi_mau.json"

    def test_khop_vi_tri_sao(self):
        bo = json.loads(self.MAU.read_text(encoding="utf-8"))
        so_sao = 0
        for m in bo["la_so"]:
            d, t, n = m["am_lich"]
            ls = la_so.lap_la_so(d, t, n, DIA_CHI.index(m["gio"]) * 2, 0,
                                 gioi_tinh=m["gioi_tinh"], duong_lich=False)
            vi_tri = {s["ten"].lower(): c["chi"] for c in ls["cac_cung"] for s in c["sao"]}
            self.assertEqual(len(vi_tri), 109, m)
            for ten, chi in m["sao"].items():
                self.assertEqual(vi_tri.get(ten), chi, f"{ten} — {m['am_lich']} {m['gio']}")
                so_sao += 1
            self.assertEqual(set(ls["tuan"]), set(m["tuan"]), m)
            self.assertEqual(set(ls["triet"]), set(m["triet"]), m)
        self.assertEqual(so_sao, 60 * bo["so_sao_moi_la_so"])

    def test_du_109_sao_khong_trung(self):
        for d, m, y, g, gt in [(20, 9, 1990, 14, "nam"), (1, 1, 1985, 6, "nu"),
                               (22, 8, 1987, 10, "nam"), (5, 7, 1992, 2, "nu")]:
            ls = la_so.lap_la_so(d, m, y, g, gioi_tinh=gt)
            ten = [s["ten"].lower() for c in ls["cac_cung"] for s in c["sao"]]
            self.assertEqual(len(ten), 109)
            self.assertEqual(len(set(ten)), 109)
            self.assertEqual(set(ten), {s["ten"].lower() for s in load("tu_vi/sao")})

    def test_vong_trang_sinh_dung_thu_tu(self):
        # Tuyệt — Thai — Dưỡng — Tràng Sinh phải nối tiếp nhau một cung một.
        ls = la_so.lap_la_so(20, 9, 1990, 14, gioi_tinh="nam")
        vi_tri = {s["ten"]: DIA_CHI.index(c["chi"]) for c in ls["cac_cung"] for s in c["sao"]}
        buoc = 1 if ls["chieu_di_han"] == "thuận" else -1
        self.assertEqual((vi_tri["Thai"] - vi_tri["Tuyệt"]) % 12, buoc % 12)
        self.assertEqual((vi_tri["Dưỡng"] - vi_tri["Thai"]) % 12, buoc % 12)
        self.assertEqual((vi_tri["Tràng Sinh"] - vi_tri["Dưỡng"]) % 12, buoc % 12)


class TestAnSaoDoiChieuIztro(unittest.TestCase):
    """Nguồn đối chiếu ĐỘC LẬP thứ hai: 94 sao × 60 lá số theo SylarLong/iztro (MIT).

    iztro viết bằng JS theo phái Trung Châu, không chung dòng mã với lasotuvi; hai
    nguồn cùng khớp thì vị trí sao khó sai ngẫu nhiên. Bộ mẫu sinh bằng
    scripts/sinh_fixture_iztro.js; 5 sao iztro an theo phái khác được bỏ và ghi ở
    SOURCES.md mục E. Fixture ghi cả ngày dương iztro đổi ra, dùng kiểm luôn amlich.
    """

    MAU = Path(__file__).parent / "fixtures" / "iztro_mau.json"

    def setUp(self):
        self.bo = json.loads(self.MAU.read_text(encoding="utf-8"))

    def _la_so(self, m):
        d, t, n = m["am_lich"]
        return la_so.lap_la_so(d, t, n, DIA_CHI.index(m["gio"]) * 2, 0,
                               gioi_tinh=m["gioi_tinh"], duong_lich=False)

    def test_khop_vi_tri_sao(self):
        so_sao = 0
        for m in self.bo["la_so"]:
            ls = self._la_so(m)
            vi_tri = {s["ten"].lower(): c["chi"] for c in ls["cac_cung"] for s in c["sao"]}
            for ten, chi in m["sao"].items():
                self.assertEqual(vi_tri.get(ten), chi, f"{ten} — {m['am_lich']} {m['gio']}")
                so_sao += 1
        self.assertEqual(so_sao, 60 * self.bo["so_sao_moi_la_so"])

    def test_khop_menh_than_cuc_tuan_triet(self):
        for m in self.bo["la_so"]:
            ls = self._la_so(m)
            than = next(c["chi"] for c in ls["cac_cung"] if c["la_cung_than"])
            self.assertEqual(ls["cung_menh"], m["cung_menh"], m["am_lich"])
            self.assertEqual(than, m["cung_than"], m["am_lich"])
            self.assertEqual(ls["cuc"].split()[0], m["cuc"], m["am_lich"])
            self.assertIn(m["tuan"], ls["tuan"], m["am_lich"])
            self.assertIn(m["triet"], ls["triet"], m["am_lich"])

    # iztro đổi âm -> dương theo lịch Trung Quốc (UTC+8). Điểm sóc tháng 6 âm 1996 rơi
    # 23h15 ngày 15/7 giờ Việt Nam nhưng đã 0h15 ngày 16/7 giờ Bắc Kinh, nên tháng đó
    # hai lịch lệch nhau một ngày: kho (đã khớp 100% với Hồ Ngọc Đức) phải ra 12/8/1996,
    # iztro ra 13/8/1996. Đây là ca duy nhất trong 60 mẫu; ghi rõ để không ai "sửa" theo iztro.
    LECH_LICH_VIET_TRUNG = {(29, 6, 1996): "1996-8-12"}

    def test_khop_ngay_duong_lich(self):
        for m in self.bo["la_so"]:
            d, t, n = m["am_lich"]
            sd = lunar_to_solar(d, t, n)
            mong_doi = self.LECH_LICH_VIET_TRUNG.get((d, t, n), m["duong_lich"])
            self.assertEqual(f"{sd.year}-{sd.month}-{sd.day}", mong_doi, m["am_lich"])
        self.assertEqual(len(self.LECH_LICH_VIET_TRUNG), 1)


class TestGioSinh(unittest.TestCase):
    def test_canh_gio_va_gio_dong_ho_cho_cung_la_so(self):
        # 14:00 = giờ Mùi; nhập theo canh (đầu canh 14h) phải cho lá số y hệt.
        a = la_so.lap_la_so(20, 9, 1990, 14, 0, gioi_tinh="nam")
        b = la_so.lap_la_so(20, 9, 1990, DIA_CHI.index("Mùi") * 2, 0, gioi_tinh="nam")
        self.assertEqual(a, b)

    def test_ranh_gioi_canh_gio(self):
        from tuvi.canchi import chi_gio_tu_gio_phut
        self.assertEqual(DIA_CHI[chi_gio_tu_gio_phut(23, 0)], "Tý")
        self.assertEqual(DIA_CHI[chi_gio_tu_gio_phut(0, 59)], "Tý")
        self.assertEqual(DIA_CHI[chi_gio_tu_gio_phut(1, 0)], "Sửu")
        self.assertEqual(DIA_CHI[chi_gio_tu_gio_phut(17, 0)], "Dậu")
        self.assertEqual(DIA_CHI[chi_gio_tu_gio_phut(22, 59)], "Hợi")

    def test_gio_ty_giu_nguyen_ngay_sinh(self):
        # 23:30 ngày 20/09/1990 vẫn là ngày 2/8 âm, giờ Tý — không sang ngày 3/8.
        ls = la_so.lap_la_so(20, 9, 1990, 23, 30, gioi_tinh="nam")
        self.assertEqual((ls["am_lich"]["ngay"], ls["am_lich"]["gio"]), (2, "Tý"))
        self.assertEqual(ls, la_so.lap_la_so(20, 9, 1990, 0, 0, gioi_tinh="nam"))


class TestCachCuc(unittest.TestCase):
    def _cach(self, d, m, y, g, gt):
        return {c["ten"] for c in luan_giai.goi_y_cach_cuc(la_so.lap_la_so(d, m, y, g, gioi_tinh=gt))}

    def test_moi_cach_deu_co_the_khop(self):
        """Không cách nào 'chết': quét lưới lá số, mỗi cách phải khớp ít nhất một lần."""
        import random
        rnd = random.Random(3)
        gap = set()
        for _ in range(1500):
            ls = la_so.lap_la_so(rnd.randint(1, 28), rnd.randint(1, 12), rnd.randint(1940, 2020),
                                 rnd.randint(0, 23), gioi_tinh=rnd.choice(["nam", "nu"]))
            gap |= {c["ten"] for c in luan_giai.goi_y_cach_cuc(ls)}
        # Bốn cách hiếm (dưới 1/1000 lá số) khóa bằng lá số cụ thể ở dưới.
        hiem = {"Quân thần khánh hội", "Lục cát hội Mệnh",
                "Tử Vi cư Ngọ (Cực hướng ly minh)", "Lộc hợp uyên ương"}
        chua = {c["ten"] for c in load("tu_vi/cach_cuc")} - gap - hiem
        self.assertFalse(chua, f"Cách không bao giờ khớp: {chua}")

    def test_cach_hiem_bang_la_so_cu_the(self):
        self.assertIn("Quân thần khánh hội", self._cach(28, 4, 1985, 8, "nam"))
        self.assertIn("Lục cát hội Mệnh", self._cach(12, 4, 1951, 4, "nam"))
        self.assertIn("Tử Vi cư Ngọ (Cực hướng ly minh)", self._cach(3, 4, 1950, 18, "nam"))
        self.assertIn("Lộc hợp uyên ương", self._cach(28, 1, 1951, 10, "nam"))

    def test_la_so_mau(self):
        # 20/09/1990 14h nam: Mệnh Dần vô chính diệu, Cơ Nguyệt Đồng Lương hội.
        cc = self._cach(20, 9, 1990, 14, "nam")
        self.assertIn("Mệnh vô chính diệu", cc)
        self.assertIn("Cơ Nguyệt Đồng Lương", cc)
        self.assertNotIn("Sát Phá Tham", cc)
        # 22/08/1987 12h nam: Thất Sát thủ Mệnh tại Dần, Mệnh Thân đồng cung, Mệnh bị Triệt.
        cc = self._cach(22, 8, 1987, 12, "nam")
        self.assertIn("Thất Sát triều đẩu", cc)
        self.assertIn("Sát Phá Tham", cc)
        self.assertIn("Mệnh Thân đồng cung", cc)
        self.assertIn("Tuần Triệt án Mệnh", cc)

    def test_bo_doc_quy_tac(self):
        """Kiểm từng khóa của bộ đọc trên một lá số đã biết vị trí sao."""
        ls = la_so.lap_la_so(22, 8, 1987, 12, gioi_tinh="nam")
        bc = luan_giai._BoiCanh(ls)
        khop = lambda **qt: luan_giai._khop(qt, bc)  # noqa: E731
        self.assertTrue(khop(co_du=["Thất Sát"]))
        self.assertTrue(khop(chinh_tinh_menh=["Thất Sát"]))
        self.assertFalse(khop(chinh_tinh_menh=["Thất Sát", "Tử Vi"]))
        self.assertTrue(khop(menh_chi=["Dần"]))
        self.assertFalse(khop(menh_chi=["Ngọ"]))
        self.assertTrue(khop(noi="hoi_menh", co_du=["Thất Sát", "Phá Quân", "Tham Lang"]))
        self.assertFalse(khop(noi="menh", co_du=["Phá Quân"]))
        self.assertTrue(khop(khong_co=["Tử Vi"]))
        self.assertTrue(khop(sao_tai={"Thất Sát": ["Dần"]}))
        self.assertTrue(khop(vo_chinh_dieu=False))
        self.assertFalse(khop(vo_chinh_dieu=True))
        self.assertTrue(khop(menh_than_dong_cung=True))
        self.assertTrue(khop(tuan_triet_menh=True))
        self.assertTrue(khop(hoac=[{"menh_chi": ["Ngọ"]}, {"menh_chi": ["Dần"]}]))
        self.assertFalse(khop(va=[{"menh_chi": ["Ngọ"]}, {"menh_chi": ["Dần"]}]))
        # dong_cung: Thất Sát ở Dần, Phá Quân ở Tuất -> không cùng cung.
        self.assertFalse(khop(dong_cung=["Thất Sát", "Phá Quân"]))
        self.assertTrue(khop(dong_cung=["Thất Sát"]))

    def test_giap_menh_phai_moi_ben_mot_sao(self):
        """Hai sao cùng nằm một bên thì không phải 'giáp'."""
        import copy
        ls = copy.deepcopy(la_so.lap_la_so(22, 8, 1987, 12, gioi_tinh="nam"))
        cac = ls["cac_cung"]; i = [c["chi"] for c in cac].index("Dần")
        trai, phai = cac[(i - 1) % 12], cac[(i + 1) % 12]
        for c in cac:
            c["sao"] = [s for s in c["sao"] if s["ten"] not in ("Thiên Khôi", "Thiên Việt")]
        trai["sao"] += [{"ten": "Thiên Khôi", "nhom": "Quý nhân"}, {"ten": "Thiên Việt", "nhom": "Quý nhân"}]
        self.assertFalse(luan_giai._khop({"noi": "giap_menh", "co_du": ["Thiên Khôi", "Thiên Việt"]},
                                         luan_giai._BoiCanh(ls)))
        trai["sao"] = [s for s in trai["sao"] if s["ten"] != "Thiên Việt"]
        phai["sao"].append({"ten": "Thiên Việt", "nhom": "Quý nhân"})
        self.assertTrue(luan_giai._khop({"noi": "giap_menh", "co_du": ["Thiên Khôi", "Thiên Việt"]},
                                        luan_giai._BoiCanh(ls)))


class TestKiemTraDauVao(unittest.TestCase):
    """Tầng thư viện phải tự chặn đầu vào rác, không trông vào máy chủ web."""

    def test_la_so_chan_ngay_khong_co_that(self):
        from tuvi.kiem_tra import LoiDauVao
        for args in [(31, 2, 1990, 14), (29, 2, 2023, 14), (0, 0, 0, 0), (1, 1, 1700, 14),
                     (1, 1, 2200, 14), (20, 9, 1990, 99), (20, 9, 1990, -5), (20, 9, 1990, 14, 60)]:
            with self.assertRaises(LoiDauVao, msg=args):
                la_so.lap_la_so(*args)
        with self.assertRaises(LoiDauVao):
            la_so.lap_la_so(20, 9, 1990, 14, gioi_tinh="<script>")
        with self.assertRaises(LoiDauVao):
            la_so.lap_la_so(31, 12, 1990, 14, duong_lich=False)   # ngày âm tối đa 30

    def test_gioi_tinh_chuan_hoa(self):
        from tuvi.kiem_tra import gioi_tinh_hop_le
        self.assertEqual(gioi_tinh_hop_le("Nữ"), "nu")
        self.assertEqual(gioi_tinh_hop_le(" NAM "), "nam")
        self.assertEqual(la_so.lap_la_so(20, 9, 1990, 14, gioi_tinh="Nữ")["gioi_tinh"], "Nữ")

    def test_han_va_phong_thuy_chan_rac(self):
        from tuvi.kiem_tra import LoiDauVao
        with self.assertRaises(LoiDauVao):
            han.ho_so_han(2030, 2026, "nam")
        with self.assertRaises(LoiDauVao):
            han.sao_han(1990, 2026, "khac")
        with self.assertRaises(LoiDauVao):
            phong_thuy.ho_so_phong_thuy(1990, "nam", "Bắc Cực")
        with self.assertRaises(LoiDauVao):
            ngay_gio.xem_ngay(31, 4, 2026)
        with self.assertRaises(LoiDauVao):
            chon_ngay.chon_ngay(1987, date(2026, 1, 1), date(2026, 2, 1), so_luong=10_000)
        with self.assertRaises(LoiDauVao):
            chon_ngay.chon_ngay(1987, date(2026, 1, 1), date(2026, 2, 1), viec="khong_co")


class TestLuuNien(unittest.TestCase):
    def test_tieu_han_theo_bang_khoi(self):
        from tuvi.luu_nien import cung_tieu_han
        # Đinh Mão 1987 (Hợi Mão Mùi -> khởi Sửu), nam thuận: năm Mão tại Sửu, năm Ngọ tại Thìn.
        self.assertEqual(DIA_CHI[cung_tieu_han(3, 3, True)], "Sửu")
        self.assertEqual(DIA_CHI[cung_tieu_han(3, 6, True)], "Thìn")
        # Nữ đếm nghịch: năm Ngọ lùi 3 cung từ Sửu -> Tuất.
        self.assertEqual(DIA_CHI[cung_tieu_han(3, 6, False)], "Tuất")
        # Thân Tý Thìn khởi Tuất; Dần Ngọ Tuất khởi Thìn; Tỵ Dậu Sửu khởi Mùi.
        self.assertEqual(DIA_CHI[cung_tieu_han(0, 0, True)], "Tuất")
        self.assertEqual(DIA_CHI[cung_tieu_han(6, 6, True)], "Thìn")
        self.assertEqual(DIA_CHI[cung_tieu_han(9, 9, True)], "Mùi")

    def test_sao_luu_theo_can_chi_nam_xem(self):
        from tuvi.luu_nien import sao_luu
        vt = sao_luu(2026)   # Bính Ngọ
        self.assertEqual(DIA_CHI[vt["Lưu Thái Tuế"]], "Ngọ")
        self.assertEqual(DIA_CHI[vt["Lưu Lộc Tồn"]], "Tỵ")        # can Bính
        self.assertEqual(DIA_CHI[vt["Lưu Kình Dương"]], "Ngọ")
        self.assertEqual(DIA_CHI[vt["Lưu Thiên Mã"]], "Thân")     # Dần Ngọ Tuất
        self.assertEqual(DIA_CHI[vt["Lưu Đào Hoa"]], "Mão")
        self.assertEqual(DIA_CHI[vt["Lưu Bạch Hổ"]], "Dần")       # Thái Tuế + 8

    def test_xem_nam_tren_la_so(self):
        from tuvi.luu_nien import xem_nam
        ls = la_so.lap_la_so(22, 8, 1987, 10, gioi_tinh="nam")
        r = xem_nam(ls, 2026)
        self.assertEqual((r["tuoi_mu"], r["tieu_han"]["chi"], r["dai_han"]["tuoi"]), (40, "Thìn", "34-43"))
        self.assertEqual(r["luu_tu_hoa"]["Lưu Hóa Kỵ"], "Liêm Trinh")
        self.assertEqual(r["diem"], sum(k["diem"] for k in r["khoan_diem"]))
        self.assertEqual(sum(len(c["sao_luu"]) for c in r["sao_luu_theo_cung"]), len(r["sao_luu"]))
        lg = luan_giai.luan_giai_la_so(ls, 2026)
        self.assertEqual(lg["nam_xem"]["tieu_han"]["chi"], "Thìn")
        self.assertIsNone(luan_giai.luan_giai_la_so(ls)["nam_xem"])
        from tuvi.kiem_tra import LoiDauVao
        with self.assertRaises(LoiDauVao):
            xem_nam(ls, 1980)


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


class TestLongTieng(unittest.TestCase):
    """Phần lồng tiếng: kiểm phần ghép và tính giờ, không gọi mạng."""

    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from video import giong_doc, lam_video
        self.gd, self.lv = giong_doc, lam_video
        self.goc = giong_doc.doc_kich_ban

    def tearDown(self):
        self.gd.doc_kich_ban = self.goc
        self.lv.giong_doc.doc_kich_ban = self.goc

    def _ffmpeg(self):
        ff = self.lv._ffmpeg()
        if not ff:
            self.skipTest("Không có ffmpeg trong môi trường này")
        return ff

    def _gia_lap(self, do_dai):
        """Thay edge-tts bằng các tệp mp3 thật có độ dài định trước."""
        import subprocess
        ff = self._ffmpeg()

        def gia(canh, thu_muc, giong, toc_do, cao_do):
            thu_muc.mkdir(parents=True, exist_ok=True)
            ra = []
            for i, d in enumerate(do_dai[:len(canh)], 1):
                tep = thu_muc / f"canh{i:02d}.mp3"
                subprocess.run([ff, "-y", "-loglevel", "error", "-f", "lavfi",
                                "-i", f"sine=frequency=440:duration={d}",
                                "-c:a", "libmp3lame", str(tep)],
                               check=True, capture_output=True)
                ra.append((tep, d))
            return ra
        self.lv.giong_doc.doc_kich_ban = gia

    def test_do_dai_canh_theo_am_thanh_that(self):
        """Có giọng đọc thì độ dài cảnh phải theo audio, không theo số chữ."""
        do_dai = [4.3, 7.1, 6.4, 3.2, 5.0, 6.8, 4.1, 5.6]
        self._gia_lap(do_dai)
        kb = self.lv.kich_ban_han(1987, 2026, "nam", 9)
        uoc_luong = [c["giay"] for c in kb["canh"]]
        with tempfile.TemporaryDirectory() as tmp:
            doan = self.lv.long_tieng(kb, Path(tmp), "vi-VN-HoaiMyNeural",
                                      "+0%", "+0Hz")
        self.assertIsNotNone(doan)
        moi = [c["giay"] for c in kb["canh"]]
        self.assertEqual(
            moi, [round(d + self.lv.DEM_CUOI_CANH, 2) for d in do_dai[:len(moi)]])
        self.assertNotEqual(moi, uoc_luong)

    def test_ghep_dai_dung_tung_moc(self):
        """Mỗi đoạn phải được đệm im lặng cho đủ đúng độ dài cảnh."""
        ff = self._ffmpeg()
        do_dai = [2.0, 3.5, 1.5]
        self._gia_lap(do_dai)
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            doan = self.lv.giong_doc.doc_kich_ban(
                [{"loi_thoai": "x"}] * 3, tmp / "t", "v", "+0%", "+0Hz")
            giay = [d + 1.0 for d in do_dai]
            dai = self.gd.ghep_thanh_mot_dai(doan, giay, tmp / "dai.wav", ff)
            self.assertAlmostEqual(self.gd.do_dai_am_thanh(dai, ff),
                                   sum(giay), delta=0.15)

    def test_that_bai_thi_van_xuat_video_cam(self):
        """Mạng bị chặn hay thiếu gói thì không được làm hỏng cả lệnh."""
        def hong(*a, **kw):
            raise self.gd.KhongLongTiengDuoc("giả lập bị chặn")
        self.lv.giong_doc.doc_kich_ban = hong
        kb = self.lv.kich_ban_han(1987, 2026, "nam", 9)
        truoc = [c["giay"] for c in kb["canh"]]
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(self.lv.long_tieng(kb, Path(tmp), "v", "+0%", "+0Hz"))
        self.assertEqual([c["giay"] for c in kb["canh"]], truoc)

    def test_nap_ca_proxy_khong_no(self):
        """Không khai báo CA thì hàm phải im lặng bỏ qua."""
        cu = {k: os.environ.pop(k, None)
              for k in ("TUVI_CA_BUNDLE", "SSL_CERT_FILE", "REQUESTS_CA_BUNDLE")}
        try:
            self.gd.nap_ca_proxy()
        finally:
            os.environ.update({k: v for k, v in cu.items() if v})

    def test_giong_tieng_viet(self):
        self.assertTrue(self.gd.GIONG_NU.startswith("vi-VN"))
        self.assertTrue(self.gd.GIONG_NAM.startswith("vi-VN"))
        self.assertEqual(self.gd.GIONG_MAC_DINH, self.gd.GIONG_NU)


class TestDuLieu(unittest.TestCase):
    def test_luc_cat_tinh_deu_la_cat(self):
        """Sáu sao cát phải cùng mang tính chất "cát".

        Trước đây Tả Phù và Hữu Bật bị để "trung tính" trong khi bốn sao còn lại
        để "cát". Kho tự mâu thuẫn: data/tu_vi/cach_cuc.json coi "Tả Hữu đồng
        cung" và "Tả Hữu củng Mệnh" là cách TỐT, nhưng phần luận giải lại không
        đếm hai sao đó vào cát tinh, nên cung Mệnh có đủ Tả Hữu vẫn bị chấm là
        "hung nhiều hơn cát". Chính người dùng đọc luận giải mới phát hiện.
        """
        tinh_chat = {s["ten"].lower(): s["tinh_chat"] for s in load("tu_vi/sao")}
        for ten in ("tả phù", "hữu bật", "văn xương", "văn khúc",
                    "thiên khôi", "thiên việt"):
            self.assertEqual(tinh_chat.get(ten), "cát", ten)

    # Sao hung vẫn được phép nằm trong một cách TỐT khi đủ bộ mới thành đẹp —
    # luật tử vi đúng là như vậy, và kho ghi rõ lý do ngay trong phần luận giải
    # của cách đó. Mỗi ngoại lệ phải được kể tên ở đây, để cách mới thêm sau này
    # không lặng lẽ kéo theo một sao hung mà không ai để ý.
    HUNG_TRONG_CACH_TOT = {("Tứ Linh hội Mệnh", "Bạch Hổ"),
                           ("Tứ Linh hội Mệnh", "Hoa Cái")}

    def test_cach_cuc_va_tinh_chat_sao_khong_mau_thuan(self):
        """Sao nào được cách cục TỐT gọi tên thì không được mang tính chất hung."""
        tinh_chat = {s["ten"].lower(): s["tinh_chat"] for s in load("tu_vi/sao")}
        ngoai_le = set()
        for cach in load("tu_vi/cach_cuc"):
            if cach["tinh_chat"] != "tốt":
                continue
            for ten in cach.get("quy_tac", {}).get("co_du", []):
                if tinh_chat.get(ten.lower()) != "hung":
                    continue
                cap = (cach["ten"], ten)
                self.assertIn(cap, self.HUNG_TRONG_CACH_TOT,
                              f"{ten} là sao hung nhưng nằm trong cách tốt "
                              f"{cach['ten']}; nếu đúng luật thì khai báo ngoại lệ, "
                              f"nếu sai thì sửa tính chất sao")
                self.assertIn("đủ bộ", cach["luan_giai"], cach["ten"])
                ngoai_le.add(cap)
        self.assertEqual(ngoai_le, self.HUNG_TRONG_CACH_TOT,
                         "có ngoại lệ khai báo thừa, cách cục đã đổi rồi")

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


class TestLuanGiai(unittest.TestCase):
    def _lg(self, d, m, y, g, gt, nam_xem=2026):
        return luan_giai.luan_giai_la_so(la_so.lap_la_so(d, m, y, g, gioi_tinh=gt), nam_xem)

    def test_du_12_cung_theo_thu_tu_doc(self):
        lg = self._lg(20, 9, 1990, 14, "nam")
        ten = [c["ten_cung"] for c in lg["cac_cung"]]
        self.assertEqual(sorted(ten), sorted(la_so.TEN_CUNG))
        self.assertEqual(ten[0], "Mệnh")
        # Thân cư Phúc Đức nên Phúc Đức được đọc ngay sau Mệnh.
        self.assertEqual(ten[1], "Phúc Đức")
        self.assertTrue(lg["cac_cung"][1]["la_cung_than"])

    def test_than_cu_menh_khong_lap_cung(self):
        lg = self._lg(10, 10, 1975, 0, "nam")
        self.assertEqual(lg["tong_quan"]["than"]["cung"], "Mệnh")
        self.assertEqual([c["ten_cung"] for c in lg["cac_cung"]], luan_giai.THU_TU_DOC)
        self.assertTrue(lg["tong_quan"]["than"]["nhan_xet"].startswith("Thân cư Mệnh"))

    def test_diem_bang_tong_cac_khoan(self):
        for cung in self._lg(15, 3, 1988, 10, "nam")["cac_cung"]:
            self.assertEqual(cung["diem"], sum(k["diem"] for k in cung["khoan_diem"]), cung["ten_cung"])
            self.assertIn(cung["danh_gia"], {"vượng", "khá", "trung bình", "yếu", "xấu"})

    def test_quan_he_menh_cuc(self):
        # 1990 Lộ Bàng Thổ, Thổ ngũ cục -> cùng hành.
        self.assertEqual(self._lg(20, 9, 1990, 14, "nam")["tong_quan"]["menh_cuc"]["quan_he"],
                         "Mệnh và Cục cùng hành")
        # 1975 Đại Khê Thủy, Thổ ngũ cục -> Thổ khắc Thủy: Cục khắc Mệnh.
        self.assertEqual(self._lg(10, 10, 1975, 0, "nam")["tong_quan"]["menh_cuc"]["quan_he"],
                         "Cục khắc Mệnh")
        # 1992 Kiếm Phong Kim, Thủy nhị cục -> Kim sinh Thủy: Mệnh sinh Cục.
        self.assertEqual(self._lg(5, 7, 1992, 2, "nu")["tong_quan"]["menh_cuc"]["quan_he"],
                         "Mệnh sinh Cục")

    def test_am_duong_ly_khop_chieu_dai_han(self):
        self.assertTrue(self._lg(20, 9, 1990, 14, "nam")["tong_quan"]["am_duong"]["thuan_ly"])
        self.assertFalse(self._lg(1, 1, 1985, 6, "nu")["tong_quan"]["am_duong"]["thuan_ly"])

    def test_vo_chinh_dieu_muon_sao_xung_chieu(self):
        lg = self._lg(20, 9, 1990, 14, "nam")
        menh = lg["cac_cung"][0]
        self.assertTrue(menh["vo_chinh_dieu"])
        self.assertEqual(menh["muon_chinh_tinh"], menh["xung_chieu"]["chinh_tinh"])
        self.assertIn("vô chính diệu", menh["luan"])
        self.assertTrue(any(k["ly_do"].startswith("mượn") for k in menh["khoan_diem"]))

    def test_tu_hoa_roi_dung_cung(self):
        lg = self._lg(20, 9, 1990, 14, "nam")
        ls = la_so.lap_la_so(20, 9, 1990, 14, gioi_tinh="nam")
        for h in lg["tu_hoa"]:
            cung = next(c for c in ls["cac_cung"] if c["ten_cung"] == h["cung"])
            self.assertIn(h["sao"], [s["ten"] for s in cung["sao"]])
            self.assertIn(h["hoa"], [s["ten"] for s in cung["sao"]])

    def test_dai_han_hien_tai_theo_tuoi_mu(self):
        lg = self._lg(20, 9, 1990, 14, "nam", nam_xem=2026)
        dh = lg["dai_han"]
        self.assertEqual(dh["tuoi_mu"], 37)
        self.assertEqual(dh["hien_tai"]["tuoi"], "35-44")
        self.assertEqual([h["tu"] for h in dh["bang"]], sorted(h["tu"] for h in dh["bang"]))
        self.assertEqual(sum(1 for h in dh["bang"] if h["hien_tai"]), 1)
        # Không truyền năm xem thì không đánh dấu hạn nào.
        self.assertIsNone(self._lg(20, 9, 1990, 14, "nam", nam_xem=None)["dai_han"]["hien_tai"])

    def test_cach_cuc_khop_voi_api_cu(self):
        ls = la_so.lap_la_so(20, 9, 1990, 14, gioi_tinh="nam")
        ten = {c["ten"] for c in luan_giai.goi_y_cach_cuc(ls)}
        self.assertIn("Mệnh vô chính diệu", ten)
        self.assertIn("Cơ Nguyệt Đồng Lương", ten)


if __name__ == "__main__":
    unittest.main()
