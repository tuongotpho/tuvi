# -*- coding: utf-8 -*-
"""Tái tạo tests/fixtures/lasotuvi_mau.json từ gói doanguyen/lasotuvi (MIT).

Bộ mẫu trong kho là kết quả của chính script này với lasotuvi 0.1.2 — ai nghi
ngờ fixture đều có thể sinh lại và so bằng ``git diff``. Gói lasotuvi kéo theo
typed-ast (không cài được trên Python mới) nên cài bỏ dependency::

    pip install --no-deps --target build/lasotuvi lasotuvi==0.1.2
    python scripts/sinh_fixture_lasotuvi.py            # ghi lại fixture
    python scripts/sinh_fixture_lasotuvi.py --kiem-tra # chỉ so, không ghi

Đầu vào lấy đúng 60 lá số đang có trong fixture (âm lịch, giờ theo chi, giới
tính), nên fixture cũ chính là danh sách ca kiểm thử. Tám sao khác trường phái
và cặp Thai — Dưỡng bị loại như ghi trong ``_ghi_chu`` của fixture.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "build" / "lasotuvi"))

from tuvi.canchi import DIA_CHI  # noqa: E402
from tuvi.console import bat_utf8  # noqa: E402

TEP = ROOT / "tests" / "fixtures" / "lasotuvi_mau.json"
# lasotuvi: id 38 tên "Quan phù" nhưng là Quan Phủ vòng Lộc Tồn; "Bác sỹ" viết khác.
DOI_TEN = {38: "quan phủ"}
CHINH_TA = {"bác sỹ": "bác sĩ"}
BO_QUA = {"thiên khôi", "thiên việt", "hóa khoa", "hóa kỵ", "thiên giải", "phá toái",
          "hỏa tinh", "linh tinh", "thai", "dưỡng"}


def lap_bang_lasotuvi(d: int, m: int, y: int, gio: str, gioi_tinh: str) -> dict:
    from lasotuvi.App import lapDiaBan
    from lasotuvi.DiaBan import diaBan
    db = lapDiaBan(diaBan, d, m, y, DIA_CHI.index(gio) + 1,
                   1 if gioi_tinh == "nam" else -1, False, 7)
    sao: dict[str, str] = {}
    tuan, triet = [], []
    for c in db.thapNhiCung[1:]:
        for s in c.cungSao:
            ten = DOI_TEN.get(s["saoID"], s["saoTen"].lower())
            ten = CHINH_TA.get(ten, ten)
            if ten not in BO_QUA:
                sao[ten] = c.cungTen
        if getattr(c, "tuanTrung", False):
            tuan.append(c.cungTen)
        if getattr(c, "trietLo", False):
            triet.append(c.cungTen)
    return {"am_lich": [d, m, y], "gio": gio, "gioi_tinh": gioi_tinh,
            "tuan": tuan, "triet": triet, "sao": dict(sorted(sao.items()))}


def main() -> int:
    bat_utf8()
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--kiem-tra", action="store_true", help="so với fixture hiện có, không ghi")
    a = p.parse_args()
    if importlib.util.find_spec("lasotuvi") is None:
        print("Chưa có gói lasotuvi. Cài: pip install --no-deps --target build/lasotuvi lasotuvi==0.1.2",
              file=sys.stderr)
        return 2
    cu = json.loads(TEP.read_text(encoding="utf-8"))
    moi = {"_ghi_chu": cu["_ghi_chu"], "so_sao_moi_la_so": cu["so_sao_moi_la_so"],
           "la_so": [lap_bang_lasotuvi(*m["am_lich"], m["gio"], m["gioi_tinh"]) for m in cu["la_so"]]}
    so_sao = {len(m["sao"]) for m in moi["la_so"]}
    if so_sao != {cu["so_sao_moi_la_so"]}:
        print(f"Số sao mỗi lá số không đồng nhất: {so_sao}", file=sys.stderr)
        return 1
    lech = sum(1 for a_, b in zip(cu["la_so"], moi["la_so"])
               if a_["sao"] != b["sao"] or set(a_["tuan"]) != set(b["tuan"]) or set(a_["triet"]) != set(b["triet"]))
    print(f"{len(moi['la_so'])} lá số × {cu['so_sao_moi_la_so']} sao; lệch so với fixture hiện có: {lech} lá số")
    if a.kiem_tra:
        return 1 if lech else 0
    TEP.write_text(json.dumps(moi, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"Đã ghi {TEP.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
