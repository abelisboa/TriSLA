#!/usr/bin/env bash
set -euo pipefail

NS="${1:-trisla}"
REL="${2:-trisla}"

BASE="/home/porvir5g/gtp5g/trisla"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
EVD="${BASE}/evidencias_hardening/nasp_adapter_${TS}"
mkdir -p "${EVD}"

echo "=================================================="
echo "TriSLA — HARDEN NASP ADAPTER"
echo "Namespace : ${NS}"
echo "Release   : ${REL}"
echo "Evidence  : ${EVD}"
echo "=================================================="

cd "${BASE}"

echo "[0] Verificando árvore do repositório..."
ls -lah > "${EVD}/repo_ls.txt" || true

echo "[1] Localizando código do NASP Adapter no repo..."
# tenta achar main.py do adapter
CANDIDATE="$(grep -R --line-number -m1 "TriSLA NASP Adapter" -n . 2>/dev/null | head -n1 | cut -d: -f1 || true)"
if [[ -z "${CANDIDATE}" ]]; then
  # fallback: buscar app/src/main.py que contém o endpoint
  CANDIDATE="$(grep -R --line-number -m1 '@app.post("/api/v1/nsi/instantiate")' -n . 2>/dev/null | head -n1 | cut -d: -f1 || true)"
fi

if [[ -z "${CANDIDATE}" ]]; then
  echo "ERRO: Não localizei o main.py do NASP Adapter no repositório."
  echo "Dica: garanta que o código fonte do nasp-adapter esteja presente neste repo."
  exit 1
fi

MAIN_PY="${CANDIDATE}"
ADAPTER_DIR="$(cd "$(dirname "${MAIN_PY}")"/.. && pwd -P)"
echo "MAIN_PY=${MAIN_PY}" | tee "${EVD}/paths.txt"
echo "ADAPTER_DIR=${ADAPTER_DIR}" | tee -a "${EVD}/paths.txt"

echo "[2] Backup antes do patch..."
cp -a "${MAIN_PY}" "${EVD}/main.py.prepatch"
# localizar nsi_controller.py
NSI_CTRL="$(grep -R --line-number -m1 "class NSIController" -n "${ADAPTER_DIR}" 2>/dev/null | head -n1 | cut -d: -f1 || true)"
if [[ -n "${NSI_CTRL}" ]]; then
  cp -a "${NSI_CTRL}" "${EVD}/nsi_controller.py.prepatch"
  echo "NSI_CTRL=${NSI_CTRL}" | tee -a "${EVD}/paths.txt"
else
  echo "AVISO: não localizei nsi_controller.py automaticamente (seguirei apenas com main.py)."
fi

echo "[3] Aplicando patch no main.py (observabilidade + normalização de payload)..."
python3 - <<'PY'
import re, sys, pathlib

main_py = pathlib.Path(sys.argv[1])
txt = main_py.read_text(encoding="utf-8")

# 3.1) Hardening observabilidade: nsi.phase nunca None
# substitui:
# span.set_attribute("nsi.phase", created_nsi.get("status", {}).get("phase"))
txt = re.sub(
    r'span\.set_attribute\("nsi\.phase",\s*created_nsi\.get\("status",\s*\{\}\)\.get\("phase"\)\s*\)',
    'phase_attr = (created_nsi.get("status", {}) or {}).get("phase") or "unknown"\n            span.set_attribute("nsi.phase", phase_attr)',
    txt
)

