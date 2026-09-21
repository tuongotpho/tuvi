#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dựng video dọc cho TikTok từ dữ liệu thật của gói ``tuvi``.

    python video/lam_video.py han 1987 2026 --thang-am 9 --gioi-tinh nam
    python video/lam_video.py ngay 20/09/2026
    python video/lam_video.py --chi-kich-ban han 1987 2026 --thang-am 9

Luồng: dựng danh sách cảnh từ engine -> đổ vào ``mau_video.html`` -> Playwright
quay màn hình 1080x1920 -> ffmpeg xuất MP4 dọc.

Hai phần phụ thuộc chỉ cần khi thật sự xuất video, phần dựng kịch bản thì không:
Playwright để quay và ffmpeg để chuyển mã. Không có chúng, lệnh vẫn chạy và trả
về kịch bản kèm caption, chỉ bỏ bước xuất tệp.

Video xuất ra KHÔNG CÓ TIẾNG: môi trường này không có bộ đọc giọng nói. Lời thoại
nằm trong tệp kịch bản kèm mốc thời gian để lồng tiếng hoặc chèn nhạc trên app.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tuvi.amlich import lunar_to_solar  # noqa: E402
from tuvi.canchi import can_chi_nam, can_chi_thang, quan_he_chi  # noqa: E402
from tuvi.chon_ngay import chon_ngay  # noqa: E402
from tuvi.han import ho_so_han  # noqa: E402
from tuvi.ngay_gio import xem_ngay  # noqa: E402
from tuvi.phong_thuy import cung_phi, phi_tinh_nam  # noqa: E402

MAU = Path(__file__).resolve().parent / "mau_video.html"
RONG, CAO = 1080, 1920

# Tốc độ đọc tiếng Việt khoảng 2,6 âm tiết mỗi giây khi dẫn chuyện.
AM_TIET_MOI_GIAY = 2.6
GIAY_TOI_THIEU, GIAY_TOI_DA = 2.6, 6.5


def _giay(loi_thoai: str) -> float:
    n = len(loi_thoai.split())
    return round(min(GIAY_TOI_DA, max(GIAY_TOI_THIEU, n / AM_TIET_MOI_GIAY + 0.9)), 1)


def _canh(loi_thoai: str, **kw) -> dict:
    return {**kw, "loi_thoai": loi_thoai, "giay": kw.get("giay") or _giay(loi_thoai)}


