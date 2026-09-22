# -*- coding: utf-8 -*-
"""Luận giải bằng Gemini — kiểm bằng Gemini giả lập, không gọi mạng, không cần khóa thật."""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tuvi import ai_luan_giai, la_so  # noqa: E402
from tuvi.kiem_tra import LoiDauVao  # noqa: E402

LS = la_so.lap_la_so(22, 8, 1987, 12, gioi_tinh="nam")   # Mệnh Dần, Thất Sát
BAI_GIA = ("## Tổng quan mệnh cục\nMệnh tại Dần có Thất Sát...\n\n## Năm nay\nTiểu hạn tại Phụ Mẫu.\n\n"
           "Tử vi là tri thức văn hóa dân gian, dùng để tham khảo và tự soi chiếu, "
           "không thay thế cho nỗ lực và quyết định của chính bạn.")


class GeminiGia:
    """Thay cho _goi_gemini: đếm số lần gọi, trả bài cố định, lưu prompt nhận được."""

    def __init__(self):
        self.so_lan = 0
        self.prompt = ""

    def __call__(self, prompt, model, khoa, thoi_gian_cho=90):
        self.so_lan += 1
        self.prompt = prompt
        assert khoa == "KHOA-THU"
        return BAI_GIA


class TestPrompt(unittest.TestCase):
    def test_prompt_chua_so_lieu_that_va_quy_tac(self):
        p = ai_luan_giai.dung_prompt(LS, 2026)
        # số liệu của lá số
        for tu in ("Thất Sát", "Đinh Mão", "Kim 4 cục", "Lưu Hóa Kỵ", "Sát Phá Tham", "Thất Sát triều đẩu"):
            self.assertIn(tu, p, tu)
        # quy tắc biên tập và ràng buộc kết bài
        self.assertIn("Không bịa thêm sao", p)
        self.assertIn("không dọa nạt", p)
        self.assertIn("không thay thế cho nỗ lực", p)
        self.assertIn("Không tự an thêm sao", p)
        # có mục năm xem; bỏ năm xem thì không
        self.assertIn('"nam_xem": {', p)
        self.assertIn('"nam_xem": null', ai_luan_giai.dung_prompt(LS, None))

    def test_prompt_khong_qua_dai(self):
        self.assertLess(len(ai_luan_giai.dung_prompt(LS, 2026)), 25_000)


class TestGoiGemini(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        ai_luan_giai._cache_bo_nho.clear()
        self.patches = [
            mock.patch.object(ai_luan_giai, "THU_MUC_CACHE", Path(self.tmp.name)),
            mock.patch.object(ai_luan_giai, "TEP_ENV", Path(self.tmp.name) / "khong_co.env"),
            mock.patch.dict(os.environ, {"GEMINI_API_KEY": "KHOA-THU"}, clear=False),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        ai_luan_giai._cache_bo_nho.clear()
        self.tmp.cleanup()

    def test_goi_va_cache(self):
        gia = GeminiGia()
        with mock.patch.object(ai_luan_giai, "_goi_gemini", gia):
            kq1 = ai_luan_giai.luan_giai_ai(LS, 2026)
            kq2 = ai_luan_giai.luan_giai_ai(LS, 2026)
            kq3 = ai_luan_giai.luan_giai_ai(LS, 2027)
        self.assertEqual(kq1["van_ban"], BAI_GIA)
        self.assertFalse(kq1["tu_cache"])
        self.assertTrue(kq2["tu_cache"])
        self.assertEqual(gia.so_lan, 2, "cùng lá số cùng năm không được gọi lại; đổi năm thì gọi")
        self.assertFalse(kq3["tu_cache"])
        self.assertEqual(kq1["model"], ai_luan_giai.MODEL_MAC_DINH)
        # cache đĩa có tệp
        self.assertEqual(len(list(Path(self.tmp.name).glob("*.md"))), 2)

    def test_khong_co_khoa(self):
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with self.assertRaises(LoiDauVao):
                ai_luan_giai.luan_giai_ai(LS, 2026)

    def test_nap_env_khong_ghi_de(self):
        tep = Path(self.tmp.name) / ".env"
        tep.write_text('GEMINI_API_KEY="TU-TEP"\nGEMINI_MODEL=gemini-thu\n# ghi chú\n', encoding="utf-8")
        with mock.patch.object(ai_luan_giai, "TEP_ENV", tep), \
             mock.patch.dict(os.environ, {"GEMINI_MODEL": ""}, clear=False):
            os.environ.pop("GEMINI_MODEL")
            self.assertEqual(ai_luan_giai.khoa_api(), "KHOA-THU")   # biến môi trường thắng .env
            self.assertEqual(ai_luan_giai.model_mac_dinh(), "gemini-thu")

    def test_doc_loi_http_thanh_cau_tieng_viet(self):
        def urlopen_loi(req, timeout=0):
            raise urllib.error.HTTPError(req.full_url, 429, "Too Many Requests", {},
                                         io.BytesIO(json.dumps({"error": {"message": "quota"}}).encode()))
        with mock.patch.object(ai_luan_giai.urllib.request, "urlopen", urlopen_loi):
            with self.assertRaises(ai_luan_giai.LoiGemini) as cm:
                ai_luan_giai._goi_gemini("x", "m", "k")
        self.assertIn("hạn mức", str(cm.exception))

    def test_doc_phan_hoi_that(self):
        phan_hoi = {"candidates": [{"content": {"parts": [{"text": "Phần một. "}, {"text": "Phần hai."}]},
                                    "finishReason": "STOP"}]}

        class Resp(io.BytesIO):
            def __enter__(self): return self
            def __exit__(self, *a): return False
        def urlopen_ok(req, timeout=0):
            # khóa phải đi trong header, không trên URL
            assert req.get_header("X-goog-api-key") == "k" and "key=" not in req.full_url
            return Resp(json.dumps(phan_hoi).encode())
        with mock.patch.object(ai_luan_giai.urllib.request, "urlopen", urlopen_ok):
            self.assertEqual(ai_luan_giai._goi_gemini("x", "m", "k"), "Phần một. Phần hai.")


if __name__ == "__main__":
    unittest.main()
