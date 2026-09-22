# -*- coding: utf-8 -*-
"""Bộ máy tính toán cho cơ sở dữ liệu tử vi — phong thủy — hạn — xem ngày.

Các mô-đun chính:
    amlich      đổi âm lịch <-> dương lịch (thuật toán Hồ Ngọc Đức)
    canchi      can chi, nạp âm, lục thập hoa giáp, tiết khí
    ngay_gio    12 Trực, nhị thập bát tú, hoàng đạo, ngày kiêng
    chon_ngay   chọn ngày theo tuổi: lọc ngày xung, chấm điểm theo việc
    han         sao hạn cửu diệu, tam tai, Kim Lâu, Hoang Ốc, Thái Tuế
    phong_thuy  cung phi bát trạch, du niên tám hướng, cửu cung phi tinh
    la_so       lập lá số tử vi đủ 109 sao, Tuần — Triệt
    kiem_tra    kiểm tra đầu vào, ngoại lệ LoiDauVao
    luan_giai   luận giải lá số: tổng quan, tứ hóa, 12 cung, đại hạn
    luu_nien    xem một năm: tiểu hạn, đại hạn đang đi, sao lưu
    ai_luan_giai luận giải bằng Gemini trên nền số liệu đã tính (cần GEMINI_API_KEY)
    store       nạp dữ liệu JSON trong thư mục data/
"""
from . import (ai_luan_giai, amlich, canchi, chon_ngay, han, kiem_tra,  # noqa: F401
               la_so, luan_giai, luu_nien, ngay_gio, phong_thuy, store)

__version__ = "2.0.0"  # 2.x: âm lịch sửa lỗi floor, đủ 109 sao, luận giải, 92 cách cục

__all__ = ["ai_luan_giai", "amlich", "canchi", "chon_ngay", "han", "kiem_tra",
           "la_so", "luan_giai", "luu_nien", "ngay_gio", "phong_thuy", "store"]
