"use strict";

const $ = (s, g = document) => g.querySelector(s);
const $$ = (s, g = document) => [...g.querySelectorAll(s)];
const esc = (v) => String(v ?? "").replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const ds = (v) => Array.isArray(v) ? v.join(", ") : (v ?? "");

const HUONG_8 = ["Bắc", "Đông Bắc", "Đông", "Đông Nam", "Nam", "Tây Nam", "Tây", "Tây Bắc"];
const DAC_TINH_TAT = { "Miếu": "M", "Vượng": "V", "Đắc": "Đ", "Bình": "B", "Hãm": "H" };

// Máy chủ trên Cloud Run tắt khi vắng người, lúc bật lại phải nạp Pyodide mất vài
// giây; trong lúc đó trình duyệt có thể báo "Failed to fetch" hoặc nhận trang lỗi
// 502/503 không phải JSON. Nên thử lại vài lần rồi mới báo lỗi, bằng tiếng Việt.
const LOI_KET_NOI = "Không kết nối được máy chủ — có thể máy chủ đang khởi động lại. "
  + "Đợi vài giây rồi bấm lại.";
const doi = (ms) => new Promise((r) => setTimeout(r, ms));

async function api(duongDan, tham) {
  const u = new URL(duongDan, location.href);
  Object.entries(tham).forEach(([k, v]) => v !== "" && v != null && u.searchParams.set(k, v));
  for (let lan = 0; ; lan++) {
    let res;
    try {
      res = await fetch(u);
    } catch {   // mất mạng, máy chủ đang bật lại: fetch ném lỗi chứ không trả mã
      if (lan < 2) { await doi(1500 * (lan + 1)); continue; }
      throw new Error(LOI_KET_NOI);
    }
    const data = await res.json().catch(() => null);
    if (res.ok && data) return data;
    if (data?.loi) throw new Error(data.loi);   // lỗi do dữ liệu nhập: báo ngay, không thử lại
    if (res.status >= 500 && lan < 2) { await doi(1500 * (lan + 1)); continue; }
    throw new Error(res.status >= 500 ? LOI_KET_NOI : "Không lấy được dữ liệu");
  }
}

function baoLoi(o, e) {
  o.innerHTML = `<div class="the"><p class="loi">Lỗi: ${esc(e.message)}</p></div>`;
}

/* ------------------------------- tab ------------------------------- */
$$(".tab-nut").forEach((nut) => nut.addEventListener("click", () => {
  $$(".tab-nut").forEach((n) => n.classList.toggle("dang-chon", n === nut));
  $$(".tab-noi-dung").forEach((s) => s.classList.toggle("dang-chon", s.id === "tab-" + nut.dataset.tab));
}));

/* --------------------------- ngăn kéo sao --------------------------- */
const nganKeo = $("#ngan-keo"), manChe = $("#man-che");
function moNganKeo(html) {
  $("#ngan-keo-noi-dung").innerHTML = html;
  nganKeo.hidden = manChe.hidden = false;
  nganKeo.scrollTop = 0;
}
function dongNganKeo() { nganKeo.hidden = manChe.hidden = true; }
$("#dong-ngan-keo").addEventListener("click", dongNganKeo);
manChe.addEventListener("click", dongNganKeo);
document.addEventListener("keydown", (e) => e.key === "Escape" && dongNganKeo());

/* ------------------------------ lá số ------------------------------ */
const CHI_GIO = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"];
const KHUNG_GIO = ["23h–1h", "1h–3h", "3h–5h", "5h–7h", "7h–9h", "9h–11h",
                   "11h–13h", "13h–15h", "15h–17h", "17h–19h", "19h–21h", "21h–23h"];
// Giờ đồng hồ -> chỉ số canh (23:00–00:59 là Tý), giống tuvi.canchi.chi_gio_tu_gio_phut.
const canhTuGio = (gio, phut) => Math.floor(((gio * 60 + phut + 60) % 1440) / 120);

(function dungOCanhGio() {
  const oCanh = $("#ls-canh"), oGio = $("#ls-gio");
  oCanh.innerHTML = CHI_GIO.map((c, i) => `<option value="${i}">Giờ ${c} (${KHUNG_GIO[i]})</option>`).join("");
  const dongBoTuGio = () => {
    const [g, p] = oGio.value.split(":").map(Number);
    if (!Number.isNaN(g)) oCanh.value = canhTuGio(g, p || 0);
  };
  // Chọn canh: đặt đồng hồ về đầu canh (Tý về 00:00 để giữ nguyên ngày sinh).
  oCanh.addEventListener("change", () => {
    const i = Number(oCanh.value);
    oGio.value = i === 0 ? "00:00" : `${String(i * 2).padStart(2, "0")}:00`;
  });
  oGio.addEventListener("input", dongBoTuGio);
  dongBoTuGio();
})();

function lopSao(s) {
  if (s.nhom === "Chính tinh") return "chinh-tinh";
  if (s.tinh_chat === "cát") return "cat";
  if (s.tinh_chat === "hung") return "hung";
  return "trung";
}

// Sao luôn hiện trên ô cung; sao còn lại gập vào nút "+N" (bấm để xổ) hoặc bật
// "Hiện đủ 109 sao" ở chú giải. Chính tinh, Tứ Hóa luôn hiện.
const SAO_CHINH_YEU = new Set(["Tả Phù", "Hữu Bật", "Văn Xương", "Văn Khúc", "Thiên Khôi", "Thiên Việt",
  "Kình Dương", "Đà La", "Hỏa Tinh", "Linh Tinh", "Địa Không", "Địa Kiếp", "Lộc Tồn", "Thiên Mã",
  "Đào Hoa", "Hồng Loan", "Thiên Hình", "Thiên Riêu", "Thiên Không", "Thái Tuế", "Tràng Sinh", "Đế Vượng"]);
const saoLuonHien = (s) => s.nhom === "Chính tinh" || s.nhom === "Tứ Hóa" || SAO_CHINH_YEU.has(s.ten);

function veCung(c, laMenh) {
  let an = 0;
  const sao = c.sao.map((s) => {
    const dt = s.dac_tinh ? `<span class="dt" title="${esc(s.dac_tinh)} địa">${DAC_TINH_TAT[s.dac_tinh] || ""}</span>` : "";
    const phu = saoLuonHien(s) ? "" : (an++, " phu");
    return `<button class="sao ${lopSao(s)}${phu}" data-sao="${esc(s.ten)}">${esc(s.ten)}${dt}</button>`;
  }).join("") + (an ? `<button class="sao xo" type="button" title="Xem thêm ${an} sao">+${an}</button>` : "");
  return `<div class="cung${laMenh ? " la-menh" : ""}">
    <div class="cung-dau">
      <span class="cung-ten">${esc(c.ten_cung)}</span>
      <span class="cung-chi">${esc(c.can)} ${esc(c.chi)}</span>
    </div>
    <div class="cung-sao">${sao || '<span class="cung-chi">—</span>'}</div>
    <div class="cung-chan">
      <span>Đại hạn ${esc(c.dai_han)}</span>
      ${c.tuan ? '<span class="nhan-tuan" title="Tuần không vong án ngữ">TUẦN</span>' : ""}
      ${c.triet ? '<span class="nhan-tuan" title="Triệt lộ án ngữ">TRIỆT</span>' : ""}
      ${c.la_cung_than ? '<span class="nhan-than">THÂN</span>' : ""}
    </div>
  </div>`;
}

