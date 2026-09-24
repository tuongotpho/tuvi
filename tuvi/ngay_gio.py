# -*- coding: utf-8 -*-
"""Xem ngày giờ: 12 Trực, Nhị thập bát tú, Hoàng đạo / Hắc đạo, ngày kiêng."""
from __future__ import annotations

from .amlich import jd_from_date, solar_to_lunar
from .canchi import (DIA_CHI, can_chi_gio, can_chi_ngay, chi_thang_theo_tiet,
                     tiet_khi_cua_ngay)
from .kiem_tra import ngay_duong_hop_le
from .store import load

TRUC = ["Kiến", "Trừ", "Mãn", "Bình", "Định", "Chấp",
        "Phá", "Nguy", "Thành", "Thu", "Khai", "Bế"]

NHI_THAP_BAT_TU = [
    "Giác", "Cang", "Đê", "Phòng", "Tâm", "Vĩ", "Cơ",
    "Đẩu", "Ngưu", "Nữ", "Hư", "Nguy", "Thất", "Bích",
    "Khuê", "Lâu", "Vị", "Mão", "Tất", "Chủy", "Sâm",
    "Tỉnh", "Quỷ", "Liễu", "Tinh", "Trương", "Dực", "Chẩn",
]

# Mốc neo: 01/01/1995 (Chủ nhật) là ngày sao Hư — sao thứ 11 trong vòng 28.
_TU_ANCHOR_JD = jd_from_date(1, 1, 1995)
_TU_ANCHOR_IDX = 10  # 0-based của "Hư"

# 12 vị thần trực nhật; 6 vị hoàng đạo xen 6 vị hắc đạo.
THAN_12 = [
    ("Thanh Long", True), ("Minh Đường", True), ("Thiên Hình", False),
    ("Chu Tước", False), ("Kim Quỹ", True), ("Kim Đường", True),
    ("Bạch Hổ", False), ("Ngọc Đường", True), ("Thiên Lao", False),
    ("Nguyên Vũ", False), ("Tư Mệnh", True), ("Câu Trần", False),
]

# Tháng âm lịch -> địa chi mà Thanh Long khởi đầu.
_THANH_LONG_KHOI = {1: 0, 7: 0, 2: 2, 8: 2, 3: 4, 9: 4,
                    4: 6, 10: 6, 5: 8, 11: 8, 6: 10, 12: 10}

# Giờ hoàng đạo theo địa chi ngày (chi % 6); mỗi chuỗi 12 ký tự ứng Tý..Hợi.
_GIO_HD = ["110100101100", "001101001011", "110011010010",
           "101100110100", "001011001101", "010010110011"]

KHUNG_GIO = ["23h-01h", "01h-03h", "03h-05h", "05h-07h", "07h-09h", "09h-11h",
             "11h-13h", "13h-15h", "15h-17h", "17h-19h", "19h-21h", "21h-23h"]

# Ngày Thọ tử theo tháng âm lịch (can chi ngày).
_THO_TU = {1: "Bính Tuất", 2: "Nhâm Thìn", 3: "Tân Hợi", 4: "Đinh Tỵ",
           5: "Mậu Tý", 6: "Bính Ngọ", 7: "Ất Sửu", 8: "Quý Mùi",
           9: "Giáp Dần", 10: "Mậu Thân", 11: "Tân Mão", 12: "Tân Dậu"}

# Dương công kỵ nhật: 13 ngày âm lịch cố định trong năm.
_DUONG_CONG = {1: 13, 2: 11, 3: 9, 4: 7, 5: 5, 6: 3,
               7: 1, 8: 27, 9: 25, 10: 23, 11: 21, 12: 19}
_DUONG_CONG_PHU = {7: 29}  # tháng 7 có thêm ngày 29

TAM_NUONG = [3, 7, 13, 18, 22, 27]
NGUYET_KY = [5, 14, 23]


