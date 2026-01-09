# API 接口设计

## 基础规范

### RESTful API 设计原则

- 使用标准 HTTP 方法：GET, POST, PUT, DELETE
- 使用语义化 URL 路径
- 统一的响应格式
- 版本控制：`/api/v1/`

### 基础 URL

```
开发环境: http://localhost:8000/api/v1
生产环境: https://api.lingnexus.com/api/v1
```

### 通用响应格式

```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "error": null,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 错误码规范

| 错误码 | 说明 |
|-------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

---

## 认证和授权

### 1. 用户注册

```
POST /api/v1/auth/register
```

**请求体**：
```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "SecurePassword123!",
  "full_name": "张三"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "usr_1234567890",
      "username": "zhangsan",
      "email": "zhangsan@example.com",
      "full_name": "张三",
      "created_at": "2024-01-15T10:30:00Z"
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### 2. 用户登录

```
POST /api/v1/auth/login
```

**请求体**：
```json
{
  "username": "zhangsan",
  "password": "SecurePassword123!"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_in": 86400,
    "user": {
      "id": "usr_1234567890",
      "username": "zhangsan",
      "avatar_url": "/avatars/usr_1234567890.png"
    }
  }
}
```

### 3. Token 刷新

```
POST /api/v1/auth/refresh
```

**请求头**：
```
Authorization: Bearer <refresh_token>
```

**响应**：
```json
{
  "success": true,
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_in": 86400
  }
}
```

### 4. 获取当前用户信息

```
GET /api/v1/auth/me
```

**请求头**：
```
Authorization: Bearer <token>
```

**响应**：
```json
{
  "success": true,
  "data": {
    "id": "usr_1234567890",
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "full_name": "张三",
    "avatar_url": "/avatars/usr_1234567890.png",
    "is_admin": false,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

## Skill 管理

### 1. 创建 Skill

```
POST /api/v1/skills
```

**请求头**：
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**请求体**：
```json
{
  "name": "合同审查助手",
  "description": "审查合同法律风险",
  "category": "法务",
  "tags": ["合同", "风控"],
  "visibility": "private",
  "skill_md": "---\nname: 合同审查助手\n...",
  "resources": [
    {
      "filename": "reference.pdf",
      "content": "<base64_encoded_content>"
    }
  ]
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "id": "sk_abc123",
    "name": "合同审查助手",
    "storage_path": "users/usr_123/sk_abc123/",
    "version": "1.0.0",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 2. 获取 Skill 详情

```
GET /api/v1/skills/{skill_id}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "id": "sk_abc123",
    "name": "合同审查助手",
    "description": "审查合同法律风险",
    "author": {
      "id": "usr_123",
      "username": "zhangsan"
    },
    "category": "法务",
    "tags": ["合同", "风控"],
    "visibility": "public",
    "version": "1.0.0",
    "skill_md": "---\nname: 合同审查助手\n...",
    "usage_count": 150,
    "favorite_count": 25,
    "rating": 4.5,
    "rating_count": 20,
    "is_favorited": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-16T09:20:00Z"
  }
}
```

### 3. 列出 Skills

```
GET /api/v1/skills
```

**查询参数**：
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 20, 最大: 100)
- `author_id`: 筛选作者
- `visibility`: 筛选可见性 (`private`|`team`|`public`)
- `category`: 筛选分类
- `tags`: 筛选标签 (逗号分隔)
- `sort`: 排序方式 (`created_at`|`usage_count`|`rating`)
- `order`: 排序顺序 (`asc`|`desc`)
- `q`: 搜索关键词

**示例**：
```
GET /api/v1/skills?page=1&page_size=20&category=法务&sort=rating&order=desc
```

