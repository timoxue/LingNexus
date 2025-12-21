# LingNexus

> 基于 AgentScope 的医药智能服务平台  
> 采用"n8n 编排 + AgentScope 服务"架构，为 BD、情报、药物研发三大核心场景提供可编排的 AI 能力

---

## 📋 项目概述

LingNexus 是一个面向医药行业的 AI 智能服务平台，旨在通过微服务化的 Agent 架构，为业务团队提供：

- **情报分析服务**：整合多源数据（临床试验、专利、研报），提供智能分析与总结
- **BD 流程服务**：支持商务拓展场景的智能决策与推荐
- **药物研发服务**：提供化合物分析、预测等研发辅助能力

### 核心特性

- ✅ **服务化架构**：每个业务场景独立部署，可单独扩展
- ✅ **Skill 能力层**：底层原子能力，通过 `@register_skill` 注册，跨服务复用
- ✅ **Plugin 生态**：
  - 插件封装 Skill，面向终端用户
  - Plugin Store Web UI 提供可视化管理
  - 自动表单生成，零代码运行
- ✅ **统一配置管理**：环境变量 + YAML 配置，敏感信息安全隔离
- ✅ **能力层复用**：共享大模型、知识库、数据访问等核心能力
- ✅ **可编排接口**：通过 FastAPI 暴露标准 HTTP 端点，支持 n8n 等工具编排
- ✅ **容器化部署**：提供 Docker + docker-compose 一键启动方案

---

## 🏗️ 技术栈

- **Python**: 3.10
- **Web 框架**: FastAPI + Uvicorn
- **Agent 框架**: AgentScope >= 1.0.0
- **配置管理**: Pydantic Settings + python-dotenv + PyYAML
- **HTTP 客户端**: httpx
- **数据存储**: Elasticsearch（结构化数据）+ 向量数据库（语义检索）+ MySQL/PostgreSQL（关系数据）
- **部署**: Docker + docker-compose

---

## 📂 目录结构

