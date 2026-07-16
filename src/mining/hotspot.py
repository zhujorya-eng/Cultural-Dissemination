"""受众关注热点识别：关键词、TF-IDF、LDA 主题模型。"""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


def top_keywords(df: pd.DataFrame, top_n: int = 40) -> pd.DataFrame:
    counter: Counter[str] = Counter()
    for tokens in df["tokens"]:
        counter.update(tokens)
    rows = [{"keyword": k, "frequency": v} for k, v in counter.most_common(top_n)]
    return pd.DataFrame(rows)


def tfidf_keywords(df: pd.DataFrame, top_n: int = 30, max_features: int = 5000) -> pd.DataFrame:
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        min_df=5,
        max_df=0.85,
    )
    matrix = vectorizer.fit_transform(df["token_str"])
    scores = np.asarray(matrix.mean(axis=0)).ravel()
    terms = np.array(vectorizer.get_feature_names_out())
    order = scores.argsort()[::-1][:top_n]
    return pd.DataFrame(
        {
            "term": terms[order],
            "mean_tfidf": scores[order],
        }
    )


def theme_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if "theme_zh" in df.columns:
        counts = df["theme_zh"].value_counts().rename_axis("theme").reset_index(name="count")
    else:
        counts = df["theme"].value_counts().rename_axis("theme").reset_index(name="count")
    counts["share"] = counts["count"] / counts["count"].sum()
    return counts


def platform_theme_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    theme_col = "theme_zh" if "theme_zh" in df.columns else "theme"
    ct = pd.crosstab(df["platform"], df[theme_col])
    return ct


def fit_lda(
    df: pd.DataFrame,
    n_topics: int = 8,
    max_features: int = 4000,
    max_iter: int = 20,
    random_state: int = 42,
) -> dict[str, Any]:
    vectorizer = CountVectorizer(
        max_features=max_features,
        min_df=8,
        max_df=0.8,
        ngram_range=(1, 2),
    )
    x = vectorizer.fit_transform(df["token_str"])
    lda = LatentDirichletAllocation(
        n_components=n_topics,
        learning_method="batch",
        max_iter=max_iter,
        random_state=random_state,
        n_jobs=1,
    )
    doc_topic = lda.fit_transform(x)
    feature_names = vectorizer.get_feature_names_out()

    topic_rows = []
    for topic_idx, topic in enumerate(lda.components_):
        top_idx = topic.argsort()[::-1][:12]
        words = [feature_names[i] for i in top_idx]
        weights = [float(topic[i]) for i in top_idx]
        topic_rows.append(
            {
                "topic_id": topic_idx,
                "top_terms": ", ".join(words),
                "term_list": words,
                "weight_list": weights,
                "doc_share": float((doc_topic.argmax(axis=1) == topic_idx).mean()),
            }
        )

    topic_df = pd.DataFrame(topic_rows).sort_values("doc_share", ascending=False)
    assigned = doc_topic.argmax(axis=1)
    return {
        "model": lda,
        "vectorizer": vectorizer,
        "doc_topic": doc_topic,
        "topic_summary": topic_df.reset_index(drop=True),
        "assigned_topic": assigned,
    }


def engagement_weighted_hotspots(df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    """按互动量加权的主题热度。"""
    theme_col = "theme_zh" if "theme_zh" in df.columns else "theme"
    g = (
        df.groupby(theme_col, as_index=False)
        .agg(posts=("post_id", "count"), total_engagement=("engagement", "sum"), avg_engagement=("engagement", "mean"))
        .sort_values("total_engagement", ascending=False)
    )
    g["engagement_share"] = g["total_engagement"] / g["total_engagement"].sum()
    return g.head(top_n)
