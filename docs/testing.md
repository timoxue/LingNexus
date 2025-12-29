# 测试指南

## 概述

LingNexus 提供了完整的测试套件，包括基础测试、功能测试和集成测试。

## 快速开始

### 运行完整测试套件（推荐）

```bash
uv run python tests/test_setup.py
```

这会运行所有基础测试：
- ✅ API Key 加载
- ✅ 模型创建（Qwen 和 DeepSeek）
- ✅ Skill 注册
- ✅ Agent 创建

## 测试分类

### 基础测试（不消耗 API）

以下测试不会实际调用 API，只验证配置和初始化：

```bash
# API Key 测试
uv run python tests/test_api_key.py

# 模型创建测试
uv run python tests/test_model_creation.py

# Skill 注册测试
uv run python tests/test_skill_registration.py

# Agent 创建测试
uv run python tests/test_agent_creation.py
```

### 功能测试（消耗 API）

以下测试会实际调用 API：

```bash
# Skill 执行测试（包含代码提取和执行）
uv run python tests/test_skill_execution.py

# CLI 功能测试
uv run python tests/test_cli.py

# 架构测试
uv run python tests/test_architecture.py
```

## Skill 执行测试

验证 docx 技能是否被正确调用并生成文件：

### 测试模式

```bash
# 简单测试（默认，自动执行代码）
uv run python tests/test_skill_execution.py

# 基础测试（不执行代码，只验证 Agent 响应）
uv run python tests/test_skill_execution.py --mode basic

# 完整测试（包含代码提取和执行，详细输出）
uv run python tests/test_skill_execution.py --mode full

# 使用 DeepSeek 模型
uv run python tests/test_skill_execution.py --model deepseek

# 指定输出文件名
uv run python tests/test_skill_execution.py --output my_document.docx
```

### 验证 Skill 是否被调用

**方法 1: 查看 Agent 响应**

如果 Agent 的响应中包含 Python 代码块（```python ... ```），说明：
- ✅ Agent **理解**了技能的使用方法
- ✅ Agent **知道**如何使用 docx 技能
- ✅ Skill 提示词**生效**

**方法 2: 提取并执行代码**

使用代码执行器提取并执行 Agent 生成的代码：

```python
from lingnexus.utils.code_executor import extract_and_execute_code

# Agent 响应
response_text = "..."  # Agent 的响应

# 提取并执行代码
result = extract_and_execute_code(response_text)
if result['success']:
    print("✅ 代码执行成功")
    if result.get('output'):
        print(f"输出: {result['output']}")
else:
    print(f"❌ 代码执行失败: {result.get('error')}")
```

**方法 3: 在 Studio 中查看**

启用 Studio 后，可以在浏览器中查看：
- Agent 的推理过程
- 是否识别了需要使用的技能
- 生成的代码和建议

```bash
# 启用 Studio
$env:ENABLE_STUDIO="true"
uv run python tests/test_skill_execution.py

# 然后在浏览器中访问 http://localhost:3000
```

## 测试场景

### 场景 1: 验证 API Key 加载

```python
from lingnexus.config import get_dashscope_api_key

key = get_dashscope_api_key()
if key:
    print(f"✅ API Key 已加载: {key[:10]}...{key[-4:]}")
else:
    print("❌ API Key 未加载")
```

### 场景 2: 测试模型创建

```python
from lingnexus.config import create_model, ModelType

# 测试创建 Qwen 模型
model = create_model(ModelType.QWEN, model_name="qwen-max")
print(f"✅ Qwen 模型创建成功: {model.model_name}")

# 测试创建 DeepSeek 模型
model = create_model(ModelType.DEEPSEEK, model_name="deepseek-chat")
print(f"✅ DeepSeek 模型创建成功: {model.model_name}")
```

### 场景 3: 测试 Skill 注册

```python
from lingnexus.utils import SkillLoader

loader = SkillLoader()
success = loader.register_skill("docx", skill_type="external")
if success:
    prompt = loader.get_skill_prompt()
    print(f"✅ docx 技能注册成功")
    print(f"   提示词长度: {len(prompt) if prompt else 0} 字符")
```

### 场景 4: 测试 Agent 创建

```python
from lingnexus.agent import create_docx_agent
from lingnexus.config import ModelType

agent = create_docx_agent(
    model_type=ModelType.QWEN,
    model_name="qwen-max",
)
print(f"✅ Agent 创建成功")
print(f"   Agent 名称: {agent.name}")
print(f"   模型: {agent.model.model_name}")
```

## 故障排查

### API Key 未加载

**错误**：`❌ API Key 未加载`

**解决方法**：
1. 检查 `.env` 文件是否存在
2. 检查 `.env` 文件中是否包含 `DASHSCOPE_API_KEY=your_key`
3. 确保 `.env` 文件在项目根目录

### Skill 注册失败

**错误**：`❌ 技能注册失败`

**解决方法**：
1. 检查 `skills/external/docx` 目录是否存在
2. 检查 `skills/external/docx/SKILL.md` 文件是否存在
3. 确保 Skill 目录结构正确

### 模型创建失败

**错误**：`❌ 模型创建失败`

**解决方法**：
1. 检查 API Key 是否正确
2. 检查网络连接
3. 验证模型名称是否正确

## 相关文档

- [API Key 管理指南](api_key_guide.md)
- [CLI 使用指南](cli_guide.md)
- [AgentScope Studio 指南](agentscope_studio.md)

