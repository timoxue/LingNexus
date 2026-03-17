#!/bin/bash
# 手动端到端工作流测试（逐步执行）

set -e

CONTAINER="lingnexus-gateway"
BLACKBOARD_DIR="/workspace/.openclaw/blackboard-test"

echo "=========================================="
echo "LINGNEXUS 手动端到端工作流测试"
echo "=========================================="
echo ""

TEST_QUERY="请挖掘全球 PROTAC BRD4 靶向药的最新专利，重点关注 2023-2026 年间的临床早期项目"

# 1. 清空黑板
echo "[Step 0] 清空黑板..."
docker exec ${CONTAINER} runuser -u node -- sh -c "
    rm -rf ${BLACKBOARD_DIR}/*.json
    mkdir -p ${BLACKBOARD_DIR}
"
echo "✅ 黑板已清空"
echo ""

# 2. Step 1: Coach - 查询拆解
echo "[Step 1] Coach - 查询拆解..."
echo "查询: ${TEST_QUERY}"
echo ""

docker exec ${CONTAINER} runuser -u node -- sh -c "
    cd /app && node openclaw.mjs agent --agent coach \
    --message '任务：${TEST_QUERY}

请将此查询拆解为 5 条多语种搜索子任务，写入黑板 [Pending_Tasks]。

要求：
1. 覆盖中、英、日、韩、德五种语言
2. 每条任务包含：task_id, language, region, target_source, search_query, priority, status
3. 搜索关键词：PROTAC + BRD4 + 2023-2026 + Pre-Clinical/IND/Phase I
4. 数据源：PubMed, USPTO, CNIPA, J-PlatPat, Espacenet' \
    --local
" 2>&1 | tail -50

echo ""

# 检查 Pending_Tasks
if docker exec ${CONTAINER} test -f ${BLACKBOARD_DIR}/Pending_Tasks.json 2>/dev/null; then
    TASK_COUNT=$(docker exec ${CONTAINER} runuser -u node -- sh -c "cat ${BLACKBOARD_DIR}/Pending_Tasks.json" | python3 -c "import json, sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo "✅ Coach 完成：生成 ${TASK_COUNT} 条任务"
else
    echo "❌ Coach 失败：未生成 Pending_Tasks"
    exit 1
fi
echo ""

# 3. Step 2: Investigator - 数据采集
echo "[Step 2] Investigator - 数据采集..."
echo "注意：由于实际搜索需要时间，我们使用模拟数据"
echo ""

# 创建模拟的 Raw_Evidence 数据
cat > /tmp/mock_raw_evidence.json << 'EOF'
[
  {
    "evidence_id": "E_E2E_001",
    "source_task_id": "T1_EN_GLOBAL",
    "language": "en",
    "region": "US",
    "source_url": "https://pubmed.ncbi.nlm.nih.gov/38123456",
    "source_name": "PubMed",
    "raw_text": "Arvinas Inc. (Connecticut, USA) disclosed ARV-825, a PROTAC compound targeting BRD4 for degradation. Patent US2024789012 filed on June 15, 2024. The compound is currently in Pre-Clinical development, demonstrating potent BRD4 degradation in breast cancer cell lines.",
    "crawled_at": "2026-03-17T12:00:00Z",
    "status": "pending_validation"
  },
  {
    "evidence_id": "E_E2E_002",
    "source_task_id": "T2_ZH_CHINA",
    "language": "zh",
    "region": "CN",
    "source_url": "https://www.yaozh.com/patent/CN202410987654",
    "source_name": "药智网",
    "raw_text": "中国科学院上海药物研究所于2024年8月申请专利CN202410987654，公开了一种靶向BRD4的PROTAC降解剂SH-BRD4-01。该化合物处于临床前研究阶段，在体外实验中显示出良好的BRD4蛋白降解活性。",
    "crawled_at": "2026-03-17T12:05:00Z",
    "status": "pending_validation"
  },
  {
    "evidence_id": "E_E2E_003",
    "source_task_id": "T3_JA_JAPAN",
    "language": "ja",
    "region": "JP",
    "source_url": "https://www.j-platpat.jp/patent/JP2024-123456",
    "source_name": "J-PlatPat",
    "raw_text": "武田薬品工業株式会社（大阪、日本）は2023年11月に特許JP2024-123456を出願し、BRD4を標的とするPROTAC化合物TAK-BRD4を開示した。本化合物は第I相臨床試験の準備段階（IND申請中）にあり、血液がんを対象としている。",
    "crawled_at": "2026-03-17T12:10:00Z",
    "status": "pending_validation"
  },
  {
    "evidence_id": "E_E2E_004",
    "source_task_id": "T1_EN_GLOBAL",
    "language": "en",
    "region": "US",
    "source_url": "https://patents.google.com/patent/US2022555555",
    "source_name": "Google Patents",
    "raw_text": "C4 Therapeutics filed patent US2022555555 on November 10, 2022, describing a BRD4-targeting PROTAC. The compound is in Pre-Clinical stage. (Note: This should be rejected due to 2022 date)",
    "crawled_at": "2026-03-17T12:15:00Z",
    "status": "pending_validation"
  },
  {
    "evidence_id": "E_E2E_005",
    "source_task_id": "T2_ZH_CHINA",
    "language": "zh",
    "region": "CN",
    "source_url": "https://example.com/news",
    "source_name": "医药观察家",
    "raw_text": "恒瑞医药的BRD4抑制剂HR-BRD4-02于2024年5月进入二期临床试验。该药物采用传统小分子抑制剂技术，非PROTAC降解剂。(Note: Should be rejected - Phase II and not PROTAC)",
    "crawled_at": "2026-03-17T12:20:00Z",
    "status": "pending_validation"
  }
]
EOF

docker cp /tmp/mock_raw_evidence.json ${CONTAINER}:${BLACKBOARD_DIR}/Raw_Evidence.json
echo "✅ Investigator 完成：生成 5 条原始证据（模拟数据）"
echo ""

# 4. Step 3: Validator - 质量校验
echo "[Step 3] Validator - 质量校验..."
echo ""

docker exec ${CONTAINER} runuser -u node -- sh -c "
    cd /app && node openclaw.mjs agent --agent validator \
    --message '请从黑板 [Raw_Evidence] 读取所有 status=pending_validation 的证据（共5条），逐条执行 4 维硬性规则校验：
1. 时间范围：2023-01-01 到 2026-12-31
2. 技术类别：PROTAC/Molecular Glue/LYTAC/ATTEC/AUTAC
3. 临床阶段：Pre-Clinical/IND-Enabling/Phase I/Phase I/II
4. 国家提取：origin_country

通过的写入 [Validated_Assets]，拒绝的写入 [Rejected_Evidence]。' \
    --local
" 2>&1 | tail -60

echo ""

# 检查 Validator 输出
if docker exec ${CONTAINER} test -f ${BLACKBOARD_DIR}/Validated_Assets.json 2>/dev/null; then
    VALIDATED_COUNT=$(docker exec ${CONTAINER} runuser -u node -- sh -c "cat ${BLACKBOARD_DIR}/Validated_Assets.json" | python3 -c "import json, sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo "✅ Validator 完成：通过 ${VALIDATED_COUNT} 条"
else
    VALIDATED_COUNT=0
fi

if docker exec ${CONTAINER} test -f ${BLACKBOARD_DIR}/Rejected_Evidence.json 2>/dev/null; then
    REJECTED_COUNT=$(docker exec ${CONTAINER} runuser -u node -- sh -c "cat ${BLACKBOARD_DIR}/Rejected_Evidence.json" | python3 -c "import json, sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo "❌ Validator 完成：拒绝 ${REJECTED_COUNT} 条"
else
    REJECTED_COUNT=0
fi
echo ""

# 5. Step 4: Deduplicator - 去重和简报
echo "[Step 4] Deduplicator - 去重和简报生成..."
echo ""

docker exec ${CONTAINER} runuser -u node -- sh -c "
    cd /app && node openclaw.mjs agent --agent deduplicator \
    --message '请从黑板 [Validated_Assets] 读取所有资产，执行跨语言去重，生成高管级 Markdown 简报。' \
    --local
" 2>&1 | tee e2e_deduplicator_output.log

echo ""

# 6. 测试结果总结
echo "=========================================="
echo "端到端测试结果总结"
echo "=========================================="
echo ""
echo "数据流:"
echo "  Coach → Pending_Tasks: ${TASK_COUNT:-0} 条"
echo "  Investigator → Raw_Evidence: 5 条（模拟）"
echo "  Validator → Validated: ${VALIDATED_COUNT:-0} 条"
echo "  Validator → Rejected: ${REJECTED_COUNT:-0} 条"
echo "  Deduplicator → Markdown: $(grep -q '# LINGNEXUS' e2e_deduplicator_output.log 2>/dev/null && echo '✅' || echo '❌')"
echo ""

if [ "${VALIDATED_COUNT:-0}" -gt "0" ] && grep -q "# LINGNEXUS" e2e_deduplicator_output.log 2>/dev/null; then
    echo "✅ 端到端测试通过！"
    echo ""
    echo "--- 最终 Markdown 简报 ---"
    grep -A 100 "# LINGNEXUS" e2e_deduplicator_output.log | head -80
else
    echo "⚠️  测试未完全通过"
fi
