"""YouTube Data API v3 采集（推荐，需 API Key）。"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from ..models import CommentRecord, CultureWorkRecord


class YouTubeApiError(RuntimeError):
    def __init__(self, message: str, *, status: int | None = None):
        super().__init__(message)
        self.status = status


class YouTubeApiCollector:
    platform = "youtube"

    def __init__(
        self,
        api_key: str,
        max_results: int = 15,
        fetch_comments: bool = True,
        max_comments: int = 50,
        request_delay_sec: float = 0.35,
    ):
        if not api_key:
            raise ValueError("api_key 不能为空")
        self.api_key = api_key
        self.max_results = max_results
        self.fetch_comments = fetch_comments
        self.max_comments = max_comments
        self.request_delay_sec = request_delay_sec
        self.api_calls = 0

    def verify(self) -> dict[str, Any]:
        """验证 API Key 并返回配额测试搜索结果。"""
        data = self._get(
            "search",
            {
                "part": "snippet",
                "q": "Jiangsu culture",
                "type": "video",
                "maxResults": 1,
            },
        )
        return {
            "ok": True,
            "api_calls": self.api_calls,
            "sample_title": data.get("items", [{}])[0].get("snippet", {}).get("title", ""),
        }

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        params["key"] = self.api_key
        url = f"https://www.googleapis.com/youtube/v3/{path}?{urllib.parse.urlencode(params)}"
        time.sleep(self.request_delay_sec)
        self.api_calls += 1
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            msg = body
            try:
                err = json.loads(body)
                msg = err.get("error", {}).get("message", body)
            except json.JSONDecodeError:
                pass
            raise YouTubeApiError(f"YouTube API 错误 ({exc.code}): {msg}", status=exc.code) from exc

    @staticmethod
    def _parse_duration(iso: str | None) -> int | None:
        if not iso:
            return None
        m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
        if not m:
            return None
        h, mi, s = (int(x or 0) for x in m.groups())
        return h * 3600 + mi * 60 + s

    def search(self, query: str, search_date: str) -> list[CultureWorkRecord]:
        data = self._get(
            "search",
            {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": min(self.max_results, 50),
                "relevanceLanguage": "en",
                "safeSearch": "none",
            },
        )

        video_ids = [
            item["id"]["videoId"]
            for item in data.get("items", [])
            if item.get("id", {}).get("videoId")
        ]
        if not video_ids:
            return []

        details = self._get(
            "videos",
            {
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(video_ids),
            },
        )

        records: list[CultureWorkRecord] = []
        for item in details.get("items", []):
            vid = item["id"]
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})
            url = f"https://www.youtube.com/watch?v={vid}"

            comments: list[CommentRecord] = []
            if self.fetch_comments and stats.get("commentCount", "0") != "0":
                comments = self._fetch_comments(vid)

            tags = snippet.get("tags") or []
            records.append(
                CultureWorkRecord(
                    search_date=search_date,
                    search_query=query,
                    platform=self.platform,
                    url=url,
                    platform_id=vid,
                    title=snippet.get("title", ""),
                    description=(snippet.get("description") or "")[:10000],
                    uploader=snippet.get("channelTitle", ""),
                    upload_date=(snippet.get("publishedAt") or "")[:10].replace("-", ""),
                    duration_sec=self._parse_duration(content.get("duration")),
                    view_count=int(stats["viewCount"]) if stats.get("viewCount") else None,
                    like_count=int(stats["likeCount"]) if stats.get("likeCount") else None,
                    comment_count=int(stats["commentCount"]) if stats.get("commentCount") else None,
                    tags=[str(t) for t in tags],
                    comments=comments,
                )
            )
        return records

    def _fetch_comments(self, video_id: str) -> list[CommentRecord]:
        try:
            data = self._get(
                "commentThreads",
                {
                    "part": "snippet",
                    "videoId": video_id,
                    "maxResults": min(self.max_comments, 100),
                    "order": "relevance",
                    "textFormat": "plainText",
                },
            )
        except YouTubeApiError:
            return []

        comments: list[CommentRecord] = []
        for item in data.get("items", []):
            top = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
            text = top.get("textDisplay", "").strip()
            if not text:
                continue
            comments.append(
                CommentRecord(
                    author=top.get("authorDisplayName", "unknown"),
                    text=text,
                    like_count=int(top.get("likeCount", 0)),
                    timestamp=top.get("publishedAt"),
                )
            )
        return comments
