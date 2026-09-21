"use strict";

const $ = (s, g = document) => g.querySelector(s);
const $$ = (s, g = document) => [...g.querySelectorAll(s)];
const esc = (v) => String(v ?? "").replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const ds = (v) => Array.isArray(v) ? v.join(", ") : (v ?? "");

const HUONG_8 = ["Bắc", "Đông Bắc", "Đông", "Đông Nam", "Nam", "Tây Nam", "Tây", "Tây Bắc"];
const DAC_TINH_TAT = { "Miếu": "M", "Vượng": "V", "Đắc": "Đ", "Bình": "B", "Hãm": "H" };

async function api(duongDan, tham) {
  const u = new URL(duongDan, location.href);
  Object.entries(tham).forEach(([k, v]) => v !== "" && v != null && u.searchParams.set(k, v));
  const res = await fetch(u);
  const data = await res.json();
  if (!res.ok) throw new Error(data.loi || "Không lấy được dữ liệu");
  return data;
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
function lopSao(s) {
  if (s.nhom === "Chính tinh") return "chinh-tinh";
  if (s.tinh_chat === "cát") return "cat";
  if (s.tinh_chat === "hung") return "hung";
  return "trung";
}

function veCung(c, laMenh) {
  const sao = c.sao.map((s) => {
    const dt = s.dac_tinh ? `<span class="dt" title="${esc(s.dac_tinh)} địa">${DAC_TINH_TAT[s.dac_tinh] || ""}</span>` : "";
    return `<button class="sao ${lopSao(s)}" data-sao="${esc(s.ten)}">${esc(s.ten)}${dt}</button>`;
  }).join("");
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
      : "<p class=\"goi-y\">Lá số này không khớp cách cục nào trong bộ 20 cách đang có.</p>");

  $("#ls-ket-qua").hidden = false;
  $("#ls-goi-y").hidden = true;
  $("#ls-luan-giai").hidden = true;
  $("#ls-luan-giai").innerHTML = "";
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

  const tk = d.thong_ke;
  $("#ls-luan-giai").innerHTML = `
    <div class="lg-phan"><h3>Tổng quan</h3><div class="luoi">${theTongQuan}</div></div>
    <div class="lg-phan the"><h3>Tứ Hóa</h3><ul>${tuHoa}</ul></div>
    <div class="lg-phan the"><h3>Đại hạn</h3>${hienTai}${bangDaiHan}<p class="goi-y">${esc(dh.ghi_chu)}</p></div>
    <div class="lg-phan"><h3>12 cung theo thứ tự đọc</h3>
      <p class="goi-y">Cung mạnh nhất: <b>${esc(tk.cung_manh_nhat)}</b> · yếu nhất: <b>${esc(tk.cung_yeu_nhat)}</b> ·
        ${tk.so_cung_vo_chinh_dieu} cung vô chính diệu · điểm trung bình ${tk.diem_trung_binh}.</p>
      ${d.cac_cung.map((c, i) => veCungLuan(c, i === 0)).join("")}
    </div>
    <div class="lg-phan the"><h3>Lưu ý</h3><ul class="lg-luu-y">${d.luu_y.map((l) => `<li>${esc(l)}</li>`).join("")}</ul></div>`;
  $("#ls-luan-giai").hidden = false;
}

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
      nam_sinh: $("#h-sinh").value, nam_xem: $("#h-xem").value, gioi_tinh: $("#h-gt").value,
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
      nam_sinh: $("#pt-sinh").value, gioi_tinh: $("#pt-gt").value, huong: $("#pt-huong").value,
    }));
  } catch (err) { baoLoi($("#pt-ket-qua"), err); }
});

