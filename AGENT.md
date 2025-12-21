# AGENT.md - AI 编程工具专用项目上下文

> 本文件专门为 AI 编程助手（如 GitHub Copilot、Cursor、Qoder 等）设计，提供项目架构、约束规则和代码模式的完整上下文。

---

## 项目元信息

- **项目名称**: LingNexus
- **语言**: Python 3.10
- **架构模式**: 微服务 + 分层架构
- **主要框架**: FastAPI + AgentScope >= 1.0.0 + Pydantic
- **部署方式**: Docker + docker-compose
- **业务领域**: 医药行业 AI 智能服务（情报分析、BD、药物研发）

---

## 核心架构约束（CRITICAL）

### 1. 分层依赖规则（强制）

```
┌─────────────────────────────────────────┐
│  core_agents/                          │  ← 业务服务层（禁止互相 import）
│  ├─ intelligence_service/             │
│  ├─ bd_service/                       │
│  └─ rd_service/                       │
└───────────────┬───────────────────────┘
                │ 仅向下依赖
┌───────────────▼───────────────────────┐
│  shared/                              │  ← 能力支撑层（可被所有服务使用）
│  ├─ storage/    (数据访问)            │
│  ├─ knowledge/  (RAG 引擎)            │
│  ├─ models/     (大模型管理)          │
│  ├─ prompts/    (Prompt 统一管理)     │
│  ├─ tools/      (通用工具)            │
│  └─ utils/      (基础设施)            │
└───────────────┬───────────────────────┘
                │ 仅向下依赖
┌───────────────▼───────────────────────┐
│  config/                              │  ← 配置中心（只被依赖，不依赖业务）
│  ├─ settings.py                       │
│  ├─ model_config.yaml                 │
│  ├─ agentscope_config.yaml            │
│  └─ service_config.yaml               │
└───────────────────────────────────────┘
```

**强制约束**：
- ❌ `core_agents/intelligence_service` **禁止** import `core_agents/bd_service` 的任何模块
- ❌ `shared/` 下任何模块 **禁止** import `core_agents/` 的代码
- ✅ 服务间调用必须通过 HTTP API（调用对方的 FastAPI 端点）
- ✅ 所有服务可以自由使用 `shared/` 和 `config/` 的任何模块

### 2. 配置与安全规则

**环境变量（.env）**：
- ✅ 所有敏感信息（API Key、密码、连接串）**只能**放 `.env`
- ✅ 使用 `pydantic-settings` 的 `validation_alias` 从环境变量读取
- 示例：
  ```python
  openai_api_key: Optional[str] = Field(default=None, validation_alias="OPENAI_API_KEY")
  ```

**YAML 配置文件**：
- ✅ 只存放非敏感的结构化配置（端口、模型名称、索引名称等）
- ❌ **禁止**在 YAML 中硬编码 API Key 或密码
- 示例结构：
  ```yaml
  default_llm: openai_gpt4o
  models:
    openai_gpt4o:
      api_base: "https://api.openai.com"
      model_name: "gpt-4o-mini"
      api_key_env: "OPENAI_API_KEY"  # 指向环境变量名，而非真实 Key
  ```

**配置加载流程**：
1. `config/settings.py` 的 `Settings.load()` 类方法统一加载
2. 先读 `.env` 构造基础 `Settings` 实例
3. 再加载 YAML 合并到嵌套配置对象中
4. 对外暴露全局单例 `settings`

### 3. 数据访问封装规则

**禁止行为**：
- ❌ 在 Agent 或 Workflow 中直接 `import elasticsearch`、`import pymysql` 等
- ❌ 在业务代码中硬编码数据库连接字符串或 API 端点

**正确模式**：
```python
# ✅ 在 workflow 中调用 shared 层封装
from shared.storage.es_query_medical import search_clinical_trials
from shared.knowledge.rag_engine import RAGEngine

async def my_workflow(request):
    # 通过封装的函数调用数据源
    results = await search_clinical_trials(es_client, query=request.query, filters={}, top_k=10)
    # ...
```

**数据访问层职责划分**：
- `shared/storage/es_client.py`: 管理 ES 连接池、基础 CRUD
- `shared/storage/es_query_medical.py`: 提供医药业务语义化查询接口（如 `search_clinical_trials()`）
- `shared/knowledge/rag_engine.py`: 融合 ES + 向量库的统一检索入口

---

## 代码生成模式（Code Patterns）

