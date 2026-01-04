# LingNexus - 多智能体系统

基于 AgentScope 框架的多智能体系统，支持 Claude Skills 兼容。

## 项目结构

```
LingNexus/
├── lingnexus/              # 核心代码包
│   ├── agent/             # Agent 封装和工厂类
│   ├── config/            # 模型配置
│   ├── utils/             # 工具函数（Skill 加载器等）
│   └── cli/               # 交互式命令行工具
├── skills/                 # Skills 目录
│   ├── external/          # Claude 格式的 Skills
│   └── internal/          # 自主开发的 Skills
├── examples/               # 使用示例
├── tests/                  # 测试脚本
├── scripts/                # 工具脚本
└── docs/                   # 文档
```

### 目录职责说明

| 目录 | 职责 | 面向 | 文件示例 |
|------|------|------|---------|
| **examples/** | 使用示例、演示代码 | 用户 | `docx_agent_example.py` |
| **scripts/** | 工具脚本、自动化 | 开发者 | `load_claude_skills.py` |
| **tests/** | 测试脚本、验证 | 测试 | `test_skill_execution.py` |

## Phase 1: 基础功能（已完成 ✅）

已实现的基础功能：
- ✅ Agent 工厂类 - 快速创建配置好的 ReActAgent
- ✅ Skill 注册和加载 - 自动注册 Claude Skills
- ✅ 基础 docx Agent 示例 - 演示如何使用 docx 技能
- ✅ 模型配置模块 - 支持 Qwen 和 DeepSeek 模型
- ✅ 交互式测试工具 - 用户友好的命令行界面
- ✅ **渐进式披露机制** - 实现 Claude Skills 的渐进式加载（使用 qwen-max 作为 orchestrator）

### 快速使用示例

**1. 设置 API Key**

DeepSeek 和 Qwen 都使用 DashScope API，需要设置 `DASHSCOPE_API_KEY`：

```bash
# 方式 1: 环境变量（推荐）
export DASHSCOPE_API_KEY="your_api_key"

# 方式 2: .env 文件（开发环境）
# 复制 .env.example 为 .env 并填入你的 API Key
cp .env.example .env
```

**2. 交互式测试（推荐）**

```bash
# 启动交互式测试工具
uv run python -m lingnexus.cli

# 或使用示例脚本
uv run python examples/interactive_test.py
```

在交互式界面中：
- 直接输入文本与 Agent 对话
- 输入 `/help` 查看帮助
- 输入 `/mode test` 切换到测试模式（自动执行代码）
- 输入 `/exit` 退出

**3. 编程方式使用**

**传统方式（一次性加载所有 Skills）**：

```python
from lingnexus.agent import create_docx_agent
from lingnexus.config import ModelType
import asyncio
from agentscope.message import Msg

# 创建 docx Agent（自动从环境变量或 .env 读取 API Key）
agent = create_docx_agent(
    model_type=ModelType.QWEN,
    model_name="qwen-max",
    temperature=0.5,
)

# 使用 Agent
async def main():
    user_msg = Msg(name="user", role="user", content="请帮我创建一个新的 Word 文档")
    response = await agent(user_msg)
    print(response)

asyncio.run(main())
```

**渐进式披露方式（推荐，Token 效率更高）**：

```python
from lingnexus.agent import create_progressive_agent
from lingnexus.config import init_agentscope
import asyncio
from agentscope.message import Msg

# 初始化 AgentScope
init_agentscope()

# 创建支持渐进式披露的 Agent（使用 qwen-max 作为 orchestrator）
agent = create_progressive_agent(
    model_name="qwen-max",
    temperature=0.3,  # orchestrator 使用较低温度
)

# 使用 Agent（会自动按需加载 Skills 的完整指令）
async def main():
    user_msg = Msg(name="user", role="user", content="请创建一个 Word 文档")
    # Agent 会自动判断需要 docx 技能，并动态加载其完整指令
    response = await agent(user_msg)
    print(response.content)

asyncio.run(main())
```

**渐进式披露的优势**：
- ✅ Token 效率高：初始只加载 Skills 的元数据（~100 tokens/Skill）
- ✅ 智能按需加载：只在需要时加载完整指令（~5k tokens）
- ✅ 可扩展性强：支持大量 Skills，不会 token 爆炸
- ✅ 符合 Claude Skills 设计理念

更多示例请查看：
- `examples/docx_agent_example.py` - 传统方式示例
- `examples/progressive_agent_example.py` - 渐进式披露示例

**API Key 管理说明**：详见 [API Key 管理指南](docs/api_key_guide.md)

**AgentScope Studio**：详见 [Studio 使用指南](docs/agentscope_studio_guide.md)

**交互式测试**：详见 [CLI 使用指南](docs/cli_guide.md)

**测试**：运行 `uv run python tests/test_setup.py` 进行环境测试

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

#### 交互式测试（推荐）

```bash
# 启动交互式工具
uv run python -m lingnexus.cli

# 或使用示例脚本
uv run python examples/interactive_test.py
```

#### 脚本测试

```bash
# 测试技能执行
uv run python tests/test_skill_execution.py

# 查看所有选项
uv run python tests/test_skill_execution.py --help
```

#### 基础示例

```bash
# 运行基础示例
uv run python examples/docx_agent_example.py
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

- 📖 [快速开始](docs/quick_start.md) - 快速上手指南
- 📖 [CLI 使用指南](docs/cli_guide.md) - 交互式工具使用
- 📖 [API Key 管理](docs/api_key_guide.md) - API Key 设置和管理
- 🛠️ [架构设计](docs/architecture.md) - 系统架构和设计
- 🛠️ [模型配置](docs/model_config.md) - 模型配置说明
- 🛠️ [Skill 集成](docs/skill_integration.md) - Claude Skills 集成
- 📚 [测试指南](docs/testing.md) - 测试方法和指南
- 📚 [AgentScope Studio](docs/agentscope_studio_guide.md) - Studio 集成指南

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
```

### 代码质量

```bash
# 格式化代码
uv run ruff format .

# 检查代码
uv run ruff check .
```

## 许可证

[添加许可证信息]

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。