function veLaSo(d) {
  const am = d.am_lich;
  $("#ls-tom-tat").innerHTML = [
    ["Âm lịch", `${am.ngay}/${am.thang}${am.nhuan ? " nhuận" : ""}/${am.nam} · giờ ${am.gio}`],
    ["Năm sinh", `${d.nam_sinh_can_chi} (${d.con_giap})`],
    ["Bản mệnh", d.menh_nap_am],
    ["Cục", d.cuc],
    ["Mệnh tại", d.cung_menh],
    ["Thân cư", d.cung_than_tai],
    ["Chính tinh Mệnh", d.chinh_tinh_menh.length ? d.chinh_tinh_menh.join(" + ") : "Vô chính diệu"],
    ["Đại hạn đi", `${d.chieu_di_han} (${d.am_duong_nam_sinh} ${d.gioi_tinh})`],
    ["Tuần / Triệt", `${d.tuan.join("–")} / ${d.triet.join("–")}`],
  ].map(([k, v]) => `<div class="o-tom-tat"><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join("");

  const cung = d.bo_cuc.flat().filter(Boolean);
  const thienBan = `<div class="thien-ban">
    ${[["Tuổi", `${d.nam_sinh_can_chi} · ${d.con_giap}`],
       ["Bản mệnh", d.menh_nap_am],
       ["Ngũ hành cục", d.cuc],
       ["Giờ sinh", am.gio],
       ["Hóa Lộc", d.tu_hoa["Hóa Lộc"]],
       ["Hóa Quyền", d.tu_hoa["Hóa Quyền"]],
       ["Hóa Khoa", d.tu_hoa["Hóa Khoa"]],
       ["Hóa Kỵ", d.tu_hoa["Hóa Kỵ"]]]
      .map(([k, v]) => `<div class="dong"><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join("")}
  </div>`;
  $("#dia-ban").innerHTML = cung.map((c) => veCung(c, c.ten_cung === "Mệnh")).join("") + thienBan;

  $("#ls-cach-cuc").innerHTML = `<h3>Cách cục nhận ra được (${d.cach_cuc_goi_y.length})</h3>` +
    (d.cach_cuc_goi_y.length
      ? `<table class="xep-chong"><thead><tr><th>Cách</th><th>Tính chất</th><th>Luận giải</th></tr></thead><tbody>` +
        d.cach_cuc_goi_y.map((c) => `<tr>
            <td data-nhan="Cách"><b>${esc(c.ten)}</b><br><span class="cung-chi">${esc(c.dieu_kien)}</span></td>
            <td data-nhan="Tính chất"><span class="nhan-tt ${c.tinh_chat.startsWith("xấu") ? "xau" : c.tinh_chat.startsWith("trung") ? "vua" : "tot"}">${esc(c.tinh_chat)}</span></td>
            <td data-nhan="Luận giải">${esc(c.luan_giai)}</td></tr>`).join("") + "</tbody></table>"
      : "<p class=\"goi-y\">Lá số này không khớp cách cục nào trong bộ 92 cách đang có.</p>");

  $("#ls-ket-qua").hidden = false;
  $("#xuat-trang-thai").textContent = XUAT_GOI_Y;
  $("#ls-goi-y").hidden = true;
  $("#ls-luan-giai").hidden = true;
  $("#ls-luan-giai").innerHTML = "";
  $("#hang-ai").hidden = true;
  $("#ls-ai").hidden = true;
  $("#ls-ai").innerHTML = "";
}

/* --------------------------- luận giải chi tiết --------------------------- */
const NHAN_DANH_GIA = { "vượng": "tot", "khá": "tot", "trung bình": "vua", "yếu": "yeu", "xấu": "xau" };
const dau = (n) => (n > 0 ? "+" + n : String(n));

function veKhoanDiem(khoan) {
  if (!khoan.length) return '<span class="lg-khoan">Không có sao nào được chấm điểm.</span>';
  return `<div class="lg-khoan">${khoan.map((k) =>
    `<span class="${k.diem > 0 ? "duong" : k.diem < 0 ? "am" : ""}">${dau(k.diem)} ${esc(k.ly_do)}</span>`).join("")}</div>`;
}

function veCungLuan(c, mo) {
  const nhan = `<span class="nhan-tt ${NHAN_DANH_GIA[c.danh_gia] || "vua"}">${esc(c.danh_gia)} · ${dau(c.diem)}</span>`;
  const chinh = c.chinh_tinh.length
    ? c.chinh_tinh.map((s) => `<li><b>${esc(s.ten)}</b>${s.dac_tinh ? ` <span class="cung-chi">(${esc(s.dac_tinh)})</span>` : ""} — ${esc(s.y_nghia)}</li>`).join("")
    : `<li><i>Vô chính diệu</i>${c.muon_chinh_tinh.length ? ` — mượn ${esc(c.muon_chinh_tinh.join(" + "))} từ cung ${esc(c.xung_chieu.ten_cung)}` : ""}</li>`;
  const danhSach = (tieuDe, ds) => ds.length
    ? `<h4>${tieuDe}</h4><ul>${ds.map((s) => `<li><b>${esc(s.ten)}</b> — ${esc(s.y_nghia)}</li>`).join("")}</ul>` : "";
  return `<details class="lg-cung"${mo ? " open" : ""}>
    <summary><b>${esc(c.ten_cung)}</b>${c.la_cung_than ? '<span class="than">THÂN</span>' : ""}${c.tuan ? '<span class="than">TUẦN</span>' : ""}${c.triet ? '<span class="than">TRIỆT</span>' : ""}${nhan}
      <span class="cung-chi">${esc(c.can)} ${esc(c.chi)} · đại hạn ${esc(c.dai_han)}</span></summary>
    <div class="lg-than">
      <p>${esc(c.luan)}</p>
      <h4>Chính tinh</h4><ul>${chinh}</ul>
      ${danhSach("Cát tinh", c.cat_tinh)}
      ${danhSach("Sát tinh, bại tinh", c.sat_tinh)}
      ${c.trung_tinh.length ? `<h4>Sao khác</h4><p>${esc(c.trung_tinh.join(", "))}</p>` : ""}
      <h4>Nội dung nên xem ở cung này</h4><p>${esc(c.noi_dung_xem.join(" · "))}</p>
      <h4>Điểm gợi ý (từng khoản)</h4>${veKhoanDiem(c.khoan_diem)}
    </div>
  </details>`;
}

function veLuanGiai(d) {
  const tq = d.tong_quan;
  const theTongQuan = [
    ["Bản mệnh", `${tq.ban_menh.nap_am} (${tq.ban_menh.hanh})`, tq.ban_menh.y_nghia],
    ["Tính cách theo hành", tq.ban_menh.hanh, tq.ban_menh.tinh_cach_hanh],
    ["Cục", tq.cuc.ten, tq.cuc.y_nghia],
    ["Mệnh — Cục", tq.menh_cuc.quan_he, tq.menh_cuc.nhan_xet],
    ["Âm dương", tq.am_duong.ten, tq.am_duong.nhan_xet],
    ["Thân cư", tq.than.cung, tq.than.nhan_xet],
  ].map(([k, v, p]) => `<div class="the lg-the"><span class="dau">${esc(k)}</span><b>${esc(v)}</b><p>${esc(p)}</p></div>`).join("");

  const tuHoa = d.tu_hoa.map((h) => `<li><b>${esc(h.hoa)}</b> → ${esc(h.sao)}${h.cung ? ` tại <b>${esc(h.cung)}</b>` : ""}: ${esc(h.nhan_xet)}</li>`).join("");

  const dh = d.dai_han;
  const hienTai = dh.hien_tai
    ? `<p>Năm ${dh.nam_xem}, tuổi mụ <b>${dh.tuoi_mu}</b>: đang đi đại hạn <b>${esc(dh.hien_tai.tuoi)}</b> tại cung
       <b>${esc(dh.hien_tai.cung)}</b> (${esc(dh.hien_tai.chi)}) — chính tinh ${esc(dh.hien_tai.chinh_tinh.join(" + ") || "vô chính diệu")}${dh.hien_tai.tu_hoa.length ? `, có ${esc(dh.hien_tai.tu_hoa.join(", "))}` : ""}.</p>`
    : `<p class="goi-y">Năm ${dh.nam_xem}: tuổi mụ ${dh.tuoi_mu} chưa vào đại hạn nào trong bảng.</p>`;
  const bangDaiHan = `<table class="lg-dai-han"><thead><tr><th>Tuổi</th><th>Cung</th><th>Chính tinh</th><th>Tứ Hóa</th></tr></thead><tbody>` +
    dh.bang.map((h) => `<tr class="${h.hien_tai ? "hien-tai" : ""}"><td>${esc(h.tuoi)}</td><td>${esc(h.cung)} (${esc(h.chi)})</td>
      <td>${esc(h.chinh_tinh.join(" + ") || "—")}</td><td>${esc(h.tu_hoa.join(", ") || "—")}</td></tr>`).join("") + "</tbody></table>";

  const nx = d.nam_xem;
  const khoiNamXem = nx ? `
    <div class="lg-phan the"><h3>Năm ${nx.nam_xem} — ${esc(nx.nam_xem_can_chi)}, tuổi mụ ${nx.tuoi_mu}
      <span class="nhan-tt ${nx.diem >= 2 ? "tot" : nx.diem <= -2 ? "xau" : "vua"}">${dau(nx.diem)}</span></h3>
      ${nx.nhan_xet.map((t) => `<p>${esc(t)}</p>`).join("")}
      <div class="luoi">
        <div><h4>Tiểu hạn</h4><p><b>${esc(nx.tieu_han.ten_cung)}</b> (${esc(nx.tieu_han.chi)}) —
          ${esc(nx.tieu_han.chinh_tinh.join(" + ") || "vô chính diệu")}${nx.tieu_han.tuan ? " · TUẦN" : ""}${nx.tieu_han.triet ? " · TRIỆT" : ""}<br>
          <span class="cung-chi">Sao lưu: ${esc(nx.tieu_han.sao_luu.join(", ") || "không")}</span></p></div>
        ${nx.dai_han ? `<div><h4>Đại hạn ${esc(nx.dai_han.tuoi)}</h4><p><b>${esc(nx.dai_han.ten_cung)}</b> (${esc(nx.dai_han.chi)}) —
          ${esc(nx.dai_han.chinh_tinh.join(" + ") || "vô chính diệu")}<br>
          <span class="cung-chi">Sao lưu: ${esc(nx.dai_han.sao_luu.join(", ") || "không")}</span></p></div>` : ""}
        <div><h4>Lưu Tứ Hóa năm nay</h4><p>${Object.entries(nx.luu_tu_hoa).map(([h, s]) => `${esc(h.replace("Lưu ", ""))} → <b>${esc(s)}</b>`).join(" · ")}</p></div>
      </div>
      <h4>Sao lưu rơi vào từng cung</h4>
      <table class="lg-dai-han"><tbody>${nx.sao_luu_theo_cung.map((c) => `<tr class="${c.ten_cung === nx.tieu_han.ten_cung ? "hien-tai" : ""}">
        <td>${esc(c.ten_cung)} (${esc(c.chi)})</td><td>${esc(c.sao_luu.map((t) => t.replace("Lưu ", "")).join(", ") || "—")}</td></tr>`).join("")}</tbody></table>
      <h4>Điểm gợi ý của năm (từng khoản)</h4>${veKhoanDiem(nx.khoan_diem.map((k) => ({ ...k, ly_do: `${k.ly_do} (${k.noi})` })))}
      <p class="goi-y">${esc(nx.ghi_chu)}</p>
    </div>` : "";
  const tk = d.thong_ke;
  $("#ls-luan-giai").innerHTML = `
    <div class="lg-phan"><h3>Tổng quan</h3><div class="luoi">${theTongQuan}</div></div>
    <div class="lg-phan the"><h3>Tứ Hóa</h3><ul>${tuHoa}</ul></div>
    <div class="lg-phan the"><h3>Đại hạn</h3>${hienTai}${bangDaiHan}<p class="goi-y">${esc(dh.ghi_chu)}</p></div>
    ${khoiNamXem}
    <div class="lg-phan"><h3>12 cung theo thứ tự đọc</h3>
      <p class="goi-y">Cung mạnh nhất: <b>${esc(tk.cung_manh_nhat)}</b> · yếu nhất: <b>${esc(tk.cung_yeu_nhat)}</b> ·
        ${tk.so_cung_vo_chinh_dieu} cung vô chính diệu · điểm trung bình ${tk.diem_trung_binh}.</p>
      ${d.cac_cung.map((c, i) => veCungLuan(c, i === 0)).join("")}
    </div>
    <div class="lg-phan the"><h3>Lưu ý</h3><ul class="lg-luu-y">${d.luu_y.map((l) => `<li>${esc(l)}</li>`).join("")}</ul></div>`;
  $("#ls-luan-giai").hidden = false;
  $("#hang-ai").hidden = false;
}

/* ---------------------------- ô chọn ngày ---------------------------- */
// Ô <input type="date"> gốc của trình duyệt hiện ngày theo vùng máy — máy đặt
// tiếng Anh là ra "08/22/1987", người Việt đọc dễ nhầm ngày với tháng.
//
// Nên thay bằng ô chữ luôn hiện "ngày/tháng/năm", bấm vào thì mở một bảng lịch
// tiếng Việt (tuần bắt đầu thứ Hai) có ô chọn tháng và năm để nhảy nhanh về năm
// sinh xa. Vẫn gõ tay được. Ô gốc được giữ lại (ẩn đi) nên mọi chỗ đang đọc
// .value dạng yyyy-mm-dd vẫn chạy y nguyên.
const TEN_THANG = ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
  "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"];
const THU = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"];

const hai = (n) => String(n).padStart(2, "0");
const isoCua = (d) => `${d.getFullYear()}-${hai(d.getMonth() + 1)}-${hai(d.getDate())}`;
const chuCua = (d) => `${hai(d.getDate())}/${hai(d.getMonth() + 1)}/${d.getFullYear()}`;
function tuIso(s) {
  const [y, m, d] = (s || "").split("-").map(Number);
  return y ? new Date(y, m - 1, d) : null;
}
// Nhận "22/8/1987", "22-08-1987", "22.8.1987"; sai ngày (31/2) thì trả null.
function docChuNgay(s) {
  const m = s.trim().match(/^(\d{1,2})\D+(\d{1,2})\D+(\d{4})$/);
  if (!m) return null;
  const d = new Date(+m[3], +m[2] - 1, +m[1]);
  return d.getDate() === +m[1] && d.getMonth() === +m[2] - 1 ? d : null;
}

function nangCapONgay(o) {
  const namMin = o.min ? +o.min.slice(0, 4) : 1900;
  const namMax = o.max ? +o.max.slice(0, 4) : 2199;
  const trongKhoang = (d) => d.getFullYear() >= namMin && d.getFullYear() <= namMax;

  const khung = document.createElement("div");
  khung.className = "o-lich";
  const chu = document.createElement("input");
  chu.type = "text";
  chu.className = "o-lich-chu";
  chu.placeholder = "ngày/tháng/năm";
  chu.inputMode = "numeric";
  chu.autocomplete = "off";
  chu.required = o.required;
  if (o.id) {   // nhãn <label for=...> trỏ sang ô chữ mới
    chu.id = o.id + "-chu";
    document.querySelector(`label[for="${o.id}"]`)?.setAttribute("for", chu.id);
  }
  const nut = document.createElement("button");
  nut.type = "button";
  nut.className = "nut-lich";
  nut.setAttribute("aria-label", "Mở lịch");
  nut.innerHTML = `<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"
    fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
    <rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>`;
  const bang = document.createElement("div");
  bang.className = "lich";
  bang.hidden = true;
  bang.setAttribute("role", "dialog");
  bang.setAttribute("aria-label", "Chọn ngày");
  khung.append(chu, nut, bang);
  o.after(khung);
  o.type = "hidden";
  o.required = false;

  let dangXem = new Date();   // tháng đang hiện trên bảng lịch
  let tro = null;             // ngày đang được trỏ bằng bàn phím

  function ghi(d) {
    o.value = isoCua(d);
    chu.value = chuCua(d);
    chu.setCustomValidity("");
    o.dispatchEvent(new Event("change", { bubbles: true }));
  }

  // Vẽ lại bảng lịch của tháng đang xem; trả về nút ngày đang được trỏ.
  function ve() {
    const nam = dangXem.getFullYear(), thang = dangXem.getMonth();
    const chon = o.value, homNay = isoCua(new Date());
    const dau = (new Date(nam, thang, 1).getDay() + 6) % 7;   // thứ Hai = 0
    const soNgay = new Date(nam, thang + 1, 0).getDate();
    let oNgay = "";
    for (let i = 0; i < dau; i++) oNgay += "<span></span>";
    for (let n = 1; n <= soNgay; n++) {
      const iso = `${nam}-${hai(thang + 1)}-${hai(n)}`;
      const lop = [iso === chon && "chon", iso === homNay && "hom-nay"].filter(Boolean).join(" ");
      oNgay += `<button type="button" data-ngay="${n}" class="${lop}" tabindex="-1"
        aria-label="${n} ${TEN_THANG[thang].toLowerCase()} năm ${nam}">${n}</button>`;
    }
    let namOpt = "";
    for (let y = namMin; y <= namMax; y++) namOpt += `<option${y === nam ? " selected" : ""}>${y}</option>`;
    bang.innerHTML = `
      <div class="lich-dau">
        <button type="button" class="lich-lui" aria-label="Tháng trước">‹</button>
        <select class="lich-thang" aria-label="Tháng">${TEN_THANG.map((t, i) =>
          `<option value="${i}"${i === thang ? " selected" : ""}>${t}</option>`).join("")}</select>
        <select class="lich-nam" aria-label="Năm">${namOpt}</select>
        <button type="button" class="lich-toi" aria-label="Tháng sau">›</button>
      </div>
      <div class="lich-thu">${THU.map((t) => `<span>${t}</span>`).join("")}</div>
      <div class="lich-ngay">${oNgay}</div>
      <div class="lich-chan">
        <button type="button" class="lich-hom-nay">Hôm nay</button>
        <button type="button" class="lich-dong">Đóng</button>
      </div>`;
    const cungThang = chon.startsWith(`${nam}-${hai(thang + 1)}-`);
    const ngayTro = tro && tro.getMonth() === thang && tro.getFullYear() === nam
      ? tro.getDate() : (cungThang ? Number(chon.slice(8)) : 1);
    const nutTro = bang.querySelector(`[data-ngay="${ngayTro}"]`);
    nutTro.tabIndex = 0;
    return nutTro;
  }

  function doiThang(buoc) {
    const d = new Date(dangXem.getFullYear(), dangXem.getMonth() + buoc, 1);
    if (!trongKhoang(d)) return;
    dangXem = d; tro = null; ve();
  }

  function mo() {
    if (!bang.hidden) return;
    dangXem = tuIso(o.value) || new Date();
    tro = null;
    ve();
    bang.hidden = false;
    // Sát mép phải màn hình thì canh bảng theo mép phải của ô.
    bang.classList.remove("canh-phai");
    if (bang.getBoundingClientRect().right > document.documentElement.clientWidth - 8) {
      bang.classList.add("canh-phai");
    }
    bang.scrollIntoView({ block: "nearest" });
  }

  function dong(traVe = true) {
    if (bang.hidden) return;
    bang.hidden = true;
    if (traVe) chu.focus();
  }

  chu.addEventListener("click", mo);
  nut.addEventListener("click", () => (bang.hidden ? mo() : dong()));
  chu.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") {
      e.preventDefault(); mo(); bang.querySelector('.lich-ngay [tabindex="0"]')?.focus();
    } else if (e.key === "Escape") dong();
  });
  // Gõ tay: đúng dạng thì nhận ngay, sai thì trình duyệt báo khi bấm Xem.
  chu.addEventListener("input", () => {
    const d = docChuNgay(chu.value);
    if (d && trongKhoang(d)) {
      o.value = isoCua(d);
      chu.setCustomValidity("");
      o.dispatchEvent(new Event("change", { bubbles: true }));
      if (!bang.hidden) { dangXem = d; ve(); }
    } else {
      o.value = "";
      chu.setCustomValidity(chu.value
        ? `Gõ theo dạng ngày/tháng/năm, năm từ ${namMin} đến ${namMax}.` : "");
    }
  });
  // Rời ô thì viết lại cho gọn: "5/8/1987" thành "05/08/1987".
  chu.addEventListener("blur", () => { const d = tuIso(o.value); if (d) chu.value = chuCua(d); });

  bang.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    if (b.dataset.ngay) {
      ghi(new Date(dangXem.getFullYear(), dangXem.getMonth(), +b.dataset.ngay));
      dong();
    } else if (b.classList.contains("lich-lui")) doiThang(-1);
    else if (b.classList.contains("lich-toi")) doiThang(1);
    else if (b.classList.contains("lich-hom-nay")) { ghi(new Date()); dong(); }
    else if (b.classList.contains("lich-dong")) dong();
  });
  bang.addEventListener("change", (e) => {
    if (!e.target.matches(".lich-thang, .lich-nam")) return;
    const laThang = e.target.matches(".lich-thang");
    dangXem = new Date(+bang.querySelector(".lich-nam").value,
      +bang.querySelector(".lich-thang").value, 1);
    tro = null;
    ve();
    bang.querySelector(laThang ? ".lich-thang" : ".lich-nam").focus();
  });
  // Mũi tên đi từng ngày / từng tuần, PageUp/PageDown sang tháng, Enter để chọn.
  bang.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { e.preventDefault(); dong(); return; }
    const b = e.target.closest(".lich-ngay button");
    if (!b) return;
    const buoc = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7 }[e.key];
    const thang = { PageUp: -1, PageDown: 1 }[e.key];
    if (!buoc && !thang) return;
    e.preventDefault();
    const y = dangXem.getFullYear(), m = dangXem.getMonth(), n = +b.dataset.ngay;
    const moi = buoc ? new Date(y, m, n + buoc) : new Date(y, m + thang, 1);
    if (!trongKhoang(moi)) return;
    tro = moi;
    dangXem = new Date(moi.getFullYear(), moi.getMonth(), 1);
    ve().focus();
  });
  // Bấm ra ngoài hoặc chuyển tiêu điểm đi chỗ khác thì đóng.
  document.addEventListener("pointerdown", (e) => { if (!khung.contains(e.target)) dong(false); });
  khung.addEventListener("focusout", (e) => {
    if (e.relatedTarget && !khung.contains(e.relatedTarget)) dong(false);
  });

  // Các chỗ khác trong app đặt giá trị bằng datNgay(); nghe sự kiện này để ô
  // chữ luôn khớp với ô ẩn dù ai đặt giá trị.
  o.addEventListener("dat-gia-tri", () => {
    const d = tuIso(o.value);
    chu.value = d ? chuCua(d) : "";
    chu.setCustomValidity("");
  });
}

