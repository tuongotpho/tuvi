# -*- coding: utf-8 -*-
"""Xem tuổi hai người có hợp nhau không — theo lối dân gian Việt Nam.

Bốn phép xét, mỗi phép đều tính lại được từ dữ liệu trong ``data/`` chứ không
chép sẵn kết luận ở đâu:

1. **Bản mệnh** — ngũ hành nạp âm của hai tuổi: tương sinh, bình hòa hay tương khắc.
   Kèm ghi chú vài nạp âm dân gian coi là "không sợ" hành khắc mình (SOURCES.md mục G).
2. **Thiên can** — ngũ hợp (Giáp Kỷ, Ất Canh, Bính Tân, Đinh Nhâm, Mậu Quý),
   tứ xung (Giáp Canh, Ất Tân, Bính Nhâm, Đinh Quý), hay chỉ khắc nhau.
3. **Địa chi** — tam hợp, lục hợp (tốt); lục xung, lục hại, lục phá, tương hình (xấu).
4. **Cung phi bát trạch** — lấy cung phi người này soi vào cung phi người kia
   theo bảng Đại du niên: Sinh Khí, Thiên Y, Diên Niên, Phục Vị là tốt;
   Tuyệt Mệnh, Ngũ Quỷ, Lục Sát, Họa Hại là xấu.

Thêm một mục cảnh báo riêng: **thiên khắc địa xung** — vừa can khắc can vừa chi
xung chi. Đây là trường hợp mọi trường phái đều coi là nặng nhất.

Riêng khi xem **hôn nhân** (một nam một nữ) có thêm:

- **Cao Ly Đầu Hình** — can chồng phối chi vợ, lời xưa chép nguyên văn từ
  ``data/hop_tuoi/cao_ly_dau_hinh.json``; kho không chấm điểm phần này.
- **Hành trung gian** khi hai mệnh khắc nhau (A khắc B thì lấy C mà A sinh C,
  C sinh B) và các năm tới có mệnh con mang hành đó.

**Điểm số chỉ để xếp thứ tự đáng chú ý**, không phải thước đo hôn nhân. Từng
khoản cộng trừ đều được liệt kê ra để người đọc tự kiểm lại và tự bỏ khoản nào
họ không tin. Các trường phái cân nặng nhẹ khác nhau; lựa chọn của kho này ghi
trong SOURCES.md mục E và G.
"""
from __future__ import annotations

from datetime import date

from .canchi import (HANH_CAN, THIEN_CAN, can_chi_nam, can_khac, luc_xung,
                     nhom_tam_hop, quan_he_chi)
from .kiem_tra import LoiDauVao, gioi_tinh_hop_le, nam_hop_le
from .phong_thuy import cung_phi
from .store import load

# Ngũ hành tương sinh: Mộc sinh Hỏa, Hỏa sinh Thổ, Thổ sinh Kim, Kim sinh Thủy,
# Thủy sinh Mộc. Tra từ data/ngu_hanh.json để không chép bảng ra hai nơi.
_SINH: dict[str, str] = {}
_KHAC: dict[str, str] = {}


def _bang_ngu_hanh() -> tuple[dict, dict]:
    if not _SINH:
        for h in load("ngu_hanh"):
            _SINH[h["hanh"]] = h["sinh"]
            _KHAC[h["hanh"]] = h["khac"]
    return _SINH, _KHAC


DIEM = {   # mỗi khoản đáng bao nhiêu điểm; đổi ở đây là đổi cả cách chấm
    "menh_tuong_sinh": 3, "menh_binh_hoa": 1, "menh_tuong_khac": -3,
    "can_ngu_hop": 2, "can_hop": 1, "can_khac": -2,
    "tam_hop": 3, "luc_hop": 3, "luc_xung": -4, "luc_hai": -2,
    "luc_pha": -1, "tuong_hinh": -2,
    "du_nien_tot": 3, "du_nien_xau": -3,
    "thien_khac_dia_xung": -3,
}

MUC_DICH = {"hon_nhan": "Hôn nhân", "lam_an": "Làm ăn"}

