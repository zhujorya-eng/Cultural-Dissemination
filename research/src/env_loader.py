"""环境变量与 API Key 加载。"""

from __future__ import annotations

import os
from pathlib import Path


def load_env() -> None:
    """从 research/.env 加载环境变量（不覆盖已设置的变量）。"""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)


def get_youtube_api_key(cli_key: str | None = None) -> str:
    load_env()
    return (cli_key or os.environ.get("YOUTUBE_API_KEY") or "").strip()


def require_youtube_api_key(cli_key: str | None = None) -> str:
    key = get_youtube_api_key(cli_key)
    if not key:
        raise RuntimeError(
            "未配置 YouTube API Key。请任选一种方式：\n"
            "  1. 复制 .env.example 为 .env 并填入 YOUTUBE_API_KEY\n"
            "  2. export YOUTUBE_API_KEY='your-key'\n"
            "  3. python scripts/run_collection.py --api-key 'your-key'\n"
            "申请地址: https://console.cloud.google.com/apis/library/youtube.googleapis.com"
        )
    return key
