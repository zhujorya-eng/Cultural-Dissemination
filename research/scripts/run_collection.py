#!/usr/bin/env python3
"""江苏文化海外传播数据采集入口。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 允许从 research/ 目录直接运行
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="江苏文化海外社交平台公开作品采集")
    parser.add_argument(
        "--platforms",
        nargs="+",
        default=["youtube"],
        choices=["youtube", "tiktok", "instagram"],
        help="目标平台",
    )
    parser.add_argument(
        "--max-queries",
        type=int,
        default=3,
        help="每个平台使用的检索词数量（默认3，完整采集可增大）",
    )
    parser.add_argument(
        "--queries",
        nargs="*",
        help="自定义检索词（覆盖关键词表）",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "data",
        help="输出目录",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="使用内置样本数据（无需网络，验证流水线）",
    )
    parser.add_argument(
        "--api-key",
        help="YouTube Data API v3 密钥（真实采集 YouTube 时推荐）",
    )
    parser.add_argument(
        "--force-youtube-api",
        action="store_true",
        help="强制使用 YouTube API（无 Key 时报错）",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("江苏文化海外传播 — 数据采集流水线")
    print("=" * 60)
    print(f"平台: {', '.join(args.platforms)}")
    print(f"检索词数量: {args.max_queries if not args.queries else len(args.queries)}")
    print()

    result = run_pipeline(
        platforms=args.platforms,
        queries=args.queries,
        max_queries=None if args.queries else args.max_queries,
        output_dir=args.output_dir,
        demo=args.demo,
        youtube_api_key=args.api_key,
        force_youtube_api=args.force_youtube_api,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()
    print(f"纳入记录: {result['included']} / 总采集: {result['total_collected']}")
    print(f"人工编码表: {result['coding_path']}")


if __name__ == "__main__":
    main()