def truc_cua_ngay(jd: int) -> str:
    """12 Trực = khoảng cách giữa chi ngày và nguyệt kiến (tháng tiết lệnh)."""
    chi_ngay = (jd + 1) % 12
    return TRUC[(chi_ngay - chi_thang_theo_tiet(jd)) % 12]


def tu_cua_ngay(jd: int) -> str:
    """Nhị thập bát tú — vòng 28 ngày liên tục, neo vào 01/01/1995 (sao Hư)."""
    return NHI_THAP_BAT_TU[(jd - _TU_ANCHOR_JD + _TU_ANCHOR_IDX) % 28]


def than_truc_nhat(lunar_month: int, jd: int) -> tuple[str, bool]:
    """Vị thần trực nhật và ngày đó là hoàng đạo (True) hay hắc đạo."""
    chi_ngay = (jd + 1) % 12
    khoi = _THANH_LONG_KHOI[lunar_month]
    return THAN_12[(chi_ngay - khoi) % 12]


def gio_hoang_dao(jd: int) -> list[dict]:
    """Danh sách 12 canh giờ kèm đánh giá hoàng đạo / hắc đạo."""
    chi_ngay = (jd + 1) % 12
    mask = _GIO_HD[chi_ngay % 6]
    can_ngay = (jd + 9) % 10
    out = []
    for i, ch in enumerate(mask):
        cc = can_chi_gio(can_ngay, i)
        out.append({
            "chi": DIA_CHI[i],
            "can_chi": cc.ten,
            "khung_gio": KHUNG_GIO[i],
            "hoang_dao": ch == "1",
        })
    return out


def ngay_kieng(lunar_day: int, lunar_month: int, jd: int) -> list[str]:
    """Các loại ngày xấu dân gian mà ngày này phạm phải."""
    ra = []
    if lunar_day in TAM_NUONG:
        ra.append("Tam nương")
    if lunar_day in NGUYET_KY:
        ra.append("Nguyệt kỵ")
    if can_chi_ngay(jd).ten == _THO_TU.get(lunar_month):
        ra.append("Thọ tử")
    if _DUONG_CONG.get(lunar_month) == lunar_day or \
            _DUONG_CONG_PHU.get(lunar_month) == lunar_day:
        ra.append("Dương công kỵ nhật")
    return ra


def xem_ngay(dd: int, mm: int, yy: int) -> dict:
    """Hồ sơ đầy đủ của một ngày dương lịch — đầu vào chuẩn để dựng content."""
    ngay_duong_hop_le(dd, mm, yy)
    am = solar_to_lunar(dd, mm, yy)
    jd = am.jd
    than, la_hoang_dao = than_truc_nhat(am.month, jd)
    truc = truc_cua_ngay(jd)
    tu = tu_cua_ngay(jd)
    truc_info = {r["ten"]: r for r in load("lich/truc")}
    tu_info = {r["ten"]: r for r in load("lich/nhi_thap_bat_tu")}
    gio = gio_hoang_dao(jd)
    kieng = ngay_kieng(am.day, am.month, jd)
    return {
        "duong_lich": f"{dd:02d}/{mm:02d}/{yy}",
        "am_lich": f"{am.day:02d}/{am.month:02d}/{am.year}",
        "ngay_can_chi": can_chi_ngay(jd).ten,
        "tiet_khi": tiet_khi_cua_ngay(jd),
        "truc": truc,
        "truc_y_nghia": truc_info.get(truc, {}),
        "nhi_thap_bat_tu": tu,
        "tu_y_nghia": tu_info.get(tu, {}),
        "than_truc_nhat": than,
        "loai_ngay": "Hoàng đạo" if la_hoang_dao else "Hắc đạo",
        "gio_hoang_dao": [g for g in gio if g["hoang_dao"]],
        "gio_hac_dao": [g for g in gio if not g["hoang_dao"]],
        "ngay_kieng": kieng,
        "diem_tong_hop": _cham_diem(la_hoang_dao, truc_info.get(truc, {}),
                                    tu_info.get(tu, {}), kieng),
    }


