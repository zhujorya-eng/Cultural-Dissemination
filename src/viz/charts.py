"""可视化输出。"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from wordcloud import WordCloud

sns.set_theme(style="whitegrid", font_scale=1.05)
plt.rcParams["axes.unicode_minus"] = False
# 优先使用可用的中文字体；若无则图表中文可能显示为方框，英文不受影响
plt.rcParams["font.sans-serif"] = [
    "Noto Sans CJK SC",
    "WenQuanYi Micro Hei",
    "DejaVu Sans",
    "Arial Unicode MS",
    "sans-serif",
]


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_theme_distribution(theme_df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    data = theme_df.sort_values("count", ascending=True)
    ax.barh(data["theme"], data["count"], color="#2F6F8F")
    ax.set_xlabel("Posts")
    ax.set_title("Jiangsu Culture Hotspots (Theme Distribution)")
    _save(fig, path)


def plot_sentiment_pie(sent_df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 6.5))
    colors = {"positive": "#3B8C6E", "neutral": "#C4A35A", "negative": "#C05A5A"}
    labels = sent_df["sentiment"].tolist()
    sizes = sent_df["count"].tolist()
    ax.pie(
        sizes,
        labels=[f"{l}\n{s/sum(sizes):.1%}" for l, s in zip(labels, sizes)],
        colors=[colors.get(l, "#999999") for l in labels],
        startangle=90,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    ax.set_title("Overall Sentiment Distribution")
    _save(fig, path)


def plot_sentiment_by_theme(by_theme: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    plot_df = by_theme.copy()
    for col in ["positive", "neutral", "negative"]:
        if col not in plot_df.columns:
            plot_df[col] = 0.0
    plot_df = plot_df.sort_values("mean_compound", ascending=True)
    y = np.arange(len(plot_df))
    left = np.zeros(len(plot_df))
    for col, color in [("negative", "#C05A5A"), ("neutral", "#C4A35A"), ("positive", "#3B8C6E")]:
        ax.barh(y, plot_df[col], left=left, color=color, label=col, height=0.7)
        left += plot_df[col].to_numpy()
    ax.set_yticks(y)
    ax.set_yticklabels(plot_df.iloc[:, 0])
    ax.set_xlabel("Share")
    ax.set_title("Sentiment Structure by Theme")
    ax.legend(loc="lower right")
    _save(fig, path)


def plot_platform_sentiment(by_platform: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    data = by_platform.sort_values("mean_compound", ascending=False)
    colors = ["#3B8C6E" if v >= 0 else "#C05A5A" for v in data["mean_compound"]]
    ax.bar(data.iloc[:, 0], data["mean_compound"], color=colors)
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_ylabel("Mean VADER Compound")
    ax.set_title("Sentiment Polarity by Platform")
    ax.tick_params(axis="x", rotation=20)
    _save(fig, path)


def plot_monthly_trend(trend: pd.DataFrame, path: Path) -> None:
    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax1.plot(trend["month"], trend["mean_compound"], color="#2F6F8F", marker="o", linewidth=2)
    ax1.set_ylabel("Mean Sentiment Compound", color="#2F6F8F")
    ax1.tick_params(axis="x", rotation=45)
    ax2 = ax1.twinx()
    ax2.fill_between(trend["month"], trend["posts"], color="#8FA8B8", alpha=0.35)
    ax2.set_ylabel("Post Volume", color="#5A7280")
    ax1.set_title("Monthly Sentiment Trend & Discussion Volume")
    # 稀疏显示横轴标签
    step = max(1, len(trend) // 12)
    ax1.set_xticks(range(0, len(trend), step))
    ax1.set_xticklabels(trend["month"].iloc[::step], rotation=45, ha="right")
    _save(fig, path)


def plot_wordcloud(tfidf_df: pd.DataFrame, path: Path) -> None:
    freq = {row["term"]: float(row["mean_tfidf"]) for _, row in tfidf_df.iterrows()}
    wc = WordCloud(
        width=1200,
        height=700,
        background_color="white",
        colormap="viridis",
        max_words=80,
    ).generate_from_frequencies(freq)
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("TF-IDF Keyword Cloud (Jiangsu Culture Corpus)")
    _save(fig, path)


def plot_platform_theme_heatmap(ct: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 5.5))
    sns.heatmap(ct, annot=False, cmap="YlGnBu", ax=ax)
    ax.set_title("Platform × Theme Discussion Heatmap")
    ax.set_xlabel("Theme")
    ax.set_ylabel("Platform")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    _save(fig, path)


def plot_engagement_hotspots(eng_df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    data = eng_df.sort_values("total_engagement", ascending=True)
    ax.barh(data.iloc[:, 0], data["total_engagement"], color="#D27D2C")
    ax.set_xlabel("Total Engagement")
    ax.set_title("Engagement-Weighted Cultural Hotspots")
    _save(fig, path)


def render_all_charts(
    *,
    theme_df: pd.DataFrame,
    sent_df: pd.DataFrame,
    by_theme: pd.DataFrame,
    by_platform: pd.DataFrame,
    trend: pd.DataFrame,
    tfidf_df: pd.DataFrame,
    heatmap: pd.DataFrame,
    engagement_df: pd.DataFrame,
    out_dir: str | Path,
) -> dict[str, str]:
    out = Path(out_dir)
    paths = {
        "theme_distribution": out / "theme_distribution.png",
        "sentiment_pie": out / "sentiment_distribution.png",
        "sentiment_by_theme": out / "sentiment_by_theme.png",
        "platform_sentiment": out / "platform_sentiment.png",
        "monthly_trend": out / "monthly_sentiment_trend.png",
        "wordcloud": out / "tfidf_wordcloud.png",
        "heatmap": out / "platform_theme_heatmap.png",
        "engagement": out / "engagement_hotspots.png",
    }
    plot_theme_distribution(theme_df, paths["theme_distribution"])
    plot_sentiment_pie(sent_df, paths["sentiment_pie"])
    plot_sentiment_by_theme(by_theme, paths["sentiment_by_theme"])
    plot_platform_sentiment(by_platform, paths["platform_sentiment"])
    plot_monthly_trend(trend, paths["monthly_trend"])
    plot_wordcloud(tfidf_df, paths["wordcloud"])
    plot_platform_theme_heatmap(heatmap, paths["heatmap"])
    plot_engagement_hotspots(engagement_df, paths["engagement"])
    return {k: str(v) for k, v in paths.items()}
