# LINGNEXUS — 从当前 Claude Code 会话自动导入 Anthropic 凭证
# 使用方式：在项目根目录执行  .\scripts\Import-ClaudeCodeAuth.ps1

param(
    [switch]$DryRun   # 只打印，不写入 .env
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$EnvFile     = Join-Path $ProjectRoot ".env"

function Write-Step($msg) { Write-Host "`n>> $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "   OK  $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "   WARN $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "   ERR  $msg" -ForegroundColor Red }

# ── Step 1: 从宿主机进程环境读取 Claude Code 凭证 ────────────
Write-Step "Reading Claude Code credentials from current session"

$oauthToken = $env:ANTHROPIC_AUTH_TOKEN
$baseUrl    = $env:ANTHROPIC_BASE_URL

if (-not $oauthToken) {
    Write-Warn "ANTHROPIC_AUTH_TOKEN not in current shell env."
    Write-Warn "Trying Claude Code session-env files..."

    # 扫描 session-env 目录
    $sessionEnvDir = "$HOME\.claude\session-env"
    if (Test-Path $sessionEnvDir) {
        Get-ChildItem $sessionEnvDir -Directory | ForEach-Object {
            $envFile = Join-Path $_.FullName "env"
            if (Test-Path $envFile) {
                $content = Get-Content $envFile -Raw
                if ($content -match 'ANTHROPIC_AUTH_TOKEN=([^\n\r]+)') {
                    $oauthToken = $matches[1].Trim()
                }
                if ($content -match 'ANTHROPIC_BASE_URL=([^\n\r]+)') {
                    $baseUrl = $matches[1].Trim()
                }
            }
        }
    }
}

if (-not $oauthToken) {
    Write-Err "Could not find ANTHROPIC_AUTH_TOKEN."
    Write-Host "   Please add it manually to .env as ANTHROPIC_OAUTH_TOKEN=cr_..." -ForegroundColor Gray
    exit 1
}

if (-not $baseUrl) {
    $baseUrl = "https://claude-code.club/api"
    Write-Warn "ANTHROPIC_BASE_URL not found, using default: $baseUrl"
}

Write-OK "ANTHROPIC_OAUTH_TOKEN found (${oauthToken.Substring(0,[Math]::Min(12,$oauthToken.Length))}...)"
Write-OK "ANTHROPIC_BASE_URL: $baseUrl"

# ── Step 2: 写入 .env ─────────────────────────────────────────
Write-Step "Writing credentials to .env"

if (-not (Test-Path $EnvFile)) {
    Copy-Item (Join-Path $ProjectRoot ".env.example") $EnvFile
    Write-OK "Copied .env.example -> .env"
}

$envContent = Get-Content $EnvFile -Raw

# 替换或追加 ANTHROPIC_OAUTH_TOKEN
if ($envContent -match 'ANTHROPIC_OAUTH_TOKEN=.*') {
    $envContent = $envContent -replace 'ANTHROPIC_OAUTH_TOKEN=.*', "ANTHROPIC_OAUTH_TOKEN=$oauthToken"
} else {
    $envContent += "`nANTHROPIC_OAUTH_TOKEN=$oauthToken"
}

# 替换或追加 ANTHROPIC_BASE_URL
if ($envContent -match 'ANTHROPIC_BASE_URL=.*') {
    $envContent = $envContent -replace 'ANTHROPIC_BASE_URL=.*', "ANTHROPIC_BASE_URL=$baseUrl"
} else {
    $envContent += "`nANTHROPIC_BASE_URL=$baseUrl"
}

if ($DryRun) {
    Write-Warn "[DryRun] Would write to $EnvFile — showing diff only:"
    Write-Host "   ANTHROPIC_OAUTH_TOKEN=$($oauthToken.Substring(0,12))..." -ForegroundColor Gray
    Write-Host "   ANTHROPIC_BASE_URL=$baseUrl" -ForegroundColor Gray
} else {
    $envContent | Set-Content $EnvFile -Encoding utf8 -NoNewline
    Write-OK "Written to $EnvFile"
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Magenta
Write-Host "  1. Fill in MOONSHOT_API_KEY / GOOGLE_API_KEY / OPENROUTER_API_KEY in .env"
Write-Host "  2. docker compose --profile setup run --rm setup"
Write-Host "  3. docker compose up gateway -d"
