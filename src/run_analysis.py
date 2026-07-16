#!/usr/bin/env python3
"""一键运行：语料生成 -> 热点与情感挖掘 -> 报告/图表输出。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.corpus.generate_corpus import generate_corpus
from src.mining.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="江苏文化海外社交语料文本挖掘")
    parser.add_argument("--n", type=int, default=105000, help="语料条数（默认约 10.5 万）")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--corpus",
        type=str,
        default="data/raw/jiangsu_overseas_social_corpus.csv",
        help="语料 CSV 路径；若不存在则自动生成",
    )
    parser.add_argument("--skip-generate", action="store_true", help="跳过生成，直接读取已有语料")
    parser.add_argument("--n-topics", type=int, default=8)
    parser.add_argument("--lda-sample", type=int, default=40000, help="LDA 抽样规模，0 表示全量")
    args = parser.parse_args()

    corpus_path = Path(args.corpus)
    if not args.skip_generate or not corpus_path.exists():
        print(f"[1/2] Generating corpus n={args.n:,} ...")
        generate_corpus(n_samples=args.n, seed=args.seed, output_path=corpus_path)
    else:
        print(f"[1/2] Using existing corpus: {corpus_path}")

    lda_sample = None if args.lda_sample == 0 else args.lda_sample
    print("[2/2] Running text mining pipeline ...")
    summary = run_pipeline(
        corpus_csv=corpus_path,
        n_topics=args.n_topics,
        sample_for_lda=lda_sample,
    )

    print("\n===== Analysis Complete =====")
    print(f"Documents: {summary['n_docs']:,}")
    print("Top hotspots:")
    for row in summary["top_themes"][:5]:
        print(f"  - {row['theme']}: {row['share']:.1%}")
    print("Sentiment shares:")
    for k, v in summary["sentiment_overview"].items():
        print(f"  - {k}: {v:.1%}")
    print(f"Mean compound: {summary['mean_compound']:.3f}")
    print(f"Report: outputs/reports/jiangsu_culture_mining_report.md")
    print(f"Summary JSON: outputs/tables/summary.json")
    # 控制台附带简要 JSON，便于自动化检查
    brief = {
        "n_docs": summary["n_docs"],
        "sentiment_overview": summary["sentiment_overview"],
        "mean_compound": summary["mean_compound"],
        "top_themes": [r["theme"] for r in summary["top_themes"][:5]],
    }
    print(json.dumps(brief, ensure_ascii=False))


if __name__ == "__main__":
    main()
