#!/bin/bash
# 系统功能测试脚本

echo "=========================================="
echo " LINGNEXUS 系统测试"
echo "=========================================="
echo ""

# 1. 检查容器状态
echo "1. 检查容器状态..."
docker ps --filter "name=lingnexus" --format "table {{.Names}}\t{{.Status}}"
echo ""

# 2. 检查代理服务器
echo "2. 测试代理服务器..."
curl -s -X POST http://localhost:18790/v1/messages \
  -H "x-api-key: ${ANTHROPIC_OAUTH_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-sonnet-4-6","max_tokens":50,"messages":[{"role":"user","content":"Hi"}]}' \
  | jq -r '.content[0].text' 2>/dev/null || echo "代理服务器测试失败"
echo ""

# 3. 测试 Deep COI Parsing
echo "3. 测试 Deep COI Parsing..."
docker exec lingnexus-gateway sh -c "cd /workspace && python3 skills/engines/medical_engine.py 'PROTAC BRD4' pubmed 2>&1 | head -20"
echo ""

# 4. 列出已注册的智能体
echo "4. 列出已注册的智能体..."
docker exec lingnexus-gateway sh -c "cd /app && node openclaw.mjs agents list"
echo ""

echo "=========================================="
echo " 测试完成"
echo "=========================================="