**响应**：
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "sk_abc123",
        "name": "合同审查助手",
        "description": "审查合同法律风险",
        "author": {"id": "usr_123", "username": "zhangsan"},
        "category": "法务",
        "tags": ["合同", "风控"],
        "visibility": "public",
        "usage_count": 150,
        "rating": 4.5,
        "created_at": "2024-01-15T10:30:00Z"
      }
    ],
    "total": 45,
    "page": 1,
    "page_size": 20,
    "total_pages": 3
  }
}
```

### 4. 更新 Skill

```
PUT /api/v1/skills/{skill_id}
```

**请求头**：
```
Authorization: Bearer <token>
```

**请求体**：
```json
{
  "name": "合同审查助手 v2",
  "description": "审查合同法律风险（增强版）",
  "category": "法务",
  "tags": ["合同", "风控", "增强"],
  "visibility": "team",
  "skill_md": "---\nname: 合同审查助手\n...",
  "change_log": "新增风险等级评估功能"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "id": "sk_abc123",
    "version": "2.0.0",
    "updated_at": "2024-01-16T09:20:00Z"
  }
}
```

### 5. 删除 Skill

```
DELETE /api/v1/skills/{skill_id}
```

**请求头**：
```
Authorization: Bearer <token>
```

**查询参数**：
- `permanent`: 是否永久删除 (默认: false，软删除)

**响应**：
```json
{
  "success": true,
  "data": {
    "deleted": true,
    "message": "Skill 已移至回收站"
  }
}
```

### 6. Fork Skill

```
POST /api/v1/skills/{skill_id}/fork
```

**请求头**：
```
Authorization: Bearer <token>
```

**请求体**：
```json
{
  "name": "我的合同审查助手",
  "visibility": "private"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "id": "sk_xyz789",
    "parent_skill_id": "sk_abc123",
    "name": "我的合同审查助手",
    "created_at": "2024-01-16T10:00:00Z"
  }
}
```

### 7. Skill 评分

```
POST /api/v1/skills/{skill_id}/rating
```

**请求头**：
```
Authorization: Bearer <token>
```

**请求体**：
```json
{
  "rating": 5,
  "comment": "非常好用，帮我节省了大量时间！"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "skill_id": "sk_abc123",
    "rating": 5,
    "average_rating": 4.7,
    "rating_count": 21
  }
}
```

### 8. 收藏/取消收藏 Skill

```
POST /api/v1/skills/{skill_id}/favorite
```

**请求头**：
```
Authorization: Bearer <token>
```

**请求体**：
```json
{
  "action": "add"  // "add" 或 "remove"
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "favorited": true,
    "favorite_count": 26
  }
}
```

---

## Agent 管理

### 1. 创建 Agent

```
POST /api/v1/agents
```

**请求头**：
```
Authorization: Bearer <token>
```

**请求体**：
```json
{
  "name": "合同处理工作流",
  "description": "自动处理合同审查流程",
  "visibility": "private",
  "config": {
    "model": "qwen-max",
    "temperature": 0.3,
    "skills": ["sk_abc123", "sk_def456"],
    "flow": {
      "type": "sequential",
      "steps": [
        {"skill_id": "sk_abc123", "name": "提取关键信息"},
        {"skill_id": "sk_def456", "name": "生成风险报告"}
      ]
    },
    "memory": {
      "type": "long-term",
      "duration": 7
    }
  }
}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "id": "ag_123",
    "name": "合同处理工作流",
    "created_at": "2024-01-16T10:00:00Z"
  }
}
```

### 2. 运行 Agent

```
POST /api/v1/agents/{agent_id}/run
```

**请求头**：
```
Authorization: Bearer <token>
```

**请求体**：
```json
{
  "input": "请审查这份合同：...",
  "stream": true
}
```

**响应 (stream=false)**：
```json
{
  "success": true,
  "data": {
    "agent_id": "ag_123",
    "run_id": "run_abc",
    "output": "审查结果：...",
    "execution_time_ms": 3500,
    "steps": [
      {
        "skill_id": "sk_abc123",
        "name": "提取关键信息",
        "output": "..."
      },
      {
        "skill_id": "sk_def456",
        "name": "生成风险报告",
        "output": "..."
      }
    ]
  }
}
```

**响应 (stream=true)**：
```
Server-Sent Events (SSE)
data: {"step": 1, "skill": "提取关键信息", "output": "..."}

data: {"step": 2, "skill": "生成风险报告", "output": "..."}

data: {"done": true, "final_output": "..."}
```

### 3. 获取 Agent 详情

```
GET /api/v1/agents/{agent_id}
```

**响应**：
```json
{
  "success": true,
  "data": {
    "id": "ag_123",
    "name": "合同处理工作流",
    "description": "自动处理合同审查流程",
    "author": {"id": "usr_123", "username": "zhangsan"},
    "config": {
      "model": "qwen-max",
      "skills": ["sk_abc123", "sk_def456"],
      "flow": {...}
    },
    "usage_count": 50,
    "created_at": "2024-01-16T10:00:00Z"
  }
}
```

### 4. 列出 Agents

```
GET /api/v1/agents
```

**查询参数**：与 Skills 列表接口类似

---

## 搜索和推荐

### 1. 全文搜索

```
GET /api/v1/search
```

**查询参数**：
- `q`: 搜索关键词
- `type`: 搜索类型 (`skills`|`agents`|`all`)
- `page`, `page_size`: 分页参数

**示例**：
```
GET /api/v1/search?q=合同审查&type=skills&page=1
```

**响应**：
```json
{
  "success": true,
  "data": {
    "skills": [
      {
        "id": "sk_abc123",
        "name": "合同审查助手",
        "description": "审查合同法律风险",
        "highlight": "...<em>合同</em> <em>审查</em>..."
      }
    ],
    "agents": [],
    "total": 5
  }
}
```

### 2. 推荐 Skills

```
GET /api/v1/skills/{skill_id}/recommendations
```

**查询参数**：
- `limit`: 返回数量 (默认: 10)

**响应**：
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "id": "sk_def456",
        "name": "风险评估工具",
        "reason": "经常与'合同审查助手'一起使用",
        "score": 0.85
      }
    ]
  }
}
```

