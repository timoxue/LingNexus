#!/bin/bash
# 构建 LingNexus 自定义镜像

set -e

echo "🏗️  开始构建 LingNexus 镜像..."
echo ""

# 检查 openclaw:local 是否存在
if ! docker image inspect openclaw:local &> /dev/null; then
    echo "❌ 错误: 基础镜像 openclaw:local 不存在"
    echo "请先确保 OpenClaw 镜像已安装"
    exit 1
fi

# 构建镜像
docker build \
    -f Dockerfile.lingnexus \
    -t lingnexus:latest \
    --progress=plain \
    .

echo ""
echo "✅ 镜像构建完成！"
echo ""
echo "镜像信息:"
docker images lingnexus:latest

echo ""
echo "📦 镜像大小对比:"
echo "基础镜像 (openclaw:local):"
docker images openclaw:local --format "  {{.Size}}"
echo "LingNexus 镜像:"
docker images lingnexus:latest --format "  {{.Size}}"

echo ""
echo "🚀 下一步: 运行 'docker compose up gateway -d' 启动服务"
