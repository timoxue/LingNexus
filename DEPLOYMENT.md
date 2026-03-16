# LINGNEXUS 部署文档

> 全球医药专利多智能体情报挖掘系统 - 完整部署指南

**最后更新**: 2026-03-16
**状态**: ✅ 生产就绪

---

## 📋 目录

1. [系统架构](#系统架构)
2. [关键设计](#关键设计)
3. [目录结构](#目录结构)
4. [配置说明](#配置说明)
5. [启动流程](#启动流程)
6. [故障排查](#故障排查)

---

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    宿主机 (Windows 11)                    │
│                                                           │
│  D:\Projects\LingNexus (挂载点)                          │
│  ├── agents/          ← Agent配置文件                    │
│  ├── scripts/         ← 启动脚本和proxy                  │
│  ├── .env             ← 环境变量                         │
│  └── docker-compose.yml                                  │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Claude Proxy (Node.js)                         │    │
│  │  Port: 18790                                     │    │
│  │  功能: x-api-key → Authorization: Bearer 转换   │    │
│  └─────────────────────────────────────────────────┘    │
│                          ↓                                │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Docker Container: lingnexus-gateway            │    │
│  │                                                  │    │
│  │  Mounts:                                         │    │
│  │  • D:\Projects\LingNexus → /workspace (bind)   │    │
│  │  • openclaw-state → /home/node/.openclaw        │    │
│  │                                                  │    │
│  │  OpenClaw Gateway (Port 18789)                  │    │
│  │  ├── main (Haiku)                               │    │
│  │  ├── coach (Sonnet) ← 查询分解                 │    │
│  │  ├── investigator (Haiku) ← 多语言爬虫         │    │
│  │  ├── validator (Sonnet) ← 专利验证             │    │
│  │  └── deduplicator (Sonnet) ← 跨语言去重        │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          ↓
              https://claude-code.club/api
              (Claude Code API)
```

---

## 关键设计

### 🔑 1. Claude Proxy 设计

**问题**: OpenClaw使用`x-api-key`头，但Claude Code API需要`Authorization: Bearer`格式

**解决方案**: 本地代理服务器进行头部转换

#### Proxy实现 (`scripts/claude-proxy.js`)

```javascript
// 核心转换逻辑
const apiKey = req.headers['x-api-key'];
const options = {
  hostname: 'claude-code.club',
  port: 443,
  path: `/api${targetPath}`,
  method: req.method,
  rejectUnauthorized: false,  // 绕过SSL证书验证
  headers: {
    ...req.headers,
    'host': 'claude-code.club',
    'authorization': `Bearer ${apiKey}`,  // 关键转换
    'x-api-key': undefined  // 移除原header
  }
};
```

**关键配置**:
- 监听端口: `18790`
- 目标地址: `https://claude-code.club/api`
- SSL验证: 禁用 (`rejectUnauthorized: false`)

**启动方式**:
```bash
node D:\Projects\LingNexus\scripts\claude-proxy.js
```

**验证proxy工作**:
```bash
curl -X POST http://localhost:18790/v1/messages \
  -H "x-api-key: cr_xxx" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-haiku-4-5-20251001","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
```

---

### 🗂️ 2. Docker Mount 设计

**核心原则**: 配置文件在宿主机，运行时状态在Docker volume

#### Mount配置 (`docker-compose.yml`)

```yaml
volumes:
  # 1. Workspace挂载 (READ-ONLY)
  - type: bind
    source: .                    # D:\Projects\LingNexus
    target: /workspace
    read_only: true              # 防止容器修改配置

  # 2. 运行时状态 (VOLUME)
  - openclaw-state:/home/node/.openclaw
```

#### 为什么需要两层存储？

| 路径 | 类型 | 用途 | 持久化 |
|------|------|------|--------|
| `/workspace` | bind mount | Agent配置文件(SOUL.md, models.json) | 宿主机 |
| `/home/node/.openclaw` | volume | OpenClaw运行时状态(openclaw.json) | Docker volume |

**关键操作**: 容器启动后需要复制`models.json`

```bash
# 必须执行！否则OpenClaw不会使用proxy
for agent in coach investigator validator deduplicator; do
  docker exec lingnexus-gateway sh -c "
    mkdir -p ~/.openclaw/agents/$agent/agent
    cp /workspace/agents/$agent/.openclaw/models.json \
       ~/.openclaw/agents/$agent/agent/models.json
  "
done
```

**为什么需要复制？**
- `/workspace`是read-only，OpenClaw无法直接写入
- OpenClaw从`~/.openclaw/agents/*/agent/models.json`读取配置
- `models.json`包含proxy的baseURL配置

---

### 🤖 3. Agent模型配置

**设计原则**: 根据agent职责选择合适的模型

| Agent | 模型 | 原因 |
|-------|------|------|
| **coach** | Sonnet | 需要强推理能力进行医药BD策略分解 |
| **investigator** | Haiku | 执行搜索任务，轻量级足够 |
| **validator** | Sonnet | 严格JSON校验，需要高准确度 |
| **deduplicator** | Sonnet | 跨语言实体消歧，需要强理解力 |
| **main** | Haiku | 简单路由，轻量级足够 |

**配置位置**: `.env`文件

```bash
MODEL_COACH=anthropic/claude-sonnet-4-6
MODEL_INVESTIGATOR=anthropic/claude-haiku-4-5-20251001
MODEL_VALIDATOR=anthropic/claude-sonnet-4-6
MODEL_DEDUPLICATOR=anthropic/claude-sonnet-4-6
```

---

## 目录结构

```
D:\Projects\LingNexus/
├── .env                          # 环境变量（包含API keys）
├── .env.example                  # 环境变量模板
├── docker-compose.yml            # Docker配置
├── openclaw.config.json          # OpenClaw全局配置
├── DEPLOYMENT.md                 # 本文档
├── LINGNEXUS.md                  # 架构设计文档
│
├── agents/                       # Agent配置目录
│   ├── main/
│   │   ├── SOUL.md              # Agent人格定义
│   │   ├── AGENTS.md            # Agent能力配置
│   │   └── .openclaw/
│   │       └── models.json      # 模型配置（含proxy baseURL）
│   ├── coach/
│   ├── investigator/
│   ├── validator/
│   └── deduplicator/
│
├── scripts/
│   ├── claude-proxy.js          # ⭐ Claude Code代理服务器
│   ├── register-agents.sh       # Agent注册脚本
│   ├── Start-LingNexus.ps1      # 启动脚本
│   └── Test-LingNexus.ps1       # 测试脚本
│
└── workflows/
    └── biopharma-scouting.json  # 医药专利挖掘工作流
```

---

## 配置说明

### 1. 环境变量 (`.env`)

```bash
# Claude Code 订阅凭证
ANTHROPIC_OAUTH_TOKEN=cr_xxx...
ANTHROPIC_API_KEY=${ANTHROPIC_OAUTH_TOKEN}  # SDK兼容
ANTHROPIC_BASE_URL=http://host.docker.internal:18790  # ⭐ 指向proxy

# 第三方模型（当前未使用，OpenClaw不支持）
MOONSHOT_API_KEY=sk-xxx
GOOGLE_API_KEY=AIza...
DASHSCOPE_API_KEY=sk-xxx

# Agent模型分配
MODEL_MAIN=claude-haiku-4-5-20251001
MODEL_COACH=anthropic/claude-sonnet-4-6
MODEL_INVESTIGATOR=anthropic/claude-haiku-4-5-20251001
MODEL_VALIDATOR=anthropic/claude-sonnet-4-6
MODEL_DEDUPLICATOR=anthropic/claude-sonnet-4-6
```

### 2. models.json 配置

**位置**: `agents/*/. openclaw/models.json`

**关键配置**:
```json
{
  "providers": {
    "anthropic": {
      "baseUrl": "http://host.docker.internal:18790",  // ⭐ Proxy地址
      "api": "anthropic-messages",
      "apiKey": "ANTHROPIC_OAUTH_TOKEN"
    }
  }
}
```

**⚠️ 重要**: 这个配置必须复制到容器内的`~/.openclaw/agents/*/agent/models.json`

---

## 启动流程

### 完整启动步骤

```bash
# 1. 启动Claude Proxy（新终端）
cd D:\Projects\LingNexus
node scripts\claude-proxy.js

# 2. 初始化agents（首次运行）
docker compose --profile setup run --rm setup

# 3. 启动gateway
docker compose up -d gateway

# 4. 修复权限
docker exec -u root lingnexus-gateway chown -R node:node /home/node/.openclaw

# 5. ⭐ 复制models.json（关键步骤）
docker exec lingnexus-gateway sh -c '
for agent in coach investigator validator deduplicator; do
  mkdir -p ~/.openclaw/agents/$agent/agent
  cp /workspace/agents/$agent/.openclaw/models.json \
     ~/.openclaw/agents/$agent/agent/models.json
  echo "✓ $agent"
done
'

# 6. 注册agents
docker exec lingnexus-gateway sh -c '
node /app/openclaw.mjs agents add coach --workspace /workspace/agents/coach --model anthropic/claude-sonnet-4-6 --non-interactive --json
node /app/openclaw.mjs agents add investigator --workspace /workspace/agents/investigator --model anthropic/claude-haiku-4-5-20251001 --non-interactive --json
node /app/openclaw.mjs agents add validator --workspace /workspace/agents/validator --model anthropic/claude-sonnet-4-6 --non-interactive --json
node /app/openclaw.mjs agents add deduplicator --workspace /workspace/agents/deduplicator --model anthropic/claude-sonnet-4-6 --non-interactive --json
'

# 7. 验证
docker exec lingnexus-gateway node /app/openclaw.mjs agents list
docker exec lingnexus-gateway node /app/openclaw.mjs agent --agent coach -m "测试"
```

### 快速重启

```bash
# 停止
docker compose down

# 启动（proxy保持运行）
docker compose up -d gateway

# 复制models.json（如果volume被清理）
# ... 执行步骤5
```

---

## 故障排查

### ❌ 问题1: Agent返回401错误

**症状**:
```
HTTP 401 authentication_error: invalid x-api-key
```

**原因**: OpenClaw没有使用proxy，直连claude-code.club

**解决**:
1. 检查proxy是否运行: `netstat -ano | findstr 18790`
2. 检查models.json是否复制到容器:
   ```bash
   docker exec lingnexus-gateway cat ~/.openclaw/agents/coach/agent/models.json | grep baseUrl
   ```
3. 重新复制models.json（见启动流程步骤5）

---

### ❌ 问题2: Agent未注册

**症状**:
```
Error: Unknown agent id "coach"
```

**原因**: Volume被清理或agents未注册

**解决**:
```bash
# 重新注册所有agents
docker exec lingnexus-gateway sh -c 'node /app/openclaw.mjs agents add coach ...'
```

---

### ❌ 问题3: 权限错误

**症状**:
```
EACCES: permission denied, mkdir '/home/node/.openclaw/...'
```

**解决**:
```bash
docker exec -u root lingnexus-gateway chown -R node:node /home/node/.openclaw
docker compose restart gateway
```

---

### ❌ 问题4: Proxy连接失败

**症状**: 容器内无法访问`host.docker.internal:18790`

**检查**:
```bash
# 1. Proxy是否运行
netstat -ano | findstr 18790

# 2. 容器内测试
docker exec lingnexus-gateway curl -v http://host.docker.internal:18790/v1/messages
```

**解决**: 重启proxy服务器

---

## 测试命令

### 测试单个Agent

```bash
# Coach (查询分解)
docker exec lingnexus-gateway node /app/openclaw.mjs agent --agent coach \
  -m "请帮我挖掘全球PROTAC靶向降解剂的最新专利"

# Validator (专利验证)
docker exec lingnexus-gateway node /app/openclaw.mjs agent --agent validator \
  -m "验证这个专利数据"

# Deduplicator (去重简报)
docker exec lingnexus-gateway node /app/openclaw.mjs agent --agent deduplicator \
  -m "ARV-471和阿维替尼是同一个药物吗？"
```

### 测试Proxy

```bash
curl -X POST http://localhost:18790/v1/messages \
  -H "x-api-key: $(grep ANTHROPIC_OAUTH_TOKEN .env | cut -d= -f2)" \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-haiku-4-5-20251001","max_tokens":20,"messages":[{"role":"user","content":"Hi"}]}'
```

---

## 关键经验总结

### ✅ 成功要素

1. **Proxy是必须的**: Claude Code token无法直接用于OpenClaw
2. **models.json必须复制**: 从read-only workspace复制到可写的agent目录
3. **模型配置要针对性**: Sonnet用于复杂推理，Haiku用于简单任务
4. **权限要正确**: `/home/node/.openclaw`必须是node用户所有

### ⚠️ 常见陷阱

1. **不要清理volume**: `docker compose down -v`会删除所有agent配置
2. **环境变量要完整**: 需要同时设置`ANTHROPIC_OAUTH_TOKEN`和`ANTHROPIC_API_KEY`
3. **容器重启后要重新复制**: models.json不会自动同步
4. **OpenClaw不支持第三方模型**: Moonshot/Gemini会fallback到Claude

---

## 维护建议

### 日常维护

```bash
# 查看日志
docker logs lingnexus-gateway --tail 50

# 检查agent状态
docker exec lingnexus-gateway node /app/openclaw.mjs agents list

# 重启gateway
docker compose restart gateway
```

### 备份

```bash
# 备份配置
tar -czf lingnexus-backup-$(date +%Y%m%d).tar.gz D:\Projects\LingNexus

# 备份volume
docker run --rm -v lingnexus-openclaw-state:/data -v D:\backup:/backup \
  alpine tar czf /backup/openclaw-state.tar.gz /data
```

---

## 联系信息

- **项目路径**: `D:\Projects\LingNexus`
- **Gateway端口**: 18789
- **Proxy端口**: 18790
- **OpenClaw版本**: 2026.3.13
- **Docker镜像**: openclaw:local (4.11GB)

---

**文档版本**: 1.0
**创建日期**: 2026-03-16
**最后验证**: 2026-03-16 00:47 UTC