$$('input[type="date"]').forEach(nangCapONgay);

// Đặt giá trị cho ô ngày từ mã: dùng hàm này thay cho gán .value trực tiếp,
// để ô chữ hiển thị cập nhật theo.
function datNgay(o, giaTri) {
  o.value = giaTri;
  o.dispatchEvent(new Event("dat-gia-tri"));
}

/* ------------------------------ hợp tuổi ------------------------------ */
function veHopTuoi(d) {
  const nguoi = (n, nhan) => `<div class="o-tom-tat"><span>${nhan} (${n.gioi_tinh === "nam" ? "Nam" : "Nữ"})</span>
    <b>${esc(n.can_chi)} (${esc(n.con_giap)})</b>
    <span>${esc(n.nap_am)} · cung ${esc(n.cung_phi)} · ${esc(n.nhom_bat_trach)}</span></div>`;
  const hang = (m) => `<tr>
    <td data-nhan="Xét về"><b>${esc(m.muc)}</b></td>
    <td data-nhan="Kết quả">${esc(m.ket_qua)}</td>
    <td data-nhan="Tính chất"><span class="nhan-tt ${m.tinh_chat === "xấu" ? "xau"
      : m.tinh_chat === "tốt" ? "tot" : "vua"}">${esc(m.tinh_chat)}</span></td>
    <td data-nhan="Điểm">${m.diem > 0 ? "+" : ""}${m.diem}</td>
    <td data-nhan="Giải thích">${esc(m.giai_thich)}</td></tr>`;

  // Cao Ly Đầu Hình: lời xưa chép nguyên văn, không chấm điểm.
  const cl = d.cao_ly_dau_hinh;
  const htmlCaoLy = cl ? `<div class="the">
      <h3>Cao Ly Đầu Hình — chồng can ${esc(cl.can_chong)}, vợ chi ${esc(cl.chi_vo)}</h3>
      <p class="goi-y">Lối xem "Nam dụng Can, Nữ dụng Chi": can năm sinh của chồng phối với
        chi năm sinh của vợ. Lời xưa chép nguyên văn, không tính vào điểm.</p>
      <div class="caoly-tho">${esc(cl.loi)}</div></div>` : "";

  // Hành trung gian và năm sinh con (chỉ khi xem hôn nhân một nam một nữ).
  const tg = d.hanh_trung_gian;
  const htmlSinhCon = d.sinh_con_goi_y ? `<div class="the">
      <h3>Năm sinh con (${d.sinh_con_goi_y.length} năm tới)</h3>
      <p class="goi-y">${tg ? `Hai mệnh khắc nhau. ${esc(tg.giai_thich)}`
        : "Hai mệnh không khắc nhau nên không cần hành trung gian."}
        Bảng dưới liệt kê mệnh và chi của từng năm so với bố và mẹ; điểm chỉ để xếp thứ tự.</p>
      <table class="xep-chong">
        <thead><tr><th>Năm</th><th>Can chi</th><th>Mệnh</th><th>Điểm</th><th>Lý do</th></tr></thead>
        <tbody>${d.sinh_con_goi_y.map((c) => `<tr>
          <td data-nhan="Năm"><b>${c.nam}</b></td>
          <td data-nhan="Can chi">${esc(c.can_chi)}</td>
          <td data-nhan="Mệnh">${esc(c.nap_am)} (${esc(c.hanh)})${c.la_hanh_trung_gian
            ? ' <span class="nhan-tt tot">hành trung gian</span>' : ""}</td>
          <td data-nhan="Điểm">${c.diem > 0 ? "+" : ""}${c.diem}</td>
          <td data-nhan="Lý do">${c.ly_do.map(esc).join("; ")}</td></tr>`).join("")}
        </tbody></table></div>` : "";

  $("#ht-ket-qua").innerHTML = `
    <div class="the-tom-tat">${nguoi(d.nguoi_a, "Người thứ nhất")}${nguoi(d.nguoi_b, "Người thứ hai")}
      <div class="o-tom-tat"><span>Chênh lệch</span><b>${d.chenh_lech_tuoi} tuổi</b></div>
      <div class="o-tom-tat"><span>Kết luận</span>
        <b class="ht-${d.diem >= 4 ? "tot" : d.diem >= 0 ? "vua" : "xau"}">${esc(d.danh_gia)}</b>
        <span>${d.diem > 0 ? "+" : ""}${d.diem} điểm — ${esc(d.nhan_xet)}</span></div>
    </div>
    ${d.canh_bao.map((c) => `<div class="the canh-bao"><b>⚠ ${esc(c.ten)}</b>
        <p>${esc(c.giai_thich)}</p></div>`).join("")}
    <div class="the"><h3>Bốn mặt đã xét</h3>
      <table class="xep-chong"><thead><tr><th>Xét về</th><th>Kết quả</th><th>Tính chất</th>
        <th>Điểm</th><th>Giải thích</th></tr></thead>
        <tbody>${d.muc_xet.map(hang).join("")}</tbody></table></div>
    ${htmlCaoLy}
    ${htmlSinhCon}
    <div class="the"><h3>Lưu ý</h3><ul class="lg-luu-y">
      ${d.luu_y.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>`;
}

