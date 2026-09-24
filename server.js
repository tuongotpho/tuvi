// Pure Node.js Web Server for Tuvi application
// Uses WebAssembly Pyodide for core astrology calculations with zero system python dependencies
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const STATIC_DIR = path.resolve(__dirname, "web", "static");
const PORT = parseInt(process.env.PORT || "3000", 10);
const HOST = "0.0.0.0";

const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml; charset=utf-8",
  ".png": "image/png",
  ".ico": "image/x-icon",
  ".txt": "text/plain; charset=utf-8",
};

// AI rate-limiting & cache
const AI_GIAY_MOI_IP = 15;
const AI_DONG_THOI = 2;
let aiActiveRequests = 0;
const aiLastCallByIp = new Map();
const aiMemoryCache = new Map();

// Initialize Pyodide
let pyodideInstance = null;
let handleApiFn = null;
let getAiPromptFn = null;

const initPyodidePromise = (async () => {
  console.log("Initializing Pyodide WebAssembly runtime...");
  const { loadPyodide } = await import("pyodide");
  const py = await loadPyodide();
  
  py.FS.mkdir("/workspace");
  py.FS.mount(py.FS.filesystems.NODEFS, { root: __dirname }, "/workspace");

  py.runPython(`
import sys, json
sys.path.insert(0, '/workspace')
from web import server
from tuvi import ai_luan_giai
from tuvi.kiem_tra import LoiDauVao

def handle_api(path, query_json):
    q = json.loads(query_json)
    if path == '/api/laso.svg':
        try:
            svg, ten = server.api_laso_svg(q)
            return json.dumps({'status': 200, 'type': 'svg', 'svg': svg, 'filename': ten})
        except LoiDauVao as e:
            return json.dumps({'status': 400, 'type': 'json', 'data': {'loi': str(e)}})
        except Exception:
            return json.dumps({'status': 400, 'type': 'json', 'data': {'loi': 'Tham số không hợp lệ.'}})
    
    if path in server.TUYEN:
        try:
            res = server.TUYEN[path](q)
            return json.dumps({'status': 200, 'type': 'json', 'data': res})
        except LoiDauVao as e:
            return json.dumps({'status': 400, 'type': 'json', 'data': {'loi': str(e)}})
        except Exception as e:
            return json.dumps({'status': 400, 'type': 'json', 'data': {'loi': 'Tham số không hợp lệ — kiểm tra lại ngày, giờ, năm sinh và giới tính.'}})
    return json.dumps({'status': 404, 'type': 'json', 'data': {'loi': 'Không tìm thấy API'}})

def get_ai_prompt(query_json):
    q = json.loads(query_json)
    try:
        ls = server._la_so_tu_query(q)
        nam_xem = server.nam_hop_le(q.get('nam_xem') or server.hom_nay_vn().year, 'Năm xem')
        prompt = ai_luan_giai.dung_prompt(ls, nam_xem)
        return json.dumps({'status': 200, 'prompt': prompt})
    except LoiDauVao as e:
        return json.dumps({'status': 400, 'loi': str(e)})
    except Exception:
        return json.dumps({'status': 400, 'loi': 'Tham số không hợp lệ — kiểm tra lại ngày, giờ, năm sinh và giới tính.'})
  `);

  handleApiFn = py.globals.get("handle_api");
  getAiPromptFn = py.globals.get("get_ai_prompt");
  pyodideInstance = py;
  console.log("Pyodide ready!");
})();
// Nạp Pyodide hỏng thì ghi lại lỗi chứ không để "unhandled rejection" làm sập
// cả tiến trình Node — sập là trình duyệt chỉ thấy "Failed to fetch".
let pyodideLoi = null;
initPyodidePromise.catch((err) => {
  pyodideLoi = err;
  console.error("Pyodide init failed:", err);
});

function traJson(res, status, obj) {
  if (res.headersSent) return res.end();
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
  });
  return res.end(JSON.stringify(obj));
}