# --------------------------------------------------------------------------
# Kịch bản: hạn của một tuổi trong một năm, có thể soi riêng một tháng âm lịch
# --------------------------------------------------------------------------
def kich_ban_han(nam_sinh: int, nam_xem: int, gioi_tinh: str = "nam",
                 thang_am: int | None = None) -> dict:
    h = ho_so_han(nam_sinh, nam_xem, gioi_tinh)
    s, tt, tue = h["sao_han"], h["tam_tai"], h["thai_tue"]
    tuoi = h["tuoi_can_chi"]
    chi_tuoi = can_chi_nam(nam_sinh).chi
    gt_chu = "Nam" if gioi_tinh.startswith("nam") else "Nữ"
    canh = []

    canh.append(_canh(
        f"{gt_chu} sinh năm {nam_sinh}, năm {h['nam_xem_can_chi']} này có gì phải giữ.",
        lon=True, nhan=f"{gt_chu} {nam_sinh}",
        tieu_de=f"Tuổi *{tuoi}*\nnăm {h['nam_xem_can_chi']}",
        phu=f"Mệnh {h['nap_am']} · {h['tuoi_mu']} tuổi mụ",
        chan="Tra cứu tử vi"))

    canh.append(_canh(
        f"Sao chiếu mệnh năm nay là {s['sao']}. {s['y_nghia']}",
        nhan="Sao chiếu mệnh", tieu_de=f"*{s['sao']}*",
        phu=s["y_nghia"],
        dong=[{"so": "!", "chinh": x.capitalize(),
               "loai": "xau" if s["tinh_chat"] == "xấu" else "tot"}
              for x in s["anh_huong"][:3]],
        chan="Cửu diệu tinh quân"))

    if tt["pham"]:
        canh.append(_canh(
            f"Năm nay còn là năm thứ {tt['nam_thu']} của tam tai, {tt['ten_dan_gian']}, "
            f"mức {tt['muc_do']}. {tt['canh_bao']}",
            nhan="Tam tai", tieu_de=f"Năm thứ *{tt['nam_thu']}* — {tt['ten_dan_gian']}",
            phu=tt["canh_bao"],
            dong=[{"so": "×", "chinh": "Hùn vốn, góp vốn", "loai": "xau"},
                  {"so": "×", "chinh": "Đứng tên vay nợ", "loai": "xau"},
                  {"so": "×", "chinh": "Đầu tư vào chỗ chưa quen", "loai": "xau"}],
            chan=f"Nhóm {' '.join(tt['tam_hop'])}"))
    else:
        canh.append(_canh(
            "Năm nay tuổi này không phạm tam tai.",
            nhan="Tam tai", tieu_de="*Không phạm* tam tai",
            phu=f"Nhóm {' '.join(tt['tam_hop'])} gặp tam tai vào các năm "
                f"{', '.join(tt['cac_nam_tam_tai'])}.",
            chan="Tam hợp hóa tam tai"))

    if tue["pham"]:
        canh.append(_canh(
            "Ngoài ra năm nay phạm Thái Tuế: " + tue["chi_tiet"][0]["canh_bao"],
            nhan="Thái Tuế", tieu_de=f"*{tue['cac_dang'][0]}*",
            phu=tue["chi_tiet"][0]["canh_bao"], chan="Quan hệ chi tuổi với chi năm"))

    if thang_am:
        th = can_chi_thang(nam_xem, thang_am)
        d1 = lunar_to_solar(1, thang_am, nam_xem)
        d2 = lunar_to_solar(30, thang_am, nam_xem)
        qh = quan_he_chi(chi_tuoi, th.chi)
        tot = [q for q in qh if q in ("Tam hợp", "Lục hợp")]
        xau = [q for q in qh if q in ("Lục xung", "Lục hại", "Lục phá", "Tương hình")]
        thang_ky = thang_am in s["thang_ky"]
        canh.append(_canh(
            f"Riêng tháng {thang_am} âm là tháng {th.ten}. "
            + (f"Chi tháng {tot[0].lower()} với tuổi {chi_tuoi}. "
               if tot else
               (f"Chi tháng {xau[0].lower()} với tuổi {chi_tuoi}. " if xau else ""))
            + ("Đây lại đúng tháng kỵ của sao hạn."
               if thang_ky else "Tháng này không phải tháng kỵ của sao hạn."),
            nhan=f"Tháng {thang_am} âm",
            tieu_de=f"Tháng *{th.ten}*",
            phu=f"{d1.day:02d}/{d1.month:02d} – {d2.day:02d}/{d2.month:02d}/{d2.year}",
            dong=[{"so": "✓" if tot else ("!" if xau else "·"),
                   "chinh": (f"{tot[0]} với tuổi {chi_tuoi}" if tot else
                             (f"{xau[0]} với tuổi {chi_tuoi}" if xau
                              else f"Không xung hợp gì với tuổi {chi_tuoi}")),
                   "loai": "tot" if tot else ("xau" if xau else "")},
                  {"so": "!" if thang_ky else "✓",
                   "chinh": ("Đúng tháng kỵ của sao " + s["sao"]) if thang_ky
                            else ("Không phải tháng kỵ của sao " + s["sao"]),
                   "loai": "xau" if thang_ky else "tot"}],
            chan=f"{th.ten} · {nam_xem}"))

        a = date(d1.year, d1.month, d1.day)
        b = date(d2.year, d2.month, d2.day)
        kq = chon_ngay(nam_sinh, a, b, "cau_tai", gioi_tinh, 3)
        if kq["ngay_tot"]:
            canh.append(_canh(
                "Trong tháng, đây là những ngày đẹp nhất với tuổi này.",
                nhan="Ngày nên chọn", tieu_de="Ngày *đẹp* trong tháng",
                dong=[{"so": i + 1,
                       "chinh": x["duong_lich"],
                       "phu": f"{x['thu']} · ngày {x['ngay_can_chi']} · "
                              f"trực {x['truc']} · {x['diem_ca_nhan']} điểm",
                       "loai": "tot"}
                      for i, x in enumerate(kq["ngay_tot"])],
                chan=f"{kq['tong_so_ngay'] - kq['so_ngay_bi_chan']}"
                     f"/{kq['tong_so_ngay']} ngày dùng được"))

        chan_ds = [c for c in kq["ngay_bi_chan"] if "xung tuổi" in c["nhom"]][:3]
        if chan_ds:
            canh.append(_canh(
                "Còn đây là những ngày phải tránh, vì xung thẳng tuổi.",
                nhan="Ngày phải tránh", tieu_de="Ngày *xung tuổi*",
                dong=[{"so": "×", "chinh": c["duong_lich"],
                       "phu": f"{c['thu']} · ngày {c['ngay_can_chi']}",
                       "loai": "xau"} for c in chan_ds],
                chan="Lục xung · thiên khắc địa xung"))

    canh.append(_canh(
        "Đây là tri thức dân gian, dùng để tham khảo, không phải lời phán.",
        nhan="Nhớ cho", tieu_de="Tham khảo thôi,\nđừng *lo quá*",
        phu="Tử vi là tri thức văn hóa dân gian, không thay thế cho nỗ lực và "
            "quyết định của chính bạn.", chan="Tra cứu tử vi"))

    return {
        "ten": f"han-{gioi_tinh}-{nam_sinh}-{nam_xem}"
               + (f"-thang{thang_am}" if thang_am else ""),
        "tieu_de": f"{gt_chu} {nam_sinh} năm {h['nam_xem_can_chi']}"
                   + (f" — tháng {thang_am} âm" if thang_am else ""),
        "canh": canh,
        "caption": _caption_han(h, thang_am),
    }


