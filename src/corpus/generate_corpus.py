"""生成模拟海外社交平台江苏文化相关语料（约 10 万条）。

说明：真实平台 API 需密钥与合规授权，本模块基于江苏文化主题模板、
情感极性与平台风格参数，合成可复现的大规模英文语料，用于文本挖掘演示与研究流程验证。
"""

from __future__ import annotations

import argparse
import hashlib
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from tqdm import tqdm

# 主题标签 -> 关注热点维度
THEMES = {
    "classical_gardens": {
        "label_zh": "古典园林",
        "keywords": [
            "Suzhou gardens",
            "Humble Administrator's Garden",
            "Lingering Garden",
            "classical Chinese garden",
            "rockery and ponds",
            "UNESCO World Heritage",
        ],
        "weight": 0.14,
    },
    "kunqu_opera": {
        "label_zh": "昆曲艺术",
        "keywords": [
            "Kunqu opera",
            "Kun Opera",
            "Peony Pavilion",
            "traditional Chinese opera",
            "Jiangsu intangible heritage",
            "elegant singing",
        ],
        "weight": 0.08,
    },
    "huaiyang_cuisine": {
        "label_zh": "淮扬菜/苏菜",
        "keywords": [
            "Huaiyang cuisine",
            "Jiangsu food",
            "Yangzhou fried rice",
            "lion's head meatballs",
            "sweet and savory flavors",
            "Nanjing salted duck",
        ],
        "weight": 0.16,
    },
    "water_towns": {
        "label_zh": "水乡古镇",
        "keywords": [
            "Zhouzhuang",
            "Tongli water town",
            "Jiangnan water town",
            "stone bridges and canals",
            "boat rides",
            "ancient alleys",
        ],
        "weight": 0.13,
    },
    "grand_canal": {
        "label_zh": "大运河文化",
        "keywords": [
            "Grand Canal",
            "Beijing-Hangzhou Canal",
            "canal heritage",
            "riverside culture",
            "Jiangsu canal cities",
            "historic waterway",
        ],
        "weight": 0.07,
    },
    "silk_embroidery": {
        "label_zh": "丝绸与苏绣",
        "keywords": [
            "Suzhou embroidery",
            "Su Xiu",
            "silk workshops",
            "double-sided embroidery",
            "Jiangsu silk",
            "handcrafted silk art",
        ],
        "weight": 0.09,
    },
    "nanjing_heritage": {
        "label_zh": "南京历史文化",
        "keywords": [
            "Nanjing history",
            "Ming Xiaoling",
            "Confucius Temple Qinhuai",
            "city wall of Nanjing",
            "six dynasties culture",
            "Sun Yat-sen Mausoleum",
        ],
        "weight": 0.12,
    },
    "jiangnan_lifestyle": {
        "label_zh": "江南生活美学",
        "keywords": [
            "Jiangnan aesthetics",
            "tea houses",
            "scholar culture",
            "misty canals",
            "poetic lifestyle",
            "Wuxi Taihu scenery",
        ],
        "weight": 0.10,
    },
    "festivals_heritage": {
        "label_zh": "节庆与非遗",
        "keywords": [
            "Jiangsu festival",
            "dragon boat",
            "lantern festival",
            "intangible cultural heritage",
            "folk performance",
            "temple fair",
        ],
        "weight": 0.06,
    },
    "tourism_experience": {
        "label_zh": "文旅体验与服务",
        "keywords": [
            "Jiangsu travel",
            "tourist experience",
            "guided tour",
            "museum visit",
            "hospitality",
            "cultural trip planning",
        ],
        "weight": 0.05,
    },
}

PLATFORMS = {
    "Twitter": 0.28,
    "Reddit": 0.22,
    "Instagram": 0.18,
    "YouTube": 0.14,
    "TripAdvisor": 0.12,
    "Facebook": 0.06,
}

REGIONS = [
    "United States",
    "United Kingdom",
    "Canada",
    "Australia",
    "Germany",
    "France",
    "Japan",
    "South Korea",
    "Singapore",
    "Malaysia",
    "India",
    "Brazil",
    "Italy",
    "Spain",
    "Netherlands",
]

# 情感模板：positive / neutral / negative
SENTIMENT_TEMPLATES = {
    "positive": [
        "Absolutely loved discovering {kw} in Jiangsu — breathtaking and unforgettable!",
        "Just saw {kw} and I'm speechless. Jiangsu culture is so refined.",
        "Highly recommend experiencing {kw}. One of the highlights of my China trip.",
        "{kw} exceeded expectations. The craftsmanship and atmosphere are incredible.",
        "Fell in love with {kw}. Jiangsu's cultural soft power is real.",
        "As a visitor from overseas, {kw} felt authentic, warm and deeply aesthetic.",
        "Sharing my favorite moment with {kw} — pure Jiangnan vibes!",
        "Amazing documentation of {kw}. Makes me want to book a Jiangsu itinerary ASAP.",
        "The details of {kw} are stunning. Such elegance and historical depth.",
        "Best cultural experience this year: {kw} in Jiangsu. 10/10 would return.",
    ],
    "neutral": [
        "Visited {kw} during my Jiangsu trip. Crowded but informative.",
        "Reading about {kw} before going to Jiangsu — any tips from travelers?",
        "Documentary on {kw} explains the history well. Neutral overview of Jiangsu culture.",
        "Comparing {kw} with other Chinese heritage sites. Interesting similarities.",
        "Local guide talked about {kw}. Useful context for first-time visitors.",
        "Photo series featuring {kw}. Looks photogenic, wondering about ticket prices.",
        "Thread: thoughts on {kw} as part of Jiangsu cultural tourism?",
        "Saw a short clip about {kw}. Planning to include it if time allows.",
        "Museum panel on {kw} was factual and concise.",
        "Looking for English resources on {kw} and Jiangsu intangible heritage.",
    ],
    "negative": [
        "Disappointed by overcrowding around {kw}. Hard to appreciate the culture.",
        "Expected more explanation in English for {kw}. Felt lost as a foreign visitor.",
        "Commercialization around {kw} was a bit much. Less authentic than hoped.",
        "Long queues and unclear signage near {kw} ruined part of the experience.",
        "Tour felt rushed at {kw}. Barely had time to understand the history.",
        "Maintenance issues near {kw} were noticeable. Hope they improve preservation.",
        "Overpriced souvenirs linked to {kw}. Culture deserves better presentation.",
        "Audio guide for {kw} was outdated. Needs better storytelling for overseas guests.",
        "Too noisy around {kw} for such a refined cultural site.",
        "Mixed feelings about {kw} — beautiful idea, uneven visitor management.",
    ],
}

