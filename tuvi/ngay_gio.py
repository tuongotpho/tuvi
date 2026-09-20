# -*- coding: utf-8 -*-
"""Xem ngày giờ: 12 Trực, Nhị thập bát tú, Hoàng đạo / Hắc đạo, ngày kiêng."""
from __future__ import annotations

from .amlich import jd_from_date, solar_to_lunar
from .canchi import (DIA_CHI, can_chi_gio, can_chi_ngay, chi_thang_theo_tiet,
                     tiet_khi_cua_ngay)
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
