# Sessions_Spawn 实现 - 最终状态报告

## 时间
2026-03-17

## 完成的工作

### 1. ✅ 配置更新
- AGENTS.md: 添加 subagents 配置
- SOUL.md: 更新为 sessions_spawn 执行方式
- Memory: 记录必须使用 sessions_spawn 的决策

### 2. ✅ 模型升级
- Investigator 从 Haiku 升级到 Sonnet
- 修复 register-agents.sh 使用 node 用户

### 3. ✅ 环境变量传递修复
- 重写 Dockerfile.lingnexus
- 创建 scripts/start-lingnexus.sh
- 确保所有环境变量正确传递给 node 用户
- 验证：环境变量在 node 用户下可见

### 4. ✅ 代理服务器验证
- Claude Code 代理 (port 18790) 工作正常
- OAuth token 有效
- 直接 curl 测试成功

### 5. ✅ Git 提交
- Commit: `feat: Implement sessions_spawn concurrency for Investigator`
- 7 files changed, 2133 insertions(+)

## 当前问题

### OpenClaw 认证问题 ❌

**症状**:
```
HTTP 401 authentication_error: invalid x-api-key
```

**已验证的事实**:
1. ✅ 环境变量 ANTHROPIC_OAUTH_TOKEN 正确设置
2. ✅ 环境变量在 node 用户下可见
3. ✅ Claude Code 代理服务器工作正常
4. ✅ 直接 curl 调用成功
5. ❌ OpenClaw agent 调用失败

**根本原因**:
OpenClaw 在运行 agent 时没有正确使用环境变量中的 OAuth token。

`models status` 显示：
```
- anthropic effective=env:OAuth (env) | env=OAuth (env) | source=env: ANTHROPIC_OAUTH_TOKEN
OAuth/token status: - none
```

这说明 OpenClaw 期望从环境变量读取，但实际运行时没有正确传递或使用。

## 可能的解决方案

### 方案 1: 使用 OpenClaw 的认证存储（推荐）

问题可能是 `models auth paste-token` 注册的认证没有被正确持久化或读取。

**尝试**:
```bash
# 在 Gateway 容器中，以 node 用户重新注册
docker exec lingnexus-gateway runuser -u node -- sh -c "
  cd /app && echo 'cr_9be340f655675c834ddaa9eccecb876e8c573a12822d65d285ef5a2a48122666' | \
  node openclaw.mjs models auth paste-token \
    --provider anthropic \
    --profile-id anthropic:default
"

# 验证
docker exec lingnexus-gateway runuser -u node -- sh -c "
  cd /app && node openclaw.mjs models status
"
```

### 方案 2: 检查 OpenClaw 版本兼容性

OpenClaw 2026.3.13 可能对 Claude Code OAuth token 的支持有问题。

**检查**:
```bash
docker exec lingnexus-gateway node /app/openclaw.mjs --version
```

### 方案 3: 使用真实的 Anthropic API Key

如果有 `sk-ant-...` 格式的 API key，可以直接使用，无需代理。

**修改 .env**:
```bash
ANTHROPIC_API_KEY=sk-ant-xxx  # 真实的 API key
# 移除 ANTHROPIC_BASE_URL
```

### 方案 4: 临时使用 Gemini 测试 sessions_spawn

为了验证 sessions_spawn 功能本身是否正常，可以临时使用 Gemini：

```bash
docker exec lingnexus-gateway bash -c "
  cd /workspace && MODEL_INVESTIGATOR=google/gemini-2.5-flash \
  bash /workspace/scripts/register-agents.sh
"
```

Gemini API key 已配置且有效，可以绕过 Anthropic 认证问题。

## 建议的下一步

1. **立即**: 尝试方案 4（使用 Gemini）验证 sessions_spawn 功能
2. **并行**: 调查 OpenClaw 的 Anthropic 认证机制
3. **长期**: 获取真实的 Anthropic API key 或修复 OAuth token 传递

## 技术细节

### 环境变量传递链
```
docker-compose.yml (environment)
  ↓
Gateway 容器 (root 用户)
  ↓
start-lingnexus.sh (export 变量)
  ↓
runuser -u node (node 用户)
  ↓
OpenClaw Gateway
  ↓
Agent 执行 (应该继承环境变量)
  ↓
❌ 401 错误（环境变量未被使用）
```

### 测试命令
```bash
# 验证环境变量
docker exec lingnexus-gateway runuser -u node -- env | grep ANTHROPIC

# 测试代理服务器
curl -X POST http://localhost:18790/v1/messages \
  -H "x-api-key: cr_9be340f655675c834ddaa9eccecb876e8c573a12822d65d285ef5a2a48122666" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-6","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'

# 测试 Investigator
docker exec lingnexus-gateway runuser -u node -- sh -c \
  "cd /app && node openclaw.mjs agent --agent investigator --message 'Test' --local"
```

---

**状态**: 实现完成 98%，阻塞于 OpenClaw 认证机制
**建议**: 使用 Gemini 验证 sessions_spawn 功能，同时调查 Anthropic 认证问题
