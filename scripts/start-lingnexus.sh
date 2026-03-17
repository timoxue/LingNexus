#!/bin/bash
set -e

# 标记文件，避免重复安装
INSTALL_MARKER="/tmp/.lingnexus-deps-installed"

if [ ! -f "$INSTALL_MARKER" ]; then
    echo "📦 首次启动：安装依赖（Python + 浏览器）..."
    export DEBIAN_FRONTEND=noninteractive

    # 移除可能有问题的安全源
    rm -f /etc/apt/sources.list.d/debian-security.list 2>/dev/null || true

    # 更新包列表
    apt-get update -qq || true

    # 安装 Python 依赖
    echo "  → 安装 Python 工具..."
    apt-get install -y --no-install-recommends python3-pip > /dev/null 2>&1 || true
    pip3 install --no-cache-dir --break-system-packages beautifulsoup4 biopython > /dev/null 2>&1 || true

    # 安装浏览器依赖
    echo "  → 安装浏览器依赖..."
    apt-get install -y --no-install-recommends --fix-missing \
        xvfb libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
        libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
        libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
        > /dev/null 2>&1 || true

    # 尝试安装 Chromium（可选）
    echo "  → 安装 Chromium..."
    apt-get install -y --no-install-recommends --fix-missing chromium > /dev/null 2>&1 || \
        echo "    ⚠️  Chromium 安装失败（网络问题），将使用 OpenClaw 内置浏览器"

    rm -rf /var/lib/apt/lists/*
    touch "$INSTALL_MARKER"
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装，快速启动"
fi

# 启动虚拟显示服务器
if command -v Xvfb &> /dev/null; then
    Xvfb :99 -screen 0 1280x1024x24 &> /dev/null &
    sleep 2
    export DISPLAY=:99
fi

# 切换到 node 用户并启动 OpenClaw Gateway
# 重要：传递所有环境变量给 node 用户
echo "🚀 启动 OpenClaw Gateway..."
exec runuser -u node -- bash -c "
  export ANTHROPIC_OAUTH_TOKEN='${ANTHROPIC_OAUTH_TOKEN}'
  export ANTHROPIC_API_KEY='${ANTHROPIC_API_KEY}'
  export ANTHROPIC_BASE_URL='${ANTHROPIC_BASE_URL}'
  export MOONSHOT_API_KEY='${MOONSHOT_API_KEY}'
  export GOOGLE_API_KEY='${GOOGLE_API_KEY}'
  export OPENROUTER_API_KEY='${OPENROUTER_API_KEY}'
  export NCBI_EMAIL='${NCBI_EMAIL}'
  export OPENCLAW_LOG_LEVEL='${OPENCLAW_LOG_LEVEL}'
  export DISPLAY=:99
  cd /app && node openclaw.mjs gateway --allow-unconfigured --port 18789 --bind loopback --auth ${OPENCLAW_AUTH_MODE:-none}
"
