# -*- coding: utf-8 -*-
"""Vị trí biểu kiến của mặt trời và thời khắc giao 24 tiết khí.

Tiết khí đổi khi kinh độ biểu kiến của mặt trời qua một bội số của 15°. Hàm
``sun_longitude`` trong ``amlich.py`` là công thức gần đúng của thuật toán âm lịch
Hồ Ngọc Đức (sai vài phút, không tính quang sai và chương động) — đủ để xếp
tháng âm lịch nên KHÔNG sửa ở đó, nhưng không đủ để biết tiết giao trước hay sau
nửa đêm. Module này tính chính xác tới cỡ giây:

- Kinh độ hình học: lý thuyết VSOP87D (Bretagnon & Francou 1988), hệ số trong
  ``data/lich/vsop87d_trai_dat.json`` (chép từ thư viện astronomia, MIT).
- Đổi sang hệ FK5, cộng chương động (công thức rút gọn của Meeus, sai ≤ 0,5″)
  và quang sai −20,4898″/R — Meeus, *Astronomical Algorithms*, chương 22, 25, 32.
- Thời gian thiên văn TT = UT + ΔT (đa thức Espenak & Meeus, NASA).

Kiểm thử đối chiếu với thời khắc tiết khí của lunar-javascript (thuật toán Thọ
Tinh vạn niên lịch) cho 1900–2100 ở ``tests/test_xem_ngay.py``.
"""
from __future__ import annotations

import math
from functools import lru_cache

from .store import load

TIMEZONE_VN = 7
J2000 = 2451545.0

# 24 tiết khí, bắt đầu từ Xuân phân (kinh độ 0°), mỗi tiết 15°.
TEN_TIET = ["Xuân phân", "Thanh minh", "Cốc vũ", "Lập hạ", "Tiểu mãn", "Mang chủng",
            "Hạ chí", "Tiểu thử", "Đại thử", "Lập thu", "Xử thử", "Bạch lộ",
            "Thu phân", "Hàn lộ", "Sương giáng", "Lập đông", "Tiểu tuyết", "Đại tuyết",
            "Đông chí", "Tiểu hàn", "Đại hàn", "Lập xuân", "Vũ thủy", "Kinh trập"]


def delta_t(nam: float) -> float:
    """ΔT = TT − UT (giây), đa thức Espenak & Meeus (NASA) cho 1800–2150."""
    y = nam
    if y < 1860:
        t = y - 1800
        return (13.72 - 0.332447 * t + 0.0068612 * t**2 + 0.0041116 * t**3
                - 0.00037436 * t**4 + 0.0000121272 * t**5 - 0.0000001699 * t**6
                + 0.000000000875 * t**7)
    if y < 1900:
        t = y - 1860
        return (7.62 + 0.5737 * t - 0.251754 * t**2 + 0.01680668 * t**3
                - 0.0004473624 * t**4 + t**5 / 233174)
    if y < 1920:
        t = y - 1900
        return -2.79 + 1.494119 * t - 0.0598939 * t**2 + 0.0061966 * t**3 - 0.000197 * t**4
    if y < 1941:
        t = y - 1920
        return 21.20 + 0.84493 * t - 0.076100 * t**2 + 0.0020936 * t**3
    if y < 1961:
        t = y - 1950
        return 29.07 + 0.407 * t - t**2 / 233 + t**3 / 2547
    if y < 1986:
        t = y - 1975
        return 45.45 + 1.067 * t - t**2 / 260 - t**3 / 718
    if y < 2005:
        t = y - 2000
        return (63.86 + 0.3345 * t - 0.060374 * t**2 + 0.0017275 * t**3
                + 0.000651814 * t**4 + 0.00002373599 * t**5)
    if y < 2050:
        t = y - 2000
        return 62.92 + 0.32217 * t + 0.005589 * t**2
    if y < 2150:
        return -20 + 32 * ((y - 1820) / 100) ** 2 - 0.5628 * (2150 - y)
    return -20 + 32 * ((y - 1820) / 100) ** 2


@lru_cache(maxsize=1)
def _vsop() -> tuple:
    d = load("lich/vsop87d_trai_dat")
    return (tuple(tuple(map(tuple, d["L"][str(i)])) for i in range(6)),
            tuple(tuple(map(tuple, d["R"][str(i)])) for i in range(6)))


def _chuoi(bac: tuple, tau: float) -> float:
    return sum(sum(a * math.cos(b + c * tau) for a, b, c in hang) * tau**i
               for i, hang in enumerate(bac))


