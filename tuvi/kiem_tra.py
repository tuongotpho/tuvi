# -*- coding: utf-8 -*-
"""Kiểm tra đầu vào cho mọi hàm công khai của gói ``tuvi``.

Trước đây một ngày không có thật như 31/02/1990 vẫn được đổi lịch rồi lập lá số
như thường (thuật toán Julius tự "trôi" sang 03/03), giờ 99 hay giới tính lạ cũng
lọt qua. Mọi hàm ở đây ném :class:`LoiDauVao` (một ``ValueError``) với thông báo
tiếng Việt, để máy chủ web trả về cho người dùng nguyên văn.
"""
from __future__ import annotations

from datetime import date

from .canchi import DIA_CHI

NAM_MIN, NAM_MAX = 1800, 2199   # khoảng thuật toán âm lịch đã đối chiếu 100%


class LoiDauVao(ValueError):
    """Đầu vào không hợp lệ; thông báo an toàn để hiện cho người dùng."""


def so_nguyen(gia_tri, ten: str, thap: int | None = None, cao: int | None = None) -> int:
    """Ép về int và kiểm khoảng; ``gia_tri`` có thể là chuỗi từ query."""
    try:
        n = int(str(gia_tri).strip())
    except (TypeError, ValueError):
        raise LoiDauVao(f"{ten} phải là số nguyên, đang nhận '{gia_tri}'.") from None
    if thap is not None and n < thap or cao is not None and n > cao:
        raise LoiDauVao(f"{ten} phải trong khoảng {thap}–{cao}, đang nhận {n}.")
    return n


def nam_hop_le(nam, ten: str = "Năm") -> int:
    return so_nguyen(nam, ten, NAM_MIN, NAM_MAX)


def ngay_duong_hop_le(ngay, thang, nam) -> date:
    """Ngày dương lịch có thật và nằm trong khoảng thuật toán."""
    y = nam_hop_le(nam, "Năm")
    m = so_nguyen(thang, "Tháng", 1, 12)
    d = so_nguyen(ngay, "Ngày", 1, 31)
    try:
        return date(y, m, d)
    except ValueError:
        raise LoiDauVao(f"Ngày {d:02d}/{m:02d}/{y} không có thật trên lịch dương.") from None


def ngay_am_hop_le(ngay, thang, nam) -> tuple[int, int, int]:
    return (so_nguyen(ngay, "Ngày âm", 1, 30), so_nguyen(thang, "Tháng âm", 1, 12),
            nam_hop_le(nam, "Năm âm"))


def gio_phut_hop_le(gio, phut=0) -> tuple[int, int]:
    return so_nguyen(gio, "Giờ", 0, 23), so_nguyen(phut, "Phút", 0, 59)


def canh_gio_hop_le(canh) -> int:
    """'Dậu' hoặc '9' -> 9. Chấp nhận viết thường, thừa khoảng trắng."""
    s = str(canh).strip()
    if s.isdigit():
        return so_nguyen(s, "Canh giờ", 0, 11)
    ten = s.capitalize()
    if ten not in DIA_CHI:
        raise LoiDauVao(f"Canh giờ '{canh}' không hợp lệ; dùng Tý, Sửu, Dần… Hợi hoặc số 0–11.")
    return DIA_CHI.index(ten)


def gioi_tinh_hop_le(gt) -> str:
    """Chỉ nhận nam/nữ (mọi cách viết thường gặp) và trả về 'nam' hoặc 'nu'."""
    s = str(gt or "").strip().lower()
    if s in ("nam", "male", "m", "1"):
        return "nam"
    if s in ("nu", "nữ", "female", "f", "0"):
        return "nu"
    raise LoiDauVao(f"Giới tính phải là 'nam' hoặc 'nu', đang nhận '{gt}'.")


def nam_sinh_va_nam_xem(nam_sinh, nam_xem) -> tuple[int, int]:
    ns = nam_hop_le(nam_sinh, "Năm sinh")
    nx = nam_hop_le(nam_xem, "Năm xem")
    if nx < ns:
        raise LoiDauVao(f"Năm xem {nx} không thể trước năm sinh {ns}.")
    return ns, nx


__all__ = ["LoiDauVao", "so_nguyen", "nam_hop_le", "ngay_duong_hop_le", "ngay_am_hop_le",
           "gio_phut_hop_le", "canh_gio_hop_le", "gioi_tinh_hop_le", "nam_sinh_va_nam_xem",
           "NAM_MIN", "NAM_MAX"]