/* ----------------------------- xem ngày ----------------------------- */
function veNgay(d) {
  const mau = d.diem_tong_hop >= 70 ? "var(--cat)" : d.diem_tong_hop >= 45 ? "var(--vang)" : "var(--hung)";
  const gio = (ds_) => ds_.map((g) => `<li><b>${esc(g.can_chi)}</b> — ${esc(g.khung_gio)}</li>`).join("");
  $("#ngay-ket-qua").innerHTML = `
  <div class="the-tom-tat">
    ${[["Dương lịch", d.duong_lich], ["Âm lịch", d.am_lich], ["Ngày", d.ngay_can_chi],
       ["Tiết khí", d.tiet_khi], ["Loại ngày", d.loai_ngay], ["Thần trực nhật", d.than_truc_nhat]]
      .map(([k, v]) => `<div class="o-tom-tat"><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join("")}
  </div>
  <div class="the">
    <h3>Điểm tổng hợp ${d.diem_tong_hop}/100</h3>
    <div class="thanh-diem"><i style="width:${d.diem_tong_hop}%;background:${mau}"></i></div>
    <p class="goi-y">Điểm này chỉ xét trực, nhị thập bát tú, hoàng đạo và ngày kiêng chung —
      chưa xét xung khắc với tuổi người dùng.</p>
    ${d.ngay_kieng.length ? `<p class="loi">Ngày này phạm: ${esc(ds(d.ngay_kieng))}</p>` : ""}
  </div>
  <div class="luoi">
    <div class="the">
      <h3>Trực ${esc(d.truc)} <span class="nhan-tt ${d.truc_y_nghia.tinh_chat === "tốt" ? "tot" : d.truc_y_nghia.tinh_chat === "xấu" ? "xau" : "vua"}">${esc(d.truc_y_nghia.tinh_chat)}</span></h3>
      <p>${esc(d.truc_y_nghia.tom_tat)}</p>
      <p><b>Nên:</b> ${esc(ds(d.truc_y_nghia.nen))}</p>
      <p><b>Kỵ:</b> ${esc(ds(d.truc_y_nghia.ky))}</p>
    </div>
    <div class="the">
      <h3>Sao ${esc(d.tu_y_nghia.ten_day_du || d.nhi_thap_bat_tu)} <span class="nhan-tt ${d.tu_y_nghia.tinh_chat === "tốt" ? "tot" : d.tu_y_nghia.tinh_chat === "xấu" ? "xau" : "vua"}">${esc(d.tu_y_nghia.tinh_chat)}</span></h3>
      <p>${esc(d.tu_y_nghia.mo_ta)}</p>
      <p><b>Nên:</b> ${esc(ds(d.tu_y_nghia.nen))}</p>
      <p><b>Kỵ:</b> ${esc(ds(d.tu_y_nghia.ky))}</p>
    </div>
    <div class="the"><h3>Giờ hoàng đạo</h3><ul>${gio(d.gio_hoang_dao)}</ul></div>
    <div class="the"><h3>Giờ hắc đạo</h3><ul>${gio(d.gio_hac_dao)}</ul></div>
  </div>`;
}

$("#form-ngay").addEventListener("submit", async (e) => {
  e.preventDefault();
  const [nam, thang, ngay] = $("#n-ngay").value.split("-").map(Number);
  try { veNgay(await api("/api/ngay", { ngay, thang, nam })); }
  catch (err) { baoLoi($("#ngay-ket-qua"), err); }
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
      nam_sinh: $("#cn-sinh").value, gioi_tinh: $("#cn-gt").value,
      viec: $("#cn-viec").value, tu_ngay: $("#cn-tu").value,
      den_ngay: $("#cn-den").value, so_luong: 12,
    }));
  } catch (err) { baoLoi($("#cn-ket-qua"), err); }
});

/* ------------------------------ khởi tạo ------------------------------ */
(function khoiTao() {
  $("#ls-nam-xem").value = new Date().getFullYear();
  const h = new Date(), iso = h.toISOString().slice(0, 10);
  $("#n-ngay").value = iso;
  $("#ls-ngay").value = "1990-09-20";
  $("#h-xem").value = h.getFullYear();
  HUONG_8.forEach((x) => $("#pt-huong").insertAdjacentHTML("beforeend", `<option>${x}</option>`));
  const sau = new Date(h.getTime() + 60 * 864e5).toISOString().slice(0, 10);
  $("#cn-tu").value = iso;
  $("#cn-den").value = sau;
  api("/api/viec", {}).then((d) => d.viec.forEach((v) => {
    const canh = v.so_tu_khop === 0 ? " (chỉ xét theo Trực)" : "";
    $("#cn-viec").insertAdjacentHTML("beforeend",
      `<option value="${v.ma}">${v.ten}${canh}</option>`);
  })).catch(() => {});
  $("#form-ngay").dispatchEvent(new Event("submit"));
})();
