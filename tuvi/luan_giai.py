# -*- coding: utf-8 -*-
"""Luận giải lá số Tử Vi từ dữ liệu trong ``data/``.

Mọi câu chữ đều ghép từ các trường ``y_nghia``, ``luan_giai``, ``chu_ve``…
trong bộ dữ liệu và một số mẫu câu cố định ở đây; mọi con số (đắc tính, điểm,
đại hạn, tuổi) đều tính ra từ lá số. Không có khâu "đoán" nào ở giữa.

Điểm gợi ý của từng cung chỉ là cách xếp thứ tự để người đọc biết cung nào đáng
chú ý trước; các khoản cộng trừ được liệt kê đầy đủ để ai cũng kiểm lại được.
"""
from __future__ import annotations

from functools import lru_cache

from .canchi import tuoi_mu
from .la_so import chinh_tinh_cung_menh
from .store import load

# Thứ tự đọc lá số theo lệ thường: Mệnh — Thân — Phúc — rồi các cung còn lại.
THU_TU_DOC = ["Mệnh", "Phúc Đức", "Quan Lộc", "Tài Bạch", "Thiên Di", "Phu Thê",
              "Tử Tức", "Điền Trạch", "Phụ Mẫu", "Huynh Đệ", "Nô Bộc", "Tật Ách"]

# Điểm gợi ý cho từng cung. Chỉ để xếp thứ tự, không phải "số phận".
DIEM_DAC_TINH = {"Miếu": 2, "Vượng": 2, "Đắc": 1, "Bình": 0, "Hãm": -2}
DIEM_TU_HOA = {"Hóa Lộc": 2, "Hóa Quyền": 1, "Hóa Khoa": 1, "Hóa Kỵ": -2}
DIEM_CAT, DIEM_HUNG = 1, -1
NGUONG_DANH_GIA = [(4, "vượng"), (2, "khá"), (0, "trung bình"), (-2, "yếu")]
DANH_GIA_THAP_NHAT = "xấu"

THAN_CU = {
    "Mệnh": "Thân cư Mệnh: Mệnh và Thân cùng một cung, đời người nhất quán, "
            "tính cách lúc trẻ thế nào về sau vẫn vậy; tự lực là chính.",
    "Phúc Đức": "Thân cư Phúc Đức: nửa đời sau nghiêng về đời sống tinh thần, "
                "hưởng phúc hay chịu thiệt tùy cung Phúc tốt xấu; nên vun bồi phúc phần.",
    "Quan Lộc": "Thân cư Quan Lộc: sự nghiệp là trục chính của cuộc đời, càng về "
                "sau công việc càng chi phối; hợp người cầu tiến, ham làm.",
    "Tài Bạch": "Thân cư Tài Bạch: về sau lấy tiền bạc, kinh doanh làm trọng; "
                "giàu nghèo gắn với cung Tài, nên xem kỹ cung này.",
    "Thiên Di": "Thân cư Thiên Di: đời hay đi xa, lập nghiệp xa quê hoặc nhờ giao "
                "thiệp bên ngoài mà nên; ở yên một chỗ khó phát.",
    "Phu Thê": "Thân cư Phu Thê: hôn nhân ảnh hưởng lớn đến nửa đời sau, thành bại "
               "có phần nhờ hoặc vì bạn đời; nên chọn bạn đời kỹ.",
}

QUAN_HE_MENH_CUC = {
    "cuc_sinh_menh": ("Cục sinh Mệnh", "Hoàn cảnh nâng đỡ bản thân: gặp thời dễ "
                      "phát, ít phải gắng gượng; là quan hệ thuận nhất."),
    "menh_sinh_cuc": ("Mệnh sinh Cục", "Bản thân phải bỏ sức nuôi hoàn cảnh: "
                      "hay lo cho người khác, được việc nhưng hao tâm lực."),
    "menh_khac_cuc": ("Mệnh khắc Cục", "Bản thân làm chủ hoàn cảnh: quyết đoán, "
                      "tự lập, nhưng vất vả vì phải tự mở đường."),
    "cuc_khac_menh": ("Cục khắc Mệnh", "Hoàn cảnh chi phối bản thân: dễ bị động, "
                      "cần kiên nhẫn và dựa vào cát tinh ở Mệnh — Thân."),
    "cung_hanh": ("Mệnh và Cục cùng hành", "Trong ngoài hòa hợp, đời ổn định, "
                  "ít đột biến; hợp với lối đi bền hơn lối đi nhanh."),
}

