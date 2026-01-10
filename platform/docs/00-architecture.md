# LingNexus Skill Platform - 技术架构文档

## 项目概述

基于 AgentScope 的低代码智能体构建平台，面向无编程技能的业务人员，支持 Skill 的创建、组合、分享和运行。

**核心特性**：
- 🎨 **可视化编辑** - 拖拽式构建智能体
- 📦 **Skill 市场** - 创建、分享、复用技能
- 🔐 **权限管控** - 私有/团队/公开三级权限
- 💾 **纯本地存储** - 零云成本，数据完全可控
- 🚀 **AgentScope 集成** - 成熟的多智能体运行时

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    前端层 (Frontend)                         │
│  Vue 3 + TypeScript + Element Plus + React Flow             │
│  ├─ Skill 编辑器  ├─ Agent 构建器  ├─ 市场浏览  ├─ 监控面板  │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API
┌──────────────────────────────┴──────────────────────────────┐
│                    后端层 (Backend)                          │
│  FastAPI + Python 3.10+                                      │
│  ├─ 用户认证    ├─ Skill 管理   ├─ 权限控制   ├─ 编排引擎    │
│  └─ AgentScope Runtime Wrapper                              │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────┐
│                    存储层 (Storage)                          │
├─────────────────────────────────────────────────────────────┤
│  📁 文件系统 (File System)      🗄️ SQLite (元数据索引)      │
│  ├── skills/system/             ├── skills.db               │
│  ├── skills/users/              ├── skills.db.lock           │
│  └── skills/market/             └── skills.db-shm           │
│                                                              │
│  💾 本地缓存 (Cache)                                       │
│  └── data/cache/ (可选的 LRU 缓存)                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 技术栈选型

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue 3** | ^3.4.0 | 前端框架 |
| **TypeScript** | ^5.3.0 | 类型安全 |
| **Element Plus** | ^2.5.0 | UI 组件库 |
| **React Flow** | ^11.10.0 | 流程图编辑器 |
| **Pinia** | ^2.1.0 | 状态管理 |
| **Vue Router** | ^4.2.0 | 路由管理 |
| **Axios** | ^1.6.0 | HTTP 客户端 |
| **Vite** | ^5.0.0 | 构建工具 |

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.10+ | 运行时 |
| **FastAPI** | ^0.109.0 | Web 框架 |
| **SQLAlchemy** | ^2.0.0 | ORM |
| **SQLite** | 3.40+ | 元数据库 |
| **Pydantic** | ^2.5.0 | 数据验证 |
| **AgentScope** | latest | Agent 运行时 |
| **uvicorn** | ^0.27.0 | ASGI 服务器 |

### 为什么选择这些技术？

#### 为什么选择 SQLite 而不是 PostgreSQL？

✅ **SQLite 的优势**：
- 零配置，无需安装数据库服务器
- 单文件存储，易于备份和迁移
- 适合中小规模（<100万条记录）
- 支持完整的 SQL 功能
- 读取性能优异

❌ **PostgreSQL 的劣势**（对于本项目）：
- 需要额外安装和维护
- 增加部署复杂度
- 对于本地化应用过重

**结论**：对于面向个人/小团队的本地化平台，SQLite 是最佳选择。

#### 为什么选择文件系统存储 Skill 内容？

✅ **文件系统的优势**：
- Git 友好，版本控制自然
- 直观可见，便于调试
- 支持大文件（PDF、图片等）
- 简单备份（复制文件夹）

❌ **数据库存内容的劣势**：
- 大文件处理复杂
- 需要 Base64 编码，增加体积
- 不符合文件操作习惯

**结论**：混合方案 - SQLite 存元数据，文件系统存内容。

---

## 数据流设计

### 1. Skill 创建流程

```
用户操作                    后端处理                    存储操作
   │                          │                           │
   ├─ 填写Skill表单  ────────► ├─ 验证输入      ────────► ├─ 生成 Skill ID
   │                          │                           │
   ├─ 上传资源文件  ────────► ├─ 保存资源     ────────► ├─ skills/users/user_XYZ/skill_id/
   │                          │                           │   ├─ SKILL.md
   │                          │                           │   ├─ skill.json
   │                          │                           │   └─ resources/
   │                          │                           │
   ├─ 提交创建      ────────► ├─ 写入数据库    ────────► ├─ skills.db
   │                          │   (skills表)              │
   └─ 显示成功      ────────► └─ 返回 Skill ID           └─ (索引和元数据)
```

