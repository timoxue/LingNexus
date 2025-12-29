# 使用 uv 快速设置项目 (PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "LingNexus 项目设置" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 uv 是否安装
try {
    $uvVersion = uv --version 2>&1
    Write-Host "✅ 检测到 uv: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 未找到 uv" -ForegroundColor Red
    Write-Host "   正在安装 uv..." -ForegroundColor Yellow
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    Write-Host "✅ uv 已安装" -ForegroundColor Green
    Write-Host "   请重新运行此脚本" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 同步依赖
Write-Host "📦 正在安装依赖..." -ForegroundColor Yellow
uv sync

Write-Host ""
Write-Host "✅ 依赖安装完成" -ForegroundColor Green
Write-Host ""

# 加载 Skills
Write-Host "🔍 正在加载 Skills..." -ForegroundColor Yellow
python scripts/load_claude_skills.py --generate-only

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ 项目设置完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步：" -ForegroundColor Yellow
Write-Host "  1. 运行 'uv run python scripts/load_claude_skills.py' 来注册 Skills"
Write-Host "  2. 查看 README.md 了解如何使用"
Write-Host ""

