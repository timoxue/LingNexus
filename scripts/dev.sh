#!/bin/bash
# 启动开发环境

set -e

echo "🚀 启动 LingNexus 开发环境"

# 1. 安装依赖
echo "📦 安装依赖..."
uv sync

# 2. 初始化数据库
if [ ! -f "data/intelligence.db" ]; then
    echo "🗄️  初始化数据库..."
    cd packages/platform/backend
    uv run python -m scripts.init_db
    cd ../..
fi

# 3. 启动后端（后台运行）
echo "🔧 启动后端服务..."
cd packages/platform/backend
uv run uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# 4. 启动前端
echo "🎨 启动前端服务..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ 开发环境已启动！"
echo "   前端: http://localhost:5173"
echo "   后端: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获退出信号
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

wait