PLATFORM_PREFIX = {
    "Twitter": ["Just posted:", "Hot take:", "Travel note:", "Culture thread:"],
    "Reddit": [
        "r/travel:",
        "r/china:",
        "Genuine question:",
        "Trip report:",
    ],
    "Instagram": ["Photo dump:", "Today's muse:", "Captured this:", "Aesthetic stop:"],
    "YouTube": [
        "New vlog mention:",
        "Comment section:",
        "Watched a video on:",
        "Creator spotlight:",
    ],
    "TripAdvisor": [
        "Review:",
        "Visitor tip:",
        "Attraction note:",
        "Day trip review:",
    ],
    "Facebook": ["Shared post:", "Group discussion:", "Travel album:", "Event share:"],
}

# 主题默认情感先验（海外受众整体偏正向，文旅服务与拥挤类负向略高）
THEME_SENTIMENT_PRIORS = {
    "classical_gardens": (0.62, 0.28, 0.10),
    "kunqu_opera": (0.58, 0.32, 0.10),
    "huaiyang_cuisine": (0.68, 0.22, 0.10),
    "water_towns": (0.60, 0.25, 0.15),
    "grand_canal": (0.55, 0.35, 0.10),
    "silk_embroidery": (0.66, 0.26, 0.08),
    "nanjing_heritage": (0.57, 0.30, 0.13),
    "jiangnan_lifestyle": (0.64, 0.28, 0.08),
    "festivals_heritage": (0.59, 0.30, 0.11),
    "tourism_experience": (0.45, 0.30, 0.25),
}


def _weighted_choice(rng: random.Random, weight_map: dict[str, float]) -> str:
    keys = list(weight_map.keys())
    weights = [weight_map[k] for k in keys]
    return rng.choices(keys, weights=weights, k=1)[0]


def _choose_sentiment(rng: random.Random, theme: str) -> str:
    p, n, neg = THEME_SENTIMENT_PRIORS[theme]
    return rng.choices(["positive", "neutral", "negative"], weights=[p, n, neg], k=1)[0]


def _make_text(
    rng: random.Random,
    platform: str,
    theme: str,
    sentiment: str,
) -> tuple[str, str]:
    kw = rng.choice(THEMES[theme]["keywords"])
    template = rng.choice(SENTIMENT_TEMPLATES[sentiment])
    body = template.format(kw=kw)
    prefix = rng.choice(PLATFORM_PREFIX[platform])
    extras = [
        "",
        " #JiangsuCulture",
        " #VisitJiangsu",
        " #Jiangnan",
        " #ChinaTravel",
        f" Hashtags: #{theme.replace('_', '')}",
    ]
    text = f"{prefix} {body}{rng.choice(extras)}".strip()
    return text, kw


def generate_corpus(
    n_samples: int = 105000,
    seed: int = 42,
    start_date: str = "2022-01-01",
    end_date: str = "2025-12-31",
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """生成约 n_samples 条海外社交平台江苏文化语料。"""
    rng = random.Random(seed)
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    span_days = (end - start).days

    theme_weights = {k: v["weight"] for k, v in THEMES.items()}
    rows: list[dict] = []

    for i in tqdm(range(n_samples), desc="Generating corpus"):
        theme = _weighted_choice(rng, theme_weights)
        platform = _weighted_choice(rng, PLATFORMS)
        sentiment = _choose_sentiment(rng, theme)
        text, focal_kw = _make_text(rng, platform, theme, sentiment)
        created = start + timedelta(
            days=rng.randint(0, span_days),
            hours=rng.randint(0, 23),
            minutes=rng.randint(0, 59),
        )
        engagement = max(0, int(rng.lognormvariate(2.2, 1.1)))
        post_id = hashlib.md5(f"{i}-{seed}-{platform}".encode()).hexdigest()[:16]

        rows.append(
            {
                "post_id": post_id,
                "platform": platform,
                "region": rng.choice(REGIONS),
                "created_at": created.isoformat(sep=" ", timespec="seconds"),
                "theme": theme,
                "theme_zh": THEMES[theme]["label_zh"],
                "focal_keyword": focal_kw,
                "text": text,
                "engagement": engagement,
                "seed_sentiment": sentiment,  # 合成标签，仅用于评估；分析时以模型预测为准
            }
        )

    df = pd.DataFrame(rows)
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False, encoding="utf-8")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="生成江苏文化海外社交语料")
    parser.add_argument("--n", type=int, default=105000, help="语料条数")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--output",
        type=str,
        default="data/raw/jiangsu_overseas_social_corpus.csv",
    )
    args = parser.parse_args()
    df = generate_corpus(n_samples=args.n, seed=args.seed, output_path=args.output)
    print(f"Saved {len(df):,} rows -> {args.output}")
    print(df["theme_zh"].value_counts().head(10).to_string())


if __name__ == "__main__":
    main()
