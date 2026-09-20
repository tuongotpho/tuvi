# -*- coding: utf-8 -*-
"""Can Chi, Ngũ hành nạp âm, tiết khí — nền tảng cho mọi phép luận đoán."""
from __future__ import annotations

from typing import NamedTuple

from .amlich import (PI, get_sun_longitude, jd_from_date, solar_to_lunar,
                     sun_longitude)

THIEN_CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu",
             "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]

DIA_CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
           "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

CON_GIAP = ["Chuột", "Trâu", "Hổ", "Mèo", "Rồng", "Rắn",
            "Ngựa", "Dê", "Khỉ", "Gà", "Chó", "Lợn"]

# Ngũ hành của Thiên Can (theo cặp: Giáp Ất Mộc, Bính Đinh Hỏa, ...)
HANH_CAN = ["Mộc", "Mộc", "Hỏa", "Hỏa", "Thổ",
            "Thổ", "Kim", "Kim", "Thủy", "Thủy"]

# Ngũ hành bản khí của Địa Chi
HANH_CHI = ["Thủy", "Thổ", "Mộc", "Mộc", "Thổ", "Hỏa",
            "Hỏa", "Thổ", "Kim", "Kim", "Thổ", "Thủy"]

AM_DUONG_CAN = [1, -1, 1, -1, 1, -1, 1, -1, 1, -1]  # 1 = Dương, -1 = Âm

# 30 hành nạp âm của Lục thập hoa giáp, theo thứ tự Giáp Tý -> Quý Hợi.
NAP_AM_60 = [
    "Hải Trung Kim", "Hải Trung Kim", "Lư Trung Hỏa", "Lư Trung Hỏa",
    "Đại Lâm Mộc", "Đại Lâm Mộc", "Lộ Bàng Thổ", "Lộ Bàng Thổ",
    "Kiếm Phong Kim", "Kiếm Phong Kim", "Sơn Đầu Hỏa", "Sơn Đầu Hỏa",
    "Giản Hạ Thủy", "Giản Hạ Thủy", "Thành Đầu Thổ", "Thành Đầu Thổ",
    "Bạch Lạp Kim", "Bạch Lạp Kim", "Dương Liễu Mộc", "Dương Liễu Mộc",
    "Tuyền Trung Thủy", "Tuyền Trung Thủy", "Ốc Thượng Thổ", "Ốc Thượng Thổ",
    "Tích Lịch Hỏa", "Tích Lịch Hỏa", "Tùng Bách Mộc", "Tùng Bách Mộc",
    "Trường Lưu Thủy", "Trường Lưu Thủy", "Sa Trung Kim", "Sa Trung Kim",
    "Sơn Hạ Hỏa", "Sơn Hạ Hỏa", "Bình Địa Mộc", "Bình Địa Mộc",
    "Bích Thượng Thổ", "Bích Thượng Thổ", "Kim Bạch Kim", "Kim Bạch Kim",
    "Phúc Đăng Hỏa", "Phúc Đăng Hỏa", "Thiên Hà Thủy", "Thiên Hà Thủy",
    "Đại Trạch Thổ", "Đại Trạch Thổ", "Thoa Xuyến Kim", "Thoa Xuyến Kim",
    "Tang Đố Mộc", "Tang Đố Mộc", "Đại Khê Thủy", "Đại Khê Thủy",
    "Sa Trung Thổ", "Sa Trung Thổ", "Thiên Thượng Hỏa", "Thiên Thượng Hỏa",
    "Thạch Lựu Mộc", "Thạch Lựu Mộc", "Đại Hải Thủy", "Đại Hải Thủy",
]

TIET_KHI = [
    "Xuân phân", "Thanh minh", "Cốc vũ", "Lập hạ", "Tiểu mãn", "Mang chủng",
    "Hạ chí", "Tiểu thử", "Đại thử", "Lập thu", "Xử thử", "Bạch lộ",
    "Thu phân", "Hàn lộ", "Sương giáng", "Lập đông", "Tiểu tuyết", "Đại tuyết",
    "Đông chí", "Tiểu hàn", "Đại hàn", "Lập xuân", "Vũ thủy", "Kinh trập",
]


class CanChi(NamedTuple):
    can: str
    chi: str
    can_idx: int
    chi_idx: int

    @property
    def ten(self) -> str:
        return f"{self.can} {self.chi}"

    @property
    def hoa_giap_idx(self) -> int:
        """Vị trí 0..59 trong Lục thập hoa giáp."""
        return _hoa_giap_index(self.can_idx, self.chi_idx)

    @property
    def nap_am(self) -> str:
        return NAP_AM_60[self.hoa_giap_idx]

    @property
    def nap_am_hanh(self) -> str:
        return self.nap_am.split()[-1]


def _hoa_giap_index(can_idx: int, chi_idx: int) -> int:
    """Vị trí 0..59 của cặp Can Chi trong Lục thập hoa giáp."""
    for i in range(60):
        if i % 10 == can_idx and i % 12 == chi_idx:
            return i
    raise ValueError("Cặp Can Chi không hợp lệ")


