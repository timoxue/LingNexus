#!/bin/bash
set -e

echo "📦 构建所有包"

# Framework
echo "构建 Framework..."
cd packages/framework
uv build

# Platform Backend
echo "构建 Platform Backend..."
cd ../platform/backend
uv build

# Platform Frontend
echo "构建 Platform Frontend..."
cd ../frontend
npm run build

echo "✅ 构建完成"
