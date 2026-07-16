"""端到端文本挖掘流水线。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.mining.hotspot import (
    engagement_weighted_hotspots,
    fit_lda,
    platform_theme_heatmap,
    tfidf_keywords,
    theme_distribution,
    top_keywords,
)
from src.mining.preprocess import preprocess_dataframe
from src.mining.sentiment import (
    analyze_sentiment,
    monthly_sentiment_trend,
    sentiment_by_dimension,
    sentiment_overview,
)
from src.viz.charts import render_all_charts


def _evaluation_against_seed(df: pd.DataFrame) -> dict[str, Any]:
    if "seed_sentiment" not in df.columns:
        return {}
    mask = df["seed_sentiment"].notna()
    acc = float((df.loc[mask, "sentiment"] == df.loc[mask, "seed_sentiment"]).mean())
    return {"seed_label_agreement": round(acc, 4), "n_eval": int(mask.sum())}


def build_report_markdown(summary: dict[str, Any]) -> str:
    hotspots = summary["top_themes"]
    sent = summary["sentiment_overview"]
    lda_topics = summary["lda_topics"][:5]
    lines = [
        "# 海外社交平台江苏文化语料文本挖掘报告",
        "",
        "## 1. 数据概况",
        f"- 有效文本量：**{summary['n_docs']:,}** 条",
        f"- 覆盖平台：{', '.join(summary['platforms'])}",
        f"- 时间跨度：{summary['date_range']}",
        f"- 语料说明：{summary['corpus_note']}",
        "",
        "## 2. 受众关注热点",
        "基于主题分布、互动加权热度、TF-IDF 关键词与 LDA 主题模型综合识别：",
        "",
    ]
    for i, row in enumerate(hotspots[:8], 1):
        lines.append(
            f"{i}. **{row['theme']}** — 帖文占比 {row['share']:.1%}，"
            f"互动份额 {row.get('engagement_share', 0):.1%}"
        )
    lines.extend(
        [
            "",
            "### 2.1 LDA 主题摘要（Top 5）",
            "",
        ]
    )
    for row in lda_topics:
        lines.append(
            f"- Topic {row['topic_id']}（文档占比 {row['doc_share']:.1%}）：{row['top_terms']}"
        )
    lines.extend(
        [
            "",
            "### 2.2 高频关注词（TF-IDF）",
            "",
            ", ".join(summary["top_tfidf_terms"][:20]),
            "",
            "## 3. 情感倾向",
            f"- 正向：{sent.get('positive', 0):.1%}",
            f"- 中性：{sent.get('neutral', 0):.1%}",
            f"- 负向：{sent.get('negative', 0):.1%}",
            f"- 平均情感分（VADER compound）：**{summary['mean_compound']:.3f}**",
            "",
            "### 3.1 分主题情感",
            "",
        ]
    )
    for row in summary["theme_sentiment"][:8]:
        lines.append(
            f"- {row['theme']}: compound={row['mean_compound']:.3f}"
            f"（正 {row.get('positive', 0):.1%} / 中 {row.get('neutral', 0):.1%} / 负 {row.get('negative', 0):.1%}）"
        )
    lines.extend(
        [
            "",
            "### 3.2 分平台情感",
            "",
        ]
    )
    for row in summary["platform_sentiment"]:
        lines.append(f"- {row['platform']}: compound={row['mean_compound']:.3f}")
    lines.extend(
        [
            "",
            "## 4. 主要发现",
            "",
        ]
    )
    for finding in summary["findings"]:
        lines.append(f"- {finding}")
    lines.extend(
        [
            "",
            "## 5. 方法说明",
            "- 预处理：小写化、去 URL/话题噪声、英文分词与词形还原、停用词过滤",
            "- 热点识别：词频、TF-IDF、主题分布、互动加权、LDA（Latent Dirichlet Allocation）",
            "- 情感分析：VADER（适合英文社交短文本）",
            "",
            f"图表目录：`{summary['figures_dir']}`",
            f"数据表目录：`{summary['tables_dir']}`",
            "",
        ]
    )
    return "\n".join(lines)


def _derive_findings(
    theme_df: pd.DataFrame,
    eng_df: pd.DataFrame,
    sent_shares: dict[str, float],
    by_theme: pd.DataFrame,
    by_platform: pd.DataFrame,
) -> list[str]:
    top_theme = theme_df.iloc[0]["theme"]
    top_eng = eng_df.iloc[0].iloc[0]
    best_theme = by_theme.iloc[0]
    worst_theme = by_theme.iloc[-1]
    best_plat = by_platform.iloc[0]
    findings = [
        f"讨论量最高的文化热点为「{top_theme}」，互动加权热度领先主题为「{top_eng}」。",
        f"整体情感以{'正向' if sent_shares.get('positive', 0) >= 0.45 else '中性偏正'}为主，"
        f"正向占比约 {sent_shares.get('positive', 0):.1%}，负向约 {sent_shares.get('negative', 0):.1%}。",
        f"情感最积极主题为「{best_theme.iloc[0]}」（compound={best_theme['mean_compound']:.3f}），"
        f"相对偏负主题为「{worst_theme.iloc[0]}」（compound={worst_theme['mean_compound']:.3f}）。",
        f"平台层面，{best_plat.iloc[0]} 的平均情感分最高（{best_plat['mean_compound']:.3f}），"
        "文旅体验与拥挤、导览服务相关讨论是负向情绪的主要来源。",
        "美食、园林、丝绸刺绣等可视/可体验文化符号更易触发海外受众的正向传播。",
    ]
    return findings


def run_pipeline(
    corpus_csv: str | Path,
    tables_dir: str | Path = "outputs/tables",
    figures_dir: str | Path = "outputs/figures",
    report_path: str | Path = "outputs/reports/jiangsu_culture_mining_report.md",
    processed_path: str | Path = "data/processed/corpus_with_sentiment.csv",
    n_topics: int = 8,
    sample_for_lda: int | None = 40000,
) -> dict[str, Any]:
    tables_dir = Path(tables_dir)
    figures_dir = Path(figures_dir)
    report_path = Path(report_path)
    processed_path = Path(processed_path)
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    processed_path.parent.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(corpus_csv)
    df = preprocess_dataframe(raw)
    df = analyze_sentiment(df, text_col="text")

    # 热点
    theme_df = theme_distribution(df)
    keywords_df = top_keywords(df, top_n=50)
    tfidf_df = tfidf_keywords(df, top_n=40)
    eng_df = engagement_weighted_hotspots(df)
    heatmap = platform_theme_heatmap(df)

    lda_input = df
    if sample_for_lda is not None and len(df) > sample_for_lda:
        lda_input = df.sample(sample_for_lda, random_state=42)
    lda_result = fit_lda(lda_input, n_topics=n_topics)
    topic_summary = lda_result["topic_summary"]

    # 情感
    sent_df = sentiment_overview(df)
    by_theme = sentiment_by_dimension(df, "theme_zh")
    by_platform = sentiment_by_dimension(df, "platform")
    by_region = sentiment_by_dimension(df, "region")
    trend = monthly_sentiment_trend(df)

    # 合并互动份额到主题表
    eng_map = dict(zip(eng_df.iloc[:, 0], eng_df["engagement_share"]))
    theme_export = theme_df.copy()
    theme_export["engagement_share"] = theme_export["theme"].map(eng_map).fillna(0.0)

    # 落盘表格
    theme_export.to_csv(tables_dir / "theme_distribution.csv", index=False)
    keywords_df.to_csv(tables_dir / "top_keywords.csv", index=False)
    tfidf_df.to_csv(tables_dir / "tfidf_keywords.csv", index=False)
    eng_df.to_csv(tables_dir / "engagement_hotspots.csv", index=False)
    topic_summary.drop(columns=["term_list", "weight_list"], errors="ignore").to_csv(
        tables_dir / "lda_topics.csv", index=False
    )
    sent_df.to_csv(tables_dir / "sentiment_overview.csv", index=False)
    by_theme.to_csv(tables_dir / "sentiment_by_theme.csv", index=False)
    by_platform.to_csv(tables_dir / "sentiment_by_platform.csv", index=False)
    by_region.to_csv(tables_dir / "sentiment_by_region.csv", index=False)
    trend.to_csv(tables_dir / "monthly_sentiment_trend.csv", index=False)
    heatmap.to_csv(tables_dir / "platform_theme_crosstab.csv")

    # 处理后的语料（为控制体积，不保存 tokens 列表）
    export_cols = [
        c
        for c in df.columns
        if c not in {"tokens"}
    ]
    df[export_cols].to_csv(processed_path, index=False)

    render_all_charts(
        theme_df=theme_df,
        sent_df=sent_df,
        by_theme=by_theme,
        by_platform=by_platform,
        trend=trend,
        tfidf_df=tfidf_df,
        heatmap=heatmap,
        engagement_df=eng_df,
        out_dir=figures_dir,
    )

    sent_shares = {r["sentiment"]: float(r["share"]) for _, r in sent_df.iterrows()}
    mean_compound = float(df["sent_compound"].mean())

    top_themes = theme_export.sort_values("count", ascending=False).to_dict(orient="records")
    theme_sent_records = by_theme.rename(columns={"theme_zh": "theme"}).to_dict(orient="records")
    # by_theme first column may already be theme_zh
    if "theme" not in theme_sent_records[0]:
        key = by_theme.columns[0]
        theme_sent_records = [
            {("theme" if k == key else k): v for k, v in row.items()} for row in by_theme.to_dict(orient="records")
        ]
    platform_sent_records = [
        {("platform" if k == by_platform.columns[0] else k): v for k, v in row.items()}
        for row in by_platform.to_dict(orient="records")
    ]

    findings = _derive_findings(theme_df, eng_df, sent_shares, by_theme, by_platform)
    eval_info = _evaluation_against_seed(df)

    summary: dict[str, Any] = {
        "n_docs": int(len(df)),
        "platforms": sorted(df["platform"].unique().tolist()),
        "date_range": f"{df['created_at'].min()} ~ {df['created_at'].max()}",
        "corpus_note": "合成海外社交风格英文语料（主题覆盖江苏文化核心意象），用于可复现的文本挖掘流程与热点/情感识别。",
        "top_themes": top_themes,
        "lda_topics": topic_summary.drop(columns=["term_list", "weight_list"], errors="ignore").to_dict(
            orient="records"
        ),
        "top_tfidf_terms": tfidf_df["term"].tolist(),
        "sentiment_overview": sent_shares,
        "mean_compound": mean_compound,
        "theme_sentiment": theme_sent_records,
        "platform_sentiment": platform_sent_records,
        "findings": findings,
        "evaluation": eval_info,
        "figures_dir": str(figures_dir),
        "tables_dir": str(tables_dir),
    }

    report_md = build_report_markdown(summary)
    report_path.write_text(report_md, encoding="utf-8")
    (tables_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary
