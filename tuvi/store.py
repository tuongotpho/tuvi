# -*- coding: utf-8 -*-
"""Nạp dữ liệu JSON trong thư mục ``data/`` và cache lại."""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from .duong_dan import thu_muc_tai_nguyen

DATA_DIR = thu_muc_tai_nguyen() / "data"


@lru_cache(maxsize=None)
def load(name: str) -> Any:
    """Nạp một tệp dữ liệu, ví dụ ``load("lich/truc")``."""
    path = DATA_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy bộ dữ liệu: {path}")
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def all_datasets() -> list[str]:
    """Danh sách tên mọi bộ dữ liệu hiện có."""
    return sorted(
        str(p.relative_to(DATA_DIR)).removesuffix(".json")
        for p in DATA_DIR.rglob("*.json")
    )


def index(name: str, key: str) -> dict[str, dict]:
    """Chuyển một mảng bản ghi thành dict tra cứu theo khoá."""
    return {str(row[key]): row for row in load(name)}