# Ngũ hợp thiên can và hành hợp hóa; tên gọi theo Tam Mệnh Thông Hội
# (三命通會, "論十干合"). Cặp nào cũng là can dương khắc can âm, nên ngũ hợp
# được xét TRƯỚC can khắc.
NGU_HOP_CAN: dict[frozenset, tuple[str, str]] = {
    frozenset(("Giáp", "Kỷ")): ("Thổ", "Trung Chính chi hợp"),
    frozenset(("Ất", "Canh")): ("Kim", "Nhân Nghĩa chi hợp"),
    frozenset(("Bính", "Tân")): ("Thủy", "Uy Chế chi hợp"),
    frozenset(("Đinh", "Nhâm")): ("Mộc", "Dâm Nặc chi hợp"),
    frozenset(("Mậu", "Quý")): ("Hỏa", "Vô Tình chi hợp"),
}

# Tứ xung thiên can (天干四衝). Mậu Kỷ ở trung ương nên không xung.
TU_XUNG_CAN = {frozenset(p) for p in (("Giáp", "Canh"), ("Ất", "Tân"),
                                      ("Bính", "Nhâm"), ("Đinh", "Quý"))}

# Nạp âm dân gian coi là không sợ hành vẫn khắc mình. Chỉ giữ những nạp âm có
# ít nhất hai nguồn cùng nói (SOURCES.md mục G); chỉ ghi chú, KHÔNG đổi điểm.
NAP_AM_KHONG_SO = {
    "Kiếm Phong Kim": ("Hỏa", "vàng mũi kiếm cần lửa rèn mới sắc"),
    "Thiên Hà Thủy": ("Thổ", "nước trên trời, đất không ngăn được"),
    "Đại Hải Thủy": ("Thổ", "nước biển lớn, đất không lấp được"),
    "Thiên Thượng Hỏa": ("Thủy", "lửa trên trời, nước khó dập"),
    "Tích Lịch Hỏa": ("Thủy", "lửa sấm sét đi cùng mưa giông"),
}


def _menh(nam_am: int) -> dict:
    cc = can_chi_nam(nam_am)
    nap = cung_phi(nam_am, "nam")   # chỉ lấy nạp âm, không phụ thuộc giới tính
    return {"nam": nam_am, "can_chi": f"{cc.can} {cc.chi}", "can": cc.can,
            "chi": cc.chi, "nap_am": nap["menh_nap_am"], "hanh": nap["hanh_nap_am"]}


def _xet_ban_menh(a: dict, b: dict) -> dict:
    sinh, khac = _bang_ngu_hanh()
    ha, hb = a["hanh"], b["hanh"]
    if ha == hb:
        return {"muc": "Bản mệnh", "ket_qua": "Bình hòa", "tinh_chat": "trung bình",
                "diem": DIEM["menh_binh_hoa"],
                "giai_thich": f"Hai người cùng hành {ha} — không sinh không khắc, "
                              f"hợp tính nhau nhưng ít bổ khuyết cho nhau."}
    if sinh.get(ha) == hb or sinh.get(hb) == ha:
        nguoi_sinh, nguoi_duoc = (a, b) if sinh.get(ha) == hb else (b, a)
        return {"muc": "Bản mệnh", "ket_qua": "Tương sinh", "tinh_chat": "tốt",
                "diem": DIEM["menh_tuong_sinh"],
                "giai_thich": f"{nguoi_sinh['hanh']} sinh {nguoi_duoc['hanh']}: "
                              f"tuổi {nguoi_sinh['can_chi']} ({nguoi_sinh['nap_am']}) "
                              f"nâng đỡ tuổi {nguoi_duoc['can_chi']} "
                              f"({nguoi_duoc['nap_am']}). Đây là quan hệ thuận nhất."}
    nguoi_khac, nguoi_bi = (a, b) if khac.get(ha) == hb else (b, a)
    loi = (f"{nguoi_khac['hanh']} khắc {nguoi_bi['hanh']}: "
           f"tuổi {nguoi_khac['can_chi']} ({nguoi_khac['nap_am']}) khắc "
           f"tuổi {nguoi_bi['can_chi']} ({nguoi_bi['nap_am']}). "
           f"Dân gian kiêng, nhưng nhiều nhà vẫn ở với nhau êm — "
           f"xem thêm ba mục còn lại rồi hãy kết luận.")
    ngoai_le = NAP_AM_KHONG_SO.get(nguoi_bi["nap_am"])
    if ngoai_le and ngoai_le[0] == nguoi_khac["hanh"]:
        loi += (f" Ghi chú: dân gian cho rằng {nguoi_bi['nap_am']} không sợ "
                f"{ngoai_le[0]} ({ngoai_le[1]}); các sách không thống nhất nên "
                f"điểm vẫn tính là khắc.")
    return {"muc": "Bản mệnh", "ket_qua": "Tương khắc", "tinh_chat": "xấu",
            "diem": DIEM["menh_tuong_khac"], "giai_thich": loi}


