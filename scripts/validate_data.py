#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm tra tính toàn vẹn của dữ liệu và độ khớp của các phép tính.

    python scripts/validate_data.py

Thoát với mã 1 nếu có lỗi, để cắm thẳng vào CI.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tuvi import chon_ngay, han, la_so, ngay_gio, phong_thuy  # noqa: E402
from tuvi.canchi import (DIA_CHI, NAP_AM_60, THIEN_CAN, can_chi_nam,  # noqa: E402
                         luc_thap_hoa_giap)
from tuvi.store import all_datasets, load  # noqa: E402
from tuvi.console import bat_utf8  # noqa: E402

bat_utf8()

loi: list[str] = []
canh_bao: list[str] = []


def check(dieu_kien: bool, thong_diep: str) -> None:
    if not dieu_kien:
        loi.append(thong_diep)


def main() -> int:
    # 1. Mọi tệp JSON đọc được
    for ten in all_datasets():
        try:
            load(ten)
        except json.JSONDecodeError as e:
            loi.append(f"{ten}.json không phải JSON hợp lệ: {e}")

    # 2. Can chi và nạp âm
    check(len(THIEN_CAN) == 10, "Phải có đúng 10 thiên can")
    check(len(DIA_CHI) == 12, "Phải có đúng 12 địa chi")
    check(len(NAP_AM_60) == 60, "Bảng nạp âm phải có 60 mục")
    check(len({r["ten"] for r in luc_thap_hoa_giap()}) == 60,
          "60 cặp can chi phải khác nhau")
    check(len({r["nap_am"] for r in luc_thap_hoa_giap()}) == 30,
          "Phải có đúng 30 hành nạp âm")
    for nam, mong_doi in [(1990, "Lộ Bàng Thổ"), (2000, "Bạch Lạp Kim"),
                          (1975, "Đại Khê Thủy"), (1980, "Thạch Lựu Mộc"),
                          (2026, "Thiên Hà Thủy")]:
        check(can_chi_nam(nam).nap_am == mong_doi,
              f"Nạp âm năm {nam} phải là {mong_doi}, đang ra "
              f"{can_chi_nam(nam).nap_am}")

    # 3. Bảng Đại du niên bát biến phải đối xứng
    bt = load("phong_thuy/bat_trach")
    huong2cung = {c["huong"]: c["ten"] for c in bt["cung"]}
    bang = {c["ten"]: c["du_nien"] for c in bt["cung"]}
    for a, row in bang.items():
        check(len(row) == 8, f"Cung {a} phải có đủ 8 hướng")
        for huong, dn in row.items():
            b = huong2cung[huong]
            huong_a = next(c["huong"] for c in bt["cung"] if c["ten"] == a)
            check(bang[b][huong_a] == dn,
                  f"Du niên không đối xứng: {a}->{b} là {dn} nhưng "
                  f"{b}->{a} là {bang[b][huong_a]}")
        check(sum(1 for v in row.values()
                  if v in ("Sinh Khí", "Thiên Y", "Diên Niên", "Phục Vị")) == 4,
              f"Cung {a} phải có đúng 4 hướng tốt")

    # 4. Hoang Ốc khớp bảng tuổi xấu đã công bố
    ho = load("han/hoang_oc")
    tinh = [t for t in range(10, 76) if han.hoang_oc(t)["pham"]]
    check(tinh == ho["tuoi_xau_tham_khao"],
          f"Hoang Ốc lệch bảng công bố: {set(tinh) ^ set(ho['tuoi_xau_tham_khao'])}")

    # 5. Sao hạn: chu kỳ 9 năm, nam và nữ cùng mốc tuổi
    sh = load("han/sao_han")
    check(sorted(sh["thu_tu_nam"]) == sorted(sh["thu_tu_nu"]),
          "Hai bảng sao hạn phải chứa cùng 9 sao")
    check({s["ten"] for s in sh["sao"]} == set(sh["thu_tu_nam"]),
          "Danh sách chi tiết sao hạn phải khớp bảng tra")
    check(han.sao_han(2000, 2024, "nam")["sao"] == "Kế Đô"
          and han.sao_han(2000, 2024, "nu")["sao"] == "Thái Dương",
          "Sao hạn năm 2024 cho người sinh 2000 phải là Kế Đô (nam) / "
          "Thái Dương (nữ)")
    for t in range(10, 100):
        check(han.sao_han(2000, 2000 + t - 1, "nam")["sao"]
              == han.sao_han(2000, 2000 + t - 1 + 9, "nam")["sao"],
              f"Sao hạn phải lặp sau 9 năm (tuổi {t})")

    # 6. Tam tai: mỗi chi thuộc đúng một nhóm
    tt = load("han/tam_tai")
    tat_ca = [c for n in tt["nhom"] for c in n["tam_hop"]]
    check(sorted(tat_ca) == sorted(DIA_CHI), "12 chi phải phủ đúng 4 nhóm tam hợp")
    for n in tt["nhom"]:
        check(len(n["nam_tam_tai"]) == 3, "Mỗi nhóm phải có đúng 3 năm tam tai")

    # 7. Sao tử vi
    sao = load("tu_vi/sao")
    check(len(sao) == 109, f"Phải có 109 sao, đang có {len(sao)}")
    check(sum(1 for s in sao if s["nhom"] == "Chính tinh") == 14,
          "Phải có đúng 14 chính tinh")
    thieu = [s["ten"] for s in sao if not s["y_nghia"].strip()]
    check(not thieu, f"Các sao chưa có ý nghĩa: {thieu}")

    # 7b. Cách cục: quy tắc máy đọc được phải nhắc đúng tên sao và đúng khóa
    KHOA_QUY_TAC = {"noi", "co_du", "co_mot", "khong_co", "menh_chi", "sao_tai",
                    "vo_chinh_dieu", "chinh_tinh_menh", "tuan_triet_menh",
                    "menh_than_dong_cung", "hoac", "va", "dong_cung", "hai_ben"}
    VUNG = {"menh", "hoi_menh", "than", "giap_menh", "dien_trach", "phuc_duc"}
    ten_sao = {x["ten"].lower() for x in sao}
    chi_hop_le = set(DIA_CHI)

    def kiem_quy_tac(qt: dict, ten_cach: str) -> None:
        check(set(qt) <= KHOA_QUY_TAC,
              f"Cách '{ten_cach}' dùng khóa lạ: {set(qt) - KHOA_QUY_TAC}")
        check(qt.get("noi", "menh") in VUNG, f"Cách '{ten_cach}': vùng '{qt.get('noi')}' không hợp lệ")
        nhac = list(qt.get("co_du", [])) + list(qt.get("co_mot", [])) + \
            list(qt.get("khong_co", [])) + list(qt.get("chinh_tinh_menh", [])) + \
            list(qt.get("dong_cung", [])) + list(qt.get("sao_tai", {}))
        for ben in qt.get("hai_ben", []):
            nhac += list(ben)
        la = [t for t in nhac if t.lower() not in ten_sao]
        check(not la, f"Cách '{ten_cach}' nhắc sao không có trong sao.json: {la}")
        for chi in list(qt.get("menh_chi", [])) + [c for v in qt.get("sao_tai", {}).values() for c in v]:
            check(chi in chi_hop_le, f"Cách '{ten_cach}': chi '{chi}' không hợp lệ")
        for con in list(qt.get("hoac", [])) + list(qt.get("va", [])):
            kiem_quy_tac(con, ten_cach)

    cach_cuc = load("tu_vi/cach_cuc")
    check(len({c["ten"] for c in cach_cuc}) == len(cach_cuc), "Tên cách cục bị trùng")
    for c in cach_cuc:
        check(bool(c.get("quy_tac")), f"Cách '{c['ten']}' chưa có quy tắc máy đọc được")
        kiem_quy_tac(c["quy_tac"], c["ten"])

    # 8. Lá số: 14 chính tinh mỗi sao xuất hiện đúng một lần
    for ngay, thang, nam, gio, gt in [(20, 9, 1990, 14, "nam"),
                                      (1, 1, 2000, 2, "nu"),
                                      (29, 2, 2004, 23, "nam")]:
        ls = la_so.lap_la_so(ngay, thang, nam, gio, gioi_tinh=gt)
        dem: dict[str, int] = {}
        for c in ls["cac_cung"]:
            for s in c["sao"]:
                if s["nhom"] == "Chính tinh":
                    dem[s["ten"]] = dem.get(s["ten"], 0) + 1
        check(len(dem) == 14 and set(dem.values()) == {1},
              f"Lá số {ngay}/{thang}/{nam}: 14 chính tinh phải xuất hiện "
              f"đúng một lần, đang ra {dem}")
        check(len(ls["cac_cung"]) == 12, "Lá số phải có 12 cung")
        check({c["ten_cung"] for c in ls["cac_cung"]} == set(la_so.TEN_CUNG),
              "Lá số phải có đủ 12 tên cung")

    # 9. Xem ngày: điểm hợp lệ, giờ hoàng đạo luôn đúng 6 khung
    for d, m, y in [(1, 1, 2024), (20, 9, 2026), (17, 2, 2026)]:
        r = ngay_gio.xem_ngay(d, m, y)
        check(0 <= r["diem_tong_hop"] <= 100, "Điểm ngày phải trong khoảng 0-100")
        check(len(r["gio_hoang_dao"]) == 6 and len(r["gio_hac_dao"]) == 6,
              f"Ngày {d}/{m}/{y} phải có 6 giờ hoàng đạo và 6 giờ hắc đạo")
    check(ngay_gio.xem_ngay(1, 1, 2024)["truc"] == "Kiến",
          "Ngày 01/01/2024 phải là trực Kiến")
    check(ngay_gio.xem_ngay(1, 1, 1995)["nhi_thap_bat_tu"] == "Hư",
          "Ngày 01/01/1995 phải là sao Hư (mốc neo của vòng 28 tú)")

    # 10. Cung phi
    for nam, gt, mong_doi in [(1990, "nam", "Khảm"), (1990, "nu", "Cấn"),
                              (1985, "nam", "Càn"), (1985, "nu", "Ly"),
                              (2000, "nam", "Ly"), (2000, "nu", "Càn")]:
        got = phong_thuy.cung_phi(nam, gt)["cung_phi"]
        check(got == mong_doi,
              f"Cung phi {gt} sinh {nam} phải là {mong_doi}, đang ra {got}")
    for nam, so in [(2024, 3), (2025, 2), (2026, 1)]:
        check(phong_thuy.phi_tinh_nam(nam)["sao_nhap_trung_cung"] == so,
              f"Phi tinh năm {nam} phải nhập trung cung số {so}")

    # 11. Chọn ngày theo tuổi
    kho_cum_tu = set()
    for r in load("lich/truc"):
        kho_cum_tu |= set(r["nen"]) | set(r["ky"])
    for r in load("lich/nhi_thap_bat_tu"):
        kho_cum_tu |= set(r["nen"]) | set(r["ky"])
    kieng_hop_le = {"Tam nương", "Nguyệt kỵ", "Thọ tử", "Dương công kỵ nhật"}
    for v in load("lich/viec")["viec"]:
        for c in v["cum_tu"]:
            check(c in kho_cum_tu,
                  f"Việc {v['ma']}: cụm từ '{c}' không khớp mục nên/kỵ nào "
                  f"của 12 Trực hay 28 tú")
        check(set(v["kieng"]) <= kieng_hop_le,
              f"Việc {v['ma']}: loại ngày kiêng không hợp lệ "
              f"{set(v['kieng']) - kieng_hop_le}")
        if not any(set(v["cum_tu"]) & (set(r["nen"]) | set(r["ky"]))
                   for r in load("lich/nhi_thap_bat_tu")):
            canh_bao.append(f"Việc {v['ma']} chưa có mục nào trong bộ 28 tú — "
                            f"điểm sẽ chỉ dựa vào 12 Trực")

    # Ngày xung tuổi phải bị loại dù điểm chung rất cao.
    r = chon_ngay.xem_ngay_theo_tuoi(20, 9, 2026, 1987, "nam")
    check(r["diem_chung"] == 95 and r["bi_chan"] and r["diem_ca_nhan"] == 0,
          "Ngày 20/09/2026 (95 điểm chung) phải bị loại với tuổi Đinh Mão 1987")

    from datetime import date as _date
    kq = chon_ngay.chon_ngay(1987, _date(2026, 10, 10), _date(2026, 11, 7),
                             "dong_tho", "nam", 30)
    check(all(not x["bi_chan"] for x in kq["ngay_tot"]),
          "Kết quả chọn ngày không được chứa ngày đã bị loại")
    check(all(not set(x["ngay_kieng"]) & set(kq["ngay_kieng_cua_viec"])
              for x in kq["ngay_tot"]),
          "Kết quả chọn ngày không được chứa ngày kiêng của chính việc đó")

    # 12. Cảnh báo mềm: trường dài bất thường hoặc thiếu mô tả
    for ten in all_datasets():
        d = load(ten)
        if isinstance(d, list) and not d:
            canh_bao.append(f"{ten}.json rỗng")

    for c in canh_bao:
        print(f"  [cảnh báo] {c}")
    if loi:
        print(f"\n{len(loi)} LỖI:")
        for e in loi:
            print(f"  - {e}")
        return 1
    print(f"\nTất cả kiểm tra đều đạt ({len(all_datasets())} bộ dữ liệu).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
