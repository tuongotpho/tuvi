# -*- coding: utf-8 -*-
"""Lồng tiếng bằng edge-tts (bộ đọc của Microsoft Edge).

Dùng giọng tiếng Việt có sẵn của Microsoft, không cần khóa API. Mỗi cảnh trong
kịch bản được đọc thành một tệp mp3, và **độ dài thật của tệp âm thanh quyết
định độ dài cảnh** — chính xác hơn hẳn cách ước lượng theo số chữ.

    pip install edge-tts

Nếu máy chạy sau proxy có TLS re-terminate (proxy doanh nghiệp, môi trường CI),
edge-tts sẽ báo CERTIFICATE_VERIFY_FAILED vì nó ghim cứng bộ CA của certifi.
Đặt biến môi trường ``TUVI_CA_BUNDLE`` (hoặc ``SSL_CERT_FILE``) trỏ tới tệp CA
của proxy, hàm :func:`nap_ca_proxy` sẽ nạp thêm CA đó vào — vẫn giữ nguyên việc
xác thực chứng chỉ, chỉ thêm một CA được tin cậy.
"""
from __future__ import annotations

import asyncio
import os
import ssl
import subprocess
import sys
from pathlib import Path

# Giọng tiếng Việt của Microsoft Edge.
GIONG_NU = "vi-VN-HoaiMyNeural"
GIONG_NAM = "vi-VN-NamMinhNeural"
GIONG_MAC_DINH = GIONG_NU
SO_LAN_THU = 4          # số lần gọi edge-tts cho một câu trước khi bỏ cuộc
GIAY_CHO_THU_LAI = 4.0  # nghỉ giữa hai lần thử, nhân dần theo số lần: 4, 8, 12 giây
GIAY_NGHI_GIUA_CAU = 1.0  # nghỉ giữa hai câu liên tiếp để khỏi bị dịch vụ coi là gọi dồn dập


class KhongLongTiengDuoc(RuntimeError):
    """Không tổng hợp được giọng đọc — thiếu gói, hoặc mạng bị chặn."""


def nap_ca_proxy() -> None:
    """Nạp thêm CA của proxy vào context TLS mà edge-tts dùng, nếu có khai báo.

    edge-tts tạo sẵn ``_SSL_CTX`` từ ``certifi.where()`` nên biến môi trường
    SSL_CERT_FILE không có tác dụng; phải nạp thẳng vào context đó.
    """
    ca = next((p for p in (os.environ.get("TUVI_CA_BUNDLE"),
                           os.environ.get("SSL_CERT_FILE"),
                           os.environ.get("REQUESTS_CA_BUNDLE"))
               if p and Path(p).exists()), None)
    if not ca:
        return
    try:
        import certifi
        import edge_tts.communicate as _c
        import edge_tts.voices as _v
    except ImportError:
        return
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.load_verify_locations(ca)
    for mo_dun in (_c, _v):
        if hasattr(mo_dun, "_SSL_CTX"):
            mo_dun._SSL_CTX = ctx


def co_san() -> bool:
    """edge-tts đã cài chưa."""
    try:
        import edge_tts  # noqa: F401
        return True
    except ImportError:
        return False


async def _doc_mot_canh(loi_thoai: str, ra: Path, giong: str,
                        toc_do: str, cao_do: str) -> float:
    """Đọc một đoạn thành mp3, trả về độ dài thật tính bằng giây."""
    import edge_tts

    noi = edge_tts.Communicate(loi_thoai, giong, rate=toc_do, pitch=cao_do)
    cuoi = 0
    with ra.open("wb") as fh:
        async for goi in noi.stream():
            if goi["type"] == "audio":
                fh.write(goi["data"])
            elif goi["type"] == "WordBoundary":
                # offset và duration tính bằng đơn vị 100 nano giây.
                cuoi = max(cuoi, goi["offset"] + goi["duration"])
    if not ra.exists() or ra.stat().st_size == 0:
        raise KhongLongTiengDuoc(f"Không nhận được âm thanh cho: {loi_thoai[:40]}…")
    return cuoi / 1e7 if cuoi else do_dai_am_thanh(ra)