### 1. Skill 层（shared/skills）

**设计目标**：将可复用的“能力”从具体服务中抽离出来，形成可被多个服务、Agent、Workflow 调用的技能库。

- 抽象定义：
  - `BaseSkill`：所有技能的基类，定义：
    - `name`：技能唯一标识（如 `intel.fetch_news`、`bd.lead_qualification`、`rd.compound_analysis`）
    - `domain`：业务域（`intelligence`/`bd`/`rd`）
    - `category`：技能类别（`retrieval`/`analysis`/`reporting` 等）
    - `tags`：便于检索和展示的标签列表
    - `async execute(input_data: SkillInput) -> SkillOutput`
  - `SkillInput`：所有技能输入模型的基类（Pydantic），具体技能继承并声明字段；
  - `SkillOutput`：统一输出结构，包含：`success`/`data`/`message`/`meta`。
- 注册与发现：
  - 使用 `@register_skill` 装饰器注册技能：
    - 示例：`@register_skill class FetchNewsSkill(BaseSkill): name = "intel.fetch_news" ...`
  - 通过 `get_skill(name)` 获取技能实例；`list_skills(domain, category)` 可列出技能。
- 示例：订阅日报链路中的两个技能：
  - `intel.fetch_news`（资讯检索技能）：
    - 输入：`topic_name`、`keywords`、`max_items`
    - 输出：`data` 为原始资讯 dict 列表（字段结构与 `pharma_news` 索引一致）；
  - `intel.generate_daily_digest`（日报生成技能）：
    - 输入：`topic_name`、`topic_description`、`news_items_text`、`role`
    - 输出：`data` 为生成好的订阅日报文本。

**Agent 调用 Skill 的推荐模式**：

```python
from shared.skills import get_skill
from shared.skills.intelligence.fetch_news import FetchNewsInput

skill = get_skill("intel.fetch_news")
if skill is not None:
    skill_input = FetchNewsInput(topic_name=topic.name, keywords=keywords, max_items=topic.max_items)
    skill_output = await skill.execute(skill_input)
    raw_items = skill_output.data if skill_output.success else []
else:
    # 可选：回退到函数封装逻辑
    from shared.skills.intelligence.fetch_news import fetch_raw_news_for_topic
    raw_items = await fetch_raw_news_for_topic(topic.name, keywords, topic.max_items)
```

> 设计原则：业务 Agent 更关注“**用什么能力**”，Skill 层关注“**能力如何实现**”，Shared 层继续屏蔽具体数据源与模型供应商差异。

#### 1.1 三大服务与 Skill 的典型联调用例

- **情报订阅日报（intelligence_service）**：
  - **接口**：`POST /v1/internal/daily_digest`
  - **调用链**：`DailyDigestWorkflow` → `RetrievalAgent.fetch_news_for_topic` → Skill `intel.fetch_news` → `AnalysisAgent.build_digest` → Skill `intel.generate_daily_digest` → `llm_manager.chat`。
  - **设计思路**：Workflow 只负责编排 Topic/User；Agent 专注检索与摘要逻辑；Skill 封装“如何查资讯”“如何写日报”；Prompt 保存在 `shared/prompts/intelligence.yaml`。
- **BD 线索评估（bd_service）**：
  - **接口**：`POST /bd/analyze`
  - **调用链**：`run_bd_pipeline` → Skill `bd.lead_qualification` → `prompt_manager.render(service="bd", key=...)` → `llm_manager.chat`。
  - **设计思路**：BD Workflow 不直接写 Prompt，只决定“何时需要线索评估”；Skill 使用 BD 域 Prompt（`shared/prompts/bd.yaml`）和指定模型（如 Qwen）生成一段可复用的 BD 报告。
- **RD 化合物分析（rd_service）**：
  - **接口**：`POST /rd/analyze`
  - **调用链**：`run_rd_pipeline` → Skill `rd.compound_analysis` → `prompt_manager.render(service="rd", key=...)` → `llm_manager.chat`。
  - **设计思路**：RD Workflow 负责“一个化合物需要怎样的分析流程”；Skill 将具体的分析维度（作用机制、安全性、竞品格局等）固化在 Prompt 中，方便后续统一升级。

> 总体设计思路：场景（Workflow）→ 能力编排（Agent）→ 能力实现（Skill）→ 模型与 Prompt（shared/models + shared/prompts），通过 Skill 层把“可复用能力”和“具体场景”解耦，既便于联调测试，也便于在 BD/RD/情报之间迁移能力。

