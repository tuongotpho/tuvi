# -*- coding: utf-8 -*-
"""Đối chiếu tab Xem ngày với hai nguồn độc lập và với ví dụ trong sách.

- Nguồn 1: lịch vạn niên tiếng Việt xemlicham.com, 730 ngày 2025–2026
  (``tests/fixtures/xemlicham_2025_2026.json.gz``, tạo bằng
  ``scripts/tai_xemlicham.py``).
- Nguồn 2: lunar-javascript 1.7.7 — hoàng lịch theo Hiệp Kỷ Biện Phương Thư và
  thời khắc 24 tiết khí 1900–2100 (``tests/fixtures/lunarjs_2025_2026.json.gz``,
  tạo bằng ``scripts/sinh_fixture_lunarjs.cjs``).

Những chỗ một nguồn sai đã được tra sách phân xử; bài kiểm ghi rõ chỗ đó để
không ai "sửa" kho theo nguồn sai. Chi tiết ở SOURCES.md mục H.
"""
from __future__ import annotations

import gzip
import json
import re
import sys
import unittest
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

from tuvi import ngay_gio  # noqa: E402
from tuvi.amlich import jd_from_date, solar_to_lunar  # noqa: E402
from tuvi.canchi import DIA_CHI, THIEN_CAN, can_chi_ngay  # noqa: E402
from tuvi.store import load  # noqa: E402
from tuvi.thien_van import (muc_tiet_cuoi_ngay, moc_tiet_nam,  # noqa: E402
                            thoi_khac_tiet)

FIX = GOC / "tests" / "fixtures"
CAN_CN = dict(zip("甲乙丙丁戊己庚辛壬癸", THIEN_CAN))
CHI_CN = dict(zip("子丑寅卯辰巳午未申酉戌亥", DIA_CHI))
HUONG_CN = {"正北": "Chính Bắc", "东北": "Đông Bắc", "正东": "Chính Đông", "东南": "Đông Nam",
            "正南": "Chính Nam", "西南": "Tây Nam", "正西": "Chính Tây", "西北": "Tây Bắc"}
TRUC_CN = dict(zip("建除满平定执破危成收开闭", ngay_gio.TRUC))
TU_CN = dict(zip("角亢氐房心尾箕斗牛女虚危室壁奎娄胃昴毕觜参井鬼柳星张翼轸", ngay_gio.NHI_THAP_BAT_TU))
TIET_CN = {"春分": 0, "清明": 1, "谷雨": 2, "立夏": 3, "小满": 4, "芒种": 5, "夏至": 6, "小暑": 7,
           "大暑": 8, "立秋": 9, "处暑": 10, "白露": 11, "秋分": 12, "寒露": 13, "霜降": 14,
           "立冬": 15, "小雪": 16, "大雪": 17, "冬至": 18, "小寒": 19, "大寒": 20, "立春": 21,
           "雨水": 22, "惊蛰": 23, "DONG_ZHI": 18, "XIAO_HAN": 19, "DA_HAN": 20, "LI_CHUN": 21,
           "YU_SHUI": 22, "JING_ZHE": 23, "DA_XUE": 17}
# Tên sao của kho -> tên trên xemlicham (khi khác nhau).
TEN_WEB = {"Sinh Khí": "Sinh Khí (Trực Khai)", "Thiên Mã": "Thiên Mã (Lộc Mã)",
           "Phổ Hộ": "Phổ Hộ (Hội Hộ)", "Yếu Yên": "Yếu Yên (Thiên Quý)",
           "Nguyệt Yếm Đại Họa": "Nguyệt Yếm Đại Hoạ", "Tai Sát (Phi Ma Sát)": "Phi Ma Sát (Tai Sát)",
           "Thiên Cương": "Thiên Cương (hay Diệt Môn)", "Hà Khôi": "Hà khôi, Cẩu Giảo",
           "Nguyệt Sát (Nguyệt Hư)": "Nguyệt Hư (Nguyệt Sát)", "Vãng Vong": "Vãng Vong (Thổ Kỵ)"}


@lru_cache(maxsize=None)
def _nap(ten: str) -> dict:
    return json.loads(gzip.decompress((FIX / ten).read_bytes()).decode("utf-8"))


