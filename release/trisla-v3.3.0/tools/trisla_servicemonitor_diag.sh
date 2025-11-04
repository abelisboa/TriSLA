#!/bin/bash
# ======================================================================
# 🔎 TriSLA ServiceMonitor Diagnostic Tool (v3.5)
# Autor: Abel Lisboa / GPT-5
# Data: $(date)
# ----------------------------------------------------------------------
# Objetivo:
#  - Detectar resíduos de ServiceMonitor do TriSLA Portal em QUALQUER namespace.
#  - Identificar duplicidades, inconsistências de schema e CRDs corrompidos.
#  - Gerar relatório diagnóstico completo.
# ======================================================================

echo "🚀 Iniciando varredura diagnóstica do ServiceMonitor TriSLA..."
echo "------------------------------------------------------------------"
sleep 1

# Etapa 1: Checagem de CRDs do Prometheus Operator
echo "🔍 [1/5] Verificando CRDs do Prometheus Operator..."
kubectl get crd | grep monitoring.coreos.com | awk '{print "  - "$1}' || echo "❌ Nenhum CRD encontrado!"
echo "------------------------------------------------------------------"

# Etapa 2: Buscar ServiceMonitors residuais
echo "🔍 [2/5] Buscando objetos ServiceMonitor relacionados ao TriSLA..."
matches=$(kubectl get servicemonitor -A 2>/dev/null | grep -i trisla || true)
if [ -z "$matches" ]; then
  echo "✅ Nenhum ServiceMonitor TriSLA encontrado em namespaces conhecidos."
else
  echo "⚠️ ServiceMonitor(s) encontrados:"
  echo "$matches"
fi
echo "------------------------------------------------------------------"

# Etapa 3: Buscar objetos travados no etcd (órfãos / CRD conflitantes)
echo "🔍 [3/5] Checando CRDs residuais diretos (via API resources)..."
kubectl api-resources --verbs=list --namespaced -o name | grep servicemonitor >/dev/null && \
  echo "✅ APIResource ServiceMonitor ativo." || echo "⚠️ APIResource ServiceMonitor ausente."
echo "------------------------------------------------------------------"

# Etapa 4: Verificação estrutural dos manifests (schema & campos desconhecidos)
echo "🔍 [4/5] Validando schema e campos do ServiceMonitor..."
crd_yaml=$(kubectl get crd servicemonitors.monitoring.coreos.com -o yaml 2>/dev/null)
if echo "$crd_yaml" | grep -q "openAPIV3Schema"; then
  if echo "$crd_yaml" | grep -q "namespaceSelector"; then
    echo "✅ Schema contém 'namespaceSelector' (válido)."
  else
    echo "⚠️ Campo 'namespaceSelector' ausente — pode causar warnings."
  fi
else
  echo "❌ CRD ServiceMonitor está corrompido ou incompleto."
fi
echo "------------------------------------------------------------------"

# Etapa 5: Diagnóstico final
echo "�� [5/5] Diagnóstico consolidado:"
if [ -z "$matches" ]; then
  echo "🟢 Nenhum conflito detectado. Ambiente pronto para Helm."
else
  echo "🔴 Conflitos detectados:"
  echo "$matches"
  echo ""
  echo "Para limpar manualmente:"
  echo "  kubectl delete servicemonitor <nome> -n <namespace> --ignore-not-found"
fi
echo "------------------------------------------------------------------"

# Relatório rápido de inconsistência temporal
echo "⏱️ Verificando timestamps de CRD:"
kubectl get crd servicemonitors.monitoring.coreos.com -o jsonpath='{.metadata.creationTimestamp}' 2>/dev/null || echo "Sem timestamp."
echo
echo "✅ Diagnóstico TriSLA-Diag v3.5 concluído."
