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

低代码可视化平台：

- **Web 界面**: 基于 Vue 3 + FastAPI 的现代化界面
- **技能市场**: Skills Marketplace 2.0 - 发现、试用、收藏、评分技能
- **一键创建**: 从技能一键创建 Agent
- **权限管理**: 支持私有/团队/公开三种共享范围
- **代理管理**: Agent 配置、执行、历史记录
- **监控数据**: ClinicalTrials、CDE 等数据可视化

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
│   └── platform/              # Platform 包（v1.0.2）
│       ├── backend/           # FastAPI 后端
│       └── frontend/          # Vue 3 前端
│
├── docs/                      # 项目文档
├── scripts/                   # 开发脚本
├── config/                    # 配置文件
└── data/                      # 数据目录（运行时生成）
```

## 🚀 快速开始

> 💡 **新用户？** 查看 [START_GUIDE.md](START_GUIDE.md) 获取详细的一键启动指南

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

### 3. 使用 Platform

#### ⚠️ 架构说明

**当前架构**（临时方案）：
- Backend 直接导入 Framework 代码
- 适合：开发、测试、单机部署
- 生产环境计划使用微服务架构（详见 [architecture.md](docs/architecture.md#platform-与-framework-架构)）

#### 启动服务

```bash
# 后端（端口 8000）
cd packages/platform/backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 前端（端口 5173，新终端窗口）
cd packages/platform/frontend
npm install
npm run dev
```

**访问地址**:
- 前端界面: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- AgentScope Studio: http://localhost:3000（自动启动）

📖 **详细启动指南**: [START_GUIDE.md](START_GUIDE.md)

#### Platform 功能

**认证系统** (`/login`, `/register`):
- 用户注册和登录
- JWT Token 认证
- 角色权限管理（管理员、普通用户）

**技能市场** (`/marketplace`):
- 🔍 浏览 19+ 公开技能（无需登录）
- 🏷️ 搜索、过滤、排序技能
  - 按类别：外部/内部
  - 按范围：公开/团队/私有
  - 按官方：官方认证技能
- 🧪 试用技能（立即测试效果，无需登录）
- ⭐ 收藏和评分技能
- 🚀 一键从技能创建 Agent

**Agent 管理** (`/agents`):
- ➕ 创建和配置 Agent
  - 选择模型（Qwen Max/Plus/Turbo、DeepSeek Chat/Coder）
  - 配置温度参数
  - 关联多个技能
  - 自定义系统提示
- ✏️ 编辑和删除 Agent
- ▶️ 执行 Agent
  - 发送消息给 Agent
  - 实时查看执行结果
  - 查看 Token 使用和执行时间
- 📜 查看执行历史
  - 状态追踪
  - 详细的输入/输出消息
  - 错误信息展示

**技能同步** (`/skills`):
- 🔄 从 Framework 自动导入技能
- 📊 同步统计（创建、更新、跳过）
- ⚙️ 管理员专属功能

**技能创建器** (`/skill-creator`):
- 🤖 AI 驱动的技能创建助手（唯一版本）
- 📝 4 维度渐进式问答流程
  - 核心价值：技能解决什么问题
  - 使用场景：典型工作流程
  - 别名偏好：简洁自然的调用方式
  - 边界限制：明确技能的适用范围
- 🎯 LLM 智能评分系统（0-100 分）
  - 评分 ≥ 91：进入下一维度
  - 评分 < 91：智能追问并提供建议
- 📊 自动生成技能元数据
  - 技能名称、类别、别名
  - 目标用户、建议能力
  - 合规要求、资源清单
- 🔗 AgentScope Studio 集成
  - 实时监控 LLM 对话
  - 可视化评分过程
  - 调试和优化提示词
- 🧹 **代码优化**：清理了 ~2,400 行未使用代码

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

### v1.0.2 (2025-01-19)

**Platform 新功能**：
- ✨ Skill Creator Agent
  - AI 驱动的技能创建助手
  - 4 维度渐进式问答流程
  - LLM 智能评分系统（0-100 分）
  - 自动生成技能元数据
  - AgentScope Studio 集成
- 🔧 端口配置优化
  - 后端：8000 端口
  - 前端：5173 端口

**代码优化**：
- 🧹 删除旧版 Skill Creator 系统（~2,400 行代码）
  - 后端：`skill_creator.py` (301 行)、`skill_creator_service.py` (705 行)
  - 前端：7 个未使用组件、1 个未使用的 store
- ✨ 简化 API 客户端
  - `skillCreator.ts` 从 372 行精简到 152 行
  - 统一为 Agent 驱动的单一系统
- 🎁 清理项目结构
  - 删除嵌套的空目录 `packages/packages/`
  - 更清晰的代码架构

**技术改进**：
- 🐛 修复 JSON 响应解析问题（ContentBlock 格式提取）
- 🐛 优化 ReActAgent 配置（温度 0.4 → 0.1）
- 🐛 修复 Msg 构造函数缺少 role 参数
- 📝 完善文档和 API 说明

### v1.0.1 (2025-01-12)

**Platform 功能增强**：
- ✨ Agent 创建功能
  - 技能多选（可搜索、可过滤）
  - 完整的配置选项（模型、温度、Token、系统提示）
  - Agent 列表显示关联技能
- ✨ Agent 执行功能
  - 实时执行对话框
  - 执行结果展示（输出、错误、Token、时间）
  - 完整的执行历史记录
  - 点击查看执行详情
- ✨ 技能同步功能
  - 从 Framework 自动导入技能
  - 同步状态和统计
  - 强制更新选项
- ✨ Marketplace 快速创建
  - 从技能一键创建 Agent
  - 预填充配置信息
  - 创建后跳转到 Agent 列表
- ⚠️ 架构文档更新
  - 说明当前临时方案的优缺点
  - 提供未来微服务架构的迁移计划

**Bug 修复**：
- 🐛 修复 JWT Token 认证问题（sub 字段类型）
- 🐛 修复 Agent 创建时技能数据类型问题
- 🐛 修复 Agent 列表的 Pydantic 验证错误
- 🐛 修复 Agent 执行时的数据库字段问题

### v1.0.0 (2025-01-11)

**Platform 首个功能版本**：
- ✨ Skills Marketplace 2.0 - 技能市场
  - 技能浏览、搜索、过滤、排序
  - 技能详情页
  - 试用技能（无需登录）
  - 收藏和评分技能
  - 一键从技能创建 Agent
- ✨ 权限管理系统
  - 私有/团队/公开三种共享范围
  - 部门隔离
  - 用户角色和权限
- ✨ Agent 执行功能
  - 连接到 Framework 的 Progressive Agent
  - 实时执行结果展示
  - 执行历史记录
- ✨ 完整的前端界面
  - Vue 3 + TypeScript + Element Plus
  - Pinia 状态管理
  - 响应式设计

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
