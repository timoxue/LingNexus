# 使用示例

**examples/** 目录包含使用示例和演示代码，面向用户展示如何使用 LingNexus API。

## 目录定位

- **examples/** - 使用示例和演示代码（面向用户）
- **scripts/** - 工具脚本和自动化脚本（面向开发者）
- **tests/** - 测试脚本和验证（面向测试）

## Phase 1: 基础功能示例

### docx Agent 示例

演示如何使用 ReActAgent 调用 docx 技能处理 Word 文档。

#### 前置要求

1. **设置环境变量**：
   ```bash
   # Windows PowerShell
   $env:DASHSCOPE_API_KEY="your_api_key"
   
   # Linux/Mac
   export DASHSCOPE_API_KEY="your_api_key"
   ```

2. **获取 API Key**：
   - Qwen（通义千问）：访问 [阿里云 DashScope](https://dashscope.console.aliyun.com/)
   - DeepSeek：访问 [DeepSeek 官网](https://www.deepseek.com/)

#### 运行示例

```bash
# 使用 uv 运行
uv run python examples/docx_agent_example.py

# 或直接运行（如果已激活虚拟环境）
python examples/docx_agent_example.py
```

#### 示例代码

```python
from lingnexus.agent import create_docx_agent
from lingnexus.config import ModelType
import os

# 创建 docx Agent（使用 Qwen 模型）
agent = create_docx_agent(
    model_type=ModelType.QWEN,
    model_name="qwen-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    temperature=0.5,
)

# 使用 Agent
response = agent.call("请帮我创建一个新的 Word 文档，标题是'项目计划'")
print(response)
```

#### 支持的模型

- **Qwen（通义千问）**：
  - `qwen-max` - 最强模型
  - `qwen-plus` - 平衡模型
  - `qwen-turbo` - 快速模型

- **DeepSeek**：
  - `deepseek-chat` - 对话模型
  - `deepseek-coder` - 代码模型

#### 更多示例

查看 `examples/docx_agent_example.py` 了解：
- 基础使用
- DeepSeek 模型使用
- 自定义 Agent 配置
- 多技能 Agent（预览）

### 交互式测试工具

快速启动交互式测试工具，与 Agent 进行对话：

```bash
# 使用模块方式启动（推荐）
uv run python -m lingnexus.cli

# 或使用示例脚本
uv run python examples/interactive_test.py

# 带参数启动
uv run python examples/interactive_test.py --model deepseek --mode chat
```

**功能**：
- 交互式对话
- 自动执行代码（test 模式）
- 命令支持（/help, /mode, /model, /execute 等）
- Studio 集成

### AgentScope Studio 集成示例

演示如何集成 AgentScope Studio 进行可视化监控：

```bash
# 启用 Studio（需要先启动 as_studio）
$env:ENABLE_STUDIO="true"
uv run python examples/studio_example.py
```

## 测试脚本

测试脚本已移至 `tests/` 目录，包括：
- `test_skill_execution.py` - Skill 执行测试
- `test_cli.py` - CLI 功能测试
- `test_architecture.py` - 架构测试

查看 `tests/README.md` 了解测试相关的内容。

## 下一步

- Phase 2: 多技能支持、自定义工具集成
- Phase 3: Skill 脚本自动封装、技能组合