### 3. 热门 Skills

```
GET /api/v1/skills/trending
```

**查询参数**：
- `period`: 时间周期 (`day`|`week`|`month`|`all`)
- `limit`: 返回数量 (默认: 20)

**响应**：
```json
{
  "success": true,
  "data": {
    "period": "week",
    "skills": [
      {
        "id": "sk_abc123",
        "name": "合同审查助手",
        "usage_count": 150,
        "rating": 4.5
      }
    ]
  }
}
```

---

## 统计和分析

### 1. 用户统计

```
GET /api/v1/users/{user_id}/stats
```

**响应**：
```json
{
  "success": true,
  "data": {
    "skills_count": 15,
    "agents_count": 5,
    "total_usage": 350,
    "popular_skills": [
      {
        "id": "sk_abc123",
        "name": "合同审查助手",
        "usage_count": 150
      }
    ]
  }
}
```

### 2. Skill 使用统计

```
GET /api/v1/skills/{skill_id}/stats
```

**查询参数**：
- `period`: 统计周期 (`day`|`week`|`month`)

**响应**：
```json
{
  "success": true,
  "data": {
    "period": "week",
    "usage_count": 150,
    "unique_users": 45,
    "avg_execution_time_ms": 3200,
    "success_rate": 0.98,
    "daily_usage": [
      {"date": "2024-01-10", "count": 20},
      {"date": "2024-01-11", "count": 25}
    ]
  }
}
```

---

## 文件上传

### 1. 上传资源文件

```
POST /api/v1/skills/{skill_id}/resources
```

**请求头**：
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**请求体**：
```
file: <binary>
description: "参考文档"
```

**响应**：
```json
{
  "success": true,
  "data": {
    "filename": "reference.pdf",
    "url": "/api/v1/skills/sk_abc123/resources/reference.pdf",
    "size": 1024000
  }
}
```

### 2. 下载资源文件

```
GET /api/v1/skills/{skill_id}/resources/{filename}
```

**响应**：文件二进制内容

---

## 组织管理

### 1. 创建组织

```
POST /api/v1/organizations
```

**请求体**：
```json
{
  "name": "法务部",
  "slug": "legal-dept",
  "description": "公司法务部门",
  "max_members": 50
}
```

### 2. 邀请成员

```
POST /api/v1/organizations/{org_id}/members
```

**请求体**：
```json
{
  "user_id": "usr_456",
  "role": "member"
}
```

### 3. 成员列表

```
GET /api/v1/organizations/{org_id}/members
```

---

## Admin API (管理员专用)

### 1. 审核待发布 Skills

```
PUT /api/v1/admin/skills/{skill_id}/review
```

**请求体**：
```json
{
  "status": "approved",
  "note": "内容合规，准予发布"
}
```

### 2. 用户管理

```
GET /api/v1/admin/users
PUT /api/v1/admin/users/{user_id}/status
DELETE /api/v1/admin/users/{user_id}
```

---

## WebSocket API

### 实时执行 Agent

```
WS /api/v1/ws/agents/{agent_id}/run?token=<jwt_token>
```

**消息格式**：
```json
// 客户端发送
{
  "type": "start",
  "input": "请审查这份合同"
}

// 服务端返回
{
  "type": "step",
  "step": 1,
  "skill": "提取关键信息",
  "output": "..."
}

{
  "type": "complete",
  "final_output": "...",
  "execution_time_ms": 3500
}
```

---

## API 限流

### 限流规则

| 用户类型 | 限制 |
|---------|------|
| **免费用户** | 100 requests/hour |
| **专业版** | 1000 requests/hour |
| **企业版** | 10000 requests/hour |

### 限流响应

```
HTTP 429 Too Many Requests

{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求过于频繁，请稍后再试",
    "retry_after": 3600
  }
}
```

---

## 下一步

查看前端组件设计：`03-frontend-design.md`