### 2. 插件运行时（plugin_runtime/ + plugins/）

**设计目标**：在不破坏现有分层架构的前提下，引入一层“插件运行时”，将多个 Skill/Workflow 封装为可安装、可调用的插件（Plugin），便于 Web 操作台、IM 机器人等统一调用。

- 目录结构：
  - `plugin_runtime/`
    - `api.py`：Plugin Runtime 的 FastAPI 应用入口，提供：
      - `GET /plugins`：列出可用插件；
      - `GET /plugins/{plugin_id}/schema`：返回插件的 `input_schema` / `output_schema`；
      - `POST /plugins/{plugin_id}/invoke`：执行插件入口；
    - `models.py`：`PluginManifest` / `PluginSummary` / `PluginInvokeResponse` 等运行时模型；
    - `registry.py`：从 `plugins/` 目录加载 `plugin_manifest.json`，导入入口函数并注册到内存。
  - `plugins/`
    - `intel_daily_digest/`：首个 PoC 插件“订阅日报 Quick Run”：
      - `plugin_manifest.json`：插件元信息、依赖 `required_skills`、输入输出 Schema；
      - `main.py`：约定入口 `async def run_plugin(input_data: dict, context: dict | None) -> dict`。

- 推荐使用方式（面向外部系统 / 工具）：
  - 优先通过 Plugin Runtime 的 `/plugins/...` 接口调用插件，而不是直接调用某个服务的内部接口；
  - 插件内部再调用对应的 Workflow/Skill，例如：
    - 订阅日报插件：内部调用 `DailyDigestWorkflow.run_daily_digest`（间接使用 `intel.fetch_news` + `intel.generate_daily_digest`）；
    - 未来的 BD/RD 插件可以复用 `bd.lead_qualification`、`rd.compound_analysis` 等 Skill。

> 对 AI 编程助手而言：如果用户希望“像 App 一样使用 AI 能力”，优先考虑通过 Plugin Runtime 调用插件；如果是针对具体服务做底层改造，则继续直接操作 `core_agents/` 与 `shared/skills/`。

### 3. 新增服务（core_agents/xxx_service/）

**目录结构**：
```
core_agents/new_service/
├── __init__.py
├── schema.py          # Pydantic 请求/响应模型
├── api.py             # FastAPI 应用入口
├── agents/            # AgentScope Agent 定义
│   └── __init__.py
├── workflows/         # 多 Agent 编排流程
│   ├── __init__.py
│   └── new_workflow.py
└── tools/             # 服务内专用工具
    └── __init__.py
```

**schema.py 模板**：
```python
from typing import List, Optional
from pydantic import BaseModel, Field

class NewServiceRequest(BaseModel):
    """请求模型注释"""
    query: str = Field(..., description="查询内容")
    context: Optional[str] = Field(None, description="额外上下文")

class NewServiceResponse(BaseModel):
    """响应模型注释"""
    summary: str = Field(..., description="分析总结")
    results: List[str] = Field(default_factory=list, description="结果列表")
```

**workflow 模板**：
```python
from core_agents.new_service.schema import NewServiceRequest, NewServiceResponse
from shared.models.llm_manager import llm_manager
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

async def run_new_pipeline(request: NewServiceRequest) -> NewServiceResponse:
    """服务主流程"""
    logger.info("Pipeline started", extra={"query": request.query})
    
    # TODO: 实现业务逻辑
    # 1. 调用 shared/knowledge 做检索
    # 2. 调用 llm_manager.chat() 做分析
    # 3. 构造响应
    
    return NewServiceResponse(summary="示例结果", results=[])
```

**api.py 模板**：
```python
from fastapi import Depends, FastAPI
from config.settings import settings
from core_agents.new_service.schema import NewServiceRequest, NewServiceResponse
from core_agents.new_service.workflows.new_workflow import run_new_pipeline
from shared.utils.logging_utils import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="New Service", description="服务描述", version="0.1.0")

def get_settings():
    return settings

@app.post("/new/analyze", response_model=NewServiceResponse, tags=["new"])
async def analyze(request: NewServiceRequest, _settings=Depends(get_settings)) -> NewServiceResponse:
    """API 端点描述"""
    logger.info("Request received", extra={"query": request.query})
    result = await run_new_pipeline(request)
    return result
```

### 2. 使用 Prompt 统一管理

