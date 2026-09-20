# -*- coding: utf-8 -*-
"""Chuyển đổi Âm lịch <-> Dương lịch theo thuật toán của Hồ Ngọc Đức.

Thuật toán gốc: Hồ Ngọc Đức, "Âm lịch Việt Nam" (tính theo múi giờ UTC+7),
được công bố công khai và cài đặt lại trong rất nhiều dự án mã nguồn mở.
Xem SOURCES.md mục [S-01].

Mọi hàm ở đây thuần tính toán, không phụ thuộc thư viện ngoài.
"""
from __future__ import annotations

import math
from typing import NamedTuple

PI = math.pi
TIMEZONE_VN = 7.0


class LunarDate(NamedTuple):
    day: int
    month: int
    year: int
    leap: bool
    jd: int


class SolarDate(NamedTuple):
    day: int
    month: int
    year: int


def jd_from_date(dd: int, mm: int, yy: int) -> int:
    """Số ngày Julius của ngày dương lịch dd/mm/yy (lịch Gregory/Julius)."""
    a = (14 - mm) // 12
    y = yy + 4800 - a
    m = mm + 12 * a - 3
    jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    if jd < 2299161:
        jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
    return jd


def jd_to_date(jd: int) -> SolarDate:
    """Ngược lại của :func:`jd_from_date`."""
    if jd > 2299160:  # sau 05/10/1582, lịch Gregory
        a = jd + 32044
        b = (4 * a + 3) // 146097
        c = a - (b * 146097) // 4
    else:
        b = 0
        c = jd + 32082
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = b * 100 + d - 4800 + m // 10
    return SolarDate(day, month, year)


def new_moon(k: int) -> float:
    """Thời điểm Sóc thứ k (điểm Sóc thứ 0 là 1/1/1900), tính theo ngày Julius."""
    T = k / 1236.85
    T2 = T * T
    T3 = T2 * T
    dr = PI / 180
    Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    Jd1 += 0.00033 * math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)
    M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
    C1 = (0.1734 - 0.000393 * T) * math.sin(M * dr) + 0.0021 * math.sin(2 * dr * M)
    C1 = C1 - 0.4068 * math.sin(Mpr * dr) + 0.0161 * math.sin(dr * 2 * Mpr)
    C1 = C1 - 0.0004 * math.sin(dr * 3 * Mpr)
    C1 = C1 + 0.0104 * math.sin(dr * 2 * F) - 0.0051 * math.sin(dr * (M + Mpr))
    C1 = C1 - 0.0074 * math.sin(dr * (M - Mpr)) + 0.0004 * math.sin(dr * (2 * F + M))
    C1 = C1 - 0.0004 * math.sin(dr * (2 * F - M)) - 0.0006 * math.sin(dr * (2 * F + Mpr))
    C1 = C1 + 0.0010 * math.sin(dr * (2 * F - Mpr)) + 0.0005 * math.sin(dr * (2 * Mpr + M))
    if T < -11:
        deltat = (0.001 + 0.000839 * T + 0.0002261 * T2
                  - 0.00000845 * T3 - 0.000000081 * T * T3)
    else:
        deltat = -0.000278 + 0.000265 * T + 0.000262 * T2
    return Jd1 + C1 - deltat


def sun_longitude(jdn: float) -> float:
    """Kinh độ mặt trời (radian) tại thời điểm jdn (ngày Julius)."""
    T = (jdn - 2451545.0) / 36525
    T2 = T * T
    dr = PI / 180
    M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
    L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
    DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * math.sin(dr * M)
    DL += (0.019993 - 0.000101 * T) * math.sin(dr * 2 * M) + 0.000290 * math.sin(dr * 3 * M)
    L = L0 + DL
    L = L * dr
    L = L - PI * 2 * int(L / (PI * 2))
    return L


