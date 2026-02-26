#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/porvir5g/gtp5g/trisla"
RUNBOOK="$ROOT/docs/TRISLA_MASTER_RUNBOOK.md"
TS="$(date +%Y%m%d-%H%M%S)"
EVD="$ROOT/evidencias_runbook/${TS}-update-runbook-baseline-freeze"
mkdir -p "$EVD"

echo "=============================================="
echo "TriSLA – Update Runbook: Baseline Freeze + E2E Full (Portal→3GPP)"
echo "Runbook: $RUNBOOK"
echo "Evidence: $EVD"
echo "=============================================="

if [[ ! -f "$RUNBOOK" ]]; then
  echo "❌ FAIL: Runbook não encontrado: $RUNBOOK"
  exit 1
fi

cp -a "$RUNBOOK" "$EVD/TRISLA_MASTER_RUNBOOK.md.backup"
echo "✔ Backup criado."

SECTION_MARK="## GATE — Baseline Freeze e E2E FULL (Portal → 3GPP → Observabilidade)"

# Evitar duplicar
if grep -qF "$SECTION_MARK" "$RUNBOOK"; then
  echo "ℹ️ Seção já existe no Runbook. Gerando apenas evidência (diff vazio esperado)."
else
  cat >> "$RUNBOOK" <<'MD'

## GATE — Baseline Freeze e E2E FULL (Portal → 3GPP → Observabilidade)

### Objetivo
Estabelecer um baseline operacional congelado (baseline freeze) e validar o fluxo E2E completo com instantiation 3GPP real via NASP Adapter, com evidências auditáveis (sem simulação).

### Regras (anti-regressão)
1. Todos os comandos devem produzir saída verificável (sem arquivos vazios, sem “null” silencioso).
2. Não é permitido “simular” métricas: se uma query Prometheus não existir, registrar explicitamente NOT_FOUND com evidência do endpoint.
3. O Gate 3GPP só é considerado ativo se `GATE_3GPP_ENABLED=true` estiver refletido no Deployment do NASP Adapter.
4. O E2E FULL só é considerado aprovado se houver:
   - resposta do Portal com `status=ok`
   - `tx_hash` e `block_number` válidos (BC confirmado)
   - criação detectável de namespace `ns-nsi-*` (diff before/after)
   - inventário do namespace criado (get all / quotas / netpol)
   - coleta mínima CORE/RAN/Transporte (mesmo que com fallback auditável)

### Scripts Oficiais
- Habilitar Gate 3GPP (controlado e verificável):
  - `scripts/runbook/enable_gate_3gpp_instantiation.sh`

- E2E FULL com evidências:
  - `scripts/e2e/e2e_portal_to_nasp_full.sh`

### Evidências geradas
- `evidencias_runbook/*-enable-gate-3gpp/*`
- `evidencias_e2e/*-e2e-portal-to-nasp-full/*`

### Critério de PASS/FAIL
- PASS: todos os asserts do script E2E FULL satisfeitos.
- FAIL: qualquer um dos seguintes:
  - Gate 3GPP não habilitado no deployment
  - submit sem `status=ok`
  - BC sem confirmação
  - namespace `ns-nsi-*` não criado
  - evidência incompleta (outputs vazios sem justificativa)

MD
  echo "✔ Seção adicionada ao Runbook."
fi

diff -u "$EVD/TRISLA_MASTER_RUNBOOK.md.backup" "$RUNBOOK" | tee "$EVD/runbook.diff" >/dev/null || true
echo "✔ Diff salvo."
echo "=============================================="
echo "✅ Runbook atualizado (Baseline Freeze + E2E FULL)"
echo "Evidence: $EVD"
echo "=============================================="
