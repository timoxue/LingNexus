#!/bin/bash
echo "=========================================="
echo " LINGNEXUS Agent 全面测试"
echo "=========================================="
echo ""

echo "1. 测试 main agent (Claude Haiku)..."
docker exec openclaw-gateway bash -c 'cd /app && node openclaw.mjs agent --agent main --local -m "测试"' 2>&1 | grep -v "^\[plugins\]" | tail -2
echo ""

echo "2. 测试 validator agent (Claude Sonnet)..."
docker exec openclaw-gateway bash -c 'cd /app && node openclaw.mjs agent --agent validator --local -m "测试"' 2>&1 | grep -v "^\[plugins\]" | tail -2
echo ""

echo "3. 测试 investigator agent (Gemini)..."
docker exec openclaw-gateway bash -c 'cd /app && node openclaw.mjs agent --agent investigator --local -m "测试"' 2>&1 | grep -v "^\[plugins\]" | tail -2
echo ""

echo "4. 测试 coach agent (Moonshot/Kimi)..."
docker exec openclaw-gateway bash -c 'cd /app && node openclaw.mjs agent --agent coach --local -m "测试"' 2>&1 | grep -v "^\[plugins\]" | tail -2
echo ""

echo "5. 测试 deduplicator agent (DashScope/Qwen)..."
docker exec openclaw-gateway bash -c 'cd /app && node openclaw.mjs agent --agent deduplicator --local -m "测试"' 2>&1 | grep -v "^\[plugins\]" | tail -2
echo ""

echo "=========================================="
echo " 测试完成"
echo "=========================================="
