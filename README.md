# LINGNEXUS

> 全球医药专利多智能体情报挖掘系统
> Global Pharmaceutical Patent Intelligence Mining System with Multi-Agent Architecture

[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.3.13-blue)](https://openclaw.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

LINGNEXUS 是一个基于多智能体架构的医药专利情报挖掘系统，专注于靶向蛋白降解剂（PROTAC、Molecular Glue 等）的全球专利和临床早期项目情报收集。

## ✨ 核心特性

- 🤖 **5个专业智能体协作**：查询拆解、数据采集、质量校验、去重简报
- 🌍 **多语种支持**：中文、英文、日文、韩文、德文并行搜索
- 🔍 **全球数据源覆盖**：USPTO、CNIPA、J-PlatPat、Espacenet、药智网等
- ✅ **严格质量控制**：4维硬性规则校验（时间、技术、阶段、地域）
- 🧬 **跨语种去重**：智能识别同一药物的多语种别名
- 📊 **高管级简报**：自动生成结构化 Markdown 报告
- 🌐 **三层搜索架构**：PubMed 医学数据库 + OpenClaw Browser 网页抓取 + 智能数据清洗
- 🚀 **智能启动**：首次安装依赖，后续快速启动（< 10秒）

## 🏗️ 系统架构

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
└─────────────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 前置要求

- Docker & Docker Compose
- Git
- 有效的 API 密钥：
  - Anthropic Claude Code OAuth Token
  - （可选）Moonshot AI / Google AI / OpenRouter API Keys
  - （可选）NCBI Email（用于 PubMed API）

### 安装步骤

1. **克隆仓库**

```bash
git clone git@github.com:timoxue/LingNexus.git
cd LingNexus
```

2. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填入真实的 API Keys
```

3. **构建自定义镜像**（首次运行）

```bash
# Windows PowerShell
.\scripts\Build-Image.ps1

# Linux/Mac
bash scripts/build-image.sh
```

4. **注册智能体**

```bash
docker compose --profile setup run --rm setup
```

5. **启动系统**

```bash
docker compose up gateway -d
```

> 💡 **首次启动**：需要 2-3 分钟安装浏览器依赖（Python + Playwright Chromium + Xvfb）
> 💡 **后续启动**：< 10 秒快速启动

6. **验证运行**

```bash
# 查看启动日志
docker logs lingnexus-gateway --tail 50

# 检查健康状态
docker compose ps
```

## 📖 使用指南

### Investigator 三层搜索架构

Investigator Agent 采用三层架构设计，支持多数据源智能搜索：

```
┌─────────────────────────────────────────────────────────────┐
│  L0: 全局搜索技能 (global_search_skill.py)                  │
│  统一搜索入口，路由到不同的数据源                             │
└────────────────┬────────────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
┌───────▼──────┐  ┌──────▼────────┐
│ L1: 引擎层    │  │ L1: 引擎层     │
│ medical_engine│  │ browser_engine │
│ (PubMed API) │  │ (OpenClaw)    │
└───────┬──────┘  └──────┬────────┘
        │                 │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ L2: 数据清洗层   │
        │ data_cleaner.py │
        │ (HTML → Text)   │
        └─────────────────┘
```

**测试三层架构**：

```bash
# 测试 PubMed 搜索
docker compose exec gateway bash -c \
  "cd /workspace/skills && python3 global_search_skill.py 'PROTAC degradation' pubmed"

# 测试浏览器抓取
docker compose exec gateway bash -c \
  "cd /workspace/skills && python3 global_search_skill.py 'https://example.com' general_web"
```

### 测试完整工作流

```bash
# 执行端到端测试
./test-complete-workflow.sh
```

### 测试单个智能体

```bash
# 测试 coach agent
docker exec lingnexus-gateway bash -c \
  'cd /workspace && node /app/openclaw.mjs agent --agent coach --local -m "测试查询"'

# 测试 validator agent
docker exec lingnexus-gateway bash -c \
  'cd /workspace && node /app/openclaw.mjs agent --agent validator --local -m "测试验证"'
```

### API 稳定性测试

```bash
./test-api-stability.sh
```

## 🤖 智能体说明

| Agent | 角色 | 职责 | 模型 |
|-------|------|------|------|
| **main** | 接待员 | 接收用户查询，触发工作流，返回简报 | Claude Haiku 4.5 |
| **coach** | 战略顾问 | 将查询拆解为5条多语种搜索任务 | Claude Sonnet 4.6 |
| **investigator** | 并行爬虫 | 并发采集全球数据源的原始证据 | Claude Haiku 4.5 |
| **validator** | 质检官 | 执行4维硬性规则校验（物理断网） | Claude Sonnet 4.6 |
| **deduplicator** | 去重专家 | 跨语种消歧，生成 Markdown 简报 | Claude Sonnet 4.6 |

## 🔧 配置说明

### 浏览器环境

系统使用 **Playwright Chromium** + **OpenClaw Browser** 实现网页抓取：

- **浏览器位置**: `/home/node/.cache/ms-playwright/chromium-1208`
- **浏览器大小**: 364MB (Chromium) + 254MB (Headless Shell)
- **虚拟显示**: Xvfb 运行在 `:99` 显示器
- **配置**: `noSandbox: true`（容器环境必需）

**浏览器功能测试**：

```bash
# 检查浏览器状态
docker compose exec gateway bash -c \
  "su - node -c 'cd /app && node openclaw.mjs browser status'"

# 打开网页
docker compose exec gateway bash -c \
  "export DISPLAY=:99 && su - node -c 'export DISPLAY=:99 && cd /app && node openclaw.mjs browser open https://example.com'"

# 获取页面快照
docker compose exec gateway bash -c \
  "export DISPLAY=:99 && su - node -c 'export DISPLAY=:99 && cd /app && node openclaw.mjs browser snapshot'"
```

### 环境变量

关键环境变量说明（详见 `.env.example`）：

```bash
# Anthropic Claude Code OAuth Token
ANTHROPIC_OAUTH_TOKEN=cr_xxxxxxxx...

# 代理端点（如使用本地代理）
ANTHROPIC_BASE_URL=http://host.docker.internal:18790

# 第三方模型 API Keys（可选）
MOONSHOT_API_KEY=sk-xxxxxxxx...
GOOGLE_API_KEY=AIzaxxxxxxxx...

# PubMed API（可选，用于医学文献检索）
NCBI_EMAIL=your.email@example.com
```

### 质检规则

Validator 执行的硬性拦截规则（AND 逻辑）：

1. **时间范围**：2023-01-01 ~ 2026-12-31
2. **技术类别**：PROTAC / Molecular Glue / LYTAC / ATTEC / AUTAC
3. **临床阶段**：Pre-Clinical / IND-Enabling / Phase I / Phase I/II
4. **地域**：必须提取研发主体所在国家（ISO 3166-1 alpha-2）

## 📊 测试报告

系统已通过完整的端到端测试：

- ✅ **API 稳定性测试**：100% 成功率（详见 `API_STABILITY_REPORT.md`）
- ✅ **端到端工作流测试**：所有智能体正常协作（详见 `E2E_TEST_REPORT.md`）
- ✅ **配置完整性检查**：所有配置文件验证通过（详见 `AGENT_CONFIG_REVIEW.md`）

## 📚 文档

- [系统架构](LINGNEXUS.md) - 详细的系统设计和数据流
- [智能体配置审查](AGENT_CONFIG_REVIEW.md) - 所有智能体的配置分析
- [端到端测试报告](E2E_TEST_REPORT.md) - 完整的测试结果
- [工作流修复报告](WORKFLOW_FIX_REPORT.md) - 工作流实现细节
- [部署指南](DEPLOYMENT.md) - 生产环境部署说明

## 🛠️ 开发

### 项目结构

```
LingNexus/
├── agents/                      # 智能体配置
│   ├── main/                   # 接待员
│   ├── coach/                  # 查询拆解器
│   ├── investigator/           # 并行爬虫（三层架构）
│   ├── validator/              # 质检官
│   └── deduplicator/           # 去重专家
├── skills/                      # Investigator 技能库
│   ├── engines/                # L1 引擎层
│   │   ├── medical_engine.py  # PubMed 医学数据库
│   │   └── browser_engine.py  # OpenClaw Browser 网页抓取
│   ├── scrapers/               # L2 数据清洗层
│   │   └── data_cleaner.py    # HTML → 纯文本
│   └── global_search_skill.py  # L0 统一搜索入口
├── workflows/                   # 工作流定义
│   └── biopharma-scouting.json
├── scripts/                     # 脚本工具
│   ├── Build-Image.ps1         # 构建自定义镜像（Windows）
│   ├── build-image.sh          # 构建自定义镜像（Linux/Mac）
│   ├── register-agents.sh      # 智能体注册
│   ├── Start-LingNexus.ps1     # 启动脚本
│   └── Test-LingNexus.ps1      # 测试脚本
├── Dockerfile.lingnexus         # 自定义 Docker 镜像
├── openclaw.config.json         # 系统配置
├── docker-compose.yml           # Docker 配置
└── .env.example                 # 环境变量模板
```

### 添加新的智能体

1. 在 `agents/` 目录创建新的智能体文件夹
2. 创建 `SOUL.md`（人格定义）和 `AGENTS.md`（行为配置）
3. 在 `openclaw.config.json` 中注册智能体
4. 更新工作流定义（如需要）

## 🔧 故障排除

### 浏览器环境问题

**问题：浏览器启动失败**

```bash
# 检查 Xvfb 是否运行
docker compose exec gateway bash -c "ps aux | grep Xvfb"

# 手动启动 Xvfb
docker compose exec gateway bash -c "Xvfb :99 -screen 0 1280x1024x24 &"

# 检查浏览器状态
docker compose exec gateway bash -c \
  "su - node -c 'cd /app && node openclaw.mjs browser status'"
```

**问题：首次启动时间过长**

首次启动需要安装浏览器依赖（2-3分钟），这是正常的。后续启动会自动跳过安装，< 10秒完成。

```bash
# 查看安装进度
docker compose logs gateway -f
```

### Docker 权限问题（Windows）

如果遇到 "read-only file system" 错误：

```bash
# 已修复：docker-compose.yml 已配置为可写模式
# 如果仍有问题，确保容器以 root 用户运行
docker compose down
docker compose up gateway -d
```

详见 [DOCKER_PERMISSION_FIX.md](DOCKER_PERMISSION_FIX.md)

## 🔒 安全说明

- ⚠️ **不要提交 `.env` 文件**：包含真实的 API Keys
- ⚠️ **使用 `.env.example` 作为模板**：仅包含占位符
- ⚠️ **检查 `.gitignore`**：确保敏感文件被排除
- ⚠️ **root 用户**：仅在开发环境使用，生产环境需配置专用用户

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [OpenClaw](https://openclaw.io) - 多智能体框架
- [Anthropic Claude](https://www.anthropic.com) - AI 模型支持
- [Playwright](https://playwright.dev) - 浏览器自动化
- 所有贡献者和测试者

## 🛠️ 技术栈

- **AI 框架**: OpenClaw 2026.3.13
- **AI 模型**: Claude Opus 4.6, Sonnet 4.6, Haiku 4.5
- **容器化**: Docker & Docker Compose
- **浏览器**: Playwright Chromium 1208
- **虚拟显示**: Xvfb
- **Python 库**: beautifulsoup4, biopython
- **数据源**: PubMed, USPTO, CNIPA, J-PlatPat, Espacenet

## 📧 联系方式

- GitHub Issues: [https://github.com/timoxue/LingNexus/issues](https://github.com/timoxue/LingNexus/issues)
- 项目维护者: [@timoxue](https://github.com/timoxue)

---

<div align="center">
  <sub>Built with ❤️ using Claude Sonnet 4.6</sub>
</div>
