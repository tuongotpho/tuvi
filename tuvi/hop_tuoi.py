# -*- coding: utf-8 -*-
"""Xem tuổi hai người có hợp nhau không — theo tri thức phong tục và thuật số dân gian Việt Nam.

Hệ thống luận giải toàn diện:
1. **Bản mệnh ngũ hành nạp âm**: Phân tích tương sinh, tương khắc (chồng sinh vợ / vợ sinh chồng,
   chồng khắc vợ / vợ khắc chồng), các cách nạp âm đặc thù (Kiếm Phong Kim, Sa Trung Kim,
   Đại Hải Thủy, Thiên Thượng Hỏa...).
2. **Thiên can**: Ngũ hợp thiên can (Giáp Kỷ, Ất Canh, Bính Tân, Đinh Nhâm, Mậu Quý), tứ xung thiên can,
   tương khắc ngũ hành và can bình hòa.
3. **Địa chi**: Tam hợp, Lục hợp, Tứ hành xung (Lục xung trực diện), Lục hại, Lục phá, Tương hình, Tự hình.
4. **Cung phi Bát trạch & Cung sinh (Cung mệnh)**: Bát du niên (Sinh Khí, Diên Niên, Thiên Y, Phục Vị /
   Tuyệt Mệnh, Ngũ Quỷ, Lục Sát, Họa Hại), ngũ hành cung phi, phân biệt Cung Phi và Cung Sinh.
5. **Cao Ly Đầu Hình**: 120 cách cục duyên nợ tiền định theo Can chồng - Chi vợ từ Diễn Cầm Tam Thế và Ngọc Hạp,
   kèm thơ phú dân gian và luận giải tiền vận - hậu vận.
6. **Xem Hợp tác làm ăn / Kinh doanh**: Phân tích Thiên Ất Quý Nhân, Thiên Lộc (Lộc Tồn), Thiên Mã,
   phân định vai trò điều hành (đối ngoại thị trường vs tài chính nội bộ), quản trị rủi ro.
7. **Cẩm nang hóa giải xung khắc toàn diện**:
   - Hóa giải bản mệnh tương khắc bằng hành cầu nối.
   - Hóa giải Cung phi hung theo phép Bát Trạch (Thiên Y chế Tuyệt Mệnh, Sinh Khí giáng Ngũ Quỷ...).
   - Hóa giải Địa chi xung hại bằng chi trung gian.
   - Đạo lý nhân tâm gia đạo ("Đức năng thắng số", chữ Nhẫn và sự đồng lòng).
8. **Gợi ý năm sinh con hóa giải xung khắc**: Phân tích 6 năm tiếp theo (2026–2031) về can chi, mệnh nạp âm,
   mức độ hợp với bố mẹ và vai trò cầu nối hòa hợp.
"""
from __future__ import annotations

from .canchi import (CON_GIAP, DIA_CHI, HANH_CAN, NAP_AM_60, THIEN_CAN,
                     can_chi_nam, can_khac, luc_xung, nhom_tam_hop,
                     quan_he_chi)
from .cao_ly_dau_hinh import tra_cao_ly
from .kiem_tra import LoiDauVao, gioi_tinh_hop_le, nam_hop_le
from .phong_thuy import cung_phi
from .store import load

# Ngũ hành tương sinh và tương khắc nạp từ data/ngu_hanh.json
_SINH: dict[str, str] = {}
_KHAC: dict[str, str] = {}


def _bang_ngu_hanh() -> tuple[dict, dict]:
    if not _SINH:
        for h in load("ngu_hanh"):
            _SINH[h["hanh"]] = h["sinh"]
            _KHAC[h["hanh"]] = h["khac"]
    return _SINH, _KHAC


# Điểm số của từng yếu tố cốt lõi (giữ đúng tương thích kiểm thử)
DIEM = {
    "menh_tuong_sinh": 3, "menh_binh_hoa": 1, "menh_tuong_khac": -3,
    "can_hop": 1, "can_khac": -2,
    "tam_hop": 3, "luc_hop": 3, "luc_xung": -4, "luc_hai": -2,
    "luc_pha": -1, "tuong_hinh": -2,
    "du_nien_tot": 3, "du_nien_xau": -3,
    "thien_khac_dia_xung": -3,
}

# Ngũ hợp thiên can
NGU_HOP_CAN: dict[tuple[str, str], dict[str, str]] = {
    ("Giáp", "Kỷ"): {"hoa": "Thổ", "ten": "Trung Chính chi hợp", "y_nghia": "Đôn hậu, khoan hòa, trọng chữ tín, vợ chồng hòa thuận"},
    ("Kỷ", "Giáp"): {"hoa": "Thổ", "ten": "Trung Chính chi hợp", "y_nghia": "Đôn hậu, khoan hòa, trọng chữ tín, vợ chồng hòa thuận"},
    ("Ất", "Canh"): {"hoa": "Kim", "ten": "Nhân Nghĩa chi hợp", "y_nghia": "Cương nhu tương tể, trọng nghĩa khí, cùng chung chí hướng"},
    ("Canh", "Ất"): {"hoa": "Kim", "ten": "Nhân Nghĩa chi hợp", "y_nghia": "Cương nhu tương tể, trọng nghĩa khí, cùng chung chí hướng"},
    ("Bính", "Tân"): {"hoa": "Thủy", "ten": "Oai Chế chi hợp", "y_nghia": "Trang nghiêm, quyết đoán, tình cảm sâu sắc thủy chung"},
    ("Tân", "Bính"): {"hoa": "Thủy", "ten": "Oai Chế chi hợp", "y_nghia": "Trang nghiêm, quyết đoán, tình cảm sâu sắc thủy chung"},
    ("Đinh", "Nhâm"): {"hoa": "Mộc", "ten": "Nhân Thọ chi hợp", "y_nghia": "Nhân từ, thọ duyên, vợ chồng mặn nồng tình cảm"},
    ("Nhâm", "Đinh"): {"hoa": "Mộc", "ten": "Nhân Thọ chi hợp", "y_nghia": "Nhân từ, thọ duyên, vợ chồng mặn nồng tình cảm"},
    ("Mậu", "Quý"): {"hoa": "Hỏa", "ten": "Đa Lễ chi hợp", "y_nghia": "Hòa nhã, thông tuệ, tôn trọng lẫn nhau"},
    ("Quý", "Mậu"): {"hoa": "Hỏa", "ten": "Đa Lễ chi hợp", "y_nghia": "Hòa nhã, thông tuệ, tôn trọng lẫn nhau"},
}

