# -*- coding: utf-8 -*-
"""Chọn ngày theo tuổi người dùng — lọc ngày xung khắc và chấm điểm theo việc.

Khác với :func:`tuvi.ngay_gio.xem_ngay` vốn chỉ chấm ngày một cách chung chung,
mô-đun này đưa thêm ba lớp xét:

1. Quan hệ giữa chi ngày và chi tuổi (xung, hình, hại, phá, hợp).
2. Việc định làm, đối chiếu với mục "nên" và "kỵ" của 12 Trực và 28 tú.
3. Tháng kỵ của sao hạn năm đó.

Ngày lục xung hoặc thiên khắc địa xung với tuổi bị **chặn thẳng**, không chấm
điểm, vì dù các yếu tố khác đẹp tới đâu thì lệ cũ vẫn không dùng.
"""
from __future__ import annotations

from datetime import date, timedelta

from .amlich import solar_to_lunar
from .canchi import (DIA_CHI, can_chi_gio, can_chi_ngay, can_chi_nam,
                     luc_xung, quan_he_chi, thien_khac_dia_xung)
from .han import sao_han
from .ngay_gio import KHUNG_GIO, gio_hoang_dao, xem_ngay
from .store import load

THU_VN = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm",
          "Thứ Sáu", "Thứ Bảy", "Chủ nhật"]

# Quan hệ chi ngày với chi tuổi -> khóa trọng số trong lich/viec.json.
_KHOA_QUAN_HE = {"Tam hợp": "tam_hop", "Lục hợp": "luc_hop",
                 "Trùng chi": "trung_chi", "Tự hình": "tu_hinh",
                 "Lục hại": "luc_hai", "Lục phá": "luc_pha",
                 "Tương hình": "tuong_hinh"}


def _viec(ma: str | None) -> dict | None:
    if not ma:
        return None
    ds = load("lich/viec")["viec"]
    try:
        return next(v for v in ds if v["ma"] == ma)
    except StopIteration:
        raise ValueError(f"Không có việc mã {ma}. Có: "
                         f"{', '.join(v['ma'] for v in ds)}") from None


def danh_sach_viec() -> list[dict]:
    """Danh mục việc kèm mức độ phủ của dữ liệu Trực và 28 tú cho việc đó."""
    truc, tu = load("lich/truc"), load("lich/nhi_thap_bat_tu")
    ra = []
    for v in load("lich/viec")["viec"]:
        cum = set(v["cum_tu"])
        dem = lambda ds, khoa: sum(1 for r in ds if cum & set(r[khoa]))  # noqa: E731
        ra.append({**v,
                   "so_truc_khop": dem(truc, "nen") + dem(truc, "ky"),
                   "so_tu_khop": dem(tu, "nen") + dem(tu, "ky")})
    return ra


def gio_tot_theo_tuoi(jd: int, chi_tuoi: str) -> list[dict]:
    """Giờ hoàng đạo đã loại các canh giờ xung với chi tuổi."""
    xung = luc_xung(chi_tuoi)
    return [g for g in gio_hoang_dao(jd)
            if g["hoang_dao"] and g["chi"] != xung]


