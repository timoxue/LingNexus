#!/bin/bash
# Python 依赖安装脚本
# 在 Docker 容器内自动安装 Investigator 所需的 Python 库

set -e

echo "=========================================="
echo "安装 Python 依赖（Investigator Agent）"
echo "=========================================="

# 检查 Python 是否可用
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，尝试安装..."
    apt-get update && apt-get install -y python3 python3-pip
fi

# 检查 pip 是否可用
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未安装，尝试安装..."
    apt-get update && apt-get install -y python3-pip
fi

echo "✅ Python 版本: $(python3 --version)"
echo "✅ pip 版本: $(pip3 --version)"

# 安装依赖
echo ""
echo "正在安装依赖..."
pip3 install --no-cache-dir --break-system-packages beautifulsoup4 biopython

echo ""
echo "=========================================="
echo "✅ Python 依赖安装完成！"
echo "=========================================="
echo "已安装："
echo "  - beautifulsoup4 (HTML 解析)"
echo "  - biopython (PubMed API)"
echo ""