```
LingNexus/
├── config/                        # 配置中心
│   ├── settings.py               # 主配置加载器（从 .env + YAML 加载）
│   ├── agentscope_config.yaml    # AgentScope 配置
│   ├── api_keys.yaml             # API 密钥配置（不提交到版本控制）
│   ├── api_keys.yaml.example     # API 密钥配置示例
│   ├── model_config.yaml         # 大模型配置（API 端点、模型名称）
│   └── service_config.yaml       # 服务端口、存储后端等配置
│
├── shared/                        # 能力支撑层（所有服务共享）
│   ├── knowledge/                 # 向量检索与知识管理
│   │   ├── rag_engine.py         # RAG 引擎（融合 ES + 向量检索）
│   │   └── vector_store.py       # 向量数据库客户端
│   ├── models/                    # 大模型统一管理
│   │   └── llm_manager.py        # 大模型调用、配置解析
│   ├── prompts/                   # Prompt 统一管理
│   │   ├── manager.py            # PromptManager 入口
│   │   ├── intelligence.yaml     # 情报服务 Prompt 集合
│   │   ├── bd.yaml               # BD 服务 Prompt 集合
│   │   └── rd.yaml               # RD 服务 Prompt 集合
│   ├── skills/                    # Skill 能力层（跨服务复用）
│   │   ├── intelligence/          # 情报领域 Skill
│   │   │   ├── fetch_news.py     # 新闻检索
│   │   │   └── generate_daily_digest.py  # 日报生成
│   │   ├── bd/                   # BD 领域 Skill
│   │   │   └── lead_qualification.py
│   │   ├── rd/                   # RD 领域 Skill
│   │   │   └── compound_analysis.py
│   │   ├── registry.py           # Skill 注册表
│   │   └── plugin.py             # 插件开发工具
│   ├── storage/                   # 统一数据访问层
│   │   ├── es_client.py          # ES 客户端（支持 local_file / remote_es）
│   │   ├── es_indices.py         # ES 索引配置
│   │   ├── es_query_medical.py   # 医药业务查询封装
│   │   └── rdb_client.py         # 关系型数据库客户端
│   ├── tools/                     # 全局工具库
│   │   ├── data_fetchers.py      # HTTP 数据抓取
│   │   ├── chemoinformatics.py   # 化学信息学计算
│   │   └── email_utils.py        # 邮件发送
│   ├── utils/                     # 基础设施工具
│   │   ├── logging_utils.py      # 结构化日志
│   │   ├── auth.py               # API 鉴权
│   │   └── cache_utils.py        # 缓存封装
│   └── __init__.py
│
├── core_agents/                   # 核心业务服务层（微服务）
│   ├── intelligence_service/      # 情报分析服务
│   │   ├── agents/               # Agent 定义
│   │   ├── tools/                # 服务内专用工具
│   │   ├── workflows/            # 工作流编排（含订阅日报）
│   │   ├── schema.py             # 请求/响应模型（Pydantic）
│   │   ├── api.py                # FastAPI 应用入口
│   │   └── __init__.py
│   ├── bd_service/               # BD 流程服务
│   │   ├── agents/
│   │   ├── tools/
│   │   ├── workflows/
│   │   ├── schema.py
│   │   ├── api.py
│   │   └── __init__.py
│   ├── rd_service/               # 药物研发服务
│   │   ├── agents/
│   │   ├── tools/
│   │   ├── workflows/
│   │   ├── schema.py
│   │   ├── api.py
│   │   └── __init__.py
│   └── __init__.py
│
├── plugin_runtime/                # 插件运行时服务
│   ├── server.py                 # FastAPI 服务（端口 8015）
│   ├── manager.py                # 插件管理器
│   ├── plugin_loader.py          # 自动发现插件
│   └── models.py                 # 数据模型
│
├── plugins/                       # 插件安装目录
│   ├── intel_daily_digest/       # 订阅日报插件
│   │   ├── plugin_manifest.json  # 插件元信息
│   │   ├── main.py               # 入口函数
│   │   └── __init__.py
│   └── news_quick_search/        # 新闻检索插件
│       ├── plugin_manifest.json
│       ├── main.py
│       └── __init__.py
│
├── plugin_store/                  # 插件商店
│   ├── backend/                   # BFF 层（端口 8020）
│   │   └── api.py
│   └── frontend/                  # Web UI（端口 5173）
│       ├── src/
│       │   ├── pages/
│       │   │   ├── PluginList.tsx
│       │   │   └── PluginDetail.tsx
│       │   └── api/
│       │       └── plugins.ts
│       └── vite.config.ts
│
├── infrastructure/                # 部署与运维
│   ├── docker/                   # Docker 相关文件
│   │   ├── intelligence_service.Dockerfile
│   │   ├── bd_service.Dockerfile
│   │   ├── rd_service.Dockerfile
│   │   └── docker-compose.yml    # 一键启动所有服务
│   └── scripts/                  # 运维/辅助脚本
│       ├── init_es_indices.py    # ES 索引初始化
│       └── test_prompt_manager.py# Prompt 管理测试脚本
│
├── docs/                          # 文档
│   ├── multi_model_usage_examples.md
│   ├── intelligence_subscription_daily_digest_design.md
│   ├── skill_capability_map_v0.1.md
│   ├── plugin_runtime_and_daily_digest_plugin_design.md
│   └── skill_to_plugin_architecture.md  # Skill → Plugin → Plugin Store 架构设计
│
├── .env.example                  # 环境变量示例
├── .gitignore
├── AGENT.md                      # 面向 AI 工具的项目说明
├── requirements.txt              # 依赖列表
└── README.md                     # 本文件
```

---

## 🚀 快速开始

### 部署模式选择

本项目支持三种部署模式，根据你的机器性能和需求选择：

#### **模式 A：极简开发模式（早期逻辑验证）**
- **适用场景**：初期 Prompt 调试、业务逻辑开发
- **存储后端**：
  - ES: `local_file` （从 JSON 文件读数据）
  - 向量库: `none` （内存简易实现）
- **优点**：无需任何数据库服务，可在任何笔记本上运行
- **缺点**：RAG 能力较弱，只能处理小量测试数据

#### **模式 B：轻量开发模式（推荐）**
- **适用场景**：笔记本本地开发，包含完整 RAG 流程
- **存储后端**：
  - ES: `local_file` （从 JSON 文件读数据）
  - 向量库: `chroma` （本地嵌入式向量库）
- **优点**：
  - 无需 Docker 或远程服务
  - 支持真实向量检索和 RAG
  - 占用资源少（内存 < 500MB）
- **缺点**：数据量仅适合数万条级别

#### **模式 C：生产模式**
- **适用场景**：服务器部署，大规模数据处理
- **存储后端**：
  - ES: `remote_es` （连接真实 Elasticsearch 服务）
  - 向量库: `milvus` （连接 Milvus 或 Zilliz Cloud）
- **优点**：
  - 生产级性能和稳定性
  - 支持百万级/千万级数据
  - 分布式架构支持
- **缺点**：需要额外服务器资源

---

### 1. 环境准备