**原则**：
- ✅ 所有 Prompt 必须放在 `shared/prompts/*.yaml` 中，禁止在 workflow 中硬编码
- ✅ 使用 `prompt_manager.render()` 填充变量
- ✅ Prompt 按服务分组（intelligence/bd/rd），不按模型分组

**标准使用模式**：
```python
from shared.prompts.manager import prompt_manager

async def my_workflow(request):
    # 1. 选择 Prompt
    prompt_key = "intelligence_summary_v1"  # 可根据业务逻辑动态选择
    
    # 2. 渲染 Prompt（填充变量）
    prompt_text = prompt_manager.render(
        service="intelligence",
        key=prompt_key,
        query=request.query,
        context=request.context or "无上下文",
    )
    
    # 3. 获取推荐模型
    model = prompt_manager.get_recommended_model("intelligence", prompt_key)
    
    # 4. 调用 LLM
    messages = [{"role": "system", "content": prompt_text}]
    response = await llm_manager.chat(messages, model_name=model)
```

**新增 Prompt 流程**：
1. 在 `shared/prompts/{service}.yaml` 中添加新 Prompt
2. 给定唯一 key（如 `intelligence_detailed_v2`）
3. 填写 `description`、`recommended_model`、`template` 等字段
4. 在 workflow 中使用新 key

**Prompt YAML 结构示例**：
```yaml
intelligence_summary_v1:
  description: "情报分析：基础总结版"
  version: 1
  recommended_model: "deepseek"
  locale: "zh-CN"
  template: |
    你是一个专注医药情报分析的助手。
    
    【用户查询】
    {query}
    
    【检索上下文】
    {context}
    
    请输出结构化的分析结果。

intelligence_daily_digest_v1:
  description: "情报订阅日报 - 按主题聚合 Top 资讯并支持角色个性化"
  version: 1
  recommended_model: "deepseek"
  locale: "zh-CN"
  template: |
    你是一个面向医药行业从业者的「订阅日报」撰写助手，需要根据给定主题和候选资讯，生成结构化的订阅日报内容。

    当前本次日报的主要阅读角色是：{target_role}
    （如果未指定角色，你可以面向“综合读者”进行撰写。）

    【订阅主题】
    {topic_name}

    【主题说明】
    {topic_description}

    【候选资讯列表】
    {news_items}

    【写作要求】
    1. 先给出本主题下的整体形势短评（100-200 字），说明近期的关键趋势与看点；
    2. 按重要性列出 3-10 条重点资讯，每条包含标题、1-3 句专业总结、来源和时间；
    3. 结合 {target_role} 调整侧重点，并在末尾加入该角色视角的「机会与风险提示」；
    4. 使用专业但易读的中文，避免出现“模型/Prompt”等技术细节。
```

---

### 3. 扩展 shared 层能力

在订阅日报场景中，核心的共享组件包括：

- `shared/storage/es_client.py`：
  - 在 **模式 A/B** 下通过本地 JSON 文件（如 `clinical_trials.json`、`pharma_news.json`）模拟 ES；
  - 在 **模式 C** 下可切换为真实 Elasticsearch；
- `shared/knowledge/vector_store.py`：
  - 支持 `none` / `chroma` / `milvus` 等后端，供后续 RAG/相似度检索使用；
- `shared/prompts/intelligence.yaml`：
  - 统一管理情报相关 Prompt，包括 `intelligence_summary_v1` 和 `intelligence_daily_digest_v1` 等。

**新增数据源客户端（shared/storage/）**：
```python
from typing import Any, Dict, Optional
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

class NewDataSourceClient:
    """新数据源客户端（如 MongoDB/Redis 等）"""
    
    def __init__(self, url: str) -> None:
        self.url = url
        logger.info("Client initialized", extra={"url": url})
    
    async def query(self, **kwargs) -> Dict[str, Any]:
        """查询方法"""
        logger.info("Query called", extra=kwargs)
        # TODO: 实现真实逻辑
        return {}
```

**新增通用工具（shared/tools/）**：
```python
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

async def new_tool_function(param: str) -> str:
    """工具函数描述"""
    logger.info("Tool called", extra={"param": param})
    # TODO: 实现逻辑
    return "result"
```

### 3. 调用大模型的标准模式

