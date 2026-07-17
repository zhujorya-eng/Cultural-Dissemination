"""数据模型定义。"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class CommentRecord:
    author: str
    text: str
    like_count: int = 0
    timestamp: str | None = None


@dataclass
class CultureWorkRecord:
    """江苏文化作品标准化记录。"""

    # 检索元数据
    search_date: str
    search_query: str
    platform: str
    url: str

    # 作品基础信息
    platform_id: str
    title: str
    description: str = ""
    uploader: str = ""
    upload_date: str | None = None
    duration_sec: int | None = None
    view_count: int | None = None
    like_count: int | None = None
    comment_count: int | None = None

    # 文本内容
    tags: list[str] = field(default_factory=list)
    subtitles: str = ""
    subtitles_lang: str | None = None
    comments: list[CommentRecord] = field(default_factory=list)

    # 处理状态
    language: str | None = None
    language_confidence: float | None = None
    inclusion_status: str = "pending"  # pending | included | excluded
    exclusion_reason: str | None = None
    is_duplicate: bool = False
    duplicate_of: str | None = None

    # 机器编码
    auto_codes: dict[str, Any] = field(default_factory=dict)

    # 人工编码（待填）
    manual_codes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["comments"] = [asdict(c) for c in self.comments]
        return data

    @staticmethod
    def now_iso() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
