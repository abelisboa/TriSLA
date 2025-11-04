# Push controlado para GitHub
Write-Host "🚀 Preparing controlled push to GitHub..." -ForegroundColor Green

if (Test-Path .git) {
    Remove-Item -Recurse -Force .git
}

git init
git remote add origin https://github.com/abelisboa/TriSLA.git
git add .
git commit -m "Initial unified TriSLA release"
git branch -M main
git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ TriSLA repository published successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Push failed" -ForegroundColor Red
    exit 1
}