### 2. Skill 查询流程

```
用户查询                    后端处理                    缓存策略
   │                          │                           │
   ├─ 搜索Skill      ────────► ├─ 查询 SQLite   ────────► ├─ L1: 内存缓存
   │   (关键词/分类)          │   (WHERE + LIKE)          │   (LRU Cache)
   │                          │                           │
   │                          ├─ 获取结果列表  ────────► ├─ L2: SQLite
   │                          │                           │   (持久化)
   │                          │                           │
   │                          ├─ 读取文件内容  ────────► ├─ L3: 文件系统
   │                          │   (SKILL.md)              │   (skills/)
   │                          │                           │
   └─ 显示结果      ────────► └─ 返回 Skill 对象          └─ 缓存到 L1
```

### 3. Agent 运行流程

```
用户操作                    后端处理                  AgentScope
   │                          │                         │
   ├─ 构建Agent      ────────► ├─ 加载 Skill  ────────► ├─ 读取 SKILL.md
   │   (拖拽组合)             │   (多Skill)              │
   │                          │                         │
   ├─ 配置参数      ────────► ├─ 创建 Agent  ────────► ├─ 初始化 Agent
   │   (模型/温度)            │   (AgentFactory)         │
   │                          │                         │
   ├─ 运行Agent      ────────► ├─ 发送消息    ────────► ├─ Agent 执行
   │   (输入提示)             │   (调用API)              │   (Skill逻辑)
   │                          │                         │
   │                          ├─ 流式返回    ────────► ├─ 返回结果
   └─ 显示结果      ────────► └─ (SSE/WebSocket)       └─ 记录日志
```

---

## 核心模块设计

### 1. Skill 存储管理器 (LocalSkillStorage)

**职责**：
- Skill 文件的增删改查
- 文件系统与数据库的同步
- 版本管理

**接口定义**：
```python
class LocalSkillStorage:
    def save_skill(metadata, content, resources) -> str
    def load_skill(skill_id) -> Dict
    def delete_skill(skill_id, soft_delete=True) -> bool
    def list_skills(filters) -> List[Dict]
    def update_skill(skill_id, updates) -> bool
    def fork_skill(skill_id, new_author_id) -> str
```

### 2. 权限管理器 (PermissionManager)

**职责**：
- 用户认证 (JWT)
- 权限检查 (RBAC)
- 团队管理

**权限模型**：
```
用户 (User)
  ├─ 个人空间 (Private)
  │   └─ 完全控制
  │
  ├─ 团队空间 (Team)
  │   ├─ 管理员 (Admin)    - 查看/编辑/删除/管理成员
  │   ├─ 编辑者 (Editor)   - 查看/编辑
  │   └─ 查看者 (Viewer)   - 仅查看
  │
  └─ 公开市场 (Public)
      └─ 只读访问
```

### 3. Agent 编排引擎 (OrchestrationEngine)

**职责**：
- Skill 组合逻辑
- 数据流管理
- 错误处理和重试

**编排模式**：
```
1. 串行模式
   Skill A → Skill B → Skill C

2. 并行模式
   Skill A ──┐
            ├──> 汇聚
   Skill B ──┘

3. 条件模式
   Skill A → 判断 → Skill B (真) / Skill C (假)

4. 循环模式
   Skill A → 循环N次 → Skill B
```

---

## 安全设计

### 1. 认证机制

```
用户注册
  ├─ 用户名 + 密码
  ├─ 密码哈希存储 (bcrypt)
  └─ 生成 JWT Token

用户登录
  ├─ 验证用户名密码
  ├─ 返回 JWT Token (24小时有效)
  └─ 刷新 Token (Refresh Token)
```

### 2. 数据安全

