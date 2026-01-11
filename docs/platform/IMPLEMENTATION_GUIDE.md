# Platform 实现指南

> LingNexus Platform 低代码平台完整实现方案

## 目录

- [功能需求分析](#功能需求分析)
- [技术架构设计](#技术架构设计)
- [API 设计规范](#api-设计规范)
- [数据库设计](#数据库设计)
- [前端页面设计](#前端页面设计)
- [开发优先级](#开发优先级)
- [需要补充的文档](#需要补充的文档)

---

## 功能需求分析

### 核心 MVP 功能（最小可行产品）

#### 1. 用户管理（P0）

**功能点**：
- 用户注册/登录
- JWT 令牌认证
- 基础权限控制（普通用户/管理员）
- 个人信息管理

**API 端点**：
```
POST   /api/v1/auth/register       # 用户注册
POST   /api/v1/auth/login          # 用户登录
POST   /api/v1/auth/logout         # 用户登出
GET    /api/v1/auth/me             # 获取当前用户信息
PUT    /api/v1/auth/me             # 更新用户信息
POST   /api/v1/auth/change-password # 修改密码
```

#### 2. Skill 管理（P0）

**功能点**：
- Skill 列表查询（分页、搜索、过滤）
- Skill 创建（表单提交）
- Skill 编辑
- Skill 删除
- Skill 详情查看
- Skill 文件上传（SKILL.md, scripts/, references/）
- Skill 版本管理

**数据模型**：
```python
class Skill(BaseModel):
    id: int
    name: str                        # Skill 名称
    description: str                 # 描述
    category: str                    # 分类：external/internal
    author_id: int                   # 创建者 ID
    content: Text                    # SKILL.md 内容
    metadata: JSON                   # 元数据（YAML front matter）
    version: str                     # 版本号
    is_active: bool                  # 是否启用
    created_at: datetime
    updated_at: datetime
```

**API 端点**：
```
GET    /api/v1/skills               # 获取 Skill 列表
POST   /api/v1/skills               # 创建 Skill
GET    /api/v1/skills/{id}          # 获取 Skill 详情
PUT    /api/v1/skills/{id}          # 更新 Skill
DELETE /api/v1/skills/{id}          # 删除 Skill
POST   /api/v1/skills/{id}/upload    # 上传 Skill 文件
GET    /api/v1/skills/{id}/versions # 获取版本历史
```

#### 3. Agent 管理（P0）

**功能点**：
- Agent 列表查询
- Agent 创建（配置名称、模型、参数）
- Agent 编辑
- Agent 删除
- Agent 详情查看
- Agent 执行（手动触发）

**数据模型**：
```python
class Agent(BaseModel):
    id: int
    name: str                        # Agent 名称
    description: str                 # 描述
    model_name: str                  # 模型名称（qwen-max）
    model_type: str                  # 模型类型（qwen/deepseek）
    temperature: float               # 温度参数
    max_tokens: int                  # 最大 token 数
    skills: List[int]                # 关联的 Skill IDs
    system_prompt: str               # 系统提示词
    config: JSON                     # 其他配置
    author_id: int                   # 创建者 ID
    created_at: datetime
    updated_at: datetime
```

**API 端点**：
```
GET    /api/v1/agents               # 获取 Agent 列表
POST   /api/v1/agents               # 创建 Agent
GET    /api/v1/agents/{id}          # 获取 Agent 详情
PUT    /api/v1/agents/{id}          # 更新 Agent
DELETE /api/v1/agents/{id}          # 删除 Agent
POST   /api/v1/agents/{id}/execute  # 执行 Agent
```

#### 4. 监控数据展示（P0）

**功能点**：
- 项目列表展示
- 试验数据列表（分页、搜索、过滤）
- 试验详情查看
- 数据统计（总数、状态分布）
- 数据导出（Excel/CSV）

**API 端点**：
```
GET    /api/v1/monitoring/projects      # 获取监控项目列表
GET    /api/v1/monitoring/trials        # 获取试验列表
GET    /api/v1/monitoring/trials/{id}   # 获取试验详情
GET    /api/v1/monitoring/statistics    # 获取统计数据
GET    /api/v1/monitoring/export        # 导出数据
```

### 次要功能（P1）

#### 5. 任务调度（P1）

**功能点**：
- 创建定时任务
- 查看任务列表
- 启动/停止任务
- 查看任务执行历史

#### 6. 工作流编排（P1）

**功能点**：
- 可视化工作流编辑器
- 节点类型：输入、输出、Skill、条件、循环
- 工作流保存/加载
- 工作流执行

#### 7. 数据存储管理（P2）

**功能点**：
- 查看原始数据
- 数据清理
- 数据导出

---

## 技术架构设计

### Backend 架构

```
packages/platform/backend/
├── api/                          # API 路由
│   ├── __init__.py
│   ├── dependencies.py          # 依赖注入
│   ├── v1/                      # API v1
│   │   ├── __init__.py
│   │   ├── auth.py              # 认证相关
│   │   ├── skills.py            # Skill 管理
│   │   ├── agents.py            # Agent 管理
│   │   ├── monitoring.py        # 监控数据
│   │   └── tasks.py             # 任务调度
│   └── middleware.py            # 中间件
│
├── core/                         # 核心业务逻辑
│   ├── __init__.py
│   ├── auth.py                  # 认证逻辑
│   ├── security.py              # 安全相关（JWT, 密码哈希）
│   └── config.py                # 配置管理
│
├── models/                       # 数据模型
│   ├── __init__.py
│   ├── user.py                  # 用户模型
│   ├── skill.py                 # Skill 模型
│   ├── agent.py                 # Agent 模型
│   └── task.py                  # 任务模型
│
├── schemas/                      # Pydantic schemas
│   ├── __init__.py
│   ├── user.py                  # 用户 schemas
│   ├── skill.py                 # Skill schemas
│   ├── agent.py                 # Agent schemas
│   └── common.py                # 通用 schemas
│
├── services/                     # 业务服务层
│   ├── __init__.py
│   ├── skill_service.py         # Skill 业务逻辑
│   ├── agent_service.py         # Agent 业务逻辑
│   ├── monitoring_service.py    # 监控业务逻辑
│   └── auth_service.py          # 认证业务逻辑
│
├── db/                           # 数据库
│   ├── __init__.py
│   ├── session.py               # 数据库 session
│   ├── base.py                  # Base 类
│   └── init_db.py               # 初始化脚本
│
├── scripts/                      # 脚本
│   └── init_db.py               # 初始化数据库
│
├── main.py                       # FastAPI 应用入口
├── config.py                     # 配置文件
└── requirements.txt              # 依赖（通过 pyproject.toml 管理）
```

### Frontend 架构

```
packages/platform/frontend/src/
├── components/                   # 组件
│   ├── common/                  # 通用组件
│   │   ├── Header.vue           # 头部导航
│   │   ├── Sidebar.vue          # 侧边栏
│   │   ├── Pagination.vue       # 分页
│   │   └── ConfirmDialog.vue    # 确认对话框
│   │
│   ├── skills/                  # Skill 相关
│   │   ├── SkillList.vue        # Skill 列表
│   │   ├── SkillCard.vue        # Skill 卡片
│   │   ├── SkillForm.vue        # Skill 表单
│   │   ├── SkillDetail.vue      # Skill 详情
│   │   └── SkillUploader.vue    # 文件上传
│   │
│   ├── agents/                  # Agent 相关
│   │   ├── AgentList.vue        # Agent 列表
│   │   ├── AgentCard.vue        # Agent 卡片
│   │   ├── AgentForm.vue        # Agent 表单
│   │   ├── AgentExecutor.vue    # Agent 执行器
│   │   └── SkillSelector.vue    # Skill 选择器
│   │
│   └── monitoring/              # 监控相关
│       ├── ProjectList.vue      # 项目列表
│       ├── TrialTable.vue       # 试验表格
│       ├── TrialDetail.vue      # 试验详情
│       └── Statistics.vue       # 统计图表
│
├── views/                        # 页面视图
│   ├── Dashboard.vue            # 仪表板
│   ├── SkillsView.vue           # Skills 管理
│   ├── AgentsView.vue           # Agents 管理
│   ├── MonitoringView.vue       # 监控数据
│   ├── TasksView.vue            # 任务调度
│   └── SettingsView.vue         # 设置
│
├── router/                       # 路由
│   ├── index.ts
│   └── routes.ts                # 路由配置
│
├── stores/                       # 状态管理（Pinia）
│   ├── user.ts                  # 用户状态
│   ├── skill.ts                 # Skill 状态
│   ├── agent.ts                 # Agent 状态
│   └── monitoring.ts            # 监控状态
│
├── api/                          # API 调用
│   ├── client.ts                # Axios 客户端
│   ├── auth.ts                  # 认证 API
│   ├── skills.ts                # Skills API
│   ├── agents.ts                # Agents API
│   └── monitoring.ts            # 监控 API
│
├── types/                        # TypeScript 类型
│   ├── user.ts
│   ├── skill.ts
│   ├── agent.ts
│   └── monitoring.ts
│
├── utils/                        # 工具函数
│   ├── request.ts              # 请求封装
│   ├── validation.ts            # 数据验证
│   └── format.ts                # 格式化工具
│
├── styles/                       # 样式文件
│   ├── main.scss                # 主样式
│   ├── variables.scss           # 变量
│   └── mixins.scss              # 混入
│
├── App.vue                       # 根组件
├── main.ts                       # 入口文件
└── vite.config.ts               # Vite 配置
```

---

## API 设计规范

### RESTful API 规范

**基础 URL**: `/api/v1`

#### 通用响应格式

**成功响应**：
```json
{
  "code": 200,
  "message": "Success",
  "data": { ... }
}
```

**错误响应**：
```json
{
  "code": 400,
  "message": "Error message",
  "details": { ... }
}
```

**分页响应**：
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [ ... ],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "pages": 5
  }
}
```

#### 认证 API

**1. 用户注册**
```
POST /api/v1/auth/register

Request:
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}

Response (201):
{
  "code": 201,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "created_at": "2025-01-10T12:00:00Z"
  }
}
```

**2. 用户登录**
```
POST /api/v1/auth/login

Request:
{
  "username": "john_doe",
  "password": "securepassword123"
}

Response (200):
{
  "code": 200,
  "message": "Login successful",
  "data": {
    "access_token": "eyJ0eXAiOiJ...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com"
    }
  }
}
```

#### Skill API

**1. 获取 Skill 列表**
```
GET /api/v1/skills?page=1&page_size=20&category=external&search=docx&is_active=true

Response (200):
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "docx",
        "description": "Word document generation",
        "category": "external",
        "author": {
          "id": 1,
          "username": "admin"
        },
        "version": "1.0.0",
        "is_active": true,
        "created_at": "2025-01-10T12:00:00Z"
      }
    ],
    "total": 45,
    "page": 1,
    "page_size": 20,
    "pages": 3
  }
}
```

**2. 创建 Skill**
```
POST /api/v1/skills
Authorization: Bearer {access_token}

