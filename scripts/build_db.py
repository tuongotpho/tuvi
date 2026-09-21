#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dựng cơ sở dữ liệu SQLite từ các tệp JSON trong ``data/``.

    python scripts/build_db.py [duong_dan_dich]

Mặc định ghi ra ``build/tuvi.db``. Mọi bảng đều dựng lại từ đầu nên chạy lại
bao nhiêu lần cũng cho kết quả như nhau.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tuvi.canchi import CON_GIAP, luc_thap_hoa_giap  # noqa: E402
from tuvi.store import load  # noqa: E402
from tuvi.console import bat_utf8  # noqa: E402

bat_utf8()

SCHEMA = """
DROP TABLE IF EXISTS ngu_hanh;
CREATE TABLE ngu_hanh (
  hanh TEXT PRIMARY KEY, sinh TEXT, duoc_sinh_boi TEXT, khac TEXT,
  bi_khac_boi TEXT, mau TEXT, mau_ky TEXT, huong TEXT, mua TEXT, so TEXT,
  tang_phu TEXT, tinh_cach TEXT, nghe TEXT);

DROP TABLE IF EXISTS thien_can;
CREATE TABLE thien_can (
  stt INTEGER PRIMARY KEY, ten TEXT, hanh TEXT, am_duong TEXT,
  tang_phu TEXT, hinh_tuong TEXT, hop TEXT, xung TEXT);

DROP TABLE IF EXISTS dia_chi;
CREATE TABLE dia_chi (
  stt INTEGER PRIMARY KEY, ten TEXT, con_giap TEXT, hanh TEXT, am_duong TEXT,
  gio TEXT, thang_am_lich INTEGER, huong TEXT, tam_hop TEXT,
  tu_hanh_xung TEXT, luc_hop TEXT, luc_xung TEXT, luc_hai TEXT);

DROP TABLE IF EXISTS hoa_giap;
CREATE TABLE hoa_giap (
  stt INTEGER PRIMARY KEY, can TEXT, chi TEXT, ten TEXT, nap_am TEXT,
  hanh TEXT, am_duong TEXT, con_giap TEXT);

DROP TABLE IF EXISTS nap_am;
CREATE TABLE nap_am (
  ten TEXT PRIMARY KEY, hanh TEXT, cap_can_chi TEXT, y_nghia TEXT);

DROP TABLE IF EXISTS con_giap;
CREATE TABLE con_giap (
  stt INTEGER PRIMARY KEY, chi TEXT, con_giap TEXT, hanh TEXT, am_duong TEXT,
  tinh_cach TEXT, uu_diem TEXT, nhuoc_diem TEXT, su_nghiep TEXT,
  tinh_yeu TEXT, tai_chinh TEXT, suc_khoe TEXT, mau_hop TEXT, so_hop TEXT,
  da_phong_thuy TEXT, nam_sinh TEXT);

DROP TABLE IF EXISTS sao_tu_vi;
CREATE TABLE sao_tu_vi (
  id INTEGER PRIMARY KEY, ten TEXT, nhom TEXT, hanh TEXT, loai TEXT,
  phuong_vi TEXT, am_duong TEXT, tinh_chat TEXT, y_nghia TEXT);

DROP TABLE IF EXISTS sao_dac_tinh;
CREATE TABLE sao_dac_tinh (
  sao_id INTEGER, sao_ten TEXT, chi TEXT, dac_tinh TEXT,
  PRIMARY KEY (sao_id, chi));

DROP TABLE IF EXISTS cung_tu_vi;
CREATE TABLE cung_tu_vi (
  stt INTEGER PRIMARY KEY, ten TEXT, chu_ve TEXT, cach_doc TEXT,
  noi_dung_xem TEXT);

DROP TABLE IF EXISTS cach_cuc;
CREATE TABLE cach_cuc (
  ten TEXT PRIMARY KEY, dieu_kien TEXT, tinh_chat TEXT, luan_giai TEXT);

DROP TABLE IF EXISTS sao_han;
CREATE TABLE sao_han (
  ten TEXT PRIMARY KEY, tinh_chat TEXT, nhom TEXT, y_nghia TEXT,
  nang_voi TEXT, thang_ky TEXT, anh_huong TEXT, hoa_giai TEXT,
  ngay_cung_am_lich INTEGER, huong_cung TEXT, so_den INTEGER);

DROP TABLE IF EXISTS sao_han_theo_tuoi;
CREATE TABLE sao_han_theo_tuoi (
  tuoi_mu INTEGER, gioi_tinh TEXT, sao TEXT,
  PRIMARY KEY (tuoi_mu, gioi_tinh));

DROP TABLE IF EXISTS tam_tai;
CREATE TABLE tam_tai (
  chi TEXT PRIMARY KEY, tam_hop TEXT, nam_tam_tai TEXT);

DROP TABLE IF EXISTS hoang_oc;
CREATE TABLE hoang_oc (
  stt INTEGER PRIMARY KEY, ten TEXT, tot INTEGER, y_nghia TEXT);

DROP TABLE IF EXISTS kim_lau;
CREATE TABLE kim_lau (
  so_du INTEGER PRIMARY KEY, ten TEXT, hai_den TEXT, canh_bao TEXT);

DROP TABLE IF EXISTS cung_phi;
CREATE TABLE cung_phi (
  ten TEXT PRIMARY KEY, so INTEGER, hanh TEXT, huong TEXT, nhom TEXT,
  nguoi TEXT, y_nghia TEXT);

DROP TABLE IF EXISTS du_nien;
CREATE TABLE du_nien (
  cung_phi TEXT, huong TEXT, du_nien TEXT, tinh_chat TEXT, xep_hang INTEGER,
  y_nghia TEXT, PRIMARY KEY (cung_phi, huong));

DROP TABLE IF EXISTS phi_tinh;
CREATE TABLE phi_tinh (
  so INTEGER PRIMARY KEY, ten TEXT, sao_co TEXT, hanh TEXT, tinh_chat TEXT,
  y_nghia TEXT, nen TEXT, hoa_giai_hoac_kich_hoat TEXT);

DROP TABLE IF EXISTS truc;
CREATE TABLE truc (
  stt INTEGER PRIMARY KEY, ten TEXT, tinh_chat TEXT, tom_tat TEXT,
  nen TEXT, ky TEXT, goi_y_content TEXT);

DROP TABLE IF EXISTS nhi_thap_bat_tu;
CREATE TABLE nhi_thap_bat_tu (
  stt INTEGER PRIMARY KEY, ten TEXT, ten_day_du TEXT, that_dieu TEXT,
  con_vat TEXT, tu_tuong TEXT, phuong TEXT, thu_trong_tuan TEXT,
  tinh_chat TEXT, nen TEXT, ky TEXT, mo_ta TEXT);

DROP TABLE IF EXISTS tiet_khi;
CREATE TABLE tiet_khi (
  ten TEXT PRIMARY KEY, kinh_do_mat_troi INTEGER, duong_lich TEXT,
  la_tiet_chinh INTEGER, y_nghia TEXT);

DROP TABLE IF EXISTS viec_chon_ngay;
CREATE TABLE viec_chon_ngay (
  ma TEXT PRIMARY KEY, ten TEXT, cum_tu TEXT, kieng TEXT, ghi_chu TEXT);

DROP TABLE IF EXISTS chu_de_content;
CREATE TABLE chu_de_content (
  ma TEXT PRIMARY KEY, tru_cot TEXT, ten TEXT, tan_suat TEXT,
  du_lieu TEXT, ham TEXT, muc_dich TEXT, do_kho TEXT);
"""


