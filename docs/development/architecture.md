# 架构设计

> LingNexus 系统架构详解

---

## 目录

- [整体架构](#整体架构)
- [Monorepo 结构](#monorepo-结构)
- [Framework 架构](#framework-架构)
- [Platform 架构](#platform-架构)
- [数据流设计](#数据流设计)
- [安全架构](#安全架构)
- [部署架构](#部署架构)

---

## 整体架构

### 设计原则

1. **关注点分离**: Framework 负责核心能力，Platform 负责用户体验
2. **可组合性**: 小而独立的模块，通过组合实现复杂功能
3. **可扩展性**: 插件化架构，支持自定义扩展
4. **合规优先**: 满足医药行业监管要求

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      用户层 (Users)                          │
│  业务人员    │    IT人员    │   管理员   │   开发者         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                 Platform (Web 应用)                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Frontend (Vue 3)                                  │    │
│  │  ├─ Skill 编辑器    ├─ Agent 构建器  ├─ Skill 市场  │    │
│  │  └─ 用户管理       └─ 权限配置      └─ 审计日志     │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Backend (FastAPI)                                 │    │
│  │  ├─ REST API        ├─ WebSocket     ├─ 认证授权    │    │
│  │  └─ 数据库 CRUD    └─ 文件管理      └─ 审计日志    │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │ 依赖 (pip install lingnexus-framework)
┌────────────────────────┴────────────────────────────────────┐
│                  Framework (Python 包)                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Core Modules:                                     │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │    │
│  │  │  agent   │  │  skill   │  │    storage       │  │    │
│  │  │ Agent创建│  │ Skill管理│  │ 三层存储架构     │  │    │
│  │  └──────────┘  └──────────┘  └──────────────────┘  │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │    │
│  │  │scheduler │  │compliance│  │    security      │  │    │
│  │  │任务调度  │  │审计/合规 │  │ 加密/RBAC        │  │    │
│  │  └──────────┘  └──────────┘  └──────────────────┘  │    │
│  │  ┌──────────┐  ┌──────────────────────────────────┐ │    │
│  │  │integration│  │      intelligence              │ │    │
│  │  │数据源集成 │  │ 竞争情报采集（CDE/ClinicalTrials）│ │    │
│  │  └──────────┘  └──────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │ 依赖
┌────────────────────────┴────────────────────────────────────┐
│                     第三方库                                 │
│  ┌─────────────┐  ┌──────────┐  ┌──────────┐             │
│  │ AgentScope  │  │DashScope │  │Playwright │             │
│  │ Agent运行时  │  │ 模型API  │  │ 网页自动化 │             │
│  └─────────────┘  └──────────┘  └──────────┘             │
│  ┌─────────────┐  ┌──────────┐  ┌──────────┐             │
│  │ SQLAlchemy  │  │ChromaDB  │  │  Pydantic │             │
│  │    ORM      │  │ 向量数据库 │  │ 数据验证  │             │
│  └─────────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────────┘
```

---

## Monorepo 结构

### 目录组织

```
LingNexus/
├── packages/                        # 包目录
│   ├── framework/                   # 框架包
│   │   ├── lingnexus/              # 框架代码
│   │   │   ├── __init__.py         # 导出公共 API
│   │   │   ├── agent/              # Agent 模块
│   │   │   ├── skill/              # Skill 模块
│   │   │   ├── storage/            # 存储模块
│   │   │   ├── scheduler/          # 调度模块
│   │   │   ├── compliance/         # 合规模块
│   │   │   ├── security/           # 安全模块
│   │   │   ├── integration/        # 集成模块
│   │   │   ├── intelligence/       # 情报采集
│   │   │   ├── config/             # 配置管理
│   │   │   └── cli/                # CLI 工具
│   │   │
│   │   ├── tests/                  # 框架测试
│   │   │   ├── test_agent/
│   │   │   ├── test_skill/
│   │   │   └── test_integration/
│   │   │
│   │   ├── examples/               # 示例代码
│   │   ├── skills/                 # 示例 Skills
│   │   ├── pyproject.toml          # 包配置
│   │   └── README.md               # 框架文档
│   │
│   └── platform/                    # 平台包
│       ├── backend/                # FastAPI 后端
│       │   ├── api/                # API 路由
│       │   ├── models/             # 数据模型
│       │   ├── services/           # 业务逻辑
│       │   ├── core/               # 核心配置
│       │   └── main.py             # 应用入口
│       │
│       ├── frontend/               # Vue 3 前端
│       │   ├── src/
│       │   │   ├── api/            # API 客户端
│       │   │   ├── components/     # 组件
│       │   │   ├── views/          # 页面
│       │   │   ├── stores/         # 状态管理
│       │   │   └── router/         # 路由
│       │   ├── package.json
│       │   └── vite.config.ts
│       │
│       ├── docker/                 # 部署配置
│       │   ├── docker-compose.yml
│       │   └── Dockerfile
│       │
│       └── docs/                   # 平台文档
│           ├── user-guide.md
│           ├── admin-guide.md
│           └── deployment.md
│
├── scripts/                         # 开发脚本
│   ├── dev.sh                      # 启动开发环境
│   ├── build.sh                    # 构建所有包
│   ├── test.sh                     # 运行测试
│   └── release.sh                  # 发布到 PyPI/npm
│
├── docs/                            # 总文档
│   ├── README.md                   # 文档总览
│   ├── framework/                  # Framework 文档
│   ├── platform/                   # Platform 文档
│   └── development/                # 开发文档
│
├── pyproject.toml                  # 根项目配置（工作区）
├── README.md                       # 项目总览
├── CONTRIBUTING.md                 # 贡献指南
└── LICENSE                         # 许可证
```

### 工作区配置

```toml
# pyproject.toml (根)
[project]
name = "lingnexus-workspace"
version = "0.0.0"

[tool.uv.workspace]
members = [
    "packages/framework",
    "packages/platform/backend",
]

# 共享开发依赖
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

---

## Framework 架构

### 模块设计

#### 1. Agent 模块

**职责**: Agent 创建和运行

**核心类**:
```python
lingnexus/
├── agent/
│   ├── __init__.py              # 导出 create_progressive_agent
│   ├── react_agent.py           # 统一入口 ✅
│   ├── agent_factory.py         # 工厂实现
│   └── types.py                 # 类型定义
```

**设计模式**:
- **统一入口原则**: 所有 Agent 创建通过 `react_agent.py`
- **工厂模式**: `AgentFactory` 负责实际的 Agent 创建
- **策略模式**: 支持不同的 Agent 类型（progressive, docx）

**依赖关系**:
```
react_agent.py (用户 API)
    ↓
agent_factory.py (实现)
    ↓
model_config.py + skill_loader.py (依赖)
```

#### 2. Skill 模块

**职责**: Skill 加载、管理、渐进式披露

**核心类**:
```python
lingnexus/
└── skill/
    ├── __init__.py              # 导出 SkillLoader
    ├── loader.py                # Skill 加载器
    ├── registry.py              # Skill 注册表
    └── metadata.py              # 元数据管理
```

**渐进式披露实现**:
```python
class SkillLoader:
    def __init__(self):
        self._metadata_cache: Dict[str, Dict] = {}      # Phase 1 缓存
        self._instructions_cache: Dict[str, str] = {}    # Phase 2 缓存

    def get_skill_metadata(self, skill_name: str) -> Dict:
        """Phase 1: 获取元数据（~100 tokens）"""
        if skill_name not in self._metadata_cache:
            self._load_skill_metadata(skill_name)
        return self._metadata_cache[skill_name]

    def load_skill_instructions(self, skill_name: str) -> str:
        """Phase 2: 加载完整内容（~5k tokens）"""
        if skill_name not in self._instructions_cache:
            self._load_full_skill(skill_name)
        return self._instructions_cache[skill_name]

    def get_skill_resource_path(self, skill_name: str, path: str) -> Path:
        """Phase 3: 获取资源路径（按需）"""
        skill_dir = self._find_skill_dir(skill_name)
        return skill_dir / path
```

#### 3. Storage 模块

**职责**: 三层存储架构

**核心类**:
```python
lingnexus/
└── storage/
    ├── __init__.py
    ├── raw.py                    # 原始数据存储（文件系统）
    ├── structured.py             # 结构化存储（SQLite）
    └── vector.py                 # 向量存储（ChromaDB，可选）
```

**三层存储架构**:
```
┌─────────────────────────────────────────────┐
│  L1: Raw Storage (文件系统)                 │
│  data/raw/{source}/{date}/                  │
│  └─ 保存原始 HTML、JSON                     │
├─────────────────────────────────────────────┤
│  L2: Structured Storage (SQLite)            │
│  data/intelligence.db                       │
│  └─ 结构化数据，支持 SQL 查询               │
├─────────────────────────────────────────────┤
│  L3: Vector Storage (ChromaDB，可选)        │
│  data/vectordb/                             │
│  └─ 向量嵌入，支持语义搜索                  │
└─────────────────────────────────────────────┘
```

#### 4. Compliance 模块

**职责**: 审计日志、数据保留、电子签名

**核心类**:
```python
lingnexus/
└── compliance/
    ├── audit.py                  # 审计日志
    ├── retention.py              # 数据保留策略
    └── signature.py              # 电子签名
```

**审计日志流程**:
```
用户操作
    ↓
自动记录 (装饰器)
    ↓
AuditLogger.log()
    ↓
存储到数据库/文件
    ↓
支持导出（CSV/JSON）
```

#### 5. Security 模块

**职责**: 加密、脱敏、RBAC

**核心类**:
```python
lingnexus/
└── security/
    ├── crypto.py                 # 加密/解密
    ├── mask.py                   # 数据脱敏
    └── rbac.py                   # 基于角色的访问控制
```

**RBAC 权限模型**:
```
Role (角色)
    ├─ ADMIN (管理员)
    │   └─ 所有权限
    ├─ BUSINESS_USER (业务用户)
    │   ├─ skill:create
    │   ├─ skill:read
    │   ├─ agent:create
    │   └─ agent:run
    ├─ DATA_ANALYST (数据分析师)
    │   ├─ skill:read
    │   ├─ agent:run
    │   └─ data:export
    └─ VIEWER (查看者)
        └─ skill:read
```

---

## Platform 架构

### Backend 架构

**分层设计**:
```
┌─────────────────────────────────────┐
│  API Layer (api/)                   │
│  ├─ 认证和授权                      │
│  ├─ 请求验证                        │
│  └─ 响应格式化                      │
├─────────────────────────────────────┤
│  Service Layer (services/)          │
│  ├─ 业务逻辑                        │
│  ├─ 调用 Framework                 │
│  └─ 事务管理                        │
├─────────────────────────────────────┤
│  Data Layer (models/)               │
│  ├─ SQLAlchemy 模型                 │
│  └─ 数据库操作                      │
├─────────────────────────────────────┤
│  Framework (lingnexus-framework)    │
│  └─ 提供核心能力                    │
└─────────────────────────────────────┘
```

**API 设计**:
```
/api/v1/
├── auth/                    # 认证
│   ├── POST /register
│   ├── POST /login
│   └── GET  /me
├── skills/                  # Skills
│   ├── GET    /skills
│   ├── POST   /skills
│   ├── GET    /skills/{id}
│   ├── PUT    /skills/{id}
│   └── DELETE /skills/{id}
├── agents/                  # Agents
│   ├── GET    /agents
│   ├── POST   /agents
│   ├── POST   /agents/{id}/run
│   └── GET    /agents/{id}/logs
└── admin/                   # 管理员
    ├── GET    /audit-logs
    └── PUT    /users/{id}/role
```

### Frontend 架构

**组件结构**:
```
src/
├── api/                     # API 客户端
│   ├── client.ts            # Axios 实例
│   ├── auth.ts
│   ├── skills.ts
│   └── agents.ts
├── components/              # 通用组件
│   ├── common/              # Header, Footer, Loading
│   ├── skill/               # SkillCard, SkillEditor
│   ├── agent/               # AgentBuilder
│   └── ui/                  # MarkdownEditor, FileUpload
├── views/                   # 页面
│   ├── Auth/                # Login, Register
│   ├── Skills/              # SkillList, SkillDetail, SkillEdit
│   ├── Agents/              # AgentList, AgentBuilder
│   └── Dashboard/           # Overview
├── stores/                  # Pinia 状态管理
│   ├── auth.ts
│   ├── skill.ts
│   └── agent.ts
└── router/                  # Vue Router
    └── index.ts
```

**状态管理**:
```typescript
// stores/auth.ts
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  async function login(username: string, password: string) {
    const response = await authApi.login({ username, password })
    token.value = response.data.token
    user.value = response.data.user
  }

  return { user, token, login, logout }
})
```

---

## 数据流设计

### 1. 用户创建 Skill 流程

```
用户操作              Platform Backend        Framework          存储
   │                        │                   │                 │
   ├─ 填写表单  ───────────► ├─ 验证输入  ────────►                 │
   │                        │                   │                 │
   ├─ 上传文件  ───────────► ├─ 保存到文件系统 ──────────────────► │
   │                        │                   │                 │
   ├─ 提交     ───────────► ├─ 保存到数据库    ─────────────────► │
   │                        │                   │                 │
   │                        ├─ 注册 Skill ────► ├─ SkillLoader    │
   │                        │                   │  .register()    │
   │                        │                   │                 │
   └─ 显示结果  ◄───────────└─ 返回 Skill ID                      │
```

### 2. Agent 运行流程

```
用户操作              Platform Backend        Framework
   │                        │                   │
   ├─ 构建Agent  ─────────► ├─ 加载配置 ───────► ├─ create_agent()
   │                        │                   │  │
   │                        │                   │  ├─ 加载Skills
   │                        │                   │  └─ 初始化模型
   │                        │                   │
   ├─ 运行Agent  ─────────► ├─ 调用Framework ─► ├─ agent.execute()
   │                        │                   │  │
   │                        │                   │  ├─ 执行Skills
   │                        │                   │  ├─ LLM推理
   │                        │                   │  └─ 返回结果
   │                        │                   │
   │                        │                   │
   └─ 显示结果  ◄───────────└─ 返回响应 ◄────────┘
```

### 3. 监控任务流程

```
定时触发              Scheduler              Integration         Storage
   │                      │                      │                 │
   ├─ 每日执行  ─────────► ├─ 读取配置           │                 │
   │                      │                      │                 │
   │                      ├─ 遍历数据源  ────────► ├─ CDE Scraper
   │                      │                      ├─ ClinicalTrials
   │                      │                      └─ Insight
   │                      │                      │
   │                      ├─ 清洗数据           │                 │
   │                      │                      │                 │
   │                      ├─ 保存数据 ───────────────────────────► │
   │                      │  ├─ Raw Storage                     │
   │                      │  ├─ Structured DB                   │
   │                      │  └─ Vector DB (可选)               │
   │                      │                      │
   │                      ├─ 生成报告           │                 │
   │                      │                      │                 │
   └─ 查看结果  ◄──────────└─ 返回统计                              │
```

---

## 安全架构

### 1. 认证流程

```
用户                  Platform                Framework
│                       │                       │
├─ POST /login ────────►│                       │
│   {username, password} │                       │
│                       │                       │
│                       ├─ 验证密码 ────────────► │
│                       │  (bcrypt)              │
│                       │                       │
│                       ├─ 生成JWT              │
│                       │                       │
│◄──────── 返回token ────┘                       │
│                       │                       │
├─ 后续请求 + token ────►│                       │
│                       │                       │
│                       ├─ 验证JWT ────────────► │
│                       │  (security.auth)       │
│                       │                       │
│                       ├─ 检查权限 ───────────► │
│                       │  (security.rbac)       │
│                       │                       │
│◄────── 返回数据 ────────┘                       │
```

### 2. 数据加密

```python
# 敏感字段加密
user = User(
    email="user@example.com",
    phone_encrypted=encryption_service.encrypt("13800138000")
)

# 查询时自动解密
phone = encryption_service.decrypt(user.phone_encrypted)
```

### 3. 审计日志

```python
# 自动记录所有敏感操作
@audit.log(action=AuditAction.DELETE, resource_type="skill")
async def delete_skill(skill_id: str):
    # 删除操作
    pass
    # 自动记录审计日志
```

---

## 部署架构

### 开发环境

```
本地机器
├── Frontend (Vite Dev Server)
│   └─ http://localhost:5173
├── Backend (Uvicorn)
│   └─ http://localhost:8000
└─ Framework (本地依赖)
```

### 生产环境

```
┌─────────────────────────────────────────────────────┐
│                      Nginx                          │
│  (反向代理、SSL终止、静态文件)                       │
├─────────────────────────────────────────────────────┤
│  Frontend (静态文件)  │  Backend (Gunicorn)          │
│  /var/www/dist        │  :8000                       │
├─────────────────────────────────────────────────────┤
│  PostgreSQL          │  Redis        │  File Storage│
│  (元数据)             │  (缓存/队列)  │  (Skills)     │
└─────────────────────────────────────────────────────┘
```

### Docker Compose 部署

```yaml
services:
  frontend:
    image: lingnexus-frontend:1.0.0
    ports: ["80:80"]

  backend:
    image: lingnexus-backend:1.0.0
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/lingnexus
    depends_on: [db, redis]

  db:
    image: postgres:15
    volumes: ["postgres_data:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
```

---

## 扩展性设计

### 1. 插件化数据源

```python
# 实现自定义数据源
from lingnexus.integration import DataSourceAdapter

class MyDataSource(DataSourceAdapter):
    async def search_trials(self, keyword: str, max_results: int):
        # 实现搜索逻辑
        pass

# 注册使用
from lingnexus.scheduler import DailyMonitoringTask

task = DailyMonitoringTask()
task.register_data_source(MyDataSource(config))
```

### 2. 自定义 Skill 类型

```python
# 创建自定义 Skill 类型
from lingnexus.skill import SkillLoader

class CustomSkillLoader(SkillLoader):
    def load_skill_instructions(self, skill_name: str) -> str:
        # 自定义加载逻辑
        pass
```

---

**下一步**: [开发环境搭建](setup.md)
