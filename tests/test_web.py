# -*- coding: utf-8 -*-
"""Kiểm tra máy chủ web: đầu vào rác phải bị chặn với thông báo rõ, đầu vào đúng
phải trả 200, và không có đường leo thư mục ra ngoài web/static."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location("tuvi_web_server", ROOT / "web" / "server.py")
server = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(server)


class TestMayChuWeb(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.cong = cls.httpd.server_address[1]
        cls.luong = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.luong.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def goi(self, duong_dan: str):
        url = f"http://127.0.0.1:{self.cong}{duong_dan}"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def json(self, duong_dan: str):
        ma, body = self.goi(duong_dan)
        return ma, json.loads(body)

    # ---- đầu vào đúng ----
    def test_cac_api_tra_200(self):
        for p in ["/api/laso?ngay=20&thang=9&nam=1990&gio=14&gioi_tinh=nam",
                  "/api/laso?ngay=20&thang=9&nam=1990&canh=M%C3%B9i&gioi_tinh=nu",
                  "/api/luangiai?ngay=22&thang=8&nam=1987&gio=10&gioi_tinh=nam&nam_xem=2026",
                  "/api/han?nam_sinh=1987&nam_xem=2026&gioi_tinh=nam",
                  "/api/han?ngay_sinh=1990-01-15&nam_xem=2026&gioi_tinh=nam",
                  "/api/phongthuy?nam_sinh=1990&gioi_tinh=nam&huong=%C4%90%C3%B4ng%20Nam",
                  "/api/ngay?ngay=20&thang=9&nam=2026", "/api/ngay",
                  "/api/phitinh?nam=2026", "/api/sao?ten=T%E1%BB%AD%20vi", "/api/viec",
                  "/api/chonngay?nam_sinh=1987&tu_ngay=2026-10-10&den_ngay=2026-11-07&viec=dong_tho"]:
            ma, d = self.json(p)
            self.assertEqual(ma, 200, (p, d))

    def test_ngay_sinh_duong_truoc_tet_ra_nam_am_truoc(self):
        # 15/01/1990 dương còn là năm Kỷ Tỵ 1989 âm.
        ma, d = self.json("/api/han?ngay_sinh=1990-01-15&nam_xem=2026&gioi_tinh=nam")
        self.assertEqual(ma, 200)
        self.assertEqual(d["nam_sinh_am_lich"], 1989)
        self.assertEqual(d["tuoi_can_chi"], "Kỷ Tỵ")

    # ---- đầu vào rác: trước đây tất cả những dòng này đều được 200 ----
    def test_dau_vao_rac_bi_chan(self):
        rac = ["/api/laso?ngay=31&thang=2&nam=1990&gio=14&gioi_tinh=nam",
               "/api/laso?ngay=1&thang=1&nam=99999&gio=14&gioi_tinh=nam",
               "/api/laso?ngay=1&thang=1&nam=1700&gio=14&gioi_tinh=nam",
               "/api/laso?ngay=20&thang=9&nam=1990&gio=99&gioi_tinh=nam",
               "/api/laso?ngay=20&thang=9&nam=1990&gio=-5&gioi_tinh=nam",
               "/api/laso?ngay=20&thang=9&nam=1990&canh=xyz&gioi_tinh=nam",
               "/api/laso?ngay=20&thang=9&nam=1990&canh=99&gioi_tinh=nam",
               "/api/laso?ngay=20&thang=9&nam=1990&gio=14&gioi_tinh=%3Cscript%3E",
               "/api/luangiai?ngay=20&thang=9&nam=1990&gio=14&gioi_tinh=nam&nam_xem=-1",
               "/api/han?nam_sinh=abc&nam_xem=2026",
               "/api/han?nam_sinh=1990&nam_xem=2026&gioi_tinh=khac",
               "/api/han?nam_sinh=2030&nam_xem=2026&gioi_tinh=nam",
               "/api/phongthuy?nam_sinh=1990&gioi_tinh=nam&huong=Bac%20Cuc",
               "/api/ngay?ngay=0&thang=0&nam=0",
               "/api/ngay?ngay=29&thang=2&nam=2023",
               "/api/chonngay?nam_sinh=1987&tu_ngay=2026-01-01&den_ngay=2027-12-31",
               "/api/chonngay?nam_sinh=1987&tu_ngay=2026-01-01&den_ngay=2026-03-01&so_luong=999999",
               "/api/chonngay?nam_sinh=1987&tu_ngay=2026-13-45",
               "/api/chonngay?nam_sinh=1987&tu_ngay=2026-01-01&den_ngay=2026-02-01&viec=khong_co",
               "/api/sao?ten=../../etc/passwd"]
        for p in rac:
            ma, d = self.json(p)
            self.assertEqual(ma, 400, p)
            self.assertIn("loi", d, p)
            self.assertNotIn("Traceback", d["loi"])

    def test_thong_bao_loi_tieng_viet_cu_the(self):
        ma, d = self.json("/api/laso?ngay=31&thang=2&nam=1990&gio=14&gioi_tinh=nam")
        self.assertIn("không có thật", d["loi"])
        ma, d = self.json("/api/laso?ngay=20&thang=9&nam=1990&gio=99&gioi_tinh=nam")
        self.assertIn("Giờ", d["loi"])
        ma, d = self.json("/api/han?nam_sinh=1990&nam_xem=2026&gioi_tinh=khac")
        self.assertIn("Giới tính", d["loi"])

    def test_khong_leo_thu_muc(self):
        for p in ["/../server.py", "/static/../server.py", "/%2e%2e/server.py", "/../tuvi/store.py"]:
            ma, body = self.goi(p)
            self.assertEqual(ma, 404, p)
            self.assertNotIn(b"def do_GET", body)

    def test_ai_khong_co_khoa_tra_503(self):
        from tuvi import ai_luan_giai
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": ""}),              mock.patch.object(ai_luan_giai, "TEP_ENV", Path("/khong/co/.env")):
            ma, d = self.json("/api/ai-luangiai?ngay=20&thang=9&nam=1990&gio=14&gioi_tinh=nam")
        self.assertEqual(ma, 503)
        self.assertIn("GEMINI_API_KEY", d["loi"])

    def test_ai_goi_duoc_va_chan_goi_don_dap(self):
        from tuvi import ai_luan_giai
        ai_luan_giai._cache_bo_nho.clear()
        server._ai_lan_cuoi.clear()
        bai = "## Bài giả" + chr(10) + "Nội dung."
        gia = lambda prompt, model, khoa, thoi_gian_cho=90: bai  # noqa: E731
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "KHOA-THU"}),              mock.patch.object(ai_luan_giai, "_goi_gemini", gia),              mock.patch.object(ai_luan_giai, "THU_MUC_CACHE", Path(os.devnull)):
            ma, d = self.json("/api/ai-luangiai?ngay=20&thang=9&nam=1990&gio=14&gioi_tinh=nam&nam_xem=2026")
            self.assertEqual(ma, 200, d)
            self.assertEqual(d["van_ban"], bai)
            self.assertFalse(d["tu_cache"])
            # gọi ngay lần hai từ cùng IP -> 429
            ma2, d2 = self.json("/api/ai-luangiai?ngay=20&thang=9&nam=1990&gio=14&gioi_tinh=nam&nam_xem=2026")
            self.assertEqual(ma2, 429)
        ai_luan_giai._cache_bo_nho.clear()
        server._ai_lan_cuoi.clear()

    def test_header_an_toan(self):
        url = f"http://127.0.0.1:{self.cong}/api/viec"
        with urllib.request.urlopen(url, timeout=30) as r:
            self.assertEqual(r.headers["X-Content-Type-Options"], "nosniff")
            self.assertEqual(r.headers["Cache-Control"], "no-store")


if __name__ == "__main__":
    unittest.main()