$("#form-ht").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    veHopTuoi(await api("/api/hoptuoi", {
      ngay_sinh_a: $("#ht-sinh-a").value, gioi_tinh_a: $("#ht-gt-a").value,
      ngay_sinh_b: $("#ht-sinh-b").value, gioi_tinh_b: $("#ht-gt-b").value,
      muc_dich: $("#ht-muc-dich") ? $("#ht-muc-dich").value : "hon_nhan",
    }));
  } catch (err) { baoLoi($("#ht-ket-qua"), err); }
});

/* --------------------- xuất lá số ra ảnh / PDF --------------------- */
const XUAT_GOI_Y = $("#xuat-trang-thai").textContent;

function urlAnh(taiVe) {
  const [nam, thang, ngay] = $("#ls-ngay").value.split("-").map(Number);
  const [gio, phut] = $("#ls-gio").value.split(":").map(Number);
  const u = new URL("/api/laso.svg", location.href);
  Object.entries({ ngay, thang, nam, gio, phut, gioi_tinh: $("#ls-gt").value,
                   tai_ve: taiVe ? 1 : "" })
    .forEach(([k, v]) => v !== "" && v != null && u.searchParams.set(k, v));
  return u;
}

function tenTep(duoi) {
  const [nam, thang, ngay] = $("#ls-ngay").value.split("-");
  return `la-so-${nam}${thang}${ngay}-${$("#ls-gt").value}.${duoi}`;
}

