"""演示/离线样本数据，用于验证编码流水线。"""

from __future__ import annotations

from ..models import CommentRecord, CultureWorkRecord


SAMPLE_WORKS: list[dict] = [
    {
        "platform": "youtube",
        "platform_id": "demo_kunqu_001",
        "url": "https://www.youtube.com/watch?v=demo_kunqu_001",
        "title": "Kunqu Opera 'The Peony Pavilion' - Full Performance | Jiangsu Traditional Culture",
        "description": "A complete Kunqu opera performance from Suzhou, Jiangsu. Kunqu is UNESCO intangible heritage originating from Jiangnan region.",
        "uploader": "China Culture Documentary",
        "tags": ["Kunqu", "Jiangsu", "Chinese opera", "UNESCO", "Peony Pavilion"],
        "view_count": 245000,
        "like_count": 5200,
        "comment_count": 380,
        "duration_sec": 3600,
        "subtitles": "Kunqu opera originated in Kunshan, Jiangsu province during the Ming dynasty...",
        "comments": [
            CommentRecord(author="Sarah M", text="Absolutely beautiful! I want to visit Suzhou gardens now.", like_count=42),
            CommentRecord(author="Kenji", text="Learned so much about Jiangsu culture. The water sleeves are mesmerizing.", like_count=28),
        ],
    },
    {
        "platform": "tiktok",
        "platform_id": "demo_suzhou_002",
        "url": "https://www.tiktok.com/@travelchina/video/demo_suzhou_002",
        "title": "Suzhou Gardens in 60 seconds 🌸 #Jiangsu #ChineseGarden #TravelChina",
        "description": "Humble Administrator Garden tour. Jiangsu travel vlog. #Suzhou #JiangsuCulture",
        "uploader": "travelchina_official",
        "tags": ["#Jiangsu", "#SuzhouGarden", "#TravelChina", "#ChineseGarden"],
        "view_count": 890000,
        "like_count": 95000,
        "comment_count": 1200,
        "duration_sec": 58,
        "comments": [
            CommentRecord(author="user123", text="This is so beautiful! Adding Jiangsu to my bucket list", like_count=15),
            CommentRecord(author="marco_p", text="Which garden is this? Tutorial please!", like_count=8),
        ],
    },
    {
        "platform": "instagram",
        "platform_id": "demo_huaiyang_003",
        "url": "https://www.instagram.com/reel/demo_huaiyang_003/",
        "title": "Huaiyang Cuisine Masterclass from Nanjing, Jiangsu 🦆",
        "description": "Nanjing salted duck and squirrel mandarin fish - classic Jiangsu cuisine explained step by step.",
        "uploader": "chef.li.cooking",
        "tags": ["#Huaiyang", "#JiangsuCuisine", "#Nanjing", "#ChineseFood"],
        "view_count": 120000,
        "like_count": 8500,
        "comment_count": 210,
        "duration_sec": 240,
        "comments": [
            CommentRecord(author="foodie_amy", text="Love Huaiyang food! The presentation is art.", like_count=22),
        ],
    },
    {
        "platform": "youtube",
        "platform_id": "demo_ad_excluded",
        "url": "https://www.youtube.com/watch?v=demo_ad_excluded",
        "title": "BUY NOW - Jiangsu Suning FC Jersey Discount #ad #sponsored",
        "description": "Use my code for 20% off CSL football merchandise. Affiliate link.",
        "uploader": "sports_deals",
        "tags": ["#ad", "Jiangsu FC", "football"],
        "view_count": 5000,
        "like_count": 50,
        "comment_count": 10,
        "duration_sec": 45,
        "comments": [],
    },
    {
        "platform": "youtube",
        "platform_id": "demo_dup_004",
        "url": "https://www.youtube.com/watch?v=demo_dup_004a",
        "title": "Kunqu Opera Peony Pavilion Jiangsu",
        "description": "Duplicate test record",
        "uploader": "China Culture Documentary",
        "tags": ["Kunqu", "Jiangsu"],
        "view_count": 100,
        "like_count": 5,
        "comment_count": 1,
        "duration_sec": 600,
        "comments": [],
    },
]


class DemoCollector:
    """返回内置样本，不依赖网络。"""

    def __init__(self, platform: str):
        self.platform = platform

    def search(self, query: str, search_date: str) -> list[CultureWorkRecord]:
        records: list[CultureWorkRecord] = []
        for item in SAMPLE_WORKS:
            if item["platform"] != self.platform:
                continue
            q = query.lower()
            blob = " ".join([
                item["title"], item["description"], " ".join(item["tags"])
            ]).lower()
            if q not in blob and not any(w in blob for w in q.split() if len(w) > 3):
                continue

            records.append(
                CultureWorkRecord(
                    search_date=search_date,
                    search_query=query,
                    platform=item["platform"],
                    url=item["url"],
                    platform_id=item["platform_id"],
                    title=item["title"],
                    description=item["description"],
                    uploader=item["uploader"],
                    tags=item["tags"],
                    view_count=item.get("view_count"),
                    like_count=item.get("like_count"),
                    comment_count=item.get("comment_count"),
                    duration_sec=item.get("duration_sec"),
                    subtitles=item.get("subtitles", ""),
                    comments=item.get("comments", []),
                )
            )
        return records
