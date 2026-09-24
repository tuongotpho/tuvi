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
import socket
import sys
import threading
import time
import traceback
import unicodedata
from datetime import date, datetime, timedelta, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tuvi import (ai_luan_giai, chon_ngay, han, hop_tuoi,  # noqa: E402
                  la_so, ngay_gio, phong_thuy)
from tuvi.canchi import CON_GIAP, can_chi_nam  # noqa: E402
from tuvi.store import load  # noqa: E402
from tuvi.console import bat_utf8  # noqa: E402
from tuvi.kiem_tra import (LoiDauVao, canh_gio_hop_le, gio_phut_hop_le,  # noqa: E402
                           gioi_tinh_hop_le, nam_hop_le, ngay_duong_hop_le,
                           so_nguyen)
from tuvi.luan_giai import (bo_sung_y_nghia_sao, goi_y_cach_cuc,  # noqa: E402
                            luan_giai_la_so, tra_sao)
from tuvi.xuat_anh import ve_la_so_svg  # noqa: E402

bat_utf8()

STATIC = Path(__file__).resolve().parent / "static"
GIO_VN = timezone(timedelta(hours=7))


def hom_nay_vn() -> date:
    """Ngày hôm nay theo giờ Việt Nam, không phụ thuộc múi giờ máy chủ."""
    return datetime.now(GIO_VN).date()

BO_CUC = la_so.BO_CUC_DIA_BAN   # bố cục 4x4, định nghĩa trong tuvi/la_so.py


def api_laso(q: dict) -> dict:
    ls = _la_so_tu_query(q)
    theo_chi = {c["chi"]: c for c in ls["cac_cung"]}
    ls["bo_cuc"] = [[theo_chi.get(o) for o in hang] for hang in BO_CUC]
    ls["cach_cuc_goi_y"] = goi_y_cach_cuc(ls)
    return ls


def api_luangiai(q: dict) -> dict:
    """Luận giải chi tiết; cùng tham số với /api/laso, thêm nam_xem (mặc định năm nay)."""
    ls = _la_so_tu_query(q)
    nam_xem = nam_hop_le(q.get("nam_xem") or hom_nay_vn().year, "Năm xem")
    return luan_giai_la_so(ls, nam_xem)


def _khong_dau(chuoi: str) -> str:
    """Bỏ dấu tiếng Việt, còn lại chữ ASCII thường, số và dấu nối.

    Tên tệp đi trong header HTTP mà header chỉ nhận bảng mã latin-1, nên
    "la-so-19871127-tuất.svg" làm máy chủ ném UnicodeEncodeError và ngắt kết nối
    giữa chừng — đã dính một lần, có bài kiểm chặn lại.
    """
    thay = unicodedata.normalize("NFD", chuoi.replace("đ", "d").replace("Đ", "D"))
    thay = "".join(c for c in thay if not unicodedata.combining(c)).lower()
    return "".join(c if c.isalnum() or c in "-_." else "-" for c in thay)


def api_laso_svg(q: dict) -> tuple[str, str]:
    """Lá số vẽ thành ảnh SVG. Trả về (chuỗi SVG, tên tệp gợi ý khi tải về)."""
    ls = _la_so_tu_query(q)
    am = ls["am_lich"]
    d = ngay_duong_hop_le(q.get("ngay"), q.get("thang"), q.get("nam"))
    tieu_de = (f'Lá số {d.day:02d}/{d.month:02d}/{d.year} · {ls["gioi_tinh"].lower()}'
               f' · giờ {am["gio"]}')
    ten_tep = _khong_dau(f'la-so-{d.year}{d.month:02d}{d.day:02d}-{am["gio"]}.svg')
    return ve_la_so_svg(ls, tieu_de), ten_tep


# Gọi Gemini tốn tiền và chậm (5–20 giây) nên có hai khóa van: tối đa
# AI_DONG_THOI lượt cùng lúc, và mỗi địa chỉ IP phải cách nhau AI_GIAY_MOI_IP giây.
AI_DONG_THOI = 2
AI_GIAY_MOI_IP = 15
_ai_van = threading.BoundedSemaphore(AI_DONG_THOI)
_ai_lan_cuoi: dict[str, float] = {}
_ai_khoa = threading.Lock()


