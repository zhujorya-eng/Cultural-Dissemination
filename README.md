# 昆曲 VR 剧场 · 文化传播数字化方案

> Cultural Dissemination — 昆曲非遗的沉浸式 VR/MR 体验设计与 A/B 实验框架

## 项目概述

本项目为**昆曲 VR 剧场**提供完整的内容设计、技术实现路径与 A/B 测试方案，突破传统“演员演、观众看”的单向传播，采用 **MR-VR-MR 虚实切换**与**双轨表演者**机制，让受众成为虚实融合的参与者。

## 核心特性

- **叙事架构**：开场 MR 建立认知 → 中段 VR 穿越百年流变（戏园/茶楼/园林/数字剧场）→ 结尾 MR 闭环
- **交互设计**：虚拟乐器伴奏、茶馆就座观戏、园林对唱、场景漫游
- **技术路线**：多相机阵列 + 高斯泼溅场景重建、生成式 AI 沉浸空间、Meta Quest 3 终端
- **实验验证**：叙事方式 × 沉浸程度 × 文化阐释 三因子 A/B 设计

## 可交互 Web 体验（立即观看）

基于 **Three.js + WebXR** 实现的浏览器端昆曲 VR 剧场，完整呈现 MR-VR-MR 六场景流程。

### 快速启动

```bash
cd web
npm install
npm run dev
```

浏览器打开 `http://localhost:5173`，点击 **开始体验**。

### 操作方式

| 平台 | 操作 |
|------|------|
| **桌面浏览器** | 点击画面锁定鼠标 · WASD 移动 · 点击交互对象 · `N` 切换场景 |
| **VR 头显** | Meta Quest 3 等 WebXR 设备 · 点击「Enter VR」· 手柄射线交互 |
| **MR 模拟** | 开场/结尾场景调用摄像头作为 Passthrough 背景（需授权） |

### 场景与交互

1. **MR 开场** — 接取「游园帖」进入 VR
2. **清代戏园** — 拨弄琵琶为《牡丹亭》伴奏
3. **民国茶楼** — 选择茶席就座、品茗观戏
4. **园林实景** — 与杜丽娘对唱《游园·惊梦》
5. **数字剧场** — 粒子与水袖光带意象空间
6. **MR 结尾** — 生成「昆曲印记」卡片

### 生产构建

```bash
cd web && npm run build && npm run preview
```

构建产物位于 `web/dist/`，可部署至任意静态托管服务。

## 文档结构

| 文档 | 说明 |
|------|------|
| [内容设计](./docs/content-design.md) | 叙事架构、交互设计、双轨表演者、模块清单 |
| [技术架构](./docs/technical-architecture.md) | 高斯泼溅、MR-VR 切换、AI 集成、埋点 |
| [A/B 测试方案](./docs/ab-testing-design.md) | 变量操作化、指标、统计方法、8 组因子设计 |

## 实验配置示例

```
configs/
├── variant-g1-linear-passive-none.json      # 全对照组
└── variant-g8-interactive-participatory-guided.json  # 全实验组
```

## 参考

- XR 昆曲《游园·惊梦》双轨表演者机制
- Meta Quest 3 Passthrough MR
- 3D Gaussian Splatting 场景重建

## 许可

本项目用于文化传播与学术研究目的。
