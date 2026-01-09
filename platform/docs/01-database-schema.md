# 数据库 Schema 设计

## 数据库选型

**SQLite 3.40+**

选择理由：
- ✅ 零配置，无需安装数据库服务器
- ✅ 单文件存储，易于备份和迁移
- ✅ 支持 WAL 模式，提高并发性能
- ✅ 支持 FTS5 全文搜索
- ✅ 适合中小规模（<100万条记录）

---

## 数据库文件组织

```
data/
├── skills.db              # 主数据库文件
├── skills.db-wal          # Write-Ahead Log (WAL模式)
├── skills.db-shm          # Shared Memory (WAL模式)
└── cache/                 # 缓存目录 (可选)
    └── lru_cache.pkl      # LRU 缓存持久化
```

---

## 完整 Schema 定义

### 1. 用户表 (users)

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,              -- UUID 格式
    username TEXT NOT NULL UNIQUE,    -- 用户名 (唯一)
    email TEXT UNIQUE,                -- 邮箱 (可选，唯一)
    password_hash TEXT NOT NULL,      -- 密码哈希 (bcrypt)
    full_name TEXT,                   -- 全名
    avatar_url TEXT,                  -- 头像URL (相对路径)

    -- 账户状态
    is_active INTEGER DEFAULT 1,      -- 是否激活 (0/1)
    is_admin INTEGER DEFAULT 0,       -- 是否管理员 (0/1)

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,          -- 最后登录时间

    -- 删除标记 (软删除)
    deleted_at TIMESTAMP
);

