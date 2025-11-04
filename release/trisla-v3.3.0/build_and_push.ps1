# TriSLA Docker Build and Push Script (PowerShell)
Write-Host "Building and publishing TriSLA Docker images to GHCR..." -ForegroundColor Green

# Login to GHCR
Write-Host "Logging into GHCR..." -ForegroundColor Yellow
docker login ghcr.io -u abelisboa

# Build and push semantic module
Write-Host "Building trisla-semantic..." -ForegroundColor Yellow
docker build -t ghcr.io/abelisboa/trisla-semantic:latest ./apps/semantic
docker push ghcr.io/abelisboa/trisla-semantic:latest

# Build and push AI module
Write-Host "Building trisla-ai..." -ForegroundColor Yellow
docker build -t ghcr.io/abelisboa/trisla-ai:latest ./apps/ai
docker push ghcr.io/abelisboa/trisla-ai:latest

# Build and push blockchain module
Write-Host "Building trisla-blockchain..." -ForegroundColor Yellow
docker build -t ghcr.io/abelisboa/trisla-blockchain:latest ./apps/blockchain
docker push ghcr.io/abelisboa/trisla-blockchain:latest

# Build and push monitoring module
Write-Host "Building trisla-monitoring..." -ForegroundColor Yellow
docker build -t ghcr.io/abelisboa/trisla-monitoring:latest ./apps/monitoring
docker push ghcr.io/abelisboa/trisla-monitoring:latest

Write-Host "All TriSLA images built and published successfully!" -ForegroundColor Green
