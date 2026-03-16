# LINGNEXUS — 全球医药专利多智能体情报挖掘系统

## 系统架构

```
飞书用户
   │
   │ [关键词: 专利|挖掘|靶向药|全球]
   ▼
┌─────────────────────────────────────────────────────────────┐
│                      OpenClaw Runtime                        │
│                                                             │
│  [Channel Binding: feishu] ──► AGENT: main (接待员)        │
│                                      │                      │
│                               触发工作流                    │
│                                      │                      │
│                    ┌─────────────────▼──────────────────┐   │
│                    │  Workflow: biopharma-scouting        │   │
│                    │                                      │   │
│                    │  Step 1: coach (查询拆解)            │   │
│                    │    └─► 写入 [Pending_Tasks] x5       │   │
│                    │                                      │   │
│                    │  Step 2: investigator (并行爬虫)     │   │
│                    │    ├─► T1 英文全球库  ─┐             │   │
│                    │    ├─► T2 中国药智网  ─┤             │   │
│                    │    ├─► T3 日本临床库  ─┼► [Raw_Evidence] │
│                    │    ├─► T4 欧洲/韩国库 ─┤             │   │
│                    │    └─► T5 行业媒体    ─┘             │   │
│                    │                                      │   │
│                    │  Step 3: validator (质检 断网)       │   │
│                    │    ├─► 通过 → [Validated_Assets]    │   │
│                    │    └─► 拒绝 → [Rejected_Evidence]   │   │
│                    │                                      │   │
│                    │  Step 4: deduplicator (消歧+简报)   │   │
│                    │    └─► Markdown 简报                 │   │
│                    └──────────────────────────────────────┘   │
│                                      │                      │
│                               返回 main                     │
└─────────────────────────────────────────────────────────────┘
   │
   ▼
飞书用户 (收到 Markdown 简报)
```

## 共享黑板数据流

```
[Pending_Tasks]    ← coach 写入
      ↓
[Raw_Evidence]     ← investigator 写入 (原文，无总结)
      ↓
[Validated_Assets] ← validator 写入 (is_met: true)
[Rejected_Evidence]← validator 写入 (is_met: false)
      ↓
deduplicator.output← deduplicator 生成 Markdown
```

## 文件结构

```
D:/Projects/LingNexus/
├── openclaw.config.json          # 全局路由 + 共享记忆 + 工作流注册
├── LINGNEXUS.md                  # 本文件
├── agents/
│   ├── main/
│   │   ├── SOUL.md               # 飞书接待员人格
│   │   └── AGENTS.md             # 接待员行为配置
│   ├── coach/
│   │   ├── SOUL.md               # 全球医药BD人格
│   │   └── AGENTS.md             # 查询拆解行为配置
│   ├── investigator/
│   │   ├── SOUL.md               # 多语种并行爬虫人格
│   │   └── AGENTS.md             # 并发采集行为配置
│   ├── validator/
│   │   ├── SOUL.md               # 全球专利质检官人格
│   │   └── AGENTS.md             # 硬性规则校验配置
│   └── deduplicator/
│       ├── SOUL.md               # 跨语种消歧专家人格
│       └── AGENTS.md             # 去重简报生成配置
└── workflows/
    └── biopharma-scouting.json   # 工作流详细规范（含黑板Schema）
```

## 质检硬性拦截规则 (Validator)

| 规则 | 条件 |
|------|------|
| 时间 | 2023-01-01 ~ 2026-12-31 |
| 技术类别 | PROTAC / Molecular Glue / LYTAC / ATTEC / AUTAC |
| 临床阶段 | Pre-Clinical / IND-Enabling / Phase I / Phase I/II |
| 地域 | 全球不限，必须提取 `origin_country` |

所有规则 AND 关系，一条不满足即拒绝。
