# -*- coding: utf-8 -*-
"""An sao Tử Vi ở mức cốt lõi: 12 cung, Cục, 14 chính tinh, Tứ Hóa,
vòng Tràng Sinh, vòng Thái Tuế, bộ Lộc Tồn — Kình — Đà và đại hạn.

Đây là bản rút gọn phục vụ sinh nội dung, không phải bộ an sao đầy đủ 109 sao.
Muốn an đủ sao, xem dự án mã nguồn mở ``doanguyen/lasotuvi`` (MIT) nêu trong
SOURCES.md mục [S-02].
"""
from __future__ import annotations

from .amlich import solar_to_lunar
from .canchi import (AM_DUONG_CAN, DIA_CHI, THIEN_CAN, can_chi_nam,
                     chi_gio_tu_gio_phut, nap_am)
from .store import load

TEN_CUNG = ["Mệnh", "Phụ Mẫu", "Phúc Đức", "Điền Trạch", "Quan Lộc", "Nô Bộc",
            "Thiên Di", "Tật Ách", "Tài Bạch", "Tử Tức", "Phu Thê", "Huynh Đệ"]

# Vị trí Lộc Tồn theo can năm sinh (chỉ số địa chi, Tý = 0).
_LOC_TON = {"Giáp": 2, "Ất": 3, "Bính": 5, "Mậu": 5, "Đinh": 6, "Kỷ": 6,
            "Canh": 8, "Tân": 9, "Nhâm": 11, "Quý": 0}

# Tứ Hóa theo can năm sinh: (Hóa Lộc, Hóa Quyền, Hóa Khoa, Hóa Kỵ).
_TU_HOA = {
    "Giáp": ("Liêm Trinh", "Phá Quân", "Vũ Khúc", "Thái Dương"),
    "Ất": ("Thiên Cơ", "Thiên Lương", "Tử Vi", "Thái Âm"),
    "Bính": ("Thiên Đồng", "Thiên Cơ", "Văn Xương", "Liêm Trinh"),
    "Đinh": ("Thái Âm", "Thiên Đồng", "Thiên Cơ", "Cự Môn"),
    "Mậu": ("Tham Lang", "Thái Âm", "Hữu Bật", "Thiên Cơ"),
    "Kỷ": ("Vũ Khúc", "Tham Lang", "Thiên Lương", "Văn Khúc"),
    "Canh": ("Thái Dương", "Vũ Khúc", "Thái Âm", "Thiên Đồng"),
    "Tân": ("Cự Môn", "Thái Dương", "Văn Khúc", "Văn Xương"),
    "Nhâm": ("Thiên Lương", "Tử Vi", "Tả Phù", "Vũ Khúc"),
    "Quý": ("Phá Quân", "Cự Môn", "Thái Âm", "Tham Lang"),
}

# Thiên Khôi / Thiên Việt theo can năm sinh, dùng khẩu quyết phổ biến:
# "Giáp Mậu Canh ngưu dương, Ất Kỷ thử hầu hương, Bính Đinh trư kê vị,
#  Nhâm Quý thố xà tàng, Tân phùng mã hổ hương".
# Một số phái (trong đó có lasotuvi) dùng bảng khác cho Đinh, Mậu, Canh.
_KHOI_VIET = {"Giáp": (1, 7), "Mậu": (1, 7), "Canh": (1, 7),
              "Ất": (0, 8), "Kỷ": (0, 8),
              "Bính": (11, 9), "Đinh": (11, 9),
              "Nhâm": (3, 5), "Quý": (3, 5),
              "Tân": (6, 2)}

# Cung khởi Tràng Sinh theo số Cục.
_TRANG_SINH_KHOI = {2: 8, 3: 11, 4: 5, 5: 8, 6: 2}

VONG_TRANG_SINH = ["Tràng Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng",
                   "Suy", "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng"]

VONG_THAI_TUE = ["Thái Tuế", "Thiếu Dương", "Tang Môn", "Thiếu Âm", "Quan Phù",
                 "Tử Phù", "Tuế Phá", "Long Đức", "Bạch Hổ", "Phúc Đức",
                 "Điếu Khách", "Trực Phù"]

_CHINH_TINH_TU_VI = [("Tử Vi", 0), ("Thiên Cơ", -1), ("Thái Dương", -3),
                     ("Vũ Khúc", -4), ("Thiên Đồng", -5), ("Liêm Trinh", -8)]