AM_DUONG_LY = {
    True: ("Âm dương thuận lý", "Dương nam hoặc Âm nữ: đại hạn đi thuận, đường "
           "đời khai mở sớm, trẻ đã có hướng."),
    False: ("Âm dương nghịch lý", "Âm nam hoặc Dương nữ: đại hạn đi nghịch, khởi "
            "đầu chậm hơn nhưng càng về sau càng vững; không phải xấu."),
}

TU_HOA_Y = {
    "Hóa Lộc": "tài lộc, may mắn và cơ hội đến từ lĩnh vực này",
    "Hóa Quyền": "quyền hành, tính chủ động và khả năng nắm việc ở lĩnh vực này",
    "Hóa Khoa": "danh tiếng, học vấn và quý nhân hóa giải khó khăn ở lĩnh vực này",
    "Hóa Kỵ": "điểm nghẽn của lá số: lĩnh vực này dễ trắc trở, hao tổn, cần đề phòng",
}


# ----------------------------------------------------------------------------
# Tra cứu dữ liệu
# ----------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _tu_dien_sao() -> dict[str, dict]:
    """Tra sao theo tên viết thường, vì lá số và dữ liệu viết hoa khác nhau."""
    return {s["ten"].lower(): s for s in load("tu_vi/sao")}


@lru_cache(maxsize=1)
def _tu_dien_cung() -> dict[str, dict]:
    return {c["ten"]: c for c in load("tu_vi/cung")}


@lru_cache(maxsize=1)
def _tu_dien_nap_am() -> dict[str, dict]:
    return {n["ten"]: n for n in load("nap_am")}


@lru_cache(maxsize=1)
def _tu_dien_ngu_hanh() -> dict[str, dict]:
    return {h["hanh"]: h for h in load("ngu_hanh")}


@lru_cache(maxsize=1)
def _tu_dien_cuc() -> dict[int, dict]:
    return {c["so"]: c for c in load("tu_vi/cuc")["cuc"]}


def tra_sao(ten: str) -> dict | None:
    """Bản ghi một sao theo tên, không phân biệt hoa thường."""
    return _tu_dien_sao().get(ten.lower())


def bo_sung_y_nghia_sao(cung: dict) -> dict:
    """Gắn ý nghĩa, tính chất, loại, hành và đắc tính cho từng sao trong cung."""
    tu_dien = _tu_dien_sao()
    sao = []
    for s in cung["sao"]:
        goc = tu_dien.get(s["ten"].lower(), {})
        sao.append({
            **s,
            "tinh_chat": goc.get("tinh_chat", "trung tính"),
            "loai": goc.get("loai", ""),
            "hanh": goc.get("hanh", ""),
            "y_nghia": goc.get("y_nghia", ""),
            "dac_tinh": goc.get("mieu_vuong_dac_ham", {}).get(cung["chi"]),
        })
    return {**cung, "sao": sao}


def _da_bo_sung(ls: dict) -> bool:
    return all("tinh_chat" in s for c in ls["cac_cung"] for s in c["sao"])


