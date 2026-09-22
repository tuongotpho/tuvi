# -*- coding: utf-8 -*-
"""Vẽ lá số ra ảnh SVG bằng thư viện chuẩn, không cần gói ngoài.

Chọn SVG chứ không phải PNG vì ba lý do:

* SVG là ảnh vector — phóng to bao nhiêu chữ vẫn sắc, in ra giấy hay xuất PDF
  đều nét, không vỡ như ảnh chấm điểm.
* Chữ trong SVG là chữ thật, nên tiếng Việt có dấu hiển thị đúng mà không phải
  nhúng phông; máy nào mở cũng dùng phông hệ thống.
* Sinh được bằng thư liệu chuẩn (chỉ là ghép chuỗi XML), nên bản đóng gói .exe
  không phải kéo theo thư viện đồ họa nào.

Đổi sang PNG thì làm ở trình duyệt (vẽ SVG lên canvas rồi tải xuống) — xem
``web/static/app.js``. Xuất PDF thì dùng lệnh in của trình duyệt, chữ vẫn là
chữ vector chọn bôi đen được.
"""
from __future__ import annotations

from xml.sax.saxutils import escape

from .la_so import BO_CUC_DIA_BAN
from .luan_giai import bo_sung_y_nghia_sao

# Khổ ảnh: phần đầu ghi thông tin (hai hàng, mỗi hàng 4 ô), dưới là địa bàn
# 4x4, cuối là dòng ghi chú.
RONG = 1240
CAO_DAU = 236
CAO_CHAN = 54
LE = 20
CANH_DIA_BAN = RONG - 2 * LE
O_RONG = CANH_DIA_BAN / 4      # bề ngang một ô cung
KHE = 5                        # khe hở giữa các ô
MOI_HANG_DAU = 4               # số ô thông tin trên mỗi hàng của phần đầu

# Chiều cao một ô cung tính theo cung nhiều sao nhất, chứ không để cứng: lá số
# nào sao dồn vào một cung thì ô cao lên cho đủ chỗ, lá số thưa sao thì ảnh gọn
# lại. Để cứng thì hoặc thừa khoảng trắng, hoặc sao tràn đè lên dòng đại hạn.
DAU_O = 56                     # từ mép trên ô đến dòng sao đầu tiên
BUOC_DONG = 24                 # khoảng cách giữa hai dòng sao
CHAN_O = 46                    # chỗ chừa cho vạch ngăn và dòng "Đại hạn"
O_CAO_TOI_THIEU = 210


def _o_cao(so_dong: int) -> float:
    return max(O_CAO_TOI_THIEU, DAU_O + so_dong * BUOC_DONG + CHAN_O)

# Bảng màu lấy đúng từ web/static/style.css (bản nền sáng) để ảnh và màn hình
# nhìn như nhau.
MAU = {
    "nen": "#ffffff", "nen_o": "#fffdf8", "vien": "#d8cfbc", "chu": "#2a2620",
    "mo": "#6f675a", "nhan": "#8b2f2f", "nhan_nhat": "#f6ece8",
    "cat": "#2f6b46", "hung": "#a83232", "trung": "#6f675a", "vang": "#b08422",
}
PHONG = "'Segoe UI', 'Noto Sans', 'DejaVu Sans', system-ui, sans-serif"

# Bề rộng trung bình một ký tự so với cỡ chữ. Tiếng Việt có dấu nhưng dấu nằm
# trên đầu chứ không nới chữ ra, nên hệ số này đủ dùng để ngắt dòng.
HE_SO_RONG = 0.55


def _rong_chu(chuoi: str, co: float) -> float:
    return len(chuoi) * co * HE_SO_RONG


def _mau_sao(s: dict) -> tuple[str, int, bool]:
    """Màu, cỡ chữ và có in đậm không — cùng quy ước với giao diện web."""
    if s["nhom"] == "Chính tinh":
        return MAU["chu"], 19, True
    if s["nhom"] == "Tứ Hóa":
        return MAU["vang"], 17, True
    return {"cát": MAU["cat"], "hung": MAU["hung"]}.get(
        s.get("tinh_chat"), MAU["trung"]), 17, False


def _xep_sao(sao: list[dict], rong: float) -> list[list[dict]]:
    """Xếp các sao thành từng dòng vừa bề ngang ô, giữ nguyên thứ tự an sao."""
    dong: list[list[dict]] = [[]]
    con = rong
    for s in sao:
        co = _mau_sao(s)[1]
        can = _rong_chu(s["ten"], co) + (10 if s.get("dac_tinh") else 0) + 12
        if dong[-1] and can > con:
            dong.append([])
            con = rong
        dong[-1].append(s)
        con -= can
    return [d for d in dong if d]


