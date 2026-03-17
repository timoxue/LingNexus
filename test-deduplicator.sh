#!/bin/bash
# Deduplicator 智能体测试脚本
# 测试跨语言去重和 Markdown 简报生成

set -e

CONTAINER="lingnexus-gateway"
BLACKBOARD_DIR="/workspace/.openclaw/blackboard-test"

echo "=========================================="
echo "LINGNEXUS Deduplicator 测试"
echo "=========================================="
echo ""

# 1. 检查容器状态
echo "[1/4] 检查 Gateway 容器状态..."
if ! docker ps --filter "name=${CONTAINER}" --format "{{.Names}}" | grep -q "${CONTAINER}"; then
    echo "错误: Gateway 容器未运行"
    exit 1
fi
echo "Gateway 容器运行正常"
echo ""

# 2. 检查输入数据
echo "[2/4] 检查 Validated_Assets 输入数据..."
ASSET_COUNT=$(docker exec ${CONTAINER} runuser -u node -- sh -c "cat ${BLACKBOARD_DIR}/Validated_Assets.json" | python3 -c "import json, sys; print(len(json.load(sys.stdin)))")
echo "Validated_Assets 数据量: ${ASSET_COUNT} 条"

if [ "${ASSET_COUNT}" -eq "0" ]; then
    echo "错误: 没有可用的验证资产"
    echo "请先运行 Validator 测试: ./test-validator-simple.sh"
    exit 1
fi

echo "输入数据概览:"
docker exec ${CONTAINER} runuser -u node -- sh -c "cat ${BLACKBOARD_DIR}/Validated_Assets.json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for item in data:
    print(f\"  - {item['drug_candidate']} ({item['origin_country']}, {item['degrader_modality']}, {item['clinical_stage']})\")
"
echo ""

# 3. 触发 Deduplicator
echo "[3/4] 触发 Deduplicator 智能体..."
echo ""

docker exec ${CONTAINER} runuser -u node -- sh -c "
    cd /app && node openclaw.mjs agent --agent deduplicator \
    --message '请从黑板 [Validated_Assets] 读取所有 is_met=true 的资产（共${ASSET_COUNT}条），执行跨语言去重，生成高管级 Markdown 简报。

简报要求：
1. 执行摘要：2-3句话总结核心发现
2. 情报详情：每个药物一个表格，包含研发主体、国家、靶点、降解剂类型、临床阶段、专利号、关键证据
3. 数据质量说明：数据来源、校验通过率、生成时间

请按照 SOUL.md 中的 Markdown 模板格式输出。' \
    --local
" 2>&1 | tee deduplicator_output.log

echo ""
echo "=========================================="
echo "测试完成"
echo "=========================================="
echo ""

# 4. 检查输出
echo "[4/4] 检查生成的 Markdown 简报..."
echo ""

if grep -q "# LINGNEXUS" deduplicator_output.log; then
    echo "✅ Markdown 简报已生成"
    echo ""
    echo "--- 简报预览 ---"
    grep -A 100 "# LINGNEXUS" deduplicator_output.log | head -80
else
    echo "⚠️  未找到 Markdown 简报"
fi

echo ""
echo "完整输出已保存到: deduplicator_output.log"