def _cham_diem(la_hoang_dao: bool, truc: dict, tu: dict, kieng: list[str]) -> int:
    """Điểm 0-100 để xếp hạng ngày — thuần quy ước, phục vụ sắp xếp content."""
    diem = 50
    diem += 15 if la_hoang_dao else -15
    diem += {"tốt": 15, "trung bình": 0, "xấu": -15}.get(truc.get("tinh_chat"), 0)
    diem += {"tốt": 15, "trung bình": 0, "xấu": -15}.get(tu.get("tinh_chat"), 0)
    diem -= 7 * len(kieng)
    return max(0, min(100, diem))


# ==========================================================================
# Thông tin mở rộng cho tab Xem ngày. Mỗi mục đều đã đối chiếu với ít nhất hai
# nguồn độc lập — xem SOURCES.md mục H và tests/test_xem_ngay.py.
# ==========================================================================

THU = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"]

# Ngũ hành ngày theo quan hệ hành của can và chi (Hiệp Kỷ Biện Phương Thư):
# can sinh chi = Bảo nhật, chi sinh can = Nghĩa nhật, can khắc chi = Chế nhật,
# chi khắc can = Phạt nhật, cùng hành = Chuyên nhật.
_LOAI_NGAY = {
    "Can sinh Chi": ("Bảo nhật", "tốt"), "Chi sinh Can": ("Nghĩa nhật", "tốt"),
    "Can khắc Chi": ("Chế nhật", "tốt vừa"), "Chi khắc Can": ("Phạt nhật", "xấu"),
    "Can Chi cùng hành": ("Chuyên nhật", "tốt"),
}
_SINH = {"Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim", "Kim": "Thủy", "Thủy": "Mộc"}
_KHAC = {"Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim", "Kim": "Mộc"}


def ngu_hanh_ngay(can: str, chi: str) -> dict:
    """Ngày Bảo / Nghĩa / Chế / Phạt / Chuyên theo hành của can và chi."""
    from .canchi import HANH_CAN, HANH_CHI, THIEN_CAN
    a, b = HANH_CAN[THIEN_CAN.index(can)], HANH_CHI[DIA_CHI.index(chi)]
    if a == b:
        qh = "Can Chi cùng hành"
    elif _SINH[a] == b:
        qh = "Can sinh Chi"
    elif _SINH[b] == a:
        qh = "Chi sinh Can"
    elif _KHAC[a] == b:
        qh = "Can khắc Chi"
    else:
        qh = "Chi khắc Can"
    ten, tc = _LOAI_NGAY[qh]
    return {"ten": ten, "tinh_chat": tc, "quan_he": qh, "hanh_can": a, "hanh_chi": b}


def tuoi_hop_xung(chi_ngay: str) -> dict:
    """Con giáp hợp / xung / hình / hại / phá với chi của ngày."""
    from .canchi import CON_GIAP, quan_he_chi
    nhom = {"Tam hợp": [], "Lục hợp": [], "Lục xung": [], "Tương hình": [],
            "Lục hại": [], "Lục phá": []}
    for c in DIA_CHI:
        if c == chi_ngay:
            continue
        for qh in quan_he_chi(chi_ngay, c):
            if qh in nhom:
                nhom[qh].append(f"{c} ({CON_GIAP[DIA_CHI.index(c)]})")
    return {"tam_hop": nhom["Tam hợp"], "luc_hop": nhom["Lục hợp"],
            "xung": nhom["Lục xung"], "hinh": nhom["Tương hình"],
            "hai": nhom["Lục hại"], "pha": nhom["Lục phá"]}


def luc_dieu(thang_am: int, ngay_am: int) -> dict:
    """Khổng Minh lục diệu của ngày: mùng 1 tháng Giêng là Đại An."""
    ds = load("lich/luc_dieu")["thu_tu"]
    return ds[(thang_am + ngay_am - 2) % 6]


