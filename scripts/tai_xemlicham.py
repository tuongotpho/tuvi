# -*- coding: utf-8 -*-
"""Tải trang xemlicham.com cho một khoảng ngày, đọc ra các mục xem ngày, ghi fixture.

Dùng làm nguồn đối chiếu thứ nhất (lịch vạn niên tiếng Việt) cho
tests/test_xem_ngay.py. Trang đã tải được lưu vào thư mục đệm nên chạy lại
không tải lại.

Chạy:  python scripts/tai_xemlicham.py 2025-01-01 2026-12-31 <thư mục đệm>
Ghi:   tests/fixtures/xemlicham_2025_2026.json.gz

Trang của xemlicham có lỗi: một số ngày phần trên và phần dưới trang là của hai
ngày khác nhau (can chi không khớp). Những ngày đó được ghi vào "trang_hong" và
bỏ khỏi phép đối chiếu.
"""
from __future__ import annotations

import gzip
import html
import json
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
RA = GOC / "tests" / "fixtures" / "xemlicham_2025_2026.json.gz"


def tai(d: date, dem: Path) -> None:
    f = dem / f"{d.isoformat()}.txt"
    if f.exists() and f.stat().st_size > 2000:
        return
    url = f"https://www.xemlicham.com/am-lich/nam/{d.year}/thang/{d.month}/ngay/{d.day}"
    for lan in range(4):
        try:
            raw = urllib.request.urlopen(urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8", "replace")
            break
        except OSError:
            time.sleep(3 * (lan + 1))
    else:
        raise SystemExit(f"Không tải được {url}")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    t = html.unescape(re.sub(r"<br\s*/?>", "\n", t))
    t = re.sub(r"<[^>]+>", "\n", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    a = t.find("CHI TIẾT ÂM DƯƠNG LỊCH")
    i = t.find("XEM TỐT XẤU NGÀY")
    f.write_text(t[a:t.find("MÀU ĐỎ", a)] + "\n=====\n" + t[i:t.find("TIỆN ÍCH ONLINE", i)],
                 encoding="utf-8")


def gon(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def doan(t: str, dau: str, cuoi: list[str]) -> str:
    a = t.find(dau)
    if a < 0:
        return ""
    a += len(dau)
    b = min([x for x in (t.find(c, a) for c in cuoi) if x >= 0] or [len(t)])
    return t[a:b]


def doc(t: str) -> dict:
    m = re.search(r"Tháng (\d+)(?: \(nhuận\))? Năm (\d+) \((\S+ \S+)\)\n\d+\n(\d+)\nNgày:\s*\n(\S+ \S+)\n, Tháng:\s*\n(\S+ \S+)", t)
    r = {"am": [int(m[4]), int(m[1]), int(m[2]), "nhuận" in t[:t.find("Ngày:")].lower()],
         "cc": m[5], "thang_cc": m[6]}
    r["tiet"] = gon(re.search(r"Tiết khí:\s*\n([^\n]+)", t)[1])
    r["gio_hd"] = re.findall(r"(\S+) \(\d+:00", doan(t, "Giờ Hoàng Đạo\n", ["Giờ Hắc Đạo"]))
    r["ngay_ky"] = [gon(x) for x in re.findall(r"-\s*\n([^\n:]+)\n?:", doan(t, "Các Ngày Kỵ", ["Ngũ Hành"]))]
    nh = gon(doan(t, "Ngũ Hành\n", ["Bành Tổ"]))
    r["ngu_hanh_cc"] = (re.match(r"Ngày: (\S+ \S+)", nh) or [None, None])[1]
    r["ngu_hanh"] = re.search(r"tức (Chi sinh Can|Can sinh Chi|Can khắc Chi|Chi khắc Can|Can Chi tương đồng)", nh)[1]
    r["quan_he_chi"] = (re.search(r"- Ngày \S+ (lục hợp.*)$", nh) or [None, None])[1]
    r["banh_to"] = re.findall(r"“([^”]+)”", doan(t, "Bành Tổ Bách Kỵ Nhật", ["Khổng Minh"]))
    r["khong_minh"] = gon(re.search(r"Ngày:\s*\n([^\n]+)\n", doan(t, "Khổng Minh Lục Diệu", ["Nhị Thập Bát Tú"]))[1])
    r["tu"] = re.search(r"Tên sao\s*\n?:\s*Sao (\S+)", t)[1]
    r["truc"] = re.search(r"Thập Nhị Kiến Trừ\s*\n?Trực (\S+)", t)[1]
    sao = doan(t, "Ngọc Hạp Thông Thư", ["Hướng xuất hành"])
    r["sao_tot"] = [gon(x) for x in re.findall(r"-\s*([^:\n]+):", doan(sao, "Sao tốt", ["Sao xấu"]))]
    r["sao_xau"] = [gon(x) for x in re.findall(r"-\s*([^:\n]+):", doan(sao, "Sao xấu", ["\0"]))]
    hx = doan(t, "Hướng xuất hành", ["Giờ xuất hành"])
    r["hy_than"] = (re.search(r"hướng ([^'.]+?) để đón 'Hỷ Thần'", hx) or [None, None])[1]
    r["tai_than"] = (re.search(r"hướng ([^'.]+?) để đón 'Tài Thần'", hx) or [None, None])[1]
    r["hac_than"] = (re.search(r"hướng ([^'.]+?) gặp Hạc Thần", hx) or [None, None])[1]
    return r


def main() -> None:
    dau, cuoi, dem = date.fromisoformat(sys.argv[1]), date.fromisoformat(sys.argv[2]), Path(sys.argv[3])
    dem.mkdir(parents=True, exist_ok=True)
    ngay = [dau + timedelta(n) for n in range((cuoi - dau).days + 1)]
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda d: tai(d, dem), ngay))
    ra, hong = {}, []
    for d in ngay:
        r = doc((dem / f"{d.isoformat()}.txt").read_text(encoding="utf-8"))
        if r.pop("ngu_hanh_cc") != r["cc"]:
            hong.append(d.isoformat())
        ra[d.isoformat()] = r
    RA.write_bytes(gzip.compress(json.dumps(
        {"nguon": "https://www.xemlicham.com (tải " + date.today().isoformat() + ")",
         "trang_hong": hong, "ngay": ra}, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0))
    print(f"{len(ra)} ngày, {len(hong)} trang tự mâu thuẫn: {hong}")


if __name__ == "__main__":
    main()