async function handleAiLuanGiai(query, clientIp, res) {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    res.writeHead(503, {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    });
    return res.end(JSON.stringify({ loi: "Máy chủ chưa cấu hình GEMINI_API_KEY nên chưa bật được luận giải AI." }));
  }

  // Check rate limit per IP
  const now = Date.now();
  const lastTime = aiLastCallByIp.get(clientIp) || 0;
  if (now - lastTime < AI_GIAY_MOI_IP * 1000) {
    res.writeHead(429, {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    });
    return res.end(JSON.stringify({ loi: `Mỗi ${AI_GIAY_MOI_IP} giây chỉ gọi AI được một lần, đợi chút rồi thử lại.` }));
  }

  if (aiActiveRequests >= AI_DONG_THOI) {
    res.writeHead(429, {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    });
    return res.end(JSON.stringify({ loi: "Đang có người khác dùng AI, thử lại sau vài giây." }));
  }

  aiLastCallByIp.set(clientIp, now);
  if (aiLastCallByIp.size > 5000) aiLastCallByIp.clear();

  // Generate prompt
  const promptRes = JSON.parse(getAiPromptFn(JSON.stringify(query)));
  if (promptRes.status !== 200) {
    res.writeHead(promptRes.status, {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    });
    return res.end(JSON.stringify({ loi: promptRes.loi }));
  }

  const prompt = promptRes.prompt;
  const model = process.env.GEMINI_MODEL || "gemini-3.6-flash";
  const hashKey = crypto.createHash("sha256").update(`${model}\n${prompt}`).digest("hex").slice(0, 24);

  if (aiMemoryCache.has(hashKey)) {
    res.writeHead(200, {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    });
    return res.end(JSON.stringify({
      model,
      van_ban: aiMemoryCache.get(hashKey),
      tu_cache: true,
      so_ky_tu_prompt: prompt.length,
    }));
  }

  aiActiveRequests++;
  try {
    const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;
    const payload = {
      contents: [{ role: "user", parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.7, maxOutputTokens: 4096 },
    };

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 90000);

    const apiRes = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "x-goog-api-key": apiKey,
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    const data = await apiRes.json();
    if (!apiRes.ok) {
      const errMsg = data?.error?.message || `HTTP ${apiRes.status}`;
      res.writeHead(502, {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      });
      return res.end(JSON.stringify({ loi: `Gemini từ chối: ${errMsg}` }));
    }

    const candidate = data.candidates?.[0];
    if (candidate?.finishReason === "SAFETY") {
      res.writeHead(502, {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      });
      return res.end(JSON.stringify({ loi: "Gemini chặn nội dung vì bộ lọc an toàn; thử lại hoặc đổi năm xem." }));
    }

    const van_ban = candidate?.content?.parts?.map((p) => p.text || "").join("").trim() || "";
    if (!van_ban) {
      res.writeHead(502, {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      });
      return res.end(JSON.stringify({ loi: "Gemini trả về văn bản rỗng." }));
    }

    aiMemoryCache.set(hashKey, van_ban);

    res.writeHead(200, {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    });
    return res.end(JSON.stringify({
      model,
      van_ban,
      tu_cache: false,
      so_ky_tu_prompt: prompt.length,
    }));
  } catch (err) {
    res.writeHead(502, {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    });
    return res.end(JSON.stringify({ loi: `Không nối được tới Gemini: ${err.message}` }));
  } finally {
    aiActiveRequests--;
  }
}

const server = http.createServer(async (req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  const pathname = parsedUrl.pathname;

  // Handle API routes
  if (pathname.startsWith("/api/")) {
    try {
      await initPyodidePromise;
    } catch {
      return traJson(res, 503, { loi: "Máy chủ chưa nạp xong bộ tính toán, thử lại sau ít phút." });
    }

    const query = Object.fromEntries(parsedUrl.searchParams.entries());

    if (pathname === "/api/ai-luangiai") {
      const clientIp = (req.headers["x-forwarded-for"] || req.socket.remoteAddress || "127.0.0.1").toString().split(",")[0].trim();
      try {
        return await handleAiLuanGiai(query, clientIp, res);
      } catch (err) {
        console.error("AI error:", err);
        return traJson(res, 500, { loi: "Lỗi máy chủ. Thử lại sau." });
      }
    }

    try {
      const rawRes = handleApiFn(pathname, JSON.stringify(query));
      const parsed = JSON.parse(rawRes);

      if (parsed.type === "svg") {
        const headers = {
          "Content-Type": "image/svg+xml; charset=utf-8",
          "Cache-Control": "no-store",
          "X-Content-Type-Options": "nosniff",
          "Referrer-Policy": "no-referrer",
        };
        if (query.tai_ve === "1") {
          headers["Content-Disposition"] = `attachment; filename="${parsed.filename}"`;
        }
        res.writeHead(parsed.status, headers);
        return res.end(parsed.svg);
      }

      res.writeHead(parsed.status, {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
      });
      return res.end(JSON.stringify(parsed.data));
    } catch (err) {
      console.error("API error:", err);
      res.writeHead(500, {
        "Content-Type": "application/json; charset=utf-8",
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
      });
      return res.end(JSON.stringify({ loi: "Lỗi máy chủ. Thử lại sau." }));
    }
  }

  // Serve static files from web/static
  // So "/" TRƯỚC khi normalize: trên Windows path.normalize("/") ra "\\" nên
  // trang chủ từng bị 404 khi chạy thử trên máy.
  const safePath = path.normalize(pathname).replace(/^(\.\.[/\\])+/, "");
  const targetFile = pathname === "/" ? "index.html" : safePath.replace(/^[/\\]/, "");
  const filePath = path.join(STATIC_DIR, targetFile);

  // Prevent directory traversal
  if (!filePath.startsWith(STATIC_DIR)) {
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    return res.end("Not Found");
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
      return res.end("Not Found");
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || "application/octet-stream";

    res.writeHead(200, {
      "Content-Type": contentType,
      "Cache-Control": "no-cache",
      "Referrer-Policy": "no-referrer",
      "X-Content-Type-Options": "nosniff",
    });

    const stream = fs.createReadStream(filePath);
    stream.pipe(res);
  });
});

server.listen(PORT, HOST, () => {
  console.log(`Tuvi web server running on http://${HOST}:${PORT}`);
});
