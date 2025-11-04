# Build completo do TriSLA
Write-Host "🚀 Building TriSLA unified stack..." -ForegroundColor Green

docker compose build

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ All TriSLA components built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}


