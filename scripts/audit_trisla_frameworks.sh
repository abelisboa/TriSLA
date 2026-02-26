#!/usr/bin/env bash
set -euo pipefail

NS="trisla"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="evidencias_observability_audit_${TS}"
mkdir -p "$OUT_DIR"

echo "==============================================="
echo "TriSLA — Auditoria de Frameworks (FastAPI/Flask/ASGI)"
echo "Namespace: ${NS}"
echo "Evidence: ${OUT_DIR}"
echo "==============================================="

kubectl -n "$NS" get deploy -o name > "${OUT_DIR}/deployments.txt"

while read -r DEP; do
  echo
  echo "-----------------------------------------------"
  echo "DEPLOY: $DEP"
  echo "-----------------------------------------------"

  POD="$(kubectl -n "$NS" get pods -l app=$(echo "$DEP" | sed 's|deployment.apps/||') -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)"
  if [[ -z "${POD}" ]]; then
    # fallback: pega primeiro pod do deployment pelo ownerRef
    POD="$(kubectl -n "$NS" get pods -o jsonpath="{.items[?(@.metadata.ownerReferences[0].kind=='ReplicaSet')].metadata.name}" | tr ' ' '\n' | head -n 1)"
  fi

  echo "POD: ${POD}" | tee -a "${OUT_DIR}/summary.txt"

  # 1) Comando/args do container
  kubectl -n "$NS" get "$DEP" -o jsonpath='{.spec.template.spec.containers[0].name}{"\n"}{.spec.template.spec.containers[0].command}{"\n"}{.spec.template.spec.containers[0].args}{"\n"}' \
    > "${OUT_DIR}/$(echo "$DEP" | tr '/' '_')_cmd.txt" || true

  # 2) Processos (indicadores: uvicorn/gunicorn/hypercorn/waitress)
  kubectl -n "$NS" exec "$POD" -- sh -lc 'ps auxww 2>/dev/null | head -n 5; echo "----"; ps auxww 2>/dev/null | egrep -i "uvicorn|gunicorn|hypercorn|daphne|waitress|flask|fastapi|starlette|asgiref" || true' \
    > "${OUT_DIR}/$(echo "$DEP" | tr '/' '_')_ps.txt" || true

  # 3) requirements (python) e imports (se existir /app)
  kubectl -n "$NS" exec "$POD" -- sh -lc '
    if [ -f /app/requirements.txt ]; then
      echo "== /app/requirements.txt ==";
      sed -n "1,200p" /app/requirements.txt;
    else
      echo "== requirements.txt não encontrado em /app ==";
    fi
    echo "----"
    if [ -d /app/src ]; then
      echo "== Indicadores em /app/src ==";
      grep -RniE "from fastapi|import fastapi|from flask|import flask|from starlette|import starlette|ASGIApp|get_asgi_application" /app/src 2>/dev/null | head -n 50 || true
    else
      echo "== /app/src não existe ==";
    fi
  ' > "${OUT_DIR}/$(echo "$DEP" | tr '/' '_')_python_audit.txt" || true

  # 4) Heurística final (baseada no que foi detectado)
  FRAME="UNKNOWN"
  if grep -qiE "fastapi" "${OUT_DIR}/$(echo "$DEP" | tr '/' '_')_python_audit.txt" 2>/dev/null || \
     grep -qiE "FastAPI" "${OUT_DIR}/$(echo "$DEP" | tr '/' '_')_ps.txt" 2>/dev/null; then
    FRAME="FastAPI/ASGI"
  elif grep -qiE "flask" "${OUT_DIR}/$(echo "$DEP" | tr '/' '_')_python_audit.txt" 2>/dev/null || \
       grep -qiE "flask" "${OUT_DIR}/$(echo "$DEP" | tr '/' '_')_ps.txt" 2>/dev/null; then
    FRAME="Flask/WSGI"
  elif grep -qiE "uvicorn|hypercorn|daphne" "${OUT_DIR}/$(echo "$DEP" | tr '/' '_')_ps.txt" 2>/dev/null; then
    FRAME="ASGI (provável)"
  elif grep -qiE "gunicorn" "${OUT_DIR}/$(echo "$DEP" | tr '/' '_')_ps.txt" 2>/dev/null; then
    FRAME="Gunicorn (WSGI/ASGI mix)"
  fi

  echo "$(echo "$DEP" | sed 's|deployment.apps/||') => ${FRAME}" | tee -a "${OUT_DIR}/framework_matrix.txt"

done < "${OUT_DIR}/deployments.txt"

echo
echo "✅ Auditoria concluída."
echo "Arquivos principais:"
echo " - ${OUT_DIR}/framework_matrix.txt"
echo " - ${OUT_DIR}/*_python_audit.txt"
echo " - ${OUT_DIR}/*_ps.txt"
