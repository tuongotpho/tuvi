# -*- coding: utf-8 -*-
"""Xem một năm cụ thể trên lá số: tiểu hạn, đại hạn đang đi và các sao lưu.

Tiểu hạn: khởi theo tam hợp chi năm sinh (Thân Tý Thìn khởi Tuất, Dần Ngọ Tuất
khởi Thìn, Tỵ Dậu Sửu khởi Mùi, Hợi Mão Mùi khởi Sửu), tuổi 1 tại cung khởi,
nam đếm thuận, nữ đếm nghịch. Vì chu kỳ 12 năm trùng 12 cung nên cung tiểu hạn
của một năm chỉ phụ thuộc chi năm đó.

Sao lưu (an lại theo can chi của NĂM XEM, dùng chung bảng với ``la_so``):
vòng Lưu Thái Tuế 12 sao, Lưu Lộc Tồn — Lưu Kình — Lưu Đà, Lưu Khôi — Lưu Việt,
Lưu Tứ Hóa, Lưu Thiên Mã, Lưu Khốc — Lưu Hư, Lưu Đào Hoa — Lưu Hồng Loan — Lưu
Thiên Hỷ. Đây là bộ sao lưu thông dụng trong sách Việt; các sao lưu khác (Lưu
Xương Khúc, Lưu Tang Hổ theo phái khác...) chưa đưa vào.
"""
from __future__ import annotations

from .canchi import DIA_CHI, can_chi_nam, tuoi_mu
from .kiem_tra import nam_hop_le
from .la_so import (VONG_THAI_TUE, _DAO_HOA, _KHOI_VIET, _LOC_TON, _TAM_HOP_MA,
                    _TU_HOA)

# Cung khởi tiểu hạn (tuổi 1) theo chi năm sinh, chỉ số địa chi Tý = 0.
_KHOI_TIEU_HAN = {8: 10, 0: 10, 4: 10,     # Thân Tý Thìn: Tuất
                  2: 4, 6: 4, 10: 4,       # Dần Ngọ Tuất: Thìn
                  5: 7, 9: 7, 1: 7,        # Tỵ Dậu Sửu: Mùi
                  11: 1, 3: 1, 7: 1}       # Hợi Mão Mùi: Sửu

# Điểm gợi ý của sao lưu khi rơi vào cung tiểu hạn / đại hạn (cùng tinh thần
# luan_giai: chỉ để xếp thứ tự đáng chú ý, liệt kê từng khoản).
DIEM_SAO_LUU = {"Lưu Hóa Lộc": 2, "Lưu Hóa Quyền": 1, "Lưu Hóa Khoa": 1, "Lưu Hóa Kỵ": -2,
                "Lưu Lộc Tồn": 2, "Lưu Kình Dương": -1, "Lưu Đà La": -1,
                "Lưu Thiên Khôi": 1, "Lưu Thiên Việt": 1, "Lưu Thiên Mã": 1,
                "Lưu Thiên Khốc": -1, "Lưu Thiên Hư": -1,
                "Lưu Thái Tuế": -1, "Lưu Tang Môn": -1, "Lưu Bạch Hổ": -1, "Lưu Tuế Phá": -1,
                "Lưu Điếu Khách": -1, "Lưu Quan Phù": -1, "Lưu Long Đức": 1, "Lưu Phúc Đức": 1,
                "Lưu Thiên Đức": 1, "Lưu Hồng Loan": 1, "Lưu Thiên Hỷ": 1, "Lưu Đào Hoa": 0}

Y_SAO_LUU = {
    "Lưu Hóa Lộc": "tài lộc, cơ hội của năm đến từ cung này",
    "Lưu Hóa Quyền": "năm nay được giao quyền, chủ động ở việc của cung này",
    "Lưu Hóa Khoa": "danh tiếng, thi cử, quý nhân hóa giải ở cung này",
    "Lưu Hóa Kỵ": "điểm nghẽn của năm — việc của cung này dễ trắc trở",
    "Lưu Lộc Tồn": "lộc năm đóng ở đây, giữ được của",
    "Lưu Kình Dương": "va chạm, tranh chấp, mổ xẻ liên quan cung này",
    "Lưu Đà La": "trì trệ, dây dưa ở việc của cung này",
    "Lưu Thiên Khôi": "quý nhân năm nay ở cung này", "Lưu Thiên Việt": "quý nhân năm nay ở cung này",
    "Lưu Thiên Mã": "năm hay đi lại, thay đổi liên quan cung này",
    "Lưu Thiên Khốc": "buồn phiền, hao tổn", "Lưu Thiên Hư": "hư hao, lo nghĩ",
    "Lưu Thái Tuế": "năm Thái Tuế đến cung này: thị phi, việc quan, nên giữ mình",
    "Lưu Tang Môn": "tang chế, buồn việc nhà", "Lưu Bạch Hổ": "tai nạn, kiện tụng, máu me",
    "Lưu Tuế Phá": "phá tán, đổ vỡ kế hoạch", "Lưu Điếu Khách": "viếng tang, tin buồn",
    "Lưu Quan Phù": "giấy tờ, kiện cáo", "Lưu Long Đức": "được che chở",
    "Lưu Phúc Đức": "phúc đến", "Lưu Thiên Đức": "đức độ hóa giải",
    "Lưu Đào Hoa": "duyên, giao thiệp", "Lưu Hồng Loan": "hỷ sự, cưới hỏi", "Lưu Thiên Hỷ": "tin vui",
    "Lưu Thiếu Dương": "", "Lưu Thiếu Âm": "", "Lưu Tử Phù": "", "Lưu Trực Phù": "",
}