| 安全措施 | 实现方式 |
|---------|---------|
| **密码加密** | bcrypt 哈希 |
| **SQL 注入防护** | 参数化查询 |
| **XSS 防护** | 前端输入转义 |
| **路径遍历防护** | 文件路径校验 |
| **文件类型限制** | 白名单验证 |
| **文件大小限制** | <10MB 警告 |

### 3. 隔离策略

```
文件系统隔离：
skills/
├── users/
│   ├── user_123/    # 只能被 user_123 访问
│   └── user_456/    # 只能被 user_456 访问
└── system/          # 只读，所有人可访问

数据库隔离：
- 每条记录都有 author_id
- 查询时自动添加 WHERE author_id = ?
- 权限检查在业务层强制执行
```

---

## 性能优化

### 1. 缓存策略

```python
# 三级缓存
L1: 内存缓存 (LRU, 100条)
  └─ 热门 Skill
  └─ 响应时间: <1ms

L2: SQLite (WAL模式)
  └─ 所有 Skill 元数据
  └─ 响应时间: 10-50ms

L3: 文件系统
  └─ Skill 完整内容
  └─ 响应时间: 50-200ms
```

### 2. 数据库优化

```sql
-- 索引优化
CREATE INDEX idx_skills_author ON skills(author_id);
CREATE INDEX idx_skills_visibility ON skills(visibility);
CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_name ON skills(name COLLATE NOCASE);

-- 全文搜索 (SQLite FTS5)
CREATE VIRTUAL TABLE skills_fts USING fts5(
    name, description, tags,
    content='skills',
    content_rowid='rowid'
);

-- 分页查询
SELECT * FROM skills
WHERE deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 20 OFFSET 0;
```

### 3. 文件系统优化

```python
# 技巧1: 批量读取
def load_skills_batch(skill_ids):
    # 避免多次文件IO
    return [read_skill_file(sid) for sid in skill_ids]

# 技巧2: 延迟加载
def list_skills():
    # 先从数据库获取元数据
    metadatas = db.query("SELECT id, name FROM skills")
    # 按需加载完整内容
    return metadatas

# 技巧3: 并行加载
from concurrent.futures import ThreadPoolExecutor

def load_skills_parallel(skill_ids):
    with ThreadPoolExecutor(max_workers=4) as executor:
        return list(executor.map(load_skill, skill_ids))
```

---

## 部署方案

### 开发环境

```bash
# 前端
cd platform/frontend
npm install
npm run dev  # http://localhost:5173

# 后端
cd platform/backend
uv sync
uv run uvicorn main:app --reload  # http://localhost:8000
```

### 生产环境

```bash
# 1. 构建前端
cd platform/frontend
npm run build

# 2. 启动后端 (单机部署)
cd platform/backend
uv run uvicorn main:app --host 0.0.0.0 --port 8000

# 3. 使用 Gunicorn (多进程)
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000

# 4. Nginx 反向代理
location /api/ {
    proxy_pass http://localhost:8000/;
}

location / {
    root /path/to/frontend/dist;
}
```

### 单文件部署 (可选)

使用 PyInstaller 打包成单个可执行文件：

```bash
pyinstaller --onefile \
    --add-data "skills:skills" \
    --add-data "data:data" \
    main.py
```

---

## 监控和日志

### 日志级别

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/platform.log'),
        logging.StreamHandler()
    ]
)

# 使用
logger.info("Skill created: %s", skill_id)
logger.error("Failed to load skill: %s", error)
```

### 关键指标

| 指标 | 说明 | 告警阈值 |
|------|------|---------|
| **API 响应时间** | 平均请求耗时 | >500ms |
| **数据库连接数** | SQLite 并发连接 | >10 |
| **磁盘使用率** | skills/ 目录大小 | >10GB |
| **内存使用** | 进程内存占用 | >2GB |
| **Skill 加载失败率** | 加载失败比例 | >1% |

---

## 下一步

- [ ] 数据库 Schema 详细设计 (`01-database-schema.md`)
- [ ] API 接口定义 (`02-api-design.md`)
- [ ] 前端组件设计 (`03-frontend-design.md`)
- [ ] 部署指南 (`04-deployment-guide.md`)
- [ ] 开发指南 (`05-development-guide.md`)