def get_sun_longitude(day_number: int, time_zone: float = TIMEZONE_VN) -> int:
    """Trả về 0..11: cung hoàng đạo (mỗi cung 30 độ) của mặt trời lúc 0h."""
    return int(sun_longitude(day_number - 0.5 - time_zone / 24) / PI * 6)


def get_new_moon_day(k: int, time_zone: float = TIMEZONE_VN) -> int:
    """Ngày (số Julius) chứa điểm Sóc thứ k."""
    return int(new_moon(k) + 0.5 + time_zone / 24)


def get_lunar_month_11(yy: int, time_zone: float = TIMEZONE_VN) -> int:
    off = jd_from_date(31, 12, yy) - 2415021
    k = int(off / 29.530588853)
    nm = get_new_moon_day(k, time_zone)
    sun_long = get_sun_longitude(nm, time_zone)
    if sun_long >= 9:
        nm = get_new_moon_day(k - 1, time_zone)
    return nm


def get_leap_month_offset(a11: int, time_zone: float = TIMEZONE_VN) -> int:
    k = int((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    last = 0
    i = 1
    arc = get_sun_longitude(get_new_moon_day(k + i, time_zone), time_zone)
    while True:
        last = arc
        i += 1
        arc = get_sun_longitude(get_new_moon_day(k + i, time_zone), time_zone)
        if not (arc != last and i < 14):
            break
    return i - 1


def solar_to_lunar(dd: int, mm: int, yy: int, time_zone: float = TIMEZONE_VN) -> LunarDate:
    """Đổi ngày dương lịch sang âm lịch Việt Nam."""
    day_number = jd_from_date(dd, mm, yy)
    k = int((day_number - 2415021.076998695) / 29.530588853)
    month_start = get_new_moon_day(k + 1, time_zone)
    if month_start > day_number:
        month_start = get_new_moon_day(k, time_zone)
    a11 = get_lunar_month_11(yy, time_zone)
    b11 = a11
    if a11 >= month_start:
        lunar_year = yy
        a11 = get_lunar_month_11(yy - 1, time_zone)
    else:
        lunar_year = yy + 1
        b11 = get_lunar_month_11(yy + 1, time_zone)
    lunar_day = day_number - month_start + 1
    diff = int((month_start - a11) / 29)
    lunar_leap = False
    lunar_month = diff + 11
    if b11 - a11 > 365:
        leap_month_diff = get_leap_month_offset(a11, time_zone)
        if diff >= leap_month_diff:
            lunar_month = diff + 10
            if diff == leap_month_diff:
                lunar_leap = True
    if lunar_month > 12:
        lunar_month -= 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1
    return LunarDate(lunar_day, lunar_month, lunar_year, lunar_leap, day_number)


def lunar_to_solar(lunar_day: int, lunar_month: int, lunar_year: int,
                   lunar_leap: bool = False,
                   time_zone: float = TIMEZONE_VN) -> SolarDate:
    """Đổi ngày âm lịch Việt Nam sang dương lịch."""
    if lunar_month < 11:
        a11 = get_lunar_month_11(lunar_year - 1, time_zone)
        b11 = get_lunar_month_11(lunar_year, time_zone)
    else:
        a11 = get_lunar_month_11(lunar_year, time_zone)
        b11 = get_lunar_month_11(lunar_year + 1, time_zone)
    k = int(0.5 + (a11 - 2415021.076998695) / 29.530588853)
    off = lunar_month - 11
    if off < 0:
        off += 12
    if b11 - a11 > 365:
        leap_off = get_leap_month_offset(a11, time_zone)
        leap_month = leap_off - 2
        if leap_month < 0:
            leap_month += 12
        if lunar_leap and lunar_month != leap_month:
            raise ValueError("Tháng nhuận không hợp lệ cho năm âm lịch này")
        if lunar_leap or off >= leap_off:
            off += 1
    month_start = get_new_moon_day(k + off, time_zone)
    return jd_to_date(month_start + lunar_day - 1)
