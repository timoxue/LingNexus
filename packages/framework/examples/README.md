# Framework 使用示例

本目录包含 LingNexus Framework 的使用示例和演示代码。

## 目录定位

在 Monorepo 结构中：
- **`packages/framework/examples/`** - Framework 使用示例（面向用户）
- **`packages/framework/tests/`** - Framework 测试（面向测试）
- **`scripts/`** - 项目级工具脚本（面向开发者）

## 示例列表

### 1. DOCX Agent 示例

**文件**: `docx_agent_example.py`

演示如何使用 ReActAgent 调用 docx 技能处理 Word 文档。

**运行方式**:

```bash
cd packages/framework
uv run python examples/docx_agent_example.py
```

**支持的模型**:
- **Qwen（通义千问）**: `qwen-max`, `qwen-plus`, `qwen-turbo`
- **DeepSeek**: `deepseek-chat`, `deepseek-coder`

### 2. 渐进式 Agent 示例

**文件**: `progressive_agent_example.py`

演示使用渐进式披露机制的 Agent，这是推荐的使用方式。

**运行方式**:

```bash
cd packages/framework
uv run python examples/progressive_agent_example.py
```

**优势**:
- 高效管理大量 Skills
- 最小化 Token 使用
- 按需加载技能说明

### 3. 监控系统示例

**文件**: `monitoring_example.py`

演示如何使用监控系统 API 进行数据采集。

**运行方式**:

```bash
cd packages/framework
uv run python examples/monitoring_example.py
```

**功能**:
- 执行监控任务
- 查询数据库
- 数据分析

### 4. CDE 爬虫示例（调试用）

**文件**: `cde_scraper_example.py`

**重要**: 此脚本仅供调试使用，正常使用应通过 CLI 监控系统。

**运行方式**:

```bash
# 必须直接用 Python 运行（不能用 uv run）
cd packages/framework
python examples/cde_scraper_example.py
```

**推荐使用方式**:

```bash
# 通过 CLI 监控系统（推荐）
cd packages/framework
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"
```

### 5. 交互式测试

**文件**: `interactive_test.py`

快速启动交互式测试工具，与 Agent 进行对话。

**运行方式**:

```bash
# 使用 CLI（推荐）
cd packages/framework
uv run python -m lingnexus.cli chat

# 或使用示例脚本
uv run python examples/interactive_test.py

# 带参数启动
uv run python examples/interactive_test.py --model deepseek --mode chat
```

**可用命令**:
- `/help` - 显示帮助
- `/mode <chat|test>` - 切换模式
- `/model <qwen|deepseek>` - 切换模型
- `/execute <on|off>` - 切换代码执行
- `/history` - 查看对话历史
- `/clear` - 清空对话历史
- `/exit` - 退出程序

## 前置要求

### 1. 设置环境变量

```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your_api_key"

# Linux/Mac
export DASHSCOPE_API_KEY="your_api_key"
```

或创建 `.env` 文件：

```bash
cp .env.example .env
# 编辑 .env 文件，添加你的 DASHSCOPE_API_KEY
```

### 2. 获取 API Key

**通义千问**:
1. 访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
2. 注册/登录账号
3. 创建 API Key

**DeepSeek**:
1. 访问 [DeepSeek 官网](https://www.deepseek.com/)
2. 注册/登录账号
3. 创建 API Key

### 3. 安装依赖

```bash
# 从项目根目录
cd packages/framework
uv sync

# 如果使用监控系统
uv add playwright tabulate
uv run python -m playwright install chromium

# 如果使用向量搜索（可选）
uv add chromadb
```

## CLI 使用示例

LingNexus Framework 提供统一的命令行接口：

### 交互式对话

```bash
# 启动交互式对话
uv run python -m lingnexus.cli chat

# 指定模型和模式
uv run python -m lingnexus.cli chat --model qwen --mode test
```

### 监控系统

```bash
# 监控所有项目
uv run python -m lingnexus.cli monitor

# 监控特定项目
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# 查看监控状态
uv run python -m lingnexus.cli status
```

### 数据库查询

```bash
# 查看所有项目数据
uv run python -m lingnexus.cli db

# 查看特定项目数据
uv run python -m lingnexus.cli db --project "司美格鲁肽"

# 查看特定试验
uv run python -m lingnexus.cli db --nct NCT06989203
```

### 语义搜索

```bash
# 在向量数据库中搜索
uv run python -m lingnexus.cli search "GLP-1"
```

## 常见问题

### Q: asyncio loop 错误？

**原因**: `uv run` 会创建 asyncio loop

**解决方案**:
```bash
# 方式1：使用 CLI 监控系统（推荐）
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"

# 方式2：直接运行 Python 脚本
python examples/cde_scraper_example.py
```

### Q: CDE 爬虫返回空白页面？

**解决方案**: 使用 CLI 监控系统自动触发

```bash
uv run python -m lingnexus.cli monitor --project "司美格鲁肽"
```

### Q: 必须安装 ChromaDB 吗？

**A**: 不必须。ChromaDB 是可选依赖，用于语义搜索功能。未安装时系统自动降级，核心功能完全可用。

## 更多文档

- **[Framework 快速开始](../../../docs/framework/getting-started.md)** - 入门指南
- **[Framework API 参考](../../../docs/framework/api.md)** - 完整 API 文档
- **[架构设计](../../../docs/development/architecture.md)** - 系统架构详解
- **[CLAUDE.md](../../../CLAUDE.md)** - 开发者指南

## 下一步

- 查看 [Framework README](../README.md) 了解包结构
- 查看 [测试指南](../tests/README.md) 了解测试相关内容
- 阅读 [完整文档](../../../docs/) 深入了解系统
