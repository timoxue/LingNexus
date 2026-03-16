#!/bin/bash
# LINGNEXUS 完整工作流测试脚本
# 手动编排 main → coach → investigator → validator → deduplicator

set -e

QUERY="请帮我挖掘全球PROTAC靶向降解剂的最新专利，重点关注BRD4靶点，2024年以来的临床早期项目"
WORKSPACE="/workspace"
CLI="node /app/openclaw.mjs"

echo "=========================================="
echo " LINGNEXUS 完整工作流测试"
echo "=========================================="
echo ""
echo "查询: $QUERY"
echo ""

# ── Step 1: Main Agent 接收查询 ──────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Main Agent - 接收用户查询"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

MAIN_OUTPUT=$(docker exec lingnexus-gateway bash -c "cd $WORKSPACE && $CLI agent --agent main --local -m '$QUERY'" 2>&1 | tail -10)
echo "$MAIN_OUTPUT"
echo ""

# ── Step 2: Coach Agent 拆解查询 ──────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Coach Agent - 查询拆解"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

COACH_PROMPT="请将以下查询拆解为5条多语种搜索任务（输出JSON格式）：$QUERY"
COACH_OUTPUT=$(docker exec lingnexus-gateway bash -c "cd $WORKSPACE && $CLI agent --agent coach --local -m '$COACH_PROMPT'" 2>&1)

echo "$COACH_OUTPUT" | tail -50
echo ""

# 保存 coach 输出
mkdir -p ./test-workflow
echo "$COACH_OUTPUT" > ./test-workflow/01-coach-output.txt
echo "  ✓ Coach 输出已保存到 ./test-workflow/01-coach-output.txt"
echo ""

# ── Step 3: Investigator Agent 数据采集 ──────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Investigator Agent - 数据采集"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

INV_PROMPT="请基于以下搜索任务采集原始证据（生成2-3条模拟数据，JSON格式）：
T1: 英文全球库 - PROTAC BRD4 2024年专利
T2: 中国药智网 - PROTAC 靶向降解 BRD4"

INV_OUTPUT=$(docker exec lingnexus-gateway bash -c "cd $WORKSPACE && $CLI agent --agent investigator --local -m '$INV_PROMPT'" 2>&1)

echo "$INV_OUTPUT" | tail -50
echo ""

# 保存 investigator 输出
echo "$INV_OUTPUT" > ./test-workflow/02-investigator-output.txt
echo "  ✓ Investigator 输出已保存到 ./test-workflow/02-investigator-output.txt"
echo ""

# ── Step 4: Validator Agent 质量校验 ──────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Validator Agent - 质量校验"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

VAL_PROMPT="请验证以下证据（输出JSON格式）：
证据ID: E001
来源: Google Patents US20240123456
内容: PROTAC BRD4 Degrader, Arvinas Inc. (US), 2024-02-10, Phase I clinical trial for cancer treatment
请按4条硬性规则校验并输出验证结果。"

VAL_OUTPUT=$(docker exec lingnexus-gateway bash -c "cd $WORKSPACE && $CLI agent --agent validator --local -m '$VAL_PROMPT'" 2>&1)

echo "$VAL_OUTPUT" | tail -50
echo ""

# 保存 validator 输出
echo "$VAL_OUTPUT" > ./test-workflow/03-validator-output.txt
echo "  ✓ Validator 输出已保存到 ./test-workflow/03-validator-output.txt"
echo ""

# ── Step 5: Deduplicator Agent 生成简报 ──────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Deduplicator Agent - 生成简报"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

DEDUP_PROMPT="请基于以下通过验证的资产生成Markdown简报：
1. ARV-825 (Arvinas Inc., US) - PROTAC, BRD4, Phase I
2. 未命名化合物 (中国科学院, CN) - PROTAC, BRD4, Pre-Clinical
请执行跨语种去重并生成高管级简报。"

DEDUP_OUTPUT=$(docker exec lingnexus-gateway bash -c "cd $WORKSPACE && $CLI agent --agent deduplicator --local -m '$DEDUP_PROMPT'" 2>&1)

echo "$DEDUP_OUTPUT" | tail -100
echo ""

# 保存 deduplicator 输出
echo "$DEDUP_OUTPUT" > ./test-workflow/04-deduplicator-output.txt
echo "  ✓ Deduplicator 输出已保存到 ./test-workflow/04-deduplicator-output.txt"
echo ""

# ── 提取最终简报 ──────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "最终简报"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 尝试提取 Markdown 内容
if echo "$DEDUP_OUTPUT" | grep -q "^#"; then
    echo "$DEDUP_OUTPUT" | sed -n '/^#/,$p' > ./test-workflow/FINAL_REPORT.md
    echo "  ✓ 最终简报已保存到 ./test-workflow/FINAL_REPORT.md"
    echo ""
    cat ./test-workflow/FINAL_REPORT.md
else
    echo "  ⚠ 未找到 Markdown 格式的简报"
fi

echo ""
echo "=========================================="
echo " ✅ 完整工作流测试完成"
echo "=========================================="
echo ""
echo "所有输出已保存到 ./test-workflow/ 目录"
echo ""
