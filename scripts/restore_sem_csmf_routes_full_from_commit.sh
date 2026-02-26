#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-/home/porvir5g/gtp5g/trisla}"
APP_FILE="apps/sem-csmf/src/main.py"
GOOD_COMMIT_DEFAULT="1677b94b986bfc084a79f27bac226a82b5a55155"

GOOD_COMMIT="${GOOD_COMMIT:-$GOOD_COMMIT_DEFAULT}"

TS_UTC="$(date -u +%Y%m%dT%H%M%SZ)"
EVID="${ROOT}/evidencias_restore_sem_csmf_routes_${TS_UTC}"
mkdir -p "$EVID"

log(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }
die(){ echo "FATAL: $*" >&2; exit 1; }

need(){ command -v "$1" >/dev/null 2>&1 || die "comando ausente: $1"; }
need git
need python3
need awk
need sed
need grep

cd "$ROOT" || die "não foi possível acessar $ROOT"

[[ -f "$APP_FILE" ]] || die "arquivo não encontrado: $APP_FILE"

log "EVIDENCIA: $EVID"
git status --porcelain > "$EVID/git_status_porcelain.txt" || true
git diff > "$EVID/git_diff_full.patch" || true
cp -a "$APP_FILE" "$EVID/main.py.before.backup"

# ------------------------------------------------------------
# 1) Extrair seção de rotas do commit bom:
#    do '@app.post("/api/v1/interpret")' até EOF
# ------------------------------------------------------------
log "Extraindo rotas do commit bom: $GOOD_COMMIT"

git show "${GOOD_COMMIT}:${APP_FILE}" > "$EVID/main.py.good_commit.raw" \
  || die "falha ao ler ${APP_FILE} no commit ${GOOD_COMMIT}"

python3 - <<'PY' "$EVID/main.py.good_commit.raw" "$EVID/routes_from_commit.py"
import sys,re
src=sys.argv[1]
out=sys.argv[2]
data=open(src,'r',encoding='utf-8',errors='ignore').read().splitlines()

start=None
for i,line in enumerate(data):
    if re.match(r'^\s*@app\.post\("/api/v1/interpret"\)\s*$', line):
        start=i
        break

if start is None:
    raise SystemExit("Não encontrei '@app.post(\"/api/v1/interpret\")' no commit bom.")

block="\n".join(data[start:]).rstrip()+"\n"
open(out,'w',encoding='utf-8').write(block)

# Gates mínimos: confirmar rotas críticas do Portal
must = [
  '/api/v1/intents',
  '/api/v1/intents/register',
  '/api/v1/slices',
  '/api/v1/nests'
]
missing=[m for m in must if m not in block]
if missing:
    raise SystemExit("Rotas críticas ausentes no bloco do commit: " + ", ".join(missing))

print("OK: rotas extraídas a partir da linha", start, "com tamanho", len(block.splitlines()), "linhas")
PY

log "OK: rotas do commit salvas em $EVID/routes_from_commit.py"

# ------------------------------------------------------------
# 2) Substituir no arquivo atual tudo a partir de '/interpret' até EOF
#    mantendo observability/boot/middlewares atuais
# ------------------------------------------------------------
log "Aplicando substituição no main.py atual (a partir de /api/v1/interpret)"

python3 - <<'PY' "$APP_FILE" "$EVID/routes_from_commit.py" "$EVID/main.py.after"
import sys,re
cur_path=sys.argv[1]
routes_path=sys.argv[2]
out_path=sys.argv[3]

cur=open(cur_path,'r',encoding='utf-8',errors='ignore').read().splitlines()
routes=open(routes_path,'r',encoding='utf-8',errors='ignore').read().splitlines()

# localizar primeiro @app.post("/api/v1/interpret") no arquivo atual
cut=None
for i,line in enumerate(cur):
    if re.match(r'^\s*@app\.post\("/api/v1/interpret"\)\s*$', line):
        cut=i
        break

if cut is None:
    raise SystemExit("Não encontrei '@app.post(\"/api/v1/interpret\")' no main.py atual.")

# manter tudo antes do cut e anexar rotas do commit
final = cur[:cut] + routes
open(out_path,'w',encoding='utf-8').write("\n".join(final).rstrip()+"\n")
print("OK: arquivo final gerado. cut:", cut, "final_lines:", len(final))
PY

cp -a "$EVID/main.py.after" "$APP_FILE"

# ------------------------------------------------------------
# 3) Gates: confirmar rotas críticas e compilação
# ------------------------------------------------------------
log "Gates: verificando presença das rotas críticas no main.py final"

grep -q '/api/v1/intents/register' "$APP_FILE" || die "rota /api/v1/intents/register não está no main.py final"
grep -q '/api/v1/intents' "$APP_FILE" || die "rota /api/v1/intents não está no main.py final"
grep -q '/api/v1/slices' "$APP_FILE" || die "rota /api/v1/slices não está no main.py final"
grep -q '/api/v1/nests' "$APP_FILE" || die "rota /api/v1/nests não está no main.py final"

log "OK: rotas presentes"

log "Gate: py_compile"
python3 -m py_compile "$APP_FILE" || die "py_compile falhou"

log "OK: py_compile passou"

# evidência final
git diff -- "$APP_FILE" > "$EVID/diff_main_after.patch" || true

log "CONCLUÍDO ✅"
log "EVIDÊNCIAS: $EVID"
echo "$EVID"
