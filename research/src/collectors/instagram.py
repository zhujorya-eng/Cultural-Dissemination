"""Instagram 公开作品采集。"""

from __future__ import annotations

from ..models import CultureWorkRecord
from .base import BaseCollector


class InstagramCollector(BaseCollector):
    platform = "instagram"

    def search(self, query: str, search_date: str) -> list[CultureWorkRecord]:
        clean = query.lstrip("#")
        if query.startswith("#"):
            target = f"https://www.instagram.com/explore/tags/{clean}/"
        else:
            # Instagram 无通用搜索 API，使用标签探索页
            target = f"https://www.instagram.com/explore/tags/{clean.replace(' ', '')}/"

        extra = ["--write-comments"] if self.fetch_comments else []
        extra.extend(["--playlist-end", str(self.max_results)])

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
