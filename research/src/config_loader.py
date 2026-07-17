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


def _collect_english_terms(kw: dict[str, Any], *paths: str) -> list[str]:
    """从嵌套 geo_terms / theme_terms 提取 english 列表。"""
    terms: list[str] = []
    node: Any = kw
    for key in paths:
        node = node.get(key, {}) if isinstance(node, dict) else {}
    if isinstance(node, dict):
        for sub in node.values():
            if isinstance(sub, dict) and "english" in sub:
                terms.extend(sub["english"])
            elif isinstance(sub, list):
                terms.extend(sub)
    elif isinstance(node, list):
        terms.extend(node)
    return terms


def build_search_queries(limit: int | None = None) -> list[str]:
    """从关键词表 v2 生成去重检索查询列表。"""
    kw = load_yaml("keywords.yaml")
    seen: set[str] = set()
    queries: list[str] = []

    def add(q: str) -> None:
        q = q.strip()
        if q and q.lower() not in seen:
            seen.add(q.lower())
            queries.append(q)

    # 1. 精选查询
    sq = kw.get("search_queries", {})
    for group in sq.values():
        if isinstance(group, list):
            for q in group:
                add(str(q))

    # 2. 地名 × 主题交叉
    cross = kw.get("cross_combinations", {})
    for city in cross.get("cities_for_cross", []):
        for theme in cross.get("themes_for_cross", []):
            add(f"{city} {theme}")

    # 3. 省级地名 + 代表性主题
    province = _collect_english_terms(kw, "geo_terms", "province")
    landmarks = _collect_english_terms(kw, "geo_terms", "landmarks")[:8]
    opera = kw.get("theme_terms", {}).get("heritage_opera", {}).get("english", [])[:4]
    craft = kw.get("theme_terms", {}).get("heritage_craft", {}).get("english", [])[:3]
    cuisine = kw.get("theme_terms", {}).get("cuisine", {}).get("english", [])[:3]

    for p in province[:3]:
        for t in opera + craft + cuisine:
            add(f"{p} {t}")

    for lm in landmarks:
        add(f"{lm} tour")
        add(f"{lm} documentary")

    # 4. 主题标签
    for tag in kw.get("hashtags", {}).get("primary", []):
        add(tag if str(tag).startswith("#") else f"#{tag}")

    if limit:
        return queries[:limit]
    return queries


def query_stats() -> dict[str, int]:
    """返回关键词表统计。"""
    kw = load_yaml("keywords.yaml")
    all_q = build_search_queries()
    return {
        "total_queries": len(all_q),
        "curated": len(kw.get("search_queries", {}).get("curated", [])),
        "hashtags_primary": len(kw.get("hashtags", {}).get("primary", [])),
        "hashtags_secondary": len(kw.get("hashtags", {}).get("secondary", [])),
    }