def doc_kich_ban(canh: list[dict], thu_muc: Path,
                 giong: str = GIONG_MAC_DINH, toc_do: str = "+0%",
                 cao_do: str = "+0Hz") -> list[tuple[Path, float]]:
    """Đọc toàn bộ lời thoại, trả về [(tệp mp3, độ dài giây)] theo thứ tự cảnh."""
    if not co_san():
        raise KhongLongTiengDuoc(
            "Chưa cài edge-tts. Chạy: pip install edge-tts")
    nap_ca_proxy()
    thu_muc.mkdir(parents=True, exist_ok=True)

    async def doc_co_thu_lai(loi_thoai: str, tep: Path) -> float:
        # Dịch vụ của Microsoft thỉnh thoảng trả về "NoAudioReceived" cho một
        # câu hoàn toàn bình thường rồi lần sau lại đọc được. Thử lại vài lần
        # trước khi chịu thua, để một cú chập chờn không làm cả video câm.
        loi_cuoi: Exception | None = None
        for lan in range(SO_LAN_THU):
            if lan:
                await asyncio.sleep(GIAY_CHO_THU_LAI * lan)
            try:
                return await _doc_mot_canh(loi_thoai, tep, giong, toc_do, cao_do)
            except Exception as e:  # noqa: BLE001 — mọi lỗi mạng/dịch vụ đều đáng thử lại
                loi_cuoi = e
                print(f"  [lồng tiếng] lần {lan + 1}/{SO_LAN_THU} hỏng "
                      f"({type(e).__name__}), thử lại: {loi_thoai[:40]}…",
                      file=sys.stderr)
        assert loi_cuoi is not None
        raise loi_cuoi

    async def chay() -> list[tuple[Path, float]]:
        ra = []
        for i, c in enumerate(canh, 1):
            if i > 1:
                await asyncio.sleep(GIAY_NGHI_GIUA_CAU)
            tep = thu_muc / f"canh{i:02d}.mp3"
            ra.append((tep, await doc_co_thu_lai(c["loi_thoai"], tep)))
        return ra

    try:
        return asyncio.run(chay())
    except KhongLongTiengDuoc:
        raise
    except Exception as e:  # lỗi mạng, chặn egress, dịch vụ đổi giao thức...
        raise KhongLongTiengDuoc(
            f"Không gọi được dịch vụ đọc của Microsoft ({type(e).__name__}: "
            f"{str(e)[:160]}). Kiểm tra mạng ra speech.platform.bing.com, "
            f"hoặc đặt TUVI_CA_BUNDLE nếu máy chạy sau proxy TLS.") from e


def do_dai_am_thanh(tep: Path, ffmpeg: str | None = None) -> float:
    """Độ dài tệp âm thanh tính bằng giây, đọc từ đầu ra của ffmpeg."""
    from .lam_video import _ffmpeg  # nhập muộn để tránh phụ thuộc vòng

    ff = ffmpeg or _ffmpeg()
    if not ff:
        raise KhongLongTiengDuoc("Không có ffmpeg để đo độ dài âm thanh")
    kq = subprocess.run([ff, "-i", str(tep)], capture_output=True, text=True)
    for dong in kq.stderr.splitlines():
        if "Duration:" in dong:
            gio = dong.split("Duration:")[1].split(",")[0].strip()
            h, m, s = gio.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise KhongLongTiengDuoc(f"Không đọc được độ dài của {tep}")


def ghep_thanh_mot_dai(doan: list[tuple[Path, float]], giay_canh: list[float],
                       ra: Path, ffmpeg: str) -> Path:
    """Ghép các đoạn thành một dải âm thanh khớp đúng mốc từng cảnh.

    Mỗi đoạn được đệm im lặng cho đủ độ dài cảnh, nên tiếng của cảnh nào bắt đầu
    đúng lúc cảnh đó hiện lên.
    """
    tam = ra.parent / "_doan"
    tam.mkdir(parents=True, exist_ok=True)
    danh_sach = []
    for i, ((tep, _), giay) in enumerate(zip(doan, giay_canh), 1):
        wav = tam / f"seg{i:02d}.wav"
        subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error", "-i", str(tep),
             "-af", f"apad=whole_dur={giay:.3f},aresample=44100",
             "-t", f"{giay:.3f}", "-ac", "2", "-c:a", "pcm_s16le", str(wav)],
            check=True, capture_output=True)
        danh_sach.append(wav)
    bang = tam / "danh_sach.txt"
    bang.write_text("".join(f"file '{w.name}'\n" for w in danh_sach),
                    encoding="utf-8")
    subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(bang), "-c:a", "pcm_s16le", str(ra)],
        check=True, capture_output=True, cwd=str(tam))
    return ra