```bash
# 克隆项目（或解压到本地）
cd LingNexus

# 创建虚拟环境（推荐，本地安装python3.10.x版本）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量与 API 密钥

#### 方式一：使用 api_keys.yaml（推荐）

复制示例文件并填入真实 API 密钥：

```bash
cp config/api_keys.yaml.example config/api_keys.yaml
```

编辑 `config/api_keys.yaml`，填入你的 API 密钥：

```yaml
# 至少配置一个模型供应商
deepseek:
  api_key: "sk-your-deepseek-key-here"
  base_url: "https://api.deepseek.com"
  model: "deepseek-chat"

qwen:
  api_key: "sk-your-qwen-key-here"
  base_url: "https://dashscope.aliyuncs.com/compatible-mode"
  model: "qwen-plus"
```

#### 方式二：使用环境变量（可选）

如果不使用 `api_keys.yaml`，可以通过环境变量配置：

复制 `.env.example` 为 `.env`，并填入真实配置：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
ENVIRONMENT=dev
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx  # 替换为你的 OpenAI API Key
```

> **注意**：如果使用其他模型供应商（如 Azure、智谱等），需同时修改 `config/model_config.yaml` 中的 `api_base` 和 `model_name`。

### 3. 选择部署模式（修改 service_config.yaml）

编辑 `config/service_config.yaml`，选择合适的后端模式：

#### **模式 A 配置（极简模式）**

```yaml
es_backend: "local_file"
vector_backend: "none"

es_url: null
vector_url: null
```

#### **模式 B 配置（轻量模式，默认）**

```yaml
es_backend: "local_file"
vector_backend: "chroma"  # 使用本地 Chroma 向量库

es_url: null
vector_url: null
```

然后安装 chromadb：

```bash
pip install chromadb
```

#### **模式 C 配置（生产模式）**

```yaml
es_backend: "remote_es"
vector_backend: "milvus"

es_url: "http://your-es-server:9200"
vector_url: "tcp://your-milvus-server:19530"
```

需要先搭建 Elasticsearch 和 Milvus 服务。

### 4. 准备测试数据（仅模式 A/B）

已提供示例数据文件 `data/clinical_trials.json`（包含 5 条临床试验数据）。

你可以添加更多数据到该文件，格式为 JSON 数组：

```json
[
  {
    "id": "NCT12345678",
    "title": "临床试验标题",
    "disease": "适应症",
    "phase": "III期",
    "description": "详细描述..."
  }
]
```

### 5. 启动服务

#### 方式一：单服务启动（开发调试）

```bash
# 启动情报分析服务（端口 8001）
uvicorn core_agents.intelligence_service.api:app --host 0.0.0.0 --port 8001

# 启动 BD 服务（端口 8002）
uvicorn core_agents.bd_service.api:app --host 0.0.0.0 --port 8002

# 启动 RD 服务（端口 8003）
uvicorn core_agents.rd_service.api:app --host 0.0.0.0 --port 8003
```

#### 方式二：Docker 一键启动（生产部署）

```bash
cd infrastructure/docker
docker-compose up --build
```

所有服务会自动启动：
- 情报服务：`http://localhost:8001`
- BD 服务：`http://localhost:8002`
- RD 服务：`http://localhost:8003`

### 6. 情报服务接口示例

#### 6.1 情报分析接口（外部）

```bash
curl -X POST "http://localhost:8001/intelligence/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "某抗肿瘤药物在中国的临床试验进展",
    "context": "关注近三年的III期临床",
    "top_k": 5
  }'
```

#### 6.2 订阅日报接口（内部，供 n8n 调用）

- 路径：`POST /v1/internal/daily_digest`
- 用途：根据 **主题列表 + 用户列表** 生成情报订阅日报，可按角色（BD/医学/市场等）生成多版本摘要。
- 示例请求：

```json
{
  "topics": [
    {
      "topic_id": "t1",
      "name": "PD-1 肺癌",
      "description": "关注 PD-1 相关的肺癌适应症与临床进展",
      "keywords": ["PD-1", "肺癌", "NSCLC"],
      "max_items": 5
    }
  ],
  "users": [
    {
      "user_id": "u_bd",
      "email": "bd@example.com",
      "subscribed_topics": ["t1"],
      "role": "bd"
    }
  ]
}
```

返回示例（结构）：

```json
{
  "task_id": "daily_xxx",
  "status": "completed",
  "items": [
    {
      "topic": { "topic_id": "t1", "name": "PD-1 肺癌", "max_items": 5 },
      "news": [ { "id": "NEWS_0001", "title": "..." } ],
      "digest_summary": "这里是一整篇可直接推送的订阅日报文本",
      "role": "bd"
    }
  ]
}
```

