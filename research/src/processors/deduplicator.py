"""机器去重。"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any

from ..models import CultureWorkRecord


def _normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^\w\s\u4e00-\u9fff#]", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def deduplicate_records(
    records: list[CultureWorkRecord],
    rules: dict[str, Any],
) -> list[CultureWorkRecord]:
    dedup_cfg = rules.get("deduplication", {})
    threshold = float(dedup_cfg.get("fuzzy_match", {}).get("title_similarity_threshold", 0.92))
    same_uploader = dedup_cfg.get("fuzzy_match", {}).get("same_uploader_required", True)

    seen_urls: set[str] = set()
    seen_ids: set[str] = set()
    kept: list[CultureWorkRecord] = []

    for record in records:
        if record.url in seen_urls:
            record.is_duplicate = True
            record.inclusion_status = "excluded"
            record.exclusion_reason = "duplicate_url"
            kept.append(record)
            continue

        pid = f"{record.platform}:{record.platform_id}"
        if record.platform_id and pid in seen_ids:
            record.is_duplicate = True
            record.inclusion_status = "excluded"
            record.exclusion_reason = "duplicate_platform_id"
            kept.append(record)
            continue

        is_fuzzy_dup = False
        norm_title = _normalize_title(record.title)
        for prev in kept:
            if prev.inclusion_status != "included" or prev.is_duplicate:
                continue
            if prev.platform != record.platform:
                continue
            if same_uploader and prev.uploader and record.uploader and prev.uploader != record.uploader:
                continue
            if _similarity(norm_title, _normalize_title(prev.title)) >= threshold:
                record.is_duplicate = True
                record.duplicate_of = prev.url
                record.inclusion_status = "excluded"
                record.exclusion_reason = "fuzzy_duplicate"
                is_fuzzy_dup = True
                break

        if record.url:
            seen_urls.add(record.url)
        if record.platform_id:
            seen_ids.add(pid)

        kept.append(record)

    return kept
