#!/usr/bin/env python3
"""YouTube Data API 真实采集脚本。"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.collectors.youtube_api import YouTubeApiCollector, YouTubeApiError  # noqa: E402
from src.config_loader import build_search_queries, query_stats  # noqa: E402
from src.env_loader import get_youtube_api_key, load_env, require_youtube_api_key  # noqa: E402
from src.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser(description="YouTube API 真实采集（江苏文化）")
    parser.add_argument("--api-key", help="YouTube Data API v3 密钥（也可用 .env / 环境变量）")
    parser.add_argument(
        "--max-queries",
        type=int,
        default=int(os.environ.get("COLLECTION_MAX_QUERIES", "20")),
        help="本次使用的检索词数量（默认20）",
    )
    parser.add_argument("--max-results", type=int, default=10, help="每个检索词返回视频数（默认10）")
    parser.add_argument("--verify-only", action="store_true", help="仅验证 API Key，不采集")
    parser.add_argument("--queries", nargs="*", help="自定义检索词（覆盖关键词表）")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data")
    args = parser.parse_args()

    api_key = require_youtube_api_key(args.api_key)
    stats = query_stats()

    print("=" * 60)
    print("江苏文化 — YouTube API 真实采集")
    print("=" * 60)
    print(f"关键词表 v2 可用检索词: {stats['total_queries']} 条")
    print(f"本次使用: {args.max_queries if not args.queries else len(args.queries)} 条")
    print(f"每词返回: {args.max_results} 条")
    print()

    collector = YouTubeApiCollector(api_key=api_key, max_results=args.max_results)
    try:
        verify = collector.verify()
        print(f"✓ API Key 验证通过，示例结果: {verify.get('sample_title', '(无)')}")
    except YouTubeApiError as exc:
        print(f"✗ API Key 验证失败: {exc}")
        sys.exit(1)

    if args.verify_only:
        return

    # 将 max_results 传入采集器配置
    os.environ["YOUTUBE_MAX_RESULTS"] = str(args.max_results)

    result = run_pipeline(
        platforms=["youtube"],
        queries=args.queries,
        max_queries=None if args.queries else args.max_queries,
        output_dir=args.output_dir,
        youtube_api_key=api_key,
        force_youtube_api=True,
    )

    print()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()
    print(f"纳入: {result['included']} / 采集: {result['total_collected']}")
    print(f"纳入数据: {result['included_path']}")
    print(f"编码表:   {result['coding_path']}")


if __name__ == "__main__":
    main()
