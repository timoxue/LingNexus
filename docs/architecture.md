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

1. **阶段1（元数据层）**：初始化时只加载所有 Skills 的元数据（~100 tokens/Skill）
2. **阶段2（指令层）**：LLM 判断需要时，动态加载完整指令（~5k tokens）
3. **阶段3（资源层）**：按需访问资源文件
   - **References**：按需加载参考文档（references/ 或根目录的 .md 文件）
   - **Assets**：通过文件系统访问资源文件（不加载到 context）
   - **Scripts**：通过文件系统访问或执行脚本

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
动态加载选定 Skill 的完整指令（SKILL.md）
    ↓
LLM 调用 #2：根据完整指令规划如何使用 Skill
    ↓
如果指令中引用了参考文档，调用 load_skill_reference 工具
    ↓
按需加载参考文档（如 docx-js.md, ooxml.md）
    ↓
如果需要访问资源，调用 get_skill_resource_path 工具
    ↓
获取资源路径，通过文件系统访问 scripts/, assets/ 等
    ↓
生成代码并执行
    ↓
返回结果给用户
```

**关键点**：
- LLM 调用发生在使用 Skill 之前
- 第一次调用：判断是否需要使用 Skill（基于元数据）
- 第二次调用：规划如何使用 Skill（基于完整指令）
- 可能多次调用：按需加载参考文档
- 资源层按需访问：references 加载到 context，assets/scripts 通过文件系统访问
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

---

# Platform 与 Framework 架构

## 📦 当前架构（临时方案）

### 架构概览

```
LingNexus Monorepo
├── packages/
│   ├── framework/          ← Agent 运行框架
│   │   ├── lingnexus/      ← 核心 Agent 逻辑
│   │   ├── skills/         ← Claude Skills
│   │   └── tests/
│   │
│   └── platform/
│       └── backend/        ← Web API & 数据管理
│           ├── api/        ← REST API
│           ├── db/         ← 数据库
│           ├── services/
│           │   └── agent_service.py  ← ⚠️ 直接导入 framework
│           └── tests/
```

### 依赖关系

**packages/platform/backend/pyproject.toml**:
```toml
dependencies = [
    "lingnexus-framework",  # ← 通过 UV workspace 依赖
]

[tool.uv.sources]
lingnexus-framework = { workspace = true }
```

**packages/platform/backend/services/agent_service.py**:
```python
# ⚠️ 临时方案：直接导入 Framework
from lingnexus import create_progressive_agent
from lingnexus.config import init_agentscope

async def execute_agent(message, model_name, temperature):
    agent = create_progressive_agent(...)  # ← 进程内调用
    return await agent(message)
```

### 调用流程

```
用户请求 (HTTP)
    ↓
Platform Backend (FastAPI :8000)
    ↓
AgentController.execute_agent()
    ↓
agent_service.py (导入 lingnexus)  ← ⚠️ 紧耦合
    ↓
create_progressive_agent()  ← 进程内直接调用
    ↓
Agent 执行
    ↓
返回结果
```

## ⚠️ 当前架构的问题

### 1. 无法独立部署

| 问题 | 说明 |
|------|------|
| **紧耦合** | Backend 代码直接导入 Framework，必须包含 Framework 代码 |
| **无法独立运行** | Backend 不能单独部署，必须带上整个 Framework |
| **依赖复杂** | Python 环境、依赖必须完全一致 |
| **资源浪费** | Backend 服务器也需要加载 Agent 模型 |

### 2. 技术限制

- ❌ Backend 和 Framework 必须使用相同 Python 版本
- ❌ Backend 无法独立扩展（扩容时必须带上 Framework）
- ❌ Framework 更新需要重新部署 Backend
- ❌ 无法使用不同技术栈（如 Go、Java 实现 Backend）

### 3. 违反设计原则

- ❌ **单一职责原则**：Backend 既管理数据又执行 Agent
- ❌ **微服务原则**：应该独立部署、独立扩展
- ❌ **松耦合原则**：直接导入导致紧耦合

## 🎯 未来改进计划

### 方案 1：微服务架构（推荐）

#### 目标架构

```
┌─────────────────────────────────────────────────────┐
│  Platform Backend (可独立部署)                        │
│  ┌───────────────────────────────────────────────┐  │
│  │ FastAPI Server (:8000)                        │  │
│  │  - 用户认证                                    │  │
│  │  - 技能管理 (CRUD)                             │  │
│  │  - Agent 管理 (CRUD)                           │  │
│  │  - 执行历史 (存储)                              │  │
│  │  - WebSocket (实时通信)                        │  │
│  └───────────────────────────────────────────────┘  │
│                      │ HTTP/REST                     │
│                      ▼                               │
│  ┌───────────────────────────────────────────────┐  │
│  │ Framework Service (独立服务)                   │  │
│  │  FastAPI/Flask Server (:8001)                 │  │
│  │  - Agent 执行引擎                              │  │
│  │  - Skill 加载器                                │  │
│  │  - Model 管理 (DashScope)                     │  │
│  │  - 资源隔离                                    │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

#### 优势

| 特性 | 说明 |
|------|------|
| **独立部署** | Backend 和 Framework 可以独立部署、独立扩展 |
| **技术解耦** | Backend 可以用其他语言重写（Go、Java） |
| **故障隔离** | Framework 崩溃不影响 Backend 的数据管理功能 |
| **弹性扩展** | 根据负载独立扩展 Backend 或 Framework |
| **团队协作** | 不同团队可以独立开发、部署 |

