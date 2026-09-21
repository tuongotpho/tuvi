# -*- coding: utf-8 -*-
"""An sao Tử Vi: 12 cung, Cục, đủ 109 sao, Tứ Hóa, Tuần — Triệt và đại hạn.

Quy tắc an sao lấy theo sách phổ thông và được đối chiếu tự động với dự án
mã nguồn mở ``doanguyen/lasotuvi`` (MIT, SOURCES.md mục [S-02]) trong
``tests/``. Những chỗ hai bên khác trường phái liệt kê ở SOURCES.md mục E.
"""
from __future__ import annotations

from .amlich import solar_to_lunar
from .canchi import (AM_DUONG_CAN, DIA_CHI, THIEN_CAN, can_chi_nam,
                     chi_gio_tu_gio_phut, nap_am)
from .kiem_tra import (gio_phut_hop_le, gioi_tinh_hop_le, ngay_am_hop_le,
                       ngay_duong_hop_le)
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

VONG_BAC_SI = ["Bác Sĩ", "Lực Sĩ", "Thanh Long", "Tiểu Hao", "Tướng Quân", "Tấu Thư",
               "Phi Liêm", "Hỷ Thần", "Bệnh Phù", "Đại Hao", "Phục Binh", "Quan Phủ"]

# Cung khởi Hỏa Tinh, Linh Tinh theo tam hợp chi năm sinh (kể là giờ Tý).
# Tuổi Tỵ Dậu Sửu có hai phái; ở đây theo bản phổ thông "Hỏa Mão, Linh Tuất".
_KHOI_HOA_LINH = {2: (1, 3), 6: (1, 3), 10: (1, 3),      # Dần Ngọ Tuất: Sửu, Mão
                  8: (2, 10), 0: (2, 10), 4: (2, 10),    # Thân Tý Thìn: Dần, Tuất
                  5: (3, 10), 9: (3, 10), 1: (3, 10),    # Tỵ Dậu Sửu: Mão, Tuất
                  11: (9, 10), 3: (9, 10), 7: (9, 10)}   # Hợi Mão Mùi: Dậu, Tuất

# Cô Thần, Quả Tú theo tam hợp chi năm sinh.
_CO_QUA = {11: (2, 10), 0: (2, 10), 1: (2, 10),        # Hợi Tý Sửu: Dần, Tuất
           2: (5, 1), 3: (5, 1), 4: (5, 1),            # Dần Mão Thìn: Tỵ, Sửu
           5: (8, 4), 6: (8, 4), 7: (8, 4),            # Tỵ Ngọ Mùi: Thân, Thìn
           8: (11, 7), 9: (11, 7), 10: (11, 7)}        # Thân Dậu Tuất: Hợi, Mùi

# Phá Toái: Tý Ngọ Mão Dậu tại Tỵ; Dần Thân Tỵ Hợi tại Dậu; Thìn Tuất Sửu Mùi tại Sửu.
_PHA_TOAI = {0: 5, 6: 5, 3: 5, 9: 5, 2: 9, 8: 9, 5: 9, 11: 9, 4: 1, 10: 1, 1: 1, 7: 1}

# Các sao an theo can năm sinh (chỉ số địa chi, Tý = 0).
_THIEN_QUAN = {"Giáp": 7, "Ất": 4, "Bính": 5, "Đinh": 2, "Mậu": 3,
               "Kỷ": 9, "Canh": 11, "Tân": 9, "Nhâm": 10, "Quý": 6}
_THIEN_PHUC = {"Giáp": 9, "Ất": 8, "Bính": 0, "Đinh": 11, "Mậu": 3,
               "Kỷ": 2, "Canh": 6, "Tân": 5, "Nhâm": 6, "Quý": 5}
_LUU_HA = {"Giáp": 9, "Ất": 10, "Bính": 7, "Đinh": 4, "Mậu": 5,
           "Kỷ": 6, "Canh": 8, "Tân": 3, "Nhâm": 11, "Quý": 2}
_THIEN_TRU = {"Giáp": 5, "Ất": 6, "Bính": 0, "Đinh": 5, "Mậu": 6,
              "Kỷ": 8, "Canh": 2, "Tân": 6, "Nhâm": 9, "Quý": 10}
