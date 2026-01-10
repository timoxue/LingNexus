#!/bin/bash
set -e

echo "🧪 运行所有测试"

# Framework 测试
echo "Framework 测试..."
cd packages/framework
uv run pytest

# Platform Backend 测试
echo "Platform Backend 测试..."
cd ../platform/backend
uv run pytest

echo "✅ 所有测试通过"
