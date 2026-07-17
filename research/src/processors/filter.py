"""纳入/排除规则过滤。"""

from __future__ import annotations

import re
from typing import Any

from ..models import CultureWorkRecord


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _field_text(record: CultureWorkRecord, fields: list[str]) -> str:
    parts: list[str] = []
    for f in fields:
        if f == "title":
            parts.append(record.title)
        elif f == "description":
            parts.append(record.description)
        elif f == "tags":
            parts.extend(record.tags)
    return _normalize(" ".join(parts))


def _match_any(text: str, patterns: list[str]) -> bool:
    for p in patterns:
        if p and p.lower() in text:
            return True
    return False


def apply_inclusion_exclusion(
    record: CultureWorkRecord,
    rules: dict[str, Any],
) -> CultureWorkRecord:
    """根据规则标记纳入或排除。"""
    inclusion = rules.get("inclusion", {})
    exclusion = rules.get("exclusion", {})

    text_all = _normalize(
        " ".join([record.title, record.description, " ".join(record.tags), record.subtitles])
    )

    # 排除规则优先
    for rule in exclusion.get("any_of", []):
        patterns = rule.get("patterns", [])
        if patterns and _match_any(text_all, patterns):
            record.inclusion_status = "excluded"
            record.exclusion_reason = rule.get("id", "excluded")
            return record

    # 纳入规则：至少满足一条
    included = False
    for rule in inclusion.get("any_of", []):
        fields = rule.get("fields", ["title", "description", "tags"])
        field_text = _field_text(record, fields)
        patterns = rule.get("patterns", [])
        if patterns and _match_any(field_text, patterns):
            included = True
            break

    if included:
        record.inclusion_status = "included"
        record.exclusion_reason = None
    else:
        record.inclusion_status = "excluded"
        record.exclusion_reason = "no_inclusion_match"

    return record