def xlc() -> dict:
    """Ngày của xemlicham, đã bỏ các trang tự mâu thuẫn."""
    d = _nap("xemlicham_2025_2026.json.gz")
    return {k: v for k, v in d["ngay"].items() if k not in d["trang_hong"]}


def ljs() -> dict:
    return _nap("lunarjs_2025_2026.json.gz")["ngay"]


def _ngay(k: str) -> tuple[int, int, int]:
    y, m, d = map(int, k.split("-"))
    return d, m, y


@lru_cache(maxsize=None)
def _chi_tiet(k: str) -> dict:
    return ngay_gio.chi_tiet_ngay(*_ngay(k))


class TestTietKhi(unittest.TestCase):
    """Tiết khí và thời khắc giao tiết — chuẩn cho Trực và nguyệt kiến."""

    def _moc(self):
        for s, ten in _nap("lunarjs_2025_2026.json.gz")["tiet_khi_utc8"].items():
            bj = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
            if 1900 <= bj.year <= 2100:
                yield bj, TIET_CN[ten]

    def test_ngay_giao_tiet_1900_2100(self):
        """Mọi mốc tiết khí 1900–2100: ngày giao tiết (giờ Việt Nam) đúng từng ngày."""
        sai = []
        for bj, muc in self._moc():
            vn = bj - timedelta(hours=1)
            jd = jd_from_date(vn.day, vn.month, vn.year)
            if muc_tiet_cuoi_ngay(jd) != muc or muc_tiet_cuoi_ngay(jd - 1) == muc:
                sai.append(vn)
        self.assertEqual(sai, [])

    def test_thoi_khac_lech_duoi_mot_phut(self):
        for i, (bj, muc) in enumerate(self._moc()):
            if i % 7:
                continue
            ut = bj - timedelta(hours=8)
            jd_ut = (jd_from_date(ut.day, ut.month, ut.year) - 0.5
                     + (ut.hour * 3600 + ut.minute * 60 + ut.second) / 86400)
            lech = (thoi_khac_tiet(jd_ut, muc * 15) - jd_ut) * 86400
            self.assertLess(abs(lech), 60, f"{bj} lệch {lech:.0f} giây")

    def test_phan_chi_2025_theo_usno(self):
        """Xuân phân, hạ chí, thu phân, đông chí 2025 do USNO công bố (UT, tới phút)."""
        for muc, (d, m, h, p) in [(0, (20, 3, 9, 1)), (6, (21, 6, 2, 42)),
                                  (12, (22, 9, 18, 19)), (18, (21, 12, 15, 3))]:
            thuc = jd_from_date(d, m, 2025) - 0.5 + (h * 60 + p) / 1440
            self.assertLess(abs(thoi_khac_tiet(thuc, muc * 15) - thuc) * 1440, 1)

    def test_truc_lap_lai_dung_ngay_giao_tiet(self):
        """Ngày giao tiết (tiết lệnh) đổi nguyệt kiến nên Trực lặp lại Trực hôm trước."""
        for jd, muc in moc_tiet_nam(2026):
            if muc % 2 == 1:        # Tiết lệnh: Thanh minh, Lập hạ, ... (chỉ số lẻ)
                from tuvi.thien_van import jd_sang_gio_vn
                d, m, y, _, _ = jd_sang_gio_vn(jd)
                hom = jd_from_date(d, m, y)
                self.assertEqual(ngay_gio.truc_cua_ngay(hom), ngay_gio.truc_cua_ngay(hom - 1))

    def test_moc_tiet_nam_du_va_tang_dan(self):
        moc = moc_tiet_nam(2026)
        self.assertEqual(len(moc), 28)
        self.assertTrue(all(b[0] - a[0] > 14 for a, b in zip(moc, moc[1:])))


