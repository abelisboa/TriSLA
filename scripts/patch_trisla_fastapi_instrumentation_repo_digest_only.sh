#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/porvir5g/gtp5g/trisla"
APPS="$ROOT/apps"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
EVID="$ROOT/evidencias_trisla_fastapi_repo_patch_$TS"
mkdir -p "$EVID"

log(){ echo "[$(date -u +%H:%M:%SZ)] $*"; }

log "ROOT=$ROOT"
log "APPS=$APPS"
log "EVID=$EVID"

if [[ ! -d "$APPS" ]]; then
  echo "FATAL: apps/ não existe em $APPS" | tee "$EVID/FATAL.txt"
  exit 1
fi

# Descoberta de serviços FastAPI sem rg:
# Critério: presença de "from fastapi import FastAPI" ou "FastAPI(" em .py dentro de apps/<service>/
log "[SCAN] Descobrindo serviços FastAPI em apps/* ..."
python3 - <<'PY' "$APPS" "$EVID/fastapi_services.txt"
import os,sys,re
apps=sys.argv[1]
out=sys.argv[2]
pat=re.compile(r'\bfrom\s+fastapi\s+import\s+FastAPI\b|\bFastAPI\s*\(')
services=[]
for s in sorted(os.listdir(apps)):
    sp=os.path.join(apps,s)
    if not os.path.isdir(sp): 
        continue
    hit=False
    for root,_,files in os.walk(sp):
        for fn in files:
            if fn.endswith(".py"):
                p=os.path.join(root,fn)
                try:
                    data=open(p,"r",encoding="utf-8",errors="ignore").read()
                except Exception:
                    continue
                if pat.search(data):
                    hit=True
                    break
        if hit: break
    if hit:
        services.append(s)
open(out,"w").write("\n".join(services)+("\n" if services else ""))
print("FOUND:", len(services))
for s in services: print(" -", s)
PY

if [[ ! -s "$EVID/fastapi_services.txt" ]]; then
  log "Nenhum serviço FastAPI detectado. Nada a fazer."
  exit 0
fi

log "[PATCH] Aplicando instrumentação Prometheus + OTEL em todos os serviços detectados..."
log "Lista: $(tr '\n' ' ' < "$EVID/fastapi_services.txt")"

# Função python para patch idempotente em cada serviço:
# - adiciona deps no requirements.txt (ou cria se não existir)
# - injeta código em um "entrypoint" FastAPI (tenta main.py / app.py / server.py / __init__.py)
# - se não achar arquivo alvo, registra como SKIP
python3 - <<'PY' "$APPS" "$EVID"
import os,sys,re,datetime

apps=sys.argv[1]
evid=sys.argv[2]
services_path=os.path.join(evid,"fastapi_services.txt")
services=open(services_path,"r").read().strip().splitlines()

deps=[
  "opentelemetry-api==1.25.0",
  "opentelemetry-sdk==1.25.0",
  "opentelemetry-exporter-otlp==1.25.0",
  "opentelemetry-instrumentation==0.46b0",
  "opentelemetry-instrumentation-fastapi==0.46b0",
  "opentelemetry-instrumentation-asgi==0.46b0",
  "opentelemetry-instrumentation-logging==0.46b0",
  "prometheus-client==0.20.0",
]

# Instrumentação aplicada (idempotente). Evita dependências de terceiros adicionais.
INJECT_MARK_BEGIN = "# === TRISLA_OBSERVABILITY_BEGIN ==="
INJECT_MARK_END   = "# === TRISLA_OBSERVABILITY_END ==="

inject_block = f"""{INJECT_MARK_BEGIN}
import os
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.requests import Request
from starlette.responses import Response

# --- Prometheus primitives ---
TRISLA_HTTP_REQUESTS_TOTAL = Counter(
    "trisla_http_requests_total",
    "Total de requisições HTTP por serviço e rota",
    ["service", "method", "path", "status"]
)
TRISLA_HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "trisla_http_request_duration_seconds",
    "Duração de requisições HTTP em segundos por serviço e rota",
    ["service", "method", "path"]
)
TRISLA_PROCESS_CPU_SECONDS_TOTAL = Gauge(
    "trisla_process_cpu_seconds_total",
    "CPU seconds (aprox) exposto via OTEL/Runtime; placeholder gauge para padronização",
    ["service"]
)

# --- OTEL setup (OTLP -> Collector) ---
def _trisla_setup_otel(service_name: str):
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://trisla-otel-collector.trisla.svc.cluster.local:4317")
        insecure = os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true"

        resource = Resource.create({{"service.name": service_name}})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=endpoint, insecure=insecure)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        return FastAPIInstrumentor
    except Exception:
        return None

def _trisla_attach_observability(app: FastAPI, service_name: str):
    # Prometheus middleware + endpoint
    @app.middleware("http")
    async def _trisla_prom_mw(request: Request, call_next):
        method = request.method
        path = request.url.path
        with TRISLA_HTTP_REQUEST_DURATION_SECONDS.labels(service=service_name, method=method, path=path).time():
            response = await call_next(request)
        TRISLA_HTTP_REQUESTS_TOTAL.labels(service=service_name, method=method, path=path, status=str(response.status_code)).inc()
        return response

    @app.get("/metrics")
    async def _metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    # OTEL instrument app (traces)
    instr = _trisla_setup_otel(service_name)
    if instr is not None:
        try:
            instr.instrument_app(app)
        except Exception:
            pass

{INJECT_MARK_END}
"""

