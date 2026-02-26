#!/usr/bin/env bash
set -euo pipefail

echo "==============================================="
echo "PROMPT_SNASP_31 — MDCE Deterministic Evolution"
echo "==============================================="

BASE_DIR="/home/porvir5g/gtp5g/trisla"
RUNBOOK="$BASE_DIR/docs/TRISLA_MASTER_RUNBOOK.md"
EVID_DIR="$BASE_DIR/evidencias_nasp/31_mdce_deterministic_evolution"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
HASH_BEFORE=$(sha256sum "$RUNBOOK" | awk '{print $1}')

mkdir -p "$EVID_DIR"

echo "Timestamp: $TIMESTAMP" | tee "$EVID_DIR/00_metadata.txt"
echo "Runbook Hash (before): $HASH_BEFORE" | tee -a "$EVID_DIR/00_metadata.txt"

echo "Atualizando Runbook..."

cat <<EOF >> "$RUNBOOK"

---

### PROMPT_SNASP_31 — MDCE Deterministic Headroom + Transport Domain Activation

**Data:** $TIMESTAMP  
**Ambiente:** node006 ≡ node1  

#### Objetivo

Formalizar evolução arquitetural pós-Freeze v3.11.0, ativando:

- Headroom determinístico no MDCE
- Transporte como domínio decisório completo
- RTT real via Prometheus (probe_duration_seconds)
- Aplicação de modelo conservador: estado_atual + delta_por_slice <= limite

#### Motivação Técnica

Alinhar decisão preventiva de SLA à pergunta de pesquisa:

"Como decidir, no momento da solicitação, se há recursos suficientes nos domínios RAN, Transporte e Core?"

#### Alterações Controladas

- Decision Engine:
  - MDCE_HEADROOM_ENABLED=true
  - MDCE_TRANSPORT_ENABLED=true
  - Custos por slice (CPU, MEM, UE, RTT)
- NASP Adapter:
  - Integração definitiva com Prometheus
  - Extração rtt_p95_ms real
- Nenhuma alteração em:
  - Modelo ML
  - Pesos de decisão
  - Blockchain
  - Kafka
  - Portal

#### Status

PASS (evolução governada)

#### Observação

Esta alteração inaugura nova baseline experimental pós-freeze v3.11.0.
Freeze anterior permanece íntegro e rastreável.

---

EOF

HASH_AFTER=$(sha256sum "$RUNBOOK" | awk '{print $1}')
echo "Runbook Hash (after): $HASH_AFTER" | tee -a "$EVID_DIR/00_metadata.txt"

echo "Gerando snapshot de integridade..."
cp "$RUNBOOK" "$EVID_DIR/TRISLA_MASTER_RUNBOOK_snapshot.md"

echo "==============================================="
echo "PROMPT_SNASP_31 REGISTRADO COM SUCESSO"
echo "==============================================="
echo "Hash Before: $HASH_BEFORE"
echo "Hash After : $HASH_AFTER"