def _caption_han(h: dict, thang_am: int | None) -> str:
    s, tt = h["sao_han"], h["tam_tai"]
    dong = [f"Tuổi {h['tuoi_can_chi']} năm {h['nam_xem_can_chi']}: "
            f"sao {s['sao']}" + (f", tam tai năm thứ {tt['nam_thu']}"
                                 if tt["pham"] else ", không phạm tam tai") + "."]
    if thang_am:
        dong.append(f"Tháng {thang_am} âm nên làm gì, tránh ngày nào — xem trong video.")
    dong.append("")
    dong.append("#tuvi #phongthuy #tamtai #xemngay #saochieumenh "
                f"#tuoi{h['tuoi_can_chi'].lower().replace(' ', '')} #lichvanien")
    return "\n".join(dong)


# --------------------------------------------------------------------------
# Kịch bản: một ngày tốt xấu
# --------------------------------------------------------------------------
def kich_ban_ngay(dd: int, mm: int, yy: int) -> dict:
    r = xem_ngay(dd, mm, yy)
    canh = [
        _canh(f"Ngày {dd} tháng {mm} là ngày tốt hay xấu.",
              lon=True, nhan="Xem ngày", tieu_de=f"Ngày *{r['duong_lich']}*",
              phu=f"Tức {r['am_lich']} âm lịch · ngày {r['ngay_can_chi']}",
              chan="Tra cứu tử vi"),
        _canh(f"Đây là ngày {r['loai_ngay'].lower()}, trực {r['truc']}, "
              f"sao {r['nhi_thap_bat_tu']}. Chấm {r['diem_tong_hop']} trên 100.",
              nhan="Tổng quan", tieu_de=f"*{r['diem_tong_hop']}*/100",
              dong=[{"so": "·", "chinh": r["loai_ngay"],
                     "loai": "tot" if r["loai_ngay"] == "Hoàng đạo" else "xau"},
                    {"so": "·", "chinh": f"Trực {r['truc']}",
                     "phu": r["truc_y_nghia"]["tom_tat"]},
                    {"so": "·", "chinh": f"Sao {r['nhi_thap_bat_tu']}",
                     "phu": r["tu_y_nghia"]["mo_ta"]}],
              chan=r["tiet_khi"]),
        _canh("Việc nên làm trong ngày này.",
              nhan="Nên", tieu_de="Việc *nên* làm",
              dong=[{"so": "✓", "chinh": x.capitalize(), "loai": "tot"}
                    for x in r["truc_y_nghia"]["nen"][:4]],
              chan=f"Trực {r['truc']}"),
        _canh("Và việc nên tránh.",
              nhan="Kỵ", tieu_de="Việc nên *tránh*",
              dong=[{"so": "×", "chinh": x.capitalize(), "loai": "xau"}
                    for x in r["truc_y_nghia"]["ky"][:4]],
              chan=("Phạm " + ", ".join(r["ngay_kieng"])) if r["ngay_kieng"]
                   else f"Trực {r['truc']}"),
        _canh("Giờ hoàng đạo trong ngày.",
              nhan="Giờ tốt", tieu_de="*Giờ hoàng đạo*",
              dong=[{"so": "✓", "chinh": g["can_chi"], "phu": g["khung_gio"],
                     "loai": "tot"} for g in r["gio_hoang_dao"][:4]],
              chan="6 giờ hoàng đạo mỗi ngày"),
        _canh("Tham khảo thôi, đừng lấy làm điều chắc chắn.",
              nhan="Nhớ cho", tieu_de="Tham khảo thôi",
              phu="Tri thức văn hóa dân gian, không phải khoa học dự báo.",
              chan="Tra cứu tử vi"),
    ]
    return {"ten": f"ngay-{yy}{mm:02d}{dd:02d}",
            "tieu_de": f"Xem ngày {r['duong_lich']}",
            "canh": canh,
            "caption": f"Ngày {r['duong_lich']} ({r['am_lich']} âm): "
                       f"{r['loai_ngay'].lower()}, trực {r['truc']}, "
                       f"{r['diem_tong_hop']}/100.\n\n"
                       f"#xemngay #ngayhoangdao #lichvanien #tuvi #phongthuy"}