def _o_cung(c: dict, x: float, y: float, cao: float, la_menh: bool) -> list[str]:
    """Một ô cung: khung, tên cung, can chi, danh sách sao, dòng chân."""
    r = []
    vien = MAU["nhan"] if la_menh else MAU["vien"]
    r.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{O_RONG - KHE:.1f}" '
             f'height="{cao - KHE:.1f}" '
             f'rx="8" fill="{MAU["nen_o"]}" stroke="{vien}" '
             f'stroke-width="{2.5 if la_menh else 1}"/>')
    trai, phai = x + 12, x + O_RONG - KHE - 12
    r.append(f'<text x="{trai:.1f}" y="{y + 28:.1f}" font-size="19" font-weight="700" '
             f'fill="{MAU["nhan"]}">{escape(c["ten_cung"])}</text>')
    r.append(f'<text x="{phai:.1f}" y="{y + 28:.1f}" font-size="16" text-anchor="end" '
             f'fill="{MAU["mo"]}">{escape(c["can"] + " " + c["chi"])}</text>')

    y_sao = y + DAU_O
    for dong_sao in _xep_sao(c["sao"], O_RONG - KHE - 24):
        x_sao = trai
        for s in dong_sao:
            mau, co, dam = _mau_sao(s)
            net = 'font-weight="700" ' if dam else ""
            r.append(f'<text x="{x_sao:.1f}" y="{y_sao:.1f}" font-size="{co}" '
                     f'{net}fill="{mau}">{escape(s["ten"])}</text>')
            rong_ten = _rong_chu(s["ten"], co)
            if s.get("dac_tinh"):
                r.append(f'<text x="{x_sao + rong_ten + 2:.1f}" y="{y_sao - 7:.1f}" '
                         f'font-size="11" font-weight="700" fill="{MAU["vang"]}">'
                         f'{escape(s["dac_tinh"][0])}</text>')
                rong_ten += 10
            x_sao += rong_ten + 12
        y_sao += BUOC_DONG

    chan_y = y + cao - KHE - 14
    r.append(f'<line x1="{trai:.1f}" y1="{chan_y - 16:.1f}" x2="{phai:.1f}" '
             f'y2="{chan_y - 16:.1f}" stroke="{MAU["vien"]}" stroke-dasharray="3 3"/>')
    r.append(f'<text x="{trai:.1f}" y="{chan_y:.1f}" font-size="15" fill="{MAU["mo"]}">'
             f'Đại hạn {escape(c["dai_han"])}</text>')
    nhan = []
    if c["la_cung_than"]:
        nhan.append(("THÂN", MAU["nhan"]))
    if c.get("tuan"):
        nhan.append(("TUẦN", MAU["hung"]))
    if c.get("triet"):
        nhan.append(("TRIỆT", MAU["hung"]))
    x_nhan = phai
    for chu, mau in reversed(nhan):
        r.append(f'<text x="{x_nhan:.1f}" y="{chan_y:.1f}" font-size="15" font-weight="700" '
                 f'text-anchor="end" fill="{mau}">{escape(chu)}</text>')
        x_nhan -= _rong_chu(chu, 15) + 12
    return r


def _thien_ban(ls: dict, x: float, y: float, rong: float, cao: float) -> list[str]:
    """Ô giữa 2x2: thông tin gốc của lá số."""
    r = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{rong - KHE:.1f}" height="{cao - KHE:.1f}" '
         f'rx="8" fill="{MAU["nhan_nhat"]}" stroke="{MAU["vien"]}"/>']
    am = ls["am_lich"]
    dong = [
        ("Tuổi", f'{ls["nam_sinh_can_chi"]} · {ls["gioi_tinh"]}'),
        ("Âm lịch", f'{am["ngay"]}/{am["thang"]}{" nhuận" if am["nhuan"] else ""}/{am["nam"]}'),
        ("Giờ sinh", am["gio"]),
        ("Bản mệnh", ls["menh_nap_am"]),
        ("Ngũ hành cục", ls["cuc"]),
        ("Mệnh / Thân", f'{ls["cung_menh"]} · {ls["cung_than_tai"]}'),
        ("Đại hạn đi", f'{ls["chieu_di_han"]} ({ls["am_duong_nam_sinh"]} {ls["gioi_tinh"]})'),
        ("", ""),
    ] + [(hoa, sao) for hoa, sao in ls["tu_hoa"].items()]

    trai, phai = x + 26, x + rong - KHE - 26
    buoc = (cao - KHE - 56) / len(dong)
    y_dong = y + 38
    for nhan, gia_tri in dong:
        if nhan:
            r.append(f'<text x="{trai:.1f}" y="{y_dong:.1f}" font-size="17" '
                     f'fill="{MAU["mo"]}">{escape(nhan)}</text>')
            r.append(f'<text x="{phai:.1f}" y="{y_dong:.1f}" font-size="17" font-weight="700" '
                     f'text-anchor="end" fill="{MAU["chu"]}">{escape(gia_tri)}</text>')
        y_dong += buoc
    return r


