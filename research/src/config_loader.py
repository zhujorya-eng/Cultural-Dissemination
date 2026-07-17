"""配置加载工具。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"


def load_yaml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_search_queries() -> list[str]:
    """从关键词表生成检索查询列表。"""
    kw = load_yaml("keywords.yaml")
    queries: list[str] = list(kw.get("search_queries", {}).get("curated", []))

    # 英文主题 + 地名组合
    geo_en = kw.get("geo_terms", {}).get("english", [])[:4]
    theme_en: list[str] = []
    for group in kw.get("theme_terms", {}).values():
        theme_en.extend(group.get("english", [])[:2])

    for geo in geo_en:
        for theme in theme_en[:6]:
            combo = f"{geo} {theme}"
            if combo not in queries:
                queries.append(combo)

    # 标签检索
    for tag in kw.get("hashtags", {}).get("primary", [])[:6]:
        q = tag if tag.startswith("#") else f"#{tag}"
        if q not in queries:
            queries.append(q)

    return queries
