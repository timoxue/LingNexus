# LINGNEXUS — 一键启动脚本 (PowerShell)
# 使用方式：在项目根目录执行  .\scripts\Start-LingNexus.ps1

param(
    [switch]$Reset,        # 清除所有状态并重新初始化
    [switch]$SetupOnly,    # 只执行 Agent 注册，不启动 Gateway
    [switch]$Logs          # 启动后持续跟踪日志
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

function Write-Step($msg) { Write-Host "`n▶ $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  ⚠ $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "  ✗ $msg" -ForegroundColor Red }

# ── 0. 前置检查 ───────────────────────────────────────────────
Write-Step "Pre-flight checks"

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Warn ".env not found — copied from .env.example"
        Write-Warn "请编辑 .env 并填入你的 ANTHROPIC_API_KEY，然后重新运行此脚本"
        exit 1
    }
}

$envContent = Get-Content ".env" -Raw
if ($envContent -match "ANTHROPIC_API_KEY=sk-ant-api03-xxx") {
    Write-Err "请先在 .env 文件中填入真实的 ANTHROPIC_API_KEY"
    exit 1
}
Write-OK ".env loaded"

docker info > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Err "Docker is not running. 请先启动 Docker Desktop"
    exit 1
}
Write-OK "Docker is running"

# ── 1. 清理（可选）───────────────────────────────────────────
if ($Reset) {
    Write-Step "Resetting state (--Reset flag detected)"
    docker compose down -v --remove-orphans 2>/dev/null
    Write-OK "State volume cleared"
}

# ── 2. Agent 注册（首次或 Reset 后）──────────────────────────
Write-Step "Running agent registration (setup profile)"
docker compose --profile setup run --rm setup
if ($LASTEXITCODE -ne 0) {
    Write-Err "Agent registration failed"
    exit 1
}
Write-OK "All 5 agents registered"

if ($SetupOnly) {
    Write-OK "Setup complete (--SetupOnly). Gateway not started."
    exit 0
}

# ── 3. 启动 Gateway ───────────────────────────────────────────
Write-Step "Starting LINGNEXUS Gateway"
docker compose up gateway -d
if ($LASTEXITCODE -ne 0) {
    Write-Err "Failed to start gateway"
    exit 1
}

# ── 4. 等待健康检查 ───────────────────────────────────────────
Write-Step "Waiting for gateway to become healthy..."
$maxWait = 30
$waited  = 0
do {
    Start-Sleep -Seconds 2
    $waited += 2
    $health = docker inspect lingnexus-gateway --format '{{.State.Health.Status}}' 2>/dev/null
} while ($health -ne "healthy" -and $waited -lt $maxWait)

if ($health -eq "healthy") {
    Write-OK "Gateway is healthy at http://localhost:18789"
} else {
    Write-Warn "Gateway health check timed out (status: $health) — check logs below"
}

# ── 5. 打印状态摘要 ───────────────────────────────────────────
Write-Host "`n══════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host " LINGNEXUS is running!" -ForegroundColor Magenta
Write-Host "══════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host " Gateway:   http://localhost:18789"
Write-Host " Healthz:   http://localhost:18789/healthz"
Write-Host " Logs:      docker compose logs -f gateway"
Write-Host " Stop:      docker compose down"
Write-Host "══════════════════════════════════════════════`n" -ForegroundColor Magenta

if ($Logs) {
    docker compose logs -f gateway
}
