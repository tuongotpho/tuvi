# -*- coding: utf-8 -*-
"""Luận giải lá số bằng mô hình ngôn ngữ Gemini, trên nền số liệu đã tính sẵn.

Cách làm: gói ``tuvi`` tính xong mọi con số (sao, cung, cách cục, đại hạn, năm
xem), rồi đưa **toàn bộ số liệu đó** cùng bộ quy tắc biên tập vào prompt; Gemini
chỉ làm việc viết văn. Mô hình không được tự an sao hay đoán ngày — mọi tên sao,
tên cung trong bài phải có trong dữ liệu gửi lên (``content/prompts/`` ghi rõ).

Khóa API lấy từ biến môi trường ``GEMINI_API_KEY`` hoặc tệp ``.env`` ở gốc kho
(không đưa vào git). Chỉ dùng thư viện chuẩn: gọi REST bằng ``urllib``.
Kết quả được cache theo nội dung prompt (bộ nhớ + ``build/cache_ai/``) để cùng
một lá số không tốn tiền gọi lại.
"""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from .kiem_tra import LoiDauVao
from .luan_giai import luan_giai_la_so

ROOT = Path(__file__).resolve().parent.parent
TEP_ENV = ROOT / ".env"
THU_MUC_CACHE = ROOT / "build" / "cache_ai"
TEP_PROMPT = ROOT / "content" / "prompts" / "luan_giai_la_so.md"

MODEL_MAC_DINH = "gemini-2.5-flash"
DIA_CHI_API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
THOI_GIAN_CHO = 90          # giây chờ Gemini trả lời
SO_TOKEN_TOI_DA = 4096

_cache_bo_nho: dict[str, str] = {}


class LoiGemini(RuntimeError):
    """Gọi Gemini thất bại; thông báo đủ rõ để hiện cho người dùng."""


# ----------------------------------------------------------------------------
# Khóa API
# ----------------------------------------------------------------------------
def nap_env(tep: Path | None = None) -> None:
    """Nạp KEY=VALUE từ tệp .env vào os.environ, không ghi đè biến đã có."""
    tep = tep or TEP_ENV
    if not tep.exists():
        return
    for dong in tep.read_text(encoding="utf-8").splitlines():
        dong = dong.strip()
        if not dong or dong.startswith("#") or "=" not in dong:
            continue
        k, v = dong.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def khoa_api() -> str | None:
    nap_env()
    return os.environ.get("GEMINI_API_KEY") or None


def model_mac_dinh() -> str:
    nap_env()
    return os.environ.get("GEMINI_MODEL") or MODEL_MAC_DINH


# ----------------------------------------------------------------------------
# Dựng prompt từ số liệu đã tính
# ----------------------------------------------------------------------------
def _tom_tat_la_so(ls: dict) -> dict:
    """Phiên bản gọn của lá số: đủ để viết, không thừa trường kỹ thuật."""
    cung = []
    for c in ls["cac_cung"]:
        cung.append({
            "cung": c["ten_cung"], "chi": f"{c['can']} {c['chi']}", "chu_ve": c["chu_ve"],
            "dai_han": c["dai_han"],
            "than": c["la_cung_than"], "tuan": bool(c.get("tuan")), "triet": bool(c.get("triet")),
            "chinh_tinh": [f"{s['ten']} ({s['dac_tinh']})" if s.get("dac_tinh") else s["ten"]
                           for s in c["sao"] if s["nhom"] == "Chính tinh"],
            "sao_khac": [s["ten"] for s in c["sao"] if s["nhom"] != "Chính tinh"],
        })
    am = ls["am_lich"]
    return {
        "am_lich": f"{am['ngay']}/{am['thang']}{' nhuận' if am.get('nhuan') else ''}/{am['nam']} giờ {am['gio']}",
        "nam_sinh_can_chi": ls["nam_sinh_can_chi"], "gioi_tinh": ls["gioi_tinh"],
        "menh_nap_am": ls["menh_nap_am"], "cuc": ls["cuc"], "am_duong": ls["am_duong_nam_sinh"],
        "cung_menh": ls["cung_menh"], "than_cu": ls["cung_than_tai"],
        "tu_hoa": ls["tu_hoa"], "tuan": ls.get("tuan"), "triet": ls.get("triet"),
        "cac_cung": cung,
    }


def _tom_tat_luan_giai(lg: dict) -> dict:
    nx = lg.get("nam_xem")
    return {
        "tong_quan": lg["tong_quan"],
        "cach_cuc": [{"ten": c["ten"], "tinh_chat": c["tinh_chat"], "luan_giai": c["luan_giai"]}
                     for c in lg["cach_cuc"]],
        "diem_cung": [{"cung": c["ten_cung"], "danh_gia": c["danh_gia"], "diem": c["diem"]}
                      for c in lg["cac_cung"]],
        "dai_han_hien_tai": lg["dai_han"]["hien_tai"],
        "nam_xem": {"nam": nx["nam_xem"], "can_chi": nx["nam_xem_can_chi"], "tuoi_mu": nx["tuoi_mu"],
                    "tieu_han": nx["tieu_han"], "dai_han": nx["dai_han"],
                    "luu_tu_hoa": nx["luu_tu_hoa"], "nhan_xet": nx["nhan_xet"]} if nx else None,
    }


