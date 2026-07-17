"""平台采集器基类。"""

from __future__ import annotations

import json
import subprocess
from abc import ABC, abstractmethod
from typing import Any

from ..models import CommentRecord, CultureWorkRecord


class BaseCollector(ABC):
    platform: str = "unknown"

    def __init__(self, max_results: int = 15, fetch_comments: bool = True, max_comments: int = 50):
        self.max_results = max_results
        self.fetch_comments = fetch_comments
        self.max_comments = max_comments

    @abstractmethod
    def search(self, query: str, search_date: str) -> list[CultureWorkRecord]:
        ...

    def _run_ytdlp(self, target: str, extra_args: list[str] | None = None) -> list[dict[str, Any]]:
        """通过 yt-dlp 提取元数据。"""
        cmd = [
            "yt-dlp",
            "--js-runtimes", "node",
            "--ignore-errors",
            "--no-download",
            "--dump-single-json",
            "--no-warnings",
        ]
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(target)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            raise RuntimeError(f"yt-dlp 执行失败: {exc}") from exc

        records: list[dict[str, Any]] = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return records

    def _parse_comments(self, data: dict[str, Any]) -> list[CommentRecord]:
        comments: list[CommentRecord] = []
        for item in data.get("comments") or []:
            if not isinstance(item, dict):
                continue
            text = item.get("text") or item.get("comment") or ""
            if not text.strip():
                continue
            comments.append(
                CommentRecord(
                    author=str(item.get("author") or item.get("author_id") or "unknown"),
                    text=text.strip(),
                    like_count=int(item.get("like_count") or 0),
                    timestamp=item.get("timestamp"),
                )
            )
            if len(comments) >= self.max_comments:
                break
        return comments

    def _extract_subtitles(self, data: dict[str, Any]) -> tuple[str, str | None]:
        subtitles = data.get("subtitles") or data.get("automatic_captions") or {}
        if not subtitles:
            return "", None

        # 优先英语/中文字幕
        for lang in ("en", "en-US", "en-GB", "zh", "zh-Hans", "zh-Hant", "zh-CN"):
            if lang in subtitles and subtitles[lang]:
                texts: list[str] = []
                for track in subtitles[lang][:1]:
                    for frag in track.get("fragments") or []:
                        t = frag.get("text", "").strip()
                        if t:
                            texts.append(t)
                if texts:
                    return " ".join(texts)[:8000], lang

        # 回退任意可用字幕
        for lang, tracks in subtitles.items():
            if not tracks:
                continue
            texts = []
            for frag in tracks[0].get("fragments") or []:
                t = frag.get("text", "").strip()
                if t:
                    texts.append(t)
            if texts:
                return " ".join(texts)[:8000], lang
        return "", None

    def _map_record(
        self,
        data: dict[str, Any],
        *,
        search_date: str,
        search_query: str,
        url: str,
    ) -> CultureWorkRecord | None:
        if data.get("_type") == "playlist":
            return None

        title = (data.get("title") or "").strip()
        if not title:
            return None

        tags = data.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]

        subtitles, sub_lang = self._extract_subtitles(data)

        return CultureWorkRecord(
            search_date=search_date,
            search_query=search_query,
            platform=self.platform,
            url=url or data.get("webpage_url") or data.get("original_url") or "",
            platform_id=str(data.get("id") or ""),
            title=title,
            description=(data.get("description") or "")[:10000],
            uploader=str(data.get("uploader") or data.get("channel") or data.get("uploader_id") or ""),
            upload_date=data.get("upload_date"),
            duration_sec=data.get("duration"),
            view_count=data.get("view_count"),
            like_count=data.get("like_count"),
            comment_count=data.get("comment_count"),
            tags=[str(t) for t in tags],
            subtitles=subtitles,
            subtitles_lang=sub_lang,
            comments=self._parse_comments(data),
        )
