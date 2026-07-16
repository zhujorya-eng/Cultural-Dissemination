# 海外社交平台江苏文化语料文本挖掘报告

## 1. 数据概况
- 有效文本量：**105,000** 条
- 覆盖平台：Facebook, Instagram, Reddit, TripAdvisor, Twitter, YouTube
- 时间跨度：2022-01-01 00:26:00 ~ 2025-12-31 23:44:00
- 语料说明：合成海外社交风格英文语料（主题覆盖江苏文化核心意象），用于可复现的文本挖掘流程与热点/情感识别。

## 2. 受众关注热点
基于主题分布、互动加权热度、TF-IDF 关键词与 LDA 主题模型综合识别：

1. **淮扬菜/苏菜** — 帖文占比 16.1%，互动份额 16.0%
2. **古典园林** — 帖文占比 14.2%，互动份额 14.3%
3. **水乡古镇** — 帖文占比 12.9%，互动份额 13.2%
4. **南京历史文化** — 帖文占比 12.0%，互动份额 12.0%
5. **江南生活美学** — 帖文占比 10.1%，互动份额 10.2%
6. **丝绸与苏绣** — 帖文占比 9.0%，互动份额 8.8%
7. **昆曲艺术** — 帖文占比 7.9%，互动份额 7.7%
8. **大运河文化** — 帖文占比 7.0%，互动份额 7.0%

### 2.1 LDA 主题摘要（Top 5）

- Topic 3（文档占比 16.2%）：garden, heritage, jiangsu, pond, comparing, stand, stand factually, factually, site, heritage site, planning, include
- Topic 4（文档占比 14.7%）：jiangsu, photogenic, blew, refined, refined photogenic, culture, canal, house, tea, tea house, focus, overview
- Topic 6（文档占比 13.5%）：jiangnan, aesthetic, jiangnan aesthetic, show, show jiangnan, encounter, stunning, stunning encounter, culture, nanjing, jiangsu, city
- Topic 2（文档占比 12.5%）：jiangsu, silk, opera, embroidery, culture, heritage, intangible, festival, folk, lantern, unforgettable, jiangsu silk
- Topic 0（文档占比 12.0%）：authentic especially, especially, authentic, overseas, explained, ticket, guide, first, timer, guide explained, context first, context

### 2.2 高频关注词（TF-IDF）

jiangsu, culture, garden, jiangnan, canal, photogenic, local, jiangnan aesthetic, aesthetic, elegant, unforgettable, jiangsu culture, highlight jiangsu, highlight, cultural, museum, heritage, hospitality, lasting, impression

## 3. 情感倾向
- 正向：67.1%
- 中性：21.5%
- 负向：11.4%
- 平均情感分（VADER compound）：**0.312**

### 3.1 分主题情感

- 节庆与非遗: compound=0.452（正 78.8% / 中 11.1% / 负 10.1%）
- 淮扬菜/苏菜: compound=0.372（正 74.0% / 中 16.3% / 负 9.6%）
- 丝绸与苏绣: compound=0.353（正 70.6% / 中 21.5% / 负 7.8%）
- 昆曲艺术: compound=0.339（正 69.0% / 中 21.2% / 负 9.8%）
- 大运河文化: compound=0.338（正 69.2% / 中 20.8% / 负 10.0%）
- 江南生活美学: compound=0.327（正 66.5% / 中 25.3% / 负 8.2%）
- 古典园林: compound=0.308（正 65.5% / 中 24.6% / 负 9.9%）
- 南京历史文化: compound=0.252（正 61.6% / 中 24.6% / 负 13.8%）

### 3.2 分平台情感

- TripAdvisor: compound=0.364
- Facebook: compound=0.352
- YouTube: compound=0.305
- Twitter: compound=0.305
- Reddit: compound=0.299
- Instagram: compound=0.296

## 4. 主要发现

- 讨论量最高的文化热点为「淮扬菜/苏菜」，互动加权热度领先主题为「淮扬菜/苏菜」。
- 整体情感以正向为主，正向占比约 67.1%，负向约 11.4%。
- 情感最积极主题为「节庆与非遗」（compound=0.452），相对偏负主题为「文旅体验与服务」（compound=0.098）。
- 平台层面，TripAdvisor 的平均情感分最高（0.364），文旅体验与拥挤、导览服务相关讨论是负向情绪的主要来源。
- 美食、园林、丝绸刺绣等可视/可体验文化符号更易触发海外受众的正向传播。

## 5. 方法说明
- 预处理：小写化、去 URL/话题噪声、英文分词与词形还原、停用词过滤
- 热点识别：词频、TF-IDF、主题分布、互动加权、LDA（Latent Dirichlet Allocation）
- 情感分析：VADER（适合英文社交短文本）

图表目录：`outputs/figures`
数据表目录：`outputs/tables`
