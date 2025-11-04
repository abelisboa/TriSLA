# Script para instalar dependências
# Usa cmd.exe para evitar problemas de política de execução

Write-Host "📦 Instalando dependências..." -ForegroundColor Cyan
Write-Host ""

$backendPath = Resolve-Path "$PSScriptRoot\..\backend"
$frontendPath = Resolve-Path "$PSScriptRoot\..\frontend"

# 1. Backend - Criar venv e instalar dependências
Write-Host "1️⃣ Configurando backend..." -ForegroundColor Yellow
Set-Location $backendPath

if (-not (Test-Path "venv")) {
    Write-Host "   Criando venv..." -ForegroundColor Gray
    cmd.exe /c "python -m venv venv"
}

$pythonPath = Join-Path $backendPath "venv\Scripts\python.exe"
if (Test-Path $pythonPath) {
    Write-Host "   Instalando dependências Python..." -ForegroundColor Gray
    cmd.exe /c "`"$pythonPath`" -m pip install --upgrade pip"
    cmd.exe /c "`"$pythonPath`" -m pip install -r requirements.txt"
    Write-Host "   ✅ Backend configurado" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Venv criado, mas python.exe não encontrado" -ForegroundColor Yellow
}
Write-Host ""

# 2. Frontend - Instalar dependências npm
Write-Host "2️⃣ Configurando frontend..." -ForegroundColor Yellow
Set-Location $frontendPath

Write-Host "   Instalando dependências npm..." -ForegroundColor Gray
cmd.exe /c "npm install"
Write-Host "   ✅ Frontend configurado" -ForegroundColor Green
Write-Host ""

Write-Host "✅ Todas as dependências instaladas!" -ForegroundColor Green
Set-Location $backendPath




