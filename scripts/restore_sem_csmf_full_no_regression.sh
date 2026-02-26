#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# TriSLA — Restore SEM-CSMF (FULL) + Keep Observability Block
# Governança: sem regressão, sem invenção, baseado em Git
# ============================================================

ROOT="${ROOT:-/home/porvir5g/gtp5g/trisla}"
APP_FILE_REL="apps/sem-csmf/src/main.py"
VALUES_FILE_REL="helm/trisla/values.yaml"

# Marcadores para localizar o bloco de observabilidade "novo" no arquivo atual
OBS_BEGIN_REGEX='^# ============================================================\s*$'
# Âncora segura para "fim do bloco de observabilidade" (antes dos imports internos)
OBS_END_ANCHOR='^# ============================================================\s*$'

# Endpoints que o Portal usa (âncoras para achar commit bom)
NEEDLE_1='/api/v1/intents/register'
NEEDLE_2='/api/v1/intents'
NEEDLE_3='/api/v1/slices'
NEEDLE_4='/api/v1/nests'

TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
EVID_DIR="${ROOT}/evidencias_restore_sem_csmf_${TS_UTC}"
mkdir -p "${EVID_DIR}"

log(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }

die(){
  echo "FATAL: $*" >&2
  exit 1
}

need(){
  command -v "$1" >/dev/null 2>&1 || die "comando ausente: $1"
}

need git
need sed
need awk
need grep
need python3

cd "${ROOT}" || die "não foi possível acessar ROOT=${ROOT}"

log "EVIDENCIA: ${EVID_DIR}"

# ------------------------------------------------------------
# 0) Pré-gate: confirmar repo e arquivo
# ------------------------------------------------------------
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "ROOT não é um repositório git"
[[ -f "${APP_FILE_REL}" ]] || die "arquivo não encontrado: ${APP_FILE_REL}"
[[ -f "${VALUES_FILE_REL}" ]] || log "AVISO: values.yaml não encontrado: ${VALUES_FILE_REL} (continuando sem corrigir digest default)"

log "Salvando status/diff atuais"
git status --porcelain > "${EVID_DIR}/git_status_porcelain.txt" || true
git diff > "${EVID_DIR}/git_diff_full.patch" || true
git diff -- "${APP_FILE_REL}" > "${EVID_DIR}/diff_sem_csmf_main.patch" || true

# Backup do arquivo atual
cp -a "${APP_FILE_REL}" "${EVID_DIR}/main.py.current.backup"

# ------------------------------------------------------------
# 1) Extrair bloco de observabilidade DO ARQUIVO ATUAL
#    (vamos re-injetar esse bloco no arquivo restaurado)
# ------------------------------------------------------------
log "Extraindo bloco de observabilidade do main.py atual"

python3 - <<'PY' "${APP_FILE_REL}" "${EVID_DIR}/observability_block.py"
import re,sys

src_path=sys.argv[1]
out_path=sys.argv[2]

data=open(src_path,'r',encoding='utf-8',errors='ignore').read().splitlines()

# Estratégia:
# - Capturar do topo até antes de "# IMPORTS INTERNOS DO PROJETO"
# - Isso inclui: docstring + imports + métricas + setup OTEL + attach + seção "TRISLA OBSERVABILITY"
# - E garante que /metrics está no bloco.
start=0
end=None
for i,line in enumerate(data):
    if line.strip() == "# IMPORTS INTERNOS DO PROJETO":
        end=i
        break

if end is None or end < 20:
    raise SystemExit("Não foi possível localizar '# IMPORTS INTERNOS DO PROJETO' no main.py atual.")

block = "\n".join(data[start:end]).rstrip() + "\n\n"
open(out_path,'w',encoding='utf-8').write(block)
print("OK: observability block lines:", end-start)
PY

if ! grep -q 'def _trisla_attach_observability' "${EVID_DIR}/observability_block.py"; then
  die "bloco de observabilidade extraído não contém _trisla_attach_observability()"
fi
if ! grep -q '@app.get("/metrics")' "${EVID_DIR}/observability_block.py"; then
  die "bloco de observabilidade extraído não contém endpoint /metrics"
fi

log "OK: bloco de observabilidade salvo em ${EVID_DIR}/observability_block.py"

