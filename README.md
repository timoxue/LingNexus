# LingNexus

> 医药行业智能多代理系统与低代码平台

基于 AgentScope 框架构建的多智能体系统，支持 Claude Skills 兼容性，专为医药行业设计的竞品情报监控和自动化平台。

## 🎯 项目概述

LingNexus 采用 **Monorepo 架构**，包含两个核心子项目：

### 📦 Framework (`lingnexus-framework`)

多智能体框架，提供完整的 Agent 运行时环境：

- **Claude Skills 兼容**: 三层渐进式披露机制，高效管理 Token 使用
- **竞品情报监控**: 自动采集 ClinicalTrials.gov、CDE 等数据源
- **三层存储架构**: 原始数据 + 结构化数据库 + 向量搜索
- **统一命令行工具**: 一行命令完成所有操作

### 🌐 Platform (`lingnexus-platform`)

低代码可视化平台（开发中）：

- **Web 界面**: 基于 Vue 3 + FastAPI 的现代化界面
- **可视化编排**: 拖拽式 Skill 和 Agent 工作流设计
- **合规支持**: 符合 FDA 21 CFR Part 11 标准的审计日志

## 📁 项目结构

```
LingNexus/
├── packages/
│   ├── framework/              # Framework 包（v0.2.0）
│   │   ├── lingnexus/          # 核心代码
│   │   ├── skills/             # Claude Skills
│   │   ├── examples/           # 使用示例
│   │   ├── tests/              # Framework 测试
│   │   └── pyproject.toml      # 包配置
│   │
│   └── platform/              # Platform 包（v1.0.0）
│       ├── backend/           # FastAPI 后端
│       └── frontend/          # Vue 3 前端
│
├── docs/                      # 项目文档
├── scripts/                   # 开发脚本
├── config/                    # 配置文件
└── data/                      # 数据目录（运行时生成）
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆仓库
git clone https://github.com/timoxue/LingNexus
cd LingNexus

# 安装核心依赖
uv sync

# 配置 API Key
cp .env.example .env
# 编辑 .env 文件，添加你的 DASHSCOPE_API_KEY
```

### 2. 使用 Framework

#### 交互式对话

```bash
# 启动交互式对话
cd packages/framework
uv run python -m lingnexus.cli chat
```

#### 竞品监控

```bash
# 监控所有项目
uv run python -m lingnexus.cli monitor

# 监控特定项目
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# 查看监控状态
uv run python -m lingnexus.cli status

# 查询数据库
uv run python -m lingnexus.cli db --project "司美格鲁肽"
```

#### 语义搜索

```bash
# 在向量数据库中搜索
uv run python -m lingnexus.cli search "GLP-1"
```

### 3. 开发 Platform（可选）

```bash
# 后端开发
cd packages/platform/backend
uv sync
uv run uvicorn main:app --reload

# 前端开发
cd packages/platform/frontend
npm install
npm run dev
```

## 📚 文档

### 用户文档

- **[Framework 快速开始](docs/framework/getting-started.md)** - 入门指南
- **[Framework API 参考](docs/framework/api.md)** - 完整 API 文档
- **[Platform 用户手册](docs/platform/user-guide.md)** - Platform 使用指南
- **[Platform 部署指南](docs/platform/deployment.md)** - 生产部署说明

### 开发文档

- **[架构设计](docs/development/architecture.md)** - 系统架构详解
- **[开发环境搭建](docs/development/setup.md)** - 开发环境配置
- **[CLAUDE.md](CLAUDE.md)** - Claude Code 开发指南
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - v0.2.0 迁移指南

### 文档索引

- **[文档总览](docs/SUMMARY.md)** - 完整文档索引

## 🎯 核心功能

### 竞品情报监控

**数据源支持**：

| 数据源 | 状态 | 方法 | 说明 |
|--------|------|------|------|
| **ClinicalTrials.gov** | ✅ 生产就绪 | API v2 | 完全自动化 |
| **CDE** | ✅ 生产就绪 | Playwright | 反检测增强 |
| **Insight** | ⏳ 计划中 | - | 即将推出 |

**当前监控项目**：