```python
from shared.models.llm_manager import llm_manager

# 构造消息列表
messages = [
    {"role": "system", "content": "你是一个专业助手..."},
    {"role": "user", "content": f"用户查询：{user_query}"}
]

# 调用大模型（自动处理 API Key、重试、Token 统计）
response = await llm_manager.chat(
    messages=messages,
    model_name=None,        # None 表示使用默认模型
    temperature=0.2,
    max_tokens=1000
)

# response 是字符串类型，为模型返回的 content
```

**切换模型**：
1. 在 `config/model_config.yaml` 中添加新模型配置
2. 调用时传入 `model_name="新模型名称"`

### 4. 使用 RAG 检索的标准模式

```python
from shared.knowledge.rag_engine import RAGEngine
from shared.storage.es_client import ESClient
from shared.knowledge.vector_store import VectorStore

# 初始化（通常在服务启动时做一次）
es_client = ESClient(url=settings.service_config.es_url)
vector_store = VectorStore(url=settings.service_config.vector_url)
rag_engine = RAGEngine(es_client=es_client, vector_store=vector_store)

# 在 workflow 中调用
knowledge_docs = await rag_engine.retrieve_knowledge(
    query=user_query,
    domain="clinical_trials",  # 或 "patents", "reports" 等
    top_k=5
)

# 将检索结果拼进 prompt
context = "\n".join([doc["content"] for doc in knowledge_docs])
messages = [
    {"role": "system", "content": "你是助手..."},
    {"role": "user", "content": f"背景知识：\n{context}\n\n用户查询：{user_query}"}
]
```

---

## 常见任务的实现建议

### 任务 1: 为某个服务添加新的 API 端点

1. 在 `schema.py` 中定义新的请求/响应模型
2. 在 `workflows/` 中实现对应的流程函数
3. 在 `api.py` 中添加新的路由函数（装饰器 `@app.post("/xxx", ...)`）
4. 确保在 workflow 中调用 `shared/` 层能力，而非直接访问外部资源

### 任务 2: 接入新的大模型供应商

1. 在 `config/model_config.yaml` 中添加配置：
   ```yaml
   models:
     azure_gpt4:
       api_base: "https://your-azure-endpoint"
       model_name: "gpt-4"
       api_key_env: "AZURE_OPENAI_KEY"
   ```
2. 在 `.env` 中添加对应的 API Key：
   ```env
   AZURE_OPENAI_KEY=xxxxx
   ```
3. 在 `config/settings.py` 的 `Settings` 类中添加新字段：
   ```python
   azure_openai_key: Optional[str] = Field(default=None, validation_alias="AZURE_OPENAI_KEY")
   ```
4. `llm_manager.py` 会自动支持新模型（已实现通用逻辑）

### 任务 3: 添加新的数据源查询函数

1. 在 `shared/storage/` 中创建或修改对应的客户端文件
2. 定义业务语义化的查询函数（如 `search_xxx()`）
3. 函数签名示例：
   ```python
   async def search_xxx(
       es_client: ESClient,
       query: str,
       filters: Dict[str, Any],
       top_k: int = 10
   ) -> List[Dict[str, Any]]:
       """查询 XXX 数据源"""
       # 实现逻辑
   ```
4. 在服务的 workflow 中导入并调用该函数

### 任务 4: 服务间调用

假设情报服务需要调用 BD 服务：

```python
import httpx

async def call_bd_service(target: str) -> dict:
    """调用 BD 服务的分析接口"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "http://localhost:8002/bd/analyze",  # 或从 settings 读取地址
            json={"target": target, "context": None}
        )
        resp.raise_for_status()
        return resp.json()
```

**禁止**直接 `from core_agents.bd_service import xxx`。

---

## 日志规范

**统一使用 `shared/utils/logging_utils.py` 提供的日志工具**：

```python
from shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

# 基础日志
logger.info("Operation started")

# 结构化日志（推荐）
logger.info("User query received", extra={"query": user_query, "user_id": 123})

# 错误日志
try:
    result = await some_function()
except Exception as e:
    logger.error("Function failed", exc_info=True, extra={"error": str(e)})
```

**在服务入口（api.py）启动时初始化日志**：
```python
from shared.utils.logging_utils import setup_logging

setup_logging()  # 只需调用一次
```

---

## 测试规范（未来）

（第一期暂未包含测试，后续补充时遵循以下规范）

- 使用 `pytest` + `pytest-asyncio`
- 测试文件放在 `tests/` 目录，结构镜像 `core_agents/` 和 `shared/`
- 对外部依赖（ES/向量库/大模型）使用 mock
- FastAPI 测试使用 `from fastapi.testclient import TestClient`

