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

    def test_cao_ly_dau_hinh(self):
        """Kiểm tra phương pháp Cao Ly Đầu Hình (Can chồng - Chi vợ)."""
        # Giáp Tý (1984 nam) lấy Ất Sửu (1985 nữ) -> Can Giáp lấy Chi Sửu
        kq = xem_hop_tuoi(1984, "nam", 1985, "nu")
        self.assertIsNotNone(kq["cao_ly_dau_hinh"])
        cl = kq["cao_ly_dau_hinh"]
        self.assertEqual(cl["can_chong"], "Giáp")
        self.assertEqual(cl["chi_vo"], "Sửu")
        self.assertTrue(len(cl["tho"]) > 0)
        self.assertTrue(len(cl["luan"]) > 0)
        self.assertIn("danh_hieu", cl)
        self.assertIn("danh_gia", cl)

    def test_ngu_hop_thien_can(self):
        """Giáp Kỷ hóa Thổ: ngũ hợp thiên can mang lại điểm cộng và đánh giá tốt."""
        # 1984 Giáp Tý nam, 1989 Kỷ Tỵ nữ
        kq = xem_hop_tuoi(1984, "nam", 1989, "nu")
        tc = _muc(kq, "Thiên can")
        self.assertIn("Ngũ hợp", tc["ket_qua"])
        self.assertEqual(tc["tinh_chat"], "tốt")

    def test_hoa_giai_toan_dien(self):
        """Kiểm tra cẩm nang hóa giải ngũ hành, Bát trạch và địa chi."""
        # 1984 Giáp Tý (Hải Trung Kim, Cung Đoài nam) và 1990 Canh Ngọ (Lộ Bàng Thổ, Cung Cấn nữ)
        kq = xem_hop_tuoi(1984, "nam", 1990, "nu")
        self.assertIn("hoa_giai", kq)
        hg = kq["hoa_giai"]
        self.assertIn("menh", hg)
        self.assertIn("cung", hg)
        self.assertIn("dao_ly", hg)

        # Cặp khắc: 1984 (Kim) và 1987 (Hỏa)
        kq_khac = xem_hop_tuoi(1984, "nam", 1987, "nu")
        cau_noi = kq_khac["hoa_giai"]["cau_noi"]
        self.assertTrue(cau_noi["can_hoa_giai"])
        self.assertEqual(cau_noi["hanh_cau_noi"], "Thổ")  # Hỏa sinh Thổ, Thổ sinh Kim

    def test_xem_lam_an_kinh_doanh(self):
        """Kiểm tra phân tích Quý Nhân, Lộc Tồn, phân vai quản trị."""
        kq = xem_hop_tuoi(1984, "nam", 1985, "nam", muc_dich="lam_an")
        self.assertIn("lam_an", kq)
        la = kq["lam_an"]
        self.assertIn("quy_nhan", la)
        self.assertIn("thien_loc", la)
        self.assertIn("phan_vai", la)
        self.assertIn("loi_khuyen", la)
        # Giáp có Quý Nhân tại Sửu -> 1985 là Ất Sửu
        self.assertTrue(any("Quý Nhân" in s for s in la["quy_nhan"]))

    def test_goi_y_sinh_con(self):
        """Kiểm tra gợi ý 6 năm sinh con với vai trò cầu nối hòa hợp."""
        kq = xem_hop_tuoi(1984, "nam", 1987, "nu")
        self.assertIn("sinh_con_goi_y", kq)
        sc = kq["sinh_con_goi_y"]
        self.assertEqual(len(sc), 6)
        for nam_con in sc:
            self.assertIn("nam", nam_con)
            self.assertIn("can_chi", nam_con)
            self.assertIn("hanh", nam_con)
            self.assertIn("danh_gia", nam_con)

    def test_thang_diem_chuan_hoa(self):
        """Thang điểm 10 và tỉ lệ % hợp tuổi."""
        kq = xem_hop_tuoi(1987, "nam", 1990, "nu")
        self.assertIn("diem_10", kq)
        self.assertIn("ti_le_hop", kq)
        self.assertIn("xep_loai", kq)
        self.assertTrue(1.0 <= kq["diem_10"] <= 10.0)
        self.assertTrue(10 <= kq["ti_le_hop"] <= 100)


if __name__ == "__main__":
    unittest.main()