#### 实施步骤

**Phase 1: Framework HTTP API**

创建 `packages/framework/lingnexus/server.py`:

```python
"""
Framework HTTP Server
提供 Agent 执行的 HTTP API
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from lingnexus import create_progressive_agent

app = FastAPI(title="LingNexus Framework Service")

class ExecuteRequest(BaseModel):
    agent_config: dict  # model_name, temperature, skills
    message: str

class ExecuteResponse(BaseModel):
    status: str
    output_message: str
    error_message: str = None
    tokens_used: int
    execution_time: float

@app.post("/api/v1/execute", response_model=ExecuteResponse)
async def execute_agent(request: ExecuteRequest):
    """执行 Agent（HTTP API）"""
    try:
        agent = create_progressive_agent(**request.agent_config)
        from agentscope.message import Msg
        msg = Msg(name="user", content=request.message)
        response = await agent(msg)

        return ExecuteResponse(
            status="success",
            output_message=response.content,
            tokens_used=0,
            execution_time=0.0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Phase 2: Platform Backend HTTP Client**

```python
# packages/platform/backend/services/agent_service.py
"""
Agent 执行服务（生产方案：通过 HTTP API 调用 Framework）
"""
import httpx
import os

FRAMEWORK_SERVICE_URL = os.getenv(
    "FRAMEWORK_SERVICE_URL",
    "http://localhost:8001"
)

async def execute_agent(
    message: str,
    model_name: str = "qwen-max",
    temperature: float = 0.7,
    skill_ids: list = None,
) -> dict:
    """
    调用 Framework Service 的 HTTP API

    Args:
        message: 用户消息
        model_name: 模型名称
        temperature: 温度
        skill_ids: 关联技能 ID 列表

    Returns:
        执行结果
    """
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(
            f"{FRAMEWORK_SERVICE_URL}/api/v1/execute",
            json={
                "agent_config": {
                    "model_name": model_name,
                    "temperature": temperature,
                },
                "message": message,
            },
        )
        response.raise_for_status()
        return response.json()
```

**Phase 3: 配置开关**

```python
# packages/platform/backend/core/config.py
class Settings:
    # Agent 执行模式：direct（开发） | http（生产）
    AGENT_EXECUTION_MODE: str = os.getenv("AGENT_EXECUTION_MODE", "direct")
    FRAMEWORK_SERVICE_URL: str = os.getenv("FRAMEWORK_SERVICE_URL", "http://localhost:8001")

# packages/platform/backend/services/agent_service.py
if settings.AGENT_EXECUTION_MODE == "http":
    # 生产环境：HTTP API 调用
    from .agent_service_http import execute_agent
else:
    # 开发环境：直接导入
    from .agent_service_direct import execute_agent
```

**Phase 4: 部署**

```yaml
# docker-compose.yml
version: '3.8'
services:
  platform-backend:
    build: ./packages/platform/backend
    ports:
      - "8000:8000"
    environment:
      - AGENT_EXECUTION_MODE=http
      - FRAMEWORK_SERVICE_URL=http://framework-service:8001
    depends_on:
      - framework-service

  framework-service:
    build: ./packages/framework
    ports:
      - "8001:8001"
    environment:
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}
```

### 方案 2：消息队列（异步）

```
Platform Backend  ─────►  Redis/RabbitMQ  ─────►  Framework Workers
    (Web API)              (任务队列)              (Agent 执行)
```

**适用场景**：
- 长时间运行的 Agent 任务
- 需要异步执行的场景
- 需要任务队列和重试机制

### 方案 3：gRPC（高性能）

**适用场景**：
- 需要更高性能的通信
- 服务间频繁调用
- 需要强类型定义

## 📅 实施时间表

| 阶段 | 任务 | 优先级 | 状态 |
|------|------|--------|------|
| **当前** | 临时方案（直接导入） | P0 | ✅ 已完成 |
| **Phase 1** | Framework HTTP API 实现 | P0 | ⏳ 待开始 |
| **Phase 2** | Backend HTTP Client | P0 | ⏳ 待开始 |
| **Phase 3** | 配置开关（direct/http） | P1 | ⏳ 待开始 |
| **Phase 4** | Docker Compose 部署 | P1 | ⏳ 待开始 |
| **Phase 5** | 生产环境部署 | P2 | ⏳ 待开始 |

## 🎯 临时方案的限制

### 适合场景

✅ **开发环境**：快速迭代、调试方便
✅ **测试环境**：功能测试、集成测试
✅ **小规模部署**：单机部署、内部使用

### 不适合场景

❌ **生产环境**：无法独立扩展、故障隔离
❌ **大规模部署**：资源浪费、无法独立扩展
❌ **多团队协作**：紧耦合、互相影响

## 💡 最佳实践

### 当前（临时方案）

1. **明确标注**：在代码中添加 `# ⚠️ 临时方案` 注释
2. **文档说明**：在 README 中说明这是开发方案
3. **定期回顾**：每个 Sprint 回顾是否需要迁移

### 迁移到微服务后

1. **灰度发布**：先用配置开关控制，逐步切换
2. **监控指标**：API 延迟、成功率、资源使用
3. **回滚方案**：保留直接导入模式作为备选

## 📚 相关资源

- [微服务架构模式](https://microservices.io/patterns/microservices.html)
- [FastAPI 高性能部署](https://fastapi.tiangolo.com/deployment/)
- [Docker Compose 生产环境](https://docs.docker.com/compose/production/)

