# -*- coding: utf-8 -*-
"""Tải 120 lời Cao Ly Đầu Hình từ hai trang tra cứu công khai rồi đối chiếu.

Cao Ly Đầu Hình: "Nam dụng Can, Nữ dụng Chi" — can năm sinh của chồng phối
với chi năm sinh của vợ, 10 × 12 = 120 cặp. Mỗi cặp là một đoạn lời xưa (văn
xuôi + thơ). Kho KHÔNG tự viết lại lời; chỉ chép nguyên văn và ghi nguồn.

Nguồn chính: xemtuong.net. Nguồn đối chiếu: giadinh.kabala.vn.
Trang kabala ghi rõ cặp can–chi nó đang tra, nên kịch bản đọc cặp từ chính
trang trả về chứ không suy từ năm (kabala có trang trả nhầm cặp — xem SOURCES.md).

Chạy:  python scripts/tai_cao_ly_dau_hinh.py
Ghi:   data/hop_tuoi/cao_ly_dau_hinh.json
"""
from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))
from tuvi.canchi import DIA_CHI, THIEN_CAN, can_chi_nam  # noqa: E402

RA = GOC / "data" / "hop_tuoi" / "cao_ly_dau_hinh.json"
MAU = re.compile(r"người nam có can là\s*(\S+)\s*nếu lấy người nữ có chi là\s*(\S+)\s*:"
                 r"\s*❤?(.*?)Xem chi tiết tuổi vợ chồng", re.S)


def _doc(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for lan in range(3):   # hai trang này hay trả chậm, thử lại vài lần
        try:
            raw = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
            break
        except OSError:
            if lan == 2:
                raise
            time.sleep(3)
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    t = html.unescape(re.sub(r"<br\s*/?>", "\n", t))
    return re.sub(r"<[^>]+>", " ", t)


def _tach(t: str) -> tuple[str, str, str]:
    m = MAU.search(t)
    if not m:
        raise ValueError("Không tìm thấy đoạn Cao Ly trong trang")
    return m.group(1), m.group(2), m.group(3)


def lam_sach(s: str) -> str:
    """Bỏ khoảng trắng thừa; nối dòng văn xuôi bị trang cắt ngang giữa câu
    (dòng mở đầu bằng chữ thường là phần tiếp của dòng trên)."""
    dong: list[str] = []
    for d in (x.strip() for x in s.replace("❤", "").splitlines()):
        if not d:
            continue
        if dong and d[0].islower():
            dong[-1] += " " + d
        else:
            dong.append(d)
    return "\n".join(re.sub(r"\s+", " ", d) for d in dong)


def _nam(can: str | None = None, chi: str | None = None) -> int:
    for y in range(1984, 2044):
        cc = can_chi_nam(y)
        if (can is None or cc.can == can) and (chi is None or cc.chi == chi):
            return y
    raise ValueError(can or chi)


def tai_xemtuong(can: str, chi: str) -> str:
    url = ("https://xemtuong.net/caolydauhinh/index.php?day=15&month=6"
           f"&year={_nam(can=can)}&day2=15&month2=6&year2={_nam(chi=chi)}")
    c, ch, loi = _tach(_doc(url))
    if (c, ch) != (can, chi):
        raise ValueError(f"xemtuong trả {c}–{ch}, cần {can}–{chi}")
    time.sleep(0.5)
    return lam_sach(loi)


def tai_kabala(can: str, chi: str) -> tuple[str, str, str]:
    url = f"https://giadinh.kabala.vn/cao-ly-dau-hinh-{_nam(can=can)}-{_nam(chi=chi)}.html"
    c, ch, loi = _tach(_doc(url))
    return c, ch, lam_sach(loi)


def main() -> None:
    cap = [(c, ch) for c in THIEN_CAN for ch in DIA_CHI]
    xt = {k: tai_xemtuong(*k) for k in cap}
    with ThreadPoolExecutor(4) as ex:
        kb = {(c, ch): loi for c, ch, loi in ex.map(lambda k: tai_kabala(*k), cap)}

    ban_ghi = []
    for c, ch in cap:
        if (c, ch) in kb:
            # So theo chữ: hai trang chỉ khác nhau chỗ xuống dòng.
            if re.sub(r"[\s*]+", " ", kb[(c, ch)]) != re.sub(r"[\s*]+", " ", xt[(c, ch)]):
                raise SystemExit(f"Hai nguồn lệch nhau ở cặp {c}–{ch}")
            doi_chieu = "khớp kabala"
        else:
            doi_chieu = "chỉ có xemtuong (trang kabala trả nhầm cặp)"
        ban_ghi.append({"can_chong": c, "chi_vo": ch, "loi": xt[(c, ch)],
                        "doi_chieu": doi_chieu})

    RA.parent.mkdir(parents=True, exist_ok=True)
    RA.write_text(json.dumps({
        "mo_ta": "Cao Ly Đầu Hình — xem duyên vợ chồng theo lối 'Nam dụng Can, Nữ "
                 "dụng Chi': can năm sinh của chồng phối với chi năm sinh của vợ. "
                 "Lời xưa chép nguyên văn, kho không viết lại và không tự chấm điểm.",
        "nguon": [
            "https://xemtuong.net/caolydauhinh/ (nguồn chép)",
            "https://giadinh.kabala.vn/vochong/caolydauhinh/ (nguồn đối chiếu)",
        ],
        "cach_tao": "scripts/tai_cao_ly_dau_hinh.py",
        "cap": ban_ghi,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    khop = sum(b["doi_chieu"] == "khớp kabala" for b in ban_ghi)
    print(f"{len(ban_ghi)} cặp; {khop} cặp khớp nguyên văn cả hai nguồn")


if __name__ == "__main__":
    main()
