# ✅ Comandos Corrigidos para Copiar no Pod

## 🔍 Primeiro: Diagnosticar Estrutura Real

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "Pod: $POD_NAME"
echo "Container: $CONTAINER"

# Ver estrutura
echo "=== /app ==="
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -la /app | head -20

echo "=== Procurando main.py ==="
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- find /app -name "main.py" -type f

echo "=== Ver main.py (localização) ==="
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- cat /app/main.py 2>/dev/null | head -5 || \
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- cat /app/apps/api/main.py 2>/dev/null | head -5
```

---

## 📋 Possíveis Estruturas (ajustar conforme diagnóstico)

### OPÇÃO 1: Se código está em `/app/apps/api/`

```bash
# Criar diretório se não existir
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- mkdir -p /app/apps/api

# Copiar prometheus.py
kubectl cp apps/api/prometheus.py trisla/$POD_NAME:/app/apps/api/prometheus.py -c $CONTAINER

# Verificar
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/apps/api/prometheus.py
```

### OPÇÃO 2: Se código está em `/app/` (raiz)

```bash
# Copiar para raiz
kubectl cp apps/api/prometheus.py trisla/$POD_NAME:/app/prometheus.py -c $CONTAINER

# OU se estrutura é /app/api/
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- mkdir -p /app/api
kubectl cp apps/api/prometheus.py trisla/$POD_NAME:/app/api/prometheus.py -c $CONTAINER

# Verificar
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/prometheus.py || \
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/api/prometheus.py
```

---

## 🔧 Solução: Criar Arquivo Diretamente no Pod

Se `kubectl cp` não funcionar, criar o arquivo diretamente:

```bash
# Criar arquivo diretamente no pod
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- bash -c 'cat > /app/apps/api/prometheus.py << '\''PYEOF'\''
"""
TriSLA Prometheus API - Conexão direta sem Grafana
"""
from fastapi import APIRouter, HTTPException
import httpx
import os
from typing import Dict, List
from datetime import datetime

router = APIRouter(prefix="/prometheus", tags=["Prometheus"])

PROMETHEUS_URL = os.getenv(
    "PROM_URL", 
    "http://nasp-prometheus.monitoring.svc.cluster.local:9090"
).replace("/api/v1/query", "")

async def query_prometheus(query: str) -> List[Dict]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{PROMETHEUS_URL}/api/v1/query",
                params={"query": query}
            )
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                return data.get("data", {}).get("result", [])
            return []
    except Exception as e:
        print(f"Erro: {e}")
        return []

async def query_range_prometheus(query: str, start: int, end: int, step: str = "15s") -> List[Dict]:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{PROMETHEUS_URL}/api/v1/query_range",
                params={"query": query, "start": start, "end": end, "step": step}
            )
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success":
                return data.get("data", {}).get("result", [])
            return []
    except Exception as e:
        print(f"Erro: {e}")
        return []

@router.get("/health")
async def prometheus_health():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{PROMETHEUS_URL}/api/v1/status/config")
            response.raise_for_status()
            return {"status": "ok", "prometheus": "accessible"}
    except Exception as e:
        return {"status": "error", "prometheus": "unreachable", "error": str(e)}

@router.get("/metrics/slices")
async def get_slices_metrics():
    queries = {
        "total": "count(trisla_slices_active)",
        "by_type": "sum by (slice_type) (trisla_slices_active)",
        "created_total": "trisla_slices_created_total",
    }
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    return results

@router.get("/metrics/system")
async def get_system_metrics():
    queries = {
        "components_up": "up{job=~'\''trisla.*'\''}",
        "cpu_usage": "rate(container_cpu_usage_seconds_total{pod=~'\''trisla.*'\''}[5m]) * 100",
        "memory_usage": "container_memory_usage_bytes{pod=~'\''trisla.*'\''} / 1024 / 1024",
        "http_requests": "rate(http_requests_total{job=~'\''trisla.*'\''}[5m])",
    }
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    return results

@router.get("/metrics/jobs")
async def get_jobs_metrics():
    queries = {
        "completed": "trisla_jobs_completed_total",
        "failed": "trisla_jobs_failed_total",
        "active": "trisla_jobs_active_total",
    }
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    return results

@router.get("/metrics/timeseries")
async def get_timeseries_metrics(metric: str = "http_requests_total", range_minutes: int = 60, step: str = "15s"):
    end = int(datetime.now().timestamp())
    start = end - (range_minutes * 60)
    query = f"rate({metric}{{job=~'\''trisla.*'\''}}[5m])"
    results = await query_range_prometheus(query, start, end, step)
    timeseries_data = []
    for result in results:
        metric_name = result.get("metric", {}).get("job", metric)
        for value_pair in result.get("values", []):
            timeseries_data.append({
                "time": datetime.fromtimestamp(value_pair[0]).isoformat(),
                "timestamp": value_pair[0],
                "value": float(value_pair[1]),
                "metric": metric_name
            })
    return {"data": timeseries_data, "metric": metric}

@router.post("/query")
async def execute_custom_query(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query não pode ser vazia")
    results = await query_prometheus(query)
    return {"status": "success", "data": results}
PYEOF'
```

**⚠️ O comando acima é complexo. Melhor usar um script.**

---

## 🎯 Solução Recomendada: Script com Base64

```bash
# Codificar arquivo em base64 localmente
cat apps/api/prometheus.py | base64 > /tmp/prometheus_b64.txt

# No pod, decodificar
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- bash -c "
  mkdir -p /app/apps/api
  base64 -d > /app/apps/api/prometheus.py << 'EOF'
$(cat /tmp/prometheus_b64.txt)
EOF
"

# Limpar
rm /tmp/prometheus_b64.txt
```




