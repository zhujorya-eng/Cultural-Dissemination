"""采集与处理主流水线。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .coders.auto_coder import auto_code_record
from .collectors import InstagramCollector, TikTokCollector, YouTubeCollector
from .collectors.demo_data import DemoCollector
from .collectors.youtube_api import YouTubeApiCollector
from .config_loader import build_search_queries, load_yaml
from .models import CultureWorkRecord
from .processors.deduplicator import deduplicate_records
from .processors.filter import apply_inclusion_exclusion
from .processors.language import apply_language_filter

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def _collector_for_platform(platform: str, cfg: dict[str, Any], *, demo: bool = False):
    if demo:
        return DemoCollector(platform)

    pcfg = cfg.get("platforms", {}).get(platform, {})
    kwargs = {
        "max_results": int(pcfg.get("max_results_per_query", 15)),
        "fetch_comments": bool(pcfg.get("fetch_comments", True)),
        "max_comments": int(pcfg.get("max_comments", 50)),
    }
    if platform == "youtube":
        import os
        if os.environ.get("YOUTUBE_API_KEY"):
            return YouTubeApiCollector(**kwargs)
        return YouTubeCollector(**kwargs)
    if platform == "tiktok":
        return TikTokCollector(**kwargs)
    if platform == "instagram":
        return InstagramCollector(**kwargs)
    raise ValueError(f"未知平台: {platform}")


def run_pipeline(
    *,
    platforms: list[str] | None = None,
    queries: list[str] | None = None,
    max_queries: int | None = None,
    output_dir: Path | None = None,
    demo: bool = False,
) -> dict[str, Any]:
    rules = load_yaml("inclusion_exclusion.yaml")
    schema = load_yaml("coding_schema.yaml")
    search_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if queries is None:
        queries = build_search_queries()
    if max_queries:
        queries = queries[:max_queries]

    if platforms is None:
        platforms = [p for p, cfg in rules.get("platforms", {}).items() if cfg.get("enabled")]

    all_records: list[CultureWorkRecord] = []
    search_log: list[dict[str, str]] = []

    for platform in platforms:
        if not rules.get("platforms", {}).get(platform, {}).get("enabled"):
            continue
        collector = _collector_for_platform(platform, rules, demo=demo)
        for query in queries:
            search_log.append({
                "search_date": search_date,
                "platform": platform,
                "query": query,
            })
            try:
                batch = collector.search(query, search_date)
                all_records.extend(batch)
            except Exception as exc:  # noqa: BLE001
                search_log.append({
                    "search_date": search_date,
                    "platform": platform,
                    "query": query,
                    "error": str(exc),
                })

    # 处理流水线
    processed: list[CultureWorkRecord] = []
    for rec in all_records:
        rec = apply_inclusion_exclusion(rec, rules)
        rec = apply_language_filter(rec, rules)
        processed.append(rec)

    processed = deduplicate_records(processed, rules)

    coded: list[CultureWorkRecord] = []
    for rec in processed:
        coded.append(auto_code_record(rec, schema))

    out_dir = output_dir or DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    raw_path = out_dir / f"raw_{stamp}.json"
    included_path = out_dir / f"included_{stamp}.json"
    excluded_path = out_dir / f"excluded_{stamp}.json"
    log_path = out_dir / f"search_log_{stamp}.json"
    coding_path = out_dir / f"coding_review_{stamp}.csv"

    with raw_path.open("w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in coded], f, ensure_ascii=False, indent=2)

    included = [r for r in coded if r.inclusion_status == "included" and not r.is_duplicate]
    excluded = [r for r in coded if r.inclusion_status == "excluded" or r.is_duplicate]

    with included_path.open("w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in included], f, ensure_ascii=False, indent=2)

    with excluded_path.open("w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in excluded], f, ensure_ascii=False, indent=2)

    with log_path.open("w", encoding="utf-8") as f:
        json.dump(search_log, f, ensure_ascii=False, indent=2)

    export_coding_csv(included, coding_path)

    return {
        "search_date": search_date,
        "total_collected": len(all_records),
        "included": len(included),
        "excluded": len(excluded),
        "raw_path": str(raw_path),
        "included_path": str(included_path),
        "excluded_path": str(excluded_path),
        "log_path": str(log_path),
        "coding_path": str(coding_path),
    }


def export_coding_csv(records: list[CultureWorkRecord], path: Path) -> None:
    import csv

    fieldnames = [
        "search_date", "platform", "url", "title", "uploader",
        "view_count", "like_count", "comment_count", "language",
        "auto_theme", "auto_publisher_type", "auto_media_form",
        "auto_narrative_style", "auto_cultural_explanation",
        "auto_interaction_design", "auto_audience_sentiment",
        "manual_theme", "manual_publisher_type", "manual_narrative_style",
        "reviewer_id", "review_date", "confidence", "notes",
    ]

    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            ac = r.auto_codes
            af = ac.get("audience_feedback", {})
            writer.writerow({
                "search_date": r.search_date,
                "platform": r.platform,
                "url": r.url,
                "title": r.title,
                "uploader": r.uploader,
                "view_count": r.view_count,
                "like_count": r.like_count,
                "comment_count": r.comment_count,
                "language": r.language,
                "auto_theme": "|".join(ac.get("theme", [])),
                "auto_publisher_type": ac.get("publisher_type", ""),
                "auto_media_form": ac.get("media_form", ""),
                "auto_narrative_style": "|".join(ac.get("narrative_style", [])),
                "auto_cultural_explanation": ac.get("cultural_explanation", ""),
                "auto_interaction_design": "|".join(ac.get("interaction_design", [])),
                "auto_audience_sentiment": af.get("sentiment", ""),
                "manual_theme": "",
                "manual_publisher_type": "",
                "manual_narrative_style": "",
                "reviewer_id": "",
                "review_date": "",
                "confidence": "",
                "notes": "",
            })