# ----------------------------------------------------------------------------
# Cách cục
# ----------------------------------------------------------------------------
def goi_y_cach_cuc(ls: dict) -> list[dict]:
    """Cách cục nhận ra được, dựa trên chính tinh tại Mệnh và tam hợp Mệnh."""
    cung = {c["ten_cung"]: c for c in ls["cac_cung"]}
    menh = cung["Mệnh"]
    ten_sao = {s["ten"] for s in menh["sao"]}
    # Tam hợp Mệnh: Mệnh, Quan Lộc, Tài Bạch, cộng cung Thiên Di đối chiếu.
    hoi = set()
    for k in ("Mệnh", "Quan Lộc", "Tài Bạch", "Thiên Di"):
        hoi |= {s["ten"] for s in cung[k]["sao"]}
    ra = []
    for c in load("tu_vi/cach_cuc"):
        t = c["ten"]
        khop = False
        if t == "Sát Phá Tham":
            khop = {"Thất Sát", "Phá Quân", "Tham Lang"} <= hoi
        elif t == "Cơ Nguyệt Đồng Lương":
            khop = {"Thiên Cơ", "Thái Âm", "Thiên Đồng", "Thiên Lương"} <= hoi
        elif t == "Tử Phủ Vũ Tướng":
            khop = {"Tử Vi", "Thiên Phủ", "Vũ Khúc", "Thiên Tướng"} <= hoi
        elif t == "Phủ Tướng triều viên":
            khop = {"Thiên Phủ", "Thiên Tướng"} <= hoi
        elif t == "Lộc Mã giao trì":
            khop = {"Lộc Tồn", "Thiên Mã"} <= hoi or {"Hóa Lộc", "Thiên Mã"} <= hoi
        elif t == "Song Lộc triều viên":
            khop = {"Lộc Tồn", "Hóa Lộc"} <= hoi
        elif t == "Tam hóa liên châu":
            khop = {"Hóa Lộc", "Hóa Quyền", "Hóa Khoa"} <= hoi
        elif t == "Tham Vũ đồng hành":
            khop = {"Tham Lang", "Vũ Khúc"} <= hoi
        elif t == "Mệnh vô chính diệu":
            khop = not chinh_tinh_cung_menh(ls)
        elif t == "Thạch trung ẩn ngọc":
            khop = "Cự Môn" in ten_sao and menh["chi"] in ("Tý", "Ngọ")
        elif t == "Mã đầu đới kiếm":
            khop = "Kình Dương" in ten_sao and menh["chi"] == "Ngọ"
        elif t == "Hỏa Tham / Linh Tham":
            khop = "Tham Lang" in ten_sao and bool(
                {"Hỏa Tinh", "Linh Tinh"} & ten_sao)
        elif t == "Khôi Việt giáp Mệnh":
            khop = _giap(ls, menh, {"Thiên Khôi", "Thiên Việt"})
        elif t == "Xương Khúc giáp Mệnh":
            khop = _giap(ls, menh, {"Văn Xương", "Văn Khúc"})
        if khop:
            ra.append(c)
    return ra


def _giap(ls: dict, menh: dict, cap: set[str]) -> bool:
    """Hai sao nằm ở hai cung kề trái phải của cung Mệnh."""
    chi_list = [c["chi"] for c in ls["cac_cung"]]
    i = chi_list.index(menh["chi"])
    ben = [ls["cac_cung"][(i - 1) % 12], ls["cac_cung"][(i + 1) % 12]]
    co = {s["ten"] for c in ben for s in c["sao"]}
    return cap <= co


# ----------------------------------------------------------------------------
# Từng phần của luận giải
# ----------------------------------------------------------------------------
def _quan_he_hanh(a: str, b: str) -> str:
    """Quan hệ ngũ hành của a đối với b: sinh, khắc, bị sinh, bị khắc, cùng."""
    if a == b:
        return "cung"
    h = _tu_dien_ngu_hanh()[a]
    if h["sinh"] == b:
        return "sinh"
    if h["khac"] == b:
        return "khac"
    if h["duoc_sinh_boi"] == b:
        return "duoc_sinh"
    return "bi_khac"