function taiVe(url, ten) {
  const a = document.createElement("a");
  a.href = url; a.download = ten;
  document.body.appendChild(a); a.click(); a.remove();
}

$("#nut-svg").addEventListener("click", () => {
  taiVe(urlAnh(true).toString(), tenTep("svg"));
  $("#xuat-trang-thai").textContent = "Đang tải tệp SVG về máy.";
});

$("#nut-png").addEventListener("click", async () => {
  const nut = $("#nut-png"), trangThai = $("#xuat-trang-thai");
  const chuCu = nut.textContent;
  nut.disabled = true; nut.textContent = "Đang dựng ảnh…";
  try {
    const res = await fetch(urlAnh(false));
    if (!res.ok) throw new Error((await res.json()).loi || "Không lấy được ảnh");
    const svg = await res.text();
    // Vẽ SVG lên canvas rồi xuất PNG. Nhân 2 cho ảnh nét trên màn hình mật độ cao.
    const ti = 2;
    const co = svg.match(/width="(\d+)" height="(\d+)"/);
    const [w, h] = [Number(co[1]), Number(co[2])];
    const blob = new Blob([svg], { type: "image/svg+xml;charset=utf-8" });
    const nguon = URL.createObjectURL(blob);
    const anh = new Image();
    await new Promise((xong, hong) => {
      anh.onload = xong;
      anh.onerror = () => hong(new Error("Trình duyệt không đọc được ảnh SVG"));
      anh.src = nguon;
    });
    const khung = document.createElement("canvas");
    khung.width = w * ti; khung.height = h * ti;
    const ve = khung.getContext("2d");
    ve.fillStyle = "#ffffff";
    ve.fillRect(0, 0, khung.width, khung.height);
    ve.drawImage(anh, 0, 0, khung.width, khung.height);
    URL.revokeObjectURL(nguon);
    const png = await new Promise((xong) => khung.toBlob(xong, "image/png"));
    const urlPng = URL.createObjectURL(png);
    taiVe(urlPng, tenTep("png"));
    setTimeout(() => URL.revokeObjectURL(urlPng), 10000);
    trangThai.textContent = `Đã tải PNG ${khung.width}×${khung.height} điểm ảnh.`;
  } catch (err) {
    trangThai.textContent = `Không xuất được PNG: ${err.message}`;
  } finally {
    nut.disabled = false; nut.textContent = chuCu;
  }
});

$("#nut-in").addEventListener("click", async () => {
  const nut = $("#nut-in"), trangThai = $("#xuat-trang-thai");
  nut.disabled = true;
  try {
    const res = await fetch(urlAnh(false));
    if (!res.ok) throw new Error((await res.json()).loi || "Không lấy được ảnh");
    const svg = await res.text();
    // In từ một khung riêng: trang in chỉ có đúng lá số, không dính thanh tab,
    // biểu mẫu hay phần luận giải.
    let khung = $("#khung-in");
    if (!khung) {
      khung = document.createElement("iframe");
      khung.id = "khung-in";
      document.body.appendChild(khung);
    }
    const tai = new Promise((xong) => { khung.onload = xong; });
    khung.srcdoc = `<!doctype html><html lang="vi"><head><meta charset="utf-8">
      <title>${esc(tenTep("pdf"))}</title>
      <style>@page{size:A4 landscape;margin:8mm}
        html,body{margin:0;padding:0}
        svg{width:100%;height:auto;display:block}</style></head>
      <body>${svg}</body></html>`;
    await tai;
    khung.contentWindow.focus();
    khung.contentWindow.print();
    trangThai.textContent = 'Trong hộp in, chọn máy in là "Lưu thành PDF" (Save as PDF) để ra tệp PDF.';
  } catch (err) {
    trangThai.textContent = `Không in được: ${err.message}`;
  } finally {
    nut.disabled = false;
  }
});