---

## 代码风格与工具

- **类型注解**: 强制使用 Python 类型提示（`from typing import ...`）
- **格式化**: 建议使用 `black` 或 `ruff format`
- **Linting**: 建议使用 `ruff` 或 `pylint`
- **类型检查**: 建议使用 `mypy`（可选）

---

## 常见错误与解决方案

### 错误 1: ModuleNotFoundError: No module named 'config'

**原因**: 未设置 `PYTHONPATH`  
**解决**:
```bash
export PYTHONPATH=/path/to/LingNexus  # Linux/Mac
set PYTHONPATH=D:\LingNexus             # Windows CMD
$env:PYTHONPATH="D:\LingNexus"          # Windows PowerShell
```

或在 PyCharm/VSCode 中将项目根目录标记为 Sources Root。

### 错误 2: pydantic.ValidationError: 'OPENAI_API_KEY' field required

**原因**: `.env` 文件未创建或未设置环境变量  
**解决**:
1. 复制 `.env.example` 为 `.env`
2. 填入真实 API Key

### 错误 3: ImportError: attempted relative import beyond top-level package

**原因**: 违反了分层依赖规则（如 `shared/` 试图 import `core_agents/`）  
**解决**: 检查 import 语句，确保依赖方向正确。

### 错误 4: 服务启动后调用接口返回 500 错误

**排查步骤**:
1. 查看终端日志，定位具体报错
2. 检查 `.env` 中的 API Key 是否有效
3. 检查 `model_config.yaml` 中的 `api_base` 是否正确
4. 确认大模型接口可达（网络问题）

---

## 项目扩展建议

### 新增服务清单（示例）

- **市场分析服务**: 分析药物市场竞争格局
- **法规咨询服务**: 提供药监法规查询与解读
- **临床设计服务**: 辅助临床试验方案设计

每个新服务都应遵循 `core_agents/intelligence_service/` 的结构模式。

### RAG 优化方向

- 实现混合检索（BM25 + Dense Retrieval）
- 添加 Reranker 模型提升召回精度
- 实现查询改写与扩展（Query Expansion）
- 支持多轮对话的上下文管理

### 监控与可观测性

- 接入 Prometheus 采集指标（如 API 调用次数、延迟、Token 消耗）
- 使用 Grafana 可视化监控大盘
- 接入 ELK 或 Loki 进行日志聚合分析

---

## AI 编程助手使用建议

1. **优先参考现有服务结构**: 生成新代码时，参考 `intelligence_service` 的完整实现
2. **严格遵守分层约束**: 生成 import 语句时，检查是否违反依赖规则
3. **使用类型注解**: 所有函数参数和返回值都应有类型提示
4. **日志优先**: 在关键逻辑处添加结构化日志（`logger.info(..., extra={...})`）
5. **安全优先**: 生成涉及 API Key 的代码时，确保从环境变量读取，不要硬编码

---

## 快速命令参考

```bash
# 启动单个服务
uvicorn core_agents.intelligence_service.api:app --reload --port 8001

# Docker 构建单个服务
docker build -f infrastructure/docker/intelligence_service.Dockerfile -t lingnexus-intel .

# Docker Compose 启动所有服务
cd infrastructure/docker && docker-compose up

# 查看日志
docker-compose logs -f intelligence_service

# 停止所有服务
docker-compose down

# 初始化 ES 索引（示例脚本）
python infrastructure/scripts/init_es_indices.py
```

---

## 总结

本项目采用**严格分层 + 服务化**架构，核心目标是：

- **高内聚**：每个服务独立开发、测试、部署
- **低耦合**：通过 HTTP API 和共享能力层解耦
- **易扩展**：新增服务只需复制结构模板，填充业务逻辑

AI 编程助手在生成代码时，请务必遵守上述架构约束和代码模式，确保生成的代码与项目整体保持一致。

---

## Plugin 生态架构（重要补充）

### 概述

项目现已实现**三层插件化架构**：

```
Skill (能力层) → Plugin (插件层) → Plugin Store (用户层)
```

**设计目标**：
- Skill：底层原子能力，供开发者/Agent 使用
- Plugin：封装 Skill 为业务场景，面向终端用户
- Plugin Store：提供 Web UI，让用户零代码运行插件

### 目录结构

