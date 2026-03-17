#!/bin/bash
# Validator 智能体测试脚本（简化版）

set -e

CONTAINER="lingnexus-gateway"
BLACKBOARD_DIR="/home/node/.openclaw/blackboard"
TEST_DATA_FILE="test-validator-data.json"

echo "=========================================="
echo "LINGNEXUS Validator 测试"
echo "=========================================="
echo ""

# 1. 检查容器状态
echo "[1/5] 检查 Gateway 容器状态..."
if ! docker ps --filter "name=${CONTAINER}" --format "{{.Names}}" | grep -q "${CONTAINER}"; then
    echo "错误: Gateway 容器未运行"
    exit 1
fi
echo "Gateway 容器运行正常"
echo ""

# 2. 清空黑板数据
echo "[2/5] 清空黑板旧数据..."
docker exec ${CONTAINER} runuser -u node -- sh -c "
    rm -rf ${BLACKBOARD_DIR}/Raw_Evidence.json
    rm -rf ${BLACKBOARD_DIR}/Validated_Assets.json
    rm -rf ${BLACKBOARD_DIR}/Rejected_Evidence.json
    mkdir -p ${BLACKBOARD_DIR}
"
echo "黑板已清空"
echo ""

# 3. 准备并写入测试数据
echo "[3/5] 准备测试数据..."
python3 << 'PYTHON_SCRIPT'
import json
import sys

try:
    with open('test-validator-data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    evidence_list = [case['evidence'] for case in data['test_cases']]

    with open('raw_evidence_temp.json', 'w', encoding='utf-8') as out:
        json.dump(evidence_list, out, indent=2, ensure_ascii=False)

    total = len(data['test_cases'])
    pass_cases = len([c for c in data['test_cases'] if 'is_met: true' in c['expected']])
    fail_cases = len([c for c in data['test_cases'] if 'is_met: false' in c['expected']])

    print(f'测试用例: {total} 条 (预期通过: {pass_cases}, 预期拒绝: {fail_cases})')

except Exception as e:
    print(f'错误: {e}', file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT

echo ""

# 4. 写入黑板
echo "[4/5] 写入测试数据到黑板..."
docker cp raw_evidence_temp.json ${CONTAINER}:${BLACKBOARD_DIR}/Raw_Evidence.json
echo "测试数据已写入黑板"
echo ""

# 5. 触发 Validator
echo "[5/5] 触发 Validator 智能体..."
echo ""

docker exec ${CONTAINER} runuser -u node -- sh -c "
    cd /app && node openclaw.mjs agent --agent validator \
    --message '请从黑板 [Raw_Evidence] 读取所有 status=pending_validation 的证据，逐条执行 4 维硬性规则校验：
1. 时间范围：2023-01-01 到 2026-12-31
2. 技术类别：PROTAC/Molecular Glue/LYTAC/ATTEC/AUTAC
3. 临床阶段：Pre-Clinical/IND-Enabling/Phase I/Phase I/II
4. 国家提取：origin_country

通过的写入 [Validated_Assets]，拒绝的写入 [Rejected_Evidence]。' \
    --local
"

echo ""
echo "=========================================="
echo "检查结果"
echo "=========================================="
echo ""

# 检查 Validated_Assets
echo "--- [Validated_Assets] ---"
if docker exec ${CONTAINER} test -f ${BLACKBOARD_DIR}/Validated_Assets.json 2>/dev/null; then
    docker exec ${CONTAINER} runuser -u node -- sh -c "cat ${BLACKBOARD_DIR}/Validated_Assets.json"
else
    echo "文件不存在或为空"
fi
echo ""

# 检查 Rejected_Evidence
echo "--- [Rejected_Evidence] ---"
if docker exec ${CONTAINER} test -f ${BLACKBOARD_DIR}/Rejected_Evidence.json 2>/dev/null; then
    docker exec ${CONTAINER} runuser -u node -- sh -c "cat ${BLACKBOARD_DIR}/Rejected_Evidence.json"
else
    echo "文件不存在或为空"
fi
echo ""

echo "测试完成"
