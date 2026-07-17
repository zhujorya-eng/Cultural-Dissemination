"""YouTube 公开作品采集。"""

from __future__ import annotations

from ..models import CultureWorkRecord
from .base import BaseCollector


class YouTubeCollector(BaseCollector):
    platform = "youtube"

    def search(self, query: str, search_date: str) -> list[CultureWorkRecord]:
        target = f"ytsearch{self.max_results}:{query}"
        extra = ["--write-comments"] if self.fetch_comments else []
        extra.extend(["--write-subs", "--write-auto-subs", "--sub-langs", "en,zh.*"])

        try:
            raw_list = self._run_ytdlp(target, extra_args=extra)
        except RuntimeError:
            return []

        records: list[CultureWorkRecord] = []
        for data in raw_list:
            url = data.get("webpage_url") or data.get("url") or ""
            rec = self._map_record(data, search_date=search_date, search_query=query, url=url)
            if rec:
                records.append(rec)
        return records
