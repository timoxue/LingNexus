# Investigator Sessions_Spawn 实现状态报告

## 时间
2026-03-17

## 目标
实现 Investigator agent 使用 OpenClaw 原生 sessions_spawn 进行并发搜索任务执行

## 已完成工作

### 1. 配置更新 ✅
- **AGENTS.md**: 添加 subagents 配置
  ```yaml
  ## subagents
  - investigator:
      allowAgents: ["investigator"]
      maxConcurrent: 5
      timeoutSeconds: 60
      cleanup: delete
  ```

- **SOUL.md**: 更新并发执行指南，使用 sessions_spawn
- **Memory**: 记录决策 - 必须使用 sessions_spawn，不使用手动进程管理

### 2. 模型升级 ✅
- Investigator 从 Haiku 升级到 Sonnet
- 修复 register-agents.sh，确保以 node 用户运行
- 验证：`Model: claude-sonnet-4-6`

### 3. 文档完善 ✅
- INVESTIGATOR_CONCURRENCY_V2_SESSIONS_SPAWN.md（设计文档）
- INVESTIGATOR_SESSIONS_SPAWN_IMPLEMENTATION.md（实现指南）
- test-investigator-concurrent.sh（测试脚本）

### 4. Git 提交 ✅
- Commit: `feat: Implement sessions_spawn concurrency for Investigator`
- 7 files changed, 2133 insertions(+)

## 当前阻塞问题

### API 认证失败 ❌
```
HTTP 401 authentication_error: invalid x-api-key
```

**根本原因**:
- Claude Code OAuth token (cr_...) 不能直接用作 Anthropic API key
- 需要通过 Claude Code 代理服务器 (port 18790) 转换
- 但代理服务器认证配置有问题

**尝试的解决方案**:
1. ✗ 禁用 ANTHROPIC_BASE_URL，直接调用 Anthropic API - 失败（OAuth token 无效）
2. ✗ 使用代理服务器 - 失败（401 错误）

## 可行的解决方案

### 方案 A: 使用 Gemini 模型（推荐）
Investigator 原本设计使用 Gemini 2.5 Flash：
- 1M context window
- 多语种支持优秀
- GOOGLE_API_KEY 已配置
- 无需 Claude Code 代理

**实施步骤**:
```bash
# 1. 重新注册 investigator 使用 Gemini
docker exec lingnexus-gateway bash -c \
  "cd /workspace && MODEL_INVESTIGATOR=google/gemini-2.5-flash \
   bash /workspace/scripts/register-agents.sh"

# 2. 重启 Gateway
docker compose restart gateway

# 3. 测试
docker exec lingnexus-gateway runuser -u node -- sh -c \
  "cd /app && node openclaw.mjs agent --agent investigator \
   --message 'Test' --local"
```

### 方案 B: 获取真实的 Anthropic API key
- 从 Anthropic Console 获取 sk-ant-... 格式的 API key
- 替换 ANTHROPIC_OAUTH_TOKEN
- 移除 ANTHROPIC_BASE_URL

### 方案 C: 修复 Claude Code 代理认证
- 检查 Claude Code 代理服务器配置
- 确保 OAuth token 正确传递

## 测试计划（待执行）

一旦认证问题解决：

1. **准备测试数据** (3 个任务)
   - T1: PROTAC BRD4 (en, pubmed)
   - T2: 靶向蛋白降解 (zh, pubmed)
   - T3: Molecular Glue (en, pubmed)

2. **执行并发测试**
   ```bash
   docker exec lingnexus-gateway runuser -u node -- sh -c \
     "cd /app && node openclaw.mjs agent --agent investigator \
      --message '读取 /workspace/blackboard/Pending_Tasks.json，\
      使用 sessions_spawn 并发执行所有搜索任务' --local"
   ```

3. **验证结果**
   - 检查执行时间（预期 <10s vs 顺序 ~15s）
   - 验证 Raw_Evidence.json 包含所有结果
   - 确认任务状态更新为 "completed"

4. **性能测试**
   - 3 任务并发
   - 5 任务并发（满负载）
   - 测量加速比

## 下一步行动

**立即**: 实施方案 A（使用 Gemini）
- 最快解决认证问题
- Gemini 2.5 Flash 非常适合多语种并发任务
- 1M context 足够处理大量搜索结果

**后续**: 优化和扩展
- 测试 sessions_spawn 并发性能
- 集成更多数据源
- 实现缓存机制

---

**状态**: 实现完成 95%，阻塞于 API 认证
**建议**: 使用 Gemini 模型继续测试
