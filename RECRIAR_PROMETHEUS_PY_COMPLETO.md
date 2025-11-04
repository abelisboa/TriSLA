# 📝 Recriar prometheus.py Completo no node1

## ⚠️ Problema Detectado

O arquivo `prometheus.py` parece ter sido cortado durante a criação. Vamos recriá-lo completo.

---

## ✅ Execute no node1 (pasta ~/gtp5g/trisla-portal)

### Opção 1: Recriar arquivo completo (copiar e colar TODO)

```bash
# Remover arquivo incompleto se existir
rm -f apps/api/prometheus.py

# Criar arquivo completo
cat > apps/api/prometheus.py << 'PYEOF'
"""
TriSLA Prometheus API - Conexão direta sem Grafana
Coleta métricas do Prometheus e expõe via REST API para o dashboard customizado
"""
from fastapi import APIRouter, HTTPException
import httpx
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/prometheus", tags=["Prometheus"])

# URL do Prometheus NASP
PROMETHEUS_URL = os.getenv(
    "PROM_URL", 
    "http://nasp-prometheus.monitoring.svc.cluster.local:9090"
).replace("/api/v1/query", "")  # Garantir URL base

async def query_prometheus(query: str) -> List[Dict]:
    """Executa query PromQL no Prometheus"""
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
            else:
                return []
    except Exception as e:
        print(f"Erro ao query Prometheus: {e}")
        return []

async def query_range_prometheus(query: str, start: int, end: int, step: str = "15s") -> List[Dict]:
    """Executa query range no Prometheus (para gráficos)"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{PROMETHEUS_URL}/api/v1/query_range",
                params={
                    "query": query,
                    "start": start,
                    "end": end,
                    "step": step
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                return data.get("data", {}).get("result", [])
            else:
                return []
    except Exception as e:
        print(f"Erro ao query range Prometheus: {e}")
        return []

@router.get("/health")
async def prometheus_health():
    """Verifica se Prometheus está acessível"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{PROMETHEUS_URL}/api/v1/status/config")
            response.raise_for_status()
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
        "latency": "avg by (slice_type) (trisla_slice_latency_ms)",
        "bandwidth": "avg by (slice_type) (trisla_slice_bandwidth_mbps)",
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
        "latency_p95": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=~'trisla.*'}[5m]))",
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
        "rate": "rate(trisla_jobs_completed_total[5m])",
    }
    
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    
    return results

@router.get("/metrics/timeseries")
async def get_timeseries_metrics(
    metric: str = "http_requests_total",
    range_minutes: int = 60,
    step: str = "15s"
):
    """Retorna série temporal de uma métrica para gráficos"""
    end = int(datetime.now().timestamp())
    start = end - (range_minutes * 60)
    
    query = f"rate({metric}{{job=~'trisla.*'}}[5m])"
    
    results = await query_range_prometheus(query, start, end, step)
    
    # Transformar para formato de gráfico
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

@router.get("/metrics/decision-engine")
async def get_decision_engine_metrics():
    """Métricas do Decision Engine"""
    queries = {
        "predictions": "rate(decision_engine_predictions_total[5m])",
        "accepted": "rate(decision_engine_decisions_accepted_total[5m])",
        "rejected": "rate(decision_engine_decisions_rejected_total[5m])",
        "latency": "decision_engine_latency_ms",
    }
    
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    
    return results

@router.get("/metrics/nwdaf")
async def get_nwdaf_metrics():
    """Métricas do NWDAF"""
    queries = {
        "performance_score": "nwdaf_network_performance_score",
        "qos_predictions": "rate(nwdaf_qos_predictions_total[5m])",
        "network_quality": "nwdaf_network_quality_score",
    }
    
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    
    return results

@router.get("/metrics/sla")
async def get_sla_metrics():
    """Métricas de SLA"""
    queries = {
        "agents_active": "sla_agents_active",
        "violations": "sla_violations_total",
        "compliance_rate": "sla_compliance_rate",
    }
    
    results = {}
    for key, query in queries.items():
        results[key] = await query_prometheus(query)
    
    return results

@router.post("/query")
async def execute_custom_query(query: str):
    """Executa query PromQL customizada"""
    if not query:
        raise HTTPException(status_code=400, detail="Query não pode ser vazia")
    
    results = await query_prometheus(query)
    return {"status": "success", "data": results}
PYEOF

echo "✅ Arquivo prometheus.py criado completo"
```

---

## ✅ Verificar e Reiniciar API

```bash
# Verificar tamanho do arquivo
wc -l apps/api/prometheus.py
# Deve ter mais de 200 linhas

# Verificar se API está rodando
ps aux | grep -i "uvicorn\|fastapi\|trisla.*api" | grep -v grep

# Se não estiver, iniciar/reiniciar
# Depende de como está rodando (Docker, systemd, manual, etc.)

# Testar após reiniciar
sleep 5
curl http://localhost:8000/prometheus/health
```

---

## 🔧 Se API não está rodando

Dependendo de como o TriSLA Portal está rodando:

```bash
# Se Docker Compose:
cd ~/gtp5g/trisla-portal
docker compose restart api

# Se Kubernetes:
kubectl rollout restart deployment/trisla-portal-api -n trisla

# Se manual (uvicorn):
pkill -f "uvicorn.*main:app"
cd apps/api && uvicorn main:app --host 0.0.0.0 --port 8000 &
```




