# -*- coding: utf-8 -*-
"""Ép luồng in ra màn hình dùng UTF-8.

Trên Windows, PowerShell và cmd mặc định giao cho Python bảng mã cp1252 —
không có các chữ như "ả", "ố" — nên bất kỳ lệnh ``print`` tiếng Việt nào cũng
sập với ``UnicodeEncodeError``. Gọi ``bat_utf8()`` ở đầu mỗi script dòng lệnh
để khỏi phải nhớ đặt ``PYTHONUTF8=1``.
"""
from __future__ import annotations

import sys


def bat_utf8() -> None:
    """Chuyển stdout/stderr sang UTF-8 nếu chúng chưa dùng bảng mã đó."""
    for luong in (sys.stdout, sys.stderr):
        if luong is None:
            continue
        if (luong.encoding or "").lower().replace("-", "") == "utf8":
            continue
        reconfigure = getattr(luong, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")
