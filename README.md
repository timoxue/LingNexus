# LingNexus

基于 AgentScope 框架构建的多智能体系统，支持 Claude Skills 兼容性，具有竞品情报监控功能，可自动采集医药行业数据。

## 特性

- **多智能体系统**: 基于 AgentScope 框架构建
- **Claude Skills 兼容**: 渐进式披露机制，高效管理 Token 使用
- **竞品情报监控**: 自动从多个数据源采集竞争情报
- **三层存储架构**: 原始数据、结构化数据库、向量搜索
- **统一命令行工具**: 单一入口完成所有操作

## 项目结构

```
LingNexus/
├── lingnexus/                    # 核心应用模块
│   ├── agent/                    # Agent 创建和管理
│   │   ├── __init__.py
│   │   ├── agent_factory.py      # Agent 工厂类（内部使用）
│   │   └── react_agent.py        # 统一 Agent 创建入口（用户接口）
│   ├── cli/                      # 命令行工具
│   │   ├── __init__.py
│   │   ├── __main__.py           # CLI 主入口（路由所有命令）
│   │   ├── interactive.py        # 交互式对话模式
│   │   └── monitoring.py         # 监控相关命令（monitor、status、db、search）
│   ├── config/                   # 配置管理
│   │   ├── __init__.py
│   │   ├── agent_config.py       # Agent 配置
│   │   ├── api_keys.py           # API Key 管理
│   │   └── model_config.py       # 模型配置（Qwen、DeepSeek）
│   ├── scheduler/                # 任务调度系统
│   │   ├── __init__.py
│   │   └── monitoring.py         # 每日监控任务（协调数据采集和存储）
│   ├── storage/                  # 三层存储架构
│   │   ├── __init__.py
│   │   ├── raw.py                # 原始数据存储（HTML/JSON）
│   │   ├── structured.py         # 结构化数据库（SQLite + SQLAlchemy）
│   │   └── vector.py             # 向量数据库（ChromaDB，可选）
│   ├── utils/                    # 工具模块
│   │   ├── __init__.py
│   │   ├── code_executor.py      # 代码执行器
│   │   └── skill_loader.py       # Skills 加载和注册
│   └── __init__.py
│
├── skills/                       # Claude Skills 技能目录
│   ├── external/                 # 外部技能（Claude Skills 官方兼容格式）
│   │   ├── docx/                 # Word 文档生成技能
│   │   ├── pdf/                 # PDF 处理技能
│   │   ├── pptx/                # PowerPoint 生成技能
│   │   ├── xlsx/                # Excel 处理技能
│   │   ├── frontend-design/     # 前端设计技能
│   │   ├── canvas-design/       # Canvas 设计技能
│   │   ├── algorithmic-art/     # 算法艺术技能
│   │   ├── brand-guidelines/    # 品牌指南技能
│   │   ├── webapp-testing/      # Web 应用测试技能
│   │   ├── web-artifacts-builder/ # Web 构件构建技能
│   │   ├── slack-gif-creator/   # Slack GIF 创建技能
│   │   ├── theme-factory/       # 主题工厂技能
│   │   ├── internal-comms/      # 内部沟通技能
│   │   ├── mcp-builder/         # MCP 构建器技能
│   │   ├── skill-creator/       # 技能创建器技能
│   │   └── doc-coauthoring/     # 文档协作技能
│   └── internal/                 # 内部技能（自定义开发）
│       ├── docx/                # 内部 DOCX 技能
│       └── intelligence/        # 情报监控技能
│           ├── SKILL.md         # 技能说明文档
│           └── scripts/         # 数据采集脚本
│               ├── clinical_trials_scraper.py  # ClinicalTrials.gov 爬虫
│               └── cde_scraper.py              # CDE 网站爬虫
│
├── config/                       # 配置文件目录
│   └── projects_monitoring.yaml # 监控项目配置
│
├── examples/                     # 使用示例
│   ├── docx_agent_example.py           # DOCX Agent 示例
│   ├── progressive_agent_example.py    # 渐进式 Agent 示例
│   ├── monitoring_example.py           # 监控系统示例（Python API）
│   ├── cde_scraper_example.py          # CDE 爬虫示例（直接运行）
│   ├── studio_example.py               # Studio 集成示例
│   ├── interactive_test.py             # 交互式测试
│   ├── alias_usage_example.py          # 别名使用示例
│   └── README.md                       # 示例说明文档
│
├── tests/                        # 测试文件
│   ├── test_setup.py                  # 环境设置测试
│   ├── test_api_key.py                # API Key 测试
│   ├── test_model_creation.py         # 模型创建测试
│   ├── test_skill_registration.py     # 技能注册测试
│   ├── test_agent_creation.py         # Agent 创建测试
│   ├── test_cli.py                    # CLI 测试
│   ├── test_architecture.py           # 架构测试
│   ├── test_code_executor.py          # 代码执行器测试
│   ├── test_skill_execution.py        # 技能执行测试
│   ├── test_skill_priority.py         # 技能优先级测试
│   └── README.md                      # 测试说明文档
│
├── scripts/                      # 实用脚本
│   ├── load_claude_skills.py          # 加载 Claude Skills
│   ├── register_skills.py             # 注册 Skills 到系统
│   ├── setup.sh                       # Linux/Mac 安装脚本
│   └── setup.ps1                      # Windows 安装脚本
│
├── docs/                         # 文档目录
│   ├── architecture.md               # 架构文档
│   ├── monitoring_system.md          # 监控系统文档
│   ├── FINAL_IMPLEMENTATION_SUMMARY.md # 实现总结
│   ├── cli_guide.md                  # CLI 使用指南
│   └── encoding_fix.md               # 编码问题修复说明
│
├── data/                         # 数据目录（运行时生成，不在 git 中）
│   ├── raw/                         # 原始数据存储
│   │   └── {source}/                 # 按数据源分类
│   │       └── {date}/               # 按日期分类
│   ├── intelligence.db               # 结构化数据库（SQLite）
│   └── vectordb/                     # 向量数据库（ChromaDB）
│
├── .env.example                   # 环境变量示例
├── .gitignore                     # Git 忽略规则
├── pyproject.toml                 # Python 项目配置
├── package.json                   # Node.js 项目配置
├── uv.lock                       # Python 依赖锁定文件
├── CLAUDE.md                      # Claude Code 开发指南
├── README.md                      # 项目说明文档（本文件）
└── logs/                          # 日志文件
```