# 3.2) Inserir funções utilitárias (sanitização RFC1123 + normalização SLA) se ainda não existirem
if "def _rfc1123_name(" not in txt:
    insert_point = txt.find('@app.post("/api/v1/nsi/instantiate")')
    if insert_point == -1:
        raise SystemExit("Não achei o decorator do endpoint instantiate para inserir helpers.")
    helpers = r'''
import re as _re

def _rfc1123_name(name: str) -> str:
    """
    Converte para RFC1123 (lowercase, [a-z0-9-], sem underscores, sem letras maiúsculas).
    Mantém previsibilidade e evita 422 do apiserver.
    """
    s = (name or "").strip().lower()
    s = _re.sub(r"[^a-z0-9\-\.]", "-", s)  # troca tudo que não é permitido por '-'
    s = _re.sub(r"-{2,}", "-", s)
    s = s.strip("-.")
    if not s:
        s = "nsi"
    return s

def _normalize_service_profile(nsi_spec: dict) -> str:
    return nsi_spec.get("serviceProfile") or nsi_spec.get("service_type") or nsi_spec.get("service_profile") or "eMBB"

def _normalize_sla(nsi_spec: dict) -> dict:
    """
    Normaliza SLA para o CRD atual:
      spec.sla.latency: string (ex: '10ms')
      spec.sla.availability: number
      spec.sla.reliability: number
    Aceita chaves legadas e converte sem quebrar chamadas antigas.
    """
    sla = nsi_spec.get("sla") or nsi_spec.get("sla_requirements") or {}
    if not isinstance(sla, dict):
        return {}

    out = {}
    # latency
    if "latency" in sla:
        # se já vier string, mantém; se vier número, converte para ms
        v = sla.get("latency")
        if isinstance(v, (int, float)):
            out["latency"] = f"{int(v)}ms"
        else:
            out["latency"] = str(v)
    else:
        for k in ("latency_max_ms", "latencia_maxima_ms", "latency_maxima_ms"):
            if k in sla and sla.get(k) is not None:
                out["latency"] = f"{int(sla.get(k))}ms"
                break

    # availability / reliability (mantém apenas se numéricos)
    for k in ("availability", "reliability"):
        v = sla.get(k)
        if isinstance(v, (int, float)):
            out[k] = float(v)

    return out
'''
    txt = txt[:insert_point] + helpers + "\n\n" + txt[insert_point:]

main_py.write_text(txt, encoding="utf-8")
print("OK: main.py patch aplicado")
PY "${MAIN_PY}" | tee "${EVD}/patch_main_py.log"

if [[ -n "${NSI_CTRL:-}" ]]; then
  echo "[4] Aplicando patch no nsi_controller.py (RFC1123 name + remover status no create + SLA normalizado)..."
  python3 - <<'PY'
import re, sys, pathlib

p = pathlib.Path(sys.argv[1])
txt = p.read_text(encoding="utf-8")

# 4.1) Forçar nsi_id RFC1123 (lowercase) — sem alterar o ID lógico (spec.nsiId) do usuário, mas garantindo metadata.name válido
# substitui:
# nsi_id = nsi_spec.get("nsiId") or f"nsi-{uuid.uuid4().hex[:8]}"
# por uma versão sanitizada
txt = re.sub(
    r'nsi_id\s*=\s*nsi_spec\.get\("nsiId"\)\s*or\s*f"nsi-\{uuid\.uuid4\(\)\.hex\[:8\]\}"',
    'raw_id = nsi_spec.get("nsiId") or f"nsi-{uuid.uuid4().hex[:8]}"\n            nsi_id = re.sub(r"[^a-z0-9\\-\\.]", "-", str(raw_id).strip().lower())\n            nsi_id = re.sub(r"-{2,}", "-", nsi_id).strip("-.") or "nsi"',
    txt
)

# 4.2) Normalizar serviceProfile e SLA no controller (compat payload legado)
# serviceProfile: nsi_spec.get("serviceProfile","eMBB") -> aceitar service_type/service_profile
txt = txt.replace(
    'nsi_spec.get("serviceProfile", "eMBB")',
    '(nsi_spec.get("serviceProfile") or nsi_spec.get("service_type") or nsi_spec.get("service_profile") or "eMBB")'
)

# sla: nsi_spec.get("sla", {}) -> converter latency_max_ms => latency:"Xms" e filtrar campos válidos
if 'def _normalize_sla' not in txt:
    # inserir helper simples após imports
    ins = txt.find("logger = logging.getLogger(__name__)")
    helper = r'''
import re

def _normalize_sla(sla: dict) -> dict:
    if not isinstance(sla, dict):
        return {}
    out = {}
    # latency
    if "latency" in sla:
        v = sla.get("latency")
        if isinstance(v, (int, float)):
            out["latency"] = f"{int(v)}ms"
        else:
            out["latency"] = str(v)
    else:
        for k in ("latency_max_ms", "latencia_maxima_ms", "latency_maxima_ms"):
            if k in sla and sla.get(k) is not None:
                out["latency"] = f"{int(sla.get(k))}ms"
                break
    # availability/reliability
    for k in ("availability", "reliability"):
        v = sla.get(k)
        if isinstance(v, (int, float)):
            out[k] = float(v)
    return out
'''
    if ins != -1:
        txt = txt[:ins] + helper + "\n" + txt[ins:]

# trocar o ponto de uso do sla
txt = txt.replace(
    '"sla": nsi_spec.get("sla", {})',
    '"sla": _normalize_sla(nsi_spec.get("sla") or nsi_spec.get("sla_requirements") or {})'
)

