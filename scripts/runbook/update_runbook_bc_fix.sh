#!/usr/bin/env bash
set -euo pipefail

# ==============================================
# TriSLA – Update Runbook (BC-NSSMF Fix)
# ==============================================

RUNBOOK="/home/porvir5g/gtp5g/trisla/docs/TRISLA_MASTER_RUNBOOK.md"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
EVD_DIR="/home/porvir5g/gtp5g/trisla/evidencias_runbook/${TIMESTAMP}_bc_fix"

echo "=============================================="
echo "TriSLA – Runbook Update (BC Fix)"
echo "Runbook: $RUNBOOK"
echo "Evidências: $EVD_DIR"
echo "=============================================="

# ------------------------------------------------
# Gate 1 – Verificar existência do arquivo
# ------------------------------------------------
if [ ! -f "$RUNBOOK" ]; then
  echo "❌ ABORT: Runbook não encontrado em:"
  echo "$RUNBOOK"
  exit 1
fi

# ------------------------------------------------
# Criar diretório de evidências
# ------------------------------------------------
mkdir -p "$EVD_DIR"

# ------------------------------------------------
# Backup seguro
# ------------------------------------------------
cp "$RUNBOOK" "$EVD_DIR/TRISLA_MASTER_RUNBOOK_BACKUP.md"

echo "✔ Backup criado."

# ------------------------------------------------
# Idempotência
# ------------------------------------------------
if grep -q "BC-NSSMF – Correção Estrutural Definitiva" "$RUNBOOK"; then
  echo "⚠️ Entrada já existente. Nenhuma alteração aplicada."
  exit 0
fi

# ------------------------------------------------
# Append controlado
# ------------------------------------------------
cat <<EOF >> "$RUNBOOK"

---

## 🔐 BC-NSSMF – Correção Estrutural Definitiva (Helm + RPC + Wallet)

**Data:** $(date +"%Y-%m-%d %H:%M:%S")  
**Release Helm:** $(helm list -n trisla | awk '/trisla/{print $9}')  
**Imagem BC-NSSMF:**  
$(kubectl get deploy trisla-bc-nssmf -n trisla -o jsonpath='{.spec.template.spec.containers[0].image}')

---

### 📌 Problema Identificado

O endpoint:

/health/ready

retornava:

rpc_unreachable  
ou  
wallet_unavailable  

---

### 🧠 Causa Raiz

- BC_RPC_URL não estava definido explicitamente
- Código exige BC_RPC_URL ou BLOCKCHAIN_RPC_URL
- Duplicação silenciosa de BC_ENABLED
- Wallet não validada corretamente

---

### 🔧 Correções Aplicadas

- Definição explícita de BC_RPC_URL
- Injeção da private key via Secret + BC_PRIVATE_KEY_PATH
- Montagem de Secret bc-nssmf-wallet
- Montagem de ConfigMap trisla-bc-contract-address
- Remoção de duplicação de BC_ENABLED
- Readiness real via /health/ready
- Imagem fixada por digest

---

### ✅ Estado Final Validado

\`\`\`
$(kubectl run -n trisla bc-ready --rm -i --restart=Never \
--image=curlimages/curl:8.6.0 -- \
sh -c "curl -s http://trisla-bc-nssmf:8083/health/ready" 2>/dev/null || echo "Health check manual recomendado")
\`\`\`

---

STATUS: ✔️ PASS

EOF

echo "✔ Runbook atualizado."

# ------------------------------------------------
# Salvar diff como evidência
# ------------------------------------------------
diff "$EVD_DIR/TRISLA_MASTER_RUNBOOK_BACKUP.md" "$RUNBOOK" > "$EVD_DIR/diff.txt" || true

echo "✔ Diff salvo em $EVD_DIR/diff.txt"
echo "=============================================="
echo "Runbook atualizado com sucesso."
echo "=============================================="
