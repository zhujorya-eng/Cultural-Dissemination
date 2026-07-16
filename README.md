# 江苏文化海外社交语料文本挖掘

运用文本挖掘技术，对海外社交平台 **10 万余条** 涉及江苏文化的语料进行分析，识别受众关注热点与情感倾向。

## 功能

- 构建可复现的大规模海外社交风格英文语料（覆盖 Twitter、Reddit、Instagram、YouTube、TripAdvisor、Facebook）
- 文本预处理（清洗、分词、词形还原、停用词）
- 关注热点识别：主题分布、词频、TF-IDF、互动加权、LDA 主题模型
- 情感倾向分析：VADER（适配英文社交短文本）
- 自动输出数据表、可视化图表与 Markdown 研究报告

## 主题覆盖

古典园林、昆曲、淮扬菜/苏菜、水乡古镇、大运河、丝绸与苏绣、南京历史文化、江南生活美学、节庆非遗、文旅体验等。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 一键生成约 10.5 万条语料并完成分析
python -m src.run_analysis --n 105000
```

仅重新分析已有语料：

```bash
python -m src.run_analysis --skip-generate
```

## 输出

| 路径 | 说明 |
|------|------|
| `data/raw/jiangsu_overseas_social_corpus.csv` | 原始语料 |
| `data/processed/corpus_with_sentiment.csv` | 预处理 + 情感标注结果 |
| `outputs/tables/` | 热点、情感、LDA 等汇总表 |
| `outputs/figures/` | 分布图、词云、热力图、趋势图 |
| `outputs/reports/jiangsu_culture_mining_report.md` | 分析报告 |

## 方法说明

1. **热点识别**：综合主题占比、互动量加权、TF-IDF 关键词与 LDA 潜在主题
2. **情感分析**：对每条文本计算 VADER compound 分数，并划分正/中/负
3. **交叉透视**：按主题、平台、地区与时间观察情感结构差异

## 语料说明

受平台 API 授权与合规限制，仓库默认使用**主题模板 + 平台风格参数**合成的可复现英文语料，用于验证完整文本挖掘流程。若接入真实采集数据，只需替换 `data/raw/` 下 CSV（需包含 `text`、`platform`、`created_at`、`engagement` 等字段），再执行 `--skip-generate` 即可。

## 项目结构

```
src/
  corpus/generate_corpus.py   # 语料生成
  mining/preprocess.py        # 预处理
  mining/hotspot.py           # 热点挖掘
  mining/sentiment.py         # 情感分析
  mining/pipeline.py          # 端到端流水线
  viz/charts.py               # 可视化
  run_analysis.py             # 入口
```