-- 索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE deleted_at IS NULL;
```

**示例数据**：
```json
{
  "id": "usr_1234567890",
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password_hash": "$2b$12$...",
  "full_name": "张三",
  "avatar_url": "/avatars/usr_1234567890.png",
  "is_active": 1,
  "is_admin": 0,
  "created_at": "2024-01-15 10:30:00"
}
```

---

### 2. 组织表 (organizations)

```sql
CREATE TABLE organizations (
    id TEXT PRIMARY KEY,              -- UUID 格式
    name TEXT NOT NULL,               -- 组织名称
    slug TEXT NOT NULL UNIQUE,        -- 组织标识符 (用于URL)
    description TEXT,                 -- 组织描述
    logo_url TEXT,                    -- Logo URL

    -- 配额限制
    max_members INTEGER DEFAULT 10,   -- 最大成员数
    max_skills INTEGER DEFAULT 100,   -- 最大Skill数

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 索引
CREATE INDEX idx_organizations_slug ON organizations(slug);
```

**示例数据**：
```json
{
  "id": "org_abc123",
  "name": "法务部",
  "slug": "legal-dept",
  "description": "公司法务部门",
  "max_members": 50,
  "max_skills": 500
}
```

---

### 3. 组织成员表 (organization_members)

```sql
CREATE TABLE organization_members (
    org_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,               -- 'admin' | 'member' | 'viewer'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (org_id, user_id),
    FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_org_members_org ON organization_members(org_id);
CREATE INDEX idx_org_members_user ON organization_members(user_id);
```

---

### 4. Skills 表 (skills)

```sql
CREATE TABLE skills (
    id TEXT PRIMARY KEY,              -- UUID 格式
    name TEXT NOT NULL,               -- Skill 名称
    description TEXT,                 -- Skill 描述

    -- 存储位置
    storage_path TEXT NOT NULL,       -- 相对于 skills/ 的路径
    storage_type TEXT DEFAULT 'user', -- 'system' | 'user' | 'market'

    -- 作者和权限
    author_id TEXT NOT NULL,          -- 作者用户ID
    org_id TEXT,                      -- 所属组织ID (可选)
    visibility TEXT DEFAULT 'private', -- 'private' | 'team' | 'public'

    -- 分类和标签
    category TEXT,                    -- 分类 (如: "法务", "数据分析")
    tags TEXT,                        -- 标签 (JSON数组字符串)

    -- Skill 内容 (快速访问，避免频繁读文件)
    schema_json TEXT,                 -- 完整的 SKILL.md 内容
    trigger_keywords TEXT,            -- 触发关键词 (JSON数组)

    -- 统计信息
    usage_count INTEGER DEFAULT 0,    -- 使用次数
    favorite_count INTEGER DEFAULT 0, -- 收藏次数
    rating REAL DEFAULT 0.0,          -- 平均评分 (0-5)
    rating_count INTEGER DEFAULT 0,   -- 评分人数

    -- 版本信息
    version TEXT DEFAULT '1.0.0',     -- 当前版本
    parent_skill_id TEXT,             -- 父Skill ID (fork关系)
    is_latest INTEGER DEFAULT 1,      -- 是否最新版本

    -- 审核状态 (仅market类型需要)
    review_status TEXT DEFAULT 'approved', -- 'pending' | 'approved' | 'rejected'
    review_note TEXT,                 -- 审核备注
    reviewed_by TEXT,                 -- 审核人ID
    reviewed_at TIMESTAMP,            -- 审核时间

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,             -- 软删除

    FOREIGN KEY (author_id) REFERENCES users(id),
    FOREIGN KEY (org_id) REFERENCES organizations(id),
    FOREIGN KEY (parent_skill_id) REFERENCES skills(id)
);

-- 索引
CREATE INDEX idx_skills_author ON skills(author_id);
CREATE INDEX idx_skills_org ON skills(org_id);
CREATE INDEX idx_skills_visibility ON skills(visibility);
CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_storage_type ON skills(storage_type);
CREATE INDEX idx_skills_created ON skills(created_at DESC);
CREATE INDEX idx_skills_usage ON skills(usage_count DESC);
CREATE INDEX idx_skills_rating ON skills(rating DESC);
CREATE INDEX idx_skills_name ON skills(name COLLATE NOCASE); -- 不区分大小写
CREATE INDEX idx_skills_deleted ON skills(deleted_at) WHERE deleted_at IS NOT NULL;

-- 全文搜索 (FTS5)
CREATE VIRTUAL TABLE skills_fts USING fts5(
    name,
    description,
    tags,
    content='skills',
    content_rowid='rowid',
    tokenize='porter unicode61'
);

-- 触发器：自动更新 FTS 索引
CREATE TRIGGER skills_ai AFTER INSERT ON skills BEGIN
  INSERT INTO skills_fts(rowid, name, description, tags)
  VALUES (new.rowid, new.name, new.description, new.tags);
END;

CREATE TRIGGER skills_ad AFTER DELETE ON skills BEGIN
  DELETE FROM skills_fts WHERE rowid = old.rowid;
END;

CREATE TRIGGER skills_au AFTER UPDATE ON skills BEGIN
  UPDATE skills_fts
  SET name = new.name,
      description = new.description,
      tags = new.tags
  WHERE rowid = new.rowid;
END;
```

**示例数据**：
```json
{
  "id": "sk_abc123",
  "name": "合同审查助手",
  "description": "审查合同法律风险，识别潜在问题条款",
  "storage_path": "users/usr_123/sk_abc123/",
  "storage_type": "user",
  "author_id": "usr_123",
  "org_id": "org_legal",
  "visibility": "team",
  "category": "法务",
  "tags": "[\"合同\", \"风控\", \"法律\"]",
  "usage_count": 150,
  "favorite_count": 25,
  "rating": 4.5,
  "rating_count": 20,
  "version": "2.1.0",
  "created_at": "2024-01-10 09:00:00"
}
```

---

### 5. Skill 版本历史表 (skill_versions)

```sql
CREATE TABLE skill_versions (
    id TEXT PRIMARY KEY,              -- 版本记录ID
    skill_id TEXT NOT NULL,           -- 关联的Skill ID
    version TEXT NOT NULL,            -- 版本号 (如: "1.0.0")
    storage_path TEXT NOT NULL,       -- 版本文件路径

    -- 变更信息
    change_log TEXT,                  -- 变更日志
    change_type TEXT,                 -- 'major' | 'minor' | 'patch'

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    UNIQUE(skill_id, version)
);

-- 索引
CREATE INDEX idx_skill_versions_skill ON skill_versions(skill_id);
CREATE INDEX idx_skill_versions_created ON skill_versions(created_at DESC);
```

**示例数据**：
```json
{
  "id": "ver_001",
  "skill_id": "sk_abc123",
  "version": "1.0.0",
  "storage_path": "users/usr_123/sk_abc123@v1.0.0/",
  "change_log": "初始版本，实现基础审查功能",
  "change_type": "major",
  "created_at": "2024-01-10 09:00:00"
}
```

---

### 6. Skill 权限表 (skill_permissions)

```sql
CREATE TABLE skill_permissions (
    skill_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    permission TEXT NOT NULL,         -- 'view' | 'edit' | 'delete' | 'admin'
    granted_by TEXT,                  -- 授权人ID
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (skill_id, user_id),
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_skill_permissions_skill ON skill_permissions(skill_id);
CREATE INDEX idx_skill_permissions_user ON skill_permissions(user_id);
```

**示例数据**：
```json
{
  "skill_id": "sk_abc123",
  "user_id": "usr_456",
  "permission": "edit",
  "granted_by": "usr_123",
  "granted_at": "2024-01-12 10:00:00"
}
```

---

### 7. Agents 表 (agents)

```sql
CREATE TABLE agents (
    id TEXT PRIMARY KEY,              -- UUID 格式
    name TEXT NOT NULL,               -- Agent 名称
    description TEXT,                 -- Agent 描述

    -- 作者和权限
    author_id TEXT NOT NULL,
    org_id TEXT,
    visibility TEXT DEFAULT 'private', -- 'private' | 'team' | 'public'

    -- Agent 配置
    config_json TEXT NOT NULL,        -- 完整的Agent配置 (JSON)
                                       -- 包括: 使用的Skills、模型参数、编排逻辑等

    -- 统计
    usage_count INTEGER DEFAULT 0,

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,

    FOREIGN KEY (author_id) REFERENCES users(id),
    FOREIGN KEY (org_id) REFERENCES organizations(id)
);

-- 索引
CREATE INDEX idx_agents_author ON agents(author_id);
CREATE INDEX idx_agents_org ON agents(org_id);
CREATE INDEX idx_agents_visibility ON agents(visibility);
CREATE INDEX idx_agents_created ON agents(created_at DESC);
```

**config_json 示例**：
```json
{
  "model": "qwen-max",
  "temperature": 0.3,
  "skills": ["sk_abc123", "sk_def456"],
  "flow": {
    "type": "sequential",
    "steps": [
      {"skill_id": "sk_abc123", "name": "提取关键信息"},
      {"skill_id": "sk_def456", "name": "生成报告"}
    ]
  },
  "memory": {
    "type": "long-term",
    "duration": 7
  }
}
```

---

### 8. Skill 使用日志表 (skill_usage_logs)

```sql
CREATE TABLE skill_usage_logs (
    id TEXT PRIMARY KEY,
    skill_id TEXT NOT NULL,
    user_id TEXT,                    -- 可选 (匿名使用时为空)
    agent_id TEXT,                   -- 可选 (通过Agent使用时记录)
    action TEXT NOT NULL,            -- 'view' | 'run' | 'edit' | 'fork' | 'delete'
    input_text TEXT,                 -- 输入文本 (可选，用于调试)
    output_text TEXT,                -- 输出文本 (可选)
    execution_time_ms INTEGER,       -- 执行耗时 (毫秒)
    success INTEGER DEFAULT 1,       -- 是否成功 (0/1)
    error_message TEXT,              -- 错误信息 (失败时)

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL
);

-- 索引
CREATE INDEX idx_usage_logs_skill ON skill_usage_logs(skill_id, created_at DESC);
CREATE INDEX idx_usage_logs_user ON skill_usage_logs(user_id, created_at DESC);
CREATE INDEX idx_usage_logs_action ON skill_usage_logs(action, created_at DESC);
```

---

### 9. Skill 收藏表 (skill_favorites)

```sql
CREATE TABLE skill_favorites (
    user_id TEXT NOT NULL,
    skill_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_favorites_user ON skill_favorites(user_id, created_at DESC);
CREATE INDEX idx_favorites_skill ON skill_favorites(skill_id);
```

---

### 10. Skill 评分表 (skill_ratings)

```sql
CREATE TABLE skill_ratings (
    user_id TEXT NOT NULL,
    skill_id TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,                    -- 评分评论
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- 索引
CREATE INDEX idx_ratings_skill ON skill_ratings(skill_id, rating DESC);
CREATE INDEX idx_ratings_user ON skill_ratings(user_id);
```

---

## 数据库配置

### 1. SQLite WAL 模式

WAL (Write-Ahead Logging) 模式提高并发性能：

```python
import sqlite3

conn = sqlite3.connect('data/skills.db')
conn.execute('PRAGMA journal_mode=WAL')      # 启用WAL
conn.execute('PRAGMA synchronous=NORMAL')     # 平衡性能和安全
conn.execute('PRAGMA cache_size=-64000')      # 64MB缓存
conn.execute('PRAGMA temp_store=MEMORY')      # 临时表在内存
conn.execute('PRAGMA mmap_size=30000000000')  # 启用内存映射 (30GB)
```

### 2. 连接池配置

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'sqlite:///data/skills.db',
    connect_args={
        'check_same_thread': False,  # 允许多线程
        'timeout': 30                # 超时30秒
    },
    poolclass=QueuePool,
    pool_size=10,                    # 连接池大小
    max_overflow=20,                 # 最大溢出连接数
    pool_pre_ping=True,              # 连接前检查
    echo=False                       # 不打印SQL (开发时设为True)
)
```

### 3. 备份策略

```bash
#!/bin/bash
# backup_db.sh - 数据库备份脚本

BACKUP_DIR="backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# 1. 备份数据库
cp data/skills.db "$BACKUP_DIR/skills.db"
cp data/skills.db-wal "$BACKUP_DIR/skills.db-wal"
cp data/skills.db-shm "$BACKUP_DIR/skills.db-shm"

# 2. 备份文件系统
tar -czf "$BACKUP_DIR/skills_files.tar.gz" skills/

# 3. 清理30天前的备份
find backups/ -type d -mtime +30 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR"
```

---

## 常用查询示例

### 1. 搜索 Skills

```sql
-- 基础查询
SELECT id, name, description, author_id, rating, usage_count
FROM skills
WHERE deleted_at IS NULL
  AND visibility = 'public'
ORDER BY created_at DESC
LIMIT 20;

-- 全文搜索
SELECT s.id, s.name, s.description
FROM skills s
JOIN skills_fts f ON s.rowid = f.rowid
WHERE skills_fts MATCH '合同 审查'
  AND s.deleted_at IS NULL
ORDER BY s.rating DESC;

-- 按分类查询
SELECT * FROM skills
WHERE category = '法务'
  AND visibility IN ('public', 'team')
  AND deleted_at IS NULL
ORDER BY usage_count DESC;
```

### 2. 用户统计

```sql
-- 用户拥有的Skill数量
SELECT
    u.id,
    u.username,
    COUNT(s.id) as skill_count
FROM users u
LEFT JOIN skills s ON s.author_id = u.id AND s.deleted_at IS NULL
WHERE u.deleted_at IS NULL
GROUP BY u.id
ORDER BY skill_count DESC;

-- 用户的Skill使用统计
SELECT
    s.name,
    SUM(sl.execution_time_ms) as total_time,
    AVG(sl.execution_time_ms) as avg_time,
    COUNT(*) as run_count
FROM skill_usage_logs sl
JOIN skills s ON s.id = sl.skill_id
WHERE sl.user_id = ?
  AND sl.created_at >= datetime('now', '-30 days')
GROUP BY s.id
ORDER BY run_count DESC;
```

### 3. 推荐系统

```sql
-- 基于协同过滤的推荐
-- "使用过这个Skill的用户还使用了"
SELECT DISTINCT s2.id, s2.name, COUNT(*) as score
FROM skill_usage_logs l1
JOIN skill_usage_logs l2 ON l1.user_id = l2.user_id AND l1.skill_id != l2.skill_id
JOIN skills s2 ON s2.id = l2.skill_id
WHERE l1.skill_id = ?                  -- 原Skill ID
  AND s2.deleted_at IS NULL
  AND s2.visibility = 'public'
GROUP BY s2.id
ORDER BY score DESC
LIMIT 10;
```

---

## 数据迁移

### 从文件系统到数据库

```python
def migrate_skills_from_filesystem():
    """将现有文件系统Skill迁移到数据库"""
    import json
    from pathlib import Path

    skills_base = Path('skills/external')

    for skill_dir in skills_base.glob('*/'):
        skill_md = skill_dir / 'SKILL.md'
        if not skill_md.exists():
            continue

        # 读取SKILL.md
        content = skill_md.read_text(encoding='utf-8')

        # 解析YAML front matter
        yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if yaml_match:
            metadata = yaml.safe_load(yaml_match.group(1))
            body = yaml_match.group(2)
        else:
            metadata = {}
            body = content

        # 插入数据库
        cursor.execute("""
            INSERT INTO skills (id, name, description, storage_path,
                               storage_type, author_id, visibility,
                               category, tags, schema_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            metadata.get('name', skill_dir.name),
            metadata.get('description', ''),
            str(skill_dir.relative_to(skills_base)),
            'system',
            'system',
            'public',
            metadata.get('category', ''),
            json.dumps(metadata.get('tags', [])),
            content
        ))

    conn.commit()
```

---

## 性能优化建议

### 1. 定期 VACUUM

```sql
-- 每月执行一次，回收空间
VACUUM;

-- 分析查询计划
ANALYZE;
```

### 2. 批量操作

```python
# ❌ 慢：逐条插入
for skill in skills:
    cursor.execute("INSERT INTO skills ...", skill)

# ✅ 快：批量插入
cursor.executemany("INSERT INTO skills ...", skills)
```

### 3. 事务管理

```python
# 将相关操作放在一个事务中
with conn:
    cursor.execute("INSERT INTO skills ...")
    cursor.execute("UPDATE skill_versions ...")
    cursor.execute("INSERT INTO skill_usage_logs ...")
    # 自动提交或回滚
```

---

## 下一步

查看 API 接口定义：`02-api-design.md`