class TestDoiChieuLunarJs(unittest.TestCase):
    def test_truc_tu_gio_hy_than(self):
        dem = 0
        for k, l in ljs().items():
            d, m, y = _ngay(k)
            q = ngay_gio.xem_ngay(d, m, y)
            self.assertEqual(q["ngay_can_chi"], CAN_CN[l["cc"][0]] + " " + CHI_CN[l["cc"][1]], k)
            self.assertEqual(q["truc"], TRUC_CN[l["truc"]], k)
            self.assertEqual(q["nhi_thap_bat_tu"], TU_CN[l["tu"]], k)
            gio = "".join("1" if g["hoang_dao"] else "0" for g in ngay_gio.gio_hoang_dao(solar_to_lunar(d, m, y).jd))
            self.assertEqual(gio, l["gio"], k)
            self.assertEqual(_chi_tiet(k)["huong_xuat_hanh"]["hy_than"], HUONG_CN[l["hy"]], k)
            dem += 1
        self.assertEqual(dem, 730)

    def test_banh_to_chu_han(self):
        """Chữ Hán của Bành Tổ khớp lunar-javascript; dòng có dị bản thì dị bản khớp."""
        bt = load("lich/banh_to")
        cn = {}
        for l in ljs().values():
            cn[CAN_CN[l["cc"][0]]] = l["bt"][0]
            cn[CHI_CN[l["cc"][1]]] = l["bt"][1]
        for r in bt["can"] + bt["chi"]:
            self.assertEqual(r.get("di_ban", r["han_tu"]), cn[r["ten"]], r["ten"])
            # Vế "kiêng việc gì" (4 chữ đầu) thì mọi bản đều như nhau.
            self.assertEqual(r["han_tu"][:4], cn[r["ten"]][:4], r["ten"])

    def test_ngoc_hap_theo_than_sat_trung_hoa(self):
        """Bảng an sao của kho, khi đặt theo tháng tiết như sách Trung Hoa, cho đúng
        những ngày lunar-javascript đánh dấu thần sát cùng tên."""
        CN = {"Thiên Đức": "天德", "Thiên Đức Hợp": "天德合", "Nguyệt Đức": "月德", "Nguyệt Đức Hợp": "月德合",
              "Thiên Hỷ": "天喜", "Thiên Xá": "天赦", "Nguyệt Ân": "月恩", "Nguyệt Không": "月空",
              "Giải Thần": "解神", "Sinh Khí": "生气", "Thiên Mã": "天马", "Dịch Mã": "驿马", "Tam Hợp": "三合",
              "Lục Hợp": "六合", "Dân Nhật": "民日", "Phúc Sinh": "福生", "Phổ Hộ": "普护", "Thánh Tâm": "圣心",
              "Ích Hậu": "益后", "Tục Thế": "续世", "Yếu Yên": "要安", "Âm Đức": "阴德", "Kính Tâm": "敬安",
              "Nguyệt Phá": "月破", "Nguyệt Yếm Đại Họa": "月厌", "Kiếp Sát": "劫煞", "Tai Sát (Phi Ma Sát)": "灾煞",
              "Thiên Cương": "天罡", "Hà Khôi": "河魁", "Nguyệt Sát (Nguyệt Hư)": "月煞", "Vãng Vong": "往亡",
              "Nguyệt Hình": "月刑", "Thổ Phủ": "土府"}
        sao = load("lich/ngoc_hap")["sao"]
        self.assertEqual({s["ten"] for s in sao}, set(CN))
        # Rút bảng của từng thần sát từ lunar-javascript theo đa số trong từng ô
        # (tháng tiết, can/chi/can chi của ngày). Không so từng ngày vì quanh ngày
        # giao tiết thư viện này và kho chọn mốc tháng khác nhau vài giờ.
        o = {}
        for l in ljs().values():
            thang = (DIA_CHI.index(CHI_CN[l["thang_tiet"][1]]) - 2) % 12 + 1
            can, chi = CAN_CN[l["cc"][0]], CHI_CN[l["cc"][1]]
            for s in sao:
                for khoa in (can, chi, f"{can} {chi}"):
                    o.setdefault((s["ten"], thang, khoa), [0, 0])[CN[s["ten"]] in l["sao"]] += 1
        # Chiều thuận: ô nào kho an sao thì lunar-javascript phải đánh dấu ít nhất
        # một ngày trong ô đó. (Nó chép bảng 60 ngày × 12 tháng của Hiệp Kỷ Biện
        # Phương Thư, trong đó vài sao xấu bị sao tốt "át" nên xóa ở một số ngày —
        # vd. Nguyệt Hình tháng Tý chỉ còn ngày Ất Mão, Kỷ Mão.)
        # Chiều ngược: ô cùng loại khóa mà lunar-javascript đánh dấu đa số (từ 2
        # ngày trở lên) thì kho phải có.
        def loai(x):
            return "cc" if " " in x else ("can" if x in THIEN_CAN else "chi")
        lech = []
        for s in sao:
            for thang in range(1, 13):
                if s["ten"] in ("Thiên Đức", "Thiên Đức Hợp") and thang in (2, 5, 8, 11):
                    continue      # lunar-javascript bỏ trống 4 tháng an theo chi
                bang = s["bang"][str(thang)]
                for khoa in bang:
                    khong, co = o.get((s["ten"], thang, khoa), (0, 0))
                    if khong + co and not co:
                        lech.append((s["ten"], thang, khoa, "lunar-js không đánh dấu"))
                loai_sao = {loai(x) for x in bang}
                for (ten, th, khoa), (khong, co) in o.items():
                    if (ten == s["ten"] and th == thang and loai(khoa) in loai_sao
                            and co >= 2 and co > khong and khoa not in bang):
                        lech.append((ten, th, khoa, "kho thiếu"))
        self.assertEqual(lech, [])