Request:
{
  "name": "my-skill",
  "description": "My custom skill",
  "category": "internal",
  "content": "# My Skill\n\n...",
  "metadata": {
    "temperature": 0.7,
    "max_tokens": 2000
  }
}

Response (201):
{
  "code": 201,
  "message": "Skill created successfully",
  "data": {
    "id": 46,
    "name": "my-skill",
    "description": "My custom skill",
    ...
  }
}
```

#### Agent API

**1. 创建 Agent**
```
POST /api/v1/agents
Authorization: Bearer {access_token}

Request:
{
  "name": "Research Assistant",
  "description": "Helps with pharmaceutical research",
  "model_name": "qwen-max",
  "model_type": "qwen",
  "temperature": 0.3,
  "max_tokens": 4000,
  "system_prompt": "You are a helpful research assistant...",
  "skill_ids": [1, 2, 5],
  "config": {
    "enable_code_execution": true
  }
}

Response (201):
{
  "code": 201,
  "message": "Agent created successfully",
  "data": {
    "id": 10,
    "name": "Research Assistant",
    ...
  }
}
```

**2. 执行 Agent**
```
POST /api/v1/agents/{id}/execute
Authorization: Bearer {access_token}

Request:
{
  "message": "分析司美格鲁肽的最新临床试验数据",
  "parameters": {
    "stream": false
  }
}

