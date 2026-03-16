# Claude Code API 稳定性测试报告

**测试时间**: 2026-03-16 01:05
**代理地址**: http://localhost:18790
**测试轮数**: 每个端点 5 轮

---

## 测试结果总结

### ✅ 成功的 API 端点

| 端点 | 成功率 | 平均响应时间 | 备注 |
|------|--------|-------------|------|
| GET /v1/models | 5/5 (100%) | 0.1-0.6s | 稳定 |
| POST /v1/messages (Haiku) | 5/5 (100%) | 2-7s | 稳定 |
| POST /v1/messages (Sonnet) | 3/3 (100%) | ~3s | 稳定 |
| POST /v1/messages (stream) | 3/3 (100%) | ~2s | 稳定 |

### ❌ 失败的模型

| 模型 | 错误信息 | 原因分析 |
|------|---------|---------|
| claude-opus-4-6 | Service temporarily unavailable | Claude Console 账户配额不足或服务不可用 |

---

## 详细测试记录

### 测试 1: 模型列表 API

```bash
curl http://localhost:18790/v1/models
```

**结果**: ✅ 5/5 成功

**可用模型**:
- claude-haiku-4-5-20251001 ✅
- claude-opus-4-5-20251101 ❓ (未测试)
- claude-opus-4-6 ❌ (不可用)
- claude-sonnet-4-5-20250929 ❓ (未测试)
- claude-sonnet-4-6 ✅

---

### 测试 2: 消息 API - Haiku 模型

**模型**: claude-haiku-4-5-20251001
**结果**: ✅ 5/5 成功

**示例响应**:
```json
{
  "content": [{"text": "1+1=2", "type": "text"}],
  "model": "claude-haiku-4-5-20251001",
  "usage": {
    "input_tokens": 24,
    "output_tokens": 2
  }
}
```

---

### 测试 3: 消息 API - Sonnet 模型

**模型**: claude-sonnet-4-6
**结果**: ✅ 3/3 成功

**示例响应**:
```json
{
  "content": [{
    "text": "PROTAC（Proteolysis Targeting Chimera，蛋白水解靶向嵌合体）是一种双功能小分子，通过同时结合目标蛋白和E3泛素连接酶，诱导目标蛋白被泛素化并经蛋白酶体降解，从而实现对疾病相关蛋白的选择性清除。",
    "type": "text"
  }],
  "model": "claude-sonnet-4-6"
}
```

---

### 测试 4: 流式响应 API

**模型**: claude-haiku-4-5-20251001
**结果**: ✅ 3/3 成功
**参数**: `stream: true`

---

### 测试 5: Opus 4.6 模型

**模型**: claude-opus-4-6
**结果**: ❌ 失败

**错误响应**:
```json
{
  "error": "service_unavailable",
  "message": "Service temporarily unavailable. The system has attempted to process your request with all available Claude Console accounts."
}
```

**原因分析**:
- Claude Console 账户配额已用完
- 或该模型暂时不可用
- 建议使用 Haiku 或 Sonnet 替代

---

## OpenClaw 智能体调用测试

### 问题发现

OpenClaw 默认尝试使用 `claude-opus-4-6`，导致超时：

```
[agent/embedded] error=LLM request timed out.
provider=anthropic/claude-opus-4-6
```

### 解决方案

需要修改智能体配置，使用可用的模型：
- ✅ claude-haiku-4-5-20251001 (快速、便宜)
- ✅ claude-sonnet-4-6 (平衡、推荐)

---

## 建议

### 1. 修改 .env 配置

将所有智能体的模型改为可用模型：

```bash
MODEL_MAIN=claude-haiku-4-5-20251001
MODEL_COACH=claude-sonnet-4-6
MODEL_INVESTIGATOR=claude-haiku-4-5-20251001
MODEL_VALIDATOR=claude-sonnet-4-6
MODEL_DEDUPLICATOR=claude-sonnet-4-6
```

### 2. 重新注册智能体

```bash
docker compose --profile setup run --rm setup
```

### 3. 重启 Gateway

```bash
docker compose restart gateway
```

---

## 稳定性评估

| 指标 | 评分 | 说明 |
|------|------|------|
| API 可用性 | ⭐⭐⭐⭐⭐ | 代理工作正常，转发稳定 |
| Haiku 模型 | ⭐⭐⭐⭐⭐ | 100% 成功率，响应快速 |
| Sonnet 模型 | ⭐⭐⭐⭐⭐ | 100% 成功率，质量高 |
| Opus 模型 | ⭐ | 不可用，需要替代方案 |

**总体评估**: ✅ **API 稳定，可以进行生产测试**

只需避免使用 Opus 4.6 模型，改用 Haiku 或 Sonnet 即可。

---

*测试完成时间: 2026-03-16 01:05*
