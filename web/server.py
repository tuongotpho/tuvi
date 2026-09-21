#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Máy chủ web tra cứu tử vi — phong thủy — hạn — xem ngày.

    python web/server.py [cong]        # mặc định cổng 8000

Chỉ dùng thư viện chuẩn của Python. Giao diện nằm trong ``web/static``,
mọi phép tính gọi thẳng gói ``tuvi`` nên số liệu trên màn hình luôn khớp
với phần đã kiểm thử.
"""
from __future__ import annotations

import json
import sys
import traceback
from datetime import date, timedelta
from functools import lru_cache
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tuvi import chon_ngay, han, la_so, ngay_gio, phong_thuy  # noqa: E402
from tuvi.canchi import CON_GIAP, can_chi_nam  # noqa: E402
from tuvi.store import load  # noqa: E402

STATIC = Path(__file__).resolve().parent / "static"

# Bố cục địa bàn truyền thống: 4x4, 12 cung vây quanh, giữa là thiên bàn.
BO_CUC = [["Tỵ", "Ngọ", "Mùi", "Thân"],
          ["Thìn", None, None, "Dậu"],
          ["Mão", None, None, "Tuất"],
          ["Dần", "Sửu", "Tý", "Hợi"]]


@lru_cache(maxsize=1)
def _tu_dien_sao() -> dict[str, dict]:
    """Tra cứu sao theo tên viết thường, vì lá số và dữ liệu viết hoa khác nhau."""
    return {s["ten"].lower(): s for s in load("tu_vi/sao")}


def _bo_sung_sao(cung: dict) -> dict:
    """Gắn ý nghĩa, tính chất và đặc tính miếu vượng cho từng sao trong cung."""
    tu_dien = _tu_dien_sao()
    sao = []
    for s in cung["sao"]:
        goc = tu_dien.get(s["ten"].lower(), {})
        sao.append({
            **s,
            "tinh_chat": goc.get("tinh_chat", "trung tính"),
            "loai": goc.get("loai", ""),
            "hanh": goc.get("hanh", ""),
            "y_nghia": goc.get("y_nghia", ""),
            "dac_tinh": goc.get("mieu_vuong_dac_ham", {}).get(cung["chi"]),
        })
    return {**cung, "sao": sao}


def api_laso(q: dict) -> dict:
    ngay, thang, nam = int(q["ngay"]), int(q["thang"]), int(q["nam"])
    gio, phut = int(q.get("gio", 12)), int(q.get("phut", 0))
    gt = q.get("gioi_tinh", "nam")
    ls = la_so.lap_la_so(ngay, thang, nam, gio, phut, gioi_tinh=gt)
    ls["cac_cung"] = [_bo_sung_sao(c) for c in ls["cac_cung"]]
    theo_chi = {c["chi"]: c for c in ls["cac_cung"]}
    ls["bo_cuc"] = [[theo_chi.get(o) for o in hang] for hang in BO_CUC]
    ls["chinh_tinh_menh"] = la_so.chinh_tinh_cung_menh(ls)
    nam_am = ls["am_lich"]["nam"]
    ls["con_giap"] = CON_GIAP[can_chi_nam(nam_am).chi_idx]
    ls["cach_cuc_goi_y"] = _goi_y_cach_cuc(ls)
    return ls


def _goi_y_cach_cuc(ls: dict) -> list[dict]:
    """Gợi ý cách cục có thể có, dựa trên chính tinh tại Mệnh và tam hợp Mệnh."""
    cung = {c["ten_cung"]: c for c in ls["cac_cung"]}
    menh = cung["Mệnh"]
    ten_sao = {s["ten"] for s in menh["sao"]}
    # Tam hợp Mệnh: Mệnh, Quan Lộc, Tài Bạch, cộng cung Thiên Di đối chiếu.
    hoi = set()
    for k in ("Mệnh", "Quan Lộc", "Tài Bạch", "Thiên Di"):
        hoi |= {s["ten"] for s in cung[k]["sao"]}
    ra = []
    for c in load("tu_vi/cach_cuc"):
        t = c["ten"]
        khop = False
        if t == "Sát Phá Tham":
            khop = {"Thất Sát", "Phá Quân", "Tham Lang"} <= hoi
        elif t == "Cơ Nguyệt Đồng Lương":
            khop = {"Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"} <= hoi
        elif t == "Tử Phủ Vũ Tướng":
            khop = {"Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"} <= hoi
        elif t == "Phủ Tướng triều viên":
            khop = {"Thiên Phủ", "Thiên Tướng"} <= hoi
        elif t == "Lộc Mã giao trì":
            khop = {"Lộc Tồn", "Thiên Mã"} <= hoi or {"Hóa Lộc", "Thiên Mã"} <= hoi
        elif t == "Song Lộc triều viên":
            khop = {"Lộc Tồn", "Hóa Lộc"} <= hoi
        elif t == "Tam hóa liên châu":
            khop = {"Hóa Lộc", "Hóa Quyền", "Hóa Khoa"} <= hoi
        elif t == "Tham Vũ đồng hành":
            khop = {"Tham Lang", "Vũ Khúc"} <= hoi
        elif t == "Mệnh vô chính diệu":
            khop = not ls["chinh_tinh_menh"]
        elif t == "Thạch trung ẩn ngọc":
            khop = "Cự Môn" in ten_sao and menh["chi"] in ("Tý", "Ngọ")
        elif t == "Mã đầu đới kiếm":
            khop = "Kình Dương" in ten_sao and menh["chi"] == "Ngọ"
        elif t == "Hỏa Tham / Linh Tham":
            khop = "Tham Lang" in ten_sao and bool(
                {"Hỏa Tinh", "Linh Tinh"} & ten_sao)
        elif t == "Khôi Việt giáp Mệnh":
            khop = _giap(ls, menh, {"Thiên Khôi", "Thiên Việt"})
        elif t == "Xương Khúc giáp Mệnh":
            khop = _giap(ls, menh, {"Văn Xương", "Văn Khúc"})
        if khop:
            ra.append(c)
    return ra


def _giap(ls: dict, menh: dict, cap: set[str]) -> bool:
    """Hai sao nằm ở hai cung kề trái phải của cung Mệnh."""
    chi_list = [c["chi"] for c in ls["cac_cung"]]
    i = chi_list.index(menh["chi"])
    ben = [ls["cac_cung"][(i - 1) % 12], ls["cac_cung"][(i + 1) % 12]]
    co = {s["ten"] for c in ben for s in c["sao"]}
    return cap <= co


def api_han(q: dict) -> dict:
    ho_so = han.ho_so_han(int(q["nam_sinh"]), int(q["nam_xem"]),
                          q.get("gioi_tinh", "nam"))
    ho_so["lam_nha"] = han.tuoi_lam_nha(int(q["nam_sinh"]), int(q["nam_xem"]))
    return ho_so


def api_phongthuy(q: dict) -> dict:
    return phong_thuy.ho_so_phong_thuy(int(q["nam_sinh"]),
                                       q.get("gioi_tinh", "nam"),
                                       q.get("huong") or None)


def api_ngay(q: dict) -> dict:
    hom_nay = date.today()
    return ngay_gio.xem_ngay(int(q.get("ngay", hom_nay.day)),
                             int(q.get("thang", hom_nay.month)),
                             int(q.get("nam", hom_nay.year)))


def api_phitinh(q: dict) -> dict:
    return phong_thuy.phi_tinh_nam(int(q.get("nam", date.today().year)))


def api_sao(q: dict) -> dict:
    ten = (q.get("ten") or "").lower()
    if ten:
        s = _tu_dien_sao().get(ten)
        if not s:
            raise KeyError(f"Không có sao tên {ten}")
        return s
    return {"sao": load("tu_vi/sao")}


def _doc_ngay(s: str | None, mac_dinh: date) -> date:
    """Nhận 'yyyy-mm-dd' từ ô <input type=date> hoặc 'dd/mm/yyyy' từ dòng lệnh."""
    if not s:
        return mac_dinh
    if "-" in s:
        nam, thang, ngay = (int(x) for x in s.split("-"))
    else:
        ngay, thang, nam = (int(x) for x in s.split("/"))
    return date(nam, thang, ngay)


def api_chonngay(q: dict) -> dict:
    hom_nay = date.today()
    tu = _doc_ngay(q.get("tu_ngay"), hom_nay)
    den = _doc_ngay(q.get("den_ngay"), tu + timedelta(days=60))
    return chon_ngay.chon_ngay(int(q["nam_sinh"]), tu, den,
                               q.get("viec") or None,
                               q.get("gioi_tinh", "nam"),
                               int(q.get("so_luong", 12)))


def api_viec(q: dict) -> dict:
    return {"viec": chon_ngay.danh_sach_viec()}


TUYEN = {"/api/laso": api_laso, "/api/han": api_han,
         "/api/chonngay": api_chonngay, "/api/viec": api_viec,
         "/api/phongthuy": api_phongthuy, "/api/ngay": api_ngay,
         "/api/phitinh": api_phitinh, "/api/sao": api_sao}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(STATIC), **kw)

    def do_GET(self):  # noqa: N802
        duong_dan = urlparse(self.path).path
        if duong_dan in TUYEN:
            q = {k: v[0] for k, v in
                 parse_qs(urlparse(self.path).query).items()}
            try:
                self._json(200, TUYEN[duong_dan](q))
            except (KeyError, ValueError, TypeError):
                self._json(400, {"loi": "Tham số không hợp lệ — kiểm tra lại "
                                        "ngày, giờ, năm sinh và giới tính."})
            except Exception as e:  # noqa: BLE001
                traceback.print_exc()
                self._json(500, {"loi": f"Lỗi máy chủ: {e}"})
            return
        super().do_GET()

    def _json(self, ma: int, obj) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(ma)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # bớt ồn, chỉ in lỗi
        if not str(args[1] if len(args) > 1 else "").startswith("2"):
            super().log_message(fmt, *args)


def main() -> int:
    cong = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    may_chu = HTTPServer(("0.0.0.0", cong), Handler)
    print(f"Giao diện tử vi đang chạy tại http://localhost:{cong}")
    print("Nhấn Ctrl+C để dừng.")
    try:
        may_chu.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