```
LingNexus/
├── plugin_store/                  # 插件商店
│   ├── backend/                   # BFF 层 (FastAPI, :8020)
│   │   └── api.py                 # 透传 Plugin Runtime API
│   └── frontend/                  # Web UI (React + Vite, :5173)
│       ├── src/pages/
│       │   ├── PluginList.tsx     # 插件列表
│       │   └── PluginDetail.tsx   # 插件详情 + 表单
│       └── vite.config.ts         # Vite 配置 (/api 代理到 8020)
│
├── plugin_runtime/                # 插件运行时 (FastAPI, :8015)
│   ├── server.py                 # FastAPI 应用入口
│   ├── manager.py                # 插件管理器
│   ├── plugin_loader.py          # 自动发现 plugins/
│   └── models.py                 # PluginManifest/Detail/StoreItem
│
└── plugins/                       # 插件安装目录
    ├── intel_daily_digest/
    │   ├── plugin_manifest.json  # 元信息 + input/output schema
    │   ├── main.py               # 入口函数 run_plugin()
    │   └── __init__.py
    └── news_quick_search/
        ├── plugin_manifest.json
        ├── main.py
        └── __init__.py
```

### 数据流向

```
用户在浏览器填写表单
    ↓
Plugin Store Frontend (5173)
    ↓ /api/plugins/{id}/run
Plugin Store Backend (8020)
    ↓ HTTP 请求
Plugin Runtime (8015)
    ↓ 加载并执行
plugins/ 目录中的插件
    ↓ get_skill()
调用底层 Skill
    ↓
返回结果 → 用户
```

### Plugin 开发模式

#### 1. 插件元信息 (plugin_manifest.json)

**关键字段**：
```json
{
  "plugin_id": "com.lingnexus.intel.news-quick-search",
  "version": "1.0.0",
  "name": "新闻快速搜索",
  "description": "插件简介",
  
  "required_skills": ["intel.fetch_news"],  // 声明依赖的 Skill
  "entrypoint": "plugins.news_quick_search.main:run_plugin",
  
  "input_schema": {
    "type": "object",          // 必须！符合 JSON Schema 标准
    "properties": {
      "topic_name": {
        "type": "string",
        "description": "搜索主题"
      }
    },
    "required": ["topic_name"]
  },
  
  "permissions": ["read_pharma_news"]
}
```

**关键约束**：
- ✅ `input_schema` **必须**有 `type: "object"` 和 `properties` 包装
- ✅ `required` 在顶层，而不是每个属性内
- ✅ `entrypoint` 使用 Python 导入路径（`模块:函数`）

#### 2. 插件入口函数 (main.py)

**模式 1：使用 @plugin_entrypoint 装饰器（推荐）**：
```python
from shared.skills.plugin import plugin_entrypoint
from shared.skills.registry import get_skill
from shared.skills.intelligence.fetch_news import FetchNewsInput

@plugin_entrypoint
async def run_plugin(payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None):
    # 1. 提取参数
    topic_name = payload.get("topic_name")
    keywords = payload.get("keywords", [])
    
    # 2. 获取 Skill（关键！）
    skill = get_skill("intel.fetch_news")
    if not skill:
        return {"status": "error", "error": "Skill 不可用"}
    
    # 3. 调用 Skill
    skill_output = await skill.execute(FetchNewsInput(
        topic_name=topic_name,
        keywords=keywords
    ))
    
    # 4. 返回用户友好格式
    return {
        "status": "success",
        "news_count": len(skill_output.data),
        "news_items": skill_output.data
    }
```

**模式 2：继承 BasePlugin 类**：
```python
from shared.skills.plugin import BasePlugin

class MyPlugin(BasePlugin):
    async def execute(self, payload, context):
        # 插件逻辑
        return {"status": "success"}

run_plugin = MyPlugin()
```

**关键设计原则**：
- ❗ **禁止在插件中重复实现业务逻辑**
- ✅ **必须通过 `get_skill()` 调用底层 Skill**
- ✅ 插件只负责：参数转换 + 结果格式化

#### 3. 自动发现机制

Plugin Runtime 启动时：
1. 扫描 `plugins/` 目录的所有 `plugin_manifest.json`
2. 验证 manifest 合法性
3. 动态导入 `entrypoint` 指定的函数
4. 注册到内存管理器

**关键代码**：
```python
# plugin_runtime/plugin_loader.py
def discover_manifests() -> List[PluginManifest]:
    plugins_dir = Path(__file__).parent.parent / "plugins"
    manifests = []
    for manifest_path in plugins_dir.rglob("plugin_manifest.json"):
        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = PluginManifest(**json.load(f))
            manifests.append(manifest)
    return manifests
```

