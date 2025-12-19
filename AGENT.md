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

### 1. 新增服务（core_agents/xxx_service/）

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
