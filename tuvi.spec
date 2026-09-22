# -*- mode: python ; coding: utf-8 -*-
"""Đóng gói bộ tra cứu tử vi thành .exe chạy được không cần cài Python.

Dựng:  python -m PyInstaller tuvi.spec --noconfirm   (hoặc bấm build.bat)

Engine tử vi chỉ dùng thư viện chuẩn nên gói rất gọn; phần nặng duy nhất là
pywebview + pythonnet để có cửa sổ riêng. Phần dựng video (playwright, ffmpeg,
edge-tts) CỐ Ý không gói: nó nặng vài trăm MB và vẫn chạy tốt từ mã nguồn.
"""
from PyInstaller.utils.hooks import collect_all

# pywebview nạp backend (WebView2) động lúc chạy nên PyInstaller không tự thấy.
wv_datas, wv_binaries, wv_hidden = collect_all("webview")
clr_datas, clr_binaries, clr_hidden = collect_all("clr_loader")

a = Analysis(
    ["app.py"],
    pathex=["."],
    binaries=wv_binaries + clr_binaries,
    # Giữ nguyên cấu trúc thư mục: tuvi/duong_dan.py trỏ vào sys._MEIPASS,
    # nên data/ và web/static/ phải nằm đúng chỗ như trong kho.
    datas=[("data", "data"), ("web/static", "web/static"),
           ("content", "content"),
           ("assets/icon.ico", "assets"), ("assets/icon.png", "assets")]
          + wv_datas + clr_datas,
    hiddenimports=wv_hidden + clr_hidden + ["clr"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # Không dùng đến, loại cho nhẹ. video/ không nằm trong gói nên
        # playwright, edge_tts, imageio_ffmpeg cũng không bị kéo theo.
        "tkinter", "matplotlib", "numpy", "pandas", "pytest", "PIL",
        "playwright", "edge_tts", "imageio_ffmpeg", "aiohttp",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

# Dạng thư mục (onedir): mở gần như tức thì, không phải giải nén mỗi lần chạy,
# và ít bị phần mềm diệt virus báo nhầm hơn bản một tệp.
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="Tu-Vi",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # console=False: không hiện cửa sổ đen. Mọi thứ in ra đi vào tuvi.log
    # cạnh tệp .exe (xem bao_dam_dau_ra trong app.py).
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.ico",
)

coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False,
               upx_exclude=[], name="Tu-Vi")