### Plugin Store 前端特性

#### 1. 自动表单生成

基于 `input_schema` 自动生成输入表单：
- `type: "string"` → 文本输入框
- `type: "number"` → 数字输入框
- `type: "array"` → 多行文本框（每行一个值）
- `type: "string", enum: [...]` → 下拉选择框
- `required: [...]` → 必填标识（*）

**关键代码**：
```typescript
// plugin_store/frontend/src/pages/PluginDetail.tsx
const renderInputField = (key: string, schema: any) => {
  if (schema.type === 'string' && schema.enum) {
    return <select>...</select>;
  }
  if (schema.type === 'array') {
    return <textarea placeholder="每行一个值">...</textarea>;
  }
  return <input type="text" />;
};
```

#### 2. 插件运行流程

1. 用户在详情页填写表单
2. 点击“运行插件”
3. 前端收集表单数据，构造 `payload`
4. 调用 `/api/plugins/{id}/run` (8020)
5. Backend 透传到 `/plugins/{id}/invoke` (8015)
6. Runtime 加载插件并执行
7. 返回结果展示给用户

### API 端点

#### Plugin Runtime (8015)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/store/plugins` | GET | 获取所有插件列表 |
| `/plugins/{id}/detail` | GET | 获取插件详情 |
| `/plugins/{id}/invoke` | POST | 执行插件 |
| `/store/plugins/{id}/enable` | POST | 启用插件 |
| `/store/plugins/{id}/disable` | POST | 禁用插件 |

#### Plugin Store Backend (8020)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/plugins` | GET | 透传 Runtime 插件列表 |
| `/api/plugins/{id}` | GET | 透传 Runtime 插件详情 |
| `/api/plugins/{id}/run` | POST | 透传 Runtime 执行请求 |

### Skill → Plugin 转换流程

**场景**：将现有 Skill `intel.fetch_news` 转为插件

```bash
# 1. 确认 Skill 已注册
from shared.skills.registry import get_skill
get_skill("intel.fetch_news")  # 返回 Skill 实例

# 2. 创建插件目录
mkdir -p plugins/news_quick_search

# 3. 编写 plugin_manifest.json
# - 在 required_skills 中声明 "intel.fetch_news"
# - 定义 input_schema（符合 JSON Schema 标准）
# - 设置 entrypoint

# 4. 编写 main.py
# - 使用 @plugin_entrypoint 装饰器
# - 通过 get_skill("intel.fetch_news") 获取 Skill
# - 调用 skill.execute()
# - 返回用户友好格式

# 5. 创建 __init__.py
touch plugins/news_quick_search/__init__.py

# 6. 重启 Plugin Runtime
python -m uvicorn plugin_runtime.server:app --port 8015

# 7. 验证插件已上架
curl http://localhost:8015/store/plugins
```

### 服务启动顺序

```bash
# 1️⃣ 启动 Plugin Runtime（必需）
conda activate lingnexus
python -m uvicorn plugin_runtime.server:app --host 0.0.0.0 --port 8015

# 2️⃣ 启动 Plugin Store Backend（必需）
python -m uvicorn plugin_store.backend.api:app --host 0.0.0.0 --port 8020

# 3️⃣ 启动 Plugin Store Frontend（开发模式）
cd plugin_store/frontend
npm run dev
```

访问：http://localhost:5173

### AI 编程助手注意事项

1. **开发插件时**：
   - ✅ 必须使用 `@plugin_entrypoint` 装饰器
   - ✅ 必须通过 `get_skill()` 调用底层 Skill
   - ❗ 禁止在插件中重复实现逻辑
   - ✅ `input_schema` 必须符合 JSON Schema 标准

2. **修改 manifest 时**：
   - ✅ 确保 `type: "object"` 和 `properties` 存在
   - ✅ `required` 在顶层，而不是各属性内
   - ✅ `entrypoint` 使用正确的 Python 路径

3. **调试时**：
   - 查看 Plugin Runtime 日志：`tail -f logs/plugin_runtime.log`
   - 测试 API：`curl http://localhost:8015/store/plugins`
   - 检查 Skill 是否注册：`get_skill("skill_name")`

### 完整文档

**详细架构设计请参考**：`docs/skill_to_plugin_architecture.md`