# ------------------------------------------------------------
# 2) Encontrar commit "bom" onde os endpoints do Portal existiam
# ------------------------------------------------------------
log "Procurando commit anterior que contenha endpoints do Portal (via git log -S)"

# Procura por commit que contenha pelo menos um dos needles no arquivo
find_commit(){
  local needle="$1"
  # -S procura por alterações que introduzem/removem a string, mas ainda é um bom filtro
  git log --format='%H' -S"${needle}" -- "${APP_FILE_REL}" | head -n 1 || true
}

C1="$(find_commit "${NEEDLE_1}")"
C2="$(find_commit "${NEEDLE_2}")"
C3="$(find_commit "${NEEDLE_3}")"
C4="$(find_commit "${NEEDLE_4}")"

# Heurística: preferir o commit mais recente (primeiro encontrado em log)
# Como cada log retorna do mais recente para o mais antigo, pegamos o primeiro que existir.
GOOD_COMMIT=""
for c in "${C1}" "${C2}" "${C3}" "${C4}"; do
  if [[ -n "${c}" ]]; then
    GOOD_COMMIT="${c}"
    break
  fi
done

# Se não achou por -S, fazer fallback varrendo histórico procurando o conteúdo no "git show"
if [[ -z "${GOOD_COMMIT}" ]]; then
  log "Fallback: varrendo histórico do arquivo procurando needles (pode demorar)"
  GOOD_COMMIT="$(git rev-list HEAD -- "${APP_FILE_REL}" | head -n 50 | while read -r h; do
    if git show "${h}:${APP_FILE_REL}" 2>/dev/null | grep -q "${NEEDLE_1}"; then echo "${h}"; break; fi
  done)"
fi

[[ -n "${GOOD_COMMIT}" ]] || die "não foi possível encontrar commit com endpoints do Portal no histórico de ${APP_FILE_REL}"

log "Commit candidato para restauração total: ${GOOD_COMMIT}"
echo "${GOOD_COMMIT}" > "${EVID_DIR}/good_commit.txt"

# Salvar a versão do arquivo no commit bom para evidência
git show "${GOOD_COMMIT}:${APP_FILE_REL}" > "${EVID_DIR}/main.py.good_commit.raw"

# Gate: confirmar que o arquivo do commit bom contém endpoints esperados
if ! grep -q "${NEEDLE_1}" "${EVID_DIR}/main.py.good_commit.raw"; then
  die "commit candidato não contém '${NEEDLE_1}' — abortando por segurança"
fi

log "OK: commit bom validado via needle '${NEEDLE_1}'"

# ------------------------------------------------------------
# 3) Montar main.py final:
#    - topo (observability block atual) + resto (do commit bom a partir de IMPORTS INTERNOS)
# ------------------------------------------------------------
log "Gerando main.py restaurado: endpoints do commit bom + observability atual"

python3 - <<'PY' "${EVID_DIR}/observability_block.py" "${EVID_DIR}/main.py.good_commit.raw" "${EVID_DIR}/main.py.restored"
import sys

obs_path=sys.argv[1]
good_path=sys.argv[2]
out_path=sys.argv[3]

obs=open(obs_path,'r',encoding='utf-8',errors='ignore').read().rstrip()+"\n\n"
good_lines=open(good_path,'r',encoding='utf-8',errors='ignore').read().splitlines()

# Encontrar ponto de corte no "good commit": linha "# IMPORTS INTERNOS DO PROJETO"
cut=None
for i,line in enumerate(good_lines):
    if line.strip() == "# IMPORTS INTERNOS DO PROJETO":
        cut=i
        break
if cut is None:
    raise SystemExit("Não foi possível localizar '# IMPORTS INTERNOS DO PROJETO' no main.py do commit bom.")

tail="\n".join(good_lines[cut:]).lstrip()+"\n"
final=obs+tail
open(out_path,'w',encoding='utf-8').write(final)
print("OK: restored file generated. cut_line:", cut)
PY

# Gate: garantir que os endpoints voltaram no arquivo restaurado
RESTORED_TMP="${EVID_DIR}/main.py.restored"
for needle in "${NEEDLE_1}" "${NEEDLE_2}" "${NEEDLE_3}" "${NEEDLE_4}"; do
  if ! grep -q "${needle}" "${RESTORED_TMP}"; then
    die "restauração falhou: não encontrei '${needle}' no main.py restaurado"
  fi