def _tong_quan(ls: dict) -> dict:
    nap_am = _tu_dien_nap_am().get(ls["menh_nap_am"], {})
    hanh_menh = nap_am.get("hanh") or ls["menh_nap_am"].split()[-1]
    cuc = _tu_dien_cuc()[ls["so_cuc"]]
    hanh_cuc = cuc["hanh"]
    qh = _quan_he_hanh(hanh_cuc, hanh_menh)
    ma = {"sinh": "cuc_sinh_menh", "duoc_sinh": "menh_sinh_cuc",
          "khac": "cuc_khac_menh", "bi_khac": "menh_khac_cuc",
          "cung": "cung_hanh"}[qh]
    ten_qh, y_qh = QUAN_HE_MENH_CUC[ma]
    thuan = ls["chieu_di_han"] == "thuận"
    ten_ad, y_ad = AM_DUONG_LY[thuan]
    ngu_hanh = _tu_dien_ngu_hanh().get(hanh_menh, {})
    return {
        "ban_menh": {"nap_am": ls["menh_nap_am"], "hanh": hanh_menh,
                     "y_nghia": nap_am.get("y_nghia", ""),
                     "tinh_cach_hanh": ngu_hanh.get("tinh_cach", ""),
                     "nghe_hop_hanh": ngu_hanh.get("nghe", [])},
        "cuc": {"ten": cuc["ten"], "hanh": hanh_cuc, "so": ls["so_cuc"],
                "y_nghia": cuc.get("y_nghia", "")},
        "menh_cuc": {"quan_he": ten_qh, "nhan_xet": y_qh},
        "am_duong": {"ten": ten_ad, "am_duong_nam_sinh": ls["am_duong_nam_sinh"],
                     "gioi_tinh": ls["gioi_tinh"], "thuan_ly": thuan,
                     "nhan_xet": y_ad},
        "than": {"cung": ls["cung_than_tai"],
                 "nhan_xet": THAN_CU.get(ls["cung_than_tai"], "")},
    }


def _tu_hoa(ls: dict) -> list[dict]:
    cung_theo_sao = {}
    for c in ls["cac_cung"]:
        for s in c["sao"]:
            cung_theo_sao.setdefault(s["ten"], c)
    ra = []
    for hoa, sao in ls["tu_hoa"].items():
        c = cung_theo_sao.get(sao)
        if not c:
            # Chủ tinh chưa được an trong bản rút gọn (Văn Xương, Tả Phù...).
            ra.append({"hoa": hoa, "sao": sao, "cung": None, "chi": None,
                       "chu_ve": None, "nhan_xet": f"{hoa} theo {sao}; sao này "
                       "chưa được an trong bản rút gọn nên không rõ rơi vào cung nào."})
            continue
        ra.append({
            "hoa": hoa, "sao": sao, "cung": c["ten_cung"], "chi": c["chi"],
            "chu_ve": c["chu_ve"],
            "nhan_xet": f"{hoa} theo {sao} vào cung {c['ten_cung']} "
                        f"({c['chu_ve'].lower()}): {TU_HOA_Y[hoa]}.",
        })
    return ra


def _ten_chinh_tinh(c: dict) -> list[str]:
    return [s["ten"] for s in c["sao"] if s["nhom"] == "Chính tinh"]


