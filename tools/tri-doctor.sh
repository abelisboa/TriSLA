#!/usr/bin/env bash
# ======================================================
# TriSLA Doctor — Diagnóstico Estático e Operacional
# ======================================================
set -euo pipefail

CHART_DIR="./helm/trisla-portal"
VALUES_FILE="./docs/config-examples/values-nasp.yaml"
NAMESPACE="trisla"

echo ""
echo "TriSLA Doctor — análise estática dos artefatos (sem alterações)"
echo ""

# ------------------------------------------------------
# 1️⃣ Verificação de arquivos essenciais
# ------------------------------------------------------
essential_files=(
  "$CHART_DIR/templates/service.yaml"
  "$CHART_DIR/templates/deployment.yaml"
  "$VALUES_FILE"
  "./apps/api/main.py"
  "./apps/api/Dockerfile"
  "./apps/ui/Dockerfile"
)

for file in "${essential_files[@]}"; do
  if [[ -f "$file" ]]; then
    echo "✅ Arquivo presente: $file"
  else
    echo "❌ Arquivo ausente: $file"
  fi
done
echo ""

# ------------------------------------------------------
# 2️⃣ Lint e validação Helm
# ------------------------------------------------------
echo "2) Lint e renderização Helm"
if helm lint "$CHART_DIR" >/dev/null 2>&1; then
  echo "✅ Helm lint sem erros"
else
  echo "❌ Helm lint falhou — verifique templates"
fi

if helm template trisla-portal "$CHART_DIR" -f "$VALUES_FILE" >/dev/null 2>&1; then
  echo "✅ Renderização Helm OK"
else
  echo "❌ Erro ao renderizar chart com $VALUES_FILE"
fi
echo ""

# ------------------------------------------------------
# 3️⃣ Checagem de coerência values-nasp.yaml
# ------------------------------------------------------
echo "3) Coerência de values-nasp.yaml"
grep -q "8000" "$VALUES_FILE" && echo "✅ Backend.port = 8000" || echo "⚠️  backend.service.port não definido corretamente"
grep -q "5173" "$VALUES_FILE" && echo "✅ Frontend.port = 5173" || echo "⚠️  frontend.service.port diferente de 5173"
grep -q "ghcr-creds" "$VALUES_FILE" && echo "✅ imagePullSecrets encontrado" || echo "⚠️  imagePullSecrets ausente"
echo ""

# ------------------------------------------------------
# 4️⃣ Checagem de rota health em apps/api/main.py
# ------------------------------------------------------
echo "4) Verificando rota /api/v1/health"
if grep -q "/api/v1/health" ./apps/api/main.py; then
  echo "✅ Rota /api/v1/health detectada"
else
  echo "❌ Rota /api/v1/health ausente"
fi
echo ""

# ------------------------------------------------------
# 5️⃣ Estado do cluster (opcional)
# ------------------------------------------------------
if command -v kubectl >/dev/null 2>&1; then
  echo "5) Estado atual do cluster ($NAMESPACE)"
  kubectl get pods -n "$NAMESPACE" -o wide 2>/dev/null || echo "⚠️  Nenhum pod encontrado"
  kubectl get svc -n "$NAMESPACE" 2>/dev/null || true
else
  echo "⚠️  kubectl não encontrado — pulando checagem de cluster"
fi
echo ""

echo "Fim do diagnóstico. Itens com ❌/⚠️ devem ser revisados."
echo ""
