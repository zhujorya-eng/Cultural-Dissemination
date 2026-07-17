# 江苏文化海外传播 — 社交平台数据采集

从 YouTube、TikTok、Instagram 采集**公开发布**的江苏文化相关作品，提取标题、字幕、标签与评论，经纳入/排除规则过滤后，进行机器与人工联合编码。

## 功能概览

| 模块 | 说明 |
|------|------|
| 关键词表 | 英文译名、拼音、主题标签组合（`config/keywords.yaml`） |
| 纳入/排除 | 广告、同名词、重复、语种不明过滤（`config/inclusion_exclusion.yaml`） |
| 三平台采集 | YouTube 搜索、TikTok/Instagram 标签页 |
| 机器编码 | 主题、发布主体、媒介形态、叙事、文化解释、互动、受众反馈 |
| 人工复核 | 导出 CSV 编码表供研究员填写 |

## 环境准备

```bash
cd research
pip install -r requirements.txt
```

依赖 `yt-dlp` 提取公开元数据；YouTube 推荐配置官方 API Key。

### 方式 A：演示模式（无需网络）

```bash
python scripts/run_collection.py --demo --platforms youtube tiktok instagram --queries "Kunqu" "Suzhou" "Huaiyang"
```

### 方式 B：YouTube Data API（推荐生产采集）

1. 在 [Google Cloud Console](https://console.cloud.google.com/) 启用 YouTube Data API v3
2. 创建 API Key 并设置环境变量：

```bash
export YOUTUBE_API_KEY="your-api-key"
python scripts/run_collection.py --platforms youtube --max-queries 10
```

### 方式 C：yt-dlp 直连（可能受平台反爬限制）

```bash
# 默认：YouTube，前 3 个检索词
python scripts/run_collection.py

# 指定平台
python scripts/run_collection.py --platforms youtube tiktok --max-queries 5
```

## 输出文件

运行后在 `research/data/` 生成：

- `raw_*.json` — 全部采集记录
- `included_*.json` — 通过筛选的纳入记录
- `excluded_*.json` — 被排除记录及原因
- `search_log_*.json` — 检索日期、平台、检索词
- `coding_review_*.csv` — 机器编码 + 人工复核列

## 编码维度

1. **作品主题** — 戏曲、工艺、园林、美食、历史等
2. **发布主体** — 官方机构、媒体、博主、艺术家等
3. **媒介形态** — 短/中/长视频、直播切片等
4. **叙事方式** — 体验、科普、表演、跨文化对比等
5. **文化解释** — 无/隐含/字幕/专家解读/双语
6. **互动设计** — 提问、挑战、教程、订阅引导等
7. **受众反馈** — 评论情感、互动热度、评论主题（机器预编码，需人工复核）

## 合规说明

- 仅采集**公开可访问**内容元数据
- 请遵守各平台服务条款与当地法律法规
- TikTok/Instagram 反爬策略较强，大批量采集可能受限
- 研究用途请引用原始链接并注明检索日期

## 目录结构

```
research/
├── config/
│   ├── keywords.yaml              # 关键词表
│   ├── inclusion_exclusion.yaml   # 纳入排除规则
│   └── coding_schema.yaml         # 编码模式
├── src/
│   ├── collectors/                # 平台采集器
│   ├── processors/                # 过滤、去重、语种
│   ├── coders/                    # 机器编码
│   └── pipeline.py                # 主流水线
├── scripts/
│   └── run_collection.py
└── data/                          # 输出目录
```