Response (200):
{
  "code": 200,
  "message": "Agent executed successfully",
  "data": {
    "response": "根据数据分析...",
    "tokens_used": 1234,
    "execution_time": 3.45
  }
}
```

#### 监控 API

**1. 获取试验列表**
```
GET /api/v1/monitoring/trials?project=司美格鲁肽&page=1&page_size=20&status=进行中

Response (200):
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [
      {
        "id": 1,
        "nct_id": "NCT06989203",
        "title": "Study of Semaglutide...",
        "status": "进行中",
        "start_date": "2025-01-01",
        "completion_date": null,
        "phase": "Phase 3",
        "source": "ClinicalTrials.gov"
      }
    ],
    "total": 150,
    "page": 1,
    "page_size": 20,
    "pages": 8
  }
}
```

---

## 数据库设计

### 表结构

#### 1. users 表

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

#### 2. skills 表

```sql
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(20) NOT NULL,  -- 'external' or 'internal'
    author_id INTEGER REFERENCES users(id),
    content TEXT NOT NULL,            -- SKILL.md content
    metadata JSONB,                   -- YAML front matter
    version VARCHAR(20) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_skills_name ON skills(name);
CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_author ON skills(author_id);
CREATE INDEX idx_skills_active ON skills(is_active);
```

#### 3. skills_agents 表（关联表）

```sql
CREATE TABLE skills_agents (
    skill_id INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    agent_id INTEGER REFERENCES agents(id) ON DELETE CASCADE,
    PRIMARY KEY (skill_id, agent_id)
);
```

#### 4. agents 表

```sql
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    model_name VARCHAR(50) NOT NULL,
    model_type VARCHAR(20) NOT NULL,
    temperature DECIMAL(3, 2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 2000,
    system_prompt TEXT,
    config JSONB,
    author_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agents_name ON agents(name);
CREATE INDEX idx_agents_author ON agents(author_id);
```

#### 5. agent_executions 表（执行历史）

```sql
CREATE TABLE agent_executions (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES agents(id),
    user_id INTEGER REFERENCES users(id),
    input_message TEXT NOT NULL,
    output_message TEXT,
    tokens_used INTEGER,
    execution_time DECIMAL(5, 2),
    status VARCHAR(20),  -- 'success', 'error', 'pending'
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_executions_agent ON agent_executions(agent_id);
CREATE INDEX idx_executions_user ON agent_executions(user_id);
CREATE INDEX idx_executions_created ON agent_executions(created_at);
```

#### 6. monitoring_projects 表

```sql
CREATE TABLE monitoring_projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(50),
    keywords JSONB,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 7. clinical_trials 表

```sql
CREATE TABLE clinical_trials (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES monitoring_projects(id),
    source VARCHAR(50) NOT NULL,  -- 'ClinicalTrials.gov', 'CDE'
    nct_id VARCHAR(50),
    registration_number VARCHAR(100),
    title TEXT,
    status VARCHAR(50),
    phase VARCHAR(20),
    start_date DATE,
    completion_date DATE,
    study_design TEXT,
    json_data JSONB,  -- 存储完整的原始数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trials_project ON clinical_trials(project_id);
CREATE INDEX idx_trials_source ON clinical_trials(source);
CREATE INDEX idx_trials_nct ON clinical_trials(nct_id);
CREATE INDEX idx_trials_status ON clinical_trials(status);
```

### SQLAlchemy 模型

**`packages/platform/backend/db/models.py`**：

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, DECIMAL, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skills = relationship("Skill", back_populates="author")
    agents = relationship("Agent", back_populates="author")
    executions = relationship("AgentExecution", back_populates="user")

class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(20), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), index=True)
    content = Column(Text, nullable=False)
    metadata = Column(JSON)
    version = Column(String(20), default="1.0.0")
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="skills")
    agents = relationship("Agent", secondary="skills_agents", back_populates="skills")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    model_name = Column(String(50), nullable=False)
    model_type = Column(String(20), nullable=False)
    temperature = Column(DECIMAL(3, 2), default=0.7)
    max_tokens = Column(Integer, default=2000)
    system_prompt = Column(Text)
    config = Column(JSON)
    author_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = relationship("User", back_populates="agents")
    skills = relationship("Skill", secondary="skills_agents", back_populates="agents")
    executions = relationship("AgentExecution", back_populates="agent")

