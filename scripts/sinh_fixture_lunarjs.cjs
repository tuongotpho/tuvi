// Xuất dữ liệu hoàng lịch của lunar-javascript (6tail, MIT) làm nguồn đối chiếu
// thứ hai cho tests/test_xem_ngay.py: trực, 28 tú, giờ hoàng đạo, Hỷ thần,
// Bành Tổ, các thần sát (theo Hiệp Kỷ Biện Phương Thư), và thời khắc giao 24
// tiết khí 1900–2100 (giờ Bắc Kinh, UTC+8).
//
// Chạy: npm install lunar-javascript@1.7.7 rồi
//       node scripts/sinh_fixture_lunarjs.cjs <thư mục node_modules>
// Ghi:  tests/fixtures/lunarjs_2025_2026.json.gz
const path = require("path"), fs = require("fs"), zlib = require("zlib");
const nm = process.argv[2] || "node_modules";
const { Solar, Lunar } = require(path.resolve(nm, "lunar-javascript"));

const ngay = {};
for (let t = Date.UTC(2025, 0, 1); t <= Date.UTC(2026, 11, 31); t += 864e5) {
  const d = new Date(t);
  const l = Solar.fromYmd(d.getUTCFullYear(), d.getUTCMonth() + 1, d.getUTCDate()).getLunar();
  ngay[d.toISOString().slice(0, 10)] = {
    cc: l.getDayInGanZhi(), thang_tiet: l.getMonthInGanZhiExact(),
    truc: l.getZhiXing(), tu: l.getXiu(), than: l.getDayTianShen(),
    gio: l.getTimes().slice(0, 12).map((x) => (x.getTianShenType() === "黄道" ? 1 : 0)).join(""),
    hy: l.getDayPositionXiDesc(), tai: l.getDayPositionCaiDesc(),
    bt: [l.getPengZuGan(), l.getPengZuZhi()],
    sao: [...l.getDayJiShen(), ...l.getDayXiongSha()],
  };
}
const tiet = {};
for (let y = 1900; y <= 2100; y++) {
  for (const [ten, s] of Object.entries(Lunar.fromYmd(y, 6, 1).getJieQiTable())) tiet[s.toYmdHms()] = ten;
}
const ra = { nguon: "lunar-javascript 1.7.7 (https://github.com/6tail/lunar-javascript)", ngay, tiet_khi_utc8: tiet };
const f = path.resolve(__dirname, "..", "tests", "fixtures", "lunarjs_2025_2026.json.gz");
fs.writeFileSync(f, zlib.gzipSync(JSON.stringify(ra)));
console.log(Object.keys(ngay).length, "ngày,", Object.keys(tiet).length, "mốc tiết khí");