# Tứ xung thiên can
TU_XUNG_CAN = {
    ("Giáp", "Canh"), ("Canh", "Giáp"),
    ("Ất", "Tân"), ("Tân", "Ất"),
    ("Bính", "Nhâm"), ("Nhâm", "Bính"),
    ("Đinh", "Quý"), ("Quý", "Đinh"),
}

# Bảng Thiên Ất Quý Nhân (Can người này -> Chi quý nhân của người kia)
QUY_NHAN = {
    "Giáp": ["Sửu", "Mùi"], "Mậu": ["Sửu", "Mùi"], "Canh": ["Sửu", "Mùi"],
    "Ất": ["Tý", "Thân"], "Kỷ": ["Tý", "Thân"],
    "Bính": ["Hợi", "Dậu"], "Đinh": ["Hợi", "Dậu"],
    "Tân": ["Dần", "Ngọ"],
    "Nhâm": ["Tỵ", "Mão"], "Quý": ["Tỵ", "Mão"],
}

# Bảng Lộc Tồn (Thiên Lộc)
LOC_TON = {
    "Giáp": "Dần", "Ất": "Mão", "Bính": "Tỵ", "Mậu": "Tỵ",
    "Đinh": "Ngọ", "Kỷ": "Ngọ", "Canh": "Thân", "Tân": "Dậu",
    "Nhâm": "Hợi", "Quý": "Tý",
}

# Bảng Thiên Mã
THIEN_MA = {
    "Dần": "Thân", "Ngọ": "Thân", "Tuất": "Thân",
    "Thân": "Dần", "Tý": "Dần", "Thìn": "Dần",
    "Tỵ": "Hợi", "Dậu": "Hợi", "Sửu": "Hợi",
    "Hợi": "Tỵ", "Mão": "Tỵ", "Mùi": "Tỵ",
}

# Cung Sinh (Cung Bát Tự Lữ Tài theo năm sinh)
CUNG_SINH_8 = ["Càn", "Khảm", "Cấn", "Chấn", "Tốn", "Ly", "Khôn", "Đoài"]


