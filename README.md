# LingNexus - 多智能体系统

基于 AgentScope 框架的多智能体系统，支持 Claude Skills 兼容，内置竞品情报监控功能。

## 特性

- 🤖 **多智能体协作** - 基于 AgentScope 框架的可扩展多智能体系统
- 🎯 **Claude Skills 兼容** - 完全兼容 Claude Skills 格式和渐进式披露机制
- 📊 **竞品情报监控** - 自动化采集和分析医药领域竞争情报数据
- 💾 **三层存储架构** - 原始数据、向量数据库、结构化数据库
- 🖥️ **统一 CLI 工具** - 一个入口，多种功能（交互式对话、监控、查询）
- 🔍 **语义搜索** - 基于向量数据库的智能搜索能力

## 项目结构

```
LingNexus/
├── lingnexus/              # 核心代码包
│   ├── agent/             # Agent 封装和工厂类
│   ├── cli/               # 统一命令行工具 ⭐
│   ├── config/            # 模型配置
│   ├── scheduler/         # 监控调度器 ⭐
│   ├── storage/           # 三层存储架构 ⭐
│   └── utils/             # 工具函数（Skill 加载器等）
│
├── skills/                 # Skills 目录
│   ├── external/          # Claude 格式的 Skills
│   └── internal/          # 自主开发的 Skills
│       └── intelligence/   # 竞品情报监控技能 ⭐
│
├── config/                 # 配置文件
│   └── projects_monitoring.yaml  # 监控项目配置 ⭐
│
├── examples/               # 使用示例
├── tests/                  # 测试脚本
├── scripts/                # 工具脚本
└── docs/                   # 文档
```

### 目录职责说明