## 目录职责说明

### 核心模块 (`lingnexus/`)

#### `lingnexus/agent/` - Agent 管理层
- **react_agent.py**: 统一的 Agent 创建入口点，提供 `create_docx_agent()` 和 `create_progressive_agent()` 函数
- **agent_factory.py**: 内部工厂实现，负责实际的 Agent 实例化
- **设计原则**: 用户代码永远只调用 `react_agent.py`，不直接调用 `agent_factory.py`

#### `lingnexus/cli/` - 命令行工具
- **__main__.py**: CLI 主入口，路由所有子命令（chat、monitor、status、db、search、report）
- **interactive.py**: 交互式对话界面实现
- **monitoring.py**: 监控相关命令实现
- **使用方式**: `python -m lingnexus.cli [command]`

#### `lingnexus/config/` - 配置管理
- **model_config.py**: 创建 Qwen 和 DeepSeek 模型实例，通过 DashScope API
- **api_keys.py**: 管理 API 密钥（支持环境变量和 .env 文件）
- **agent_config.py**: Agent 配置参数

#### `lingnexus/scheduler/` - 任务调度
- **monitoring.py**: 每日监控任务的核心实现
  - 加载项目配置（`projects_monitoring.yaml`）
  - 协调多个数据源采集器
  - 数据清洗和验证
  - 保存到三层存储架构

#### `lingnexus/storage/` - 三层存储架构
- **raw.py**: 原始数据存储（保留完整的 HTML/JSON 响应）
- **structured.py**: 结构化数据库（使用 SQLAlchemy ORM + SQLite）
- **vector.py**: 向量数据库（使用 ChromaDB，可选依赖）

#### `lingnexus/utils/` - 工具模块
- **skill_loader.py**: 实现 Claude Skills 三层渐进式披露机制
- **code_executor.py**: 安全的代码执行环境

### 技能目录 (`skills/`)

#### `skills/external/` - 外部技能
- 符合 Claude Skills 官方格式
- 包含各种文档生成、设计、测试等技能
- 每个技能包含 `SKILL.md`、`scripts/`、`references/`、`assets/`