def ensure_requirements(service_dir:str, report:list):
    req=os.path.join(service_dir,"requirements.txt")
    if not os.path.exists(req):
        open(req,"w").write("\n".join(deps)+"\n")
        report.append(("REQ_CREATE", req))
        return
    data=open(req,"r",encoding="utf-8",errors="ignore").read().splitlines()
    have=set([x.strip() for x in data if x.strip() and not x.strip().startswith("#")])
    changed=False
    for d in deps:
        if d not in have:
            data.append(d)
            changed=True
    if changed:
        open(req,"w").write("\n".join(data).rstrip()+"\n")
        report.append(("REQ_UPDATE", req))
    else:
        report.append(("REQ_OK", req))

def pick_target_py(service_dir:str):
    # Preferências comuns (ajuste conservador)
    cand=[
        "main.py","app.py","server.py",
        os.path.join("src","main.py"),
        os.path.join("src","app.py"),
        os.path.join("src","server.py"),
        os.path.join("app","main.py"),
        os.path.join("app","app.py"),
        os.path.join("app","server.py"),
        "__init__.py",
    ]
    for c in cand:
        p=os.path.join(service_dir,c)
        if os.path.exists(p) and os.path.isfile(p):
            return p
    # fallback: primeiro .py que contenha FastAPI(
    pat=re.compile(r"\bFastAPI\s*\(")
    for root,_,files in os.walk(service_dir):
        for fn in files:
            if fn.endswith(".py"):
                p=os.path.join(root,fn)
                try:
                    txt=open(p,"r",encoding="utf-8",errors="ignore").read()
                except Exception:
                    continue
                if pat.search(txt):
                    return p
    return None

def patch_python_file(pyfile:str, service_name:str, report:list):
    txt=open(pyfile,"r",encoding="utf-8",errors="ignore").read()
    if INJECT_MARK_BEGIN in txt and INJECT_MARK_END in txt:
        report.append(("PY_ALREADY", pyfile))
        return

    # Inserir bloco após imports iniciais (heurística segura)
    lines=txt.splitlines()
    insert_at=0
    # pula shebang/encoding e blocos de import
    for i,l in enumerate(lines[:200]):
        if l.startswith("import ") or l.startswith("from "):
            insert_at=i+1
        elif l.strip()=="":
            continue
        elif l.startswith("#!") or "coding" in l:
            continue
        else:
            # primeiro conteúdo não-import: insere aqui
            if insert_at==0:
                insert_at=i
            break

    lines = lines[:insert_at] + ["", inject_block.rstrip(), ""] + lines[insert_at:]
    txt2="\n".join(lines).rstrip()+"\n"

    # Agora anexar chamada _trisla_attach_observability(app, service) após criação do app
    # Procura "app = FastAPI(" ou "app=FastAPI("
    pat=re.compile(r"^\s*app\s*=\s*FastAPI\s*\(", re.M)
    m=pat.search(txt2)
    if m:
        # inserir chamada logo depois da linha do app = FastAPI(...)
        parts=txt2.splitlines()
        idx=0
        for i,l in enumerate(parts):
            if re.match(r"^\s*app\s*=\s*FastAPI\s*\(", l):
                idx=i
                break
        call = f'_trisla_attach_observability(app, os.getenv("TRISLA_SERVICE_NAME", "{service_name}"))'
        # evita duplicar
        if call not in txt2:
            parts.insert(idx+1, call)
            txt2="\n".join(parts).rstrip()+"\n"
            report.append(("PY_ATTACH", pyfile))
    else:
        report.append(("PY_WARN_NOAPP", pyfile))

    open(pyfile,"w").write(txt2)
    report.append(("PY_PATCHED", pyfile))

report=[]
skips=[]
for s in services:
    sd=os.path.join(apps,s)
    if not os.path.isdir(sd):
        skips.append((s,"NO_DIR"))
        continue
    ensure_requirements(sd, report)
    target=pick_target_py(sd)
    if not target:
        skips.append((s,"NO_PY_TARGET"))
        continue
    patch_python_file(target, s, report)

# salvar relatório
with open(os.path.join(evid,"repo_patch_report.tsv"),"w") as f:
    for a,b in report:
        f.write(f"{a}\t{b}\n")
with open(os.path.join(evid,"repo_patch_skips.tsv"),"w") as f:
    for s,why in skips:
        f.write(f"{s}\t{why}\n")

print("PATCH_REPORT:", len(report))
print("SKIPS:", len(skips))
PY

log "[OK] Patch aplicado. Evidência:"
ls -la "$EVID" | tee "$EVID/ls_evid.txt" >/dev/null

log "Arquivo(s) gerados:"
echo " - $EVID/fastapi_services.txt"
echo " - $EVID/repo_patch_report.tsv"
echo " - $EVID/repo_patch_skips.tsv"
