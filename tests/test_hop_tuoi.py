# -*- coding: utf-8 -*-
"""Kiểm phép xem tuổi hai người có hợp nhau không.

Mỗi mốc đối chiếu dưới đây tự tính lại được bằng tay từ bảng tra, nên bài kiểm
này bắt được cả lỗi tính lẫn lỗi chép bảng.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tuvi.hop_tuoi import xem_hop_tuoi  # noqa: E402
from tuvi.kiem_tra import LoiDauVao  # noqa: E402


def _muc(kq: dict, ten: str) -> dict:
    return next(m for m in kq["muc_xet"] if m["muc"] == ten)


class TestHopTuoi(unittest.TestCase):
    def test_ban_menh_tuong_sinh(self):
        # Đinh Mão 1987 = Lư Trung Hỏa; Canh Ngọ 1990 = Lộ Bàng Thổ. Hỏa sinh Thổ.
        m = _muc(xem_hop_tuoi(1987, "nam", 1990, "nu"), "Bản mệnh")
        self.assertEqual(m["ket_qua"], "Tương sinh")
        self.assertEqual(m["tinh_chat"], "tốt")

    def test_ban_menh_tuong_khac(self):
        # Canh Ngọ 1990 = Lộ Bàng Thổ; Bính Tý 1996 = Giản Hạ Thủy. Thổ khắc Thủy.
        m = _muc(xem_hop_tuoi(1990, "nam", 1996, "nu"), "Bản mệnh")
        self.assertEqual(m["ket_qua"], "Tương khắc")

    def test_ban_menh_binh_hoa_khi_cung_hanh(self):
        m = _muc(xem_hop_tuoi(1987, "nam", 1987, "nu"), "Bản mệnh")
        self.assertEqual(m["ket_qua"], "Bình hòa")

    def test_dia_chi_tam_hop(self):
        # Thân — Tý — Thìn là một nhóm tam hợp: 1992 Nhâm Thân và 1996 Bính Tý.
        m = _muc(xem_hop_tuoi(1992, "nam", 1996, "nu"), "Địa chi")
        self.assertIn("Tam hợp", m["quan_he"])
        self.assertEqual(m["tinh_chat"], "tốt")
        self.assertGreater(m["diem"], 0)

    def test_dia_chi_luc_xung(self):
        # Ngọ xung Tý: 1990 Canh Ngọ và 1996 Bính Tý.
        m = _muc(xem_hop_tuoi(1990, "nam", 1996, "nu"), "Địa chi")
        self.assertIn("Lục xung", m["quan_he"])
        self.assertLess(m["diem"], 0)

    def test_cung_toi_khong_xung_khong_hop(self):
        m = _muc(xem_hop_tuoi(1987, "nam", 1987, "nu"), "Địa chi")
        self.assertEqual(m["tinh_chat"], "trung bình")
        self.assertEqual(m["diem"], 0)
        self.assertIn("cùng lúc gặp hạn", m["giai_thich"])

    def test_cung_phi_lay_dung_bang_bat_trach(self):
        kq = xem_hop_tuoi(1987, "nam", 1990, "nu")
        m = _muc(kq, "Cung phi")
        # Đinh Mão 1987 nam -> cung Tốn (Đông tứ mệnh);
        # Canh Ngọ 1990 nữ -> cung Cấn (Tây tứ mệnh), hướng Đông Bắc.
        self.assertEqual(m["cung_a"], "Tốn")
        self.assertEqual(m["cung_b"], "Cấn")
        # Tốn soi về Đông Bắc là Tuyệt Mệnh — hai người khác nhóm bát trạch.
        self.assertEqual(m["ket_qua"], "Tuyệt Mệnh")
        self.assertEqual(m["tinh_chat"], "xấu")
        self.assertFalse(m["cung_nhom"])

    def test_du_nien_doi_xung_hai_chieu(self):
        """Đổi chỗ hai người thì du niên phải như nhau — bảng bát trạch đối xứng."""
        for a, b in [(1987, 1990), (1984, 1990), (1992, 1996), (1975, 1980)]:
            xuoi = _muc(xem_hop_tuoi(a, "nam", b, "nu"), "Cung phi")["ket_qua"]
            nguoc = _muc(xem_hop_tuoi(b, "nu", a, "nam"), "Cung phi")["ket_qua"]
            self.assertEqual(xuoi, nguoc, f"{a} và {b}")

    def test_diem_bang_tong_cac_khoan(self):
        """Điểm tổng phải đúng bằng tổng các khoản đã liệt kê — không có khoản ẩn."""
        for a, b in [(1987, 1990), (1990, 1996), (1984, 1990), (1987, 1987)]:
            kq = xem_hop_tuoi(a, "nam", b, "nu")
            tong = sum(m["diem"] for m in kq["muc_xet"]) + sum(c["diem"] for c in kq["canh_bao"])
            self.assertEqual(kq["diem"], tong, f"{a} và {b}")

    def test_thien_khac_dia_xung_duoc_canh_bao(self):
        # Giáp Tý 1984 và Canh Ngọ 1990: can Giáp (Mộc) bị Canh (Kim) khắc,
        # chi Tý xung chi Ngọ — đủ cả hai vế.
        kq = xem_hop_tuoi(1984, "nam", 1990, "nu")
        ten = [c["ten"] for c in kq["canh_bao"]]
        self.assertIn("Thiên khắc địa xung", ten)

    def test_khong_canh_bao_khi_chi_co_mot_ve(self):
        kq = xem_hop_tuoi(1987, "nam", 1990, "nu")   # can khắc nhưng chi không xung
        self.assertEqual(kq["canh_bao"], [])

    def test_danh_gia_theo_thang_diem(self):
        kq = xem_hop_tuoi(1990, "nam", 1996, "nu")   # khắc cả bốn mặt
        self.assertEqual(kq["danh_gia"], "khắc")
        self.assertLess(kq["diem"], -4)

    def test_du_thong_tin_hai_nguoi(self):
        kq = xem_hop_tuoi(1987, "nam", 1990, "nu")
        for nguoi in (kq["nguoi_a"], kq["nguoi_b"]):
            for khoa in ("can_chi", "nap_am", "hanh", "cung_phi",
                         "nhom_bat_trach", "con_giap", "gioi_tinh"):
                self.assertTrue(nguoi.get(khoa), khoa)
        self.assertEqual(kq["nguoi_a"]["con_giap"], "Mèo")
        self.assertEqual(kq["chenh_lech_tuoi"], 3)

    def test_bon_muc_xet_luon_du(self):
        kq = xem_hop_tuoi(1987, "nam", 1990, "nu")
        self.assertEqual([m["muc"] for m in kq["muc_xet"]],
                         ["Bản mệnh", "Thiên can", "Địa chi", "Cung phi"])
        for m in kq["muc_xet"]:
            self.assertTrue(m["giai_thich"].strip())

    def test_luon_kem_luu_y_khong_phai_thuoc_do(self):
        kq = xem_hop_tuoi(1987, "nam", 1990, "nu")
        self.assertTrue(any("không phải thước đo" in x for x in kq["luu_y"]))

    def test_kiem_tra_dau_vao(self):
        for a, ga, b, gb in [(1700, "nam", 1990, "nu"), (1987, "abc", 1990, "nu"),
                             (1987, "nam", 2500, "nu"), (None, "nam", 1990, "nu")]:
            with self.assertRaises(LoiDauVao):
                xem_hop_tuoi(a, ga, b, gb)

    def test_chay_het_moi_cap_trong_60_hoa_giap(self):
        """Quét 60x60 cặp năm: không cặp nào làm sập, điểm luôn là số nguyên."""
        for a in range(1924, 1984, 7):
            for b in range(1924, 1984, 5):
                kq = xem_hop_tuoi(a, "nam", b, "nu")
                self.assertIsInstance(kq["diem"], int)
                self.assertIn(kq["danh_gia"],
                              {"rất hợp", "hợp", "bình thường", "ít hợp", "khắc"})

    # ---- phần thêm 23/09/2026, đã rà lại theo nguồn (SOURCES.md mục G) ----

    def test_ngu_hop_thien_can_theo_tam_menh_thong_hoi(self):
        # Giáp Tý 1984 + Kỷ Tỵ 1989: Giáp Kỷ hợp hóa Thổ, "Trung Chính chi hợp".
        m = _muc(xem_hop_tuoi(1984, "nam", 1989, "nu"), "Thiên can")
        self.assertEqual(m["ket_qua"], "Ngũ hợp hóa Thổ")
        self.assertEqual(m["tinh_chat"], "tốt")
        self.assertIn("Trung Chính", m["giai_thich"])
        # Hai cặp mà bản 23/09 gọi sai tên ("Nhân Thọ", "Đa Lễ").
        self.assertIn("Dâm Nặc", _muc(xem_hop_tuoi(1987, "nam", 1992, "nu"),
                                      "Thiên can")["giai_thich"])      # Đinh Nhâm
        self.assertIn("Vô Tình", _muc(xem_hop_tuoi(1988, "nam", 1993, "nu"),
                                      "Thiên can")["giai_thich"])      # Mậu Quý

    def test_tu_xung_thien_can(self):
        m = _muc(xem_hop_tuoi(1984, "nam", 1990, "nu"), "Thiên can")   # Giáp — Canh
        self.assertEqual(m["ket_qua"], "Can xung")
        self.assertEqual(m["diem"], -2)
        # Mậu (Thổ) khắc Nhâm (Thủy) nhưng không nằm trong tứ xung.
        self.assertEqual(_muc(xem_hop_tuoi(1988, "nam", 1992, "nu"),
                              "Thiên can")["ket_qua"], "Can khắc")

    def test_nap_am_khong_so_chi_la_ghi_chu(self):
        # Đinh Mão 1987 Lư Trung Hỏa khắc Nhâm Thân 1992 Kiếm Phong Kim.
        m = _muc(xem_hop_tuoi(1992, "nam", 1987, "nu"), "Bản mệnh")
        self.assertIn("Kiếm Phong Kim không sợ Hỏa", m["giai_thich"])
        self.assertEqual(m["diem"], -3)          # không đổi điểm
        # Hải Trung Kim 1984 gặp Hỏa: không có ghi chú.
        m = _muc(xem_hop_tuoi(1984, "nam", 1987, "nu"), "Bản mệnh")
        self.assertNotIn("không sợ", m["giai_thich"])

    def test_cao_ly_chep_nguyen_van(self):
        # Quý Mùi 2003 nam + Ất Dậu 2005 nữ -> chồng can Quý, vợ chi Dậu.
        for kq in (xem_hop_tuoi(2003, "nam", 2005, "nu"),
                   xem_hop_tuoi(2005, "nu", 2003, "nam")):
            cl = kq["cao_ly_dau_hinh"]
            self.assertEqual((cl["can_chong"], cl["chi_vo"]), ("Quý", "Dậu"))
            self.assertIn("chung cuộc phải gặp nạn", cl["loi"])

    def test_cao_ly_du_120_cap_co_doi_chieu(self):
        from tuvi.store import load
        bo = load("hop_tuoi/cao_ly_dau_hinh")
        cap = {(c["can_chong"], c["chi_vo"]) for c in bo["cap"]}
        self.assertEqual(len(bo["cap"]), 120)
        self.assertEqual(len(cap), 120)
        self.assertTrue(all(c["loi"].strip() for c in bo["cap"]))
        khop = [c for c in bo["cap"] if c["doi_chieu"] == "khớp kabala"]
        self.assertGreaterEqual(len(khop), 119)

    def test_khong_cao_ly_khi_lam_an_hoac_cung_gioi(self):
        for kq in (xem_hop_tuoi(1984, "nam", 1985, "nu", muc_dich="lam_an"),
                   xem_hop_tuoi(1984, "nam", 1985, "nam")):
            self.assertIsNone(kq["cao_ly_dau_hinh"])
            self.assertIsNone(kq["sinh_con_goi_y"])

    def test_muc_dich_sai(self):
        with self.assertRaises(LoiDauVao):
            xem_hop_tuoi(1984, "nam", 1985, "nu", muc_dich="xyz")

    def test_hanh_trung_gian(self):
        from tuvi.hop_tuoi import hanh_trung_gian
        # Hỏa khắc Kim -> Thổ (Hỏa sinh Thổ, Thổ sinh Kim), chiều nào cũng vậy.
        self.assertEqual(hanh_trung_gian("Kim", "Hỏa")["hanh"], "Thổ")
        self.assertEqual(hanh_trung_gian("Hỏa", "Kim")["hanh"], "Thổ")
        self.assertEqual(hanh_trung_gian("Kim", "Mộc")["hanh"], "Thủy")
        self.assertIsNone(hanh_trung_gian("Kim", "Thủy"))       # tương sinh
        self.assertIsNone(hanh_trung_gian("Kim", "Kim"))

    def test_nam_sinh_con(self):
        from tuvi.hop_tuoi import _menh, goi_y_nam_sinh_con
        bo, me = _menh(1984), _menh(1987)            # Kim — Hỏa khắc nhau
        ds = goi_y_nam_sinh_con(bo, me, nam_dau=2026)
        self.assertEqual(sorted(c["nam"] for c in ds), list(range(2026, 2032)))
        # 2028 Mậu Thân, 2029 Kỷ Dậu là Đại Trạch Thổ — hành trung gian, xếp đầu.
        self.assertEqual([c["nam"] for c in ds[:2]], [2028, 2029])
        self.assertTrue(all(c["la_hanh_trung_gian"] == (c["hanh"] == "Thổ") for c in ds))
        # Chiều khắc phải đúng: 2030 Thoa Xuyến Kim — Hỏa của mẹ khắc Kim của con.
        nam_2030 = next(c for c in ds if c["nam"] == 2030)
        self.assertIn("mệnh mẹ (Hỏa) khắc mệnh con (Kim)", nam_2030["ly_do"])
        # Năm bắt đầu mặc định là năm hiện tại, không viết cứng.
        from datetime import date
        self.assertEqual(min(c["nam"] for c in goi_y_nam_sinh_con(bo, me)),
                         date.today().year)


if __name__ == "__main__":
    unittest.main()