def _cung_sinh(nam_am: int) -> str:
    """Cung sinh (cung mệnh bát tự) tính theo Lục thập hoa giáp (dùng chung nam nữ)."""
    cc = can_chi_nam(nam_am)
    idx = (cc.hoa_giap_idx // 2) % 8
    return CUNG_SINH_8[idx]


def _con_giap(chi: str) -> str:
    return CON_GIAP[DIA_CHI.index(chi)]


def _menh(nam_am: int) -> dict:
    cc = can_chi_nam(nam_am)
    nap = cung_phi(nam_am, "nam")
    return {
        "nam": nam_am, "can_chi": f"{cc.can} {cc.chi}", "can": cc.can,
        "chi": cc.chi, "con_giap": _con_giap(cc.chi),
        "nap_am": nap["menh_nap_am"], "hanh": nap["hanh_nap_am"],
        "cung_sinh": _cung_sinh(nam_am),
    }


def _xet_ban_menh(a: dict, b: dict, la_hon_nhan: bool = True) -> tuple[dict, dict]:
    """Xét ngũ hành nạp âm bản mệnh, trả về (mục tóm tắt, chi tiết chuyên sâu)."""
    sinh, khac = _bang_ngu_hanh()
    ha, hb = a["hanh"], b["hanh"]
    nap_a, nap_b = a["nap_am"], b["nap_am"]

    # Phân tích nạp âm đặc thù cổ truyền
    dac_thu = []
    if ("Kiếm Phong Kim" in (nap_a, nap_b) or "Sa Trung Kim" in (nap_a, nap_b)) and ("Hỏa" in (ha, hb)):
        dac_thu.append("Kim gặp Hỏa này là cách 'Kim phùng Hỏa luyện thành khí' (vàng mũi kiếm và vàng trong cát cần lửa trui rèn mới thành vật báu sắc bén). Tuy ngũ hành là khắc nhưng nạp âm lại chủ quý hiển, không đáng lo ngại.")
    if ("Đại Hải Thủy" in (nap_a, nap_b) or "Thiên Thượng Hỏa" in (nap_a, nap_b)) and ("Thổ" in (ha, hb)):
        dac_thu.append("Nước biển lớn (Đại Hải Thủy) hoặc Lửa trên trời (Thiên Thượng Hỏa) gặp Thổ không bị vùi lấp hay ngăn trở. Thổ không khắc chế được cách cục này.")
    if "Tích Lịch Hỏa" in (nap_a, nap_b) and ("Thủy" in (ha, hb)):
        dac_thu.append("Lửa sấm sét (Tích Lịch Hỏa) gặp Thủy (mưa giông) càng thêm oai phong lẫm liệt, phát huy sức mạnh chứ không bị dập tắt.")

    if ha == hb:
        tt = {
            "muc": "Bản mệnh", "ket_qua": "Bình hòa", "tinh_chat": "trung bình",
            "diem": DIEM["menh_binh_hoa"],
            "giai_thich": f"Hai người cùng hành {ha} ({nap_a} và {nap_b}) — không sinh không khắc, "
                          f"đồng điệu trong cảm xúc và lối sống nhưng ít bổ trợ bù đắp khiếm khuyết cho nhau."
        }
        ct = {
            "quan_he": "Cùng hành bình hòa",
            "chi_tiet": f"Cả hai đều mang mệnh {ha}. Sự tương đồng giúp thấu hiểu nhau nhanh chóng, song nếu cả hai cùng nóng tính hoặc cùng bướng bỉnh thì cần học chữ 'Nhẫn'.",
            "vai_ve": "Đồng hành bình đẳng, hỗ trợ tương đương.",
            "dac_thu": dac_thu,
        }
        return tt, ct

    if sinh.get(ha) == hb or sinh.get(hb) == ha:
        nguoi_sinh, nguoi_duoc = (a, b) if sinh.get(ha) == hb else (b, a)
        loi_hon_nhan = ""
        if la_hon_nhan:
            if nguoi_sinh["gioi_tinh"] == "nam":
                loi_hon_nhan = " Chồng sinh Vợ là thuận lý âm dương: chồng yêu thương che chở, nhường nhịn và tạo bệ phóng cho vợ."
            else:
                loi_hon_nhan = " Vợ sinh Chồng là phúc tướng: người vợ vượng phu ích tử, chu toàn hậu phương giúp chồng thăng tiến."
        tt = {
            "muc": "Bản mệnh", "ket_qua": "Tương sinh", "tinh_chat": "tốt",
            "diem": DIEM["menh_tuong_sinh"],
            "giai_thich": f"{nguoi_sinh['hanh']} sinh {nguoi_duoc['hanh']}: tuổi {nguoi_sinh['can_chi']} "
                          f"({nguoi_sinh['nap_am']}) nâng đỡ tuổi {nguoi_duoc['can_chi']} "
                          f"({nguoi_duoc['nap_am']}). Đây là quan hệ thuận nhất.{loi_hon_nhan}"
        }
        ct = {
            "quan_he": f"{nguoi_sinh['hanh']} sinh {nguoi_duoc['hanh']}",
            "chi_tiet": f"Tuổi {nguoi_sinh['can_chi']} là nguồn năng lượng bồi đắp, tương sinh trực tiếp cho tuổi {nguoi_duoc['can_chi']}.{loi_hon_nhan}",
            "vai_ve": f"Người mệnh {nguoi_sinh['hanh']} là chỗ dựa vững vàng cho người mệnh {nguoi_duoc['hanh']}.",
            "dac_thu": dac_thu,
        }
        return tt, ct

    # Tương khắc
    nguoi_khac, nguoi_bi = (a, b) if khac.get(ha) == hb else (b, a)
    loi_hon_nhan_khac = ""
    if la_hon_nhan:
        if nguoi_khac["gioi_tinh"] == "nam":
            loi_hon_nhan_khac = " Cổ nhân coi 'Chồng khắc Vợ là thuận lẽ tự nhiên' (cương chế nhu, chồng giữ vai trò trụ cột gia đình). Chỉ cần người chồng tránh độc đoán và đối xử hòa ái thì gia đạo vẫn vững bền."
        else:
            loi_hon_nhan_khac = " 'Vợ khắc Chồng là nghịch lý' — người vợ dễ lấn lướt chồng hoặc lo lắng thái quá. Người vợ nên nhu thuận, tôn trọng và để chồng quyết định các việc lớn trong nhà."
    tt = {
        "muc": "Bản mệnh", "ket_qua": "Tương khắc", "tinh_chat": "xấu",
        "diem": DIEM["menh_tuong_khac"],
        "giai_thich": f"{nguoi_khac['hanh']} khắc {nguoi_bi['hanh']}: tuổi {nguoi_khac['can_chi']} "
                      f"({nguoi_khac['nap_am']}) khắc tuổi {nguoi_bi['can_chi']} ({nguoi_bi['nap_am']}). "
                      f"Dân gian kiêng, nhưng nhiều nhà vẫn ở với nhau êm — xem thêm các mục còn lại và "
                      f"áp dụng phép hóa giải ngũ hành cầu nối."
    }
    ct = {
        "quan_he": f"{nguoi_khac['hanh']} khắc {nguoi_bi['hanh']}",
        "chi_tiet": f"{nguoi_khac['nap_am']} khắc {nguoi_bi['nap_am']}.{loi_hon_nhan_khac}",
        "vai_ve": f"Người mệnh {nguoi_khac['hanh']} áp chế người mệnh {nguoi_bi['hanh']}.",
        "dac_thu": dac_thu,
    }
    return tt, ct


def _xet_thien_can(a: dict, b: dict) -> tuple[dict, dict]:
    """Xét Thiên Can, trả về (mục tóm tắt, chi tiết ngũ hợp/tứ xung)."""
    cap = (a["can"], b["can"])
    hop = NGU_HOP_CAN.get(cap)
    la_xung = cap in TU_XUNG_CAN
    la_khac = can_khac(a["can"], b["can"]) or can_khac(b["can"], a["can"])

    if hop:
        tt = {
            "muc": "Thiên can", "ket_qua": f"Ngũ hợp ({hop['ten']})", "tinh_chat": "tốt",
            "diem": DIEM["can_hop"] + 1,  # Ngũ hợp điểm cao hơn
            "giai_thich": f"Can {a['can']} hợp Can {b['can']} hóa {hop['hoa']} ({hop['ten']}): {hop['y_nghia']}."
        }
        ct = {"loai": "Ngũ hợp thiên can", "hoa_khi": hop["hoa"], "ten": hop["ten"], "y_nghia": hop["y_nghia"]}
        return tt, ct

    if la_khac:
        ke, bi = ((a, b) if can_khac(a["can"], b["can"]) else (b, a))
        bo_sung = ""
        if la_xung:
            bo_sung = f" Vừa tương khắc vừa phạm Tứ xung thiên can ({a['can']} xung {b['can']}), dễ đối đầu trực diện khi tranh luận."
        tt = {
            "muc": "Thiên can", "ket_qua": "Can khắc" if not la_xung else "Can xung khắc", "tinh_chat": "xấu",
            "diem": DIEM["can_khac"],
            "giai_thich": f"Can {ke['can']} ({HANH_CAN[THIEN_CAN.index(ke['can'])]}) khắc can {bi['can']} "
                          f"({HANH_CAN[THIEN_CAN.index(bi['can'])]}): dễ va chạm trong cách nghĩ, cách quyết việc.{bo_sung}"
        }
        ct = {"loai": "Tương khắc" if not la_xung else "Tương xung khắc", "ke": ke["can"], "bi": bi["can"], "la_xung": la_xung}
        return tt, ct

    tt = {
        "muc": "Thiên can", "ket_qua": "Không khắc", "tinh_chat": "tốt",
        "diem": DIEM["can_hop"],
        "giai_thich": f"Can {a['can']} và can {b['can']} không xung không khắc, tư tưởng và quan điểm tương đối hài hòa."
    }
    ct = {"loai": "Bình hòa", "y_nghia": "Không xung khắc, dễ tìm được tiếng nói chung trong sinh hoạt và công việc."}
    return tt, ct


def _xet_dia_chi(a: dict, b: dict) -> tuple[dict, dict]:
    """Xét Địa Chi: Tam hợp, Lục hợp, Lục xung, Tứ hành xung, Lục hại, Lục phá, Tương hình."""
    quan_he = quan_he_chi(a["chi"], b["chi"])
    diem, tot, xau = 0, [], []
    for qh in quan_he:
        khoa = {"Tam hợp": "tam_hop", "Lục hợp": "luc_hop", "Lục xung": "luc_xung",
                "Lục hại": "luc_hai", "Lục phá": "luc_pha",
                "Tương hình": "tuong_hinh"}.get(qh)
        if not khoa:
            continue
        diem += DIEM[khoa]
        (tot if DIEM[khoa] > 0 else xau).append(qh)

    # Phân tích tứ hành xung và chi tiết
    tu_hanh_xung_giai_thich = ""
    nhom_thx = [
        {"Tý", "Ngọ", "Mão", "Dậu"},
        {"Dần", "Thân", "Tỵ", "Hợi"},
        {"Thìn", "Tuất", "Sửu", "Mùi"},
    ]
    for nhom in nhom_thx:
        if a["chi"] in nhom and b["chi"] in nhom:
            if "Lục xung" in quan_he:
                tu_hanh_xung_giai_thich = f"Chi {a['chi']} và {b['chi']} là cặp xung đối diện 180 độ trong bộ tứ hành xung ({', '.join(sorted(nhom))}), tác động trực tiếp và mạnh mẽ nhất."
            else:
                tu_hanh_xung_giai_thich = f"Dân gian hay gọi chung {a['chi']} và {b['chi']} nằm trong nhóm 'tứ hành xung' ({', '.join(sorted(nhom))}), nhưng thực chất hai tuổi này KHÔNG xung trực diện (chỉ xung khi đối đầu 180 độ). Thậm chí có thể còn là Nhị hợp hoặc vô hại."
            break

    if not quan_he:
        tt = {
            "muc": "Địa chi", "ket_qua": "Bình thường", "tinh_chat": "trung bình",
            "diem": 0, "quan_he": [],
            "giai_thich": f"Chi {a['chi']} ({a['con_giap']}) và {b['chi']} ({b['con_giap']}) không nằm trong nhóm hợp nào, cũng không xung hại gì nhau."
        }
        ct = {"quan_he": [], "y_nghia": "Bình hòa, các mối quan hệ đời thường diễn ra tự nhiên.", "tu_hanh_xung": tu_hanh_xung_giai_thich}
        return tt, ct

    manh = " và ".join(quan_he)
    if tot and not xau:
        loi = f"Chi {a['chi']} — {b['chi']} {manh.lower()}: hợp ý nhau, dễ đồng thuận."
        if "Tam hợp" in tot:
            loi += f" Nhóm tam hợp: {' — '.join(nhom_tam_hop(a['chi']))}."
        tc = "tốt"
    elif xau and not tot:
        loi = f"Chi {a['chi']} — {b['chi']} {manh.lower()}: hay bất đồng, cần nhường nhau."
        if "Lục xung" in xau:
            loi += f" Lục xung là cặp đối nhau trên vòng địa chi ({a['chi']} xung {luc_xung(a['chi'])})."
        tc = "xấu"
    elif tot and xau:
        loi = f"Chi {a['chi']} — {b['chi']} vừa {' vừa '.join(q.lower() for q in quan_he)}: vừa hút vừa đẩy, lúc rất hợp lúc rất căng."
        tc = "trung bình"
    else:
        loi = (f"Chi {a['chi']} — {b['chi']}: {manh.lower()}. Không nằm trong nhóm hợp nào, cũng không xung hại gì nhau."
               + (" Cùng tuổi thì dễ hiểu nhau nhưng cũng dễ cùng lúc gặp hạn, vì vòng Thái Tuế của hai người trùng nhau."
                  if a["chi"] == b["chi"] else ""))
        tc = "trung bình"

    tt = {"muc": "Địa chi", "ket_qua": manh, "tinh_chat": tc, "diem": diem, "quan_he": quan_he, "giai_thich": loi}
    ct = {"quan_he": quan_he, "giai_thich": loi, "tu_hanh_xung": tu_hanh_xung_giai_thich}
    return tt, ct


def _xet_cung_phi(a_cung: dict, b_cung: dict) -> tuple[dict, dict]:
    """Xét Cung phi Bát trạch theo Đại du niên bát biến."""
    bang = {c["ten"]: c for c in load("phong_thuy/bat_trach")["cung"]}
    y_nghia = {d["ten"]: d for d in load("phong_thuy/bat_trach")["du_nien"]}
    ten = bang[a_cung["cung_phi"]]["du_nien"][bang[b_cung["cung_phi"]]["huong"]]
    d = y_nghia[ten]
    tot = d["tinh_chat"] == "tốt"
    cung_nhom = a_cung["nhom"] == b_cung["nhom"]

    ha_cung = bang[a_cung["cung_phi"]]["hanh"]
    hb_cung = bang[b_cung["cung_phi"]]["hanh"]

    tt = {
        "muc": "Cung phi", "ket_qua": ten, "tinh_chat": d["tinh_chat"],
        "diem": DIEM["du_nien_tot"] if tot else DIEM["du_nien_xau"],
        "cung_a": a_cung["cung_phi"], "cung_b": b_cung["cung_phi"],
        "cung_nhom": cung_nhom,
        "giai_thich": f"Cung {a_cung['cung_phi']} soi sang cung {b_cung['cung_phi']} được du niên {ten} — {d['y_nghia']} "
                      + ("Hai người cùng nhóm "
                         f"{a_cung['nhom']}, chọn hướng nhà dễ thống nhất."
                         if cung_nhom else
                         f"Hai người khác nhóm ({a_cung['nhom']} và {b_cung['nhom']}), chọn hướng nhà sẽ phải nhường nhau.")
    }
    ct = {
        "du_nien": ten, "tinh_chat": d["tinh_chat"], "sao": d.get("sao", ""),
        "hanh_sao": d.get("hanh", ""), "y_nghia": d["y_nghia"],
        "cung_nhom": cung_nhom,
        "ngu_hanh_cung": f"Cung {a_cung['cung_phi']} ({ha_cung}) và Cung {b_cung['cung_phi']} ({hb_cung})",
    }
    return tt, ct


def _tim_cau_noi_ngu_hanh(ha: str, hb: str) -> dict:
    """Tìm ngũ hành trung gian làm cầu nối hóa giải tương khắc."""
    sinh, khac = _bang_ngu_hanh()
    if ha == hb or sinh.get(ha) == hb or sinh.get(hb) == ha:
        return {"can_hoa_giai": False, "hanh_cau_noi": None, "giai_thich": "Bản mệnh đã tương sinh hoặc bình hòa, không cần cầu nối."}

    nguoi_khac, nguoi_bi = (ha, hb) if khac.get(ha) == hb else (hb, ha)
    # Nguyên tắc: A khắc B -> Dùng C sao cho A sinh C, C sinh B
    # Kim khắc Mộc -> dùng Thủy (Kim sinh Thủy, Thủy sinh Mộc)
    # Mộc khắc Thổ -> dùng Hỏa (Mộc sinh Hỏa, Hỏa sinh Thổ)
    # Thổ khắc Thủy -> dùng Kim (Thổ sinh Kim, Kim sinh Thủy)
    # Thủy khắc Hỏa -> dùng Mộc (Thủy sinh Mộc, Mộc sinh Hỏa)
    # Hỏa khắc Kim -> dùng Thổ (Hỏa sinh Thổ, Thổ sinh Kim)
    hanh_cau = sinh.get(nguoi_khac, "")
    return {
        "can_hoa_giai": True,
        "nguoi_khac": nguoi_khac, "nguoi_bi": nguoi_bi,
        "hanh_cau_noi": hanh_cau,
        "cong_thuc": f"{nguoi_khac} sinh {hanh_cau}, {hanh_cau} sinh {nguoi_bi}",
        "giai_thich": f"{nguoi_khac} khắc {nguoi_bi}. Cần dùng hành {hanh_cau} làm cầu nối chuyển hung thành cát: "
                      f"{nguoi_khac} sinh {hanh_cau}, rồi {hanh_cau} lại dưỡng sinh cho {nguoi_bi}."
    }


def _phan_tich_hoa_giai(a: dict, b: dict, muc_xet: list[dict], du_nien_ten: str) -> dict:
    """Bộ cẩm nang hóa giải chi tiết cho hôn nhân và gia đạo."""
    cau_noi = _tim_cau_noi_ngu_hanh(a["hanh"], b["hanh"])

    # 1. Hóa giải mệnh
    hoa_giai_menh = []
    if cau_noi["can_hoa_giai"]:
        h = cau_noi["hanh_cau_noi"]
        hoa_giai_menh.append({
            "tieu_de": f"Hóa giải mệnh tương khắc bằng hành {h}",
            "noi_dung": f"{cau_noi['giai_thich']} Áp dụng bằng cách sinh con mang mệnh {h}, hoặc chọn màu sơn phòng ngủ, vật phẩm trang trí nội thất chủ đạo mang hành {h}."
        })
    else:
        hoa_giai_menh.append({
            "tieu_de": "Bản mệnh thuận lợi",
            "noi_dung": "Ngũ hành của hai người đã tương sinh hoặc bình hòa, gia đạo hòa khí tốt lành, không cần hóa giải bản mệnh."
        })

    # 2. Hóa giải Cung phi Bát trạch nếu phạm 4 cung xấu
    hoa_giai_cung = []
    if du_nien_ten == "Tuyệt Mệnh":
        hoa_giai_cung.append({
            "tieu_de": "Phép hóa giải Tuyệt Mệnh: 'Thiên Y chế Tuyệt Mệnh'",
            "noi_dung": "Bát Trạch dạy rằng cửa bếp hoặc hướng giường ngủ quay về hướng Thiên Y của gia chủ thì có thể trấn áp hoàn toàn khí Tuyệt Mệnh, giúp gia đạo bình an, sức khỏe dồi dào, con cái thuận hòa. Cũng có thể sinh con vào năm có cung Thiên Y."
        })
    elif du_nien_ten == "Ngũ Quỷ":
        hoa_giai_cung.append({
            "tieu_de": "Phép hóa giải Ngũ Quỷ: 'Sinh Khí giáng Ngũ Quỷ'",
            "noi_dung": "Bát Trạch có câu 'Sinh Khí giáng Ngũ Quỷ'. Chọn hướng nhà, hướng cửa chính hoặc hướng bếp quay về hướng Sinh Khí của người chồng sẽ áp chế được hỏa khí của sao Liêm Trinh (Ngũ Quỷ), chuyển họa thành phúc."
        })
    elif du_nien_ten == "Lục Sát":
        hoa_giai_cung.append({
            "tieu_de": "Phép hóa giải Lục Sát: 'Diên Niên yểm Lục Sát'",
            "noi_dung": "Đặt hướng bếp hoặc phòng ngủ theo hướng Diên Niên (Phúc Đức). Sao Vũ Khúc Kim của Diên Niên sẽ trấn áp tính dâm thủy của sao Văn Khúc (Lục Sát), giữ cho vợ chồng luôn gắn bó hòa thuận."
        })
    elif du_nien_ten == "Họa Hại":
        hoa_giai_cung.append({
            "tieu_de": "Phép hóa giải Họa Hại: 'Phục Vị an Họa Hại'",
            "noi_dung": "Đặt bàn thờ hoặc hướng bếp quay về hướng Phục Vị. Khí Phục Vị giúp giữ gìn nền nếp gia phong, ngăn ngừa hao tổn tài lộc và tránh những thị phi khẩu thiệt."
        })
    else:
        hoa_giai_cung.append({
            "tieu_de": f"Cung phi gặp cung {du_nien_ten} (Cát)",
            "noi_dung": f"Du niên {du_nien_ten} là một trong bốn hướng cát lành nhất trong Bát trạch phối hôn, mang lại may mắn, hạnh phúc và tài lộc dồi dào."
        })

    # 3. Hóa giải Địa chi nếu xung / hại
    chi_xet = next((m for m in muc_xet if m["muc"] == "Địa chi"), None)
    hoa_giai_chi = []
    if chi_xet and chi_xet.get("quan_he"):
        qh = chi_xet["quan_he"]
        if "Lục xung" in qh:
            hoa_giai_chi.append({
                "tieu_de": f"Hóa giải Lục xung ({a['chi']} — {b['chi']})",
                "noi_dung": "Lục xung là sự đối đầu về năng lượng. Cổ nhân khuyên nên dùng con giáp trung gian thuộc nhóm Nhị hợp hoặc Tam hợp để dung hòa (thông qua tuổi sinh con, người đứng mối mai hôn lễ, hoặc đeo linh vật phong thủy trợ mệnh)."
            })
        if "Lục hại" in qh:
            hoa_giai_chi.append({
                "tieu_de": f"Hóa giải Lục hại ({a['chi']} — {b['chi']})",
                "noi_dung": "Lục hại chủ về sự nghi kỵ, thiếu niềm tin. Vợ chồng cần minh bạch về tài chính, thẳng thắn trò chuyện và không giấu giếm để xóa bỏ nghi ngờ."
            })

    # 4. Đạo lý gia đạo nhân tâm
    dao_ly = [
        "Cổ nhân dạy: 'Đức năng thắng số' — Lá số hay tuổi tác là thiên định, nhưng phúc đức và cách hành xử hàng ngày là nhân định.",
        "Chữ 'Nhẫn' trong gia đình: Một người nóng thì một người nên nguội; vợ chồng nhường nhịn nhau một lời thì gia đạo bình yên nghìn thuở.",
        "Sự tôn trọng và thấu hiểu lẫn nhau luôn là bùa hộ mệnh vững chắc nhất vượt lên mọi phép tra cứu phong thủy.",
    ]

    return {
        "menh": hoa_giai_menh,
        "cung": hoa_giai_cung,
        "dia_chi": hoa_giai_chi,
        "dao_ly": dao_ly,
        "cau_noi": cau_noi,
    }


def _xet_lam_an(a: dict, b: dict) -> dict:
    """Xét độ hợp tác trong kinh doanh, làm ăn buôn bán, đối tác."""
    # 1. Quý Nhân
    qn_a_cho_b = b["chi"] in QUY_NHAN.get(a["can"], [])
    qn_b_cho_a = a["chi"] in QUY_NHAN.get(b["can"], [])
    quy_nhan_loi = []
    if qn_a_cho_b:
        quy_nhan_loi.append(f"Tuổi {a['can_chi']} là Thiên Ất Quý Nhân của tuổi {b['can_chi']}: {a['can_chi']} mang lại cơ hội, định hướng sáng suốt và nâng đỡ cứu nguy khi gặp bế tắc.")
    if qn_b_cho_a:
        quy_nhan_loi.append(f"Tuổi {b['can_chi']} là Thiên Ất Quý Nhân của tuổi {a['can_chi']}: {b['can_chi']} là người trợ thủ đắc lực, đem lại vận may tài lộc cho {a['can_chi']}.")

    # 2. Thiên Lộc (Lộc Tồn)
    loc_a = LOC_TON.get(a["can"]) == b["chi"]
    loc_b = LOC_TON.get(b["can"]) == a["chi"]
    loc_loi = []
    if loc_a:
        loc_loi.append(f"Tuổi {b['can_chi']} mang Lộc Tồn của tuổi {a['can_chi']}: Hợp tác sẽ sinh tài lộc dồi dào, tiền của vào tay thuận lợi.")
    if loc_b:
        loc_loi.append(f"Tuổi {a['can_chi']} mang Lộc Tồn của tuổi {b['can_chi']}: Là người giữ của và tạo nguồn thu bền vững cho đối tác.")

    # 3. Thiên Mã (Khởi sự, xông xáo)
    ma_a = THIEN_MA.get(a["chi"]) == b["chi"]
    ma_b = THIEN_MA.get(b["chi"]) == a["chi"]
    ma_loi = []
    if ma_a or ma_b:
        ma_loi.append("Một trong hai người kích hoạt Thiên Mã của đối phương: Thích hợp mở rộng thị trường, đi công tác xa, khai phá địa bàn mới.")

    # 4. Gợi ý phân chia vai trò
    # Dựa vào ngũ hành bản mệnh & can chi
    sinh, khac = _bang_ngu_hanh()
    if a["hanh"] in ("Kim", "Thổ") and b["hanh"] in ("Hỏa", "Mộc", "Thủy"):
        vai_a = f"{a['can_chi']} ({a['nap_am']}) tính cẩn trọng, kiên định: Nên phụ trách quản lý tài chính, kế toán, ký kết hợp đồng và điều hành nội bộ."
        vai_b = f"{b['can_chi']} ({b['nap_am']}) năng động, sáng tạo: Nên phụ trách đối ngoại, bán hàng, marketing và phát triển dự án."
    elif b["hanh"] in ("Kim", "Thổ") and a["hanh"] in ("Hỏa", "Mộc", "Thủy"):
        vai_b = f"{b['can_chi']} ({b['nap_am']}) cẩn trọng, thực tế: Nên phụ trách tài chính, hậu cần và giám sát quy trình."
        vai_a = f"{a['can_chi']} ({a['nap_am']}) nhạy bén thời cuộc: Nên đứng đầu về đàm phán, tìm kiếm khách hàng và phát triển thị trường."
    else:
        vai_a = f"{a['can_chi']}: Đồng điều hành, bàn bạc kỹ lưỡng trước khi xuất vốn."
        vai_b = f"{b['can_chi']}: Đồng điều hành, phân công nhiệm vụ rõ ràng bằng văn bản pháp lý."

    loi_khuyen_kinh_doanh = [
        "Hợp đồng và sổ sách tài chính cần minh bạch tuyệt đối ngay từ ngày đầu hợp tác.",
        "Khi xảy ra bất đồng chiến lược, nên nhờ một người thứ ba có tuổi hòa hợp hoặc cố vấn chuyên môn làm trọng tài phân xử.",
        "Khai thác thế mạnh của từng người: người giỏi đối ngoại làm thị trường, người chắc tay quản trị giữ quỹ.",
    ]

    return {
        "quy_nhan": quy_nhan_loi,
        "thien_loc": loc_loi,
        "thien_ma": ma_loi,
        "phan_vai": {"nguoi_a": vai_a, "nguoi_b": vai_b},
        "loi_khuyen": loi_khuyen_kinh_doanh,
    }


def _goi_y_sinh_con(a: dict, b: dict, nam_hien_tai: int = 2026, so_nam: int = 6) -> list[dict]:
    """Phân tích các năm tiếp theo để sinh con hóa giải và tăng cường sinh khí cho bố mẹ."""
    sinh, khac = _bang_ngu_hanh()
    cau_noi = _tim_cau_noi_ngu_hanh(a["hanh"], b["hanh"])
    ket_qua = []

    for nam in range(nam_hien_tai, nam_hien_tai + so_nam):
        cc = can_chi_nam(nam)
        hanh_con = cc.nap_am_hanh
        can_con = cc.can
        chi_con = cc.chi

        # Điểm xét với bố (A) và mẹ (B)
        diem_a, diem_b = 0, 0
        ly_do_a, ly_do_b = [], []

        # Với A
        if sinh.get(hanh_con) == a["hanh"]:
            diem_a += 2; ly_do_a.append(f"Mệnh con ({hanh_con}) sinh mệnh bố ({a['hanh']})")
        elif sinh.get(a["hanh"]) == hanh_con:
            diem_a += 2; ly_do_a.append(f"Mệnh bố ({a['hanh']}) sinh mệnh con ({hanh_con})")
        elif hanh_con == a["hanh"]:
            diem_a += 1; ly_do_a.append(f"Mệnh con bình hòa với bố ({hanh_con})")
        else:
            diem_a -= 1; ly_do_a.append(f"Mệnh con và bố tương khắc ({hanh_con} — {a['hanh']})")

        if chi_con in nhom_tam_hop(a["chi"]):
            diem_a += 2; ly_do_a.append("Tam hợp chi với bố")
        elif luc_xung(a["chi"]) == chi_con:
            diem_a -= 2; ly_do_a.append("Lục xung chi với bố")

        # Với B
        if sinh.get(hanh_con) == b["hanh"]:
            diem_b += 2; ly_do_b.append(f"Mệnh con ({hanh_con}) sinh mệnh mẹ ({b['hanh']})")
        elif sinh.get(b["hanh"]) == hanh_con:
            diem_b += 2; ly_do_b.append(f"Mệnh mẹ ({b['hanh']}) sinh mệnh con ({hanh_con})")
        elif hanh_con == b["hanh"]:
            diem_b += 1; ly_do_b.append(f"Mệnh con bình hòa với mẹ ({hanh_con})")
        else:
            diem_b -= 1; ly_do_b.append(f"Mệnh con và mẹ tương khắc ({hanh_con} — {b['hanh']})")

        if chi_con in nhom_tam_hop(b["chi"]):
            diem_b += 2; ly_do_b.append("Tam hợp chi với mẹ")
        elif luc_xung(b["chi"]) == chi_con:
            diem_b -= 2; ly_do_b.append("Lục xung chi với mẹ")

        # Đóng vai trò cầu nối hóa giải bố mẹ
        la_cau_noi = False
        if cau_noi["can_hoa_giai"] and hanh_con == cau_noi["hanh_cau_noi"]:
            la_cau_noi = True
            diem_a += 3; diem_b += 3

        tong = diem_a + diem_b
        if tong >= 5 or la_cau_noi:
            danh_gia = "Rất tốt (Thượng cát)"
        elif tong >= 2:
            danh_gia = "Tốt (Cát)"
        elif tong >= 0:
            danh_gia = "Bình thường"
        else:
            danh_gia = "Cần cân nhắc"

        ghi_chu = []
        if la_cau_noi:
            ghi_chu.append(f"★ CẦU NỐI VÀNG: Mệnh con là {hanh_con} giúp hóa giải hoàn toàn tương khắc giữa bố ({a['hanh']}) và mẹ ({b['hanh']}).")
        ghi_chu.extend(ly_do_a + ly_do_b)

        ket_qua.append({
            "nam": nam,
            "can_chi": cc.ten,
            "con_giap": _con_giap(cc.chi),
            "nap_am": cc.nap_am,
            "hanh": hanh_con,
            "danh_gia": danh_gia,
            "la_cau_noi": la_cau_noi,
            "diem_tong": tong,
            "giai_thich": " · ".join(ghi_chu[:4]),
        })

    ket_qua.sort(key=lambda x: -x["diem_tong"])
    return ket_qua


def xem_hop_tuoi(nam_sinh_a: int, gioi_tinh_a: str,
                  nam_sinh_b: int, gioi_tinh_b: str,
                  muc_dich: str = "hon_nhan") -> dict:
    """Xét độ hợp tuổi toàn diện theo tri thức cổ truyền Việt Nam."""
    nam_a = nam_hop_le(nam_sinh_a, "Năm sinh người thứ nhất")
    nam_b = nam_hop_le(nam_sinh_b, "Năm sinh người thứ hai")
    gt_a = gioi_tinh_hop_le(gioi_tinh_a)
    gt_b = gioi_tinh_hop_le(gioi_tinh_b)

    la_hon_nhan = (muc_dich == "hon_nhan")

    a, b = _menh(nam_a), _menh(nam_b)
    a["gioi_tinh"] = gt_a
    b["gioi_tinh"] = gt_b

    cung_a = cung_phi(nam_a, gt_a)
    cung_b = cung_phi(nam_b, gt_b)

    # 4 mục xét cốt lõi
    muc_bm, ct_bm = _xet_ban_menh(a, b, la_hon_nhan)
    muc_tc, ct_tc = _xet_thien_can(a, b)
    muc_dc, ct_dc = _xet_dia_chi(a, b)
    muc_cp, ct_cp = _xet_cung_phi(cung_a, cung_b)

    muc = [muc_bm, muc_tc, muc_dc, muc_cp]

    # Cảnh báo thiên khắc địa xung
    canh_bao = []
    ke, bi = ((a, b) if can_khac(a["can"], b["can"]) else (b, a))
    if ((can_khac(a["can"], b["can"]) or can_khac(b["can"], a["can"]))
            and luc_xung(a["chi"]) == b["chi"]):
        canh_bao.append({
            "ten": "Thiên khắc địa xung", "diem": DIEM["thien_khac_dia_xung"],
            "giai_thich": f"Vừa can {ke['can']} khắc can {bi['can']}, vừa chi "
                          f"{a['chi']} xung chi {b['chi']}. Đây là trường hợp mọi "
                          f"trường phái đều coi là nặng nhất; dân gian khuyên nếu "
                          f"vẫn lấy nhau thì nhờ người tuổi hợp đứng ra làm mai, "
                          f"chủ hôn, và chú trọng tu dưỡng đạo đức gia đình."
        })

    diem = sum(m["diem"] for m in muc) + sum(c["diem"] for c in canh_bao)
    toi_da = (DIEM["menh_tuong_sinh"] + DIEM["can_hop"]
              + DIEM["tam_hop"] + DIEM["du_nien_tot"])

    if diem >= 8:
        danh_gia, loi = "rất hợp", "Cả bốn mặt đều thuận, tương sinh tương hợp viên mãn."
        xep_loai = "Thượng Cát (Rất hợp)"
    elif diem >= 4:
        danh_gia, loi = "hợp", "Phần hợp nhiều hơn phần khắc, gia đạo thuận hòa."
        xep_loai = "Cát (Hợp)"
    elif diem >= 0:
        danh_gia, loi = "bình thường", "Có hợp có khắc, trung bình, cần học cách bù trừ nhường nhịn."
        xep_loai = "Bình Hòa"
    elif diem >= -4:
        danh_gia, loi = "ít hợp", "Phần khắc nhiều hơn phần hợp, cần kiên nhẫn và áp dụng phép hóa giải."
        xep_loai = "Thứ Cát / Cần Hóa Giải"
    else:
        danh_gia, loi = "khắc", "Nhiều mặt khắc nhau, cần tham khảo kỹ cẩm nang hóa giải."
        xep_loai = "Hung / Cần Hóa Giải Kỹ Lưỡng"

    # Thang điểm 10 chuẩn hóa
    diem_10 = round(max(1.0, min(10.0, 5.0 + (diem / toi_da) * 5.0)), 1)
    ti_le_hop = int(diem_10 * 10)

    # Cao Ly Đầu Hình (xác định can chồng và chi vợ)
    cao_ly = None
    if gt_a == "nam" and gt_b == "nu":
        cao_ly = tra_cao_ly(a["can"], b["chi"])
    elif gt_a == "nu" and gt_b == "nam":
        cao_ly = tra_cao_ly(b["can"], a["chi"])
    else:
        cao_ly = tra_cao_ly(a["can"], b["chi"])

    # Cẩm nang hóa giải chi tiết
    hoa_giai = _phan_tich_hoa_giai(a, b, muc, muc_cp["ket_qua"])

    # Phân tích làm ăn / kinh doanh
    lam_an = _xet_lam_an(a, b)

    # Gợi ý năm sinh con
    sinh_con = _goi_y_sinh_con(a, b)

    # Bảng phân biệt Cung Sinh và Cung Phi
    so_sanh_cung = {
        "nguoi_a": {"cung_phi": cung_a["cung_phi"], "cung_sinh": a["cung_sinh"]},
        "nguoi_b": {"cung_phi": cung_b["cung_phi"], "cung_sinh": b["cung_sinh"]},
        "giai_thich": "Cung Phi (Bát Trạch) đổi theo giới tính để định phương hướng nhà ở, phối ngẫu hôn nhân. Cung Sinh (Cung Mệnh Lữ Tài) cố định theo năm sinh để định tính cách nguyên bản."
    }

    return {
        "muc_dich": muc_dich,
        "nguoi_a": {
            **a, "gioi_tinh": gt_a, "cung_phi": cung_a["cung_phi"],
            "nhom_bat_trach": cung_a["nhom"], "con_giap": _con_giap(a["chi"])
        },
        "nguoi_b": {
            **b, "gioi_tinh": gt_b, "cung_phi": cung_b["cung_phi"],
            "nhom_bat_trach": cung_b["nhom"], "con_giap": _con_giap(b["chi"])
        },
        "muc_xet": muc,
        "canh_bao": canh_bao,
        "diem": diem,
        "diem_toi_da": toi_da,
        "diem_10": diem_10,
        "ti_le_hop": ti_le_hop,
        "xep_loai": xep_loai,
        "danh_gia": danh_gia,
        "nhan_xet": loi,
        "chenh_lech_tuoi": abs(nam_a - nam_b),
        "chi_tiet": {
            "ban_menh": ct_bm,
            "thien_can": ct_tc,
            "dia_chi": ct_dc,
            "cung_phi": ct_cp,
            "so_sanh_cung": so_sanh_cung,
        },
        "cao_ly_dau_hinh": cao_ly,
        "hoa_giai": hoa_giai,
        "lam_an": lam_an,
        "sinh_con_goi_y": sinh_con,
        "luu_y": [
            "Điểm số và phân tích chỉ để xếp thứ tự đáng chú ý, không phải thước đo định mệnh của hôn nhân hay hợp tác.",
            "Từng khoản cộng trừ và yếu tố đều được liệt kê minh bạch để tự kiểm nghiệm.",
            "Đây là tri thức phong tục văn hóa dân gian; nền tảng cốt lõi của hạnh phúc gia đình và thành công kinh doanh là sự chân thành, chữ Tín, chữ Nhẫn và 'Đức năng thắng số'.",
        ],
    }


__all__ = ["xem_hop_tuoi", "DIEM"]
