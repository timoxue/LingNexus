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
  - `create_docx_agent()` - 创建 docx Agent（传统方式）
  - `create_progressive_agent()` - 创建支持渐进式披露的 Agent（推荐）
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

### 方式 1: 传统方式（一次性加载）

1. 注册 Skill 到 Toolkit
2. 获取技能提示词
3. 将提示词添加到系统提示词
4. Agent 根据提示词生成代码

**工作流程**：

```
用户请求
    ↓
ReActAgent 接收（已包含所有 Skills 的完整指令）
    ↓
分析需求 → 识别需要使用的 Skill
    ↓
通过 Toolkit 访问 Skill 资源
    ↓
生成代码（根据技能提示词）
    ↓
返回结果给用户
```

### 方式 2: 渐进式披露（推荐）

实现 Claude Skills 的渐进式披露机制：

1. **阶段1**：初始化时只加载所有 Skills 的元数据（~100 tokens/Skill）
2. **阶段2**：LLM 判断需要时，动态加载完整指令（~5k tokens）
3. **阶段3**：按需访问资源文件（scripts/, references/, assets/）

**工作流程**：

```
用户请求
    ↓
ReActAgent 接收（只包含 Skills 的元数据）
    ↓
LLM 调用 #1：分析需求 → 判断需要哪个 Skill（基于元数据）
    ↓
调用 load_skill_instructions 工具
    ↓
动态加载选定 Skill 的完整指令
    ↓
LLM 调用 #2：根据完整指令规划如何使用 Skill
    ↓
生成代码并执行
    ↓
返回结果给用户
```

**关键点**：
- LLM 调用发生在使用 Skill 之前
- 第一次调用：判断是否需要使用 Skill（基于元数据）
- 第二次调用：规划如何使用 Skill（基于完整指令）
- Skill 脚本的执行在 LLM 调用之后

**架构组件**：

```
┌─────────────────────────────────────────┐
│    Progressive Agent (qwen-max)        │
│    - 看到所有 Skills 的元数据            │
│    - 智能选择需要的 Skill                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    渐进式加载工具                         │
│    - load_skill_instructions()          │
│    - list_available_skills()            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    SkillLoader                          │
│    - 元数据缓存                          │
│    - 完整指令缓存                         │
│    - 动态加载方法                         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│    Skills 目录                           │
│    - external/ (Claude Skills)          │
│    - internal/ (自定义 Skills)           │
└─────────────────────────────────────────┘
```

## 调用示例

### ✅ 正确方式（通过 react_agent.py）

**传统方式**：

```python
from lingnexus.agent import create_docx_agent
from lingnexus.config import ModelType

agent = create_docx_agent(model_type=ModelType.QWEN)
```

**渐进式披露方式（推荐）**：

```python
from lingnexus.agent import create_progressive_agent
import asyncio
from agentscope.message import Msg

agent = create_progressive_agent(
    model_name="qwen-max",
    temperature=0.3,
)

async def main():
    user_msg = Msg(name="user", role="user", content="创建一个 Word 文档")
    response = await agent(user_msg)
    print(response.content)

asyncio.run(main())
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
- ✅ `react_agent.py` 提供 `create_docx_agent()` 函数（传统方式）
- ✅ `react_agent.py` 提供 `create_progressive_agent()` 函数（渐进式披露）
- ✅ `agent_factory.py` 提供底层实现
- ✅ `SkillLoader` 支持渐进式披露方法
- ✅ `progressive_skill_loader.py` 提供动态加载工具
- ✅ 架构清晰，符合设计原则

## 相关文档

- [模型配置指南](model_config.md)
- [Skill 集成指南](skill_integration.md)
- [CLI 使用指南](cli_guide.md)