- **司美格鲁肽 (Semaglutide)**
  - 适应症：糖尿病、减重、心血管、NASH
  - 关键词：semaglutide, GLP-1, Ozempic, Rybelsus, Wegovy
  - 竞争企业：诺和诺德、华东医药、丽珠集团、联邦制药

**三层存储架构**：

```
data/
├── raw/                    # 原始数据（HTML/JSON）
├── intelligence.db         # 结构化数据库（SQLite）
└── vectordb/               # 向量数据库（ChromaDB）
```

### Claude Skills 兼容

**三层渐进式披露**：

1. **元数据层** (~100 tokens/skill) - 技能名称和描述
2. **指令层** (~5k tokens/skill) - 完整 SKILL.md 内容
3. **资源层** - 参考文档、静态资源、执行脚本

**技能目录**：

```
packages/framework/skills/
├── external/           # Claude Skills 官方兼容格式
│   ├── docx/          # Word 文档生成
│   ├── pdf/           # PDF 处理
│   ├── pptx/          # PowerPoint 生成
│   └── ...
└── internal/           # 自定义技能
    └── intelligence/   # 竞品情报监控
        ├── clinical_trials_scraper.py
        └── cde_scraper.py
```

## 💻 开发指南

### 代码规范

```bash
# 格式化代码
uv run ruff format .

# 检查代码质量
uv run ruff check .

# 自动修复
uv run ruff check . --fix
```

### 测试

```bash
# 运行所有测试
cd packages/framework
uv run pytest
```

### 使用示例

```python
# 创建渐进式 Agent（推荐）
from lingnexus import create_progressive_agent

agent = create_progressive_agent(
    model_name="qwen-max",
    temperature=0.3,
)

# 使用 Agent
from agentscope.message import Msg
response = await agent(Msg(name="user", content="创建一个Word文档"))
```

## 🔧 系统要求

### 必需

- **Python**: 3.10+
- **uv**: Python 包管理器
- **DASHSCOPE_API_KEY**: 通义千问 API 密钥

### 监控系统所需

- **playwright**: CDE 爬虫依赖
- **Chromium**: 浏览器（自动下载，约 150MB）
- **tabulate**: 数据库展示

### 可选

- **ChromaDB**: 向量数据库（用于语义搜索）
- **Node.js**: 18.0+（某些技能需要）

## ❓ 常见问题

### Q: CDE 爬虫返回空白页面？

**解决方案**：使用 CLI 监控系统自动触发

```bash
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"
```

### Q: asyncio loop 错误？

**解决方案**：不要使用 `uv run` 运行 CDE 爬虫脚本

```bash
# ❌ 错误
uv run python cde_scraper_example.py

# ✅ 正确 - 通过 CLI
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"
```

### Q: 必须安装 ChromaDB 吗？

**A**: 不必须。ChromaDB 是可选依赖，用于语义搜索功能。未安装时系统自动降级，核心功能完全可用。

### Q: 如何获取 API Key？

**通义千问**：
1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 注册/登录账号
3. 创建 API Key

## 📝 更新日志

### v0.2.0 (2025-01-10)

**重大更新**：
- ✨ 重构为 Monorepo 架构
- ✨ 分离 Framework 和 Platform 包
- ✨ 完整文档体系
- ✨ 开发脚本支持

**新增功能**：
- ✨ CDE 爬虫（反检测版本）
- ✨ 人类行为模拟
- ✨ 智能重试机制

### v0.1.9 (2025-01-XX)

**初始版本**：
- ✨ AgentScope 多智能体系统
- ✨ Claude Skills 兼容
- ✨ 渐进式披露机制
- ✨ ClinicalTrials.gov 数据采集
- ✨ 三层存储架构

## 🤝 贡献

欢迎贡献！请先阅读开发文档：

1. 遵循代码规范（使用 ruff）
2. 添加测试覆盖新功能
3. 更新相关文档
4. 提交 Pull Request

## 📄 许可证

MIT License

## 🔗 相关链接

- **文档**: [docs/](docs/)
- **GitHub**: https://github.com/timoxue/LingNexus
- **问题反馈**: https://github.com/timoxue/LingNexus/issues

---

**LingNexus** - 医药行业智能多代理系统
