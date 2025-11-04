# Build isolado do Dashboard
Write-Host "🚀 Building TriSLA Dashboard v3.2.4..." -ForegroundColor Green

docker build -t ghcr.io/abelisboa/trisla-dashboard-frontend:3.2.4 ./apps/dashboard/frontend
docker build -t ghcr.io/abelisboa/trisla-dashboard-backend:latest ./apps/dashboard/backend

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dashboard images built successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}