def api_ai_luangiai(q: dict, ip: str = "-") -> dict:
    """Luận giải bằng Gemini; cùng tham số với /api/luangiai."""
    if not ai_luan_giai.khoa_api():
        raise LoiCauHinh("Máy chủ chưa cấu hình GEMINI_API_KEY nên chưa bật được luận giải AI.")
    # Kiểm đầu vào trước, rồi mới tính lượt: gõ sai ngày không làm mất 15 giây chờ.
    ls = _la_so_tu_query(q)
    nam_xem = nam_hop_le(q.get("nam_xem") or hom_nay_vn().year, "Năm xem")
    with _ai_khoa:
        bay_gio = time.monotonic()
        if bay_gio - _ai_lan_cuoi.get(ip, -1e9) < AI_GIAY_MOI_IP:
            raise LoiQuaTai(f"Mỗi {AI_GIAY_MOI_IP} giây chỉ gọi AI được một lần, đợi chút rồi thử lại.")
        _ai_lan_cuoi[ip] = bay_gio
        if len(_ai_lan_cuoi) > 5000:   # không để bảng IP phình mãi
            _ai_lan_cuoi.clear()
    if not _ai_van.acquire(timeout=0.5):
        raise LoiQuaTai("Đang có người khác dùng AI, thử lại sau vài giây.")
    try:
        return ai_luan_giai.luan_giai_ai(ls, nam_xem)
    finally:
        _ai_van.release()


class LoiCauHinh(RuntimeError):
    """Thiếu cấu hình phía máy chủ (503)."""


class LoiQuaTai(RuntimeError):
    """Gọi dồn dập (429)."""


def _gio_tu_query(q: dict) -> tuple[int, int]:
    """Giờ sinh từ query: ``canh=Dậu`` (hoặc chỉ số 0-11) ưu tiên hơn ``gio``/``phut``.

    Giờ Tý (23h-1h) tính theo đúng ngày sinh, không chuyển sang ngày hôm sau,
    nên canh Tý quy về 0h00 của ngày đã nhập.
    """
    canh = (q.get("canh") or "").strip()
    if canh:
        return canh_gio_hop_le(canh) * 2, 0
    return gio_phut_hop_le(q.get("gio", 12), q.get("phut", 0))


def _la_so_tu_query(q: dict) -> dict:
    d = ngay_duong_hop_le(q.get("ngay"), q.get("thang"), q.get("nam"))
    gio, phut = _gio_tu_query(q)
    gt = gioi_tinh_hop_le(q.get("gioi_tinh", "nam"))
    ls = la_so.lap_la_so(d.day, d.month, d.year, gio, phut, gioi_tinh=gt)
    ls["cac_cung"] = [bo_sung_y_nghia_sao(c) for c in ls["cac_cung"]]
    ls["chinh_tinh_menh"] = la_so.chinh_tinh_cung_menh(ls)
    ls["con_giap"] = CON_GIAP[can_chi_nam(ls["am_lich"]["nam"]).chi_idx]
    return ls


def api_han(q: dict) -> dict:
    ns, nx = _nam_sinh(q), nam_hop_le(q.get("nam_xem") or hom_nay_vn().year, "Năm xem")
    ho_so = han.ho_so_han(ns, nx, gioi_tinh_hop_le(q.get("gioi_tinh", "nam")))
    ho_so["lam_nha"] = han.tuoi_lam_nha(ns, nx)
    return ho_so


def _nam_sinh(q: dict) -> int:
    """Năm sinh âm lịch: nhận thẳng ``nam_sinh`` hoặc suy từ ``ngay_sinh=yyyy-mm-dd`` dương lịch.

    Người sinh tháng 1–2 dương trước Tết thuộc năm âm trước đó, nên giao diện
    gửi ngày sinh dương để máy tự đổi, tránh gõ nhầm năm âm.
    """
    ngay_sinh = q.get("ngay_sinh")
    if ngay_sinh:
        d = _doc_ngay(ngay_sinh, hom_nay_vn())
        return la_so.solar_to_lunar(d.day, d.month, d.year).year
    return nam_hop_le(q.get("nam_sinh"), "Năm sinh")


