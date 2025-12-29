# CLI 交互式工具使用指南

## 概述

LingNexus 提供了交互式命令行工具，让你可以：
- 与 Agent 进行实时对话
- 测试 docx 技能的功能
- 自动执行 Agent 生成的代码
- 查看对话历史和文件创建结果

## 快速开始

### 启动方式

**方式 1: 模块方式（推荐）**

```bash
# 基本使用（默认 test 模式，自动执行代码）
uv run python -m lingnexus.cli

# 使用 chat 模式（不执行代码）
uv run python -m lingnexus.cli --mode chat

# 使用 DeepSeek 模型
uv run python -m lingnexus.cli --model deepseek

# 启用 Studio（方式 1: 命令行参数）
uv run python -m lingnexus.cli --studio

# 启用 Studio（方式 2: 环境变量，推荐）
# Windows PowerShell
$env:ENABLE_STUDIO="true"
uv run python -m lingnexus.cli

# Linux/Mac
export ENABLE_STUDIO=true
uv run python -m lingnexus.cli
```

**方式 2: 使用示例脚本**

```bash
# 基本使用
uv run python examples/interactive_test.py

# 指定参数
uv run python examples/interactive_test.py --mode chat --model deepseek
```

## 功能特性

### 1. 两种模式

- **Chat 模式**：普通对话，不执行代码
- **Test 模式**：自动提取并执行 Agent 生成的代码

### 2. 命令系统

所有命令以 `/` 开头：

- `/help` - 显示帮助信息
- `/status` - 显示当前状态
- `/mode <chat|test>` - 切换模式
- `/model <qwen|deepseek>` - 切换模型
- `/execute <on|off>` - 开启/关闭自动执行代码
- `/studio <on|off>` - 开启/关闭 Studio
- `/history` - 显示对话历史
- `/clear` - 清空对话历史
- `/files` - 列出生成的文件
- `/view <filename>` - 查看文件内容
- `/exit` - 退出程序

### 3. 自动代码执行

在 Test 模式下，如果 Agent 响应中包含 Python 代码块，工具会自动：
1. 提取代码
2. 执行代码
3. 验证文件是否创建

## 使用示例

### 示例 1: 创建 Word 文档

```
[test+exec]> 请创建一个 Word 文档，标题为"测试文档"

# Agent 响应...
# 代码自动执行...
# 文件创建成功
```

### 示例 2: 切换模式

```
[test+exec]> /mode chat
✅ 已切换到 chat 模式

[chat]> 请创建一个 Word 文档
# Agent 响应（不执行代码）
```

### 示例 3: 查看历史

```
[test+exec]> /history

对话历史
============================================================

[1] 用户: 请创建一个 Word 文档...
    Agent: 我将为您创建一个 Word 文档...
```

## Studio 集成

### 启用 Studio

**方式 1: 环境变量（推荐）**

```bash
# Windows PowerShell
$env:ENABLE_STUDIO="true"
uv run python -m lingnexus.cli

# Linux/Mac
export ENABLE_STUDIO=true
uv run python -m lingnexus.cli
```

**方式 2: 命令行参数**

```bash
uv run python -m lingnexus.cli --studio
```

**方式 3: 运行时启用**

在交互式界面中使用命令：

```
[test+exec]> /studio on
✅ 已开启 Studio（需要重启程序生效）
```

### Studio 使用

1. 启动 Studio：`as_studio`
2. 在代码中启用 Studio（见上方）
3. 运行 CLI 工具
4. 在浏览器中访问 `http://localhost:3000` 查看运行情况

## 命令行参数

### 启动参数

```bash
uv run python -m lingnexus.cli [OPTIONS]

选项:
  --model {qwen,deepseek}    模型类型 (默认: qwen)
  --model-name MODEL_NAME     模型名称（如 qwen-max, deepseek-chat）
  --mode {chat,test}          初始模式 (默认: test)
  --no-execute                不自动执行代码
  --studio                    启用 Studio
  --no-studio                 禁用 Studio（覆盖环境变量）
```

### 示例

```bash
# 使用 DeepSeek 模型，chat 模式
uv run python -m lingnexus.cli --model deepseek --mode chat

# 启用 Studio，不自动执行代码
uv run python -m lingnexus.cli --studio --no-execute
```

## 故障排查

### 问题 1: Agent 未创建

**原因**：API Key 未设置

**解决**：
1. 检查 `.env` 文件是否存在
2. 检查环境变量 `DASHSCOPE_API_KEY` 是否设置
3. 使用 `/status` 命令查看当前配置

### 问题 2: 代码执行失败

**原因**：代码中有错误或依赖未安装

**解决**：
1. 查看错误信息
2. 检查是否安装了 `python-docx`：`uv sync`
3. 手动执行代码查看详细错误

### 问题 3: Studio 连接失败

**原因**：Studio 未启动

**解决**：
1. 确保已启动 Studio：`as_studio`
2. 检查 Studio 是否在 `http://localhost:3000` 运行
3. 如果不需要 Studio，可以不启用

## 提示和技巧

1. **快速测试**：使用 Test 模式快速验证功能
2. **查看状态**：使用 `/status` 查看当前配置
3. **切换模型**：使用 `/model` 命令切换模型
4. **查看文件**：使用 `/files` 列出生成的文件

## 相关文档

- [AgentScope Studio 指南](agentscope_studio.md)
- [API Key 管理](api_key_guide.md)
- [测试指南](testing.md)

