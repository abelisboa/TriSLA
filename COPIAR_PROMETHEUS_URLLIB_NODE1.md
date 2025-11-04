# ✅ Copiar prometheus.py com urllib (sem httpx)

## 🎯 Solução

Criar versão que usa `urllib.request` (built-in do Python) em vez de `httpx`.

---

## 📋 Execute no node1

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

# Copiar versão com urllib
PROM_URLLIB='"""
TriSLA Prometheus API - Conexão direta sem Grafana
Usa urllib.request (built-in) em vez de httpx
"""
from fastapi import APIRouter, HTTPException
import urllib.request
import urllib.parse
import json
import os
import asyncio
from typing import Dict, List
from datetime import datetime

router = APIRouter(prefix="/prometheus", tags=["Prometheus"])

PROMETHEUS_URL = os.getenv(
    "PROM_URL", 
    "http://nasp-prometheus.monitoring.svc.cluster.local:9090"
).replace("/api/v1/query", "")

def _query_prometheus_sync(query: str, endpoint: str = "query") -> List[Dict]:
    """Versão síncrona usando urllib"""
    try:
        url = f"{PROMETHEUS_URL}/api/v1/{endpoint}"
        
        if endpoint == "query":
            params = {"query": query}
            url += "?" + urllib.parse.urlencode(params)
        else:
            params = query
            url += "?" + urllib.parse.urlencode(params)
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "success":
                return data.get("data", {}).get("result", [])
            return []
    except Exception as e:
        print(f"Erro ao query Prometheus: {e}")
        return []

async def query_prometheus(query: str) -> List[Dict]:
    """Executa query PromQL no Prometheus"""
    return await asyncio.to_thread(_query_prometheus_sync, query, "query")

async def query_range_prometheus(query: str, start: int, end: int, step: str = "15s") -> List[Dict]:
    """Executa query range no Prometheus"""
    params = {"query": query, "start": start, "end": end, "step": step}
    return await asyncio.to_thread(_query_prometheus_sync, params, "query_range")

@router.get("/health")
async def prometheus_health():
    """Verifica se Prometheus está acessível"""
    try:
        url = f"{PROMETHEUS_URL}/api/v1/status/config"
        req = urllib.request.Request(url)
        result = await asyncio.to_thread(
            lambda: urllib.request.urlopen(req, timeout=5).read().decode()
        )
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
'

# Criar arquivo local temporário
echo "$PROM_URLLIB" > /tmp/prometheus_urllib.py

# Copiar usando base64
PROM_B64=$(cat /tmp/prometheus_urllib.py | base64 -w 0)
cat > /tmp/copy_prom.py << 'PYEOF'
import sys, base64
b64_data = sys.stdin.read().strip()
content = base64.b64decode(b64_data).decode('utf-8')
with open('/app/prometheus.py', 'w') as f:
    f.write(content)
print(f"✅ prometheus.py (urllib): {len(content)} bytes")
PYEOF

kubectl cp /tmp/copy_prom.py trisla/$POD_NAME:/tmp/copy_prom.py -c $CONTAINER
echo "$PROM_B64" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_prom.py

# Limpar
rm /tmp/prometheus_urllib.py /tmp/copy_prom.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- rm /tmp/copy_prom.py 2>/dev/null

# Verificar
echo ""
echo "Verificando..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- head -5 /app/prometheus.py

# Testar import
echo ""
echo "Testando import..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "
import sys
sys.path.insert(0, '/app')
try:
    from prometheus import router
    print('✅ Import OK')
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

---

## Ou use o arquivo local criado

Se você já tiver o arquivo `prometheus_urllib.py` local:

```bash
PROM_B64=$(cat apps/api/prometheus_urllib.py | base64 -w 0)
cat > /tmp/copy_prom.py << 'PYEOF'
import sys, base64
b64_data = sys.stdin.read().strip()
content = base64.b64decode(b64_data).decode('utf-8')
with open('/app/prometheus.py', 'w') as f:
    f.write(content)
print(f"✅ Criado: {len(content)} bytes")
PYEOF

kubectl cp /tmp/copy_prom.py trisla/$POD_NAME:/tmp/copy_prom.py -c $CONTAINER
echo "$PROM_B64" | kubectl exec -i -n trisla $POD_NAME -c $CONTAINER -- python3 /tmp/copy_prom.py
rm /tmp/copy_prom.py
```




