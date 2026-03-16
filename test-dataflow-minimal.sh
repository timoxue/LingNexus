#!/bin/bash
# LINGNEXUS 最小化数据流测试
# 手动模拟黑板数据在各个智能体之间的流动

set -e

echo "=========================================="
echo " LINGNEXUS 最小化数据流测试"
echo "=========================================="
echo ""

# 创建临时黑板目录
BLACKBOARD_DIR="./.openclaw/blackboard-test"
mkdir -p "$BLACKBOARD_DIR"

# ── Step 1: 模拟 coach 输出 (Pending_Tasks) ──
echo "Step 1: 模拟 coach 生成 Pending_Tasks..."
cat > "$BLACKBOARD_DIR/Pending_Tasks.json" <<'EOF'
[
  {
    "task_id": "T1",
    "language": "en",
    "region": "GLOBAL",
    "target_source": "Google Patents",
    "search_query": "PROTAC AND (BRD4 OR AR) AND (2024 OR 2025)",
    "priority": 1,
    "status": "pending"
  },
  {
    "task_id": "T2",
    "language": "zh",
    "region": "CN",
    "target_source": "药智网",
    "search_query": "PROTAC 靶向降解 BRD4",
    "priority": 2,
    "status": "pending"
  }
]
EOF
echo "  ✓ 已写入 2 条搜索任务到 Pending_Tasks"
echo ""

# ── Step 2: 模拟 investigator 输出 (Raw_Evidence) ──
echo "Step 2: 模拟 investigator 采集 Raw_Evidence..."
cat > "$BLACKBOARD_DIR/Raw_Evidence.json" <<'EOF'
[
  {
    "evidence_id": "E001",
    "source_task_id": "T1",
    "language": "en",
    "region": "US",
    "source_url": "https://patents.google.com/patent/US20240123456",
    "source_name": "Google Patents",
    "raw_text": "A novel PROTAC compound targeting BRD4 protein for degradation. Patent filed by Arvinas Inc. (US) in January 2024. The compound ARV-825 is currently in Phase I clinical trials for treatment of solid tumors. The PROTAC molecule consists of a BRD4 ligand conjugated to an E3 ligase recruiter.",
    "crawled_at": "2026-03-16T10:00:00Z",
    "status": "pending_validation"
  },
  {
    "evidence_id": "E002",
    "source_task_id": "T2",
    "language": "zh",
    "region": "CN",
    "source_url": "https://www.yaozh.com/patent/CN202410001234",
    "source_name": "药智网",
    "raw_text": "一种靶向BRD4的PROTAC分子，由中国科学院上海药物所研发，专利申请号CN202410001234，申请日期2024年3月。该化合物目前处于临床前研究阶段，显示出良好的体外降解活性。",
    "crawled_at": "2026-03-16T10:01:00Z",
    "status": "pending_validation"
  },
  {
    "evidence_id": "E003",
    "source_task_id": "T1",
    "language": "en",
    "region": "JP",
    "source_url": "https://example.com/old-patent",
    "source_name": "J-PlatPat",
    "raw_text": "PROTAC compound for BRD4 degradation, filed in 2019. This is an old patent that should be rejected by validator due to date range.",
    "crawled_at": "2026-03-16T10:02:00Z",
    "status": "pending_validation"
  }
]
EOF
echo "  ✓ 已写入 3 条原始证据到 Raw_Evidence (包含1条应被拒绝的旧专利)"
echo ""

# ── Step 3: 模拟 validator 输出 (Validated_Assets + Rejected_Evidence) ──
echo "Step 3: 模拟 validator 执行质检..."
cat > "$BLACKBOARD_DIR/Validated_Assets.json" <<'EOF'
[
  {
    "validation_id": "V20260316_E001",
    "source_evidence_id": "E001",
    "is_met": true,
    "origin_country": "US",
    "entity_name": "Arvinas Inc.",
    "drug_candidate": "ARV-825",
    "target": "BRD4",
    "degrader_modality": "PROTAC",
    "clinical_stage": "Phase I",
    "patent_id": "US20240123456",
    "evidence_quote": "A novel PROTAC compound targeting BRD4 protein for degradation. Patent filed by Arvinas Inc. (US) in January 2024. The compound ARV-825 is currently in Phase I clinical trials",
    "failure_rationale": null,
    "validated_at": "2026-03-16T10:10:00Z"
  },
  {
    "validation_id": "V20260316_E002",
    "source_evidence_id": "E002",
    "is_met": true,
    "origin_country": "CN",
    "entity_name": "中国科学院上海药物所",
    "drug_candidate": "未命名",
    "target": "BRD4",
    "degrader_modality": "PROTAC",
    "clinical_stage": "Pre-Clinical",
    "patent_id": "CN202410001234",
    "evidence_quote": "一种靶向BRD4的PROTAC分子，由中国科学院上海药物所研发，专利申请号CN202410001234，申请日期2024年3月。该化合物目前处于临床前研究阶段",
    "failure_rationale": null,
    "validated_at": "2026-03-16T10:11:00Z"
  }
]
EOF