def api_phongthuy(q: dict) -> dict:
    return phong_thuy.ho_so_phong_thuy(_nam_sinh(q),
                                       gioi_tinh_hop_le(q.get("gioi_tinh", "nam")),
                                       (q.get("huong") or "").strip() or None)


def api_ngay(q: dict) -> dict:
    hom_nay = hom_nay_vn()
    d = ngay_duong_hop_le(q.get("ngay", hom_nay.day), q.get("thang", hom_nay.month),
                          q.get("nam", hom_nay.year))
    return ngay_gio.chi_tiet_ngay(d.day, d.month, d.year)


def api_lich_thang(q: dict) -> dict:
    hom_nay = hom_nay_vn()
    return ngay_gio.lich_thang(q.get("thang") or hom_nay.month, q.get("nam") or hom_nay.year)


def api_phitinh(q: dict) -> dict:
    return phong_thuy.phi_tinh_nam(nam_hop_le(q.get("nam") or hom_nay_vn().year, "Năm"))


def api_sao(q: dict) -> dict:
    ten = (q.get("ten") or "").strip().lower()
    if ten:
        s = tra_sao(ten)
        if not s:
            raise LoiDauVao(f"Không có sao tên '{ten}'.")
        return s
    return {"sao": load("tu_vi/sao")}


def _doc_ngay(s: str | None, mac_dinh: date) -> date:
    """Nhận 'yyyy-mm-dd' từ ô <input type=date> hoặc 'dd/mm/yyyy' từ dòng lệnh."""
    if not s:
        return mac_dinh
    try:
        if "-" in s:
            nam, thang, ngay = s.split("-")
        else:
            ngay, thang, nam = s.split("/")
    except ValueError:
        raise LoiDauVao(f"Ngày '{s}' phải có dạng yyyy-mm-dd hoặc dd/mm/yyyy.") from None
    return ngay_duong_hop_le(ngay, thang, nam)


def api_chonngay(q: dict) -> dict:
    tu = _doc_ngay(q.get("tu_ngay"), hom_nay_vn())
    den = _doc_ngay(q.get("den_ngay"), tu + timedelta(days=60))
    return chon_ngay.chon_ngay(_nam_sinh(q), tu, den,
                               (q.get("viec") or "").strip() or None,
                               gioi_tinh_hop_le(q.get("gioi_tinh", "nam")),
                               so_nguyen(q.get("so_luong", 12), "Số ngày muốn lấy",
                                         1, chon_ngay.SO_LUONG_TOI_DA))


def api_hoptuoi(q: dict) -> dict:
    """Xem tuổi hai người có hợp nhau không.

    Nhận năm sinh âm lịch (``nam_sinh_a``) hoặc ngày sinh dương lịch
    (``ngay_sinh_a=yyyy-mm-dd``) — dùng ngày dương thì máy tự đổi, tránh chuyện
    người sinh trước Tết bị tính nhầm sang năm âm sau.
    """
    def nam_cua(hau_to: str) -> int:
        ngay_sinh = q.get(f"ngay_sinh_{hau_to}")
        if ngay_sinh:
            d = _doc_ngay(ngay_sinh, hom_nay_vn())
            return la_so.solar_to_lunar(d.day, d.month, d.year).year
        return nam_hop_le(q.get(f"nam_sinh_{hau_to}"), f"Năm sinh người {hau_to.upper()}")

    return hop_tuoi.xem_hop_tuoi(nam_cua("a"), q.get("gioi_tinh_a", "nam"),
                                 nam_cua("b"), q.get("gioi_tinh_b", "nu"),
                                 muc_dich=q.get("muc_dich", "hon_nhan"))


def api_viec(q: dict) -> dict:
    return {"viec": chon_ngay.danh_sach_viec()}