def cung_tieu_han(chi_nam_sinh: int, chi_nam_xem: int, la_nam: bool) -> int:
    """Chỉ số địa chi của cung tiểu hạn trong năm có chi ``chi_nam_xem``."""
    khoi = _KHOI_TIEU_HAN[chi_nam_sinh]
    buoc = (chi_nam_xem - chi_nam_sinh) % 12
    return (khoi + buoc) % 12 if la_nam else (khoi - buoc) % 12


def sao_luu(nam_xem: int) -> dict[str, int]:
    """{tên sao lưu: chỉ số địa chi} theo can chi của năm xem."""
    cc = can_chi_nam(nam_xem)
    vt: dict[str, int] = {}
    for i, ten in enumerate(VONG_THAI_TUE):
        vt[f"Lưu {ten}"] = (cc.chi_idx + i) % 12
    lt = _LOC_TON[cc.can]
    vt["Lưu Lộc Tồn"], vt["Lưu Kình Dương"], vt["Lưu Đà La"] = lt, (lt + 1) % 12, (lt - 1) % 12
    khoi, viet = _KHOI_VIET[cc.can]
    vt["Lưu Thiên Khôi"], vt["Lưu Thiên Việt"] = khoi, viet
    vt["Lưu Thiên Mã"] = _TAM_HOP_MA[cc.chi_idx]
    vt["Lưu Thiên Khốc"], vt["Lưu Thiên Hư"] = (6 - cc.chi_idx) % 12, (6 + cc.chi_idx) % 12
    vt["Lưu Đào Hoa"] = _DAO_HOA[cc.chi_idx]
    hong = (3 - cc.chi_idx) % 12
    vt["Lưu Hồng Loan"], vt["Lưu Thiên Hỷ"] = hong, (hong + 6) % 12
    return vt


def _chi_cua_sao(ls: dict, ten: str) -> int | None:
    for c in ls["cac_cung"]:
        if any(s["ten"] == ten for s in c["sao"]):
            return DIA_CHI.index(c["chi"])
    return None


