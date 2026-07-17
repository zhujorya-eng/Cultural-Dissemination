"""语种识别与过滤。"""

from __future__ import annotations

from typing import Any

from langdetect import DetectorFactory, LangDetectException, detect_langs

from ..models import CultureWorkRecord

DetectorFactory.seed = 42


def detect_language(text: str) -> tuple[str | None, float]:
    text = text.strip()
    if len(text) < 8:
        return None, 0.0
    try:
        langs = detect_langs(text)
        if not langs:
            return None, 0.0
        best = langs[0]
        return best.lang, float(best.prob)
    except LangDetectException:
        return None, 0.0


def apply_language_filter(
    record: CultureWorkRecord,
    rules: dict[str, Any],
) -> CultureWorkRecord:
    lang_cfg = rules.get("language", {})
    allowed = {x.lower() for x in lang_cfg.get("allowed_languages", [])}
    min_conf = float(lang_cfg.get("min_confidence", 0.7))

    # 检测文本：标题 > 描述 > 字幕
    candidates = [record.title, record.description, record.subtitles]
    lang, conf = None, 0.0
    for text in candidates:
        if text and len(text.strip()) >= 8:
            lang, conf = detect_language(text)
            if lang:
                break

    record.language = lang
    record.language_confidence = conf

    if record.inclusion_status != "included":
        return record

    if not lang or conf < min_conf:
        record.inclusion_status = "excluded"
        record.exclusion_reason = "unidentifiable_language"
        return record

    # 标准化中文变体
    normalized = lang.lower()
    if normalized.startswith("zh"):
        normalized = "zh"

    if allowed and normalized not in allowed and lang.lower() not in allowed:
        # 允许未知但高置信度语种通过并标记
        if conf >= 0.85:
            pass
        else:
            record.inclusion_status = "excluded"
            record.exclusion_reason = "language_not_allowed"

    return record
