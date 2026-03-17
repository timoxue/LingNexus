#!/bin/bash
# Test Investigator concurrent execution with sessions_spawn
# 测试 Investigator 使用 sessions_spawn 的并发执行能力

set -e

echo "=========================================="
echo "Investigator Concurrent Execution Test"
echo "=========================================="
echo ""

# Step 1: Prepare test data with 3 tasks
echo "Step 1: Preparing test data with 3 concurrent tasks..."
cat > /tmp/test-concurrent-tasks.json << 'EOF'
[
  {
    "task_id": "T1",
    "search_query": "PROTAC BRD4",
    "language": "en",
    "region": "GLOBAL",
    "target_source": "pubmed",
    "status": "pending"
  },
  {
    "task_id": "T2",
    "search_query": "靶向蛋白降解",
    "language": "zh",
    "region": "CN",
    "target_source": "pubmed",
    "status": "pending"
  },
  {
    "task_id": "T3",
    "search_query": "Molecular Glue degrader",
    "language": "en",
    "region": "US",
    "target_source": "pubmed",
    "status": "pending"
  }
]
EOF

# Step 2: Copy to container blackboard
echo "Step 2: Copying tasks to container blackboard..."
docker exec lingnexus-gateway runuser -u node -- sh -c \
  "mkdir -p /workspace/blackboard && cat > /workspace/blackboard/Pending_Tasks.json" \
  < /tmp/test-concurrent-tasks.json

echo "✓ Tasks written to /workspace/blackboard/Pending_Tasks.json"
echo ""

# Step 3: Clear previous evidence
echo "Step 3: Clearing previous evidence..."
docker exec lingnexus-gateway runuser -u node -- sh -c \
  "echo '[]' > /workspace/blackboard/Raw_Evidence.json"
echo "✓ Raw_Evidence cleared"
echo ""

# Step 4: Execute Investigator with concurrent tasks
echo "Step 4: Executing Investigator (concurrent mode)..."
echo "Expected: 3 tasks execute in parallel using sessions_spawn"
echo ""

START_TIME=$(date +%s)

docker exec lingnexus-gateway runuser -u node -- sh -c \
  "cd /app && node openclaw.mjs agent --agent investigator \
   --message '读取 /workspace/blackboard/Pending_Tasks.json 中的所有 pending 任务，使用 sessions_spawn 并发执行所有搜索任务' \
   --local" 2>&1 | tee /tmp/investigator-concurrent-output.txt

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "✓ Execution completed in ${DURATION} seconds"
echo ""

# Step 5: Verify results
echo "Step 5: Verifying results..."
echo ""

# Check Raw_Evidence
docker exec lingnexus-gateway runuser -u node -- sh -c \
  "cat /workspace/blackboard/Raw_Evidence.json" > /tmp/raw-evidence-result.json

EVIDENCE_COUNT=$(python3 -c "import json; data=json.load(open('/tmp/raw-evidence-result.json')); print(len(data))")

echo "Evidence count: ${EVIDENCE_COUNT}"

if [ "$EVIDENCE_COUNT" -gt 0 ]; then
  echo "✓ Evidence collected successfully"

  # Show sample evidence
  echo ""
  echo "Sample evidence (first item):"
  python3 -c "
import json
data = json.load(open('/tmp/raw-evidence-result.json'))
if data:
    print(json.dumps(data[0], indent=2, ensure_ascii=False))
"
else
  echo "✗ No evidence collected"
  exit 1
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Tasks executed: 3"
echo "Evidence collected: ${EVIDENCE_COUNT}"
echo "Execution time: ${DURATION}s"
echo "Expected time (sequential): ~15s"
echo "Expected time (concurrent): ~5s"
echo ""

if [ "$DURATION" -lt 10 ]; then
  echo "✓ Performance: EXCELLENT (concurrent execution confirmed)"
elif [ "$DURATION" -lt 15 ]; then
  echo "⚠ Performance: GOOD (some parallelism achieved)"
else
  echo "✗ Performance: POOR (likely sequential execution)"
fi

echo ""
echo "Test completed!"
