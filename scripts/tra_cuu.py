#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Công cụ dòng lệnh tra cứu nhanh — cũng là ví dụ dùng gói ``tuvi``.

    python scripts/tra_cuu.py ngay 20/09/2026
    python scripts/tra_cuu.py han 1990 2026 nam
    python scripts/tra_cuu.py nha 1990 2027
    python scripts/tra_cuu.py phongthuy 1990 nam --huong "Đông Nam"
    python scripts/tra_cuu.py laso 20/09/1990 14 nam
    python scripts/tra_cuu.py phitinh 2026
    python scripts/tra_cuu.py chonngay 1987 01/10/2026 30/11/2026 --viec dong_tho
    python scripts/tra_cuu.py viec
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tuvi import chon_ngay, han, la_so, ngay_gio, phong_thuy  # noqa: E402
from tuvi.console import bat_utf8  # noqa: E402

bat_utf8()


def _ngay(s: str) -> tuple[int, int, int]:
    d, m, y = (int(x) for x in s.replace("-", "/").split("/"))
    return d, m, y


def _in(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=1))


def main() -> int:
    p = argparse.ArgumentParser(description="Tra cứu tử vi — phong thủy — hạn")
    sub = p.add_subparsers(dest="lenh", required=True)

    s = sub.add_parser("ngay", help="Xem ngày tốt xấu")
    s.add_argument("ngay", help="dd/mm/yyyy dương lịch")

    s = sub.add_parser("han", help="Hồ sơ hạn của một người trong một năm")
    s.add_argument("nam_sinh", type=int)
    s.add_argument("nam_xem", type=int)
    s.add_argument("gioi_tinh", choices=["nam", "nu"])

    s = sub.add_parser("nha", help="Xem tuổi làm nhà")
    s.add_argument("nam_sinh", type=int)
    s.add_argument("nam_lam", type=int)

    s = sub.add_parser("phongthuy", help="Cung phi và hướng hợp tuổi")
    s.add_argument("nam_sinh", type=int)
    s.add_argument("gioi_tinh", choices=["nam", "nu"])
    s.add_argument("--huong", default=None, help="Hướng nhà muốn kiểm tra")

    s = sub.add_parser("laso", help="Lập lá số tử vi rút gọn")
    s.add_argument("ngay", help="dd/mm/yyyy dương lịch")
    s.add_argument("gio", type=int, help="giờ sinh 0-23")
    s.add_argument("gioi_tinh", choices=["nam", "nu"])

    s = sub.add_parser("phitinh", help="Cửu cung phi tinh của một năm")
    s.add_argument("nam", type=int)

    s = sub.add_parser("chonngay", help="Chọn ngày tốt theo tuổi, loại ngày xung")
    s.add_argument("nam_sinh", type=int, help="năm sinh âm lịch")
    s.add_argument("tu_ngay", help="dd/mm/yyyy")
    s.add_argument("den_ngay", help="dd/mm/yyyy")
    s.add_argument("--viec", default=None, help="mã việc, xem lệnh 'viec'")
    s.add_argument("--gioi-tinh", default="nam", choices=["nam", "nu"])
    s.add_argument("--so-luong", type=int, default=10)

    sub.add_parser("viec", help="Liệt kê các việc chọn ngày đang hỗ trợ")

    a = p.parse_args()

    if a.lenh == "ngay":
        _in(ngay_gio.xem_ngay(*_ngay(a.ngay)))
    elif a.lenh == "han":
        _in(han.ho_so_han(a.nam_sinh, a.nam_xem, a.gioi_tinh))
    elif a.lenh == "nha":
        _in(han.tuoi_lam_nha(a.nam_sinh, a.nam_lam))
    elif a.lenh == "phongthuy":
        _in(phong_thuy.ho_so_phong_thuy(a.nam_sinh, a.gioi_tinh, a.huong))
    elif a.lenh == "laso":
        d, m, y = _ngay(a.ngay)
        _in(la_so.lap_la_so(d, m, y, a.gio, gioi_tinh=a.gioi_tinh))
    elif a.lenh == "phitinh":
        _in(phong_thuy.phi_tinh_nam(a.nam))
    elif a.lenh == "chonngay":
        ngay = lambda s: date(*reversed([int(x) for x in s.split("/")]))  # noqa: E731
        _in(chon_ngay.chon_ngay(a.nam_sinh, ngay(a.tu_ngay), ngay(a.den_ngay),
                                a.viec, a.gioi_tinh, a.so_luong))
    elif a.lenh == "viec":
        _in([{k: v[k] for k in ("ma", "ten", "so_truc_khop", "so_tu_khop", "ghi_chu")}
             for v in chon_ngay.danh_sach_viec()])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
