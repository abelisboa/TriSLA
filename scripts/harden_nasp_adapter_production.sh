#!/usr/bin/env bash
set -euo pipefail

NS="${1:-trisla}"
REL="${2:-trisla}"

ROOT="/home/porvir5g/gtp5g/trisla"
SCRIPTS="${ROOT}/scripts"

APP_DIR="${ROOT}/apps/nasp-adapter"
SRC_DIR="${APP_DIR}/src"
MAIN_PY="${SRC_DIR}/main.py"

TS="$(date -u +%Y%m%dT%H%M%SZ)"
EVD="${ROOT}/evidencias_hardening/nasp_adapter_prod_${TS}"
mkdir -p "${EVD}"

log(){ echo -e "$*"; }
die(){ echo -e "❌ $*" >&2; exit 1; }

require_cmd(){
  command -v "$1" >/dev/null 2>&1 || die "Comando obrigatório não encontrado: $1"
}

safe_kubectl(){
  kubectl "$@" 2>&1 | tee -a "${EVD}/kubectl.log"
}

safe_helm(){
  helm "$@" 2>&1 | tee -a "${EVD}/helm.log"
}

cat > "${EVD}/meta.txt" <<EOF
timestamp_utc=${TS}
namespace=${NS}
release=${REL}
repo_root=${ROOT}
app_dir=${APP_DIR}
EOF

log "=================================================="
log "TriSLA — HARDEN NASP ADAPTER (PRODUÇÃO)"
log "Namespace : ${NS}"
log "Release   : ${REL}"
log "Context   : ${APP_DIR}"
log "Evidence  : ${EVD}"
log "=================================================="

require_cmd kubectl
require_cmd helm
require_cmd sed
require_cmd awk
require_cmd grep
require_cmd sha256sum

[ -d "${APP_DIR}" ] || die "Diretório do app não existe: ${APP_DIR}"
[ -f "${APP_DIR}/Dockerfile" ] || die "Dockerfile não encontrado: ${APP_DIR}/Dockerfile"
[ -f "${MAIN_PY}" ] || die "main.py não encontrado: ${MAIN_PY}"

log "[0] Snapshot pre-hardening..."
cp -a "${MAIN_PY}" "${EVD}/main.py.pre.patch"
sha256sum "${MAIN_PY}" | tee "${EVD}/sha_main_pre.txt" >/dev/null

log "[1] Aplicando patch determinístico em main.py..."

python3 - <<'PY' "${MAIN_PY}" "${EVD}/main.py.post.patch"
import re, sys, pathlib, json

path = pathlib.Path(sys.argv[1])
outp = pathlib.Path(sys.argv[2])

src = path.read_text(encoding="utf-8")

