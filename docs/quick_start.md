# 快速开始

## 安装

### 前置要求

- Python >= 3.10
- `uv` 包管理器（推荐）或 `pip`

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd LingNexus

# 2. 安装依赖（使用 uv）
uv sync

# 3. 设置 API Key（见下方）
```

## 设置 API Key

### 方式 1: .env 文件（推荐，开发环境）

1. 复制示例文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件：
```
DASHSCOPE_API_KEY=your_api_key_here
```

### 方式 2: 环境变量（推荐，生产环境）

```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your_api_key_here"

# Linux/Mac
export DASHSCOPE_API_KEY="your_api_key_here"
```

详细说明请查看 [API Key 管理指南](api_key_guide.md)。

## 快速使用

### 方式 1: 交互式 CLI（推荐）

```bash
# 启动交互式工具
uv run python -m lingnexus.cli

# 在交互界面中直接输入：
[test+exec]> 请创建一个 Word 文档，标题为"测试文档"
```

### 方式 2: 编程方式

```python
from lingnexus.agent import create_docx_agent
from lingnexus.config import ModelType
import asyncio
from agentscope.message import Msg

async def main():
    # 创建 Agent
    agent = create_docx_agent(
        model_type=ModelType.QWEN,
        model_name="qwen-max",
    )
    
    # 使用 Agent
    user_msg = Msg(name="user", role="user", content="请创建一个 Word 文档")
    response = await agent(user_msg)
    print(response)

asyncio.run(main())
```

### 方式 3: 运行示例

```bash
# 运行基础示例
uv run python examples/docx_agent_example.py
```

## 验证安装

运行测试套件验证环境配置：

```bash
uv run python tests/test_setup.py
```

如果看到以下输出，说明配置正确：

```
✅ API Key 已加载
✅ Qwen 模型创建成功
✅ DeepSeek 模型创建成功
✅ docx 技能注册成功
✅ Agent 创建成功
```

## 下一步

- 📖 [CLI 使用指南](cli_guide.md) - 了解交互式工具的使用
- 📖 [API Key 管理指南](api_key_guide.md) - 详细配置说明
- 📖 [架构设计](architecture.md) - 了解系统架构
- 📖 [测试指南](testing.md) - 运行测试

## 获取帮助

- 查看 `examples/` 目录下的示例代码
- 查看 `docs/` 目录下的详细文档
- 运行 `uv run python -m lingnexus.cli --help` 查看 CLI 帮助


