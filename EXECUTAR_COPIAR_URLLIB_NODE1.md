# ✅ Criar prometheus.py com urllib no node1

## 🎯 Execute Este Comando Completo

```bash
cd ~/gtp5g/trisla-portal

POD_NAME=$(kubectl get pods -n trisla | grep portal | head -1 | awk '{print $1}')
CONTAINER=$(kubectl get pod $POD_NAME -n trisla -o jsonpath='{.spec.containers[0].name}')

echo "📦 Criando prometheus.py com urllib diretamente..."

kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 << 'PYEOF'
content = '''"""
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
    """Métricas de slices ativos"""
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
    """Métricas do sistema TriSLA"""
    queries = {
        "components_up": "up{job=~'trisla.*'}",
        "cpu_usage": "rate(container_cpu_usage_seconds_total{pod=~'trisla.*'}[5m]) * 100",
        "memory_usage": "container_memory_usage_bytes{pod=~'trisla.*'} / 1024 / 1024",
        "http_requests": "rate(http_requests_total{job=~'trisla.*'}[5m])",
    }
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    return results

@router.get("/metrics/jobs")
async def get_jobs_metrics():
    """Métricas de jobs"""
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
    """Retorna série temporal de uma métrica para gráficos"""
    end = int(datetime.now().timestamp())
    start = end - (range_minutes * 60)
    query = f"rate({metric}{{job=~'trisla.*'}}[5m])"
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
    """Executa query PromQL customizada"""
    if not query:
        raise HTTPException(status_code=400, detail="Query não pode ser vazia")
    results = await query_prometheus(query)
    return {"status": "success", "data": results}
'''

with open('/app/prometheus.py', 'w') as f:
    f.write(content)

print(f"✅ prometheus.py criado: {len(content)} bytes")
PYEOF

# Verificar
echo ""
echo "🔍 Verificando..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- ls -lh /app/prometheus.py
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- head -15 /app/prometheus.py

# Testar import
echo ""
echo "🧪 Testando import..."
kubectl exec -n trisla $POD_NAME -c $CONTAINER -- python3 -c "
import sys
sys.path.insert(0, '/app')
try:
    from prometheus import router
    print('✅ Import OK!')
    print(f'Router prefix: {router.prefix}')
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "⚠️ IMPORTANTE: Reiniciar deployment para carregar router!"
echo "   kubectl rollout restart deployment/trisla-portal -n trisla"
echo "   (Mas isso vai perder os arquivos - precisamos rebuild imagem depois)"
```




