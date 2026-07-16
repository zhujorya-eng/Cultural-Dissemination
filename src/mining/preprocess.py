"""文本预处理：清洗、分词、去停用词。"""

from __future__ import annotations

import re
from typing import Iterable

import nltk
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_MENTION_RE = re.compile(r"[@#]\w+")
_NON_ALPHA_RE = re.compile(r"[^a-zA-Z\s]")
_MULTI_SPACE_RE = re.compile(r"\s+")

# 领域保留词（避免被过度清洗）
DOMAIN_KEEP = {
    "jiangsu",
    "suzhou",
    "nanjing",
    "yangzhou",
    "wuxi",
    "jiangnan",
    "kunqu",
    "huaiyang",
    "zhouzhuang",
    "tongli",
    "taihu",
    "qinhuai",
    "unesco",
}


def ensure_nltk_data() -> None:
    packages = ["punkt", "punkt_tab", "stopwords", "wordnet", "omw-1.4"]
    for pkg in packages:
        try:
            nltk.data.find(
                {
                    "punkt": "tokenizers/punkt",
                    "punkt_tab": "tokenizers/punkt_tab",
                    "stopwords": "corpora/stopwords",
                    "wordnet": "corpora/wordnet",
                    "omw-1.4": "corpora/omw-1.4",
                }[pkg]
            )
        except LookupError:
            nltk.download(pkg, quiet=True)


def clean_text(text: str) -> str:
    text = str(text).lower()
    text = _URL_RE.sub(" ", text)
    text = _MENTION_RE.sub(" ", text)
    text = _NON_ALPHA_RE.sub(" ", text)
    text = _MULTI_SPACE_RE.sub(" ", text).strip()
    return text


def tokenize(text: str, stop: set[str] | None = None, lemmatizer: WordNetLemmatizer | None = None) -> list[str]:
    stop = stop or set()
    lemmatizer = lemmatizer or WordNetLemmatizer()
    tokens = word_tokenize(text)
    out: list[str] = []
    for tok in tokens:
        if len(tok) < 2:
            continue
        if tok in stop and tok not in DOMAIN_KEEP:
            continue
        lemma = lemmatizer.lemmatize(tok)
        if lemma in stop and lemma not in DOMAIN_KEEP:
            continue
        out.append(lemma)
    return out


def preprocess_dataframe(df: pd.DataFrame, text_col: str = "text") -> pd.DataFrame:
    ensure_nltk_data()
    stop = set(stopwords.words("english"))
    # 社交文本常见噪声词
    stop.update(
        {
            "just",
            "posted",
            "review",
            "comment",
            "section",
            "thread",
            "photo",
            "dump",
            "vlog",
            "mention",
            "hot",
            "take",
            "note",
            "trip",
            "report",
            "genuine",
            "question",
            "shared",
            "group",
            "discussion",
            "album",
            "event",
            "share",
            "creator",
            "spotlight",
            "watched",
            "video",
            "today",
            "muse",
            "captured",
            "aesthetic",
            "stop",
            "new",
            "attraction",
            "day",
            "visitor",
            "tip",
            "r",
            "travel",
            "china",
        }
    )
    lemmatizer = WordNetLemmatizer()

    out = df.copy()
    out["clean_text"] = out[text_col].map(clean_text)
    out["tokens"] = out["clean_text"].map(lambda t: tokenize(t, stop, lemmatizer))
    out["token_str"] = out["tokens"].map(lambda xs: " ".join(xs))
    out = out[out["token_str"].str.len() > 0].reset_index(drop=True)
    return out


def tokens_from_series(series: Iterable[str]) -> list[list[str]]:
    return [str(x).split() for x in series]