def xem_ngay_theo_tuoi(dd: int, mm: int, yy: int, nam_sinh_am: int,
                       gioi_tinh: str = "nam", viec: str | None = None) -> dict:
    """Chấm một ngày cho một người cụ thể, có giải thích từng khoản cộng trừ."""
    chung = xem_ngay(dd, mm, yy)
    cau_hinh = load("lich/viec")
    ts = cau_hinh["trong_so"]
    v = _viec(viec)

    am = solar_to_lunar(dd, mm, yy)
    cc_ngay = can_chi_ngay(am.jd)
    cc_tuoi = can_chi_nam(nam_sinh_am)
    quan_he = quan_he_chi(cc_tuoi.chi, cc_ngay.chi)

    # --- chặn cứng ---
    chan, nhom_chan = [], set()
    if "Lục xung" in quan_he:
        chan.append(f"Ngày {cc_ngay.chi} xung thẳng tuổi {cc_tuoi.chi}")
        nhom_chan.add("xung tuổi")
    if thien_khac_dia_xung(cc_ngay, cc_tuoi):
        chan.append(f"Thiên khắc địa xung: ngày {cc_ngay.ten} "
                    f"khắc xung tuổi {cc_tuoi.ten}")
        nhom_chan.add("xung tuổi")
    if v:
        pham = [k for k in chung["ngay_kieng"] if k in v["kieng"]]
        if pham:
            chan.append(f"Ngày {', '.join(pham)} — lệ cũ không "
                        f"{v['ten'].lower()} vào ngày này")
            nhom_chan.add("ngày kiêng")

    # --- cộng trừ ---
    khoan: list[dict] = []
    for q in quan_he:
        khoa = _KHOA_QUAN_HE.get(q)
        if khoa:
            khoan.append({"muc": f"{q} với tuổi {cc_tuoi.chi}",
                          "diem": ts[khoa], "nhom": "tuổi"})

    if v:
        cum = set(v["cum_tu"])
        truc = next(r for r in load("lich/truc") if r["ten"] == chung["truc"])
        tu = next(r for r in load("lich/nhi_thap_bat_tu")
                  if r["ten"] == chung["nhi_thap_bat_tu"])
        for bang, ten_bang in ((truc, f"Trực {truc['ten']}"),
                               (tu, f"Sao {tu['ten']}")):
            if cum & set(bang["nen"]):
                khoan.append({"muc": f"{ten_bang} hợp việc {v['ten'].lower()}",
                              "diem": ts["truc_nen" if bang is truc else "tu_nen"],
                              "nhom": "việc"})
            if cum & set(bang["ky"]):
                khoan.append({"muc": f"{ten_bang} kỵ việc {v['ten'].lower()}",
                              "diem": ts["truc_ky" if bang is truc else "tu_ky"],
                              "nhom": "việc"})

    sh = sao_han(nam_sinh_am, am.year, gioi_tinh)
    if am.month in sh["thang_ky"]:
        khoan.append({"muc": f"Tháng {am.month} âm lịch là tháng kỵ của "
                             f"sao {sh['sao']}",
                      "diem": ts["thang_ky_sao_han"], "nhom": "hạn"})

    diem = max(0, min(100, chung["diem_tong_hop"]
                      + sum(k["diem"] for k in khoan)))
    return {
        **chung,
        "thu": THU_VN[date(yy, mm, dd).weekday()],
        "tuoi_can_chi": cc_tuoi.ten,
        "quan_he_voi_tuoi": quan_he,
        "viec": v["ten"] if v else None,
        "diem_chung": chung["diem_tong_hop"],
        "diem_ca_nhan": 0 if chan else diem,
        "khoan_cong_tru": khoan,
        "bi_chan": bool(chan),
        "ly_do_chan": chan,
        "nhom_chan": sorted(nhom_chan),
        "sao_han_nam": sh["sao"],
        "gio_tot": gio_tot_theo_tuoi(am.jd, cc_tuoi.chi),
        "gio_xung_tuoi": luc_xung(cc_tuoi.chi),
    }


def chon_ngay(nam_sinh_am: int, tu_ngay: date, den_ngay: date,
              viec: str | None = None, gioi_tinh: str = "nam",
              so_luong: int = 10) -> dict:
    """Quét một khoảng ngày, loại ngày xung tuổi rồi xếp hạng phần còn lại."""
    if den_ngay < tu_ngay:
        raise ValueError("Ngày kết thúc phải sau ngày bắt đầu")
    if (den_ngay - tu_ngay).days > 400:
        raise ValueError("Khoảng thời gian tối đa là 400 ngày")

    tat_ca = []
    d = tu_ngay
    while d <= den_ngay:
        tat_ca.append(xem_ngay_theo_tuoi(d.day, d.month, d.year,
                                         nam_sinh_am, gioi_tinh, viec))
        d += timedelta(days=1)

    dung_duoc = [r for r in tat_ca if not r["bi_chan"]]
    dung_duoc.sort(key=lambda r: (-r["diem_ca_nhan"], r["duong_lich"]))
    bi_chan = [r for r in tat_ca if r["bi_chan"]]
    v = _viec(viec)
    phu = next((x for x in danh_sach_viec() if x["ma"] == viec), None) if viec else None

    return {
        "nam_sinh_am_lich": nam_sinh_am,
        "tuoi_can_chi": can_chi_nam(nam_sinh_am).ten,
        "gioi_tinh": gioi_tinh,
        "viec": v["ten"] if v else "Không chọn việc cụ thể",
        "ghi_chu_viec": v["ghi_chu"] if v else "",
        "tu_ngay": tu_ngay.strftime("%d/%m/%Y"),
        "den_ngay": den_ngay.strftime("%d/%m/%Y"),
        "tong_so_ngay": len(tat_ca),
        "so_ngay_bi_chan": len(bi_chan),
        "so_chan_xung_tuoi": sum(1 for r in bi_chan
                                 if "xung tuổi" in r["nhom_chan"]),
        "so_chan_ngay_kieng": sum(1 for r in bi_chan
                                  if "ngày kiêng" in r["nhom_chan"]),
        "ngay_kieng_cua_viec": v["kieng"] if v else [],
        "ngay_bi_chan": [{"duong_lich": r["duong_lich"], "thu": r["thu"],
                          "ngay_can_chi": r["ngay_can_chi"],
                          "nhom": r["nhom_chan"],
                          "ly_do": r["ly_do_chan"]} for r in bi_chan],
        "ngay_tot": dung_duoc[:so_luong],
        "canh_bao_du_lieu": (
            "Bộ 28 tú chưa có mục nên/kỵ cho việc này, nên điểm chỉ dựa vào "
            "12 Trực và quan hệ với tuổi."
            if phu and phu["so_tu_khop"] == 0 else ""),
    }
