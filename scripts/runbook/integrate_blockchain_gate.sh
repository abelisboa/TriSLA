#!/usr/bin/env bash

set -euo pipefail

BASE_DIR="/home/porvir5g/gtp5g/trisla"
RUNBOOK="${BASE_DIR}/docs/TRISLA_MASTER_RUNBOOK.md"
EVID_DIR="${BASE_DIR}/evidencias_runbook"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
EVID_PATH="${EVID_DIR}/${TIMESTAMP}-integrate-blockchain-gate"

echo "=============================================="
echo "TriSLA – Integrate Blockchain Gate into Runbook"
echo "Runbook: ${RUNBOOK}"
echo "Evidence: ${EVID_PATH}"
echo "=============================================="

# 1️⃣ Validar existência do Runbook
if [ ! -f "${RUNBOOK}" ]; then
  echo "❌ Runbook não encontrado."
  exit 1
fi

# 2️⃣ Criar diretório de evidência
mkdir -p "${EVID_PATH}"

# 3️⃣ Backup
cp "${RUNBOOK}" "${EVID_PATH}/TRISLA_MASTER_RUNBOOK.backup.md"
echo "✔ Backup criado."

# 4️⃣ Verificar se já existe seção do Gate
if grep -q "### BLOCKCHAIN GATE (MANDATORY BEFORE EXPERIMENTS)" "${RUNBOOK}"; then
  echo "ℹ️  Seção já existente. Nenhuma duplicação realizada."
else

cat <<EOF >> "${RUNBOOK}"

---

## 🔐 BLOCKCHAIN GATE (MANDATORY BEFORE EXPERIMENTS)

Script Oficial:
\`/home/porvir5g/gtp5g/trisla/scripts/gates/gate_blockchain_e2e.sh\`

### Objetivo
Garantir que:

- BC_ENABLED=true em runtime
- RPC Besu conectado
- Submit real gera tx_hash
- block_number confirmado
- status="ok"
- decision retornada

### Política Obrigatória

Este Gate DEVE retornar PASS antes de:

- Execução de stress tests
- Geração de evidências científicas
- Captura de dados para Capítulo 6
- Criação de nova tag de release
- Deploy em ambiente NASP

### Política de Falha

Se FAIL:
→ ABORTAR imediatamente qualquer coleta ou experimento.
→ Corrigir BC-NSSMF / Besu antes de prosseguir.

### Registro

Todas as execuções devem gerar evidências em:

\`/home/porvir5g/gtp5g/trisla/evidencias_gates/\`

Data de integração automática: ${TIMESTAMP}

---

EOF

  echo "✔ Seção adicionada ao Runbook."
fi

# 5️⃣ Gerar diff
diff "${EVID_PATH}/TRISLA_MASTER_RUNBOOK.backup.md" "${RUNBOOK}" > "${EVID_PATH}/diff.txt" || true
echo "✔ Diff salvo."

echo "=============================================="
echo "Runbook atualizado com governança Blockchain Gate."
echo "=============================================="