### 7. 联调与测试用例

#### 7.1 情报订阅日报最小联调

- **前置条件**：
  - 已按模式 B 配置好 `service_config.yaml`，并启动 `intelligence_service`：`uvicorn core_agents.intelligence_service.api:app --host 0.0.0.0 --port 8001`。
- **请求示例**：
  - 端点：`POST http://localhost:8001/v1/internal/daily_digest`
  - 请求体：使用上方示例 JSON（`topics` + `users`，其中 `role` 可为 `bd`/`med`/`market` 等）。
- **预期结果**：
  - 返回 `task_id` + 若干 `items`，每个 `item` 中 `digest_summary` 为可直接推送的订阅日报文本，`news` 中包含已去重、排序后的资讯列表。

#### 7.2 BD 线索评估接口联调

- **前置条件**：
  - 启动 BD 服务：`uvicorn core_agents.bd_service.api:app --host 0.0.0.0 --port 8002`（或你本地正在使用的端口）。
- **请求示例**：
  - 端点：`POST http://localhost:8002/bd/analyze`
  - 请求体：
    ```json
    {
      "target": "XX生物-ADC合作机会",
      "context": "对方在HER2 ADC领域有III期临床，近期完成一轮C轮融资"
    }
    ```
- **链路说明**：
  - Workflow `run_bd_pipeline` 会通过 Skill Registry 调用 `bd.lead_qualification`；
  - Skill 内部使用 `bd.yaml` 中的 Prompt 和 `llm_manager` 调用大模型，返回一段 BD 线索评估总结填充到 `BDResponse.summary` 中。

#### 7.3 RD 化合物分析接口联调

- **前置条件**：
  - 启动 RD 服务：`uvicorn core_agents.rd_service.api:app --host 0.0.0.0 --port 8003`。
- **请求示例**：
  - 端点：`POST http://localhost:8003/rd/analyze`
  - 请求体：
    ```json
    {
      "compound": "AZD1234",
      "context": "小分子口服EGFR抑制剂，拟用于晚期NSCLC二线治疗"
    }
    ```
- **链路说明**：
  - Workflow `run_rd_pipeline` 会调用技能 `rd.compound_analysis`；
  - Skill 会使用 `rd.yaml` 中的 Prompt + DeepSeek 模型，生成化合物分析文本，返回到 `RDResponse.summary`。

#### 7.4 Prompt 管理测试脚本

- **脚本位置**：`infrastructure/scripts/test_prompt_manager.py`
- **运行方式**：
  ```bash
  cd infrastructure/scripts
  python test_prompt_manager.py
  ```
- **测试内容**：
  - 自动列出 intelligence / BD / RD 服务下的所有 Prompt；
  - 验证 `render`、`get_metadata`、错误处理等逻辑是否正常工作。

---

## 🔧 开发指南

### 核心设计原则

1. **分层架构约束**
   - `config/` 只被其他层依赖，不依赖业务代码
   - `shared/` 被 `core_agents/` 使用，但不依赖具体服务
   - `core_agents/` 各服务之间**不允许直接 Python import**，必须通过 HTTP 调用

2. **配置与安全**
   - 所有敏感信息（API Key、密码）**只能**放在 `.env` 中
   - YAML 配置文件只存放非敏感的结构化配置
   - `config/settings.py` 统一加载并对外暴露 `settings` 单例

3. **数据访问封装**
   - 禁止在 Agent 中直接连接数据库或外部 API
   - 所有数据访问必须通过 `shared/storage`、`shared/knowledge`、`shared/tools` 封装

4. **服务契约**
   - 每个服务的 `schema.py` 定义清晰的 Pydantic 请求/响应模型
   - 这些模型用于 FastAPI 参数校验、自动文档生成、与 n8n 的接口契约

### 添加新服务

参考现有三大服务（intelligence/bd/rd）的结构，创建新服务：

```bash
mkdir -p core_agents/new_service/{agents,workflows,tools}
touch core_agents/new_service/{__init__.py,schema.py,api.py}
touch core_agents/new_service/workflows/{__init__.py,new_workflow.py}
```

在 `schema.py` 中定义请求/响应模型，在 `workflows/` 中实现业务逻辑，在 `api.py` 中暴露 FastAPI 端点。

### 扩展共享能力

- **新增数据源**：在 `shared/storage/` 中添加新的客户端封装
- **新增工具**：在 `shared/tools/` 中添加通用工具函数
- **新增模型**：在 `config/model_config.yaml` 中配置新模型，`llm_manager` 会自动支持

