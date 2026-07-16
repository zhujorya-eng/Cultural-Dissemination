"""情感倾向分析：VADER（适配海外英文社交文本）。"""

from __future__ import annotations

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def label_from_compound(compound: float, pos_th: float = 0.05, neg_th: float = -0.05) -> str:
    if compound >= pos_th:
        return "positive"
    if compound <= neg_th:
        return "negative"
    return "neutral"


def analyze_sentiment(df: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    analyzer = SentimentIntensityAnalyzer()
    out = df.copy()
    scores = out[text_col].map(lambda t: analyzer.polarity_scores(str(t)))
    out["sent_neg"] = scores.map(lambda d: d["neg"])
    out["sent_neu"] = scores.map(lambda d: d["neu"])
    out["sent_pos"] = scores.map(lambda d: d["pos"])
    out["sent_compound"] = scores.map(lambda d: d["compound"])
    out["sentiment"] = out["sent_compound"].map(label_from_compound)
    return out


def sentiment_overview(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["sentiment"].value_counts().rename_axis("sentiment").reset_index(name="count")
    counts["share"] = counts["count"] / counts["count"].sum()
    mean_compound = df["sent_compound"].mean()
    counts.attrs["mean_compound"] = mean_compound
    return counts


def sentiment_by_dimension(df: pd.DataFrame, dim: str) -> pd.DataFrame:
    g = (
        df.groupby([dim, "sentiment"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    totals = g.groupby(dim)["count"].transform("sum")
    g["share"] = g["count"] / totals
    compound = df.groupby(dim, as_index=False)["sent_compound"].mean().rename(
        columns={"sent_compound": "mean_compound"}
    )
    wide = g.pivot(index=dim, columns="sentiment", values="share").fillna(0.0).reset_index()
    return wide.merge(compound, on=dim, how="left").sort_values("mean_compound", ascending=False)


def monthly_sentiment_trend(df: pd.DataFrame) -> pd.DataFrame:
    tmp = df.copy()
    tmp["month"] = pd.to_datetime(tmp["created_at"]).dt.to_period("M").astype(str)
    trend = (
        tmp.groupby("month", as_index=False)
        .agg(
            posts=("post_id", "count"),
            mean_compound=("sent_compound", "mean"),
            positive_share=("sentiment", lambda s: (s == "positive").mean()),
            negative_share=("sentiment", lambda s: (s == "negative").mean()),
        )
        .sort_values("month")
    )
    return trend
