# -*- coding: utf-8 -*-
"""Kiểm phần đường dẫn dùng khi đóng gói .exe.

Chỗ này không có bài kiểm thì lỗi chỉ lộ ra sau khi dựng xong .exe và bấm chạy
— rất tốn công. Ở đây giả lập chế độ đóng gói bằng cách đặt sys.frozen và
sys._MEIPASS, không cần dựng thật.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tuvi import duong_dan  # noqa: E402

GOC = Path(__file__).resolve().parent.parent


class TestDuongDan(unittest.TestCase):
    def test_chay_tu_ma_nguon(self):
        self.assertFalse(duong_dan.dang_dong_goi())
        self.assertEqual(duong_dan.thu_muc_tai_nguyen(), GOC)
        self.assertEqual(duong_dan.thu_muc_ghi(), GOC)
        self.assertTrue((duong_dan.thu_muc_tai_nguyen() / "data").is_dir())

    def test_khi_dong_goi_doc_va_ghi_tach_doi(self):
        # Tài nguyên đọc từ thư mục giải nén tạm, nhưng ghi phải ra cạnh .exe:
        # thư mục tạm bị xóa khi thoát, lại hay nằm trong Program Files (chặn ghi).
        #
        # Dùng thư mục tạm thật chứ đừng viết "D:/App": trên Linux đó không phải
        # đường dẫn tuyệt đối nên .resolve() nối nó vào thư mục hiện hành, máy
        # Windows xanh mà CI đỏ — đã dính một lần.
        with tempfile.TemporaryDirectory() as goc_tam:
            tam = Path(goc_tam) / "_MEI123"
            canh_exe = Path(goc_tam) / "Tu-Vi"
            tam.mkdir()
            canh_exe.mkdir()
            self._kiem_tach_doi(tam, canh_exe)

    def _kiem_tach_doi(self, tam: Path, canh_exe: Path) -> None:
        with mock.patch.object(sys, "frozen", True, create=True), \
             mock.patch.object(sys, "_MEIPASS", str(tam), create=True), \
             mock.patch.object(sys, "executable", str(canh_exe / "Tu-Vi.exe")):
            self.assertTrue(duong_dan.dang_dong_goi())
            self.assertEqual(duong_dan.thu_muc_tai_nguyen(), tam)
            self.assertEqual(duong_dan.thu_muc_ghi(), canh_exe)

    def test_tai_nguyen_can_dong_goi_deu_co_that(self):
        # Danh sách này phải khớp với datas trong tuvi.spec.
        for p in ("data", "web/static", "content", "assets/icon.ico", "assets/icon.png"):
            self.assertTrue((GOC / p).exists(), f"thiếu {p} — tuvi.spec sẽ dựng ra bản hỏng")

    def test_spec_khong_goi_phan_video(self):
        # Playwright + ffmpeg nặng vài trăm MB; cố ý để ngoài gói.
        spec = (GOC / "tuvi.spec").read_text(encoding="utf-8")
        for goi in ("playwright", "edge_tts", "imageio_ffmpeg"):
            self.assertIn(f'"{goi}"', spec)


class TestAppDeBan(unittest.TestCase):
    def test_may_chu_chi_nghe_localhost(self):
        # App để bàn không được mở cổng ra mạng LAN: ngày giờ sinh là dữ liệu cá nhân.
        ma = (GOC / "app.py").read_text(encoding="utf-8")
        self.assertIn('ThreadingHTTPServer(("127.0.0.1", cong), Handler)', ma)

    def test_icon_cho_cua_so_phai_la_ico(self):
        # pywebview trên Windows ném lỗi .NET nếu đưa .png; đã dính một lần.
        ma = (GOC / "app.py").read_text(encoding="utf-8")
        self.assertIn('"assets" / "icon.ico"', ma)
        self.assertNotIn('webview.start(icon=str(thu_muc_tai_nguyen() / "assets" / "icon.png")', ma)


if __name__ == "__main__":
    unittest.main()