class TestDoiChieuXemLichAm(unittest.TestCase):
    def test_am_lich_can_chi_gio_tu(self):
        for k, x in xlc().items():
            d, m, y = _ngay(k)
            q = _chi_tiet(k)
            self.assertEqual([q["am"]["ngay"], q["am"]["thang"], q["am"]["nam"], q["am"]["nhuan"]], x["am"], k)
            self.assertEqual(q["ngay_can_chi"], x["cc"], k)
            self.assertEqual(q["thang_can_chi"], x["thang_cc"], k)
            self.assertEqual(q["nhi_thap_bat_tu"], x["tu"], k)
            gio = [{"Tí": "Tý", "Tị": "Tỵ"}.get(g, g) for g in x["gio_hd"]]
            self.assertEqual([g["chi"] for g in q["gio_hoang_dao"]], gio, k)

    def test_than_truc_nhat_theo_thang_am(self):
        """Việt Nam an 12 thần hoàng đạo theo tháng âm lịch (khác sách Trung Hoa theo tiết)."""
        doi = {"Huyền Vũ": "Nguyên Vũ", "Câu Trận": "Câu Trần"}
        dem = 0
        for k, x in xlc().items():
            ten = [doi.get(t, t) for t in (re.sub(r" (Hoàng|Hắc) Đạo$", "", s) for s in x["sao_tot"] + x["sao_xau"]
                                           if s.endswith(" Đạo"))]
            if ten:
                self.assertIn(_chi_tiet(k)["than_truc_nhat"], ten, k)
                dem += 1
        self.assertGreater(dem, 650)

    def test_ngu_hanh_ngay(self):
        doi = {"Can Chi tương đồng": "Can Chi cùng hành"}
        for k, x in xlc().items():
            self.assertEqual(_chi_tiet(k)["ngu_hanh_ngay"]["quan_he"], doi.get(x["ngu_hanh"], x["ngu_hanh"]), k)

    def test_tuoi_hop_xung(self):
        for k, x in xlc().items():
            m = re.match(r"lục hợp với (\S+), tam hợp với (\S+) và (\S+) thành \S+ cục\. (.*?)\.", x["quan_he_chi"])
            muc = {}
            for loai, chi in re.findall(r"(Xung|hình|hại|phá|tuyệt) ([^,]+)", m[4]):
                muc.setdefault(loai, []).append(chi.strip())
            t = {kk: [v.split()[0] for v in vv] for kk, vv in _chi_tiet(k)["tuoi"].items()}
            self.assertEqual(t["luc_hop"], [m[1]], k)
            self.assertEqual(sorted(t["tam_hop"]), sorted([m[2], m[3]]), k)
            self.assertEqual(t["xung"], muc["Xung"], k)
            self.assertEqual(t["hai"], muc["hại"], k)
            self.assertEqual(t["pha"], muc["phá"], k)
            # Không so mục "hình": web ghi cả những cặp không có trong tam hình hay
            # tự hình (vd. ngày Ngọ "hình Dậu", ngày Thìn "hình Mùi").

    def test_banh_to_am_han_viet(self):
        chinh_ta = {"tải thực": "tài thực", "sanh sang": "sinh sang", "lí nhược": "lý nhược",
                    "trọng tang": "trùng tang"}
        for k, x in xlc().items():
            bt = _chi_tiet(k)["banh_to"]
            for web, kho in zip(x["banh_to"], (bt["can"], bt["chi"])):
                w = web.lower()
                for a, b in chinh_ta.items():
                    w = w.replace(a, b)
                self.assertEqual(w, kho["han_viet"].split(" ", 1)[1].replace(",", "").lower(), k)

    def test_huong_xuat_hanh(self):
        for k, x in xlc().items():
            h = _chi_tiet(k)["huong_xuat_hanh"]
            if x["hy_than"]:
                self.assertEqual(h["hy_than"], x["hy_than"], k)
            self.assertIn(x["tai_than"], h["tai_than"], k)
            self.assertEqual(h["hac_than"], {"Lên Trời": "Trên trời"}.get(x["hac_than"], x["hac_than"]), k)

    def test_ngoc_hap(self):
        """33 sao của kho khớp xemlicham từng ngày, trừ 2 chỗ web sai đã phân xử:
        Thiên Đức Hợp tháng 2 (web ghi Tý, đúng là Tỵ — hợp của Thiên Đức ở Thân)
        và Thiên Xá (web đánh dấu mọi ngày can Mậu hoặc chi Dần... trong mùa, lại
        bỏ trống tháng 5 và 11; đúng là chỉ ngày Mậu Dần / Giáp Ngọ / Mậu Thân /
        Giáp Tý — đã đối chiếu với lunar-javascript)."""
        for k, x in xlc().items():
            q = _chi_tiet(k)["ngoc_hap"]
            kho = {s["ten"] for s in q["tot"] + q["xau"]}
            web = set(x["sao_tot"]) | set(x["sao_xau"])
            for s in load("lich/ngoc_hap")["sao"]:
                ten = s["ten"]
                o_kho, o_web = ten in kho, TEN_WEB.get(ten, ten) in web
                if ten == "Thiên Đức Hợp" and x["am"][1] == 2:
                    self.assertEqual(o_kho, x["cc"].endswith("Tỵ"), k)
                    self.assertEqual(o_web, x["cc"].endswith("Tý"), k)
                elif ten == "Thiên Xá":
                    continue      # web sai kiểu khác (xem docstring); đã so với sách Trung Hoa
                else:
                    self.assertEqual(o_kho, o_web, f"{k} {ten}")

    def test_ngay_ky(self):
        for k, x in xlc().items():
            q = _chi_tiet(k)
            ngay, thang = x["am"][0], x["am"][1]
            self.assertEqual("Tam nương" in q["ngay_kieng"], "Tam Nương" in x["ngay_ky"], k)
            self.assertEqual("Ngọc Hạp Thông Thư (theo chi)" in q["tho_tu"], "Thụ Tử" in x["ngay_ky"], k)
            if thang != 12:     # tháng Chạp web ghi 22, đúng là 19 (bảng 杨公忌)
                self.assertEqual("Dương công kỵ nhật" in q["ngay_kieng"], "Dương Công Kỵ Nhật" in x["ngay_ky"], k)

    def test_khong_minh_web_lech_mot_o(self):
        """xemlicham tính lục diệu lệch một ô ở MỌI ngày so với sách (mùng 1 tháng
        Giêng khởi Đại An). Bài này ghi lại độ lệch để không ai sửa kho theo web."""
        thu_tu = [r["ten"] for r in load("lich/luc_dieu")["thu_tu"]]
        for k, x in xlc().items():
            kho = _chi_tiet(k)["luc_dieu"]["ten"]
            self.assertEqual(thu_tu[(thu_tu.index(kho) + 1) % 6], x["khong_minh"], k)