# ---------------------------------------------------------------------
# 1) Inserir helpers (RFC1123 + SLA normalization + safe span attr)
# ---------------------------------------------------------------------
helpers = r'''
# ==============================
# TRI-SLA HARDENING HELPERS
# ==============================
import re as _re

_RFC1123_RE = _re.compile(r'[^a-z0-9\-\.]+')

def _to_rfc1123_name(name: str) -> str:
    """
    Normaliza nomes para RFC1123 (K8s metadata.name):
    - lowercase
    - permite [a-z0-9-\.]
    - remove caracteres inválidos
    - garante começar/terminar com alfanumérico
    """
    if not name:
        return "nsi"
    s = str(name).strip().lower()
    s = _RFC1123_RE.sub("-", s)
    s = _re.sub(r'[-\.]+', '-', s)
    s = s.strip('-.')
    if not s:
        s = "nsi"
    return s

def _normalize_latency(val):
    """
    CRD espera spec.sla.latency como string.
    Aceita:
      - int/float (assume ms) -> "10ms"
      - "10" -> "10ms"
      - "10ms" -> "10ms"
      - "0.5s" mantém
    """
    if val is None:
        return None
    if isinstance(val, (int, float)):
        # assume ms
        if float(val).is_integer():
            return f"{int(val)}ms"
        return f"{val}ms"
    s = str(val).strip()
    if not s:
        return None
    # se for só número, assume ms
    if _re.fullmatch(r'[0-9]+(\.[0-9]+)?', s):
        if s.endswith(".0"):
            s = s[:-2]
        return f"{s}ms"
    return s

def _normalize_sla(sla: dict) -> dict:
    """
    CRD schema (observado):
      sla:
        availability: number
        reliability: number
        latency: string
    Remove campos desconhecidos e normaliza aliases como latency_max_ms.
    """
    if not isinstance(sla, dict):
        return {}
    out = {}

    # aliases comuns
    if "latency" in sla:
        out["latency"] = _normalize_latency(sla.get("latency"))
    elif "latency_max_ms" in sla:
        out["latency"] = _normalize_latency(sla.get("latency_max_ms"))

    if "availability" in sla:
        try:
            out["availability"] = float(sla.get("availability"))
        except Exception:
            pass
    if "reliability" in sla:
        try:
            out["reliability"] = float(sla.get("reliability"))
        except Exception:
            pass

    # remove None
    return {k: v for k, v in out.items() if v is not None}

def _sanitize_nsi_payload(nsi_spec: dict) -> dict:
    """
    Remove campos não suportados, aplica aliases e garante conformidade CRD.
    """
    if not isinstance(nsi_spec, dict):
        return {}
    # aliases (snake_case -> camelCase)
    nsi_id = nsi_spec.get("nsiId") or nsi_spec.get("nsi_id") or nsi_spec.get("intent_id")
    service_profile = nsi_spec.get("serviceProfile") or nsi_spec.get("service_profile") or nsi_spec.get("service_type")
    tenant_id = nsi_spec.get("tenantId") or nsi_spec.get("tenant_id") or "default"

    # nssai: manter apenas sst/sd se existir
    nssai = nsi_spec.get("nssai") or {}
    if not isinstance(nssai, dict):
        nssai = {}
    clean_nssai = {}
    if "sst" in nssai:
        clean_nssai["sst"] = nssai.get("sst")
    else:
        clean_nssai["sst"] = 1
    if "sd" in nssai and nssai.get("sd"):
        clean_nssai["sd"] = str(nssai.get("sd"))

    sla = nsi_spec.get("sla") or nsi_spec.get("sla_requirements") or {}
    clean_sla = _normalize_sla(sla)

    # gera id se faltar
    if not nsi_id:
        import uuid
        nsi_id = f"nsi-{uuid.uuid4().hex[:8]}"

    # RFC1123
    nsi_id = _to_rfc1123_name(nsi_id)

    out = {
        "nsiId": nsi_id,
        "serviceProfile": service_profile or "eMBB",
        "tenantId": tenant_id,
        "nssai": clean_nssai,
        "sla": clean_sla,
    }

    # suporte a reserveOnly (cap accounting TTL tests)
    if nsi_spec.get("_reserveOnly") is True:
        out["_reserveOnly"] = True

    return out

def _span_set(span, k, v):
    """
    Evita erro do OpenTelemetry com NoneType.
    """
    try:
        if v is None:
            return
        span.set_attribute(k, v)
    except Exception:
        # nunca quebrar o fluxo por observabilidade
        return
# ==============================
# END HARDENING HELPERS
# ==============================
'''

# Inserir helpers após imports do arquivo, sem duplicar
if "TRI-SLA HARDENING HELPERS" not in src:
    # Heurística: inserir após o último import/os.getenv definition no topo
    # Encontrar último bloco de imports
    m = list(re.finditer(r'^(import .*|from .* import .*)\s*$', src, flags=re.M))
    insert_at = m[-1].end() if m else 0
    src = src[:insert_at] + "\n" + helpers + "\n" + src[insert_at:]

# ---------------------------------------------------------------------
# 2) No endpoint instantiate_nsi: sanitizar payload no início
# ---------------------------------------------------------------------
# Padrão: async def instantiate_nsi(nsi_spec: dict):
pat = r'(@app\.post\("/api/v1/nsi/instantiate"\)\s*\nasync def instantiate_nsi\(nsi_spec: dict\):\s*\n\s*"""[\s\S]*?"""\s*\n)'
m = re.search(pat, src, flags=re.M)
if not m:
    raise SystemExit("Não encontrei a assinatura do endpoint /api/v1/nsi/instantiate em main.py")

block = m.group(1)

# Inserir sanitização logo após abrir o span / try, mas antes de qualquer uso
# Vamos substituir a primeira ocorrência de logger.info(... nsi_spec.get...) para usar payload sanitizado.
# Primeiro: garantir que exista 'with tracer.start_as_current_span("instantiate_nsi") as span:'
if 'start_as_current_span("instantiate_nsi")' not in src:
    raise SystemExit("Não encontrei start_as_current_span('instantiate_nsi')")

