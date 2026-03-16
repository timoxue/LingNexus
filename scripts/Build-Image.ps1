# 构建 LingNexus 自定义镜像 (Windows PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "🏗️  开始构建 LingNexus 镜像..." -ForegroundColor Cyan
Write-Host ""

# 检查 openclaw:local 是否存在
try {
    docker image inspect openclaw:local | Out-Null
} catch {
    Write-Host "❌ 错误: 基础镜像 openclaw:local 不存在" -ForegroundColor Red
    Write-Host "请先确保 OpenClaw 镜像已安装" -ForegroundColor Yellow
    exit 1
}

# 构建镜像
Write-Host "正在构建镜像..." -ForegroundColor Yellow
docker build `
    -f Dockerfile.lingnexus `
    -t lingnexus:latest `
    --progress=plain `
    .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 镜像构建失败" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ 镜像构建完成！" -ForegroundColor Green
Write-Host ""

Write-Host "镜像信息:" -ForegroundColor Cyan
docker images lingnexus:latest

Write-Host ""
Write-Host "📦 镜像大小对比:" -ForegroundColor Cyan
Write-Host "基础镜像 (openclaw:local):"
docker images openclaw:local --format "  {{.Size}}"
Write-Host "LingNexus 镜像:"
docker images lingnexus:latest --format "  {{.Size}}"

Write-Host ""
Write-Host "🚀 下一步: 运行 'docker compose up gateway -d' 启动服务" -ForegroundColor Green