TUYEN = {"/api/laso": api_laso, "/api/luangiai": api_luangiai, "/api/han": api_han,
         "/api/chonngay": api_chonngay, "/api/viec": api_viec,
         "/api/hoptuoi": api_hoptuoi,
         "/api/phongthuy": api_phongthuy, "/api/ngay": api_ngay,
         "/api/lichthang": api_lich_thang,
         "/api/phitinh": api_phitinh, "/api/sao": api_sao,
         "/api/ai-luangiai": api_ai_luangiai}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(STATIC), **kw)

    def do_GET(self):  # noqa: N802
        duong_dan = urlparse(self.path).path
        if duong_dan == "/api/laso.svg":
            q = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}
            try:
                svg, ten_tep = api_laso_svg(q)
            except LoiDauVao as e:
                self._json(400, {"loi": str(e)})
            except (KeyError, ValueError, TypeError, OverflowError):
                self._json(400, {"loi": "Tham số không hợp lệ."})
            else:
                self._svg(svg, ten_tep, tai_ve=q.get("tai_ve") == "1")
            return
        if duong_dan in TUYEN:
            q = {k: v[0] for k, v in
                 parse_qs(urlparse(self.path).query).items()}
            try:
                if duong_dan == "/api/ai-luangiai":
                    self._json(200, api_ai_luangiai(q, self.client_address[0]))
                else:
                    self._json(200, TUYEN[duong_dan](q))
            except LoiCauHinh as e:
                self._json(503, {"loi": str(e)})
            except LoiQuaTai as e:
                self._json(429, {"loi": str(e)})
            except ai_luan_giai.LoiGemini as e:
                self._json(502, {"loi": str(e)})
            except LoiDauVao as e:
                # Thông báo do chính kho này viết, an toàn để hiện cho người dùng.
                self._json(400, {"loi": str(e)})
            except (KeyError, ValueError, TypeError, OverflowError):
                self._json(400, {"loi": "Tham số không hợp lệ — kiểm tra lại "
                                        "ngày, giờ, năm sinh và giới tính."})
            except Exception:  # noqa: BLE001
                # Chi tiết chỉ ghi vào log máy chủ, không trả cho client.
                traceback.print_exc()
                self._json(500, {"loi": "Lỗi máy chủ. Thử lại sau."})
            return
        super().do_GET()

    def _svg(self, svg: str, ten_tep: str, tai_ve: bool = False) -> None:
        body = svg.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if tai_ve:
            # Tên tệp chỉ gồm chữ số và dấu nối do máy tự đặt, không lấy từ người
            # dùng, nên không có nguy cơ chèn ký tự lạ vào header.
            self.send_header("Content-Disposition", f'attachment; filename="{ten_tep}"')
        self.end_headers()
        self.wfile.write(body)

    def _json(self, ma: int, obj) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(ma)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):  # noqa: D102 — thêm header chung cho cả file tĩnh
        self.send_header("Referrer-Policy", "no-referrer")
        if not self.path.startswith("/api/"):
            # File tĩnh: trình duyệt phải hỏi lại máy chủ mỗi lần (304 nếu chưa đổi),
            # kẻo cập nhật web xong người dùng vẫn chạy app.js cũ trong cache.
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, fmt, *args):  # chỉ in lỗi, và không in query string
        # Query chứa ngày giờ sinh (dữ liệu cá nhân) nên cắt bỏ trước khi ghi log.
        if not str(args[1] if len(args) > 1 else "").startswith("2"):
            args = tuple(a.split("?")[0] if isinstance(a, str) else a for a in args)
            super().log_message(fmt, *args)


def _mo_may_chu(cong: int) -> ThreadingHTTPServer:
    class KepGiao(ThreadingHTTPServer):
        address_family = socket.AF_INET6

        def server_bind(self):
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            super().server_bind()

    try:
        return KepGiao(("::", cong), Handler)
    except OSError:  # máy không có IPv6
        return ThreadingHTTPServer(("0.0.0.0", cong), Handler)


def main() -> int:
    cong = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    # Đa luồng: trình duyệt hay mở sẵn kết nối dự phòng mà chưa gửi yêu cầu,
    # bản một luồng sẽ kẹt chờ kết nối đó và mọi yêu cầu thật đứng hình theo.
    # Lắng nghe cả IPv6 lẫn IPv4: trình duyệt gọi "localhost" thử ::1 trước,
    # nếu chỉ mở IPv4 thì mỗi lượt gọi phải chờ hết giờ ~2 giây mới quay lại.
    may_chu = _mo_may_chu(cong)
    print(f"Giao diện tử vi đang chạy tại http://localhost:{cong}", flush=True)
    print("Nhấn Ctrl+C để dừng.", flush=True)
    try:
        may_chu.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