def _xet_thien_can(a: dict, b: dict) -> dict:
    cap = frozenset((a["can"], b["can"]))
    hop = NGU_HOP_CAN.get(cap)
    if hop:
        return {"muc": "Thiên can", "ket_qua": f"Ngũ hợp hóa {hop[0]}", "tinh_chat": "tốt",
                "diem": DIEM["can_ngu_hop"],
                "giai_thich": f"Can {a['can']} và can {b['can']} là một cặp ngũ hợp, "
                              f"hợp hóa {hop[0]} (sách Tam Mệnh Thông Hội gọi là "
                              f"\"{hop[1]}\"). Hành hai can vốn khắc nhau nhưng "
                              f"hợp được nhau nên xếp vào loại tốt."}
    if can_khac(a["can"], b["can"]) or can_khac(b["can"], a["can"]):
        ke, bi = ((a, b) if can_khac(a["can"], b["can"]) else (b, a))
        xung = cap in TU_XUNG_CAN
        return {"muc": "Thiên can", "ket_qua": "Can xung" if xung else "Can khắc",
                "tinh_chat": "xấu", "diem": DIEM["can_khac"],
                "giai_thich": f"Can {ke['can']} ({HANH_CAN[THIEN_CAN.index(ke['can'])]}) "
                              f"khắc can {bi['can']} "
                              f"({HANH_CAN[THIEN_CAN.index(bi['can'])]}): dễ va chạm "
                              f"trong cách nghĩ, cách quyết việc."
                              + (f" Cặp này còn nằm trong tứ xung thiên can "
                                 f"(Giáp Canh, Ất Tân, Bính Nhâm, Đinh Quý)."
                                 if xung else "")}
    return {"muc": "Thiên can", "ket_qua": "Không khắc", "tinh_chat": "tốt",
            "diem": DIEM["can_hop"],
            "giai_thich": f"Can {a['can']} và can {b['can']} không khắc nhau."}


def _xet_dia_chi(a: dict, b: dict) -> dict:
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
    if not quan_he:
        return {"muc": "Địa chi", "ket_qua": "Bình thường", "tinh_chat": "trung bình",
                "diem": 0, "quan_he": [],
                "giai_thich": f"Chi {a['chi']} và {b['chi']} không nằm trong nhóm hợp "
                              f"nào, cũng không xung hại gì nhau."}
    manh = " và ".join(quan_he)
    if tot and not xau:
        loi = (f"Chi {a['chi']} — {b['chi']} {manh.lower()}: hợp ý nhau, "
               f"dễ đồng thuận.")
        if "Tam hợp" in tot:
            loi += f" Nhóm tam hợp: {' — '.join(nhom_tam_hop(a['chi']))}."
        tc = "tốt"
    elif xau and not tot:
        loi = (f"Chi {a['chi']} — {b['chi']} {manh.lower()}: hay bất đồng, "
               f"cần nhường nhau.")
        if "Lục xung" in xau:
            loi += f" Lục xung là cặp đối nhau trên vòng địa chi ({a['chi']} xung {luc_xung(a['chi'])})."
        tc = "xấu"
    elif tot and xau:
        loi = (f"Chi {a['chi']} — {b['chi']} vừa {' vừa '.join(q.lower() for q in quan_he)}: "
               f"vừa hút vừa đẩy, lúc rất hợp lúc rất căng.")
        tc = "trung bình"
    else:
        # Quan hệ không tốt không xấu, ví dụ "Trùng chi" (hai người cùng con giáp).
        loi = (f"Chi {a['chi']} — {b['chi']}: {manh.lower()}. "
               f"Không nằm trong nhóm hợp nào, cũng không xung hại gì nhau."
               + (" Cùng tuổi thì dễ hiểu nhau nhưng cũng dễ cùng lúc gặp hạn, "
                  "vì vòng Thái Tuế của hai người trùng nhau."
                  if a["chi"] == b["chi"] else ""))
        tc = "trung bình"
    return {"muc": "Địa chi", "ket_qua": manh, "tinh_chat": tc, "diem": diem,
            "quan_he": quan_he, "giai_thich": loi}


