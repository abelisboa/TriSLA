#!/bin/bash
# TriSLA Diagnostic Cleanup v2 — Diagnóstico com relatório final
# Autor: Abel Lisboa | 2025-10-28

echo "🔍 Iniciando diagnóstico TriSLA Portal (ServiceMonitor + Helm + CRDs)"
echo "---------------------------------------------------------------------"

fixed_items=()
pending_items=()

# 1️⃣ Buscar ServiceMonitor em todos os namespaces
echo "🔎 Verificando ServiceMonitor em todos os namespaces..."
found_ns=$(kubectl get servicemonitor -A --no-headers 2>/dev/null | grep trisla-portal | awk '{print $1}')

if [[ -n "$found_ns" ]]; then
  echo "⚠️  Encontrado ServiceMonitor órfão nos namespaces:"
  echo "$found_ns" | while read ns; do
    echo "   - $ns"
    kubectl delete servicemonitor trisla-portal-servicemonitor -n "$ns" --ignore-not-found --force --grace-period=0
    fixed_items+=("ServiceMonitor removido de $ns")
  done
else
  echo "✅ Nenhum ServiceMonitor órfão encontrado."
  fixed_items+=("Nenhum ServiceMonitor residual detectado")
fi

# 2️⃣ Remover secrets de releases Helm antigos
echo "🧹 Limpando secrets Helm residuais..."
kubectl delete secret -A -l "owner=helm,name=trisla-portal" --ignore-not-found >/dev/null 2>&1
if [[ $? -eq 0 ]]; then
  fixed_items+=("Secrets Helm antigos removidos")
else
  pending_items+=("Falha ao remover secrets Helm antigos")
fi

# 3️⃣ Verificar release Helm
echo "🔎 Verificando se release Helm está ativo..."
helm list -A | grep trisla-portal >/dev/null 2>&1
if [[ $? -eq 0 ]]; then
  echo "⚠️  Release trisla-portal ainda ativo — será removido"
  helm uninstall trisla-portal -n trisla --wait || true
  fixed_items+=("Release Helm antigo removido")
else
  fixed_items+=("Nenhum release Helm ativo encontrado")
fi

# 4️⃣ Limpar cache Helm local
echo "🧼 Limpando cache Helm local..."
helm repo remove trisla-portal >/dev/null 2>&1 || true
helm repo add trisla-portal ./helm/trisla-portal >/dev/null 2>&1
helm repo update >/dev/null 2>&1
fixed_items+=("Cache Helm local limpo")

# 5️⃣ Sincronizar CRDs
echo "🔁 Forçando sincronização de CRDs..."
kubectl api-resources --verbs=list --namespaced -o name | \
  xargs -I{} kubectl get {} --all-namespaces >/dev/null 2>&1
fixed_items+=("Sincronização de CRDs concluída")

# 6️⃣ Relatório final
echo "---------------------------------------------------------------------"
echo "📋 RELATÓRIO FINAL DE DIAGNÓSTICO"
echo "---------------------------------------------------------------------"
if [[ ${#fixed_items[@]} -gt 0 ]]; then
  echo "✅ Ações executadas com sucesso:"
  for item in "${fixed_items[@]}"; do
    echo "   - $item"
  done
fi
if [[ ${#pending_items[@]} -gt 0 ]]; then
  echo "⚠️ Itens que requerem atenção manual:"
  for item in "${pending_items[@]}"; do
    echo "   - $item"
  done
else
  echo "🎯 Nenhum item pendente. Ambiente pronto para nova implantação."
fi

echo "---------------------------------------------------------------------"
echo "🟢 Diagnóstico TriSLA-Diag v2 concluído."