def gio_xuat_hanh(thang_am: int, ngay_am: int) -> list[dict]:
    """Giờ xuất hành theo Lý Thuần Phong: giờ Tý đứng ở lục diệu của ngày."""
    ds = load("lich/luc_dieu")["thu_tu"]
    goc = (thang_am + ngay_am - 2) % 6
    return [{"chi": DIA_CHI[i], "khung_gio": KHUNG_GIO[i], **ds[(goc + i) % 6]}
            for i in range(12)]


def huong_xuat_hanh(can: str, hoa_giap_1: int) -> dict:
    """Hỷ thần, Tài thần theo can ngày; Hạc thần theo vị trí trong Lục thập hoa giáp."""
    d = load("lich/huong_xuat_hanh")
    hac = None
    for doan in d["hac_than"]["chu_ky"]:
        if (hoa_giap_1 - doan["tu"]) % 60 < doan["so_ngay"]:
            hac = doan["huong"]
    return {"hy_than": d["hy_than"]["bang"][can],
            "tai_than": d["tai_than"]["bang"][can],
            "tai_than_chua_thong_nhat": len(d["tai_than"]["bang"][can]) > 1,
            "hac_than": hac}


def banh_to(can: str, chi: str) -> dict:
    d = load("lich/banh_to")
    return {"can": next(r for r in d["can"] if r["ten"] == can),
            "chi": next(r for r in d["chi"] if r["ten"] == chi)}


def ngoc_hap(thang_am: int, can: str, chi: str) -> dict:
    """Sao tốt, sao xấu theo Ngọc Hạp Thông Thư (33 sao đã đối chiếu)."""
    cc = f"{can} {chi}"
    tot, xau = [], []
    for s in load("lich/ngoc_hap")["sao"]:
        bang = s["bang"][str(thang_am)]
        if can in bang or chi in bang or cc in bang:
            (tot if s["tinh_chat"] == "tốt" else xau).append(
                {"ten": s["ten"], "han_tu": s["han_tu"], "y_nghia": s["y_nghia"]})
    return {"tot": tot, "xau": xau}


# Thọ tử theo Ngọc Hạp Thông Thư: chỉ xét chi ngày (cách phổ thông ở _THO_TU
# xét cả can lẫn chi). Hai cách đều lưu hành nên ghi rõ phạm theo cách nào.
_THO_TU_CHI = {1: "Tuất", 2: "Thìn", 3: "Hợi", 4: "Tỵ", 5: "Tý", 6: "Ngọ",
               7: "Sửu", 8: "Mùi", 9: "Dần", 10: "Thân", 11: "Mão", 12: "Dậu"}


def tho_tu(thang_am: int, can_chi: str) -> list[str]:
    ra = []
    if can_chi == _THO_TU.get(thang_am):
        ra.append("cách phổ thông (theo can chi)")
    if can_chi.split()[1] == _THO_TU_CHI[thang_am]:
        ra.append("Ngọc Hạp Thông Thư (theo chi)")
    return ra


def _so_ngay_thang_am(am) -> int:
    """Tháng âm lịch đủ (30 ngày) hay thiếu (29 ngày)."""
    jd_mung_1 = am.jd - am.day + 1
    from .amlich import jd_to_date
    d = jd_to_date(jd_mung_1 + 29)
    return 29 if solar_to_lunar(d.day, d.month, d.year).day == 1 else 30