# Triệt: Giáp Kỷ — Thân Dậu; Ất Canh — Ngọ Mùi; Bính Tân — Thìn Tỵ;
# Đinh Nhâm — Dần Mão; Mậu Quý — Tý Sửu.
_TRIET = {"Giáp": 8, "Kỷ": 8, "Ất": 6, "Canh": 6, "Bính": 4, "Tân": 4,
          "Đinh": 2, "Nhâm": 2, "Mậu": 0, "Quý": 0}


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
    """Lập lá số Tử Vi từ ngày giờ sinh.

    Đầu vào được kiểm trước: ngày phải có thật, năm 1800–2199, giờ 0–23,
    giới tính nam/nu — sai thì ném ``kiem_tra.LoiDauVao``.
    """
    gio, phut = gio_phut_hop_le(gio, phut)
    gioi_tinh = gioi_tinh_hop_le(gioi_tinh)
    if duong_lich:
        ngay_duong_hop_le(ngay, thang, nam)
        am = solar_to_lunar(ngay, thang, nam)
        ngay_am, thang_am, nam_am, nhuan = am.day, am.month, am.year, am.leap
    else:
        ngay_am, thang_am, nam_am = ngay_am_hop_le(ngay, thang, nam)
        nhuan = False
    # Sinh vào tháng nhuận: an Mệnh theo số tháng của tháng chính (cả tháng
    # nhuận coi như tháng đó). Một số phái chia nửa đầu về tháng trước, nửa sau
    # về tháng sau; xem SOURCES.md mục E.
    chi_gio = chi_gio_tu_gio_phut(gio, phut)
    nam_cc = can_chi_nam(nam_am)
    la_nam = gioi_tinh == "nam"
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

    # 11. Vòng Bác Sĩ (12 sao theo Lộc Tồn), chiều như vòng Tràng Sinh
    for i, ten in enumerate(VONG_BAC_SI):
        dat(ten, lt + i if thuan else lt - i, "Vòng Bác Sĩ")

    # 12. Sao đi kèm vòng Thái Tuế: Thiên Không (sau Thái Tuế), Nguyệt Đức
    #     (khởi Tỵ), Thiên Đức (khởi Dậu), cả hai đếm thuận theo chi năm.
    chi_nam = nam_cc.chi_idx
    dat("Thiên Không", chi_nam + 1, "Sát tinh")
    dat("Nguyệt Đức", 5 + chi_nam, "Phúc tinh")
    dat("Thiên Đức", 9 + chi_nam, "Phúc tinh")

    # 13. Lục sát còn lại: Không Kiếp (khởi Hợi theo giờ), Hỏa Linh
    dat("Địa Kiếp", 11 + chi_gio, "Sát tinh")
    dat("Địa Không", 11 - chi_gio, "Sát tinh")
    khoi_hoa, khoi_linh = _KHOI_HOA_LINH[chi_nam]
    if thuan:  # Dương nam, Âm nữ: Hỏa thuận, Linh nghịch
        dat("Hỏa Tinh", khoi_hoa + chi_gio, "Sát tinh")
        dat("Linh Tinh", khoi_linh - chi_gio, "Sát tinh")
    else:
        dat("Hỏa Tinh", khoi_hoa - chi_gio, "Sát tinh")
        dat("Linh Tinh", khoi_linh + chi_gio, "Sát tinh")

    # 14. Các cặp sao đối nhau qua trục Sửu — Mùi
    dat("Long Trì", 4 + chi_nam, "Quý tinh")            # khởi Thìn theo chi năm
    dat("Phượng Các", 10 - chi_nam, "Quý tinh")
    dat("Giải Thần", 10 - chi_nam, "Phúc tinh")         # đồng cung Phượng Các
    ta_phu, huu_bat = 4 + (thang_am - 1), 10 - (thang_am - 1)
    dat("Tam Thai", ta_phu + (ngay_am - 1), "Đài các")    # từ Tả Phù đếm thuận
    dat("Bát Tọa", huu_bat - (ngay_am - 1), "Đài các")    # từ Hữu Bật đếm nghịch
    van_xuong, van_khuc = 10 - chi_gio, 4 + chi_gio
    dat("Ân Quang", van_xuong + (ngay_am - 1) - 1, "Quý tinh")  # từ Xương, lùi 1
    dat("Thiên Quý", van_khuc - (ngay_am - 1) + 1, "Quý tinh")  # từ Khúc, ngược lại
    dat("Thiên Khốc", 6 - chi_nam, "Bại tinh")   # khởi Ngọ, nghịch
    dat("Thiên Hư", 6 + chi_nam, "Bại tinh")     # khởi Ngọ, thuận

    # 15. Theo cung Mệnh / Thân và chi năm
    dat("Thiên Tài", cung_menh + chi_nam, "Phụ tinh")
    dat("Thiên Thọ", cung_than + chi_nam, "Phúc tinh")

    # 16. Theo can năm sinh
    dat("Thiên Quan", _THIEN_QUAN[nam_cc.can], "Phúc tinh")
    dat("Thiên Phúc", _THIEN_PHUC[nam_cc.can], "Phúc tinh")
    dat("Lưu Hà", _LUU_HA[nam_cc.can], "Bại tinh")
    dat("Thiên Trù", _THIEN_TRU[nam_cc.can], "Phúc tinh")
    dat("Văn Tinh", lt + 3, "Văn tinh")          # Kình Dương + 2
    dat("Đường Phù", lt + 5, "Quyền tinh")       # Văn Tinh + 2
    dat("Quốc Ấn", lt + 8, "Văn tinh")           # Đường Phù + 3

    # 17. Theo tháng sinh
    dat("Thiên Hình", 9 + (thang_am - 1), "Hình tinh")   # khởi Dậu
    dat("Thiên Riêu", 1 + (thang_am - 1), "Ám tinh")     # khởi Sửu
    dat("Thiên Y", 1 + (thang_am - 1), "Phúc tinh")      # đồng cung Thiên Riêu
    dat("Thiên Giải", 8 + (thang_am - 1), "Phúc tinh")   # khởi Thân
    dat("Địa Giải", 7 + (thang_am - 1), "Phúc tinh")     # khởi Mùi

    # 18. Theo giờ sinh (quanh Văn Khúc)
    dat("Thai Phụ", van_khuc + 2, "Văn tinh")
    dat("Phong Cáo", van_khuc - 2, "Quyền tinh")

    # 19. Theo chi năm sinh
    co_than, qua_tu = _CO_QUA[chi_nam]
    dat("Cô Thần", co_than, "Ám tinh")
    dat("Quả Tú", qua_tu, "Ám tinh")
    ma = _TAM_HOP_MA[chi_nam]
    dat("Hoa Cái", ma + 2, "Phụ tinh")
    dat("Kiếp Sát", ma + 3, "Sát tinh")
    dat("Phá Toái", _PHA_TOAI[chi_nam], "Bại tinh")
    # Đẩu Quân: từ cung Thái Tuế kể là tháng Giêng đếm nghịch đến tháng sinh,
    # rồi từ đó kể là giờ Tý đếm thuận đến giờ sinh.
    dat("Đẩu Quân", chi_nam - (thang_am - 1) + chi_gio, "Phúc tinh")

    # 20. Sao cố định và theo cung chức
    dat("Thiên La", 4, "Bại tinh")               # luôn ở Thìn
    dat("Địa Võng", 10, "Bại tinh")              # luôn ở Tuất
    dat("Thiên Thương", cung_menh + 5, "Bại tinh")   # cung Nô Bộc
    dat("Thiên Sứ", cung_menh + 7, "Bại tinh")       # cung Tật Ách

    # 21. Tuần, Triệt (không phải sao, đánh dấu lên cung)
    cuoi_tuan = (chi_nam + 9 - THIEN_CAN.index(nam_cc.can)) % 12
    tuan = {(cuoi_tuan + 1) % 12, (cuoi_tuan + 2) % 12}
    triet = {_TRIET[nam_cc.can], _TRIET[nam_cc.can] + 1}

    # 22. Đại hạn 10 năm
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
            "tuan": i in tuan,
            "triet": i in triet,
            "dai_han": dai_han[i],
            "sao": sorted(sao_o_cung[i], key=lambda s: s["nhom"] != "Chính tinh"),
        })

    return {
        "am_lich": {"ngay": ngay_am, "thang": thang_am, "nam": nam_am,
                    "nhuan": nhuan, "gio": DIA_CHI[chi_gio]},
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
        "tuan": [DIA_CHI[i] for i in sorted(tuan)],
        "triet": [DIA_CHI[i] for i in sorted(triet)],
        "cac_cung": cung_list,
    }


def chinh_tinh_cung_menh(la_so: dict) -> list[str]:
    """Danh sách chính tinh tại cung Mệnh (rỗng nghĩa là Mệnh vô chính diệu)."""
    cung = next(c for c in la_so["cac_cung"] if c["ten_cung"] == "Mệnh")
    return [s["ten"] for s in cung["sao"] if s["nhom"] == "Chính tinh"]