def j(v) -> str:
    """Danh sách và dict lưu dưới dạng JSON để truy vấn bằng json_extract."""
    return json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v


def build(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    con = sqlite3.connect(dest)
    con.executescript(SCHEMA)

    for r in load("ngu_hanh"):
        con.execute(
            "INSERT INTO ngu_hanh VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (r["hanh"], r["sinh"], r["duoc_sinh_boi"], r["khac"], r["bi_khac_boi"],
             j(r["mau"]), j(r["mau_ky"]), j(r["huong"]), r["mua"], j(r["so"]),
             r["tang_phu"], r["tinh_cach"], j(r["nghe"])))

    for r in load("thien_can"):
        con.execute("INSERT INTO thien_can VALUES (?,?,?,?,?,?,?,?)",
                    (r["stt"], r["ten"], r["hanh"], r["am_duong"], r["tang_phu"],
                     r["hinh_tuong"], r["hop"], r["xung"]))

    for r in load("dia_chi"):
        con.execute("INSERT INTO dia_chi VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (r["stt"], r["ten"], r["con_giap"], r["hanh"], r["am_duong"],
                     r["gio"], r["thang_am_lich"], r["huong"], r["tam_hop"],
                     r["tu_hanh_xung"], r["luc_hop"], r["luc_xung"], r["luc_hai"]))

    for r in luc_thap_hoa_giap():
        con.execute("INSERT INTO hoa_giap VALUES (?,?,?,?,?,?,?,?)",
                    (r["stt"], r["can"], r["chi"], r["ten"], r["nap_am"],
                     r["hanh"], r["am_duong"], r["con_giap"]))

    for r in load("nap_am"):
        con.execute("INSERT INTO nap_am VALUES (?,?,?,?)",
                    (r["ten"], r["hanh"], j(r["cap_can_chi"]), r["y_nghia"]))

    for r in load("con_giap"):
        con.execute("INSERT INTO con_giap VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (r["stt"], r["chi"], r["con_giap"], r["hanh"], r["am_duong"],
                     r["tinh_cach"], j(r["uu_diem"]), j(r["nhuoc_diem"]),
                     r["su_nghiep"], r["tinh_yeu"], r["tai_chinh"], r["suc_khoe"],
                     j(r["mau_hop"]), j(r["so_hop"]), j(r["da_phong_thuy"]),
                     j(r["nam_sinh"])))

    for r in load("tu_vi/sao"):
        con.execute("INSERT OR REPLACE INTO sao_tu_vi VALUES (?,?,?,?,?,?,?,?,?)",
                    (r["id"], r.get("ten_hien_thi", r["ten"]), r["nhom"], r["hanh"],
                     r["loai"], r["phuong_vi"], r["am_duong"], r["tinh_chat"],
                     r["y_nghia"]))
        for chi, dt in r["mieu_vuong_dac_ham"].items():
            con.execute("INSERT OR REPLACE INTO sao_dac_tinh VALUES (?,?,?,?)",
                        (r["id"], r["ten"], chi, dt))

    for r in load("tu_vi/cung"):
        con.execute("INSERT INTO cung_tu_vi VALUES (?,?,?,?,?)",
                    (r["stt"], r["ten"], r["chu_ve"], r["cach_doc"],
                     j(r["noi_dung_xem"])))

    for r in load("tu_vi/cach_cuc"):
        con.execute("INSERT INTO cach_cuc VALUES (?,?,?,?)",
                    (r["ten"], r["dieu_kien"], r["tinh_chat"], r["luan_giai"]))

    sh = load("han/sao_han")
    for r in sh["sao"]:
        con.execute("INSERT INTO sao_han VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (r["ten"], r["tinh_chat"], r["nhom"], r["y_nghia"],
                     r["nang_voi"], j(r["thang_ky"]), j(r["anh_huong"]),
                     j(r["hoa_giai"]), r["ngay_cung_am_lich"], r["huong_cung"],
                     r["so_den"]))
    for tuoi in range(10, 101):
        idx = (tuoi - 10) % 9
        con.execute("INSERT INTO sao_han_theo_tuoi VALUES (?,?,?)",
                    (tuoi, "nam", sh["thu_tu_nam"][idx]))
        con.execute("INSERT INTO sao_han_theo_tuoi VALUES (?,?,?)",
                    (tuoi, "nu", sh["thu_tu_nu"][idx]))

    for nhom in load("han/tam_tai")["nhom"]:
        for chi in nhom["tam_hop"]:
            con.execute("INSERT INTO tam_tai VALUES (?,?,?)",
                        (chi, j(nhom["tam_hop"]), j(nhom["nam_tam_tai"])))

    for r in load("han/hoang_oc")["cung"]:
        con.execute("INSERT INTO hoang_oc VALUES (?,?,?,?)",
                    (r["stt"], r["ten"], int(r["tot"]), r["y_nghia"]))

    for r in load("han/kim_lau")["cac_loai"]:
        con.execute("INSERT INTO kim_lau VALUES (?,?,?,?)",
                    (r["so_du"], r["ten"], r["hai_den"], r["canh_bao"]))

    bt = load("phong_thuy/bat_trach")
    dn_info = {d["ten"]: d for d in bt["du_nien"]}
    for c in bt["cung"]:
        con.execute("INSERT INTO cung_phi VALUES (?,?,?,?,?,?,?)",
                    (c["ten"], c["so"], c["hanh"], c["huong"], c["nhom"],
                     c["nguoi"], c["y_nghia"]))
        for huong, ten in c["du_nien"].items():
            d = dn_info[ten]
            con.execute("INSERT INTO du_nien VALUES (?,?,?,?,?,?)",
                        (c["ten"], huong, ten, d["tinh_chat"], d["xep_hang"],
                         d["y_nghia"]))

    for r in load("phong_thuy/cuu_cung_phi_tinh")["sao"]:
        con.execute("INSERT INTO phi_tinh VALUES (?,?,?,?,?,?,?,?)",
                    (r["so"], r["ten"], r["sao_co"], r["hanh"], r["tinh_chat"],
                     r["y_nghia"], j(r["nen"]), j(r["hoa_giai_hoac_kich_hoat"])))

    for r in load("lich/truc"):
        con.execute("INSERT INTO truc VALUES (?,?,?,?,?,?,?)",
                    (r["stt"], r["ten"], r["tinh_chat"], r["tom_tat"],
                     j(r["nen"]), j(r["ky"]), r["goi_y_content"]))

    for r in load("lich/nhi_thap_bat_tu"):
        con.execute("INSERT INTO nhi_thap_bat_tu VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (r["stt"], r["ten"], r["ten_day_du"], r["that_dieu"],
                     r["con_vat"], r["tu_tuong"], r["phuong"], r["thu_trong_tuan"],
                     r["tinh_chat"], j(r["nen"]), j(r["ky"]), r["mo_ta"]))

    for r in load("lich/tiet_khi")["tiet_khi"]:
        con.execute("INSERT INTO tiet_khi VALUES (?,?,?,?,?)",
                    (r["ten"], r["kinh_do_mat_troi"],
                     r["duong_lich_thuong_roi_vao"], int(r["la_tiet_chinh"]),
                     r["y_nghia"]))

    for r in load("lich/viec")["viec"]:
        con.execute("INSERT INTO viec_chon_ngay VALUES (?,?,?,?,?)",
                    (r["ma"], r["ten"], j(r["cum_tu"]), j(r["kieng"]),
                     r["ghi_chu"]))

    tax = json.loads((ROOT / "content" / "taxonomy.json").read_text(encoding="utf-8"))
    for tru_cot in tax["tru_cot"]:
        for cd in tru_cot["chu_de"]:
            con.execute("INSERT INTO chu_de_content VALUES (?,?,?,?,?,?,?,?)",
                        (cd["ma"], tru_cot["ten"], cd["ten"], cd["tan_suat"],
                         j(cd["du_lieu"]), j(cd["ham"]), cd["muc_dich"],
                         cd["do_kho"]))

    con.commit()
    bang = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    tong = 0
    for b in bang:
        n = con.execute(f"SELECT COUNT(*) FROM {b}").fetchone()[0]
        tong += n
        print(f"  {b:<22} {n:>5} dòng")
    print(f"  {'TỔNG':<22} {tong:>5} dòng trong {len(bang)} bảng")
    con.close()
    return dest


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "build" / "tuvi.db"
    print(f"Dựng cơ sở dữ liệu tại {out}")
    build(out)