def kinh_do_mat_troi(jd_ut: float) -> float:
    """Kinh độ biểu kiến của mặt trời (độ, 0–360) tại thời điểm ``jd_ut`` (UT)."""
    jde = jd_ut + delta_t(2000 + (jd_ut - J2000) / 365.25) / 86400
    tau = (jde - J2000) / 365250
    T = tau * 10
    L, R = _vsop()
    l_trai_dat = _chuoi(L, tau)
    r = _chuoi(R, tau)
    theta = math.degrees(l_trai_dat) + 180            # địa tâm, hình học
    theta -= 0.09033 / 3600                            # đổi sang FK5 (Meeus 32.3)
    om = math.radians(125.04452 - 1934.136261 * T)     # chương động rút gọn (Meeus 22)
    l_tb = math.radians(280.4665 + 36000.7698 * T)
    l_mt = math.radians(218.3165 + 481267.8813 * T)
    dpsi = (-17.20 * math.sin(om) - 1.32 * math.sin(2 * l_tb)
            - 0.23 * math.sin(2 * l_mt) + 0.21 * math.sin(2 * om))
    theta += dpsi / 3600 - 20.4898 / 3600 / r          # chương động + quang sai
    return theta % 360


def thoi_khac_tiet(jd_gan: float, kinh_do: float) -> float:
    """Thời khắc (JD, UT) mặt trời tới ``kinh_do`` gần ``jd_gan`` nhất."""
    jd = jd_gan
    for _ in range(20):
        lech = (kinh_do - kinh_do_mat_troi(jd) + 180) % 360 - 180
        jd += lech * 365.2422 / 360
        if abs(lech) < 1e-7:
            break
    return jd


@lru_cache(maxsize=64)
def moc_tiet_nam(nam: int) -> tuple[tuple[float, int], ...]:
    """Các mốc giao tiết (JD UT, chỉ số tiết) từ cuối năm ``nam - 1`` tới đầu
    năm ``nam + 1`` — tính một lần mỗi năm rồi dùng lại."""
    from .amlich import jd_from_date
    jd = jd_from_date(1, 12, nam - 1)
    muc = int(kinh_do_mat_troi(jd) // 15) + 1
    ra = []
    for _ in range(28):
        jd = thoi_khac_tiet(jd + 15.2 if ra else jd, (muc % 24) * 15)
        ra.append((jd, muc % 24))
        muc += 1
    return tuple(ra)


def muc_tiet_cuoi_ngay(jd_ngay: int, tz: float = TIMEZONE_VN) -> int:
    """Chỉ số tiết (0 = Xuân phân) có hiệu lực của ngày ``jd_ngay``.

    Ngày có thời khắc giao tiết thuộc về tiết mới — tức là lấy tiết đang có
    hiệu lực lúc 24 giờ cuối ngày theo giờ Việt Nam.
    """
    return _moc_truoc(jd_ngay + 0.5 - tz / 24)[1]


def _moc_truoc(thoi_diem: float) -> tuple[float, int]:
    """Mốc giao tiết gần nhất không muộn hơn ``thoi_diem`` (JD UT)."""
    from .amlich import jd_to_date
    nam = jd_to_date(math.floor(thoi_diem + 0.5))[2]
    moc = [m for m in moc_tiet_nam(nam) if m[0] <= thoi_diem]
    return moc[-1]


def jd_sang_gio_vn(jd_ut: float, tz: float = TIMEZONE_VN) -> tuple[int, int, int, int, int]:
    """JD (UT) -> (ngày, tháng, năm, giờ, phút) theo giờ Việt Nam."""
    from .amlich import jd_to_date
    x = jd_ut + 0.5 + tz / 24
    ngay_jd = math.floor(x)
    phut = round((x - ngay_jd) * 1440)
    if phut == 1440:
        ngay_jd, phut = ngay_jd + 1, 0
    d, m, y = jd_to_date(ngay_jd)
    return d, m, y, phut // 60, phut % 60


def tiet_quanh_ngay(jd_ngay: int) -> dict:
    """Tiết đang có hiệu lực, thời khắc nó bắt đầu, và tiết kế tiếp."""
    bat_dau, muc = _moc_truoc(jd_ngay + 0.5 - TIMEZONE_VN / 24)
    ke = (muc + 1) % 24
    ke_tiep = thoi_khac_tiet(bat_dau + 15.2, ke * 15)
    return {"muc": muc, "ten": TEN_TIET[muc], "bat_dau": jd_sang_gio_vn(bat_dau),
            "ke_tiep": TEN_TIET[ke], "ke_tiep_bat_dau": jd_sang_gio_vn(ke_tiep)}
