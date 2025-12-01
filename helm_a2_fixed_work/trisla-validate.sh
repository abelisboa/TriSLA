#!/bin/bash

###############################################################
# Função para adicionar linhas ao relatório
###############################################################
add() {
  echo "$1" | tee -a /tmp/trisla-validation-report.txt
}

###############################################################
# Cabeçalho
###############################################################
echo "🧹 Limpando relatório anterior..."
rm -f /tmp/trisla-validation-report.txt

add "============================================================"
add "📘 TRI-SLA A2 — Relatório de Validação"
add "Gerado em: $(date)"
add "============================================================"
add ""

NAMESPACE="trisla"

###############################################################
# 1) Verificação do namespace
###############################################################
add "📁 Verificando namespace..."
if kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
  add "✅ Namespace $NAMESPACE existe."
else
  add "❌ Namespace $NAMESPACE não existe!"
  exit 1
fi
add ""

###############################################################
# 2) Estado dos Pods
###############################################################
add "------------------------------------------------------------"
add "📦 Estado dos Pods"
add "------------------------------------------------------------"
kubectl -n $NAMESPACE get pods -o wide | tee -a /tmp/trisla-validation-report.txt
add ""

###############################################################
# 3) Teste de Health check de todos os serviços
###############################################################
add "------------------------------------------------------------"
add "🩺 Teste de Health dos Microserviços"
add "------------------------------------------------------------"

declare -A services=(
  ["ml-nsmf"]=8081
  ["sem-csmf"]=8080
  ["nasp-adapter"]=8085
  ["ui-dashboard"]=80
  ["decision-engine"]=8082
  ["sla-agent-layer"]=8084
  ["bc-nssmf"]=8083
)

for svc in "${!services[@]}"; do
  PORT=${services[$svc]}
  IP=$(kubectl -n $NAMESPACE get svc trisla-$svc -o jsonpath='{.spec.clusterIP}')
  add "🔎 Testando $svc → http://$IP:$PORT/health"

  code=$(curl -s -o /tmp/h.txt -w "%{http_code}" "http://$IP:$PORT/health")

  if [ "$code" = "200" ]; then
    add "✅ $svc responde HEALTH OK (HTTP 200)"
  else
    add "❌ $svc NÃO respondeu corretamente (HTTP $code)"
  fi
done
add ""

###############################################################
# 4) Teste SEM-CSMF (intenção → slice type)
###############################################################
add "------------------------------------------------------------"
add "🧠 Teste funcional: Intenção → TriSLA"
add "------------------------------------------------------------"

SEM_IP=$(kubectl -n $NAMESPACE get svc trisla-sem-csmf -o jsonpath='{.spec.clusterIP}')

add "🚀 Enviando intenção: 'cirurgia remota'"

intent_response=$(curl -s -X POST "http://$SEM_IP:8080/semantic/intention" \
  -H "Content-Type: application/json" \
  -d '{"intent":"cirurgia remota"}')

add "Resposta do SEM-CSMF:"
add "$intent_response"
add ""

###############################################################
# 5) Teste Decision Engine (pipeline interno)
###############################################################
add "------------------------------------------------------------"
add "🔗 Teste do fluxo interno (pipeline completo)"
add "------------------------------------------------------------"

DE_IP=$(kubectl -n $NAMESPACE get svc trisla-decision-engine \
  -o jsonpath='{.spec.clusterIP}')

pipeline=$(curl -s -X POST "http://$DE_IP:8082/engine/decision" \
  -H "Content-Type: application/json" \
  -d '{"slice_type":"URLLC","traffic":"critical","bandwidth":10}')

add "Resposta do Decision Engine:"
add "$pipeline"
add ""

###############################################################
# Fim
###############################################################
add "============================================================"
add "🏁 FIM DO RELATÓRIO DE VALIDAÇÃO TRI-SLA A2"
add "Arquivo salvo em: /tmp/trisla-validation-report.txt"
add "============================================================"

echo "📄 Relatório salvo em: /tmp/trisla-validation-report.txt"
echo "🏁 Validação concluída!"