def chi_tiet_ngay(dd: int, mm: int, yy: int) -> dict:
    """Hồ sơ đầy đủ cho tab Xem ngày (nặng hơn ``xem_ngay``, chỉ gọi khi cần)."""
    from .canchi import can_chi_nam, can_chi_thang
    from .thien_van import tiet_quanh_ngay
    co_ban = xem_ngay(dd, mm, yy)
    am = solar_to_lunar(dd, mm, yy)
    ngay = can_chi_ngay(am.jd)
    tiet = tiet_quanh_ngay(am.jd)
    fmt = lambda t: f"{t[3]:02d}:{t[4]:02d} ngày {t[0]:02d}/{t[1]:02d}/{t[2]}"
    return {
        **co_ban,
        "thu": THU[(am.jd) % 7],
        "am": {"ngay": am.day, "thang": am.month, "nam": am.year, "nhuan": bool(am.leap),
               "so_ngay_thang": _so_ngay_thang_am(am)},
        "thang_can_chi": can_chi_thang(am.year, am.month).ten,
        "nam_can_chi": can_chi_nam(am.year).ten,
        "nap_am_ngay": ngay.nap_am,
        "tiet_chi_tiet": {"ten": tiet["ten"], "bat_dau": fmt(tiet["bat_dau"]),
                          "ke_tiep": tiet["ke_tiep"], "ke_tiep_bat_dau": fmt(tiet["ke_tiep_bat_dau"])},
        "ngu_hanh_ngay": ngu_hanh_ngay(ngay.can, ngay.chi),
        "tuoi": tuoi_hop_xung(ngay.chi),
        "luc_dieu": luc_dieu(am.month, am.day),
        "gio_xuat_hanh": gio_xuat_hanh(am.month, am.day),
        "huong_xuat_hanh": huong_xuat_hanh(ngay.can, ngay.hoa_giap_idx + 1),
        "banh_to": banh_to(ngay.can, ngay.chi),
        "ngoc_hap": ngoc_hap(am.month, ngay.can, ngay.chi),
        "tho_tu": tho_tu(am.month, ngay.ten),
    }


# Ngày lễ, tết cố định. Âm lịch: (ngày, tháng); dương lịch: (ngày, tháng).
LE_AM = {(1, 1): "Tết Nguyên đán", (2, 1): "Tết Nguyên đán", (3, 1): "Tết Nguyên đán",
         (15, 1): "Rằm tháng Giêng", (10, 3): "Giỗ Tổ Hùng Vương", (15, 4): "Lễ Phật đản",
         (5, 5): "Tết Đoan ngọ", (15, 7): "Rằm tháng Bảy (Vu lan)", (15, 8): "Tết Trung thu",
         (23, 12): "Ông Công ông Táo"}
LE_DUONG = {(1, 1): "Tết Dương lịch", (30, 4): "Ngày Giải phóng miền Nam", (1, 5): "Quốc tế Lao động",
            (2, 9): "Quốc khánh"}


def lich_thang(thang: int, nam: int) -> dict:
    """Mọi ngày của một tháng dương lịch, gọn nhẹ để vẽ bảng lịch tháng."""
    from calendar import monthrange
    from .kiem_tra import nam_hop_le, so_nguyen
    from .thien_van import TEN_TIET, muc_tiet_cuoi_ngay
    nam = nam_hop_le(nam, "Năm")
    thang = so_nguyen(thang, "Tháng", 1, 12)
    ngay = []
    for d in range(1, monthrange(nam, thang)[1] + 1):
        am = solar_to_lunar(d, thang, nam)
        than, hd = than_truc_nhat(am.month, am.jd)
        muc = muc_tiet_cuoi_ngay(am.jd)
        le = [x for x in (LE_DUONG.get((d, thang)),
                          None if am.leap else LE_AM.get((am.day, am.month))) if x]
        # Giao thừa: ngày cuối cùng của tháng Chạp (29 hoặc 30).
        if am.month == 12 and not am.leap and _so_ngay_thang_am(am) == am.day:
            le.append("Giao thừa")
        ngay.append({
            "ngay": d, "thu": am.jd % 7,
            "am": {"ngay": am.day, "thang": am.month, "nhuan": bool(am.leap)},
            "can_chi": can_chi_ngay(am.jd).ten,
            "hoang_dao": hd, "than": than,
            "kieng": ngay_kieng(am.day, am.month, am.jd),
            "tiet": TEN_TIET[muc] if muc != muc_tiet_cuoi_ngay(am.jd - 1) else None,
            "le": le,
        })
    return {"thang": thang, "nam": nam, "ngay": ngay}
