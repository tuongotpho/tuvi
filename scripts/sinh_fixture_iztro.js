// Sinh tests/fixtures/iztro_mau.json: 60 lá số lập bằng SylarLong/iztro (MIT, phái Trung Châu)
// làm nguồn đối chiếu ĐỘC LẬP thứ hai bên cạnh lasotuvi. Chạy ở gốc kho:
//
//     npm install --no-save iztro@2.6.1      (node_modules đã nằm trong .gitignore)
//     node scripts/sinh_fixture_iztro.js     (ghi lại fixture)
//     node scripts/sinh_fixture_iztro.js --kiem-tra
//
// Đầu vào lấy đúng 60 ca của lasotuvi_mau.json. Tên sao được đổi về cách gọi của kho
// (Bác Sỹ -> Bác sĩ, Phụng Các -> Phượng Các, Tuế Kiện -> Thái Tuế, ...). Những sao
// iztro an theo phái khác (Giải Thần theo tháng, Thiên Quý đếm thuận, Thiên Trù can Quý
// tại Hợi, Hỏa Linh xét thêm giờ sinh — xem SOURCES.md mục E) và sao kho không có
// (Thiên Vu, Âm Sát, Thiên Nguyệt, Không Vong, Niên Giải, vòng Tướng Tiền) bị bỏ.
"use strict";
const fs = require("fs");
const path = require("path");
const { astro } = require("iztro");

const ROOT = path.resolve(__dirname, "..");
const TEP_VAO = path.join(ROOT, "tests", "fixtures", "lasotuvi_mau.json");
const TEP_RA = path.join(ROOT, "tests", "fixtures", "iztro_mau.json");
const CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"];

// iztro -> tên trong data/tu_vi/sao.json (chữ thường)
const DOI_TEN = { "phụng các": "phượng các", "thiên diêu": "thiên riêu", "đài phụ": "thai phụ",
                  "hàm trì": "đào hoa" };
const VONG_TRANG_SINH = { "trường sinh": "tràng sinh", "mục dục": "mộc dục" };
const VONG_BAC_SI = { "bác sỹ": "bác sĩ", "lực sỹ": "lực sĩ" };
const VONG_THAI_TUE = { "tuế kiện": "thái tuế", "hối khí": "thiếu dương", "quán tác": "thiếu âm",
                        "tiểu hao": "tử phù", "đại hao": "tuế phá", "thiên đức": "phúc đức",
                        "bệnh phù": "trực phù" };
// Sao có trong danh sách chung của iztro nhưng phải lấy từ vòng riêng (trùng tên) hoặc bỏ hẳn
const BO_TRONG_DANH_SACH_CHUNG = new Set(["phi liêm", "hoa cái", "kiếp sát", "tiểu hao", "đại hao",
  "bệnh phù", "quan phù", "tuần không", "triệt lộ", "thiên vu", "âm sát", "thiên nguyệt",
  "không vong", "niên giải"]);
const KHAC_PHAI = new Set(["giải thần", "thiên quý", "thiên trù", "hỏa tinh", "linh tinh"]);

function lapIztro(m) {
  const [d, t, n] = m.am_lich;
  const a = astro.byLunar(`${n}-${t}-${d}`, CHI.indexOf(m.gio),
                          m.gioi_tinh === "nam" ? "male" : "female", false, true, "vi-VN");
  const sao = {};
  let tuan = null, triet = null, menh = null, than = null;
  for (const p of a.palaces) {
    if (p.name === "Mệnh") menh = p.earthlyBranch;
    if (p.isBodyPalace) than = p.earthlyBranch;
    for (const s of [...p.majorStars, ...p.minorStars, ...p.adjectiveStars]) {
      const ten = s.name.toLowerCase();
      if (ten === "tuần không") tuan = p.earthlyBranch;
      else if (ten === "triệt lộ") triet = p.earthlyBranch;
      else if (!BO_TRONG_DANH_SACH_CHUNG.has(ten)) sao[DOI_TEN[ten] || ten] = p.earthlyBranch;
      if (s.mutagen) sao["hóa " + s.mutagen.toLowerCase()] = p.earthlyBranch;
    }
    const ts = p.changsheng12.toLowerCase(); sao[VONG_TRANG_SINH[ts] || ts] = p.earthlyBranch;
    const bs = p.boshi12.toLowerCase(); sao[VONG_BAC_SI[bs] || bs] = p.earthlyBranch;
    const tt = p.suiqian12.toLowerCase(); sao[VONG_THAI_TUE[tt] || tt] = p.earthlyBranch;
    const jq = p.jiangqian12.toLowerCase();
    if (jq === "hoa cái" || jq === "kiếp sát") sao[jq] = p.earthlyBranch;
  }
  for (const k of KHAC_PHAI) delete sao[k];
  return { am_lich: m.am_lich, gio: m.gio, gioi_tinh: m.gioi_tinh, duong_lich: a.solarDate,
           cung_menh: menh, cung_than: than, cuc: a.fiveElementsClass.split(" ")[0],
           tuan, triet, sao: Object.fromEntries(Object.entries(sao).sort()) };
}

const vao = JSON.parse(fs.readFileSync(TEP_VAO, "utf8"));
const laSo = vao.la_so.map(lapIztro);
const soSao = new Set(laSo.map((l) => Object.keys(l.sao).length));
if (soSao.size !== 1) { console.error("Số sao mỗi lá số không đồng nhất:", [...soSao]); process.exit(1); }
const ra = {
  _ghi_chu: "Vị trí sao theo SylarLong/iztro 2.6.1 (MIT, phái Trung Châu), tên đổi về cách gọi của kho. " +
    "Bỏ 5 sao iztro an theo phái khác (Giải Thần, Thiên Quý, Thiên Trù, Hỏa Tinh, Linh Tinh — SOURCES.md mục E) " +
    "và các sao kho không có. Tuần/Triệt iztro chỉ ghi một cung (cung đầu của cặp). Sinh bằng scripts/sinh_fixture_iztro.js.",
  so_sao_moi_la_so: [...soSao][0],
  la_so: laSo,
};
const chuoi = JSON.stringify(ra, null, 1) + "\n";
if (process.argv.includes("--kiem-tra")) {
  const cu = fs.existsSync(TEP_RA) ? fs.readFileSync(TEP_RA, "utf8") : "";
  console.log(`${laSo.length} lá số × ${ra.so_sao_moi_la_so} sao; ${cu === chuoi ? "khớp" : "KHÁC"} fixture hiện có`);
  process.exit(cu === chuoi ? 0 : 1);
}
fs.writeFileSync(TEP_RA, chuoi, "utf8");
console.log(`Đã ghi ${path.relative(ROOT, TEP_RA)}: ${laSo.length} lá số × ${ra.so_sao_moi_la_so} sao`);