def dung_prompt(ls: dict, nam_xem: int | None = None) -> str:
    """Prompt đầy đủ: quy tắc biên tập + số liệu lá số + luận giải máy đã tính."""
    lg = luan_giai_la_so(ls, nam_xem)
    tax = json.loads((ROOT / "content" / "taxonomy.json").read_text(encoding="utf-8"))
    huong_dan = TEP_PROMPT.read_text(encoding="utf-8")
    so_lieu = {"la_so": _tom_tat_la_so(ls), "luan_giai_may": _tom_tat_luan_giai(lg)}
    return (
        f"{huong_dan}\n\n"
        "## Quy tắc biên tập bắt buộc của kho dữ liệu\n"
        + "".join(f"- {q}\n" for q in tax["quy_tac_bien_tap"])
        + "- Chỉ dùng tên sao, tên cung, cách cục, đại hạn, tiểu hạn, sao lưu có trong SỐ LIỆU dưới đây. "
          "Không tự an thêm sao, không tự tính lại ngày tháng.\n"
        "- Nếu có mục `nam_xem`, thêm một phần \"Năm nay\" dựa trên tiểu hạn, đại hạn và sao lưu đã cho.\n"
        "- Viết bằng tiếng Việt, định dạng Markdown với tiêu đề cấp 2 (##) cho từng phần.\n\n"
        "## SỐ LIỆU (JSON, do gói tuvi tính, đã kiểm thử)\n```json\n"
        + json.dumps(so_lieu, ensure_ascii=False, indent=1)
        + "\n```\n"
    )


# ----------------------------------------------------------------------------
# Gọi Gemini
# ----------------------------------------------------------------------------
def _goi_gemini(prompt: str, model: str, khoa: str, thoi_gian_cho: int = THOI_GIAN_CHO) -> str:
    """POST lên generateContent, trả về văn bản. Tách riêng để test thay bằng bản giả."""
    than = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": SO_TOKEN_TOI_DA},
    }, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        DIA_CHI_API.format(model=model), data=than, method="POST",
        headers={"Content-Type": "application/json; charset=utf-8",
                 "x-goog-api-key": khoa})   # khóa đi trong header, không nằm trên URL/log
    try:
        with urllib.request.urlopen(req, timeout=thoi_gian_cho) as r:
            du_lieu = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        ma = e.code
        try:
            chi_tiet = json.loads(e.read().decode("utf-8")).get("error", {}).get("message", "")
        except Exception:  # noqa: BLE001
            chi_tiet = ""
        ly_do = {400: "yêu cầu không hợp lệ (khóa hoặc tên model sai?)",
                 401: "khóa API không được chấp nhận", 403: "khóa API bị từ chối",
                 404: f"không có model '{model}'", 429: "vượt hạn mức gọi, thử lại sau ít phút",
                 503: "dịch vụ Gemini đang quá tải"}.get(ma, f"HTTP {ma}")
        raise LoiGemini(f"Gemini từ chối: {ly_do}. {chi_tiet[:200]}".strip()) from None
    except urllib.error.URLError as e:
        raise LoiGemini(f"Không nối được tới Gemini: {e.reason}") from None
    except TimeoutError:
        raise LoiGemini(f"Gemini không trả lời trong {thoi_gian_cho} giây.") from None
    try:
        ung = du_lieu["candidates"][0]
        if ung.get("finishReason") == "SAFETY":
            raise LoiGemini("Gemini chặn nội dung vì bộ lọc an toàn; thử lại hoặc đổi năm xem.")
        return "".join(p.get("text", "") for p in ung["content"]["parts"]).strip()
    except (KeyError, IndexError, TypeError):
        raise LoiGemini("Gemini trả về định dạng lạ, không đọc được văn bản.") from None


def _doc_cache(ma: str) -> str | None:
    if ma in _cache_bo_nho:
        return _cache_bo_nho[ma]
    tep = THU_MUC_CACHE / f"{ma}.md"
    if tep.exists():
        van_ban = tep.read_text(encoding="utf-8")
        _cache_bo_nho[ma] = van_ban
        return van_ban
    return None


def _ghi_cache(ma: str, van_ban: str) -> None:
    _cache_bo_nho[ma] = van_ban
    try:
        THU_MUC_CACHE.mkdir(parents=True, exist_ok=True)
        (THU_MUC_CACHE / f"{ma}.md").write_text(van_ban, encoding="utf-8")
    except OSError:
        pass   # không ghi được đĩa thì vẫn có bản trong bộ nhớ


def luan_giai_ai(ls: dict, nam_xem: int | None = None, model: str | None = None,
                 dung_cache: bool = True) -> dict:
    """Bài luận giải do Gemini viết từ số liệu của lá số ``ls``.

    Trả về ``{"model", "van_ban", "tu_cache", "so_ky_tu_prompt"}``. Ném
    ``LoiDauVao`` khi chưa có khóa (để máy chủ trả 503 rõ ràng), ``LoiGemini``
    khi gọi thất bại.
    """
    khoa = khoa_api()
    if not khoa:
        raise LoiDauVao("Chưa cấu hình GEMINI_API_KEY (biến môi trường hoặc tệp .env ở gốc kho).")
    model = model or model_mac_dinh()
    prompt = dung_prompt(ls, nam_xem)
    ma = hashlib.sha256(f"{model}\n{prompt}".encode("utf-8")).hexdigest()[:24]
    if dung_cache:
        san = _doc_cache(ma)
        if san:
            return {"model": model, "van_ban": san, "tu_cache": True, "so_ky_tu_prompt": len(prompt)}
    van_ban = _goi_gemini(prompt, model, khoa)
    if not van_ban:
        raise LoiGemini("Gemini trả về văn bản rỗng.")
    _ghi_cache(ma, van_ban)
    return {"model": model, "van_ban": van_ban, "tu_cache": False, "so_ky_tu_prompt": len(prompt)}


__all__ = ["luan_giai_ai", "dung_prompt", "khoa_api", "model_mac_dinh", "LoiGemini",
           "MODEL_MAC_DINH"]