def can_chi_nam(lunar_year: int) -> CanChi:
    """Can Chi của năm âm lịch."""
    can_idx = (lunar_year + 6) % 10
    chi_idx = (lunar_year + 8) % 12
    return CanChi(THIEN_CAN[can_idx], DIA_CHI[chi_idx], can_idx, chi_idx)


def can_chi_thang(lunar_year: int, lunar_month: int) -> CanChi:
    """Can Chi của tháng âm lịch (tháng Giêng là tháng Dần)."""
    chi_idx = (lunar_month + 1) % 12
    can_nam = (lunar_year + 6) % 10
    # Ngũ hổ độn: năm Giáp/Kỷ -> tháng Giêng là Bính Dần ...
    can_idx = ((can_nam % 5) * 2 + 2 + (lunar_month - 1)) % 10
    return CanChi(THIEN_CAN[can_idx], DIA_CHI[chi_idx], can_idx, chi_idx)


def can_chi_ngay(jd: int) -> CanChi:
    """Can Chi của ngày theo số ngày Julius."""
    can_idx = (jd + 9) % 10
    chi_idx = (jd + 1) % 12
    return CanChi(THIEN_CAN[can_idx], DIA_CHI[chi_idx], can_idx, chi_idx)


def can_chi_gio(can_ngay_idx: int, chi_gio_idx: int) -> CanChi:
    """Can Chi của giờ (Ngũ thử độn: ngày Giáp/Kỷ khởi giờ Tý là Giáp Tý)."""
    can_idx = ((can_ngay_idx % 5) * 2 + chi_gio_idx) % 10
    return CanChi(THIEN_CAN[can_idx], DIA_CHI[chi_gio_idx], can_idx, chi_gio_idx)


def chi_gio_tu_gio_phut(hour: int, minute: int = 0) -> int:
    """Giờ đồng hồ -> chỉ số địa chi của canh giờ (23:00-00:59 là giờ Tý)."""
    return int(((hour * 60 + minute + 60) % 1440) // 120)


def nap_am(can_idx: int, chi_idx: int) -> str:
    return NAP_AM_60[_hoa_giap_index(can_idx, chi_idx)]


def luc_thap_hoa_giap() -> list[dict]:
    """Bảng Lục thập hoa giáp đầy đủ (60 cặp Can Chi + nạp âm)."""
    out = []
    for i in range(60):
        can_idx, chi_idx = i % 10, i % 12
        out.append({
            "stt": i + 1,
            "can": THIEN_CAN[can_idx],
            "chi": DIA_CHI[chi_idx],
            "ten": f"{THIEN_CAN[can_idx]} {DIA_CHI[chi_idx]}",
            "nap_am": NAP_AM_60[i],
            "hanh": NAP_AM_60[i].split()[-1],
            "am_duong": "Dương" if AM_DUONG_CAN[can_idx] == 1 else "Âm",
            "con_giap": CON_GIAP[chi_idx],
        })
    return out


def tiet_khi_cua_ngay(jd: int) -> str:
    """Tiết khí đang có hiệu lực trong ngày (theo kinh độ mặt trời lúc 0h)."""
    deg = sun_longitude(jd - 0.5 - 7 / 24) / PI * 180
    return TIET_KHI[int(deg // 15) % 24]


def chi_thang_theo_tiet(jd: int) -> int:
    """Nguyệt kiến (địa chi của tháng tiết lệnh) — mốc để tính 12 Trực.

    Tháng tiết bắt đầu ở các tiết chính: Lập xuân -> tháng Dần, Kinh trập ->
    tháng Mão, Thanh minh -> tháng Thìn, ...
    """
    deg = sun_longitude(jd - 0.5 - 7 / 24) / PI * 180
    # 315 độ (Lập xuân) ứng với tháng Dần (chi index 2)
    return int(((deg - 315) % 360) // 30 + 2) % 12


def tuoi_mu(lunar_year_sinh: int, lunar_year_xem: int) -> int:
    """Tuổi mụ (tuổi âm) dùng trong hầu hết các phép xem hạn."""
    return lunar_year_xem - lunar_year_sinh + 1


def thong_tin_ngay(dd: int, mm: int, yy: int) -> dict:
    """Gói dữ liệu Can Chi đầy đủ của một ngày dương lịch."""
    am = solar_to_lunar(dd, mm, yy)
    ngay = can_chi_ngay(am.jd)
    thang = can_chi_thang(am.year, am.month)
    nam = can_chi_nam(am.year)
    return {
        "duong_lich": f"{dd:02d}/{mm:02d}/{yy}",
        "am_lich": f"{am.day:02d}/{am.month:02d}/{am.year}" + (" (nhuận)" if am.leap else ""),
        "jd": am.jd,
        "ngay_can_chi": ngay.ten,
        "thang_can_chi": thang.ten,
        "nam_can_chi": nam.ten,
        "con_giap_nam": CON_GIAP[nam.chi_idx],
        "nap_am_nam": nam.nap_am,
        "tiet_khi": tiet_khi_cua_ngay(am.jd),
    }