def _xet_cung_phi(a_cung: dict, b_cung: dict) -> dict:
    bang = {c["ten"]: c for c in load("phong_thuy/bat_trach")["cung"]}
    y_nghia = {d["ten"]: d for d in load("phong_thuy/bat_trach")["du_nien"]}
    ten = bang[a_cung["cung_phi"]]["du_nien"][bang[b_cung["cung_phi"]]["huong"]]
    d = y_nghia[ten]
    tot = d["tinh_chat"] == "tốt"
    cung_nhom = a_cung["nhom"] == b_cung["nhom"]
    return {"muc": "Cung phi", "ket_qua": ten, "tinh_chat": d["tinh_chat"],
            "diem": DIEM["du_nien_tot"] if tot else DIEM["du_nien_xau"],
            "cung_a": a_cung["cung_phi"], "cung_b": b_cung["cung_phi"],
            "cung_nhom": cung_nhom,
            "giai_thich": f"Cung {a_cung['cung_phi']} soi sang cung "
                          f"{b_cung['cung_phi']} được du niên {ten} — {d['y_nghia']} "
                          + ("Hai người cùng nhóm "
                             f"{a_cung['nhom']}, chọn hướng nhà dễ thống nhất."
                             if cung_nhom else
                             f"Hai người khác nhóm ({a_cung['nhom']} và "
                             f"{b_cung['nhom']}), chọn hướng nhà sẽ phải nhường nhau.")}


def cao_ly_dau_hinh(can_chong: str, chi_vo: str) -> dict:
    """Lời Cao Ly Đầu Hình (can chồng phối chi vợ), chép nguyên văn."""
    bo = load("hop_tuoi/cao_ly_dau_hinh")
    for c in bo["cap"]:
        if c["can_chong"] == can_chong and c["chi_vo"] == chi_vo:
            return {"can_chong": can_chong, "chi_vo": chi_vo, "loi": c["loi"],
                    "nguon": bo["nguon"]}
    raise KeyError((can_chong, chi_vo))


def hanh_trung_gian(ha: str, hb: str) -> dict | None:
    """Hai hành khắc nhau thì lấy hành đứng giữa: A khắc B → A sinh C, C sinh B.

    Không khắc nhau thì trả None.
    """
    sinh, khac = _bang_ngu_hanh()
    if khac.get(ha) == hb:
        ke, bi = ha, hb
    elif khac.get(hb) == ha:
        ke, bi = hb, ha
    else:
        return None
    c = sinh[ke]
    return {"hanh": c, "ke_khac": ke, "bi_khac": bi,
            "giai_thich": f"{ke} khắc {bi}. Hành đứng giữa là {c}: {ke} sinh {c}, "
                          f"{c} sinh {bi}. Dân gian chọn năm sinh con mang mệnh {c} "
                          f"để nối hai mệnh khắc nhau của bố mẹ."}


