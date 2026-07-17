"""YouTube Data API v3 采集（推荐，需 API Key）。"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from typing import Any

from ..models import CommentRecord, CultureWorkRecord


class YouTubeApiCollector:
    platform = "youtube"

    def __init__(
        self,
        api_key: str | None = None,
        max_results: int = 15,
        fetch_comments: bool = True,
        max_comments: int = 50,
    ):
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY", "")
        self.max_results = max_results
        self.fetch_comments = fetch_comments
        self.max_comments = max_comments

    def _get(self, path: str, params: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("未设置 YOUTUBE_API_KEY 环境变量")
        params["key"] = self.api_key
        url = f"https://www.googleapis.com/youtube/v3/{path}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(url, timeout=30) as resp:  # noqa: S310
            return json.loads(resp.read().decode())

    def search(self, query: str, search_date: str) -> list[CultureWorkRecord]:
        data = self._get(
            "search",
            {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": min(self.max_results, 50),
                "relevanceLanguage": "en",
            },
        )

        video_ids = [item["id"]["videoId"] for item in data.get("items", []) if item.get("id", {}).get("videoId")]
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
            url = f"https://www.youtube.com/watch?v={vid}"

            comments: list[CommentRecord] = []
            if self.fetch_comments:
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
                    description=snippet.get("description", ""),
                    uploader=snippet.get("channelTitle", ""),
                    upload_date=snippet.get("publishedAt", "")[:10].replace("-", ""),
                    view_count=int(stats.get("viewCount", 0)) if stats.get("viewCount") else None,
                    like_count=int(stats.get("likeCount", 0)) if stats.get("likeCount") else None,
                    comment_count=int(stats.get("commentCount", 0)) if stats.get("commentCount") else None,
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
        except Exception:  # noqa: BLE001
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