| 目录 | 职责 | 面向 | 文件示例 |
|------|------|------|---------|
| **lingnexus/cli/** | 统一CLI入口，所有命令 | 用户 | `__main__.py` |
| **lingnexus/scheduler/** | 监控任务调度 | 系统 | `monitoring.py` |
| **lingnexus/storage/** | 三层数据存储 | 系统 | `raw.py`, `structured.py` |
| **skills/internal/intelligence/** | 监控爬虫技能 | 系统 | `clinical_trials_scraper.py` |
| **examples/** | 使用示例、演示代码 | 用户 | `monitoring_example.py` |
| **scripts/** | 工具脚本、自动化 | 开发者 | `load_claude_skills.py` |
| **tests/** | 测试脚本、验证 | 测试 | `test_skill_execution.py` |

## 快速开始

### 1. 安装依赖

**重要**: 本项目需要同时安装 Python 依赖和 Node.js 依赖。

#### Python 依赖（使用 uv）

```bash
# 安装 uv（如果尚未安装）
# Windows PowerShell:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/Mac:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 Python 项目依赖
uv sync

# 安装 Playwright 浏览器（监控功能需要）
uv run playwright install chromium
```

#### Node.js 依赖（用于 docx 等技能）

```bash
# 安装 Node.js 项目依赖
npm install

# 或使用 yarn
yarn install

# 或使用 pnpm
pnpm install
```

⚠️ **注意**: 某些技能（如 docx、pdf、pptx 等）依赖 Node.js 库，**必须**安装 Node.js 依赖才能正常使用。

### 2. 设置 API Key

创建 `.env` 文件（在项目根目录）：

```env
DASHSCOPE_API_KEY=your_api_key_here
```

或设置环境变量：

```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your_api_key"

# Linux/Mac
export DASHSCOPE_API_KEY="your_api_key"
```

### 3. 运行示例

#### 交互式对话（默认模式）

```bash
# 启动交互式对话
uv run python -m lingnexus.cli

# 或显式指定 chat 命令
uv run python -m lingnexus.cli chat --model qwen --mode test
```

在交互式界面中：
- 直接输入文本与 Agent 对话
- 输入 `/help` 查看帮助
- 输入 `/mode test` 切换到测试模式（自动执行代码）
- 输入 `/exit` 退出

#### 竞品情报监控

```bash
# 监控所有项目
uv run python -m lingnexus.cli monitor

# 监控特定项目
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# 查看监控状态
uv run python -m lingnexus.cli status

# 查询数据库
uv run python -m lingnexus.cli db
uv run python -m lingnexus.cli db --project "司美格鲁肽"
uv run python -m lingnexus.cli db --nct NCT06989203

# 语义搜索
uv run python -m lingnexus.cli search "司美格鲁肽肥胖症"
```

## 核心功能

### Phase 1: 基础功能（已完成 ✅）

- ✅ Agent 工厂类 - 快速创建配置好的 ReActAgent
- ✅ Skill 注册和加载 - 自动注册 Claude Skills
- ✅ 渐进式披露机制 - 智能 Token 管理，按需加载 Skills
- ✅ 模型配置模块 - 支持 Qwen 和 DeepSeek 模型
- ✅ 交互式测试工具 - 用户友好的命令行界面
- ✅ 统一 CLI 入口 - 一个工具，多种功能

### Phase 2: 竞品情报监控（已完成 ✅）

- ✅ 三层存储架构
  - 原始数据存储（HTML/JSON）
  - 结构化数据库（SQLAlchemy + SQLite）
  - 向量数据库（ChromaDB，可选）

- ✅ 数据采集系统
  - ClinicalTrials.gov 爬虫（API v2）✅
  - CDE 爬虫（Playwright）⚠️ 框架完成
  - Insight 爬虫（待实现）

- ✅ 监控调度器
  - YAML 配置文件管理
  - 多项目并发监控
  - 数据源优先级管理
  - 自动数据清洗和验证

- ✅ 统一 CLI 工具
  - 监控命令（monitor）
  - 状态查看（status）
  - 数据库查询（db）
  - 语义搜索（search）

## 使用示例

### 1. 渐进式披露 Agent（推荐）

```python
from lingnexus.agent import create_progressive_agent
from agentscope.message import Msg
import asyncio

# 创建支持渐进式披露的 Agent
agent = create_progressive_agent(
    model_name="qwen-max",
    temperature=0.3,
)

# 使用 Agent（会自动按需加载 Skills）
async def main():
    user_msg = Msg(name="user", content="请创建一个 Word 文档")
    response = await agent(user_msg)
    print(response.content)

asyncio.run(main())
```

**渐进式披露的优势**：
- ✅ Token 效率高：初始只加载元数据（~100 tokens/Skill）
- ✅ 智能按需加载：只在需要时加载完整指令（~5k tokens）
- ✅ 可扩展性强：支持大量 Skills，不会 token 爆炸

### 2. 竞品情报监控

```python
from lingnexus.scheduler.monitoring import DailyMonitoringTask
from lingnexus.storage.structured import StructuredDB

# 执行监控
task = DailyMonitoringTask()
results = task.run(project_names=["司美格鲁肽"])

# 查看结果
for project, data in results.items():
    print(f"{project}: {len(data)} 条数据")

# 查询数据库
db = StructuredDB()
trials = db.get_project_trials("司美格鲁肽", limit=20)

for trial in trials:
    print(f"{trial['nct_id']}: {trial['title']}")
    print(f"  状态: {trial['status']}")

db.close()
```

更多示例请查看：
- `examples/progressive_agent_example.py` - 渐进式披露示例
- `examples/monitoring_example.py` - 监控系统示例

## 监控的项目

系统当前监控 6 个重点项目：

1. **司美格鲁肽** (Semaglutide) - 糖尿病 GLP-1 受体激动剂 ⭐
2. **帕利哌酮微晶** - 精神分裂症长效注射剂
3. **注射用醋酸曲普瑞林微球** - 中枢性性早熟治疗
4. **JP-1366片** - 代号项目
5. **H001胶囊** - 华汇拓项目
6. **SG1001片剂** - 代号项目

配置文件：`config/projects_monitoring.yaml`

## CLI 命令速查

```bash
# ========================================
# 交互式对话（默认）
# ========================================
python -m lingnexus.cli
python -m lingnexus.cli chat --model qwen --mode test

# ========================================
# 监控管理
# ========================================
python -m lingnexus.cli monitor              # 监控所有项目
python -m lingnexus.cli monitor --project "司美格鲁肽"
python -m lingnexus.cli status              # 查看状态
python -m lingnexus.cli db                  # 查看数据库
python -m lingnexus.cli db --project "司美格鲁肽"
python -m lingnexus.cli db --nct NCT06989203
python -m lingnexus.cli search "关键词"
```

## Claude Skills 兼容性

### 设计理念

AgentScope 的 AgentSkill 设计借鉴了 Claude Skills 的理念，两者在格式上高度兼容：

- ✅ **相同的文件结构**：都使用 `SKILL.md` 作为主文件
- ✅ **相同的 YAML front matter**：都使用 `name` 和 `description` 字段
- ✅ **相同的资源目录结构**：`scripts/`, `references/`, `assets/`
- ✅ **相同的渐进式披露机制**：按需加载元数据、指令和资源

### 使用现有 Claude Skills

项目中的 `skills/external/` 目录包含 Claude 格式的 Skills，可以直接在 AgentScope 中使用，无需修改。

## 文档

详细文档请查看 [docs/README.md](docs/README.md)

### 快速导航

#### 核心文档
- 📖 [快速开始](docs/quick_start.md) - 快速上手指南
- 📖 [CLI 使用指南](docs/cli_guide.md) - 交互式工具使用
- 📖 [监控系统文档](docs/monitoring_system.md) - 竞品情报监控完整指南 ⭐

#### 开发文档
- 🛠️ [架构设计](docs/architecture.md) - 系统架构和设计
- 🛠️ [模型配置](docs/model_config.md) - 模型配置说明
- 🛠️ [API Key 管理](docs/api_key_guide.md) - API Key 设置和管理
- 🛠️ [Skill 集成](docs/skill_integration.md) - Claude Skills 集成

#### 实施总结
- 📊 [监控系统实施总结](docs/FINAL_IMPLEMENTATION_SUMMARY.md) - 实施总结 ⭐
- 📊 [项目清理总结](docs/PROJECT_CLEANUP_SUMMARY.md) - 项目清理报告 ⭐

#### 其他文档
- 📚 [测试指南](docs/testing.md) - 测试方法和指南
- 📚 [AgentScope Studio](docs/agentscope_studio_guide.md) - Studio 集成指南
- 📚 [安装指南](docs/INSTALLATION.md) - 详细安装说明

## 开发

### 运行测试

```bash
# 运行所有测试
uv run python tests/test_setup.py

# 运行单个测试
uv run python tests/test_api_key.py
uv run python tests/test_model_creation.py
uv run python tests/test_skill_registration.py
uv run python tests/test_agent_creation.py
uv run python tests/test_cli.py
```

### 代码质量

```bash
# 格式化代码
uv run ruff format .

# 检查代码
uv run ruff check .
```

### 测试监控系统

```bash
# 测试基础监控功能
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# 查看监控结果
uv run python -m lingnexus.cli db --project "司美格鲁肽"

# 检查系统状态
uv run python -m lingnexus.cli status
```

## 技术栈

- **框架**: AgentScope (多智能体系统)
- **模型**: 通义千问 (Qwen), DeepSeek (通过 DashScope API)
- **存储**: SQLite (结构化), ChromaDB (向量), 文件系统 (原始)
- **爬虫**: Playwright (浏览器自动化), Requests (HTTP)
- **CLI**: argparse (命令行解析)
- **数据处理**: SQLAlchemy (ORM), PyYAML (配置)

## 项目状态

### 完成度

| 模块 | 完成度 | 状态 |
|------|--------|------|
| 基础框架 | 100% | ✅ 完成 |
| 存储层 | 100% | ✅ 完成 |
| ClinicalTrials.gov爬虫 | 100% | ✅ 完成 |
| CDE爬虫 | 80% | ⚠️ 框架完成，需调试 |
| Insight爬虫 | 0% | ⏳ 待实现 |
| 监控任务 | 100% | ✅ 完成 |
| CLI工具 | 100% | ✅ 完成 |
| 配置管理 | 100% | ✅ 完成 |
| 测试 | 100% | ✅ 完成 |

**总体完成度**: **85%**

## 许可证

[添加许可证信息]

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 致谢

- [AgentScope](https://github.com/modelscope/agentscope) - 多智能体系统框架
- [Claude](https://claude.ai/) - Anthropic 的 AI 助手
- DashScope API - 模型服务支持
