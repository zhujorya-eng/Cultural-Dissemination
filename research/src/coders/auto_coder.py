"""机器辅助编码。"""

from __future__ import annotations

import re
from typing import Any

from ..models import CultureWorkRecord


def _text_blob(record: CultureWorkRecord) -> str:
    comments = " ".join(c.text for c in record.comments[:20])
    return " ".join([
        record.title,
        record.description,
        " ".join(record.tags),
        record.subtitles,
        comments,
        record.uploader,
    ]).lower()


def _match_keywords(text: str, keywords: list[str]) -> bool:
    return any(k.lower() in text for k in keywords if k)


def _match_signals(text: str, signals: list[str]) -> int:
    return sum(1 for s in signals if s.lower() in text)


def code_theme(text: str, schema: dict[str, Any]) -> list[str]:
    themes: list[str] = []
    for opt in schema.get("options", []):
        if _match_keywords(text, opt.get("keywords", [])):
            themes.append(opt["id"])
    return themes or ["other"]


def code_publisher_type(text: str, schema: dict[str, Any]) -> str:
    best_id = "unknown"
    best_score = 0
    for opt in schema.get("options", []):
        score = _match_signals(text, opt.get("signals", []))
        if score > best_score:
            best_score = score
            best_id = opt["id"]
    return best_id


def code_media_form(record: CultureWorkRecord, text: str, schema: dict[str, Any]) -> str:
    for opt in schema.get("options", []):
        if _match_keywords(text, opt.get("keywords", [])):
            return opt["id"]

    dur = record.duration_sec
    if dur is not None:
        max_s = opt.get("max_duration_sec") if (opt := None) else None  # noqa: F841
        for opt in schema.get("options", []):
            min_s = opt.get("min_duration_sec", 0)
            max_s = opt.get("max_duration_sec", float("inf"))
            if min_s <= dur <= max_s:
                return opt["id"]
    return "short_video"


def code_multi(text: str, schema: dict[str, Any]) -> list[str]:
    matched: list[str] = []
    for opt in schema.get("options", []):
        if _match_keywords(text, opt.get("keywords", [])):
            matched.append(opt["id"])
    return matched


def code_cultural_explanation(text: str, schema: dict[str, Any]) -> str:
    best_id = "none"
    best_score = 0
    for opt in schema.get("options", []):
        score = _match_keywords(text, opt.get("keywords", [])) and 1 or 0
        score = _match_signals(text, opt.get("keywords", [])) if opt.get("keywords") else score
        if isinstance(score, bool):
            score = int(score)
        if score > best_score:
            best_score = score
            best_id = opt["id"]
    if best_score == 0 and ("subtitle" in text or "字幕" in text or "explain" in text):
        return "explicit_subtitle"
    return best_id


def analyze_comments(record: CultureWorkRecord) -> dict[str, Any]:
    if not record.comments:
        return {
            "sentiment": "neutral",
            "engagement_level": "low",
            "themes_in_comments": [],
        }

    pos_words = ["beautiful", "amazing", "love", "great", "wonderful", "美", "喜欢", "棒", "震撼"]
    neg_words = ["boring", "fake", "bad", "hate", "无聊", "差", "骗"]
    learn_words = ["learned", "history", "didn't know", "学到", "了解", "科普"]
    travel_words = ["want to visit", "travel", "trip", "想去", "旅游", "打卡"]

    pos = neg = 0
    themes: set[str] = set()
    for c in record.comments:
        t = c.text.lower()
        if any(w in t for w in pos_words):
            pos += 1
        if any(w in t for w in neg_words):
            neg += 1
        if any(w in t for w in learn_words):
            themes.add("cultural_learning")
        if any(w in t for w in travel_words):
            themes.add("travel_intent")
        if any(w in t for w in ["beautiful", "aesthetic", "美", "漂亮"]):
            themes.add("appreciation_aesthetic")

    if pos > neg * 2:
        sentiment = "positive"
    elif neg > pos * 2:
        sentiment = "negative"
    elif pos > 0 and neg > 0:
        sentiment = "mixed"
    else:
        sentiment = "neutral"

    views = record.view_count or 0
    likes = record.like_count or 0
    comments_n = record.comment_count or len(record.comments)
    engagement_score = views + likes * 5 + comments_n * 10
    if engagement_score >= 1000:
        engagement = "high"
    elif engagement_score >= 100:
        engagement = "medium"
    else:
        engagement = "low"

    return {
        "sentiment": sentiment,
        "engagement_level": engagement,
        "themes_in_comments": sorted(themes),
    }


def auto_code_record(record: CultureWorkRecord, schema: dict[str, Any]) -> CultureWorkRecord:
    if record.inclusion_status != "included":
        return record

    text = _text_blob(record)
    dims = schema.get("coding_dimensions", {})

    codes: dict[str, Any] = {}
    if "theme" in dims:
        codes["theme"] = code_theme(text, dims["theme"])
    if "publisher_type" in dims:
        codes["publisher_type"] = code_publisher_type(text, dims["publisher_type"])
    if "media_form" in dims:
        codes["media_form"] = code_media_form(record, text, dims["media_form"])
    if "narrative_style" in dims:
        codes["narrative_style"] = code_multi(text, dims["narrative_style"]) or ["experiential"]
    if "cultural_explanation" in dims:
        codes["cultural_explanation"] = code_cultural_explanation(text, dims["cultural_explanation"])
    if "interaction_design" in dims:
        codes["interaction_design"] = code_multi(text, dims["interaction_design"]) or ["passive"]
    if "audience_feedback" in dims:
        codes["audience_feedback"] = analyze_comments(record)

    record.auto_codes = codes
    return record
