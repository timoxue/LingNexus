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
#  Step 1: 注册 Anthropic Provider（统一走代理）
# ══════════════════════════════════════════════════════
echo ""
echo "--- Step 1: Registering Anthropic provider ---"

# Key 由 proxy 统一管理，无需各 agent 单独配置
if [ -z "${ANTHROPIC_OAUTH_TOKEN}" ] || [[ "${ANTHROPIC_OAUTH_TOKEN}" == *"xxx"* ]]; then
  echo "  [ERROR] ANTHROPIC_OAUTH_TOKEN not set — agents will fail"
  exit 1
fi

echo "  Registering anthropic provider (via proxy)..."
echo "${ANTHROPIC_OAUTH_TOKEN}" | $CLI models auth paste-token \
  --provider "anthropic" \
  --profile-id "anthropic:claude-code" \
  2>/dev/null \
  && echo "  [OK] anthropic token registered" \
  || echo "  [WARN] anthropic token registration issue"

# 写入代理 base URL
if [ -n "${ANTHROPIC_BASE_URL}" ]; then
  $CLI config set providers.anthropic.baseUrl "${ANTHROPIC_BASE_URL}" 2>/dev/null \
    && echo "  [OK] anthropic baseUrl set: ${ANTHROPIC_BASE_URL}" \
    || echo "  [WARN] could not set baseUrl via config, will rely on env var"
fi

# ══════════════════════════════════════════════════════
#  Step 2: 模型分配（全部走 Anthropic 代理）
# ══════════════════════════════════════════════════════
# main         → claude-haiku-4-5     (轻量路由)
# coach        → claude-sonnet-4-6    (策略推理)
# investigator → claude-haiku-4-5     (高速多语种采集)
# validator    → claude-sonnet-4-6    (严格 JSON 遵循)
# deduplicator → claude-sonnet-4-6    (跨语种消歧)

MODEL_MAIN="${MODEL_MAIN:-claude-haiku-4-5-20251001}"
MODEL_COACH="${MODEL_COACH:-claude-sonnet-4-6}"
MODEL_INVESTIGATOR="${MODEL_INVESTIGATOR:-claude-haiku-4-5-20251001}"
MODEL_VALIDATOR="${MODEL_VALIDATOR:-claude-sonnet-4-6}"
MODEL_DEDUPLICATOR="${MODEL_DEDUPLICATOR:-claude-sonnet-4-6}"

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
    || echo "  [INFO] ${NAME} exists, patching workspace..."

  # 强制修正 workspace（agents add 对已存在的 agent 会跳过，需手动 patch openclaw.json）
  python3 -c "
import json, sys
path = '/home/node/.openclaw/openclaw.json'
with open(path) as f:
    cfg = json.load(f)
for a in cfg.get('agents', {}).get('list', []):
    if a['id'] == '${NAME}':
        a['name'] = '${NAME}'
        a['workspace'] = '${WORKSPACE_DIR}'
        a['agentDir'] = '/home/node/.openclaw/agents/${NAME}/agent'
        a['model'] = '${MODEL}'
        break
with open(path, 'w') as f:
    json.dump(cfg, f, indent=4)
print('  [OK] ${NAME} workspace patched -> ${WORKSPACE_DIR}')
" 2>/dev/null || echo "  [WARN] patch skipped (openclaw.json not found yet)"
}

register_agent "main"         "${MODEL_MAIN}"
register_agent "coach"        "${MODEL_COACH}"
register_agent "investigator" "${MODEL_INVESTIGATOR}"
register_agent "validator"    "${MODEL_VALIDATOR}"
register_agent "deduplicator" "${MODEL_DEDUPLICATOR}"

# ══════════════════════════════════════════════════════
#  Step 3.5: 配置 Anthropic Provider（所有 agent）
# ══════════════════════════════════════════════════════
echo ""
echo "--- Step 3.5: Configuring Anthropic provider ---"
bash /workspace/scripts/configure-anthropic.sh

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
