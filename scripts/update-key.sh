#!/usr/bin/env bash
# 热更新 Anthropic API Key（无需重启任何容器）
# 用法: ./scripts/update-key.sh <new-key>
#   或: ./scripts/update-key.sh   (交互式输入)

set -euo pipefail

PROXY_URL="http://localhost:18790"

if [ $# -ge 1 ]; then
  NEW_KEY="$1"
else
  read -rsp "请输入新的 Anthropic Key (cr_... 或 sk-...): " NEW_KEY
  echo
fi

if [ -z "$NEW_KEY" ]; then
  echo "❌ Key 不能为空" >&2
  exit 1
fi

echo "🔄 正在更新 Key..."
RESPONSE=$(curl -s -X POST "${PROXY_URL}/admin/key" \
  -H "Content-Type: application/json" \
  -d "{\"key\": \"${NEW_KEY}\"}")

if echo "$RESPONSE" | grep -q '"ok":true'; then
  PREFIX=$(echo "$RESPONSE" | grep -o '"key_prefix":"[^"]*"' | cut -d'"' -f4)
  echo "✅ Proxy Key 已更新: ${PREFIX}"

  # 同步更新 .env 文件
  ENV_FILE="$(dirname "$0")/../.env"
  if [ -f "$ENV_FILE" ]; then
    sed -i "s|^ANTHROPIC_OAUTH_TOKEN=.*|ANTHROPIC_OAUTH_TOKEN=${NEW_KEY}|" "$ENV_FILE"
    echo "✅ .env 文件已同步更新"
    echo "⚠️  Gateway 仍使用旧 Key（需重启才生效）。如需立即生效请运行:"
    echo "   docker compose restart gateway"
  fi
else
  echo "❌ 更新失败: $RESPONSE" >&2
  exit 1
fi
