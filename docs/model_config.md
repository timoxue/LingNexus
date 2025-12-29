# 模型配置指南

## 概述

LingNexus 支持 Qwen 和 DeepSeek 模型，都通过 DashScope API 调用。

## 推荐方式：直接实例化模型类

**优点**：
- ✅ 简单直接，代码清晰
- ✅ 完全控制模型参数
- ✅ 不需要全局配置
- ✅ 适合我们的项目场景

## 使用方式

### 创建模型

```python
from lingnexus.config import create_model, ModelType

# 创建 Qwen 模型
model = create_model(
    model_type=ModelType.QWEN,
    model_name="qwen-max",
    api_key=None,  # 从环境变量或 .env 读取
    temperature=0.5,
    max_tokens=2048,
)

# 创建 DeepSeek 模型
model = create_model(
    model_type=ModelType.DEEPSEEK,
    model_name="deepseek-chat",
    api_key=None,
    temperature=0.5,
)
```

### 创建 Formatter

```python
from lingnexus.config import get_formatter, ModelType

# 获取对应的 formatter
formatter = get_formatter(ModelType.QWEN)
```

### 创建 Agent

```python
from lingnexus.agent import create_docx_agent
from lingnexus.config import ModelType

# 创建 Agent（自动创建模型和 formatter）
agent = create_docx_agent(
    model_type=ModelType.QWEN,
    model_name="qwen-max",
    temperature=0.5,
)
```

## 支持的模型

### Qwen（通义千问）

- `qwen-max` - 最强模型（推荐）
- `qwen-plus` - 平衡模型
- `qwen-turbo` - 快速模型

### DeepSeek

- `deepseek-chat` - 对话模型（推荐）
- `deepseek-coder` - 代码模型

## API Key 配置

模型使用 DashScope API，需要设置 `DASHSCOPE_API_KEY`：

1. **环境变量**（推荐）
   ```bash
   export DASHSCOPE_API_KEY="your_key"
   ```

2. **.env 文件**
   ```
   DASHSCOPE_API_KEY=your_key
   ```

3. **代码中传入**
   ```python
   model = create_model(
       model_type=ModelType.QWEN,
       api_key="your_key",
   )
   ```

详细说明请查看 [API Key 管理指南](api_key_guide.md)。

## 实现细节

### 模型创建

```python
# lingnexus/config/model_config.py

def create_model(
    model_type: ModelType | str,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.5,
    max_tokens: int = 2048,
) -> ChatModelBase:
    """创建模型实例"""
    # 实现细节...
```

### Formatter 创建

```python
def get_formatter(model_type: ModelType | str) -> FormatterBase:
    """获取对应的 formatter"""
    # Qwen 和 DeepSeek 都使用 DashScopeChatFormatter
    return DashScopeChatFormatter()
```

## 注意事项

1. **ReActAgent 要求**：ReActAgent 需要直接传入模型实例，不支持 `model_config_name`
2. **agentscope.init()**：主要用于全局配置（日志、Studio等），不用于模型配置
3. **API Key**：Qwen 和 DeepSeek 使用同一个 DashScope API Key

## 相关文档

- [API Key 管理指南](api_key_guide.md)
- [架构设计](architecture.md)

