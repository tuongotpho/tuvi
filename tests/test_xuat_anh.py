# -*- coding: utf-8 -*-
"""Kiểm ảnh SVG của lá số: đúng XML, đủ nội dung, và không có chữ nào tràn khung.

Lỗi bố cục ảnh rất khó thấy bằng mắt — phải mở ảnh ra nhìn, mà nhìn thì dễ bỏ
sót ô cuối hàng. Ở đây đo bằng số: đọc lại chính chuỗi SVG vừa sinh, tính bề
ngang ước lượng của từng đoạn chữ rồi so với mép ảnh. Cách này đã bắt được lỗi
hàng thông tin đầu dàn trên một dòng làm mất ô "Tuần / Triệt".
"""
from __future__ import annotations

import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tuvi import la_so, xuat_anh  # noqa: E402

SVG_NS = "{http://www.w3.org/2000/svg}"

# Vài lá số đủ khác nhau: nhiều sao dồn một cung, vô chính diệu, tháng nhuận,
# và cả hai giới để nhãn THÂN rơi vào chỗ khác nhau.
CA_KIEM = [
    (27, 11, 1987, 20, "nu"),
    (20, 9, 1990, 14, "nam"),
    (1, 1, 1985, 6, "nu"),
    (22, 8, 1987, 10, "nam"),
    (5, 7, 1992, 2, "nu"),
    (13, 6, 2020, 23, "nam"),
]


def _la_so(d: int, m: int, y: int, g: int, gt: str) -> dict:
    ls = la_so.lap_la_so(d, m, y, g, 0, gioi_tinh=gt)
    ls["chinh_tinh_menh"] = la_so.chinh_tinh_cung_menh(ls)
    return ls


class TestAnhLaSo(unittest.TestCase):
    def _cay(self, svg: str) -> ET.Element:
        return ET.fromstring(svg)

    def test_la_xml_hop_le(self):
        for ca in CA_KIEM:
            svg = xuat_anh.ve_la_so_svg(_la_so(*ca))
            goc = self._cay(svg)   # sai cú pháp là ném ParseError ngay
            self.assertEqual(goc.tag, f"{SVG_NS}svg", ca)

    def test_khong_co_chu_nao_tran_khung(self):
        """Mọi đoạn chữ phải nằm trọn trong khổ ảnh, kể cả chữ căn phải."""
        for ca in CA_KIEM:
            svg = xuat_anh.ve_la_so_svg(_la_so(*ca))
            goc = self._cay(svg)
            cao = float(goc.get("height"))
            for t in goc.iter(f"{SVG_NS}text"):
                chu = "".join(t.itertext())
                co = float(t.get("font-size", 16))
                x, y = float(t.get("x")), float(t.get("y"))
                rong = xuat_anh._rong_chu(chu, co)
                if t.get("text-anchor") == "end":
                    trai, phai = x - rong, x
                else:
                    trai, phai = x, x + rong
                self.assertGreaterEqual(trai, 0, f"{ca}: '{chu}' tràn mép trái")
                self.assertLessEqual(phai, xuat_anh.RONG,
                                     f"{ca}: '{chu}' tràn mép phải")
                self.assertLessEqual(y, cao, f"{ca}: '{chu}' tràn mép dưới")

    def test_sao_khong_de_len_dong_dai_han(self):
        """Ô cung phải đủ cao cho cung nhiều sao nhất, không đè lên dòng chân ô."""
        for ca in CA_KIEM:
            ls = _la_so(*ca)
            svg = xuat_anh.ve_la_so_svg(ls)
            cao_anh = float(self._cay(svg).get("height"))
            o_cao = (cao_anh - xuat_anh.CAO_DAU - xuat_anh.CAO_CHAN) / 4
            from tuvi.luan_giai import bo_sung_y_nghia_sao
            rong_sao = xuat_anh.O_RONG - xuat_anh.KHE - 24
            for c in ls["cac_cung"]:
                dong = xuat_anh._xep_sao(bo_sung_y_nghia_sao(c)["sao"], rong_sao)
                day_sao = xuat_anh.DAU_O + len(dong) * xuat_anh.BUOC_DONG
                vach_chan = o_cao - xuat_anh.KHE - 30
                self.assertLessEqual(day_sao, vach_chan,
                                     f"{ca}: cung {c['ten_cung']} có {len(dong)} dòng sao "
                                     f"nhưng ô chỉ cao {o_cao:.0f}")

    def test_co_du_12_cung_va_109_sao(self):
        ls = _la_so(*CA_KIEM[0])
        svg = xuat_anh.ve_la_so_svg(ls)
        for c in ls["cac_cung"]:
            self.assertIn(f">{c['ten_cung']}<", svg, c["ten_cung"])
        ten_sao = [s["ten"] for c in ls["cac_cung"] for s in c["sao"]]
        self.assertEqual(len(ten_sao), 109)
        thieu = [t for t in ten_sao if f">{t}<" not in svg]
        self.assertEqual(thieu, [], "sao bị thiếu khỏi ảnh")

    def test_danh_dau_menh_than_tuan_triet(self):
        ls = _la_so(*CA_KIEM[0])
        svg = xuat_anh.ve_la_so_svg(ls)
        self.assertIn(">THÂN<", svg)
        self.assertIn(">TUẦN<", svg)
        self.assertIn(">TRIỆT<", svg)

    def test_thoat_ky_tu_dac_biet(self):
        """Tiêu đề do người dùng đặt phải được thoát, không phá vỡ XML."""
        svg = xuat_anh.ve_la_so_svg(_la_so(*CA_KIEM[0]), tieu_de='A & B <script>"x"')
        self.assertNotIn("<script>", svg)
        self.assertEqual(self._cay(svg).tag, f"{SVG_NS}svg")

    def test_khong_phu_thuoc_goi_ngoai(self):
        """Bản đóng gói .exe không có thư viện đồ họa nào, nên mô-đun này
        chỉ được dùng thư viện chuẩn."""
        ma = (Path(__file__).resolve().parent.parent / "tuvi" / "xuat_anh.py"
              ).read_text(encoding="utf-8")
        for goi in ("PIL", "cairo", "matplotlib", "reportlab", "playwright"):
            self.assertNotIn(f"import {goi}", ma)


if __name__ == "__main__":
    unittest.main()
