# -*- coding: utf-8 -*-
"""Xem hạn: sao hạn cửu diệu, Tam tai, Kim Lâu, Hoang Ốc, Thái Tuế."""
from __future__ import annotations

from .canchi import DIA_CHI, can_chi_nam, tuoi_mu
from .store import load

HOANG_OC_CUNG = ["Nhất Cát", "Nhì Nghi", "Tam Địa Sát",
                 "Tứ Tấn Tài", "Ngũ Thọ Tử", "Lục Hoang Ốc"]

_LUC_HAI = {"Tý": "Mùi", "Mùi": "Tý", "Sửu": "Ngọ", "Ngọ": "Sửu",
            "Dần": "Tỵ", "Tỵ": "Dần", "Mão": "Thìn", "Thìn": "Mão",
            "Thân": "Hợi", "Hợi": "Thân", "Dậu": "Tuất", "Tuất": "Dậu"}
_LUC_PHA = {"Tý": "Dậu", "Dậu": "Tý", "Ngọ": "Mão", "Mão": "Ngọ",
            "Thân": "Tỵ", "Tỵ": "Thân", "Dần": "Hợi", "Hợi": "Dần",
            "Thìn": "Sửu", "Sửu": "Thìn", "Tuất": "Mùi", "Mùi": "Tuất"}
_TAM_HINH = [{"Dần", "Tỵ", "Thân"}, {"Sửu", "Tuất", "Mùi"}, {"Tý", "Mão"}]
_TU_HINH = {"Thìn", "Ngọ", "Dậu", "Hợi"}


def sao_han(nam_sinh_am: int, nam_xem: int, gioi_tinh: str) -> dict:
    """Sao chiếu mệnh của một người trong năm ``nam_xem``.

    ``gioi_tinh`` nhận "nam" hoặc "nu".
    """
    ds = load("han/sao_han")
    tuoi = tuoi_mu(nam_sinh_am, nam_xem)
    if tuoi < 10:
        # Dưới 10 tuổi vẫn quay vòng ngược lại theo đúng chu kỳ 9 năm.
        pass
    idx = (tuoi - 10) % 9
    key = "thu_tu_nam" if gioi_tinh.lower().startswith("nam") else "thu_tu_nu"
    ten = ds[key][idx]
    chi_tiet = next(s for s in ds["sao"] if s["ten"] == ten)
    return {"tuoi_mu": tuoi, "sao": ten, **chi_tiet}


def tam_tai(chi_tuoi: str, nam_xem_chi: str) -> dict:
    """Năm ``nam_xem_chi`` có phải tam tai của tuổi ``chi_tuoi`` không."""
    ds = load("han/tam_tai")
    for nhom in ds["nhom"]:
        if chi_tuoi in nhom["tam_hop"]:
            if nam_xem_chi in nhom["nam_tam_tai"]:
                thu = nhom["nam_tam_tai"].index(nam_xem_chi) + 1
                dien_bien = ds["dien_bien"][thu - 1]
                return {"pham": True, "nam_thu": thu, "tam_hop": nhom["tam_hop"],
                        "cac_nam_tam_tai": nhom["nam_tam_tai"], **dien_bien}
            return {"pham": False, "tam_hop": nhom["tam_hop"],
                    "cac_nam_tam_tai": nhom["nam_tam_tai"]}
    raise ValueError(f"Chi không hợp lệ: {chi_tuoi}")


def kim_lau(tuoi: int) -> dict:
    """Xét hạn Kim Lâu theo tuổi mụ."""
    ds = load("han/kim_lau")
    du = tuoi % 9
    for loai in ds["cac_loai"]:
        if loai["so_du"] == du:
            return {"pham": True, "tuoi_mu": tuoi, "so_du": du, **loai}
    return {"pham": False, "tuoi_mu": tuoi, "so_du": du,
            "ten": "Không phạm Kim Lâu"}