/* ------------------------- luận giải bằng AI ------------------------- */
// Markdown tối giản -> HTML, luôn escape trước: ## tiêu đề, - gạch đầu dòng, **đậm**, đoạn văn.
function mdSangHtml(md) {
  const dong = esc(md).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").split("\n");
  let html = "", trongDs = false, doan = [];
  const xaDoan = () => { if (doan.length) { html += `<p>${doan.join(" ")}</p>`; doan = []; } };
  const dongDs = () => { if (trongDs) { html += "</ul>"; trongDs = false; } };
  for (const d of dong) {
    const t = d.trim();
    if (/^#{1,6}\s/.test(t)) { xaDoan(); dongDs(); html += `<h4>${t.replace(/^#+\s*/, "")}</h4>`; }
    else if (/^[-*]\s+/.test(t)) { xaDoan(); if (!trongDs) { html += "<ul>"; trongDs = true; } html += `<li>${t.replace(/^[-*]\s+/, "")}</li>`; }
    else if (t === "") { xaDoan(); dongDs(); }
    else doan.push(t);
  }
  xaDoan(); dongDs();
  return html;
}

$("#nut-ai").addEventListener("click", async () => {
  const [nam, thang, ngay] = $("#ls-ngay").value.split("-").map(Number);
  const [gio, phut] = $("#ls-gio").value.split(":").map(Number);
  const nut = $("#nut-ai"), o = $("#ls-ai");
  nut.disabled = true; nut.textContent = "Gemini đang viết…";
  o.hidden = false; o.innerHTML = '<p class="goi-y">Đang gửi số liệu lá số cho Gemini…</p>';
  try {
    const kq = await api("/api/ai-luangiai", { ngay, thang, nam, gio, phut,
      gioi_tinh: $("#ls-gt").value, nam_xem: $("#ls-nam-xem").value });
    o.innerHTML = `<div class="lg-phan"><h3>Luận giải bằng AI</h3>
      <p class="goi-y">Bài do ${esc(kq.model)} viết${kq.tu_cache ? " (lấy từ cache)" : ""} trên nền số liệu đã tính ở trên;
        AI có thể diễn đạt chưa chuẩn — đối chiếu tên sao, cung với lá số khi thấy lạ.</p>
      <div class="ai-van-ban">${mdSangHtml(kq.van_ban)}</div></div>`;
    o.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) { baoLoi(o, err); }
  finally { nut.disabled = false; nut.textContent = "Luận giải bằng AI (Gemini)"; }
});

$("#nut-luan-giai").addEventListener("click", async () => {
  const [nam, thang, ngay] = $("#ls-ngay").value.split("-").map(Number);
  const [gio, phut] = $("#ls-gio").value.split(":").map(Number);
  const nut = $("#nut-luan-giai");
  nut.disabled = true; nut.textContent = "Đang luận giải…";
  try {
    veLuanGiai(await api("/api/luangiai", { ngay, thang, nam, gio, phut,
      gioi_tinh: $("#ls-gt").value, nam_xem: $("#ls-nam-xem").value }));
    $("#ls-luan-giai").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) { baoLoi($("#ls-luan-giai"), err); $("#ls-luan-giai").hidden = false; }
  finally { nut.disabled = false; nut.textContent = "Luận giải chi tiết"; }
});

$("#dia-ban").addEventListener("click", async (e) => {
  const nut = e.target.closest(".sao");
  if (!nut) return;
  if (nut.classList.contains("xo")) { nut.closest(".cung").classList.toggle("mo"); return; }
  try {
    const s = await api("/api/sao", { ten: nut.dataset.sao });
    const dt = Object.entries(s.mieu_vuong_dac_ham || {});
    moNganKeo(`<h3>${esc(s.ten)}</h3>
      <dl>
        <dt>Nhóm</dt><dd>${esc(s.nhom)}</dd>
        <dt>Loại sao</dt><dd>${esc(s.loai)}</dd>
        <dt>Ngũ hành</dt><dd>${esc(s.hanh)}</dd>
        <dt>Tính chất</dt><dd>${esc(s.tinh_chat)}</dd>
        ${s.phuong_vi ? `<dt>Phương vị</dt><dd>${esc(s.phuong_vi)}</dd>` : ""}
        ${s.am_duong ? `<dt>Âm dương</dt><dd>${esc(s.am_duong)}</dd>` : ""}
      </dl>
      <p>${esc(s.y_nghia)}</p>
      ${dt.length ? `<h4>Miếu vượng đắc hãm theo cung</h4>
        <table><tbody>${dt.map(([k, v]) => `<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join("")}</tbody></table>` : ""}`);
  } catch (err) { moNganKeo(`<p class="loi">${esc(err.message)}</p>`); }
});

$("#form-laso").addEventListener("submit", async (e) => {
  e.preventDefault();
  const [nam, thang, ngay] = $("#ls-ngay").value.split("-").map(Number);
  const [gio, phut] = $("#ls-gio").value.split(":").map(Number);
  try {
    veLaSo(await api("/api/laso", { ngay, thang, nam, gio, phut, gioi_tinh: $("#ls-gt").value }));
  } catch (err) { baoLoi($("#ls-ket-qua"), err); $("#ls-ket-qua").hidden = false; }
});

/* ------------------------------- hạn ------------------------------- */
function veHan(d) {
  const s = d.sao_han, tt = d.tam_tai, tue = d.thai_tue, ln = d.lam_nha;
  const nhan = (t) => `<span class="nhan-tt ${t === "tốt" ? "tot" : t === "xấu" ? "xau" : "vua"}">${esc(t)}</span>`;
  $("#han-ket-qua").innerHTML = `
  <div class="the-tom-tat">
    ${[["Tuổi", `${d.tuoi_can_chi}`], ["Bản mệnh", d.nap_am], ["Tuổi mụ", d.tuoi_mu],
       ["Năm xem", d.nam_xem_can_chi], ["Giới tính", d.gioi_tinh === "nam" ? "Nam" : "Nữ"]]
      .map(([k, v]) => `<div class="o-tom-tat"><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join("")}
  </div>

  <div class="the">
    <h3>Sao chiếu mệnh: ${esc(s.sao)} ${nhan(s.tinh_chat)}</h3>
    <p>${esc(s.y_nghia)}</p>
    <table><tbody>
      <tr><th>Ảnh hưởng</th><td>${esc(ds(s.anh_huong))}</td></tr>
      <tr><th>Tháng kỵ</th><td>${s.thang_ky.length ? "tháng " + esc(ds(s.thang_ky)) : "không có"}</td></tr>
      <tr><th>Nặng với</th><td>${esc(s.nang_voi)}</td></tr>
      <tr><th>Cúng sao</th><td>ngày ${esc(s.ngay_cung_am_lich)} âm lịch hằng tháng · hướng ${esc(s.huong_cung)} · ${esc(s.so_den)} ngọn đèn</td></tr>
      <tr><th>Nên làm</th><td><ul>${s.hoa_giai.map((x) => `<li>${esc(x)}</li>`).join("")}</ul></td></tr>
    </tbody></table>
  </div>

  <div class="luoi">
    <div class="the">
      <h3>Tam tai ${tt.pham ? '<span class="nhan-tt xau">phạm</span>' : '<span class="nhan-tt tot">không phạm</span>'}</h3>
      ${tt.pham
        ? `<p><b>Năm thứ ${esc(tt.nam_thu)} — ${esc(tt.ten_dan_gian)}</b> (mức độ: ${esc(tt.muc_do)})</p>
           <p>${esc(tt.canh_bao)}</p>`
        : "<p>Năm nay tuổi này không nằm trong tam tai.</p>"}
      <p class="goi-y">Nhóm tam hợp ${esc(ds(tt.tam_hop))} gặp tam tai vào các năm ${esc(ds(tt.cac_nam_tam_tai))}.</p>
    </div>

    <div class="the">
      <h3>Thái Tuế ${tue.pham ? '<span class="nhan-tt xau">phạm</span>' : '<span class="nhan-tt tot">không phạm</span>'}</h3>
      ${tue.pham
        ? tue.chi_tiet.map((c) => `<p><b>${esc(c.ten)}</b> (${esc(c.muc_do)})<br>${esc(c.canh_bao)}</p>`).join("")
        : "<p>Chi tuổi không xung, hình, hại hay phá với chi năm.</p>"}
    </div>

    <div class="the">
      <h3>Xem tuổi làm nhà</h3>
      <table><tbody>
        <tr><th>Kim Lâu</th><td>${esc(ln.kim_lau.ten)}${ln.kim_lau.pham ? "" : " (số dư " + esc(ln.kim_lau.so_du) + ")"}</td></tr>
        <tr><th>Hoang Ốc</th><td>${esc(ln.hoang_oc.cung)} — ${ln.hoang_oc.tot ? "tốt" : "xấu"}</td></tr>
        <tr><th>Tam Tai</th><td>${ln.tam_tai.pham ? "phạm" : "không phạm"}</td></tr>
      </tbody></table>
      <p><b>${esc(ln.ket_luan)}</b></p>
    </div>
  </div>`;
}

$("#form-han").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    veHan(await api("/api/han", {
      ngay_sinh: $("#h-sinh").value, nam_xem: $("#h-xem").value, gioi_tinh: $("#h-gt").value,
    }));
  } catch (err) { baoLoi($("#han-ket-qua"), err); }
});

/* ---------------------------- phong thủy ---------------------------- */
function vePhongThuy(d) {
  const m = d.mau_sac_vat_pham;
  const hang = (h, nhanCuoi) => `<tr>
      <td data-nhan="Hướng"><b>${esc(h.huong)}</b></td>
      <td data-nhan="Du niên">${esc(h.du_nien)}</td>
      <td data-nhan="Ý nghĩa">${esc(h.y_nghia)}</td>
      <td data-nhan="${esc(nhanCuoi)}">${esc(ds(h.dung_cho))}</td></tr>`;
  $("#pt-ket-qua").innerHTML = `
  <div class="the-tom-tat">
    ${[["Năm sinh", `${d.nam_sinh_am_lich} (${d.nam_can_chi})`], ["Cung phi", d.cung_phi],
       ["Nhóm mệnh", d.nhom], ["Bản mệnh", `${d.menh_nap_am} (${d.hanh_nap_am})`],
       ["Hướng cung", d.huong_cung]]
      .map(([k, v]) => `<div class="o-tom-tat"><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join("")}
  </div>
  <div class="the"><p>${esc(d.y_nghia)}</p></div>

  ${d.danh_gia_huong_nha ? `<div class="the">
    <h3>Hướng nhà ${esc(d.danh_gia_huong_nha.huong_nha)}
      <span class="nhan-tt ${d.danh_gia_huong_nha.tinh_chat === "tốt" ? "tot" : "xau"}">${esc(d.danh_gia_huong_nha.du_nien)}</span></h3>
    <p>${esc(d.danh_gia_huong_nha.ket_luan)} ${esc(d.danh_gia_huong_nha.y_nghia)}</p></div>` : ""}

  <div class="the">
    <h3>Bốn hướng tốt</h3>
    <table class="xep-chong"><thead><tr><th>Hướng</th><th>Du niên</th><th>Ý nghĩa</th><th>Dùng cho</th></tr></thead>
    <tbody>${d.huong_tot.map((h) => hang(h, "Dùng cho")).join("")}</tbody></table>
  </div>
  <div class="the">
    <h3>Bốn hướng xấu</h3>
    <table class="xep-chong"><thead><tr><th>Hướng</th><th>Du niên</th><th>Ý nghĩa</th><th>Nên bố trí</th></tr></thead>
    <tbody>${d.huong_xau.map((h) => hang(h, "Nên bố trí")).join("")}</tbody></table>
  </div>
  <div class="the">
    <h3>Màu sắc và vật phẩm hợp mệnh ${esc(d.hanh_nap_am)}</h3>
    <table><tbody>
      <tr><th>Màu bản mệnh</th><td>${esc(ds(m.mau_ban_menh))}</td></tr>
      <tr><th>Màu tương sinh</th><td>${esc(ds(m.mau_tuong_sinh))}</td></tr>
      <tr><th>Màu nên tránh</th><td>${esc(ds(m.mau_ky))}</td></tr>
      <tr><th>Chất liệu</th><td>${esc(ds(m.chat_lieu))}</td></tr>
      <tr><th>Vật phẩm</th><td>${esc(ds(m.vat_pham))}</td></tr>
    </tbody></table>
  </div>
  <div class="the">
    <h3>Bố trí không gian</h3>
    <div class="luoi">${d.bo_tri_khong_gian.map((k) => `<div>
        <h4>${esc(k.khu_vuc)}</h4>
        <ul>${k.nguyen_tac.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
      </div>`).join("")}</div>
  </div>`;
}

$("#form-pt").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    vePhongThuy(await api("/api/phongthuy", {
      ngay_sinh: $("#pt-sinh").value, gioi_tinh: $("#pt-gt").value, huong: $("#pt-huong").value,
    }));
  } catch (err) { baoLoi($("#pt-ket-qua"), err); }
});

/* ----------------------------- xem ngày ----------------------------- */
const lopTC = (tc) => (tc === "tốt" ? "tot" : tc === "xấu" ? "xau" : "vua");
const nhanTC = (tc) => `<span class="nhan-tt ${lopTC(tc)}">${esc(tc)}</span>`;

function veNgay(d) {
  const mau = d.diem_tong_hop >= 70 ? "var(--cat)" : d.diem_tong_hop >= 45 ? "var(--vang)" : "var(--hung)";
  const am = d.am;
  const amLich = `${am.ngay}/${am.thang}${am.nhuan ? " nhuận" : ""} năm ${d.nam_can_chi}`;
  const tiet = d.tiet_chi_tiet;
  const t = d.tuoi;
  const dsTuoi = (x) => (x.length ? esc(x.join(", ")) : "—");
  const h = d.huong_xuat_hanh;
  const kieng = [...d.ngay_kieng.filter((x) => x !== "Thọ tử"),
    ...(d.tho_tu.length ? [`Thọ tử (${d.tho_tu.join("; ")})`] : [])];
  const sao = (ds_, tc) => ds_.length
    ? `<ul class="ds-sao">${ds_.map((s) => `<li><b>${esc(s.ten)}</b> <span class="han-tu">${esc(s.han_tu)}</span>
        — ${esc(s.y_nghia)}</li>`).join("")}</ul>`
    : `<p class="goi-y">Không có sao ${tc} nào trong 33 sao đã đối chiếu.</p>`;
  const hd = new Set(d.gio_hoang_dao.map((g) => g.chi));
  const canChiGio = Object.fromEntries([...d.gio_hoang_dao, ...d.gio_hac_dao].map((g) => [g.chi, g.can_chi]));
  const bt = (r) => `<p><b>${esc(r.han_viet)}</b> <span class="han-tu">${esc(r.han_tu)}</span><br>${esc(r.nghia)}</p>`;

  $("#ngay-ket-qua").innerHTML = `
  <div class="the-tom-tat">
    ${[["Dương lịch", `${d.thu}, ${d.duong_lich}`],
       ["Âm lịch", amLich],
       ["Tháng âm", `${d.thang_can_chi} (tháng ${am.so_ngay_thang === 30 ? "đủ 30" : "thiếu 29"} ngày)`],
       ["Ngày", `${d.ngay_can_chi} — ${d.nap_am_ngay}`],
       ["Tiết khí", `${tiet.ten} (từ ${tiet.bat_dau})`],
       ["Nhằm ngày", `${d.than_truc_nhat} ${d.loai_ngay.toLowerCase()}`]]
      .map(([k, v]) => `<div class="o-tom-tat"><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join("")}
  </div>
  ${kieng.length ? `<div class="the canh-bao"><b>⚠ Ngày này phạm: ${esc(kieng.join(" · "))}</b>
    <p>Dân gian kiêng các việc lớn (cưới hỏi, khởi công, xuất hành xa) vào những ngày này.</p></div>` : ""}
  <div class="luoi">
    <div class="the">
      <h3>Tuổi hợp và xung với ngày</h3>
      <p><b>Tam hợp:</b> ${dsTuoi(t.tam_hop)}<br><b>Lục hợp:</b> ${dsTuoi(t.luc_hop)}</p>
      <p><b>Xung:</b> ${dsTuoi(t.xung)}<br><b>Hình:</b> ${dsTuoi(t.hinh)}<br>
        <b>Hại:</b> ${dsTuoi(t.hai)}<br><b>Phá:</b> ${dsTuoi(t.pha)}</p>
      <p class="goi-y">Xét theo địa chi năm sinh của người xem.</p>
    </div>
    <div class="the">
      <h3>Ngũ hành ngày: ${esc(d.ngu_hanh_ngay.ten)} ${nhanTC(d.ngu_hanh_ngay.tinh_chat)}</h3>
      <p>Can ${esc(d.ngay_can_chi.split(" ")[0])} hành ${esc(d.ngu_hanh_ngay.hanh_can)}, chi
        ${esc(d.ngay_can_chi.split(" ")[1])} hành ${esc(d.ngu_hanh_ngay.hanh_chi)}: ${esc(d.ngu_hanh_ngay.quan_he.toLowerCase())}.</p>
      <p class="goi-y">Can sinh chi là Bảo nhật, chi sinh can là Nghĩa nhật, can khắc chi là Chế nhật,
        chi khắc can là Phạt nhật, cùng hành là Chuyên nhật.</p>
    </div>
    <div class="the">
      <h3>Khổng Minh lục diệu: ${esc(d.luc_dieu.ten)} ${nhanTC(d.luc_dieu.tinh_chat)}</h3>
      <p>${esc(d.luc_dieu.y_nghia)}</p>
    </div>
  </div>
  <div class="luoi">
    <div class="the">
      <h3>Trực ${esc(d.truc)} ${nhanTC(d.truc_y_nghia.tinh_chat)}</h3>
      <p>${esc(d.truc_y_nghia.tom_tat)}</p>
      <p><b>Nên:</b> ${esc(ds(d.truc_y_nghia.nen))}</p>
      <p><b>Kỵ:</b> ${esc(ds(d.truc_y_nghia.ky))}</p>
    </div>
    <div class="the">
      <h3>Sao ${esc(d.tu_y_nghia.ten_day_du || d.nhi_thap_bat_tu)} ${nhanTC(d.tu_y_nghia.tinh_chat)}</h3>
      <p>${esc(d.tu_y_nghia.mo_ta)}</p>
      <p><b>Nên:</b> ${esc(ds(d.tu_y_nghia.nen))}</p>
      <p><b>Kỵ:</b> ${esc(ds(d.tu_y_nghia.ky))}</p>
    </div>
  </div>
  <div class="luoi">
    <div class="the"><h3>Sao tốt (Ngọc Hạp Thông Thư)</h3>${sao(d.ngoc_hap.tot, "tốt")}</div>
    <div class="the"><h3>Sao xấu (Ngọc Hạp Thông Thư)</h3>${sao(d.ngoc_hap.xau, "xấu")}</div>
  </div>
  <div class="the">
    <h3>Giờ trong ngày</h3>
    <table class="xep-chong">
      <thead><tr><th>Giờ</th><th>Hoàng đạo</th><th>Xuất hành (Lý Thuần Phong)</th><th>Ý nghĩa</th></tr></thead>
      <tbody>${d.gio_xuat_hanh.map((g) => `<tr>
        <td data-nhan="Giờ"><b>${esc(canChiGio[g.chi])}</b> ${esc(g.khung_gio)}</td>
        <td data-nhan="Hoàng đạo">${hd.has(g.chi) ? '<span class="nhan-tt tot">hoàng đạo</span>'
          : '<span class="nhan-tt xau">hắc đạo</span>'}</td>
        <td data-nhan="Xuất hành">${esc(g.ten)} ${nhanTC(g.tinh_chat)}</td>
        <td data-nhan="Ý nghĩa">${esc(g.y_nghia)}</td></tr>`).join("")}</tbody>
    </table>
  </div>
  <div class="luoi">
    <div class="the">
      <h3>Hướng xuất hành</h3>
      <p><b>Hỷ thần (đón):</b> ${esc(h.hy_than)}</p>
      <p><b>Tài thần (đón):</b> ${esc(h.tai_than.join(" hoặc "))}
        ${h.tai_than_chua_thong_nhat ? '<br><span class="goi-y">Các sách Việt ghi khác nhau cho can này.</span>' : ""}</p>
      <p><b>Hạc thần (tránh):</b> ${h.hac_than === "Trên trời" ? "ở trên trời — không phải tránh hướng nào" : esc(h.hac_than)}</p>
    </div>
    <div class="the">
      <h3>Bành Tổ bách kỵ</h3>
      ${bt(d.banh_to.can)}${bt(d.banh_to.chi)}
    </div>
    <div class="the">
      <h3>Tiết khí</h3>
      <p><b>${esc(tiet.ten)}</b> bắt đầu lúc ${esc(tiet.bat_dau)}.</p>
      <p>Tiết kế tiếp: <b>${esc(tiet.ke_tiep)}</b> lúc ${esc(tiet.ke_tiep_bat_dau)}.</p>
      <p class="goi-y">Giờ Việt Nam; sai lệch dưới một phút.</p>
    </div>
  </div>
  <div class="the">
    <h3>Điểm tổng hợp ${d.diem_tong_hop}/100</h3>
    <div class="thanh-diem"><i style="width:${d.diem_tong_hop}%;background:${mau}"></i></div>
    <p class="goi-y">Điểm quy ước của app, chỉ xét trực, nhị thập bát tú, hoàng đạo và các ngày kỵ ở trên —
      không xét tuổi người xem. Muốn chọn ngày theo tuổi, dùng tab Chọn ngày.</p>
  </div>`;
}

/* ---------------------------- lịch tháng ---------------------------- */
let lichDangXem = null;   // {thang, nam} đang vẽ

async function veLichThang(thang, nam, chon) {
  const d = await api("/api/lichthang", { thang, nam });
  lichDangXem = { thang: d.thang, nam: d.nam };
  const dau = d.ngay[0].thu;                    // 0 = thứ Hai
  const o = [];
  for (let i = 0; i < dau; i++) o.push('<div class="lt-o rong"></div>');
  for (const x of d.ngay) {
    const iso = `${d.nam}-${String(d.thang).padStart(2, "0")}-${String(x.ngay).padStart(2, "0")}`;
    const amNgay = x.am.ngay === 1 || x.ngay === 1 ? `${x.am.ngay}/${x.am.thang}${x.am.nhuan ? "n" : ""}` : x.am.ngay;
    const ghi = [...x.le, ...(x.tiet ? [x.tiet] : [])];
    o.push(`<button type="button" class="lt-o${x.hoang_dao ? " hd" : ""}${iso === chon ? " chon" : ""}${x.thu === 6 ? " cn" : ""}"
      data-ngay="${iso}" title="${esc(`${x.can_chi} — ${x.than} ${x.hoang_dao ? "hoàng đạo" : "hắc đạo"}`
        + (x.kieng.length ? ` — phạm ${x.kieng.join(", ")}` : ""))}">
      <span class="lt-duong">${x.ngay}</span><span class="lt-am">${esc(amNgay)}</span>
      ${x.kieng.length ? '<i class="lt-ky" aria-label="ngày kỵ"></i>' : ""}
      ${ghi.length ? `<span class="lt-ghi">${esc(ghi[0])}</span>` : ""}</button>`);
  }
  $("#ngay-lich-thang").innerHTML = `<div class="the lich-thang">
    <div class="lt-dau">
      <button type="button" class="nut-phu" data-buoc="-1" aria-label="Tháng trước">‹</button>
      <b>Tháng ${d.thang} năm ${d.nam}</b>
      <button type="button" class="nut-phu" data-buoc="1" aria-label="Tháng sau">›</button>
    </div>
    <div class="lt-luoi">${["T2", "T3", "T4", "T5", "T6", "T7", "CN"].map((t) => `<span class="lt-thu">${t}</span>`).join("")}
      ${o.join("")}</div>
    <p class="goi-y lt-chu-thich"><i class="lt-cham hd"></i> hoàng đạo · <i class="lt-cham"></i> hắc đạo ·
      <i class="lt-ky"></i> ngày kỵ (Tam nương, Nguyệt kỵ, Dương công, Thọ tử) · số nhỏ là ngày âm lịch</p>
  </div>`;
}

$("#ngay-lich-thang").addEventListener("click", async (e) => {
  const nut = e.target.closest("button");
  if (!nut) return;
  if (nut.dataset.buoc) {
    const t = new Date(lichDangXem.nam, lichDangXem.thang - 1 + Number(nut.dataset.buoc), 1);
    try { await veLichThang(t.getMonth() + 1, t.getFullYear(), $("#n-ngay").value); }
    catch (err) { baoLoi($("#ngay-lich-thang"), err); }
  } else if (nut.dataset.ngay) {
    datNgay($("#n-ngay"), nut.dataset.ngay);
    $("#form-ngay").requestSubmit();
  }
});

$("#form-ngay").addEventListener("submit", async (e) => {
  e.preventDefault();
  const [nam, thang, ngay] = $("#n-ngay").value.split("-").map(Number);
  try {
    const [chiTiet] = await Promise.all([api("/api/ngay", { ngay, thang, nam }),
      veLichThang(thang, nam, $("#n-ngay").value)]);
    veNgay(chiTiet);
  } catch (err) { baoLoi($("#ngay-ket-qua"), err); }
});


/* ---------------------------- chọn ngày ---------------------------- */
function veChonNgay(d) {
  const chan = d.ngay_bi_chan;
  const dong = (x, i) => {
    const khoan = x.khoan_cong_tru.map((k) =>
      `<span class="khoan ${k.diem > 0 ? "cong" : "tru"}">${k.diem > 0 ? "+" : ""}${k.diem} ${esc(k.muc)}</span>`).join(" ");
    return `<tr>
      <td data-nhan="Hạng"><b>${i + 1}</b></td>
      <td data-nhan="Ngày"><b>${esc(x.duong_lich)}</b><br>
        <span class="cung-chi">${esc(x.thu)} · ${esc(x.am_lich)} ÂL</span></td>
      <td data-nhan="Can chi">${esc(x.ngay_can_chi)}<br>
        <span class="cung-chi">trực ${esc(x.truc)} · ${esc(x.nhi_thap_bat_tu)} · ${esc(x.loai_ngay)}</span></td>
      <td data-nhan="Điểm"><b style="font-size:17px">${x.diem_ca_nhan}</b>
        <span class="cung-chi">/100 · nền ${x.diem_chung}</span>
        <div class="thanh-diem"><i style="width:${x.diem_ca_nhan}%;background:${x.diem_ca_nhan >= 70 ? "var(--cat)" : "var(--vang)"}"></i></div></td>
      <td data-nhan="Vì sao">${khoan || '<span class="cung-chi">không có khoản cộng trừ riêng</span>'}
        ${x.ngay_kieng.length ? `<br><span class="loi">phạm ${esc(ds(x.ngay_kieng))}</span>` : ""}</td>
      <td data-nhan="Giờ tốt">${x.gio_tot.map((g) => esc(g.chi)).join(", ") || "—"}</td>
    </tr>`;
  };
  $("#cn-ket-qua").innerHTML = `
  <div class="the-tom-tat">
    ${[["Tuổi", d.tuoi_can_chi], ["Việc", d.viec], ["Khoảng", `${d.tu_ngay} – ${d.den_ngay}`],
       ["Tổng số ngày", d.tong_so_ngay], ["Loại vì xung tuổi", d.so_chan_xung_tuoi],
       ["Loại vì ngày kiêng", d.so_chan_ngay_kieng]]
      .map(([k, v]) => `<div class="o-tom-tat"><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join("")}
  </div>
  ${d.ghi_chu_viec ? `<p class="goi-y">${esc(d.ghi_chu_viec)}</p>` : ""}
  ${d.canh_bao_du_lieu ? `<div class="the"><p class="loi">${esc(d.canh_bao_du_lieu)}</p></div>` : ""}

  <div class="the">
    <h3>${d.ngay_tot.length} ngày tốt nhất</h3>
    ${d.ngay_tot.length ? `<table class="xep-chong">
      <thead><tr><th>Hạng</th><th>Ngày</th><th>Can chi</th><th>Điểm</th><th>Vì sao</th><th>Giờ tốt</th></tr></thead>
      <tbody>${d.ngay_tot.map(dong).join("")}</tbody></table>`
      : "<p class=\"goi-y\">Không có ngày nào dùng được trong khoảng này. Thử nới rộng khoảng ngày.</p>"}
  </div>

  <div class="the">
    <h3>Ngày bị loại (${chan.length})</h3>
    ${chan.length ? `<table class="xep-chong">
      <thead><tr><th>Ngày</th><th>Can chi</th><th>Nhóm</th><th>Lý do</th></tr></thead>
      <tbody>${chan.map((c) => `<tr>
        <td data-nhan="Ngày">${esc(c.duong_lich)}<br><span class="cung-chi">${esc(c.thu)}</span></td>
        <td data-nhan="Can chi">${esc(c.ngay_can_chi)}</td>
        <td data-nhan="Nhóm">${c.nhom.map((n) => `<span class="khoan tru">${esc(n)}</span>`).join(" ")}</td>
        <td data-nhan="Lý do">${esc(ds(c.ly_do))}</td></tr>`).join("")}</tbody></table>`
      : "<p class=\"goi-y\">Không có ngày nào bị loại trong khoảng này.</p>"}
    <p class="goi-y">Hai nhóm bị loại thẳng, không chấm điểm dù trực và tú có đẹp tới đâu:
      ngày lục xung hoặc thiên khắc địa xung với tuổi;
      ${d.ngay_kieng_cua_viec.length
        ? `và ngày ${esc(ds(d.ngay_kieng_cua_viec))} — những ngày lệ cũ không làm việc này.`
        : "việc này không đặt ngày kiêng nào làm điều kiện loại."}</p>
  </div>`;
}

$("#form-cn").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    veChonNgay(await api("/api/chonngay", {
      ngay_sinh: $("#cn-sinh").value, gioi_tinh: $("#cn-gt").value,
      viec: $("#cn-viec").value, tu_ngay: $("#cn-tu").value,
      den_ngay: $("#cn-den").value, so_luong: 12,
    }));
  } catch (err) { baoLoi($("#cn-ket-qua"), err); }
});

/* ------------------------------ khởi tạo ------------------------------ */
$("#ls-du-sao").addEventListener("change", (e) => $("#dia-ban").classList.toggle("du", e.target.checked));

(function khoiTao() {
  $("#ls-nam-xem").value = new Date().getFullYear();
  // Lấy ngày theo giờ máy người dùng; toISOString() là giờ UTC, trước 7h sáng
  // ở Việt Nam nó còn là ngày hôm qua.
  const h = new Date(), iso = isoCua(h);
  datNgay($("#n-ngay"), iso);
  datNgay($("#ls-ngay"), "1990-09-20");
  $("#h-xem").value = h.getFullYear();
  HUONG_8.forEach((x) => $("#pt-huong").insertAdjacentHTML("beforeend", `<option>${x}</option>`));
  const sau = isoCua(new Date(h.getFullYear(), h.getMonth(), h.getDate() + 60));
  datNgay($("#cn-tu"), iso);
  datNgay($("#cn-den"), sau);
  datNgay($("#ht-sinh-a"), "1990-09-20");
  datNgay($("#ht-sinh-b"), "1992-05-15");
  api("/api/viec", {}).then((d) => d.viec.forEach((v) => {
    const canh = v.so_tu_khop === 0 ? " (chỉ xét theo Trực)" : "";
    $("#cn-viec").insertAdjacentHTML("beforeend",
      `<option value="${v.ma}">${v.ten}${canh}</option>`);
  })).catch(() => {});
  $("#form-ngay").dispatchEvent(new Event("submit"));
})();
