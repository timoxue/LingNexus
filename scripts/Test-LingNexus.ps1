# LINGNEXUS — 功能测试脚本 (PowerShell)
# 使用方式：Gateway 启动后，在项目根目录执行  .\scripts\Test-LingNexus.ps1

param(
    [string]$Query = "请帮我挖掘全球PROTAC靶向降解剂的最新专利，重点关注BRD4和AR靶点，2024年以来的临床早期项目",
    [string]$GatewayUrl = "http://localhost:18789"
)

$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host "`n▶ $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  ⚠ $msg" -ForegroundColor Yellow }

# ── Test 1: Gateway 健康检查 ──────────────────────────────────
Write-Step "Test 1: Gateway Health Check"
try {
    $health = Invoke-RestMethod -Uri "$GatewayUrl/healthz" -Method GET -TimeoutSec 5
    Write-OK "Gateway healthy: $($health | ConvertTo-Json -Compress)"
} catch {
    Write-Host "  ✗ Gateway not reachable at $GatewayUrl" -ForegroundColor Red
    Write-Host "    Run: .\scripts\Start-LingNexus.ps1" -ForegroundColor Yellow
    exit 1
}

# ── Test 2: 通过 Docker exec 验证 Agent 注册 ──────────────────
Write-Step "Test 2: Agent Registry Verification"
$agentList = docker exec lingnexus-gateway node openclaw.mjs agents list --json 2>/dev/null | ConvertFrom-Json
$expectedAgents = @("main", "coach", "investigator", "validator", "deduplicator")
foreach ($agent in $expectedAgents) {
    if ($agentList | Where-Object { $_.name -eq $agent -or $_.id -eq $agent }) {
        Write-OK "Agent '$agent' registered"
    } else {
        Write-Warn "Agent '$agent' NOT found — run setup again"
    }
}

# ── Test 3: 模拟飞书消息触发完整 Pipeline ─────────────────────
Write-Step "Test 3: Simulate Feishu Message → biopharma-scouting Workflow"
Write-Host "  Query: $Query" -ForegroundColor Gray

$payload = @{
    channel  = "feishu"
    agent    = "main"
    message  = $Query
    user_id  = "test_user_ps"
    metadata = @{ test = $true; source = "Start-LingNexus.ps1" }
} | ConvertTo-Json -Depth 3

try {
    $response = Invoke-RestMethod `
        -Uri "$GatewayUrl/api/message" `
        -Method POST `
        -ContentType "application/json" `
        -Body $payload `
        -TimeoutSec 300

    Write-OK "Response received"
    Write-Host "`n══════════════════════════════════════" -ForegroundColor Magenta
    Write-Host " LINGNEXUS Output:" -ForegroundColor Magenta
    Write-Host "══════════════════════════════════════" -ForegroundColor Magenta
    Write-Host $response.message
    Write-Host "══════════════════════════════════════`n" -ForegroundColor Magenta

    # 保存输出到文件
    $outFile = "lingnexus-output-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
    $response.message | Out-File -FilePath $outFile -Encoding utf8
    Write-OK "Output saved to: $outFile"

} catch {
    Write-Warn "API call failed (may need auth token or different endpoint)"
    Write-Host "  Try manual test via docker exec:" -ForegroundColor Gray
    Write-Host "  docker exec lingnexus-gateway node openclaw.mjs agent main --message `"$Query`"" -ForegroundColor Gray
}

# ── Test 4: docker exec 直接调用 Agent（备用）────────────────
Write-Step "Test 4: Direct Agent Call via docker exec (fallback)"
Write-Host "  Sending query directly to 'main' agent..." -ForegroundColor Gray

docker exec lingnexus-gateway `
    node openclaw.mjs agent main `
    --message $Query `
    2>&1 | Select-Object -First 50

Write-Host "`n✅ Test suite complete" -ForegroundColor Green