_CHINH_TINH_THIEN_PHU = [("Thiên Phủ", 0), ("Thái Âm", 1), ("Tham Lang", 2),
                         ("Cự Môn", 3), ("Thiên Tướng", 4), ("Thiên Lương", 5),
                         ("Thất Sát", 6), ("Phá Quân", 10)]

_TAM_HOP_MA = {0: 2, 4: 2, 8: 2, 2: 8, 6: 8, 10: 8,
               5: 11, 9: 11, 1: 11, 11: 5, 3: 5, 7: 5}
_DAO_HOA = {8: 9, 0: 9, 4: 9, 2: 3, 6: 3, 10: 3,
            5: 6, 9: 6, 1: 6, 11: 0, 3: 0, 7: 0}


def _vi_tri_tu_vi(cuc: int, ngay: int) -> int:
    """Vị trí Tử Vi (chỉ số địa chi) theo số Cục và ngày sinh âm lịch."""
    boi = cuc
    while boi < ngay:
        boi += cuc
    du = boi - ngay
    # Đi từ cung Dần thuận (boi // cuc) bước, rồi lùi/tiến theo phần dư.
    vi_tri = (2 + boi // cuc - 1) % 12
    if du % 2 == 0:
        vi_tri = (vi_tri + du) % 12
    else:
        vi_tri = (vi_tri - du) % 12
    return vi_tri


def _can_cung(can_nam: str, chi_cung: int) -> str:
    """Can của một cung địa bàn, theo phép Ngũ hổ độn từ can năm sinh."""
    can_dan = ((THIEN_CAN.index(can_nam) % 5) * 2 + 2) % 10
    # Đếm thuận vòng 12 chi kể từ cung Dần, nên phải lấy dư theo 12 trước.
    return THIEN_CAN[(can_dan + (chi_cung - 2) % 12) % 10]


def lap_la_so(ngay: int, thang: int, nam: int, gio: int, phut: int = 0,
              gioi_tinh: str = "nam", duong_lich: bool = True) -> dict:
    """Lập lá số Tử Vi rút gọn từ ngày giờ sinh."""
    if duong_lich:
        am = solar_to_lunar(ngay, thang, nam)
        ngay_am, thang_am, nam_am = am.day, am.month, am.year
    else:
        ngay_am, thang_am, nam_am = ngay, thang, nam
    chi_gio = chi_gio_tu_gio_phut(gio, phut)
    nam_cc = can_chi_nam(nam_am)
    la_nam = gioi_tinh.lower().startswith("nam")
    duong_nam_sinh = AM_DUONG_CAN[nam_cc.can_idx] == 1

    # 1. Cung Mệnh và cung Thân
    cung_menh = (2 + (thang_am - 1) - chi_gio) % 12
    cung_than = (2 + (thang_am - 1) + chi_gio) % 12

    # 2. Ngũ hành Cục = nạp âm của can chi cung Mệnh
    can_menh = _can_cung(nam_cc.can, cung_menh)
    hanh_cuc = nap_am(THIEN_CAN.index(can_menh), cung_menh).split()[-1]
    so_cuc = {"Thủy": 2, "Mộc": 3, "Kim": 4, "Thổ": 5, "Hỏa": 6}[hanh_cuc]

    sao_o_cung: dict[int, list[dict]] = {i: [] for i in range(12)}

    def dat(ten: str, vi_tri: int, nhom: str) -> None:
        sao_o_cung[vi_tri % 12].append({"ten": ten, "nhom": nhom})

    # 3. 14 chính tinh
    tv = _vi_tri_tu_vi(so_cuc, ngay_am)
    for ten, lech in _CHINH_TINH_TU_VI:
        dat(ten, tv + lech, "Chính tinh")
    tp = (4 - tv) % 12
    for ten, lech in _CHINH_TINH_THIEN_PHU:
        dat(ten, tp + lech, "Chính tinh")

    # 4. Lộc Tồn, Kình Dương, Đà La
    lt = _LOC_TON[nam_cc.can]
    dat("Lộc Tồn", lt, "Bộ Lộc Tồn")
    dat("Kình Dương", lt + 1, "Bộ Lộc Tồn")
    dat("Đà La", lt - 1, "Bộ Lộc Tồn")

    # 5. Thiên Khôi, Thiên Việt
    khoi, viet = _KHOI_VIET[nam_cc.can]
    dat("Thiên Khôi", khoi, "Quý nhân")
    dat("Thiên Việt", viet, "Quý nhân")

    # 6. Tả Phù, Hữu Bật (theo tháng); Văn Xương, Văn Khúc (theo giờ)
    dat("Tả Phù", 4 + (thang_am - 1), "Trợ tinh")
    dat("Hữu Bật", 10 - (thang_am - 1), "Trợ tinh")
    dat("Văn Xương", 10 - chi_gio, "Văn tinh")
    dat("Văn Khúc", 4 + chi_gio, "Văn tinh")

    # 7. Thiên Mã, Đào Hoa, Hồng Loan, Thiên Hỷ
    dat("Thiên Mã", _TAM_HOP_MA[nam_cc.chi_idx], "Sao di động")
    dat("Đào Hoa", _DAO_HOA[nam_cc.chi_idx], "Đào hoa tinh")
    hong_loan = (3 - nam_cc.chi_idx) % 12
    dat("Hồng Loan", hong_loan, "Đào hoa tinh")
    dat("Thiên Hỷ", (hong_loan + 6) % 12, "Đào hoa tinh")

    # 8. Vòng Tràng Sinh — theo lệ "Dương nam, Âm nữ an thuận; Âm nam,
    #    Dương nữ an nghịch". Phái cụ Thiên Lương lại an nam thuận, nữ nghịch.
    thuan = duong_nam_sinh == la_nam
    khoi_ts = _TRANG_SINH_KHOI[so_cuc]
    for i, ten in enumerate(VONG_TRANG_SINH):
        dat(ten, khoi_ts + i if thuan else khoi_ts - i, "Vòng Tràng Sinh")

    # 9. Vòng Thái Tuế (luôn đi thuận từ chi năm sinh)
    for i, ten in enumerate(VONG_THAI_TUE):
        dat(ten, nam_cc.chi_idx + i, "Vòng Thái Tuế")

    # 10. Tứ Hóa
    loc, quyen, khoa, ky = _TU_HOA[nam_cc.can]
    tu_hoa = {"Hóa Lộc": loc, "Hóa Quyền": quyen, "Hóa Khoa": khoa, "Hóa Kỵ": ky}
    for hoa, chu in tu_hoa.items():
        for vi_tri, ds in sao_o_cung.items():
            if any(s["ten"] == chu for s in ds):
                dat(hoa, vi_tri, "Tứ Hóa")
                break

    # 11. Đại hạn 10 năm
    dai_han = {}
    for i in range(12):
        vi_tri = (cung_menh + i) % 12 if thuan else (cung_menh - i) % 12
        dai_han[vi_tri] = f"{so_cuc + i * 10}-{so_cuc + i * 10 + 9}"

    cung_info = {c["ten"]: c for c in load("tu_vi/cung")}
    cung_list = []
    for i in range(12):
        ten_cung = TEN_CUNG[(i - cung_menh) % 12]
        cung_list.append({
            "chi": DIA_CHI[i],
            "can": _can_cung(nam_cc.can, i),
            "ten_cung": ten_cung,
            "chu_ve": cung_info[ten_cung]["chu_ve"],
            "la_cung_than": i == cung_than,
            "dai_han": dai_han[i],
            "sao": sorted(sao_o_cung[i], key=lambda s: s["nhom"] != "Chính tinh"),
        })

    return {
        "am_lich": {"ngay": ngay_am, "thang": thang_am, "nam": nam_am,
                    "gio": DIA_CHI[chi_gio]},
        "nam_sinh_can_chi": nam_cc.ten,
        "menh_nap_am": nam_cc.nap_am,
        "gioi_tinh": "Nam" if la_nam else "Nữ",
        "am_duong_nam_sinh": "Dương" if duong_nam_sinh else "Âm",
        "chieu_di_han": "thuận" if thuan else "nghịch",
        "cung_menh": DIA_CHI[cung_menh],
        "cung_than_tai": TEN_CUNG[(cung_than - cung_menh) % 12],
        "cuc": f"{hanh_cuc} {so_cuc} cục",
        "so_cuc": so_cuc,
        "tu_hoa": tu_hoa,
        "cac_cung": cung_list,
    }


def chinh_tinh_cung_menh(la_so: dict) -> list[str]:
    """Danh sách chính tinh tại cung Mệnh (rỗng nghĩa là Mệnh vô chính diệu)."""
    cung = next(c for c in la_so["cac_cung"] if c["ten_cung"] == "Mệnh")
    return [s["ten"] for s in cung["sao"] if s["nhom"] == "Chính tinh"]
