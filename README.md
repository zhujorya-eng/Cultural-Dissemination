# Cultural-Dissemination

中国文化海外传播研究项目集。

## 子项目

| 目录 | 说明 |
|------|------|
| [`research/`](research/) | 江苏文化海外社交平台数据采集与编码流水线 |
| VR 剧场 | 见分支 `cursor/kunqu-vr-theater-d2da` |

## 江苏文化数据采集（research）

从 YouTube、TikTok、Instagram 采集公开发布的江苏文化相关作品，进行纳入/排除过滤与机器+人工联合编码。

```bash
cd research
pip install -r requirements.txt
python scripts/run_collection.py --demo --platforms youtube tiktok instagram --queries "Kunqu" "Suzhou" "Huaiyang"
```

详见 [research/README.md](research/README.md)。