# Substituir linha de log "Recebida requisição..." para:
# nsi_spec = _sanitize_nsi_payload(nsi_spec)
# logger.info(... nsi_spec.get('nsiId'...))
src = re.sub(
    r'logger\.info\(f"🔷 \[NSI\] Recebida requisição de instanciação: \{nsi_spec\.get\(\'nsiId\', \'auto\'\)\}"\)',
    "nsi_spec = _sanitize_nsi_payload(nsi_spec)\n            logger.info(f\"🔷 [NSI] Recebida requisição de instanciação: {nsi_spec.get('nsiId','auto')}\")",
    src,
    count=1
)

# ---------------------------------------------------------------------
# 3) Corrigir span.set_attribute para _span_set
# ---------------------------------------------------------------------
# trocar padrões span.set_attribute("x", y) por _span_set(span,"x",y) apenas no instantiate_nsi
# abordagem simples: substituir globalmente, mas com cuidado: apenas linhas "span.set_attribute("
src = re.sub(r'\bspan\.set_attribute\(\s*(".*?")\s*,\s*([^)]+?)\s*\)',
             r'_span_set(span, \1, \2)', src)

# ---------------------------------------------------------------------
# 4) Garantir create_nsi não inclua status no body (se ainda existir em controller)
# (Isso é em nsi_controller.py, mas o erro de warning mostrou status.createdAt unknown, então
# vamos deixar main.py não repassar qualquer status e confiar no controller. Aqui, asseguramos
# que instantiate nsi_spec não carrega "status".)
# ---------------------------------------------------------------------
# Remover chave status se vier do payload original (por segurança)
src = re.sub(r'(_sanitize_nsi_payload\(nsi_spec\)\n)', r'\1            nsi_spec.pop("status", None)\n', src, count=1)

outp.write_text(src, encoding="utf-8")
print("OK")
PY

# Aplicar arquivo gerado
cp -a "${EVD}/main.py.post.patch" "${MAIN_PY}"
sha256sum "${MAIN_PY}" | tee "${EVD}/sha_main_post.txt" >/dev/null

log "[2] Diff (resumo) ..."
diff -u "${EVD}/main.py.pre.patch" "${MAIN_PY}" | sed -n '1,220p' | tee "${EVD}/diff_head.txt" >/dev/null || true

log "[3] Build + Push + Deploy (DIGEST ONLY)..."
# Reaproveita lógica do seu script já validado, mas embutimos aqui para não depender de versões anteriores.

require_cmd podman

IMG_REPO="ghcr.io/abelisboa/trisla-nasp-adapter"
LOCAL_TAG="build-${TS}"

# Build
(
  cd "${APP_DIR}"
  podman build -t "${IMG_REPO}:${LOCAL_TAG}" -f Dockerfile . 2>&1 | tee "${EVD}/build.log"
)

# Push
podman push "${IMG_REPO}:${LOCAL_TAG}" 2>&1 | tee "${EVD}/push.log"

# Descobrir digest do manifest remoto (podman imprime no final, mas também tentamos inspeção)
DIGEST="$(grep -Eo 'sha256:[0-9a-f]{64}' "${EVD}/push.log" | tail -n 1 || true)"
if [ -z "${DIGEST}" ]; then
  # fallback: inspect remoto via skopeo se existir
  if command -v skopeo >/dev/null 2>&1; then
    skopeo inspect "docker://${IMG_REPO}:${LOCAL_TAG}" --format '{{.Digest}}' | tee "${EVD}/digest.txt" >/dev/null
    DIGEST="$(cat "${EVD}/digest.txt" | tr -d '\n')"
  fi
fi
[ -n "${DIGEST}" ] || die "Não consegui extrair digest após push."

echo "Digest: ${DIGEST}" | tee "${EVD}/digest.txt" >/dev/null

log "[4] Helm upgrade aplicando digest (sem tag latest)..."

# aplicar digest no chart: assumir valores em 05_helm/values.yaml mostram naspAdapter.image.digest
safe_helm upgrade "${REL}" "${ROOT}/helm/trisla" -n "${NS}" --reuse-values \
  --set "naspAdapter.image.digest=${DIGEST}" \
  --set "naspAdapter.image.tag=" \
  --set "naspAdapter.image.repository=trisla-nasp-adapter" \
  --set "global.imageRegistry=ghcr.io/abelisboa"

