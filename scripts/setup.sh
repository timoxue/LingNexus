#!/bin/bash
# 使用 uv 快速设置项目

set -e

echo "=========================================="
echo "LingNexus 项目设置"
echo "=========================================="
echo

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ 未找到 uv"
    echo "   正在安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv 已安装"
    echo "   请重新运行此脚本或手动执行: source ~/.cargo/env"
    exit 1
fi

echo "✅ 检测到 uv"
echo

# 同步依赖
echo "📦 正在安装依赖..."
uv sync

echo
echo "✅ 依赖安装完成"
echo

# 加载 Skills
echo "🔍 正在加载 Skills..."
python scripts/load_claude_skills.py --generate-only

echo
echo "=========================================="
echo "✅ 项目设置完成！"
echo "=========================================="
echo
echo "下一步："
echo "  1. 运行 'uv run python scripts/load_claude_skills.py' 来注册 Skills"
echo "  2. 查看 README.md 了解如何使用"
echo

