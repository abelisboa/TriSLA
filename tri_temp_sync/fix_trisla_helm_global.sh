#!/bin/bash
set -e

ROOT="$(pwd)"
VALUES="$ROOT/helm/trisla/values-nasp.yaml"
TEMPLATES="$ROOT/helm/trisla/templates"

echo "==============================================================="
echo " 🔧 TRISLA — SCRIPT DEFINITIVO DE REPARAÇÃO GLOBAL DO HELM"
echo "     Correção 100% completa dos templates e images"
echo "==============================================================="

MODULES=(
  "bcNssmf:bc-nssmf"
  "decisionEngine:decision-engine"
  "mlNsmf:ml-nsmf"
  "naspAdapter:nasp-adapter"
  "semCsmf:sem-csmf"
  "slaAgentLayer:sla-agent-layer"
  "uiDashboard:ui-dashboard"
)

echo ""
echo "➡ Etapa 1 — Criando blocos .image para TODOS os módulos no values..."
for entry in "${MODULES[@]}"; do
  KEY="${entry%%:*}"
  NAME="${entry##*:}"

  if ! grep -q "^${KEY}:" "$VALUES"; then
    echo "  ➕ Adicionando bloco para $KEY"
    cat << EOT >> "$VALUES"

$KEY:
  image:
    repository: "localhost/trisla-$NAME"
    tag: "local"
  service:
    port: 8080
  replicas: 1
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

EOT
  else
    echo "  ✔ $KEY já existe – ajustando image.repository/tag"
    sed -i "s#repository:.*#repository: \"localhost/trisla-$NAME\"#g" "$VALUES"
    sed -i "s#tag:.*#tag: \"local\"#g" "$VALUES"
  fi
done

echo ""
echo "➡ Etapa 2 — Corrigindo HELM templates (deployment-*.yaml)..."

for entry in "${MODULES[@]}"; do
  KEY="${entry%%:*}"
  NAME="${entry##*:}"
  FILE="$TEMPLATES/deployment-$NAME.yaml"

  if [ ! -f "$FILE" ]; then
    echo "  ⚠ Template não encontrado: $FILE"
    continue
  fi

  echo "  🔧 Corrigindo template: $FILE"

  sed -i 's/–/-/g' "$FILE"
  sed -i 's/—/-/g' "$FILE"
  sed -i 's/−/-/g' "$FILE"

  sed -i "s#image: .*#image: {{ include \"trisla.image\" (dict \"repository\" .Values.$KEY.image.repository \"tag\" .Values.$KEY.image.tag \"Values\" .Values) }}#g" "$FILE"

  sed -i "s/.Values.ui.image/.Values.uiDashboard.image/g" "$FILE"
done

echo ""
echo "➡ Etapa 3 — Validando templates..."
helm template trisla ./helm/trisla -f "$VALUES" > /dev/null 2> helm_fix_errors.log || {
  echo "❌ ERRO — Templates ainda possuem problemas!"
  echo "Veja helm_fix_errors.log"
  exit 1
}

echo ""
echo "==============================================================="
echo " ✔ CORREÇÃO CONCLUÍDA COM SUCESSO"
echo "   Todos os templates e values foram reparados!"
echo "==============================================================="