class TestVanBan(unittest.TestCase):
    """Ví dụ tính tay trong sách/bài hướng dẫn tiếng Việt."""

    def test_khong_minh_theo_vi_du(self):
        # lichvannien365.com: ngày 25 tháng 8 là Lưu niên; giờ Tị ngày đó là Đại an.
        self.assertEqual(ngay_gio.luc_dieu(8, 25)["ten"], "Lưu Liên")
        self.assertEqual(ngay_gio.gio_xuat_hanh(8, 25)[5]["ten"], "Đại An")
        # tuvikhoahoc.vn: ngày 23 tháng 7 là Tiểu cát.
        self.assertEqual(ngay_gio.luc_dieu(7, 23)["ten"], "Tiểu Cát")
        # Mùng 1 tháng Giêng khởi Đại An, tháng 2 khởi Lưu Liên.
        self.assertEqual(ngay_gio.luc_dieu(1, 1)["ten"], "Đại An")
        self.assertEqual(ngay_gio.luc_dieu(2, 1)["ten"], "Lưu Liên")

    def test_duong_cong_ky_nhat(self):
        """13 ngày Dương công (杨公忌): khớp bảng của lunar-javascript."""
        bang = {1: 13, 2: 11, 3: 9, 4: 7, 5: 5, 6: 3, 8: 27, 9: 25, 10: 23, 11: 21, 12: 19}
        from tuvi.amlich import lunar_to_solar
        for thang, ngay in list(bang.items()) + [(7, 1), (7, 29)]:
            d, m, y = lunar_to_solar(ngay, thang, 2026)
            self.assertIn("Dương công kỵ nhật", ngay_gio.xem_ngay(d, m, y)["ngay_kieng"], (ngay, thang))

    def test_tho_tu_hai_cach(self):
        # Tháng Giêng: cách phổ thông chỉ ngày Bính Tuất; Ngọc Hạp mọi ngày Tuất.
        self.assertEqual(ngay_gio.tho_tu(1, "Bính Tuất"),
                         ["cách phổ thông (theo can chi)", "Ngọc Hạp Thông Thư (theo chi)"])
        self.assertEqual(ngay_gio.tho_tu(1, "Giáp Tuất"), ["Ngọc Hạp Thông Thư (theo chi)"])
        self.assertEqual(ngay_gio.tho_tu(1, "Giáp Tý"), [])

    def test_hac_than_60_ngay(self):
        """Hạc thần lên trời 16 ngày (Quý Tỵ – Mậu Thân), 44 ngày ở tám hướng."""
        dem = {}
        for i in range(60):
            h = ngay_gio.huong_xuat_hanh("Giáp", i + 1)["hac_than"]
            dem[h] = dem.get(h, 0) + 1
        self.assertEqual(dem["Trên trời"], 16)
        self.assertEqual(sum(dem.values()), 60)
        self.assertEqual(sorted(v for k, v in dem.items() if k != "Trên trời"), [5, 5, 5, 5, 6, 6, 6, 6])


