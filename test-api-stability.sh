#!/bin/bash
# API 稳定性测试脚本

API_KEY="cr_9be340f655675c834ddaa9eccecb876e8c573a12822d65d285ef5a2a48122666"
PROXY_URL="http://localhost:18790"
TEST_ROUNDS=5

echo "=========================================="
echo " Claude Code API 稳定性测试"
echo "=========================================="
echo ""
echo "代理地址: $PROXY_URL"
echo "测试轮数: $TEST_ROUNDS"
echo ""

# 测试 1: 模型列表 API
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "测试 1: 模型列表 API (/v1/models)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success_count=0
total_time=0

for i in $(seq 1 $TEST_ROUNDS); do
    echo -n "  轮次 $i: "

    response=$(curl -s -w "\n%{http_code}\n%{time_total}" \
        "$PROXY_URL/v1/models" \
        -H "x-api-key: $API_KEY" \
        --max-time 10 2>&1)

    http_code=$(echo "$response" | tail -2 | head -1)
    time_total=$(echo "$response" | tail -1)

    if [ "$http_code" = "200" ]; then
        echo "✅ 成功 (${time_total}s)"
        success_count=$((success_count + 1))
        total_time=$(echo "$total_time + $time_total" | bc)
    else
        echo "❌ 失败 (HTTP $http_code)"
    fi

    sleep 0.5
done

echo ""
echo "  结果: $success_count/$TEST_ROUNDS 成功"
if [ $success_count -gt 0 ]; then
    avg_time=$(echo "scale=3; $total_time / $success_count" | bc)
    echo "  平均响应时间: ${avg_time}s"
fi
echo ""

# 测试 2: 消息 API (简单请求)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "测试 2: 消息 API (/v1/messages)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success_count=0
total_time=0

for i in $(seq 1 $TEST_ROUNDS); do
    echo -n "  轮次 $i: "

    payload=$(cat <<'EOF'
{
  "model": "claude-haiku-4-5-20251001",
  "max_tokens": 100,
  "messages": [
    {
      "role": "user",
      "content": "请用一句话回复：你是谁？"
    }
  ]
}
EOF
)

    response=$(curl -s -w "\n%{http_code}\n%{time_total}" \
        "$PROXY_URL/v1/messages" \
        -H "x-api-key: $API_KEY" \
        -H "Content-Type: application/json" \
        -H "anthropic-version: 2023-06-01" \
        -d "$payload" \
        --max-time 30 2>&1)

    http_code=$(echo "$response" | tail -2 | head -1)
    time_total=$(echo "$response" | tail -1)

    if [ "$http_code" = "200" ]; then
        # 提取响应内容
        content=$(echo "$response" | head -n -2 | jq -r '.content[0].text' 2>/dev/null || echo "")
        echo "✅ 成功 (${time_total}s)"
        if [ -n "$content" ]; then
            echo "     回复: $content"
        fi
        success_count=$((success_count + 1))
        total_time=$(echo "$total_time + $time_total" | bc)
    else
        echo "❌ 失败 (HTTP $http_code)"
        # 显示错误信息
        error_msg=$(echo "$response" | head -n -2 | jq -r '.error.message' 2>/dev/null || echo "")
        if [ -n "$error_msg" ]; then
            echo "     错误: $error_msg"
        fi
    fi

    sleep 1
done

echo ""
echo "  结果: $success_count/$TEST_ROUNDS 成功"
if [ $success_count -gt 0 ]; then
    avg_time=$(echo "scale=3; $total_time / $success_count" | bc)
    echo "  平均响应时间: ${avg_time}s"
fi
echo ""

# 测试 3: 流式响应
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "测试 3: 流式响应 API (stream=true)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success_count=0

for i in $(seq 1 3); do
    echo -n "  轮次 $i: "

    payload=$(cat <<'EOF'
{
  "model": "claude-haiku-4-5-20251001",
  "max_tokens": 50,
  "stream": true,
  "messages": [
    {
      "role": "user",
      "content": "数到5"
    }
  ]
}
EOF
)

    start_time=$(date +%s.%N)
    response=$(curl -s -w "\n%{http_code}" \
        "$PROXY_URL/v1/messages" \
        -H "x-api-key: $API_KEY" \
        -H "Content-Type: application/json" \
        -H "anthropic-version: 2023-06-01" \
        -d "$payload" \
        --max-time 30 2>&1)
    end_time=$(date +%s.%N)

    http_code=$(echo "$response" | tail -1)
    time_total=$(echo "$end_time - $start_time" | bc)

    if [ "$http_code" = "200" ]; then
        echo "✅ 成功 (${time_total}s)"
        success_count=$((success_count + 1))
    else
        echo "❌ 失败 (HTTP $http_code)"
    fi

    sleep 1
done

echo ""
echo "  结果: $success_count/3 成功"
echo ""

echo "=========================================="
echo " 测试完成"
echo "=========================================="