def goi_y_nam_sinh_con(bo: dict, me: dict, nam_dau: int | None = None,
                       so_nam: int = 6) -> list[dict]:
    """Liệt kê quan hệ của mệnh và chi từng năm tới với bố và mẹ.

    Mỗi khoản cộng trừ ghi rõ trong ``ly_do``; điểm chỉ để xếp thứ tự.
    """
    sinh, khac = _bang_ngu_hanh()
    nam_dau = nam_dau or date.today().year
    trung_gian = hanh_trung_gian(bo["hanh"], me["hanh"])
    ket_qua = []
    for nam in range(nam_dau, nam_dau + so_nam):
        cc = can_chi_nam(nam)
        hc = cc.nap_am_hanh
        diem, ly_do = 0, []
        for vai, n in (("bố", bo), ("mẹ", me)):
            if sinh.get(hc) == n["hanh"] or sinh.get(n["hanh"]) == hc:
                diem += 2
                ly_do.append(f"mệnh con ({hc}) tương sinh mệnh {vai} ({n['hanh']})")
            elif hc == n["hanh"]:
                diem += 1
                ly_do.append(f"mệnh con cùng hành với {vai} ({hc})")
            else:
                diem -= 1
                ly_do.append(f"mệnh con ({hc}) khắc mệnh {vai} ({n['hanh']})"
                             if khac.get(hc) == n["hanh"] else
                             f"mệnh {vai} ({n['hanh']}) khắc mệnh con ({hc})")
            qh = quan_he_chi(cc.chi, n["chi"])
            if "Tam hợp" in qh or "Lục hợp" in qh:
                diem += 2
                ly_do.append(f"chi {cc.chi} {'tam hợp' if 'Tam hợp' in qh else 'lục hợp'} "
                             f"chi {n['chi']} của {vai}")
            if "Lục xung" in qh:
                diem -= 2
                ly_do.append(f"chi {cc.chi} xung chi {n['chi']} của {vai}")
        la_trung_gian = bool(trung_gian) and hc == trung_gian["hanh"]
        ket_qua.append({
            "nam": nam, "can_chi": cc.ten, "nap_am": cc.nap_am, "hanh": hc,
            "la_hanh_trung_gian": la_trung_gian,
            "diem": diem, "ly_do": ly_do,
        })
    ket_qua.sort(key=lambda x: (not x["la_hanh_trung_gian"], -x["diem"], x["nam"]))
    return ket_qua