class TestChiTietNgay(unittest.TestCase):
    def test_ngay_25_9_2026(self):
        q = ngay_gio.chi_tiet_ngay(25, 9, 2026)
        self.assertEqual(q["thu"], "Thứ Sáu")
        self.assertEqual(q["am"], {"ngay": 15, "thang": 8, "nam": 2026, "nhuan": False, "so_ngay_thang": 29})
        self.assertEqual((q["ngay_can_chi"], q["thang_can_chi"], q["nam_can_chi"]),
                         ("Nhâm Dần", "Đinh Dậu", "Bính Ngọ"))
        self.assertEqual(q["tiet_chi_tiet"]["ten"], "Thu phân")
        self.assertEqual(q["tiet_chi_tiet"]["bat_dau"], "07:05 ngày 23/09/2026")
        self.assertEqual(q["ngu_hanh_ngay"]["ten"], "Bảo nhật")
        self.assertEqual(q["huong_xuat_hanh"]["hac_than"], "Trên trời")

    def test_thang_nhuan_va_du_thieu(self):
        # 2025 có tháng 6 nhuận: 19/8/2025 là 26/6 nhuận.
        q = ngay_gio.chi_tiet_ngay(19, 8, 2025)
        self.assertTrue(q["am"]["nhuan"])
        self.assertIn(q["am"]["so_ngay_thang"], (29, 30))

    def test_tai_than_mau_quy_ghi_ro_chua_thong_nhat(self):
        for can in THIEN_CAN:
            h = ngay_gio.huong_xuat_hanh(can, 1)
            self.assertEqual(h["tai_than_chua_thong_nhat"], can in ("Mậu", "Quý"), can)


if __name__ == "__main__":
    unittest.main()
