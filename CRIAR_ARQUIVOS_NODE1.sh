#!/bin/bash
# Script para criar arquivos diretamente no node1
# Execute este script no node1, já na pasta ~/gtp5g/trisla-portal

set -e

echo "=========================================="
echo "📝 Criando Arquivos Dashboard Customizado"
echo "=========================================="
echo ""

# Verificar se está na pasta correta
if [ ! -d "apps/api" ]; then
    echo "❌ Execute este script da pasta ~/gtp5g/trisla-portal"
    exit 1
fi

# Criar diretórios
mkdir -p apps/api
mkdir -p apps/ui/src/pages

echo "✅ Diretórios criados"
echo ""

echo "📝 Criando arquivos..."
echo ""

# Arquivo 1: prometheus.py
echo "1️⃣ Criando: apps/api/prometheus.py"
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

echo "   ✅ prometheus.py criado"
echo ""

# Arquivo 2: DashboardComplete.jsx (vou criar uma versão resumida, depois pode ser expandida)
echo "2️⃣ Criando: apps/ui/src/pages/DashboardComplete.jsx"
cat > apps/ui/src/pages/DashboardComplete.jsx << 'JSEOF'
/**
 * TriSLA Dashboard Completo - Customizado e Integrado
 * Conecta diretamente ao Prometheus via API do TriSLA Portal
 * Sem necessidade de Grafana ou login separado
 */
import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer 
} from "recharts"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#2f9e44', '#ff5555']