class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    input_message = Column(Text, nullable=False)
    output_message = Column(Text)
    tokens_used = Column(Integer)
    execution_time = Column(DECIMAL(5, 2))
    status = Column(String(20))  # 'success', 'error', 'pending'
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    agent = relationship("Agent", back_populates="executions")
    user = relationship("User", back_populates="executions")

class MonitoringProject(Base):
    __tablename__ = "monitoring_projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    category = Column(String(50))
    keywords = Column(JSON)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ClinicalTrial(Base):
    __tablename__ = "clinical_trials"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("monitoring_projects.id"), index=True)
    source = Column(String(50), nullable=False, index=True)
    nct_id = Column(String(50), index=True)
    registration_number = Column(String(100))
    title = Column(Text)
    status = Column(String(50), index=True)
    phase = Column(String(20))
    start_date = Column(Date)
    completion_date = Column(Date)
    study_design = Column(Text)
    json_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("MonitoringProject")
```

---

## 前端页面设计

### 页面列表和优先级

#### P0（必须）

**1. 登录/注册页面** (`/login`, `/register`)
- 登录表单
- 注册表单
- 忘记密码

**2. Dashboard** (`/`)
- 统计卡片（Skills 数量、Agents 数量、试验数量）
- 最近活动
- 快捷操作

**3. Skills 管理页面** (`/skills`)
- Skill 列表（表格/卡片视图）
- 搜索和过滤
- 创建 Skill 按钮
- Skill 详情弹窗/抽屉

**4. Agents 管理页面** (`/agents`)
- Agent 列表
- 创建 Agent 按钮
- Agent 配置表单
- Agent 测试/执行

**5. 监控数据页面** (`/monitoring`)
- 项目列表
- 试验数据表格
- 搜索和过滤
- 数据导出

#### P1（重要）

**6. 任务调度页面** (`/tasks`)
- 任务列表
- 创建任务
- 启动/停止任务

**7. 设置页面** (`/settings`)
- 个人信息
- 修改密码
- API 密钥配置

#### P2（可选）

**8. 工作流编辑器** (`/workflow`)
- 可视化节点编辑
- 拖拽连接
- 保存/加载

### UI 组件设计

#### 通用组件

**`components/common/Pagination.vue`**
```vue
<template>
  <el-pagination
    v-model:current-page="currentPage"
    v-model:page-size="pageSize"
    :page-sizes="[10, 20, 50, 100]"
    :total="total"
    layout="total, sizes, prev, pager, next, jumper"
    @size-change="handleSizeChange"
    @current-change="handleCurrentChange"
  />
