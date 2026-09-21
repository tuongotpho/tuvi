# -*- coding: utf-8 -*-
"""Bộ máy tính toán cho cơ sở dữ liệu tử vi — phong thủy — hạn — xem ngày.

Các mô-đun chính:
    amlich      đổi âm lịch <-> dương lịch (thuật toán Hồ Ngọc Đức)
    canchi      can chi, nạp âm, lục thập hoa giáp, tiết khí
    ngay_gio    12 Trực, nhị thập bát tú, hoàng đạo, ngày kiêng
    chon_ngay   chọn ngày theo tuổi: lọc ngày xung, chấm điểm theo việc
    han         sao hạn cửu diệu, tam tai, Kim Lâu, Hoang Ốc, Thái Tuế
    phong_thuy  cung phi bát trạch, du niên tám hướng, cửu cung phi tinh
    la_so       lập lá số tử vi rút gọn
    luan_giai   luận giải lá số: tổng quan, tứ hóa, 12 cung, đại hạn
    store       nạp dữ liệu JSON trong thư mục data/
"""
from . import (amlich, canchi, chon_ngay, han, la_so, luan_giai,  # noqa: F401
               ngay_gio, phong_thuy, store)

__version__ = "1.0.0"

__all__ = ["amlich", "canchi", "chon_ngay", "han", "la_so", "luan_giai",
           "ngay_gio", "phong_thuy", "store"]
