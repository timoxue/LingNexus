#!/bin/bash
# LINGNEXUS — Agent 注册脚本（在 setup 容器内运行）
set -e

# 确保以 node 用户运行 openclaw 命令
CLI="runuser -u node -- node /app/openclaw.mjs"
WORKSPACE="/workspace"

echo "=================================================="
echo " LINGNEXUS Agent Matrix Registration"
echo "=================================================="

# 确保 node 用户的 .openclaw 目录存在
mkdir -p /home/node/.openclaw
chown -R node:node /home/node/.openclaw

# ══════════════════════════════════════════════════════
#  Step 1: 注册第三方模型 Provider API Keys
# ══════════════════════════════════════════════════════
echo ""
echo "--- Step 1: Registering provider API keys ---"

register_provider() {
  local PROVIDER=$1
  local KEY_VAR=$2
  local KEY_VAL="${!KEY_VAR}"

  if [ -z "${KEY_VAL}" ] || [[ "${KEY_VAL}" == *"xxx"* ]]; then
    echo "  [SKIP] ${PROVIDER}: ${KEY_VAR} not set"
    return 0
  fi

  echo "  Registering provider: ${PROVIDER}"
  echo "${KEY_VAL}" | $CLI models auth paste-token \
    --provider "${PROVIDER}" \
    --profile-id "${PROVIDER}:auto" \
    2>/dev/null \
    && echo "  [OK] ${PROVIDER} key registered" \
    || echo "  [WARN] ${PROVIDER} registration issue, continuing..."
}

# ── Anthropic: 使用 Claude Code 订阅的 OAuth Token ──────────
# OpenClaw 读取 ANTHROPIC_OAUTH_TOKEN (cr_...) + ANTHROPIC_BASE_URL
if [ -z "${ANTHROPIC_OAUTH_TOKEN}" ] || [[ "${ANTHROPIC_OAUTH_TOKEN}" == *"xxx"* ]]; then
  echo "  [ERROR] ANTHROPIC_OAUTH_TOKEN not set — Claude agents will fail"
  exit 1
fi

echo "  Registering anthropic provider (Claude Code OAuth)..."
# 写入 OAuth token
echo "${ANTHROPIC_OAUTH_TOKEN}" | $CLI models auth paste-token \
  --provider "anthropic" \
  --profile-id "anthropic:claude-code" \
  2>/dev/null \
  && echo "  [OK] anthropic OAuth token registered" \
  || echo "  [WARN] anthropic token registration issue"

# 写入自定义 base URL
if [ -n "${ANTHROPIC_BASE_URL}" ]; then
  $CLI config set providers.anthropic.baseUrl "${ANTHROPIC_BASE_URL}" 2>/dev/null \
    && echo "  [OK] anthropic baseUrl set: ${ANTHROPIC_BASE_URL}" \
    || echo "  [WARN] could not set baseUrl via config, will rely on env var"
fi

# Moonshot AI / Kimi (coach)
register_provider "kimi-coding" "MOONSHOT_API_KEY"

# Google AI Studio (investigator)
register_provider "google"      "GOOGLE_API_KEY"

# OpenRouter (deduplicator — routes to Qwen)
register_provider "openrouter"  "OPENROUTER_API_KEY"

# ══════════════════════════════════════════════════════
#  Step 2: 异构模型分配方案
# ══════════════════════════════════════════════════════
# main         → claude-haiku-4-5     (轻量路由)
# coach        → kimi-k2-thinking     (中文医药策略推理)
# investigator → gemini-2.5-flash     (1M ctx，多语种极速)
# validator    → claude-sonnet-4-6    (严格 JSON 遵循)
# deduplicator → qwen3-235b (OpenRouter) (中英日跨语种消歧)

MODEL_MAIN="${MODEL_MAIN:-claude-haiku-4-5-20251001}"
MODEL_COACH="${MODEL_COACH:-kimi-coding/kimi-k2-thinking}"
MODEL_INVESTIGATOR="${MODEL_INVESTIGATOR:-google/gemini-2.5-flash}"
MODEL_VALIDATOR="${MODEL_VALIDATOR:-claude-sonnet-4-6}"
MODEL_DEDUPLICATOR="${MODEL_DEDUPLICATOR:-openrouter/qwen/qwen3.5-27b}"

echo ""
echo "--- Step 2: Agent model assignments ---"
echo "  main          -> ${MODEL_MAIN}"
echo "  coach         -> ${MODEL_COACH}"
echo "  investigator  -> ${MODEL_INVESTIGATOR}"
echo "  validator     -> ${MODEL_VALIDATOR}"
echo "  deduplicator  -> ${MODEL_DEDUPLICATOR}"

# ══════════════════════════════════════════════════════
#  Step 3: 注册 Agent（绑定各自模型）
# ══════════════════════════════════════════════════════
echo ""
echo "--- Step 3: Registering agents ---"

register_agent() {
  local NAME=$1
  local MODEL=$2
  local WORKSPACE_DIR="${WORKSPACE}/agents/${NAME}"

  echo ""
  echo "  Registering: ${NAME} -> ${MODEL}"
  $CLI agents add "${NAME}" \
    --workspace "${WORKSPACE_DIR}" \
    --model "${MODEL}" \
    --non-interactive \
    --json 2>/dev/null \
    && echo "  [OK] ${NAME} registered" \
    || echo "  [WARN] ${NAME} may already exist, skipping..."
}

register_agent "main"         "${MODEL_MAIN}"
register_agent "coach"        "${MODEL_COACH}"
register_agent "investigator" "${MODEL_INVESTIGATOR}"
register_agent "validator"    "${MODEL_VALIDATOR}"
register_agent "deduplicator" "${MODEL_DEDUPLICATOR}"

# ══════════════════════════════════════════════════════
#  Step 4: 绑定飞书渠道 + 全局配置
# ══════════════════════════════════════════════════════
echo ""
echo "--- Step 4: Channel binding + global config ---"

$CLI agents bind main feishu --non-interactive 2>/dev/null \
  && echo "  [OK] feishu -> main binding set" \
  || echo "  [WARN] binding may exist, continuing..."

$CLI config set gateway.mode local  2>/dev/null || true
$CLI config set gateway.port 18789  2>/dev/null || true
$CLI config set memory.shared true  2>/dev/null || true
echo "  [OK] Global config applied"

# ══════════════════════════════════════════════════════
#  Step 5: 验证
# ══════════════════════════════════════════════════════
echo ""
echo "--- Step 5: Verification ---"
$CLI agents list 2>/dev/null

echo ""
echo "  Provider auth status:"
$CLI models status --plain 2>/dev/null | grep -E "kimi|google|openrouter|anthropic" || true

echo ""
echo "=================================================="
echo " LINGNEXUS setup complete!"
echo " Next: docker compose up gateway -d"
echo "=================================================="