def _luan_mot_cung(ls: dict, i: int) -> dict:
    cac = ls["cac_cung"]
    c = cac[i]
    info = _tu_dien_cung()[c["ten_cung"]]
    chinh = [s for s in c["sao"] if s["nhom"] == "Chính tinh"]
    phu = [s for s in c["sao"] if s["nhom"] != "Chính tinh"]
    tu_hoa = [s for s in phu if s["nhom"] == "Tứ Hóa"]
    cat = [s for s in phu if s["tinh_chat"] == "cát" and s["nhom"] != "Tứ Hóa"]
    hung = [s for s in phu if s["tinh_chat"] == "hung" and s["nhom"] != "Tứ Hóa"]
    trung = [s for s in phu if s not in cat and s not in hung and s not in tu_hoa]

    tam_hop = [cac[(i + 4) % 12], cac[(i + 8) % 12]]
    xung = cac[(i + 6) % 12]

    # Điểm gợi ý, liệt kê từng khoản để kiểm lại được.
    khoan: list[dict] = []
    for s in chinh:
        d = DIEM_DAC_TINH.get(s.get("dac_tinh") or "", 0)
        khoan.append({"ly_do": f"{s['ten']} {s.get('dac_tinh') or 'không rõ đắc tính'}",
                      "diem": d})
    if not chinh:
        # Vô chính diệu: mượn chính tinh cung xung chiếu, tính nửa điểm vì sao
        # mượn không mạnh bằng sao tọa thủ.
        for s in xung["sao"]:
            if s["nhom"] != "Chính tinh":
                continue
            d = DIEM_DAC_TINH.get(s.get("dac_tinh") or "", 0)
            khoan.append({"ly_do": f"mượn {s['ten']} {s.get('dac_tinh') or ''} "
                                   f"từ {xung['ten_cung']}".strip(),
                          "diem": int(d / 2)})
    for s in cat:
        khoan.append({"ly_do": f"cát tinh {s['ten']}", "diem": DIEM_CAT})
    for s in hung:
        khoan.append({"ly_do": f"sát tinh {s['ten']}", "diem": DIEM_HUNG})
    for s in tu_hoa:
        khoan.append({"ly_do": s["ten"], "diem": DIEM_TU_HOA.get(s["ten"], 0)})
    diem = sum(k["diem"] for k in khoan)
    danh_gia = DANH_GIA_THAP_NHAT
    for nguong, ten in NGUONG_DANH_GIA:
        if diem >= nguong:
            danh_gia = ten
            break

    # Đoạn văn ghép từ dữ liệu.
    doan = [f"Cung {c['ten_cung']} đóng tại {c['can']} {c['chi']}, chủ về "
            f"{c['chu_ve'].lower()}. {info['cach_doc']}"]
    if chinh:
        for s in chinh:
            dt = f" ({s['dac_tinh']} địa)" if s.get("dac_tinh") else ""
            doan.append(f"Chính tinh {s['ten']}{dt}: {s['y_nghia']}")
    else:
        muon = _ten_chinh_tinh(xung)
        doan.append(
            f"Cung không có chính tinh (vô chính diệu), theo lệ mượn chính tinh "
            f"cung {xung['ten_cung']} xung chiếu là "
            f"{' + '.join(muon) if muon else 'cũng không có chính tinh'} để luận; "
            f"cung vô chính diệu thường thiếu chủ kiến, dễ chịu ảnh hưởng bên ngoài.")
    if tu_hoa:
        doan.append("Có " + ", ".join(s["ten"] for s in tu_hoa) + " đóng tại đây: "
                    + "; ".join(TU_HOA_Y[s["ten"]] for s in tu_hoa) + ".")
    if cat:
        doan.append("Cát tinh hội: " + ", ".join(s["ten"] for s in cat) + ".")
    if hung:
        doan.append("Sát tinh, bại tinh: " + ", ".join(s["ten"] for s in hung) + ".")
    if cat and hung:
        can = ("cát nhiều hơn hung, nhìn chung tốt" if len(cat) > len(hung)
               else "hung nhiều hơn cát, cần thận trọng" if len(hung) > len(cat)
               else "cát hung ngang nhau, tốt xấu đan xen")
        doan.append(f"Cân bằng: {can}.")
    hop = [f"{t['ten_cung']} ({' + '.join(_ten_chinh_tinh(t)) or 'vô chính diệu'})"
           for t in tam_hop]
    doan.append(f"Tam hợp chiếu về từ {hop[0]} và {hop[1]}; xung chiếu từ "
                f"{xung['ten_cung']} ({' + '.join(_ten_chinh_tinh(xung)) or 'vô chính diệu'}).")
    if c["la_cung_than"]:
        doan.append("Đây cũng là cung an Thân, ảnh hưởng mạnh từ trung niên trở đi.")

    return {
        "ten_cung": c["ten_cung"], "chi": c["chi"], "can": c["can"],
        "chu_ve": c["chu_ve"], "cach_doc": info["cach_doc"],
        "noi_dung_xem": info["noi_dung_xem"],
        "la_cung_than": c["la_cung_than"], "dai_han": c["dai_han"],
        "vo_chinh_dieu": not chinh,
        "chinh_tinh": [{"ten": s["ten"], "dac_tinh": s.get("dac_tinh"),
                        "y_nghia": s["y_nghia"]} for s in chinh],
        "muon_chinh_tinh": _ten_chinh_tinh(xung) if not chinh else [],
        "tu_hoa": [s["ten"] for s in tu_hoa],
        "cat_tinh": [{"ten": s["ten"], "y_nghia": s["y_nghia"]} for s in cat],
        "sat_tinh": [{"ten": s["ten"], "y_nghia": s["y_nghia"]} for s in hung],
        "trung_tinh": [s["ten"] for s in trung],
        "tam_hop": [{"ten_cung": t["ten_cung"], "chi": t["chi"],
                     "chinh_tinh": _ten_chinh_tinh(t)} for t in tam_hop],
        "xung_chieu": {"ten_cung": xung["ten_cung"], "chi": xung["chi"],
                       "chinh_tinh": _ten_chinh_tinh(xung)},
        "diem": diem, "danh_gia": danh_gia, "khoan_diem": khoan,
        "luan": " ".join(doan),
    }