def hoang_oc(tuoi: int) -> dict:
    """Xét cung Hoang Ốc theo tuổi mụ."""
    ds = load("han/hoang_oc")
    if tuoi < 10:
        raise ValueError("Phép Hoang Ốc khởi từ 10 tuổi mụ trở lên")
    idx = ((tuoi // 10) - 1 + (tuoi % 10)) % 6
    cung = ds["cung"][idx]
    return {"tuoi_mu": tuoi, "cung": cung["ten"], "tot": cung["tot"],
            "y_nghia": cung["y_nghia"], "pham": not cung["tot"]}


def thai_tue(chi_tuoi: str, chi_nam: str) -> dict:
    """Quan hệ giữa chi tuổi và chi của năm xem (phạm Thái Tuế hay không)."""
    i, j = DIA_CHI.index(chi_tuoi), DIA_CHI.index(chi_nam)
    dang = []
    if i == j:
        dang.append("Bản mệnh Thái Tuế (năm tuổi)")
    if (i - j) % 12 == 6:
        dang.append("Xung Thái Tuế")
    for nhom in _TAM_HINH:
        if chi_tuoi in nhom and chi_nam in nhom and chi_tuoi != chi_nam:
            dang.append("Hình Thái Tuế")
            break
    if chi_tuoi == chi_nam and chi_tuoi in _TU_HINH:
        dang.append("Tự hình")
    if _LUC_HAI.get(chi_tuoi) == chi_nam:
        dang.append("Hại Thái Tuế")
    if _LUC_PHA.get(chi_tuoi) == chi_nam:
        dang.append("Phá Thái Tuế")
    ds = load("han/han_khac")["thai_tue"]
    chi_tiet = [d for d in ds["cac_dang"] if d["ten"] in dang]
    return {"pham": bool(dang), "cac_dang": dang, "chi_tiet": chi_tiet,
            "hoa_giai": ds["hoa_giai"] if dang else []}


def tuoi_lam_nha(nam_sinh_am: int, nam_lam: int) -> dict:
    """Bộ ba Kim Lâu — Hoang Ốc — Tam Tai, phép xem tuổi làm nhà kinh điển."""
    tuoi = tuoi_mu(nam_sinh_am, nam_lam)
    chi_tuoi = can_chi_nam(nam_sinh_am).chi
    chi_nam = can_chi_nam(nam_lam).chi
    kl, ho, tt = kim_lau(tuoi), hoang_oc(tuoi), tam_tai(chi_tuoi, chi_nam)
    pham = [x for x, ok in (("Kim Lâu", kl["pham"]), ("Hoang Ốc", ho["pham"]),
                            ("Tam Tai", tt["pham"])) if ok]
    return {
        "nam_sinh": nam_sinh_am, "nam_lam_nha": nam_lam, "tuoi_mu": tuoi,
        "tuoi_can_chi": can_chi_nam(nam_sinh_am).ten,
        "kim_lau": kl, "hoang_oc": ho, "tam_tai": tt,
        "cac_han_pham": pham,
        "ket_luan": ("Tuổi đẹp, không phạm hạn nào trong ba hạn làm nhà."
                     if not pham else
                     f"Phạm {len(pham)} hạn: {', '.join(pham)}. "
                     "Nên mượn tuổi hoặc lùi sang năm khác."),
    }


def ho_so_han(nam_sinh_am: int, nam_xem: int, gioi_tinh: str = "nam") -> dict:
    """Hồ sơ hạn đầy đủ của một người trong một năm — đầu vào chuẩn cho content."""
    chi_tuoi = can_chi_nam(nam_sinh_am).chi
    chi_nam = can_chi_nam(nam_xem).chi
    tuoi = tuoi_mu(nam_sinh_am, nam_xem)
    return {
        "nam_sinh_am_lich": nam_sinh_am,
        "tuoi_can_chi": can_chi_nam(nam_sinh_am).ten,
        "nap_am": can_chi_nam(nam_sinh_am).nap_am,
        "nam_xem": nam_xem, "nam_xem_can_chi": can_chi_nam(nam_xem).ten,
        "gioi_tinh": gioi_tinh, "tuoi_mu": tuoi,
        "sao_han": sao_han(nam_sinh_am, nam_xem, gioi_tinh),
        "tam_tai": tam_tai(chi_tuoi, chi_nam),
        "thai_tue": thai_tue(chi_tuoi, chi_nam),
        "kim_lau": kim_lau(tuoi),
        "hoang_oc": hoang_oc(tuoi) if tuoi >= 10 else None,
    }
