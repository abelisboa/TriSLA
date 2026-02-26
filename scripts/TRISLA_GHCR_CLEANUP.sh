#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# TRISLA_GHCR_CLEANUP — Limpeza determinística GHCR
# Compatível com USER ou ORG
# ============================================================

OWNER="${OWNER:-abelisboa}"
DRY_RUN="${DRY_RUN:-false}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="./evidencias_cleanup_${TS}"

mkdir -p "$OUT_DIR"

echo "========================================"
echo "TRISLA GHCR CLEANUP"
echo "Owner: $OWNER"
echo "DRY_RUN: $DRY_RUN"
echo "Timestamp: $TS"
echo "Output: $OUT_DIR"
echo "========================================"
echo

if [[ "$DRY_RUN" != "true" && "$DRY_RUN" != "false" ]]; then
  echo "ERRO: DRY_RUN deve ser true ou false."
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "ERRO: GitHub CLI (gh) não instalado."
  exit 2
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "ERRO: Não autenticado no gh."
  exit 3
fi

echo "Autenticação GH validada."
echo

# ------------------------------------------------
# Detecta se OWNER é org ou user
# ------------------------------------------------

if gh api "/orgs/${OWNER}" >/dev/null 2>&1; then
    API_BASE="/orgs/${OWNER}/packages"
    echo "Detectado: ORGANIZAÇÃO"
else
    API_BASE="/users/${OWNER}/packages"
    echo "Detectado: USUÁRIO"
fi

echo

# ------------------------------------------------
# FASE 1 — Listar packages
# ------------------------------------------------

echo "FASE 1 — Listando packages GHCR"
echo "--------------------------------"

gh api \
  -H "Accept: application/vnd.github+json" \
  "${API_BASE}?package_type=container&per_page=100" \
  --jq '.[].name' \
  > "${OUT_DIR}/packages_all.txt"

TOTAL=$(wc -l < "${OUT_DIR}/packages_all.txt")
echo "Total encontrados: $TOTAL"
echo

# ------------------------------------------------
# FASE 2 — Classificação
# ------------------------------------------------

: > "${OUT_DIR}/packages_keep.txt"
: > "${OUT_DIR}/packages_remove.txt"

while read -r pkg; do
    if [[ "$pkg" == trisla-* ]]; then
        echo "Mantido: $pkg"
        echo "$pkg" >> "${OUT_DIR}/packages_keep.txt"
    else
        echo "MARCAR PARA REMOÇÃO: $pkg"
        echo "$pkg" >> "${OUT_DIR}/packages_remove.txt"
    fi
done < "${OUT_DIR}/packages_all.txt"

KEEP_COUNT=$(wc -l < "${OUT_DIR}/packages_keep.txt")
REMOVE_COUNT=$(wc -l < "${OUT_DIR}/packages_remove.txt")

echo
echo "Resumo:"
echo "Manter : $KEEP_COUNT"
echo "Remover: $REMOVE_COUNT"
echo

# ------------------------------------------------
# FASE 3 — Remoção real
# ------------------------------------------------

if [[ "$DRY_RUN" == "false" ]]; then
    echo "FASE 3 — Removendo packages"
    echo "--------------------------------"

    while read -r pkg; do
        echo "Removendo: $pkg"

        gh api \
          -X DELETE \
          -H "Accept: application/vnd.github+json" \
          "${API_BASE}/container/${pkg}" || {
              echo "ERRO ao remover $pkg"
              exit 10
          }

        echo "OK removido: $pkg"
        echo "$pkg" >> "${OUT_DIR}/packages_deleted.txt"

    done < "${OUT_DIR}/packages_remove.txt"

    echo
    echo "Remoção concluída."
else
    echo "DRY_RUN ativo — nenhuma remoção executada."
fi

echo
echo "========================================"
echo "CLEANUP FINALIZADO"
echo "========================================"
