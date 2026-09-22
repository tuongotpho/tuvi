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

from tuvi import (ai_luan_giai, chon_ngay, han, la_so, luan_giai, ngay_gio,  # noqa: E402
                  phong_thuy)
from tuvi.canchi import DIA_CHI  # noqa: E402
from tuvi.console import bat_utf8  # noqa: E402

bat_utf8()


def _ngay(s: str) -> tuple[int, int, int]:
    d, m, y = (int(x) for x in s.replace("-", "/").split("/"))
    return d, m, y


def _gio(s: str) -> int:
    """'14' -> 14; 'Dậu' -> 18 (đầu canh). Giờ Tý quy về 0h, giữ nguyên ngày sinh."""
    if s.isdigit():
        return int(s)
    return DIA_CHI.index(s.strip().capitalize()) * 2


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
    s.add_argument("gio", help="giờ sinh 0-23 hoặc tên canh giờ (Tý, Sửu... Hợi)")
    s.add_argument("gioi_tinh", choices=["nam", "nu"])

    s = sub.add_parser("luangiai", help="Luận giải chi tiết lá số")
    s.add_argument("ngay", help="dd/mm/yyyy dương lịch")
    s.add_argument("gio", help="giờ sinh 0-23 hoặc tên canh giờ (Tý, Sửu... Hợi)")
    s.add_argument("gioi_tinh", choices=["nam", "nu"])
    s.add_argument("--nam-xem", type=int, default=None,
                   help="năm dương lịch để đánh dấu đại hạn đang đi")

    s = sub.add_parser("ai", help="Luận giải bằng Gemini (cần GEMINI_API_KEY)")
    s.add_argument("ngay", help="dd/mm/yyyy dương lịch")
    s.add_argument("gio", help="giờ sinh 0-23 hoặc tên canh giờ")
    s.add_argument("gioi_tinh", choices=["nam", "nu"])
    s.add_argument("--nam-xem", type=int, default=None)
    s.add_argument("--model", default=None, help="mặc định lấy GEMINI_MODEL hoặc gemini-2.5-flash")
    s.add_argument("--chi-prompt", action="store_true", help="chỉ in prompt, không gọi Gemini")

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
        _in(la_so.lap_la_so(d, m, y, _gio(a.gio), gioi_tinh=a.gioi_tinh))
    elif a.lenh == "luangiai":
        d, m, y = _ngay(a.ngay)
        ls = la_so.lap_la_so(d, m, y, _gio(a.gio), gioi_tinh=a.gioi_tinh)
        _in(luan_giai.luan_giai_la_so(ls, a.nam_xem))
    elif a.lenh == "ai":
        d, m, y = _ngay(a.ngay)
        ls = la_so.lap_la_so(d, m, y, _gio(a.gio), gioi_tinh=a.gioi_tinh)
        if a.chi_prompt:
            print(ai_luan_giai.dung_prompt(ls, a.nam_xem))
        else:
            try:
                kq = ai_luan_giai.luan_giai_ai(ls, a.nam_xem, a.model)
            except (ValueError, ai_luan_giai.LoiGemini) as e:
                print(f"Không luận giải được: {e}", file=sys.stderr)
                return 1
            print(f"[{kq['model']}{' · từ cache' if kq['tu_cache'] else ''}]\n")
            print(kq["van_ban"])
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
