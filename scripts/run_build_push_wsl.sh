#!/bin/bash
set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  TriSLA - Build e Push GHCR v3.7.7 (WSL corrigido)         ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo ""
echo "🟦 FASE 1 — Docker login..."
echo "$GHCR_TOKEN" | docker login ghcr.io -u abelisboa --password-stdin

echo ""
echo "🟦 FASE 2 — Iniciando PowerShell com GHCR_TOKEN..."

powershell.exe -ExecutionPolicy Bypass -Command "& {
    Write-Host 'GHCR_TOKEN criado no PowerShell:';
    \$env:GHCR_TOKEN='$GHCR_TOKEN';
    Write-Host \$env:GHCR_TOKEN;
    Write-Host '';
    Write-Host '➡️ Executando validate_and_build_ghcr_v3.7.7.ps1';
    ./scripts/validate_and_build_ghcr_v3.7.7.ps1
}"