def xem_nam(ls: dict, nam_xem: int) -> dict:
    """Tiểu hạn, đại hạn và sao lưu của năm ``nam_xem`` trên lá số ``ls``."""
    nam_xem = nam_hop_le(nam_xem, "Năm xem")
    nam_sinh = ls["am_lich"]["nam"]
    if nam_xem < nam_sinh:
        from .kiem_tra import LoiDauVao
        raise LoiDauVao(f"Năm xem {nam_xem} trước năm sinh {nam_sinh}.")
    cc_xem, cc_sinh = can_chi_nam(nam_xem), can_chi_nam(nam_sinh)
    la_nam = ls["gioi_tinh"] == "Nam"
    tuoi = tuoi_mu(nam_sinh, nam_xem)
    cac = ls["cac_cung"]
    theo_chi = {DIA_CHI.index(c["chi"]): c for c in cac}

    # Tiểu hạn
    th_idx = cung_tieu_han(cc_sinh.chi_idx, cc_xem.chi_idx, la_nam)
    th = theo_chi[th_idx]

    # Đại hạn đang đi
    dh = next((c for c in cac
               if int(c["dai_han"].split("-")[0]) <= tuoi <= int(c["dai_han"].split("-")[1])), None)

    # Sao lưu và Lưu Tứ Hóa (theo chủ tinh của can năm xem, rơi vào cung có chủ tinh)
    vt = sao_luu(nam_xem)
    loc, quyen, khoa, ky = _TU_HOA[cc_xem.can]
    for hoa, chu in (("Lưu Hóa Lộc", loc), ("Lưu Hóa Quyền", quyen),
                     ("Lưu Hóa Khoa", khoa), ("Lưu Hóa Kỵ", ky)):
        i = _chi_cua_sao(ls, chu)
        if i is not None:
            vt[hoa] = i
    luu_tu_hoa = {"Lưu Hóa Lộc": loc, "Lưu Hóa Quyền": quyen, "Lưu Hóa Khoa": khoa, "Lưu Hóa Kỵ": ky}

    cung_luu: dict[str, list[str]] = {c["ten_cung"]: [] for c in cac}
    for ten, i in vt.items():
        cung_luu[theo_chi[i]["ten_cung"]].append(ten)

    def khoan_cua(cung: dict) -> list[dict]:
        ra = []
        for ten in cung_luu[cung["ten_cung"]]:
            d = DIEM_SAO_LUU.get(ten, 0)
            if d:
                ra.append({"ly_do": ten, "diem": d})
        return ra

    khoan_th = khoan_cua(th)
    khoan_dh = khoan_cua(dh) if dh else []
    diem = sum(k["diem"] for k in khoan_th + khoan_dh)

    # Thái Tuế của năm rơi cung nào so với Mệnh
    menh_idx = DIA_CHI.index(ls["cung_menh"])
    lech = (cc_xem.chi_idx - menh_idx) % 12
    thai_tue_menh = {0: "Thái Tuế nhập Mệnh", 6: "Thái Tuế xung chiếu Mệnh",
                     4: "Thái Tuế tam hợp Mệnh", 8: "Thái Tuế tam hợp Mệnh"}.get(lech)

    def mo_ta_cung(c: dict) -> dict:
        return {"ten_cung": c["ten_cung"], "chi": c["chi"], "chu_ve": c["chu_ve"],
                "chinh_tinh": [s["ten"] for s in c["sao"] if s["nhom"] == "Chính tinh"],
                "tu_hoa_goc": [s["ten"] for s in c["sao"] if s["nhom"] == "Tứ Hóa"],
                "sao_luu": cung_luu[c["ten_cung"]],
                "tuan": bool(c.get("tuan")), "triet": bool(c.get("triet"))}

    nhan_xet = [f"Năm {cc_xem.ten} ({nam_xem}), tuổi mụ {tuoi}: tiểu hạn tại cung "
                f"{th['ten_cung']} ({th['chi']}), đại hạn "
                + (f"{dh['dai_han']} tại cung {dh['ten_cung']} ({dh['chi']})." if dh
                   else "chưa vào bảng.")]
    ct = [s["ten"] for s in th["sao"] if s["nhom"] == "Chính tinh"]
    nhan_xet.append(f"Việc trong năm mang màu sắc cung {th['ten_cung']} — {th['chu_ve'].lower()}"
                    + (f", chính tinh {' + '.join(ct)}." if ct else ", cung vô chính diệu nên mượn cung đối chiếu."))
    sl = [f"{t} ({Y_SAO_LUU[t]})" for t in cung_luu[th["ten_cung"]] if Y_SAO_LUU.get(t)]
    if sl:
        nhan_xet.append("Sao lưu vào cung tiểu hạn: " + "; ".join(sl) + ".")
    for hoa in ("Lưu Hóa Lộc", "Lưu Hóa Kỵ"):
        if hoa in vt:
            c = theo_chi[vt[hoa]]
            nhan_xet.append(f"{hoa} theo {luu_tu_hoa[hoa]} đóng cung {c['ten_cung']}: {Y_SAO_LUU[hoa]}.")
    if thai_tue_menh:
        nhan_xet.append(f"{thai_tue_menh}: năm có nhiều việc đến tay, dễ thị phi; nên giữ lời, "
                        "tránh kiện cáo.")
    if th.get("tuan") or th.get("triet"):
        nhan_xet.append("Cung tiểu hạn bị Tuần/Triệt án ngữ: việc trong năm đến chậm, tốt xấu đều giảm.")

    return {
        "nam_xem": nam_xem, "nam_xem_can_chi": cc_xem.ten, "tuoi_mu": tuoi,
        "tieu_han": mo_ta_cung(th),
        "dai_han": {**mo_ta_cung(dh), "tuoi": dh["dai_han"]} if dh else None,
        "thai_tue_voi_menh": thai_tue_menh,
        "luu_tu_hoa": luu_tu_hoa,
        "sao_luu": {ten: DIA_CHI[i] for ten, i in vt.items()},
        "sao_luu_theo_cung": [{"ten_cung": c["ten_cung"], "chi": c["chi"],
                               "sao_luu": cung_luu[c["ten_cung"]]} for c in cac],
        "diem": diem,
        "khoan_diem": [{**k, "noi": "tiểu hạn"} for k in khoan_th]
                      + [{**k, "noi": "đại hạn"} for k in khoan_dh],
        "nhan_xet": nhan_xet,
        "ghi_chu": "Sao lưu an theo can chi năm xem, cùng bảng với sao gốc. Điểm chỉ để xếp "
                   "thứ tự đáng chú ý giữa các năm; muốn so năm này với năm khác thì đổi năm xem.",
    }


__all__ = ["xem_nam", "sao_luu", "cung_tieu_han"]
