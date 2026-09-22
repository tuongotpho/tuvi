# -*- coding: utf-8 -*-
"""Chạy bộ tra cứu tử vi như một ứng dụng để bàn (cửa sổ riêng, không trình duyệt).

Máy chủ web chạy ở một luồng nền, **chỉ lắng nghe 127.0.0.1** (khác bản
``web/server.py`` mở ra cả mạng LAN): đây là app cá nhân, ngày giờ sinh không
nên ra khỏi máy. Giao diện được nhúng vào một cửa sổ WebView2 nên trông như
ứng dụng bình thường.

    python app.py              chạy từ mã nguồn
    python app.py --kiem-tra   chỉ bật máy chủ, tự gọi thử vài API rồi thoát
    Tuvi.exe                   sau khi dựng bằng build.bat
"""
from __future__ import annotations

import json
import os
import socket
import sys
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

GOC = Path(__file__).resolve().parent
if str(GOC) not in sys.path:
    sys.path.insert(0, str(GOC))

from tuvi.console import bat_utf8  # noqa: E402
from tuvi.duong_dan import thu_muc_ghi, thu_muc_tai_nguyen  # noqa: E402

TEN_APP = "Tử Vi"


def bao_dam_dau_ra() -> None:
    """Chế độ cửa sổ không có console nên sys.stdout/stderr là None.

    Để nguyên thì mọi lỗi bị nuốt sạch, app chết im lặng không dấu vết; trỏ
    chúng vào tệp nhật ký cạnh tệp .exe.
    """
    if sys.stdout is not None and sys.stderr is not None:
        return
    try:
        luong = open(thu_muc_ghi() / "tuvi.log", "a", encoding="utf-8", buffering=1)
    except OSError:
        luong = open(os.devnull, "w", encoding="utf-8")
    if sys.stdout is None:
        sys.stdout = luong
    if sys.stderr is None:
        sys.stderr = luong


def cong_trong() -> int:
    """Xin hệ điều hành một cổng còn trống, tránh đụng app khác ở 8000."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def bat_may_chu(cong: int) -> ThreadingHTTPServer:
    from web.server import Handler
    may_chu = ThreadingHTTPServer(("127.0.0.1", cong), Handler)
    threading.Thread(target=may_chu.serve_forever, daemon=True).start()
    return may_chu


def cho_may_chu(cong: int, han: float = 20.0) -> bool:
    het_gio = time.monotonic() + han
    while time.monotonic() < het_gio:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", cong)) == 0:
                return True
        time.sleep(0.15)
    return False


def kiem_tra(cong: int) -> int:
    """Tự gọi vài API để chắc chắn bản đóng gói vẫn đọc được data/ và web/static/."""
    goc = f"http://127.0.0.1:{cong}"
    phep_thu = [
        ("/", lambda t: "<title>" in t.lower()),
        ("/api/laso?ngay=20&thang=9&nam=1990&gio=14&gioi_tinh=nam",
         lambda t: len(json.loads(t)["cac_cung"]) == 12
         and sum(len(c["sao"]) for c in json.loads(t)["cac_cung"]) == 109),
        ("/api/luangiai?ngay=20&thang=9&nam=1990&gio=14&gioi_tinh=nam&nam_xem=2026",
         lambda t: bool(json.loads(t)["tong_quan"])),
        ("/api/han?nam_sinh=1987&nam_xem=2026&gioi_tinh=nam",
         lambda t: bool(json.loads(t)["sao_han"])),
        ("/api/phongthuy?nam_sinh=1987&gioi_tinh=nam", lambda t: bool(json.loads(t)["cung_phi"])),
        # Ảnh lá số: bản đóng gói vẽ được thì mới có nút tải ảnh / in PDF.
        ("/api/laso.svg?ngay=27&thang=11&nam=1987&gio=20&gioi_tinh=nu",
         lambda t: t.lstrip().startswith("<svg") and t.count("<text") > 150),
    ]
    hong = 0
    for duong_dan, kiem in phep_thu:
        try:
            with urllib.request.urlopen(goc + duong_dan, timeout=20) as r:
                ok = kiem(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001 — kiểm tra thì lỗi gì cũng phải in ra
            ok, e_ = False, e
            print(f"  LỖI {duong_dan} -> {e_}")
        print(f"  {'ĐẠT ' if ok else 'HỎNG'} {duong_dan[:70]}")
        hong += not ok
    # Khóa Gemini phải đọc được từ .env ĐẶT CẠNH TỆP .EXE, không phải trong gói.
    from tuvi import ai_luan_giai
    print(f"  {'ĐẠT ' if ai_luan_giai.khoa_api() else '----'} khóa Gemini trong "
          f"{ai_luan_giai.TEP_ENV}"
          f"{'' if ai_luan_giai.khoa_api() else ' (chưa có — phần AI sẽ báo 503)'}")
    print(f"{'Tất cả phép thử đều đạt.' if not hong else f'{hong} phép thử hỏng.'}")
    return 1 if hong else 0


def main() -> int:
    bao_dam_dau_ra()
    bat_utf8()   # console Windows mặc định cp1252, in tiếng Việt là vỡ
    print(f"[{TEN_APP}] tài nguyên: {thu_muc_tai_nguyen()} | ghi: {thu_muc_ghi()}")
    cong = cong_trong()
    bat_may_chu(cong)
    if not cho_may_chu(cong):
        print("Không bật được máy chủ nội bộ.")
        return 1

    if "--kiem-tra" in sys.argv:
        return kiem_tra(cong)

    try:
        import webview
    except ImportError:
        print("Chưa có pywebview; mở bằng trình duyệt mặc định thay thế.")
        import webbrowser
        webbrowser.open(f"http://127.0.0.1:{cong}")
        input("Nhấn Enter để dừng...")
        return 0

    webview.create_window(TEN_APP, f"http://127.0.0.1:{cong}",
                          width=1240, height=880, min_size=(900, 600))
    # Trên Windows, icon phải là .ico — đưa .png vào thì .NET ném
    # "Argument 'picture' must be a picture that can be used as a Icon" và app
    # chết ngay khi mở cửa sổ. gui=None: để pywebview tự chọn WebView2.
    icon = thu_muc_tai_nguyen() / "assets" / "icon.ico"
    webview.start(icon=str(icon) if icon.exists() else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
