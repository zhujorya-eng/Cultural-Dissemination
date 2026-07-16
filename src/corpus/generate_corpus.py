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

THEMES = {
    "classical_gardens": {
        "label_zh": "古典园林",
        "keywords": [
            "Suzhou gardens",
            "Humble Administrator's Garden",
            "Lingering Garden",
            "classical Chinese garden",
            "rockery and ponds",
            "UNESCO garden heritage",
        ],
        "motifs": [
            "moon gates",
            "white walls and dark tiles",
            "scholar rocks",
            "winding corridors",
            "lotus ponds",
            "garden landscaping philosophy",
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
            "water sleeve performance",
        ],
        "motifs": [
            "elegant singing",
            "flute accompaniment",
            "classical costumes",
            "stage choreography",
            "UNESCO listed opera",
            "poetic libretto",
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
            "Nanjing salted duck",
            "sweet and savory flavors",
        ],
        "motifs": [
            "knife skills",
            "delicate plating",
            "freshwater fish dishes",
            "tea-house dim sum",
            "seasonal ingredients",
            "banquet culture",
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
        "motifs": [
            "misty morning canals",
            "riverside houses",
            "lantern-lit evenings",
            "local handicraft stalls",
            "stone arch bridges",
            "slow boat travel",
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
        "motifs": [
            "cargo history",
            "canal museums",
            "wharf architecture",
            "shipping routes",
            "urban waterfront revival",
            "UNESCO canal corridor",
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
        "motifs": [
            "fine needlework",
            "silk threads",
            "floral patterns",
            "museum textile exhibits",
            "artisan demonstrations",
            "luxury silk scarves",
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
        "motifs": [
            "imperial tombs",
            "city wall cycling",
            "Qinhuai night cruise",
            "republican architecture",
            "museum collections",
            "historical storytelling",
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
        "motifs": [
            "ink wash vibes",
            "slow living",
            "calligraphy corners",
            "lakeside walks",
            "seasonal poetry",
            "courtyard cafes",
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
        "motifs": [
            "festive lanterns",
            "folk music",
            "community rituals",
            "seasonal celebrations",
            "handmade decorations",
            "local parade",
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
            "hospitality service",
            "cultural trip planning",
        ],
        "motifs": [
            "ticket lines",
            "English signage",
            "tour pacing",
            "visitor centers",
            "translation apps",
            "itinerary logistics",
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

POSITIVE_FRAMES = [
    "Absolutely loved {kw} in Jiangsu — {motif} made it unforgettable.",
    "{kw} blew me away. The {motif} feels so refined and photogenic.",
    "Highly recommend {kw}. {motif} is a highlight of Jiangsu culture.",
    "Fell for {kw}: elegant {motif} and warm local hospitality.",
    "As an overseas visitor, {kw} felt authentic — especially the {motif}.",
    "Stunning encounter with {kw}. {motif} shows Jiangnan aesthetics at its best.",
    "Best stop on my Jiangsu trip was {kw}; {motif} left a lasting impression.",
    "Charming and immersive: {kw} plus {motif}. Cultural soft power is real.",
]

NEUTRAL_FRAMES = [
    "Visited {kw} in Jiangsu. {motif} was interesting; crowds were moderate.",
    "Reading about {kw} and {motif} before travel — tips welcome.",
    "Documentary covers {kw} with focus on {motif}. Useful overview.",
    "Comparing {kw} with other heritage sites; {motif} stands out factually.",
    "Guide explained {kw} and {motif}. Good context for first-timers.",
    "Photo notes on {kw}: {motif} looks photogenic, checking ticket info.",
    "Planning whether to include {kw}. Curious about {motif} timing.",
    "Museum text on {kw} mentions {motif}. Concise and informative.",
]

NEGATIVE_FRAMES = [
    "Disappointed by overcrowding around {kw}. The {motif} was frustrating and hard to enjoy.",
    "Poor English guidance at {kw} left me confused; {motif} felt badly explained.",
    "Hate how commercial {kw} has become. The {motif} felt fake and overpriced.",
    "Terrible queues at {kw} ruined the visit; {motif} was rushed and stressful.",
    "Sad to see poor maintenance near {kw}. The {motif} looked neglected.",
    "Worst souvenir experience near {kw}. The {motif} presentation was disappointing.",
    "Too noisy and chaotic at {kw}; couldn't appreciate {motif} at all. Annoying.",
    "Bad visitor management at {kw}. The {motif} idea is nice but the execution failed.",
]

PLATFORM_PREFIX = {
    "Twitter": ["", "Travel note:", "Culture thread:", "Quick take:"],
    "Reddit": ["r/travel —", "r/china —", "Trip report:", "Question:"],
    "Instagram": ["", "Captured:", "Jiangnan diary:", ""],
    "YouTube": ["Video comment:", "Watched a vlog on", "Creator note:", ""],
    "TripAdvisor": ["Review:", "Visitor tip:", "Attraction note:", ""],
    "Facebook": ["Shared:", "Group chat:", "Album note:", ""],
}

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

HASHTAGS = [
    "",
    " #JiangsuCulture",
    " #VisitJiangsu",
    " #Jiangnan",
    " #ChinaTravel",
    " #CulturalHeritage",
]


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
    meta = THEMES[theme]
    kw = rng.choice(meta["keywords"])
    motif = rng.choice(meta["motifs"])
    frames = {
        "positive": POSITIVE_FRAMES,
        "neutral": NEUTRAL_FRAMES,
        "negative": NEGATIVE_FRAMES,
    }[sentiment]
    body = rng.choice(frames).format(kw=kw, motif=motif)
    prefix = rng.choice(PLATFORM_PREFIX[platform]).strip()
    text = f"{prefix} {body}{rng.choice(HASHTAGS)}".strip()
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
                "seed_sentiment": sentiment,
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