def _dai_han(ls: dict, nam_xem: int | None) -> dict:
    """Bảng 12 đại hạn theo thứ tự thời gian, đánh dấu hạn đang đi."""
    tuoi = tuoi_mu(ls["am_lich"]["nam"], nam_xem) if nam_xem else None
    bang = []
    for c in ls["cac_cung"]:
        dau, cuoi = (int(x) for x in c["dai_han"].split("-"))
        bang.append({
            "tuoi": c["dai_han"], "tu": dau, "den": cuoi,
            "cung": c["ten_cung"], "chi": c["chi"],
            "chinh_tinh": _ten_chinh_tinh(c),
            "tu_hoa": [s["ten"] for s in c["sao"] if s["nhom"] == "Tứ Hóa"],
            "hien_tai": tuoi is not None and dau <= tuoi <= cuoi,
        })
    bang.sort(key=lambda h: h["tu"])
    hien_tai = next((h for h in bang if h["hien_tai"]), None)
    return {"nam_xem": nam_xem, "tuoi_mu": tuoi, "hien_tai": hien_tai,
            "bang": bang,
            "ghi_chu": "Mỗi đại hạn 10 năm, khởi từ số Cục tại cung Mệnh; "
                       f"lá số này đi {ls['chieu_di_han']}. Đại hạn đóng ở cung nào "
                       "thì 10 năm đó mang màu sắc của cung ấy."}


# ----------------------------------------------------------------------------
# Hàm chính
# ----------------------------------------------------------------------------
def luan_giai_la_so(ls: dict, nam_xem: int | None = None) -> dict:
    """Luận giải chi tiết một lá số đã lập bằng ``la_so.lap_la_so``.

    ``nam_xem`` (dương lịch) để đánh dấu đại hạn đang đi; bỏ trống thì chỉ liệt kê.
    """
    if not _da_bo_sung(ls):
        ls = {**ls, "cac_cung": [bo_sung_y_nghia_sao(c) for c in ls["cac_cung"]]}
    vi_tri = {c["ten_cung"]: i for i, c in enumerate(ls["cac_cung"])}
    cac_cung = [_luan_mot_cung(ls, vi_tri[t]) for t in THU_TU_DOC]
    # Cung Thân được đọc ngay sau Mệnh nếu Thân không cư Mệnh.
    if ls["cung_than_tai"] != "Mệnh":
        than = next(c for c in cac_cung if c["ten_cung"] == ls["cung_than_tai"])
        cac_cung.remove(than)
        cac_cung.insert(1, than)
    diem_tb = round(sum(c["diem"] for c in cac_cung) / 12, 2)
    return {
        "tong_quan": _tong_quan(ls),
        "tu_hoa": _tu_hoa(ls),
        "cach_cuc": goi_y_cach_cuc(ls),
        "cac_cung": cac_cung,
        "dai_han": _dai_han(ls, nam_xem),
        "thong_ke": {
            "diem_trung_binh": diem_tb,
            "cung_manh_nhat": max(cac_cung, key=lambda c: c["diem"])["ten_cung"],
            "cung_yeu_nhat": min(cac_cung, key=lambda c: c["diem"])["ten_cung"],
            "so_cung_vo_chinh_dieu": sum(1 for c in cac_cung if c["vo_chinh_dieu"]),
        },
        "luu_y": [
            "Bản an sao rút gọn có 55 sao, chưa đủ 109 sao; các cách cục cần sao "
            "phụ (Hỏa, Linh, Không, Kiếp...) chưa nhận ra được.",
            "Điểm từng cung chỉ để xếp thứ tự đáng chú ý, các khoản cộng trừ được "
            "liệt kê để kiểm lại; không phải thước đo số phận.",
            "Đây là tri thức văn hóa dân gian, dùng để tham khảo; không thay thế "
            "tư vấn y tế, pháp lý hay tài chính.",
        ],
    }


__all__ = ["luan_giai_la_so", "bo_sung_y_nghia_sao", "goi_y_cach_cuc", "tra_sao",
           "THU_TU_DOC"]
