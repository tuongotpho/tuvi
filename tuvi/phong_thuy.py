# -*- coding: utf-8 -*-
"""Phong thủy: cung phi Bát trạch, du niên tám hướng, phi tinh năm."""
from __future__ import annotations

from .canchi import can_chi_nam
from .store import load

SO_CUNG = {1: "Khảm", 2: "Khôn", 3: "Chấn", 4: "Tốn",
           6: "Càn", 7: "Đoài", 8: "Cấn", 9: "Ly"}

HUONG_8 = ["Bắc", "Đông Bắc", "Đông", "Đông Nam",
           "Nam", "Tây Nam", "Tây", "Tây Bắc"]


def _rut_gon(n: int) -> int:
    """Cộng dồn các chữ số cho tới khi còn một chữ số."""
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n


def cung_phi(nam_sinh_am: int, gioi_tinh: str) -> dict:
    """Cung phi Bát trạch từ năm sinh âm lịch và giới tính."""
    la_nam = gioi_tinh.lower().startswith("nam")
    a = _rut_gon(sum(int(c) for c in f"{nam_sinh_am % 100:02d}"))
    if nam_sinh_am < 2000:
        so = (10 - a) if la_nam else (5 + a)
    else:
        so = (9 - a) if la_nam else (6 + a)
    so = _rut_gon(so) if so > 9 else so
    if so == 0:
        so = 9
    if so == 5:
        ten = "Khôn" if la_nam else "Cấn"
        so_hien_thi = 2 if la_nam else 8
    else:
        ten = SO_CUNG[so]
        so_hien_thi = so
    ds = load("phong_thuy/bat_trach")
    chi_tiet = next(c for c in ds["cung"] if c["ten"] == ten)
    return {
        "nam_sinh_am_lich": nam_sinh_am,
        "nam_can_chi": can_chi_nam(nam_sinh_am).ten,
        "menh_nap_am": can_chi_nam(nam_sinh_am).nap_am,
        "hanh_nap_am": can_chi_nam(nam_sinh_am).nap_am_hanh,
        "gioi_tinh": "Nam" if la_nam else "Nữ",
        "cung_phi": ten, "so_cung": so_hien_thi,
        "nhom": chi_tiet["nhom"], "hanh_cung": chi_tiet["hanh"],
        "huong_cung": chi_tiet["huong"], "y_nghia": chi_tiet["y_nghia"],
    }


def du_nien(cung: str) -> dict[str, str]:
    """Bảng tám hướng -> du niên của một cung phi."""
    ds = load("phong_thuy/bat_trach")
    return next(c for c in ds["cung"] if c["ten"] == cung)["du_nien"]


def huong_theo_cung(cung: str) -> dict:
    """Phân loại tám hướng thành tốt / xấu kèm giải nghĩa."""
    ds = load("phong_thuy/bat_trach")
    dn_info = {d["ten"]: d for d in ds["du_nien"]}
    bang = du_nien(cung)
    tot, xau = [], []
    for huong, ten in bang.items():
        row = {"huong": huong, "du_nien": ten, **dn_info[ten]}
        (tot if dn_info[ten]["tinh_chat"] == "tốt" else xau).append(row)
    tot.sort(key=lambda r: r["xep_hang"])
    xau.sort(key=lambda r: -r["xep_hang"])
    return {"cung_phi": cung, "huong_tot": tot, "huong_xau": xau}


def hop_huong_nha(cung: str, huong_nha: str) -> dict:
    """Đánh giá một hướng nhà cụ thể với cung phi của gia chủ."""
    ds = load("phong_thuy/bat_trach")
    dn_info = {d["ten"]: d for d in ds["du_nien"]}
    ten = du_nien(cung)[huong_nha]
    d = dn_info[ten]
    return {"cung_phi": cung, "huong_nha": huong_nha, "du_nien": ten,
            "tinh_chat": d["tinh_chat"], "xep_hang": d["xep_hang"],
            "y_nghia": d["y_nghia"],
            "ket_luan": (f"Hướng {huong_nha} là hướng {ten} — "
                         + ("hướng tốt, nên dùng." if d["tinh_chat"] == "tốt"
                            else "hướng xấu, nên tránh hoặc hóa giải."))}


def phi_tinh_nam(nam: int) -> dict:
    """Sao nhập trung cung và bản đồ cửu cung phi tinh của một năm."""
    ds = load("phong_thuy/cuu_cung_phi_tinh")
    n = _rut_gon(sum(int(c) for c in str(nam)))
    trung_cung = 11 - n
    if trung_cung > 9:
        trung_cung -= 9
    lac_thu = ds["lac_thu"]
    sao_info = {s["so"]: s for s in ds["sao"]}
    # Phi tinh bay theo chiều thuận của Lạc thư: mỗi cung = số Lạc thư + độ lệch.
    lech = trung_cung - 5
    bando = {}
    for huong, so_lac_thu in lac_thu.items():
        so = (so_lac_thu + lech - 1) % 9 + 1
        bando[huong] = {"sao": so, **{k: v for k, v in sao_info[so].items()
                                      if k != "so"}}
    return {"nam": nam, "sao_nhap_trung_cung": trung_cung,
            "ten_sao_trung_cung": sao_info[trung_cung]["ten"],
            "van": ds["van_hien_tai"], "ban_do": bando,
            "luu_y": "Năm phi tinh đổi từ tiết Lập Xuân, không phải mùng 1 Tết."}


def ho_so_phong_thuy(nam_sinh_am: int, gioi_tinh: str,
                     huong_nha: str | None = None) -> dict:
    """Hồ sơ phong thủy cá nhân — đầu vào chuẩn để dựng content tư vấn."""
    cp = cung_phi(nam_sinh_am, gioi_tinh)
    mau = load("phong_thuy/mau_sac_vat_pham")["theo_hanh"][cp["hanh_nap_am"]]
    ho_so = {**cp, **huong_theo_cung(cp["cung_phi"]),
             "mau_sac_vat_pham": mau,
             "bo_tri_khong_gian": load("phong_thuy/bo_tri_khong_gian")}
    if huong_nha:
        ho_so["danh_gia_huong_nha"] = hop_huong_nha(cp["cung_phi"], huong_nha)
    return ho_so