export default function DashboardComplete() {
  const [loading, setLoading] = useState(true)
  const [slicesMetrics, setSlicesMetrics] = useState({})
  const [systemMetrics, setSystemMetrics] = useState({})
  const [jobsMetrics, setJobsMetrics] = useState({})
  const [timeseriesData, setTimeseriesData] = useState([])
  const [refreshInterval, setRefreshInterval] = useState(10)

  const fetchAllMetrics = async () => {
    try {
      const slicesRes = await fetch(`${API_URL}/prometheus/metrics/slices`)
      const slices = await slicesRes.json()
      setSlicesMetrics(slices)

      const systemRes = await fetch(`${API_URL}/prometheus/metrics/system`)
      const system = await systemRes.json()
      setSystemMetrics(system)

      const jobsRes = await fetch(`${API_URL}/prometheus/metrics/jobs`)
      const jobs = await jobsRes.json()
      setJobsMetrics(jobs)

      const tsRes = await fetch(`${API_URL}/prometheus/metrics/timeseries?metric=http_requests_total&range_minutes=60`)
      const ts = await tsRes.json()
      setTimeseriesData(ts.data || [])

      setLoading(false)
    } catch (error) {
      console.error("Erro ao buscar métricas:", error)
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAllMetrics()
    const interval = setInterval(fetchAllMetrics, refreshInterval * 1000)
    return () => clearInterval(interval)
  }, [refreshInterval])

  const slicesByType = slicesMetrics.by_type?.map(item => ({
    name: item.metric?.slice_type || "Unknown",
    value: parseFloat(item.value?.[1] || 0)
  })) || []

  const componentsUp = systemMetrics.components_up?.map(item => ({
    name: item.metric?.job || "Unknown",
    status: item.value?.[1] === "1" ? "Up" : "Down",
    value: parseFloat(item.value?.[1] || 0)
  })) || []

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Carregando métricas...</div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">TriSLA Dashboard</h1>
          <p className="text-gray-600">Monitoramento em tempo real • Conectado ao Prometheus</p>
        </div>
        <div className="flex items-center space-x-4">
          <label className="text-sm text-gray-600">
            Refresh:
            <select 
              value={refreshInterval} 
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="ml-2 px-2 py-1 border rounded"
            >
              <option value={5}>5s</option>
              <option value={10}>10s</option>
              <option value={30}>30s</option>
              <option value={60}>1min</option>
            </select>
          </label>
          <button 
            onClick={fetchAllMetrics}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Atualizar
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-gray-600">Slices Ativos</div>
          <div className="text-3xl font-bold text-blue-600">
            {slicesMetrics.total?.[0]?.value?.[1] || 0}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600">Jobs Completados</div>
          <div className="text-3xl font-bold text-green-600">
            {jobsMetrics.completed?.[0]?.value?.[1] || 0}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600">Componentes Online</div>
          <div className="text-3xl font-bold text-purple-600">
            {componentsUp.filter(c => c.value === 1).length}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-gray-600">Taxa de Sucesso</div>
          <div className="text-3xl font-bold text-orange-600">
            {(() => {
              const completed = parseFloat(jobsMetrics.completed?.[0]?.value?.[1] || 0)
              const failed = parseFloat(jobsMetrics.failed?.[0]?.value?.[1] || 0)
              const total = completed + failed
              return total > 0 ? ((completed / total) * 100).toFixed(1) : 0
            })}%
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-4">
          <h3 className="text-xl font-semibold mb-4">Slices por Tipo</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={slicesByType}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {slicesByType.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-4">
          <h3 className="text-xl font-semibold mb-4">Status dos Componentes</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={componentsUp}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-4 lg:col-span-2">
          <h3 className="text-xl font-semibold mb-4">HTTP Requests (últimas 60 min)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeseriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time" 
                tickFormatter={(time) => new Date(time).toLocaleTimeString()}
              />
              <YAxis />
              <Tooltip 
                labelFormatter={(time) => new Date(time).toLocaleString()}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#8884d8" 
                name="Requests/sec"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card className="p-4">
        <h3 className="text-xl font-semibold mb-4">Componentes TriSLA</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-2 text-left">Componente</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-left">Valor</th>
              </tr>
            </thead>
            <tbody>
              {componentsUp.map((comp, idx) => (
                <tr key={idx} className="border-b">
                  <td className="px-4 py-2">{comp.name}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-1 rounded ${
                      comp.value === 1 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {comp.status}
                    </span>
                  </td>
                  <td className="px-4 py-2">{comp.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
JSEOF

echo "   ✅ DashboardComplete.jsx criado"
echo ""

# Arquivo 3: SlicesManagement.jsx (versão resumida)
echo "3️⃣ Criando: apps/ui/src/pages/SlicesManagement.jsx"
cat > apps/ui/src/pages/SlicesManagement.jsx << 'JSEOF'
/**
 * Gestão de Slices - Dashboard Integrado
 * Criação de slices via LNP e Templates
 */
import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts"

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"

export default function SlicesManagement() {
  const [slices, setSlices] = useState([])
  const [loading, setLoading] = useState(false)
  const [sliceForm, setSliceForm] = useState({
    slice_type: "URLLC",
    bandwidth: 100,
    latency: 1,
    description: ""
  })
  const [lnpForm, setLnpForm] = useState({ description: "" })

  const fetchSlices = async () => {
    try {
      const res = await fetch(`${API_URL}/prometheus/metrics/slices`)
      const data = await res.json()
      setSlices(data.by_type || [])
    } catch (error) {
      console.error("Erro ao buscar slices:", error)
    }
  }

  useEffect(() => {
    fetchSlices()
    const interval = setInterval(fetchSlices, 10000)
    return () => clearInterval(interval)
  }, [])

  const createSlice = async (data) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/api/v1/slices`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      })
      const result = await res.json()
      alert(result.message || "Slice criado com sucesso!")
      setSliceForm({ slice_type: "URLLC", bandwidth: 100, latency: 1, description: "" })
      setLnpForm({ description: "" })
      fetchSlices()
    } catch (error) {
      alert("Erro ao criar slice: " + error.message)
    } finally {
      setLoading(false)
    }
  }

  const handleTemplateSubmit = (e) => {
    e.preventDefault()
    createSlice(sliceForm)
  }

  const handleLnpSubmit = (e) => {
    e.preventDefault()
    createSlice({ description: lnpForm.description })
  }

  const slicesData = slices.map(item => ({
    name: item.metric?.slice_type || "Unknown",
    value: parseFloat(item.value?.[1] || 0)
  }))

  return (
    <div className="p-6 space-y-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800">Gestão de Slices</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Criar Slice via Template</h2>
          <form onSubmit={handleTemplateSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Tipo de Slice</label>
              <select
                value={sliceForm.slice_type}
                onChange={(e) => setSliceForm({...sliceForm, slice_type: e.target.value})}
                className="w-full px-3 py-2 border rounded"
              >
                <option value="URLLC">URLLC</option>
                <option value="eMBB">eMBB</option>
                <option value="mMTC">mMTC</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Bandwidth (Mbps)</label>
              <input
                type="number"
                value={sliceForm.bandwidth}
                onChange={(e) => setSliceForm({...sliceForm, bandwidth: Number(e.target.value)})}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Latência (ms)</label>
              <input
                type="number"
                value={sliceForm.latency}
                onChange={(e) => setSliceForm({...sliceForm, latency: Number(e.target.value)})}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Descrição</label>
              <input
                type="text"
                value={sliceForm.description}
                onChange={(e) => setSliceForm({...sliceForm, description: e.target.value})}
                className="w-full px-3 py-2 border rounded"
                placeholder="Descrição do slice"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Criando..." : "Criar Slice"}
            </button>
          </form>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Criar Slice via LNP</h2>
          <form onSubmit={handleLnpSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Descrição (Linguagem Natural)</label>
              <textarea
                value={lnpForm.description}
                onChange={(e) => setLnpForm({...lnpForm, description: e.target.value})}
                className="w-full px-3 py-2 border rounded"
                rows={6}
                placeholder="Ex: Criar slice URLLC com latência de 1ms e banda de 100Mbps para telecirurgia"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? "Processando..." : "Criar via LNP"}
            </button>
          </form>
        </Card>
      </div>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Distribuição de Slices por Tipo</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={slicesData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" fill="#8884d8" />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Templates Rápidos</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => createSlice({
              slice_type: "URLLC",
              bandwidth: 100,
              latency: 1,
              description: "Template URLLC"
            })}
            className="p-4 border rounded hover:bg-gray-100"
          >
            <div className="font-semibold">URLLC</div>
            <div className="text-sm text-gray-600">100 Mbps, 1ms</div>
          </button>
          <button
            onClick={() => createSlice({
              slice_type: "eMBB",
              bandwidth: 500,
              latency: 5,
              description: "Template eMBB"
            })}
            className="p-4 border rounded hover:bg-gray-100"
          >
            <div className="font-semibold">eMBB</div>
            <div className="text-sm text-gray-600">500 Mbps, 5ms</div>
          </button>
          <button
            onClick={() => createSlice({
              slice_type: "mMTC",
              bandwidth: 50,
              latency: 10,
              description: "Template mMTC"
            })}
            className="p-4 border rounded hover:bg-gray-100"
          >
            <div className="font-semibold">mMTC</div>
            <div className="text-sm text-gray-600">50 Mbps, 10ms</div>
          </button>
        </div>
      </Card>
    </div>
  )
}
JSEOF

echo "   ✅ SlicesManagement.jsx criado"
echo ""

echo "=========================================="
echo "✅ Arquivos criados com sucesso!"
echo "=========================================="
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Verificar se router está no main.py:"
echo "   grep -A 3 'prometheus_router' apps/api/main.py"
echo ""
echo "2. Se não estiver, adicionar no final do main.py:"
echo "   (já temos o código pronto para adicionar)"
echo ""
echo "3. Verificar se rotas estão no App.jsx:"
echo "   grep -A 3 'DashboardComplete' apps/ui/src/App.jsx"
echo ""
echo "4. Testar API:"
echo "   curl http://localhost:8000/prometheus/health"
echo ""




