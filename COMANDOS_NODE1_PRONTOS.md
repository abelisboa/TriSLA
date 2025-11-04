# 🚀 Comandos Prontos para Executar no node1

## 📍 Você está em: `~/gtp5g/trisla-portal`

---

## ✅ PASSO 1: Criar prometheus.py (Backend API)

Execute este comando completo (copie e cole tudo):

```bash
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
```

---

## ✅ PASSO 2: Verificar/Atualizar main.py

```bash
# Verificar se router já está integrado
if grep -q "prometheus_router" apps/api/main.py; then
    echo "✅ Router Prometheus já está no main.py"
else
    echo "📝 Adicionando router ao main.py..."
    cat >> apps/api/main.py << 'MAINEOF'

# ------------------------------------------------------------
# Prometheus router (dashboard customizado - sem Grafana)
# ------------------------------------------------------------
try:
    from prometheus import router as prometheus_router  # type: ignore

    app.include_router(prometheus_router)
    log.info("Prometheus router habilitado em /prometheus")
except Exception as e:
    log.warning("Prometheus router não carregado: %s", e)
MAINEOF
    echo "✅ Router adicionado"
fi
```

---

## ✅ PASSO 3: Testar API

```bash
# Instalar httpx se necessário (pode precisar estar no ambiente virtual)
pip install httpx 2>/dev/null || python3 -m pip install httpx

# Testar API
echo "Testando API Prometheus..."
curl -s http://localhost:8000/prometheus/health | jq . || curl -s http://localhost:8000/prometheus/health
```

---

## ⚠️ PASSO 4: Arquivos JSX (Frontend)

Os arquivos JSX são muito grandes para heredoc. **Opções:**

### Opção A: Criar arquivos JSX simplificados primeiro

Vou criar versões simplificadas que podem ser expandidas depois:

```bash
# Criar DashboardComplete.jsx (versão simplificada)
mkdir -p apps/ui/src/pages
cat > apps/ui/src/pages/DashboardComplete.jsx << 'JSEOF'
import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

export default function DashboardComplete() {
  const [metrics, setMetrics] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const slices = await fetch(`${API_URL}/prometheus/metrics/slices`).then(r => r.json())
        const system = await fetch(`${API_URL}/prometheus/metrics/system`).then(r => r.json())
        setMetrics({ slices, system })
        setLoading(false)
      } catch (error) {
        console.error("Erro:", error)
        setLoading(false)
      }
    }
    fetchMetrics()
    const interval = setInterval(fetchMetrics, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading) return <div className="p-6">Carregando...</div>

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">TriSLA Dashboard</h1>
      <div className="grid grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-gray-600">Slices Ativos</div>
          <div className="text-3xl font-bold">{metrics.slices?.total?.[0]?.value?.[1] || 0}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600">Componentes</div>
          <div className="text-3xl font-bold">
            {metrics.system?.components_up?.filter(c => c.value?.[1] === "1").length || 0}
          </div>
        </Card>
      </div>
      <Card className="p-4">
        <pre>{JSON.stringify(metrics, null, 2)}</pre>
      </Card>
    </div>
  )
}
JSEOF
```

### Opção B: Copiar arquivos completos depois via Git ou outro método

---

## ✅ PASSO 5: Verificar App.jsx (se rotas estão lá)

```bash
# Verificar se rotas estão no App.jsx
if grep -q "DashboardComplete" apps/ui/src/App.jsx; then
    echo "✅ Rotas já estão no App.jsx"
else
    echo "⚠️  Precisa adicionar rotas no App.jsx"
    echo "   Adicione:"
    echo "   import DashboardComplete from './pages/DashboardComplete'"
    echo "   <Route path=\"/dashboard-complete\" element={<DashboardComplete />} />"
fi
```

---

## 🎯 Ordem de Execução Recomendada

1. ✅ Criar `prometheus.py` (PASSO 1)
2. ✅ Verificar/atualizar `main.py` (PASSO 2)
3. ✅ Testar API (PASSO 3)
4. ⚠️ Criar JSX simplificados (PASSO 4) - ou copiar depois
5. ⚠️ Verificar/atualizar `App.jsx` (PASSO 5)

---

**Execute os comandos acima no node1, na ordem indicada!**




