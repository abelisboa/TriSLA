#!/bin/bash
set -e

CHART_DIR="/home/porvir5g/gtp5g/trisla/helm/trisla"
VALUES_FILE="$CHART_DIR/values-nasp.yaml"
REPORT="/tmp/TRISLA_HELM_SAFE_REPORT_$(date +%s).txt"

echo "============================================================"
echo "��️  TRI-SLA HELM SAFE DEPLOY MODE (A2) — OFFLINE & CONTROLADO"
echo "============================================================"
echo "Gerado em: $(date)"
echo "Relatório: $REPORT"
echo

echo "📁 Diretório Helm: $CHART_DIR"
echo "📄 Values File:   $VALUES_FILE"
echo

echo "------------------------------------------------------------"
echo "🔍 FASE 1 — Auditoria Offline"
echo "------------------------------------------------------------"

echo "🔎 Procurando arquivos residuais (.backup/.orig/.old)..."
residuos=$(find "$CHART_DIR/templates" -type f \( -name "*.backup" -o -name "*.orig" -o -name "*.old" \))
if [[ -n "$residuos" ]]; then
    echo "⚠️  Encontrados arquivos residuais:"
    echo "$residuos"
    echo "⚠️  Remova-os manualmente ANTES do deploy:"
    echo "    rm $CHART_DIR/templates/*.backup"
    exit 1
else
    echo "✅ Nenhum arquivo residual encontrado."
fi
echo

echo "🔎 Verificando selectors explícitos (app: trisla-*)..."
selectors=$(grep -R "app: trisla-" "$CHART_DIR/templates" || true)
if [[ -z "$selectors" ]]; then
    echo "❌ ERRO: nenhum selector 'app: trisla-*' encontrado."
    exit 1
fi
echo "✅ Selectors encontrados e consistentes."
echo

echo "🔎 Verificando helper trisla.image..."
if ! grep -q "define \"trisla.image\"" "$CHART_DIR/templates/_helpers.tpl"; then
    echo "❌ ERRO: helper trisla.image não encontrado."
    exit 1
fi
echo "✅ Helper encontrado."
echo

echo "------------------------------------------------------------"
echo "🧪 FASE 2 — Validação offline (helm template)"
echo "------------------------------------------------------------"

RENDER="/tmp/TRISLA_HELM_RENDER_$(date +%s).yaml"
helm template trisla "$CHART_DIR" -f "$VALUES_FILE" > "$RENDER"

if [[ $? -ne 0 ]]; then
    echo "❌ ERRO: helm template falhou. Corrija antes do deploy."
    exit 1
fi

echo "✅ helm template executado com sucesso."
echo "📄 Manifesto salvo em: $RENDER"
echo

echo "------------------------------------------------------------"
echo "🧩 FASE 3 — Validação de estrutura"
echo "------------------------------------------------------------"

services=$(grep -c "kind: Service" "$RENDER")
deploys=$(grep -c "kind: Deployment" "$RENDER")

echo "📦 Services encontrados:   $services"
echo "📦 Deployments encontrados: $deploys"

if [[ "$services" -ne 7 ]] || [[ "$deploys" -ne 7 ]]; then
    echo "❌ Quantidade incorreta de Services ou Deployments."
    exit 1
fi

echo "✅ Estrutura correta (7 Services / 7 Deployments)"
echo

echo "------------------------------------------------------------"
echo "🛑 FASE 4 — Confirmação do Usuário"
echo "------------------------------------------------------------"
echo "O deploy está pronto. Nenhum erro encontrado."
echo
read -p "👉 Deseja aplicar o deploy no cluster? (yes/no): " resp

if [[ "$resp" != "yes" ]]; then
    echo "❌ Deploy cancelado pelo usuário. Nada foi aplicado."
    exit 0
fi

echo
echo "------------------------------------------------------------"
echo "🚀 FASE 5 — Helm Upgrade (EXECUTANDO NO CLUSTER)"
echo "------------------------------------------------------------"

helm -n trisla upgrade --install trisla "$CHART_DIR" -f "$VALUES_FILE" --cleanup-on-fail

echo
echo "============================================================"
echo "🎉 DEPLOY APLICADO COM SUCESSO!"
echo "============================================================"
echo "📄 Relatório salvo em: $REPORT"
echo