#### `skills/internal/` - 内部技能
- 自定义开发的技能
- **intelligence/**: 竞品情报监控技能
  - 包含 ClinicalTrials.gov API v2 爬虫
  - 包含 CDE 网站 Playwright 爬虫（反检测增强）

### 配置和示例 (`config/`, `examples/`, `tests/`)

#### `config/`
- **projects_monitoring.yaml**: 定义监控项目、关键词、数据源优先级

#### `examples/`
- 提供各种使用场景的完整示例
- 展示最佳实践和常见用法

#### `tests/`
- 单元测试和集成测试
- 测试覆盖所有核心功能

### 脚本和文档 (`scripts/`, `docs/`)

#### `scripts/`
- **load_claude_skills.py**: 加载外部 Claude Skills
- **register_skills.py**: 注册技能到系统
- **setup.sh/ps1**: 跨平台安装脚本

#### `docs/`
- 详细的架构、实现和使用文档

### 数据目录 (`data/`)

运行时自动生成，不在版本控制中：
- **raw/**: 原始数据（按数据源和日期组织）
- **intelligence.db**: SQLite 结构化数据库
- **vectordb/**: ChromaDB 向量数据库

## 快速开始

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd LingNexus

# 安装 Python 依赖（核心）
uv sync

# 安装 CDE 爬虫依赖（如果使用监控系统）
uv add playwright tabulate
uv run python -m playwright install chromium

# 安装向量数据库依赖（可选，用于语义搜索）
uv add chromadb

# 安装 Node.js 依赖（可选，某些技能需要）
npm install

# 配置 API Key
cp .env.example .env
# 编辑 .env 文件，添加你的 DASHSCOPE_API_KEY
```

**依赖说明**：

| 依赖 | 必需 | 说明 |
|------|------|------|
| **核心依赖** | ✅ | agentscope, sqlalchemy, requests 等 |
| **playwright** | ⚠️ | CDE爬虫需要（监控系统） |
| **tabulate** | ⚠️ | 数据库查询展示需要 |
| **chromadb** | ❌ | 向量搜索功能（可选） |
| **Node.js** | ❌ | 部分技能需要（docx, pdf等） |

### 基本使用

#### 1. 交互式对话

```bash
# 启动交互式对话
uv run python -m lingnexus.cli chat

# 或直接使用（默认模式）
uv run python -m lingnexus.cli
```

对话模式下可用的命令：
- `/help` - 显示帮助信息
- `/mode <chat|test>` - 切换模式
- `/model <qwen|deepseek>` - 切换模型
- `/execute <on|off>` - 切换代码执行
- `/history` - 查看对话历史
- `/clear` - 清空对话历史
- `/status` - 显示当前状态
- `/files` - 列出生成的文件
- `/view <filename>` - 查看文件内容
- `/exit` - 退出程序

#### 2. 运行监控系统

```bash
# 监控所有项目
uv run python -m lingnexus.cli monitor

# 监控特定项目
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# 查看监控状态
uv run python -m lingnexus.cli status
```

#### 3. 查询数据库

```bash
# 查看所有项目数据
uv run python -m lingnexus.cli db

# 查看特定项目数据
uv run python -m lingnexus.cli db --project "司美格鲁肽"

# 查看特定试验
uv run python -m lingnexus.cli db --nct NCT06989203
```

#### 4. 语义搜索

```bash
# 在向量数据库中搜索
uv run python -m lingnexus.cli search "关键词"
```

## 数据源

| 数据源 | 状态 | 方法 | 说明 |
|--------|------|------|------|
| **ClinicalTrials.gov** | ✅ 生产就绪 | API v2 | 完全自动化，支持 headless |
| **CDE** | ✅ 生产就绪 | Playwright | 需要 `playwright` 和 `headless=False` |
| **Insight** | ⏳ 计划中 | - | 即将推出 |

### CDE 爬虫使用说明

CDE（中国药物临床试验）爬虫有两种使用方式：

#### 方式1：通过CLI监控系统（推荐）

```bash
# 通过监控系统自动触发CDE爬虫
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# 查看采集到的数据
uv run python -m lingnexus.cli db --project "司美格鲁肽"
```

**优点**：
- ✅ 自动集成到监控流程
- ✅ 数据自动保存到三层存储架构
- ✅ 支持多数据源协调
- ✅ 自动数据清洗和索引

#### 方式2：直接运行脚本（调试用）

```bash
# 必须直接用 Python 运行（不能用 uv run）
python examples/cde_scraper_example.py
```

**使用要求**：
- ✅ 必须使用 `headless=False`（显示浏览器窗口）
- ✅ 直接运行脚本时不能用 `uv run`（会有 asyncio loop 冲突）
- ✅ 首次运行会自动下载 Chromium 浏览器（约 150MB）

**反检测功能**：
- 禁用自动化检测标志
- 真实浏览器指纹（User-Agent、视口、时区等）
- JavaScript 注入（覆盖 navigator.webdriver）
- 人类行为模拟（鼠标移动、页面滚动、随机延迟）
- 智能重试机制（最多 3 次）
- 页面内容检测（识别空白页面）

**提取字段**：
- 注册号 (registration_number)
- 试验状态 (status)
- 药品名称 (company)
- 适应症 (indication)
- URL 链接

## 监控系统

### 当前监控项目

#### 司美格鲁肽 (Semaglutide)

**基本信息**：
- 类别：糖尿病
- 类型：GLP-1 受体激动剂
- 商品名：Ozempic（注射剂）、Rybelsus（口服片）、Wegovy（减重）

**监控关键词**：
- 司美格鲁肽
- semaglutide
- GLP-1
- Ozempic
- Rybelsus
- Wegovy

**竞争企业**：
- 诺和诺德 (Novo Nordisk)
- 华东医药
- 丽珠集团
- 联邦制药

**适应症进展**：
- ✅ 糖尿病（已上市）
- ✅ 减重（已上市）
- 🔄 心血管（研究中）
- 🔄 NASH（研究中）
- 🔄 阿尔茨海默病（研究中）

### 数据采集流程

监控系统会自动采集以下信息：

1. **国内临床试验** (CDE)
   - 注册号
   - 试验状态
   - 药品名称
   - 适应症
   - 申办单位

2. **国际临床试验** (ClinicalTrials.gov)
   - NCT 编号
   - 试验标题
   - 状态
   - 开始日期
   - 完成日期
   - 研究设计

3. **申报进度** (Insight - 计划中)
   - IND 受理号
   - NDA 受理号
   - ANDA 受理号
   - 获准上市
   - 排队序列号

4. **新闻动态** (计划中)
   - 企业新闻
   - 研究进展
   - 市场动态

### 三层存储架构

```
data/
├── raw/              # 原始数据存储
│   ├── ClinicalTrials.gov/
│   │   └── 2026-01-06/
│   │       ├── raw_data.json
│   │       └── raw_data.html
│   └── CDE/
│       └── 2026-01-06/
│           ├── raw_data.json
│           └── raw_data.html
│
├── intelligence.db   # 结构化数据库 (SQLite)
│   ├── projects      # 项目表
│   ├── clinical_trials  # 临床试验表
│   └── applications     # 申报信息表
│
└── vectordb/        # 向量数据库 (ChromaDB)
    └── collection   # 语义搜索集合
```

**原始数据层**：
- 完整保留原始 HTML/JSON
- 按数据源和日期组织
- 便于追溯和验证

**结构化数据层**：
- SQLAlchemy ORM 管理
- SQLite 数据库
- 便于查询和分析

**向量数据层**：
- ChromaDB 向量数据库
- 语义搜索功能
- 可选组件（未安装时自动禁用）

## 项目架构

### 核心组件

```
lingnexus/
├── agent/              # Agent 工厂和统一入口点
│   ├── react_agent.py  # 用户层 API（统一入口）
│   └── agent_factory.py # Agent 工厂实现
├── cli/                # 统一命令行工具
│   ├── __main__.py     # CLI 主入口
│   ├── interactive.py  # 交互式对话
│   └── monitoring.py   # 监控命令
├── config/             # 配置管理
│   ├── model_config.py # 模型配置
│   ├── agent_config.py # Agent 配置
│   └── api_keys.py     # API Key 管理
├── scheduler/          # 监控调度器
│   └── monitoring.py   # 每日监控任务
├── storage/            # 三层存储架构
│   ├── raw.py         # 原始数据存储
│   ├── structured.py  # 结构化数据库
│   └── vector.py      # 向量数据库
└── utils/              # 工具函数
    └── skill_loader.py # Skill 加载器
```

### 技能系统

```
skills/
├── external/           # Claude Skills（兼容格式）
│   └── ...             # 外部技能
└── internal/           # 自定义技能
    └── intelligence/    # 竞品情报监控
        ├── SKILL.md    # 技能描述
        └── scripts/    # 爬虫脚本
            ├── clinical_trials_scraper.py  # ClinicalTrials.gov
            └── cde_scraper.py             # CDE 爬虫
```

### 渐进式披露机制

为了高效管理大量技能同时最小化 Token 使用，系统实现了三层渐进式披露：

**第一层 - 元数据层** (~100 tokens/skill)
- 技能名称和描述
- 启动时加载
- 快速发现可用技能

**第二层 - 指令层** (~5k tokens/skill)
- 完整的 SKILL.md 内容
- 按需加载（通过 `load_skill_instructions` 工具）
- 仅在需要时获取

**第三层 - 资源层**
- 参考文档（references/）
- 静态资源（assets/）
- 执行脚本（scripts/）
- 文件系统访问

## 模型配置

系统支持通义千问（Qwen）和 DeepSeek 模型，通过 DashScope API 使用。

### 支持的模型

**Qwen 系列**：
- `qwen-max` - 最强模型
- `qwen-plus` - 均衡模型
- `qwen-turbo` - 快速模型

**DeepSeek 系列**：
- `deepseek-chat` - 对话模型
- `deepseek-coder` - 代码模型

### API Key 配置

**优先级**（从高到低）：
1. 函数参数（最高优先级）
2. 环境变量 `DASHSCOPE_API_KEY`
3. .env 文件 `DASHSCOPE_API_KEY`

**获取 API Key**：

**通义千问**：
1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 注册/登录账号
3. 创建 API Key

**DeepSeek**：
1. 访问 [DeepSeek 官网](https://www.deepseek.com/)
2. 注册/登录账号
3. 进入 API 管理页面
4. 创建 API Key

## 开发指南

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
uv run python tests/test_setup.py
uv run python tests/test_api_key.py
uv run python tests/test_model_creation.py
uv run python tests/test_skill_registration.py
uv run python tests/test_agent_creation.py
uv run python tests/test_cli.py
uv run python tests/test_architecture.py
```

### Agent 使用示例

#### 传统 Agent（加载所有技能）

```python
from lingnexus.agent import create_docx_agent
from lingnexus.config import ModelType

agent = create_docx_agent(model_type=ModelType.QWEN)
response = await agent(Msg(name="user", content="创建一个Word文档"))
```

#### 渐进式 Agent（推荐）

```python
from lingnexus.agent import create_progressive_agent

agent = create_progressive_agent(
    model_name="qwen-max",
    temperature=0.3,
)
# Agent 自动按需加载技能说明
```

### 监控系统使用示例

```python
from lingnexus.scheduler.monitoring import DailyMonitoringTask

# 执行监控任务
task = DailyMonitoringTask()
results = task.run(project_names=["司美格鲁肽"])

# 查询数据库
from lingnexus.storage.structured import StructuredDB

db = StructuredDB()
trials = db.get_project_trials("司美格鲁肽", limit=20)
for trial in trials:
    print(f"{trial['nct_id']}: {trial['title']}")

db.close()
```

## 使用示例

项目提供了多个使用示例：

```bash
# DOCX Agent 示例
uv run python examples/docx_agent_example.py

# 渐进式 Agent 示例
uv run python examples/progressive_agent_example.py

# 监控系统示例（Python API）
uv run python examples/monitoring_example.py

# CDE 爬虫示例（调试用，直接运行）
python examples/cde_scraper_example.py
```

### CLI 使用示例（推荐）

```bash
# 通过 CLI 触发监控系统（包括 CDE 爬虫）
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# 查看采集到的数据
uv run python -m lingnexus.cli db --project "司美格鲁肽"

# 查看系统状态
uv run python -m lingnexus.cli status

# 语义搜索
uv run python -m lingnexus.cli search "GLP-1"
```

## 系统要求

### 必需

- **Python**: 3.10 或更高版本
- **uv**: Python 包管理器（推荐）
- **DASHSCOPE_API_KEY**: 通义千问API密钥

### 监控系统所需

- **playwright**: CDE爬虫依赖（`uv add playwright`）
- **Chromium**: 浏览器（自动下载，约150MB）
- **tabulate**: 数据库展示（`uv add tabulate`）

### 可选

- **ChromaDB**: 向量数据库（`uv add chromadb`）
  - 用于语义搜索功能
  - 不安装时系统自动降级，核心功能不受影响
- **Node.js**: 18.0 或更高版本（某些技能需要）

## 常见问题

### Q: CDE 爬虫返回空白页面？

**原因**: 反爬虫检测

**解决方案**：
1. 确保使用 `headless=False`
2. 使用直接 Python 运行（不是 `uv run`）
3. 检查网络连接
4. 尝试手动运行观察行为

**推荐方式**：使用 CLI 监控系统自动触发
```bash
# 先安装依赖
uv add playwright tabulate
uv run python -m playwright install chromium

# 然后运行监控
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"
```

### Q: asyncio loop 错误？

**原因**: `uv run` 会创建 asyncio loop

**解决方案**：
```bash
# 方式1：使用 CLI 监控系统（推荐）
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# 方式2：直接运行 Python 脚本
# 不要使用：uv run python script.py
# 使用：python script.py
```

### Q: 如何通过 CLI 使用 CDE 爬虫？

**A**: 推荐使用 CLI 监控系统来触发 CDE 爬虫：

```bash
# 1. 执行监控（自动触发 CDE 爬虫）
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# 2. 查看采集到的数据
uv run python -m lingnexus.cli db --project "司美格鲁肽"

# 3. 查看系统状态
uv run python -m lingnexus.cli status
```

**优点**：
- 数据自动保存到三层存储架构
- 支持多数据源协调
- 自动数据清洗和索引
- 无需手动处理 asyncio loop 问题

### Q: 必须安装 ChromaDB 吗？

**A**: 不必须。ChromaDB 是可选依赖：

- **有 ChromaDB**: 支持语义搜索（`uv run python -m lingnexus.cli search "关键词"`）
- **无 ChromaDB**: 系统自动降级，核心功能完全可用
  - ✅ 数据采集正常
  - ✅ 数据存储正常（原始数据 + SQLite）
  - ✅ 数据查询正常（按项目、NCT编号查询）
  - ⚠️ 仅缺少语义搜索功能

对于竞品监控、数据追踪等核心功能，ChromaDB 不是必需的。

### Q: Unicode 编码错误？

**原因**: Windows 控制台使用 GBK 编码

**解决方案**：保存输出到 JSON 文件而不是控制台

### Q: 为什么需要同时安装 Python 和 Node.js？

**A**: LingNexus 使用 AgentScope 框架（Python）和 Claude Skills。某些技能（如 docx、pdf）使用 Node.js 库，因此需要两种运行环境。

### Q: Node.js 依赖可以全局安装吗？

**A**: 不建议。全局安装的模块无法在项目的 `require()` 中直接使用。请使用 `npm install` 在项目本地安装。

### Q: 如何检查依赖是否正确安装？

**A**: 运行以下命令：
```bash
# 检查 Python 依赖
uv run python -c "import agentscope; print('OK')"

# 检查 Node.js 依赖
npm run test:docx
```

### Q: 安装失败怎么办？

**A**: 常见解决方法：

1. 确保 Node.js 版本 >= 18.0：`node --version`
2. 确保 Python 版本 >= 3.10：`python --version`
3. 清除缓存后重试：
   ```bash
   # Python
   uv cache clean
   rm -rf .venv
   uv sync

   # Node.js
   rm -rf node_modules package-lock.json
   npm install
   ```

## 文档

详细文档请查看：

- [安装指南](./docs/INSTALLATION.md) - 详细安装说明
- [快速开始](./docs/quick_start.md) - 快速入门指南
- [架构设计](./docs/architecture.md) - 系统架构详解
- [监控系统](./docs/monitoring_system.md) - 竞品情报监控文档
- [CLAUDE.md](./CLAUDE.md) - Claude Code 开发者指南

## 更新日志

### v0.2.0 (2026-01-06)

**新增**：
- ✨ CDE 爬虫（反检测版本）
- ✨ 详细的字段提取（注册号、状态、药品、适应症）
- ✨ 人类行为模拟
- ✨ 智能重试机制

**改进**：
- 🔧 优化监控系统调度
- 🔧 完善三层存储架构
- 🔧 统一 CLI 命令

**文档**：
- 📝 新增 CDE 爬虫使用指南
- 📝 更新架构文档
- 📝 完善常见问题解答

### v0.1.0 (2025-12-XX)

**初始版本**：
- ✨ AgentScope 多智能体系统
- ✨ Claude Skills 兼容
- ✨ 渐进式披露机制
- ✨ ClinicalTrials.gov 数据采集
- ✨ 三层存储架构
- ✨ 统一命令行工具

## 贡献

欢迎贡献！请先阅读开发指南：

1. 遵循代码规范（使用 ruff）
2. 添加测试覆盖新功能
3. 更新相关文档
4. 提交 Pull Request

## 许可证

[您的许可证信息]

## 联系方式

如有问题或建议：
- 查看 [文档](./docs/)
- 阅读 [常见问题](#常见问题)
- 提交 GitHub Issue

---

**LingNexus** - 智能竞品情报监控系统
