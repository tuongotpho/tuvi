# -*- coding: utf-8 -*-
"""Đường dẫn dùng chung cho cả hai cách chạy: từ mã nguồn và từ tệp .exe.

PyInstaller giải nén tài nguyên vào một thư mục tạm (``sys._MEIPASS``) mỗi lần
chạy, nên ``__file__`` không còn dùng để tìm tệp dữ liệu được, và càng không
dùng để **ghi** (thư mục đó bị xóa khi thoát, lại hay nằm trong Program Files).

Vì vậy tách đôi:

* :func:`thu_muc_tai_nguyen` — nơi đọc ``data/``, ``web/static/``, ``content/``.
* :func:`thu_muc_ghi` — nơi ghi ``.env``, cache bài AI, tệp nhật ký: cạnh tệp
  .exe, để chép cả thư mục đi đâu cũng mang theo cấu hình.
"""
from __future__ import annotations

import sys
from pathlib import Path

_GOC_MA_NGUON = Path(__file__).resolve().parent.parent


def dang_dong_goi() -> bool:
    """True khi đang chạy từ tệp .exe do PyInstaller dựng."""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def thu_muc_tai_nguyen() -> Path:
    """Gốc của tài nguyên chỉ đọc (data/, web/static/, content/)."""
    if dang_dong_goi():
        return Path(sys._MEIPASS)   # noqa: SLF001 — PyInstaller đặt sẵn
    return _GOC_MA_NGUON


def thu_muc_ghi() -> Path:
    """Gốc để ghi: cạnh tệp .exe khi đã đóng gói, gốc kho khi chạy mã nguồn."""
    if dang_dong_goi():
        return Path(sys.executable).resolve().parent
    return _GOC_MA_NGUON


__all__ = ["dang_dong_goi", "thu_muc_tai_nguyen", "thu_muc_ghi"]