# --------------------------------------------------------------------------
# Xuất kịch bản và video
# --------------------------------------------------------------------------
def viet_kich_ban(kb: dict, thu_muc: Path) -> Path:
    moc, dong = 0.0, []
    for i, c in enumerate(kb["canh"], 1):
        het = moc + c["giay"]
        dong.append(f"### Cảnh {i} — {moc:05.1f}s đến {het:05.1f}s "
                    f"({c['giay']}s)\n\n"
                    f"**Chữ trên màn hình:** {c.get('tieu_de', '').replace(chr(10), ' / ')}\n\n"
                    f"**Lời thoại:** {c['loi_thoai']}\n")
        moc = het
    noi_dung = (f"# {kb['tieu_de']}\n\n"
                f"Tổng thời lượng: **{moc:.1f} giây**, {len(kb['canh'])} cảnh.\n\n"
                f"Video xuất ra không có tiếng. Lời thoại dưới đây dùng để đọc lồng "
                f"tiếng hoặc làm phụ đề; mốc thời gian đã khớp với video.\n\n"
                + "\n".join(dong)
                + f"\n## Caption đăng bài\n\n```\n{kb['caption']}\n```\n")
    p = thu_muc / f"{kb['ten']}.md"
    p.write_text(noi_dung, encoding="utf-8")
    return p