done

# Gate: garantir que /metrics e attach observability existem
grep -q 'def _trisla_attach_observability' "${RESTORED_TMP}" || die "restauração falhou: _trisla_attach_observability ausente"
grep -q '@app.get("/metrics")' "${RESTORED_TMP}" || die "restauração falhou: endpoint /metrics ausente"

# Aplicar o arquivo restaurado
cp -a "${RESTORED_TMP}" "${APP_FILE_REL}"
log "OK: main.py restaurado aplicado em ${APP_FILE_REL}"

# ------------------------------------------------------------
# 4) Corrigir values.yaml para remover digest inválido default (evitar bomba)
# ------------------------------------------------------------
if [[ -f "${VALUES_FILE_REL}" ]]; then
  log "Auditoria do values.yaml (remover digest default inválido e tag)"
  cp -a "${VALUES_FILE_REL}" "${EVID_DIR}/values.yaml.before"

  # Regras:
  # - tag deve permanecer vazio
  # - digest default deve ser "" (pipeline injeta via --set)
  # - pullPolicy deve voltar para IfNotPresent (padrão seguro)
  # Nota: sed aplicado apenas no bloco semCsmf.image.*
  python3 - <<'PY' "${VALUES_FILE_REL}"
import sys,re
path=sys.argv[1]
txt=open(path,'r',encoding='utf-8',errors='ignore').read().splitlines()

out=[]
in_sem=False
in_image=False
sem_indent=None
img_indent=None

for line in txt:
    # detect semCsmf:
    if re.match(r'^\s*semCsmf:\s*$', line):
        in_sem=True
        sem_indent=len(line)-len(line.lstrip())
        in_image=False
        out.append(line)
        continue

    # leave semCsmf block when indentation decreases
    if in_sem:
        cur_indent=len(line)-len(line.lstrip())
        if line.strip() and cur_indent <= sem_indent:
            in_sem=False
            in_image=False

    if in_sem and re.match(r'^\s*image:\s*$', line):
        in_image=True
        img_indent=len(line)-len(line.lstrip())
        out.append(line)
        continue

    if in_image:
        cur_indent=len(line)-len(line.lstrip())
        # leave image block when indentation decreases to <= img_indent
        if line.strip() and cur_indent <= img_indent:
            in_image=False

    if in_image:
        # normalize tag/digest/pullPolicy inside semCsmf.image
        if re.match(r'^\s*tag:\s*', line):
            out.append(re.sub(r'^\s*tag:\s*.*$', '    tag: \'\'', line))
            continue
        if re.match(r'^\s*digest:\s*', line):
            out.append(re.sub(r'^\s*digest:\s*.*$', '    digest: ""', line))
            continue
        if re.match(r'^\s*pullPolicy:\s*', line):
            out.append(re.sub(r'^\s*pullPolicy:\s*.*$', '    pullPolicy: IfNotPresent', line))
            continue

    out.append(line)

open(path,'w',encoding='utf-8').write("\n".join(out)+"\n")
print("OK: values.yaml normalized for semCsmf.image defaults")
PY

  cp -a "${VALUES_FILE_REL}" "${EVID_DIR}/values.yaml.after"
  log "OK: values.yaml atualizado (defaults neutros para semCsmf.image)"
fi

# ------------------------------------------------------------
# 5) Sanity check: compilação python do sem-csmf
# ------------------------------------------------------------
log "Sanity: python compile (sem executar)"
python3 -m py_compile "${APP_FILE_REL}" && log "OK: py_compile passou" || die "py_compile falhou"

# ------------------------------------------------------------
# 6) Evidência final
# ------------------------------------------------------------
log "Gerando evidência final (diff pós-restauração)"
git diff -- "${APP_FILE_REL}" > "${EVID_DIR}/diff_after_restore_main.patch" || true
if [[ -f "${VALUES_FILE_REL}" ]]; then
  git diff -- "${VALUES_FILE_REL}" > "${EVID_DIR}/diff_after_restore_values.patch" || true
fi

log "CONCLUÍDO ✅"
log "EVIDÊNCIAS: ${EVID_DIR}"
echo "${EVID_DIR}"