log "[5] Rollout..."
safe_kubectl rollout status -n "${NS}" deploy/trisla-nasp-adapter --timeout=180s | tee "${EVD}/rollout_status.txt" >/dev/null

log "[6] Validando digest real em execução..."
# Descobrir pod pelo label app=trisla-nasp-adapter (já confirmado)
POD="$(kubectl get pods -n "${NS}" -l app=trisla-nasp-adapter -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)"
[ -n "${POD}" ] || die "Não encontrei pod do nasp-adapter por label app=trisla-nasp-adapter"

kubectl get pod -n "${NS}" "${POD}" -o jsonpath='{.status.containerStatuses[0].image}' | tee "${EVD}/pod_image.txt" >/dev/null
kubectl get pod -n "${NS}" "${POD}" -o jsonpath='{.status.containerStatuses[0].imageID}' | tee "${EVD}/pod_imageID.txt" >/dev/null

log "[7] Health check (port-forward temporário)..."
PF_LOG="${EVD}/portforward.log"
kubectl port-forward -n "${NS}" deploy/trisla-nasp-adapter 18085:8085 >"${PF_LOG}" 2>&1 &
PF_PID=$!
sleep 2

set +e
curl -sS "http://127.0.0.1:18085/health" | tee "${EVD}/health.json"
HC=$?
set -e

kill "${PF_PID}" >/dev/null 2>&1 || true
wait "${PF_PID}" >/dev/null 2>&1 || true

[ "${HC}" -eq 0 ] || die "Health check falhou via port-forward."

log "[8] Probe CRD-compliant (NSI URLLC) + verificações..."
# cria id crd compliant
NSI_ID="probe-urllc-${TS,,}"
NSI_ID="${NSI_ID//_/}"
NSI_ID="${NSI_ID//:/}"
NSI_ID="${NSI_ID//./-}"

# port-forward novamente
kubectl port-forward -n "${NS}" deploy/trisla-nasp-adapter 18085:8085 >"${PF_LOG}.probe" 2>&1 &
PF_PID=$!
sleep 2

PAYLOAD="$(cat <<EOF
{
  "nsiId": "${NSI_ID}",
  "serviceProfile": "URLLC",
  "tenantId": "default",
  "sla": { "latency": "10ms" }
}
EOF
)"

echo "${PAYLOAD}" > "${EVD}/probe_payload.json"

set +e
curl -sS -o "${EVD}/probe_response.json" -w "HTTP=%{http_code}\n" \
  -X POST "http://127.0.0.1:18085/api/v1/nsi/instantiate" \
  -H "Content-Type: application/json" \
  -d "${PAYLOAD}" | tee "${EVD}/probe_http.txt"
RC=$?
set -e

kill "${PF_PID}" >/dev/null 2>&1 || true
wait "${PF_PID}" >/dev/null 2>&1 || true

[ "${RC}" -eq 0 ] || die "Falha no curl do probe."

HTTP_CODE="$(grep -Eo 'HTTP=[0-9]+' "${EVD}/probe_http.txt" | cut -d= -f2 | tail -n1)"
[ "${HTTP_CODE}" = "200" ] || die "Probe instantiate retornou HTTP ${HTTP_CODE}. Ver ${EVD}/probe_response.json"

sleep 3

# coletar evidências do CR criado
safe_kubectl get networksliceinstance "${NSI_ID}" -n "${NS}" -o yaml | tee "${EVD}/nsi.yaml" >/dev/null

# namespace isolado e quota
NS_ISO="ns-${NSI_ID}"
safe_kubectl get ns "${NS_ISO}" -o yaml | tee "${EVD}/namespace.yaml" >/dev/null
safe_kubectl get resourcequota -n "${NS_ISO}" -o yaml | tee "${EVD}/resourcequota.yaml" >/dev/null

# logs recentes (para confirmar ausência do erro NoneType)
safe_kubectl logs -n "${NS}" deploy/trisla-nasp-adapter --since=10m | tail -n 250 | tee "${EVD}/nasp_adapter_logs_tail.txt" >/dev/null

log "=================================================="
log "✅ HARDENING COMPLETED (PRODUÇÃO)"
log "Digest aplicado : ${DIGEST}"
log "NSI probe       : ${NSI_ID}"
log "Evidence        : ${EVD}"
log "=================================================="

