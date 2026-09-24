// Xuất hệ số VSOP87D (quy chiếu điểm xuân phân của ngày) (Trái Đất: kinh độ L và bán kính R) từ thư viện astronomia
// (MIT, bản 4.2.0) sang data/lich/vsop87d_trai_dat.json cho tuvi/thien_van.py.
// Chạy: npm install astronomia@4.2.0 rồi node scripts/tao_vsop87.mjs <thư mục node_modules>
import fs from "node:fs";
import path from "node:path";
const nm = process.argv[2] || "node_modules";
const earth = (await import("file://" + path.resolve(nm, "astronomia/data/vsop87Dearth.js"))).default;
const ra = { nguon: "VSOP87D (Bretagnon & Francou 1988), chép từ astronomia 4.2.0 (MIT, data/vsop87Dearth.js)",
             don_vi: "L: radian, R: AU; mỗi hàng [A, B, C] -> A*cos(B + C*tau), tau = thiên niên kỷ Julius từ J2000",
             L: earth.L, R: earth.R };
fs.writeFileSync("data/lich/vsop87d_trai_dat.json", JSON.stringify(ra));
console.log(Object.entries(ra.L).map(([k, v]) => `L${k}:${v.length}`).join(" "),
            Object.entries(ra.R).map(([k, v]) => `R${k}:${v.length}`).join(" "));