---

## 📊 架构图

```
┌─────────────────────────────────────────────────────────┐
│                       n8n 编排层                         │
│  (通过 HTTP 调用各服务的 API 端点，实现复杂业务流程)      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼───┐  ┌───▼────┐  ┌──▼─────┐
    │情报服务│  │BD 服务 │  │RD 服务 │  ← core_agents/
    │ :8001  │  │ :8002  │  │ :8003  │    (微服务层)
    └────┬───┘  └───┬────┘  └──┬─────┘
         │          │          │
         └──────────┼──────────┘
                    │ 调用共享能力
         ┌──────────▼──────────┐
         │    shared/          │  ← 能力支撑层
         │  ┌────────────────┐ │
         │  │ models/        │ │  (大模型管理)
         │  │ knowledge/     │ │  (RAG 引擎)
         │  │ storage/       │ │  (数据访问)
         │  │ tools/         │ │  (工具库)
         │  └────────────────┘ │
         └─────────────────────┘
                    │
         ┌──────────▼──────────┐
         │  外部系统/数据源     │
         │  (ES/向量库/MySQL)  │
         └─────────────────────┘
```

---

## 🧪 测试

（第一期暂未包含测试代码，后续可在 `tests/` 目录添加单元测试与集成测试）

---

## 📝 待办事项（Roadmap）

### 已完成 ✅

- [x] 搭建微服务框架（情报/BD/RD 三大服务）
- [x] 配置管理系统（`.env` + `service_config.yaml` + `api_keys.yaml` + `model_config.yaml`）
- [x] 多模型支持（DeepSeek / Qwen / Gemini），并在 `docs/multi_model_usage_examples.md` 中给出示例
- [x] Prompt 统一管理系统（`shared/prompts` + `PromptManager` + 测试脚本 `test_prompt_manager.py`）
- [x] **轻量开发模式（模式 B）**：
  - `local_file` ES 后端
  - Chroma 本地向量库
  - 示例数据文件（临床试验 + 医药资讯）
- [x] 情报订阅日报链路（intelligence_service）：
  - `DailyDigestWorkflow` + `POST /v1/internal/daily_digest`
  - 订阅业务设计文档：`docs/intelligence_subscription_daily_digest_design.md`
- [x] Skill 层引入与三域代表性技能：
  - Intelligence：`intel.fetch_news`、`intel.generate_daily_digest`
  - BD：`bd.lead_qualification`
  - RD：`rd.compound_analysis`
  - 对应 Workflow 已通过 Skill Registry 调用这些技能
- [x] README / AGENT.md / docs 的首轮对齐更新（目录结构、Skill 架构、联调测试用例）
- [x] 插件运行时 MVP + 首个订阅日报插件（`plugin_runtime/` + `plugins/intel_daily_digest`），并在 docs 中补充设计说明
- [x] **Plugin 生态完善**：
  - Plugin Store 前后端（React + FastAPI）
  - 插件自动发现机制（扫描 `plugins/` 目录）
  - 基于 JSON Schema 自动生成表单
  - Skill → Plugin 转换流程与最佳实践
  - 完整架构文档：`docs/skill_to_plugin_architecture.md`

### 进行中 🚧

- [ ] 持续丰富 BD 服务与 RD 服务的业务逻辑（在现有 Skill 基础上扩展更多场景）
- [ ] 梳理并补充自动化测试（单元测试 + 集成测试），规划统一的 `tests/` 结构

### 计划中 📋

- [ ] **生产模式（模式 C）支持**：
  - 接入真实 Elasticsearch 服务
  - 接入 Milvus 向量数据库
  - Docker Compose 部署配置完善
- [ ] 接入 Prometheus + Grafana 监控
- [ ] 在文档中增加“跨域 Skill 能力地图”（列出现有 `intel.*` / `bd.*` / `rd.*` 技能及适用场景）
- [ ] 完善 n8n webhook 配置示例（围绕订阅日报 + BD/RD 流程编排）
- [ ] 添加 Redis 缓存层（`shared/utils/cache_utils.py` 与实际 Redis 部署联通）

---

## 🤝 贡献指南

1. 所有代码修改需遵循分层架构原则
2. 新增配置项需在 `.env.example` 中补充示例
3. 新增 API 端点需在对应服务的 `schema.py` 中定义 Pydantic 模型
4. 提交前确保代码通过静态检查（如 `mypy`、`ruff`）

---

## 📄 许可证

（根据实际情况填写）

---

## 📮 联系方式

（根据实际情况填写）