def _ffmpeg() -> str | None:
    """ffmpeg của hệ thống, nếu không có thì thử bản đi kèm imageio-ffmpeg."""
    if (p := shutil.which("ffmpeg")):
        return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def quay_video(kb: dict, thu_muc: Path) -> Path | None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Thiếu Playwright nên bỏ qua bước quay video "
              "(kịch bản vẫn được xuất).", file=sys.stderr)
        return None
    ff = _ffmpeg()
    if not ff:
        print("Thiếu ffmpeg nên bỏ qua bước xuất MP4.", file=sys.stderr)
        return None

    tong = sum(c["giay"] for c in kb["canh"])
    html = MAU.read_text(encoding="utf-8").replace(
        "window.__CANH__ || []",
        json.dumps(kb["canh"], ensure_ascii=False))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        trang = tmp / "video.html"
        trang.write_text(html, encoding="utf-8")
        with sync_playwright() as pw:
            trinh_duyet = pw.chromium.launch(
                executable_path=_chromium(), args=["--force-device-scale-factor=1"])
            ngu_canh = trinh_duyet.new_context(
                viewport={"width": RONG, "height": CAO},
                record_video_dir=str(tmp), record_video_size={"width": RONG, "height": CAO})
            trang_web = ngu_canh.new_page()
            trang_web.goto(trang.as_uri())
            trang_web.wait_for_timeout(int(tong * 1000) + 400)
            duong_webm = trang_web.video.path()
            ngu_canh.close()
            trinh_duyet.close()
        thu_muc.mkdir(parents=True, exist_ok=True)
        ra = thu_muc / f"{kb['ten']}.mp4"
        subprocess.run(
            [ff, "-y", "-i", str(duong_webm),
             "-vf", f"scale={RONG}:{CAO}:force_original_aspect_ratio=decrease,"
                    f"pad={RONG}:{CAO}:(ow-iw)/2:(oh-ih)/2,fps=30,format=yuv420p",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-movflags", "+faststart", str(ra)],
            check=True, capture_output=True)
        return ra


def _chromium() -> str | None:
    """Chromium cài sẵn trong môi trường, nếu có."""
    for p in Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome"):
        return str(p)
    return None


def main() -> int:
    p = argparse.ArgumentParser(description="Dựng video dọc cho TikTok")
    p.add_argument("--ra", default=str(ROOT / "build" / "video"),
                   help="thư mục xuất")
    p.add_argument("--chi-kich-ban", action="store_true",
                   help="chỉ xuất kịch bản, không quay video")
    sub = p.add_subparsers(dest="loai", required=True)

    s = sub.add_parser("han", help="Video hạn của một tuổi trong một năm")
    s.add_argument("nam_sinh", type=int)
    s.add_argument("nam_xem", type=int)
    s.add_argument("--gioi-tinh", default="nam", choices=["nam", "nu"])
    s.add_argument("--thang-am", type=int, default=None, choices=range(1, 13))

    s = sub.add_parser("ngay", help="Video xem một ngày tốt xấu")
    s.add_argument("ngay", help="dd/mm/yyyy")

    a = p.parse_args()
    if a.loai == "han":
        kb = kich_ban_han(a.nam_sinh, a.nam_xem, a.gioi_tinh, a.thang_am)
    else:
        dd, mm, yy = (int(x) for x in a.ngay.replace("-", "/").split("/"))
        kb = kich_ban_ngay(dd, mm, yy)

    ra = Path(a.ra)
    ra.mkdir(parents=True, exist_ok=True)
    tep_kb = viet_kich_ban(kb, ra)
    tong = sum(c["giay"] for c in kb["canh"])
    print(f"Kịch bản: {tep_kb}  ({len(kb['canh'])} cảnh, {tong:.1f} giây)")
    if not a.chi_kich_ban:
        tep = quay_video(kb, ra)
        if tep:
            print(f"Video:    {tep}  ({tep.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