def xem_hop_tuoi(nam_sinh_a: int, gioi_tinh_a: str,
                 nam_sinh_b: int, gioi_tinh_b: str,
                 muc_dich: str = "hon_nhan") -> dict:
    """Xét độ hợp của hai tuổi theo bốn phép dân gian.

    Năm sinh là **năm âm lịch**. Người sinh tháng 1–2 dương trước Tết thuộc năm
    âm trước đó, nên giao diện nên đổi từ ngày sinh dương rồi mới gọi hàm này.
    ``muc_dich`` là ``hon_nhan`` hoặc ``lam_an``; phần riêng của hôn nhân (Cao Ly
    Đầu Hình, năm sinh con) chỉ có khi xem hôn nhân cho một nam một nữ.
    """
    nam_a = nam_hop_le(nam_sinh_a, "Năm sinh người thứ nhất")
    nam_b = nam_hop_le(nam_sinh_b, "Năm sinh người thứ hai")
    gt_a = gioi_tinh_hop_le(gioi_tinh_a)
    gt_b = gioi_tinh_hop_le(gioi_tinh_b)
    if muc_dich not in MUC_DICH:
        raise LoiDauVao("Mục đích xem chỉ nhận 'hon_nhan' hoặc 'lam_an'.")

    a, b = _menh(nam_a), _menh(nam_b)
    cung_a, cung_b = cung_phi(nam_a, gt_a), cung_phi(nam_b, gt_b)
    muc = [_xet_ban_menh(a, b), _xet_thien_can(a, b), _xet_dia_chi(a, b),
           _xet_cung_phi(cung_a, cung_b)]

    canh_bao = []
    # Khắc theo CHIỀU NÀO cũng tính. Chỉ xét một chiều là bỏ sót đúng một nửa số
    # cặp: ví dụ Giáp Tý 1984 với Canh Ngọ 1990 — Giáp không khắc Canh, nhưng
    # Canh (Kim) khắc Giáp (Mộc), lại thêm Tý xung Ngọ, đúng là thiên khắc địa xung.
    ke, bi = ((a, b) if can_khac(a["can"], b["can"]) else (b, a))
    if ((can_khac(a["can"], b["can"]) or can_khac(b["can"], a["can"]))
            and luc_xung(a["chi"]) == b["chi"]):
        canh_bao.append({
            "ten": "Thiên khắc địa xung", "diem": DIEM["thien_khac_dia_xung"],
            "giai_thich": f"Vừa can {ke['can']} khắc can {bi['can']}, vừa chi "
                          f"{a['chi']} xung chi {b['chi']}. Đây là trường hợp mọi "
                          f"trường phái đều coi là nặng nhất; dân gian khuyên nếu "
                          f"vẫn lấy nhau thì nhờ người tuổi hợp đứng ra làm mai, "
                          f"chủ hôn."})

    diem = sum(m["diem"] for m in muc) + sum(c["diem"] for c in canh_bao)
    toi_da = (DIEM["menh_tuong_sinh"] + DIEM["can_ngu_hop"]
              + DIEM["tam_hop"] + DIEM["du_nien_tot"])
    if diem >= 8:
        danh_gia, loi = "rất hợp", "Cả bốn mặt đều thuận."
    elif diem >= 4:
        danh_gia, loi = "hợp", "Phần hợp nhiều hơn phần khắc."
    elif diem >= 0:
        danh_gia, loi = "bình thường", "Có hợp có khắc, không bên nào lấn hẳn."
    elif diem >= -4:
        danh_gia, loi = "ít hợp", "Phần khắc nhiều hơn phần hợp."
    else:
        danh_gia, loi = "khắc", "Nhiều mặt khắc nhau."

    # Phần riêng của hôn nhân: cần biết ai là chồng, ai là vợ.
    cao_ly = trung_gian = sinh_con = None
    if muc_dich == "hon_nhan" and {gt_a, gt_b} == {"nam", "nu"}:
        chong, vo = (a, b) if gt_a == "nam" else (b, a)
        cao_ly = cao_ly_dau_hinh(chong["can"], vo["chi"])
        trung_gian = hanh_trung_gian(a["hanh"], b["hanh"])
        sinh_con = goi_y_nam_sinh_con(chong, vo)

    return {
        "muc_dich": muc_dich,
        "nguoi_a": {**a, "gioi_tinh": gt_a, "cung_phi": cung_a["cung_phi"],
                    "nhom_bat_trach": cung_a["nhom"], "con_giap": _con_giap(a["chi"])},
        "nguoi_b": {**b, "gioi_tinh": gt_b, "cung_phi": cung_b["cung_phi"],
                    "nhom_bat_trach": cung_b["nhom"], "con_giap": _con_giap(b["chi"])},
        "muc_xet": muc,
        "canh_bao": canh_bao,
        "diem": diem,
        "diem_toi_da": toi_da,
        "danh_gia": danh_gia,
        "nhan_xet": loi,
        "chenh_lech_tuoi": abs(nam_a - nam_b),
        "cao_ly_dau_hinh": cao_ly,
        "hanh_trung_gian": trung_gian,
        "sinh_con_goi_y": sinh_con,
        "luu_y": [
            "Điểm chỉ để xếp thứ tự đáng chú ý, không phải thước đo hôn nhân; "
            "từng khoản cộng trừ đều liệt kê ra để tự kiểm lại.",
            "Các trường phái cân nặng nhẹ khác nhau: có nơi chỉ xét bản mệnh, "
            "có nơi coi cung phi là chính. Kho này xét cả bốn mặt và nói rõ từng mặt.",
            "Đây là tri thức văn hóa dân gian, dùng để tham khảo; quyết định "
            "hôn nhân không nên dựa vào bảng tra.",
        ],
    }


def _con_giap(chi: str) -> str:
    from .canchi import CON_GIAP, DIA_CHI
    return CON_GIAP[DIA_CHI.index(chi)]


__all__ = ["xem_hop_tuoi", "cao_ly_dau_hinh", "hanh_trung_gian",
           "goi_y_nam_sinh_con", "DIEM"]
