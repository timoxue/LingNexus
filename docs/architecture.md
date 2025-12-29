# 架构设计

## 设计原则

### 1. 统一入口原则

**`react_agent.py` 作为 Agent 的统一入口**

所有需要创建 Agent 的地方都应该通过 `react_agent.py` 中的函数，而不是直接调用 `AgentFactory`。

### 2. 调用层次

```
用户/CLI 层
    ↓
react_agent.py (统一入口)
    ↓
agent_factory.py (工厂实现)
    ↓
底层组件 (model_config, skill_loader)
```

## 核心架构

### 组件关系

```
┌─────────────────────────────────────────┐
│         ReActAgent (主智能体)            │
│  - 推理 (Reasoning)                     │
│  - 行动 (Acting)                        │
│  - 观察 (Observing)                     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         Toolkit (工具集)                  │
│  - 注册 AgentSkills                     │
│  - 管理 Tools                           │
│  - 提供技能提示词                        │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐  ┌──────────────┐
│ Claude Skills│  │ 其他 Tools   │
│  (docx等)    │  │ (文件操作等)  │
└──────────────┘  └──────────────┘
```

### 文件职责

#### `lingnexus/agent/react_agent.py`
- **职责**：提供 Agent 创建的便捷函数
- **定位**：统一入口，面向用户
- **函数**：
  - `create_docx_agent()` - 创建 docx Agent
  - （未来可以添加更多：`create_pdf_agent()`, `create_multi_skill_agent()` 等）

#### `lingnexus/agent/agent_factory.py`
- **职责**：Agent 创建的工厂实现
- **定位**：内部实现，被 `react_agent.py` 调用
- **类**：
  - `AgentFactory` - Agent 工厂类

#### `lingnexus/cli/interactive.py`
- **职责**：交互式命令行工具
- **定位**：用户界面层
- **调用**：通过 `react_agent.py` 创建 Agent

## Skill 集成方式

### 通过系统提示词（当前实现）

1. 注册 Skill 到 Toolkit
2. 获取技能提示词
3. 将提示词添加到系统提示词
4. Agent 根据提示词生成代码

### 工作流程

```
用户请求
    ↓
ReActAgent 接收
    ↓
分析需求 → 识别需要使用的 Skill
    ↓
通过 Toolkit 访问 Skill 资源
    ↓
生成代码（根据技能提示词）
    ↓
返回结果给用户
```

## 调用示例

### ✅ 正确方式（通过 react_agent.py）

```python
# CLI 工具
from lingnexus.agent import create_docx_agent

agent = create_docx_agent(model_type=ModelType.QWEN)
```

### ❌ 错误方式（直接调用 AgentFactory）

```python
# 不应该这样做
from lingnexus.agent import AgentFactory

factory = AgentFactory()
agent = factory.create_docx_agent(...)
```

## 未来扩展

### 添加新的 Agent 类型

在 `react_agent.py` 中添加新函数：

```python
# react_agent.py

def create_pdf_agent(...):
    """创建 PDF Agent"""
    factory = AgentFactory()
    return factory.create_multi_skill_agent(skills=["pdf"], ...)

def create_multi_skill_agent(...):
    """创建多技能 Agent"""
    factory = AgentFactory()
    return factory.create_multi_skill_agent(...)
```

### 使用方式

```python
# CLI 或其他代码
from lingnexus.agent import create_pdf_agent, create_multi_skill_agent

# 创建 PDF Agent
pdf_agent = create_pdf_agent(model_type=ModelType.QWEN)

# 创建多技能 Agent
multi_agent = create_multi_skill_agent(
    skills=["docx", "pdf", "pptx"],
    model_type=ModelType.QWEN
)
```

## 优势

1. **统一接口**：所有 Agent 创建都通过 `react_agent.py`
2. **易于扩展**：添加新 Agent 类型只需在 `react_agent.py` 中添加函数
3. **清晰分层**：CLI -> react_agent -> agent_factory
4. **便于维护**：修改实现只需修改 `agent_factory.py`，接口不变

## 当前实现状态

- ✅ `interactive.py` 已通过 `react_agent.py` 调用
- ✅ `react_agent.py` 提供 `create_docx_agent()` 函数
- ✅ `agent_factory.py` 提供底层实现
- ✅ 架构清晰，符合设计原则

## 相关文档

- [模型配置指南](model_config.md)
- [Skill 集成指南](skill_integration.md)
- [CLI 使用指南](cli_guide.md)