def _phan_dau(ls: dict, tieu_de: str | None) -> list[str]:
    am = ls["am_lich"]
    chinh = ls.get("chinh_tinh_menh") or []
    r = [f'<text x="{LE}" y="52" font-size="30" font-weight="700" fill="{MAU["nhan"]}">'
         f'{escape(tieu_de or "Lá số Tử Vi")}</text>']
    o = [
        ("Âm lịch", f'{am["ngay"]}/{am["thang"]}{" nhuận" if am["nhuan"] else ""}/{am["nam"]}'
                    f' · giờ {am["gio"]}'),
        ("Năm sinh", ls["nam_sinh_can_chi"]),
        ("Bản mệnh", ls["menh_nap_am"]),
        ("Cục", ls["cuc"]),
        ("Mệnh tại", ls["cung_menh"]),
        ("Thân cư", ls["cung_than_tai"]),
        ("Chính tinh Mệnh", " + ".join(chinh) if chinh else "Vô chính diệu"),
        ("Tuần / Triệt", f'{"–".join(ls["tuan"])} / {"–".join(ls["triet"])}'),
    ]
    # Xếp 4 ô một hàng, hai hàng. Dàn cả 8 ô trên một dòng thì tổng bề ngang
    # vượt quá 1240 và ô cuối ("Tuần / Triệt") bị cắt mất khỏi ảnh.
    for thu_tu, (nhan, gia_tri) in enumerate(o):
        hang, cot = divmod(thu_tu, MOI_HANG_DAU)
        x = LE + cot * (CANH_DIA_BAN / MOI_HANG_DAU)
        y = 104 + hang * 56
        r.append(f'<text x="{x:.1f}" y="{y}" font-size="14" fill="{MAU["mo"]}" '
                 f'letter-spacing="0.6">{escape(nhan.upper())}</text>')
        r.append(f'<text x="{x:.1f}" y="{y + 28}" font-size="19" font-weight="700" '
                 f'fill="{MAU["chu"]}">{escape(gia_tri)}</text>')
    r.append(f'<line x1="{LE}" y1="{CAO_DAU - 18}" x2="{RONG - LE}" y2="{CAO_DAU - 18}" '
             f'stroke="{MAU["vien"]}"/>')
    return r


def ve_la_so_svg(ls: dict, tieu_de: str | None = None, ghi_chu: str | None = None) -> str:
    """Trả về chuỗi SVG hoàn chỉnh của lá số ``ls``.

    ``ls`` là kết quả ``la_so.lap_la_so``; hàm tự bổ sung ý nghĩa sao nếu chưa có
    để biết sao nào cát, sao nào hung mà tô màu.
    """
    def da_co_y_nghia(c: dict) -> bool:
        return all("tinh_chat" in s for s in c["sao"])

    cung = [c if da_co_y_nghia(c) else bo_sung_y_nghia_sao(c) for c in ls["cac_cung"]]
    theo_chi = {c["chi"]: c for c in cung}

    rong_sao = O_RONG - KHE - 24
    o_cao = _o_cao(max(len(_xep_sao(c["sao"], rong_sao)) for c in cung))
    cao = CAO_DAU + 4 * o_cao + CAO_CHAN

    r = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{RONG}" height="{cao:.0f}" '
         f'viewBox="0 0 {RONG} {cao:.0f}" font-family="{PHONG}">',
         f'<rect width="{RONG}" height="{cao:.0f}" fill="{MAU["nen"]}"/>']
    r += _phan_dau(ls, tieu_de)

    for hang, ten_chi in enumerate(BO_CUC_DIA_BAN):
        for cot, chi in enumerate(ten_chi):
            if chi is None:
                continue
            c = theo_chi[chi]
            r += _o_cung(c, LE + cot * O_RONG, CAO_DAU + hang * o_cao, o_cao,
                         c["ten_cung"] == "Mệnh")
    r += _thien_ban(ls, LE + O_RONG, CAO_DAU + o_cao, 2 * O_RONG, 2 * o_cao)

    r.append(f'<text x="{LE}" y="{cao - 18:.0f}" font-size="14" fill="{MAU["mo"]}">'
             f'{escape(ghi_chu or "Lập bằng gói tuvi — tri thức văn hóa dân gian, dùng để tham khảo.")}'
             f'</text>')
    r.append("</svg>")
    return "\n".join(r)


__all__ = ["ve_la_so_svg", "RONG"]