</template>
```

**`components/common/ConfirmDialog.vue`**
```vue
<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="400px"
  >
    <p>{{ message }}</p>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>
```

#### Skill 组件

**`components/skills/SkillForm.vue`**
```vue
<template>
  <el-form :model="form" :rules="rules" ref="formRef">
    <el-form-item label="Skill 名称" prop="name">
      <el-input v-model="form.name" />
    </el-form-item>

    <el-form-item label="描述" prop="description">
      <el-input v-model="form.description" type="textarea" />
    </el-form-item>

    <el-form-item label="分类" prop="category">
      <el-radio-group v-model="form.category">
        <el-radio label="external">External</el-radio>
        <el-radio label="internal">Internal</el-radio>
      </el-radio-group>
    </el-form-item>

    <el-form-item label="SKILL.md 内容" prop="content">
      <el-input
        v-model="form.content"
        type="textarea"
        :rows="10"
        placeholder="粘贴 SKILL.md 内容..."
      />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit">保存</el-button>
      <el-button @click="handleCancel">取消</el-button>
    </el-form-item>
  </el-form>
</template>
```

#### Agent 组件

**`components/agents/AgentForm.vue`**
```vue
<template>
  <el-form :model="form" :rules="rules" ref="formRef">
    <!-- 基本信息 -->
    <el-form-item label="Agent 名称" prop="name">
      <el-input v-model="form.name" />
    </el-form-item>

    <el-form-item label="描述" prop="description">
      <el-input v-model="form.description" type="textarea" />
    </el-form-item>

    <!-- 模型配置 -->
    <el-form-item label="模型" prop="model_name">
      <el-select v-model="form.model_name">
        <el-option label="Qwen Max" value="qwen-max" />
        <el-option label="Qwen Plus" value="qwen-plus" />
        <el-option label="DeepSeek Chat" value="deepseek-chat" />
      </el-select>
    </el-form-item>

    <el-form-item label="温度">
      <el-slider v-model="form.temperature" :min="0" :max="1" :step="0.1" />
    </el-form-item>

    <!-- Skill 选择 -->
    <el-form-item label="选择 Skills">
      <el-select v-model="form.skill_ids" multiple>
        <el-option
          v-for="skill in availableSkills"
          :key="skill.id"
          :label="skill.name"
          :value="skill.id"
        />
      </el-select>
    </el-form-item>

    <!-- 系统提示词 -->
    <el-form-item label="系统提示词">
      <el-input v-model="form.system_prompt" type="textarea" :rows="5" />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit">保存</el-button>
      <el-button @click="handleTest">测试</el-button>
      <el-button @click="handleCancel">取消</el-button>
    </el-form-item>
  </el-form>