cat > "$BLACKBOARD_DIR/Rejected_Evidence.json" <<'EOF'
[
  {
    "validation_id": "V20260316_E003",
    "source_evidence_id": "E003",
    "is_met": false,
    "failure_rationale": "[时间范围] 专利申请日期为2019年，不在2023-2026范围内",
    "evidence_quote": "PROTAC compound for BRD4 degradation, filed in 2019",
    "rejected_at": "2026-03-16T10:12:00Z"
  }
]
EOF
echo "  ✓ 已写入 2 条通过验证的资产到 Validated_Assets"
echo "  ✓ 已写入 1 条被拒绝的证据到 Rejected_Evidence"
echo ""

# ── Step 4: 模拟 deduplicator 输出 (Markdown 简报) ──
echo "Step 4: 模拟 deduplicator 生成最终简报..."
cat > "$BLACKBOARD_DIR/Final_Report.md" <<'EOF'
# 全球 PROTAC 靶向降解剂专利情报简报

**生成时间**: 2026-03-16 10:15:00
**查询范围**: BRD4 靶点 PROTAC 分子，2024年以来临床早期项目
**数据来源**: 全球专利库（美国、中国、日本）

---

## 执行摘要

本次扫描共采集 **3 条原始证据**，经质检后通过 **2 条**，拒绝 **1 条**（时间范围不符）。

---

## 通过验证的项目

### 1. ARV-825 (Arvinas Inc., 美国)

- **研发主体**: Arvinas Inc. (US)
- **候选药物**: ARV-825
- **靶点**: BRD4
- **技术类型**: PROTAC
- **临床阶段**: Phase I
- **专利号**: US20240123456
- **申请时间**: 2024年1月

**关键证据**:
> A novel PROTAC compound targeting BRD4 protein for degradation. Patent filed by Arvinas Inc. (US) in January 2024. The compound ARV-825 is currently in Phase I clinical trials

---

### 2. 未命名化合物 (中国科学院上海药物所, 中国)

- **研发主体**: 中国科学院上海药物所 (CN)
- **候选药物**: 未命名
- **靶点**: BRD4
- **技术类型**: PROTAC
- **临床阶段**: Pre-Clinical
- **专利号**: CN202410001234
- **申请时间**: 2024年3月

**关键证据**:
> 一种靶向BRD4的PROTAC分子，由中国科学院上海药物所研发，专利申请号CN202410001234，申请日期2024年3月。该化合物目前处于临床前研究阶段

---

## 被拒绝的证据

| 证据ID | 拒绝原因 | 证据片段 |
|--------|----------|----------|
| E003 | [时间范围] 专利申请日期为2019年，不在2023-2026范围内 | PROTAC compound for BRD4 degradation, filed in 2019 |

---

## 统计数据

- **总采集数**: 3
- **通过验证**: 2 (66.7%)
- **被拒绝**: 1 (33.3%)
- **覆盖国家**: 美国、中国
- **覆盖阶段**: Pre-Clinical (1), Phase I (1)

---

*本简报由 LINGNEXUS 多智能体系统自动生成*
EOF
echo "  ✓ 已生成最终 Markdown 简报到 Final_Report.md"
echo ""

# ── 展示数据流 ──
echo "=========================================="
echo " 数据流验证"
echo "=========================================="
echo ""
echo "📋 Pending_Tasks (coach 输出):"
jq -r '.[] | "  - [\(.task_id)] \(.language) | \(.target_source)"' "$BLACKBOARD_DIR/Pending_Tasks.json"
echo ""

echo "🔍 Raw_Evidence (investigator 输出):"
jq -r '.[] | "  - [\(.evidence_id)] \(.region) | \(.source_name) | status=\(.status)"' "$BLACKBOARD_DIR/Raw_Evidence.json"
echo ""

echo "✅ Validated_Assets (validator 输出 - 通过):"
jq -r '.[] | "  - [\(.validation_id)] \(.origin_country) | \(.entity_name) | \(.drug_candidate) | \(.clinical_stage)"' "$BLACKBOARD_DIR/Validated_Assets.json"
echo ""

echo "❌ Rejected_Evidence (validator 输出 - 拒绝):"
jq -r '.[] | "  - [\(.validation_id)] \(.failure_rationale)"' "$BLACKBOARD_DIR/Rejected_Evidence.json"
echo ""

echo "📄 Final_Report (deduplicator 输出):"
echo "  文件: $BLACKBOARD_DIR/Final_Report.md"
echo "  大小: $(wc -c < "$BLACKBOARD_DIR/Final_Report.md") bytes"
echo ""

echo "=========================================="
echo " ✅ 数据流测试完成"
echo "=========================================="
echo ""
echo "查看完整简报:"
echo "  cat $BLACKBOARD_DIR/Final_Report.md"
echo ""
echo "查看黑板数据:"
echo "  ls -lh $BLACKBOARD_DIR/"
echo ""