# 4.3) Remover o bloco "status" do body no create (evita warning unknown field status.createdAt)
# remove o bloco status inteiro do nsi_body, se existir
txt = re.sub(r',\s*"status"\s*:\s*\{[^}]*"createdAt"[^}]*\}\s*\n\s*\}', r'\n            }', txt, flags=re.S)

p.write_text(txt, encoding="utf-8")
print("OK: nsi_controller.py patch aplicado")
PY "${NSI_CTRL}" | tee "${EVD}/patch_nsi_controller.log"
fi

echo "[5] Gerando diff para evidência..."
git diff > "${EVD}/git_diff.patch" || true
git status > "${EVD}/git_status.txt" || true

echo "[6] Build/Push de imagem (somente NASP Adapter) e atualização via Helm..."
# Detectar docker build context
DOCKERFILE="$(find "${ADAPTER_DIR}" -maxdepth 3 -name Dockerfile -print | head -n1 || true)"
if [[ -z "${DOCKERFILE}" ]]; then
  echo "ERRO: Não encontrei Dockerfile em ${ADAPTER_DIR} (até 3 níveis)."
  echo "Ajuste o repositório/estrutura do adapter para permitir build."
  exit 1
fi

BUILD_CTX="$(dirname "${DOCKERFILE}")"
echo "DOCKERFILE=${DOCKERFILE}" | tee -a "${EVD}/paths.txt"
echo "BUILD_CTX=${BUILD_CTX}" | tee -a "${EVD}/paths.txt"

# tag imutável por timestamp (mesmo que você vá consolidar digest depois, aqui o digest será calculado já)
IMG="ghcr.io/abelisboa/trisla-nasp-adapter:hardening-${TS}"
echo "${IMG}" > "${EVD}/image_tag.txt"

echo "-> docker build"
docker build -t "${IMG}" -f "${DOCKERFILE}" "${BUILD_CTX}" | tee "${EVD}/docker_build.log"

echo "-> docker push"
docker push "${IMG}" | tee "${EVD}/docker_push.log"

echo "-> obtendo digest"
DIGEST="$(docker inspect --format='{{index .RepoDigests 0}}' "${IMG}" | awk -F'@' '{print $2}')"
if [[ -z "${DIGEST}" ]]; then
  echo "ERRO: não consegui obter digest do push (RepoDigests vazio)."
  exit 1
fi
echo "${DIGEST}" > "${EVD}/image_digest.txt"
echo "DIGEST=${DIGEST}"

echo "-> helm upgrade (somente naspAdapter.image.digest)"
helm upgrade "${REL}" helm/trisla -n "${NS}" --reuse-values \
  --set naspAdapter.image.repository=trisla-nasp-adapter \
  --set naspAdapter.image.tag="" \
  --set naspAdapter.image.digest="${DIGEST}" \
  | tee "${EVD}/helm_upgrade.log"

echo "[7] Validando rollout do NASP Adapter..."
kubectl rollout status -n "${NS}" deploy/trisla-nasp-adapter --timeout=180s | tee "${EVD}/rollout_status.txt"
kubectl get pods -n "${NS}" -l app=trisla,component=nasp-adapter -o wide | tee "${EVD}/pods.txt" || true

echo "[8] Rodando validação CRD-compliant (reaproveitando seu probe)..."
# chama seu script existente se estiver presente
PROBE="${BASE}/scripts/nsi_instantiate_probe_crd_compliant.sh"
if [[ -x "${PROBE}" ]]; then
  "${PROBE}" "${NS}" | tee "${EVD}/probe_run.log"
else
  echo "AVISO: ${PROBE} não encontrado/executável. Fazendo teste mínimo via port-forward."
  PF_PID=""
  kubectl port-forward -n "${NS}" deploy/trisla-nasp-adapter 18085:8085 >/tmp/pf.log 2>&1 &
  PF_PID=$!
  sleep 2
  curl -s http://127.0.0.1:18085/health | tee "${EVD}/health.json"; echo
  kill "${PF_PID}" || true
fi

echo "[9] Coletando logs recentes..."
kubectl logs -n "${NS}" deploy/trisla-nasp-adapter --since=10m > "${EVD}/nasp_adapter_logs_10m.txt" || true

echo "=================================================="
echo "HARDENING COMPLETO"
echo "Evidence: ${EVD}"
echo "=================================================="