</template>
```

### 状态管理（Pinia）

**`stores/skill.ts`**
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getSkills, createSkill, updateSkill, deleteSkill } from '@/api/skills'

export const useSkillStore = defineStore('skill', () => {
  const skills = ref([])
  const loading = ref(false)
  const total = ref(0)

  // 获取 Skill 列表
  const fetchSkills = async (params: any) => {
    loading.value = true
    try {
      const response = await getSkills(params)
      skills.value = response.data.items
      total.value = response.data.total
    } finally {
      loading.value = false
    }
  }

  // 创建 Skill
  const createSkillAction = async (skillData: any) => {
    loading.value = true
    try {
      await createSkill(skillData)
      await fetchSkills({})
    } finally {
      loading.value = false
    }
  }

  return {
    skills,
    loading,
    total,
    fetchSkills,
    createSkillAction
  }
})
```

---

## 开发优先级

### 第 1 周：基础搭建

**Backend**:
- [x] FastAPI 应用初始化
- [ ] 数据库模型定义
- [ ] 数据库初始化脚本
- [ ] JWT 认证实现
- [ ] 基础 API 路由框架

**Frontend**:
- [ ] Vue 项目初始化
- [ ] 路由配置
- [ ] 状态管理配置
- [ ] API 客户端封装
- [ ] 通用组件开发

### 第 2 周：认证和 Skill 管理

**Backend**:
- [ ] 用户注册/登录 API
- [ ] Skill CRUD API
- [ ] Skill 文件上传
- [ ] 数据验证和错误处理

**Frontend**:
- [ ] 登录/注册页面
- [ ] Dashboard 页面
- [ ] Skills 列表页面
- [ ] Skill 创建表单
- [ ] Skill 详情页面

### 第 3 周：Agent 管理

**Backend**:
- [ ] Agent CRUD API
- [ ] Agent 执行 API
- [ ] 调用 Framework 执行 Agent
- [ ] 执行历史记录

**Frontend**:
- [ ] Agents 列表页面
- [ ] Agent 创建表单
- [ ] Skill 选择器组件
- [ ] Agent 测试/执行界面
- [ ] 执行历史展示

### 第 4 周：监控数据展示

**Backend**:
- [ ] 监控项目 API
- [ ] 试验数据 API
- [ ] 统计数据 API
- [ ] 数据导出 API

**Frontend**:
- [ ] 监控 Dashboard
- [ ] 项目列表
- [ ] 试验数据表格
- [ ] 数据可视化图表
- [ ] 数据导出功能

### 第 5-6 周：完善和测试

- [ ] 任务调度功能
- [ ] 错误处理完善
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能优化
- [ ] 文档完善

---

## 需要补充的文档

### 1. API 文档

创建 `packages/platform/docs/api.md`：
- 所有 API 端点说明
- 请求/响应示例
- 错误码说明
- 认证方式

### 2. 数据库文档

创建 `packages/platform/docs/database.md`：
- 数据表设计
- ER 图
- 索引说明
- 查询示例

### 3. 开发指南

创建 `packages/platform/docs/development.md`：
- 环境搭建
- 代码规范
- 提交规范
- 测试指南

### 4. 部署文档

更新 `docs/platform/deployment.md`：
- Backend 部署
- Frontend 部署
- 环境变量配置
- Nginx 配置

---

## 快速开始

### 1. Backend 开发

```bash
# 进入后端目录
cd packages/platform/backend

# 安装依赖
uv sync --extra dev

# 初始化数据库
uv run python -m scripts.init_db

# 启动开发服务器
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 访问 API 文档
# http://localhost:8000/docs
```

### 2. Frontend 开发

```bash
# 进入前端目录
cd packages/platform/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问前端
# http://localhost:5173
```

### 3. 联调开发

```bash
# 终端 1: 启动后端
cd packages/platform/backend
uv run uvicorn main:app --reload

# 终端 2: 启动前端
cd packages/platform/frontend
npm run dev
```

---

## 下一步行动

1. **选择开始方向**：
   - 优先开发 Backend API
   - 优先开发 Frontend 界面
   - 同时进行（前后端分离）

2. **创建数据库模型**：
   - 设计所有表结构
   - 编写 SQLAlchemy 模型
   - 创建初始化脚本

3. **实现认证系统**：
   - JWT 认证
   - 用户注册/登录
   - 权限控制

4. **开发第一个功能**：
   - 建议：Skill 管理
   - 或：监控数据展示

需要我帮你：
- [ ] 创建具体的代码实现
- [ ] 设计数据库模型
- [ ] 实现 API 端点
- [ ] 开发前端组件
- [ ] 其他

请告诉我你想从哪里开始！
