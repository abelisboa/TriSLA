# ==========================================
# 🚀 TriSLA Portal NASP Metrics Integration Upgrade
# ==========================================
# Author: Abel Lisboa (TriSLA NASP Project)
# Purpose: Integrate NASP metrics into TriSLA Portal (Prometheus + REST)
# ==========================================

echo "🚀 Starting NASP Metrics Integration upgrade..."

# 1️⃣ Criar pastas necessárias
mkdir -p apps/api/nasp apps/ui/src/pages apps/ui/src/components/charts

# 2️⃣ Criar endpoint FastAPI para importação de métricas NASP
cat > apps/api/nasp/metrics.py <<'PYCODE'
from fastapi import APIRouter
import httpx

router = APIRouter(prefix="/nasp", tags=["NASP"])

@router.get("/metrics")
async def get_nasp_metrics():
    """Importa métricas reais do NASP via Prometheus API"""
    try:
        prometheus_url = "http://nasp-prometheus.monitoring.svc.cluster.local:9090/api/v1/query"
        metrics = {}

        async with httpx.AsyncClient(timeout=5) as client:
            # Latência média
            r = await client.get(prometheus_url, params={"query": "avg(latency_ms)"})
            metrics["latency_ms"] = r.json()["data"]["result"][0]["value"][1]

            # Jitter
            r = await client.get(prometheus_url, params={"query": "avg(jitter_ms)"})
            metrics["jitter_ms"] = r.json()["data"]["result"][0]["value"][1]

            # Packet loss
            r = await client.get(prometheus_url, params={"query": "avg(packet_loss)"})
            metrics["packet_loss"] = r.json()["data"]["result"][0]["value"][1]

            # Disponibilidade
            r = await client.get(prometheus_url, params={"query": "avg(availability)"})
            metrics["availability"] = r.json()["data"]["result"][0]["value"][1]

        return {"status": "success", "source": "NASP Prometheus", "metrics": metrics}

    except Exception as e:
        return {"status": "error", "detail": str(e)}
PYCODE

# 3️⃣ Atualizar main.py da API para incluir o roteador NASP
if ! grep -q "from nasp import metrics" apps/api/main.py; then
cat >> apps/api/main.py <<'PYCODE'

# NASP metrics endpoint
from nasp import metrics
app.include_router(metrics.router)
PYCODE
fi

# 4️⃣ Criar página React de monitoramento (Monitoring.jsx)
cat > apps/ui/src/pages/Monitoring.jsx <<'JSX'
import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from "recharts"

export default function Monitoring() {
  const [data, setData] = useState([])
  const [streaming, setStreaming] = useState(false)

  const fetchMetrics = async () => {
    try {
      const res = await fetch("http://localhost:8000/nasp/metrics")
      const json = await res.json()
      if (json.status === "success") {
        const now = new Date().toLocaleTimeString()
        setData(prev => [...prev.slice(-20), { time: now, ...json.metrics }])
      }
    } catch (err) {
      console.error("Failed to fetch NASP metrics:", err)
    }
  }

  useEffect(() => {
    let interval
    if (streaming) {
      interval = setInterval(fetchMetrics, 5000)
    }
    return () => clearInterval(interval)
  }, [streaming])

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-bold">NASP Metrics Monitoring</h2>
      <div className="flex space-x-2">
        <button onClick={() => setStreaming(true)} className="bg-green-500 text-white px-4 py-2 rounded">Start Stream</button>
        <button onClick={() => setStreaming(false)} className="bg-red-500 text-white px-4 py-2 rounded">Stop Stream</button>
      </div>
      <Card className="mt-4">
        <LineChart width={900} height={300} data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="latency_ms" stroke="#8884d8" name="Latency (ms)" />
          <Line type="monotone" dataKey="jitter_ms" stroke="#82ca9d" name="Jitter (ms)" />
          <Line type="monotone" dataKey="packet_loss" stroke="#ff7300" name="Packet Loss (%)" />
          <Line type="monotone" dataKey="availability" stroke="#2f9e44" name="Availability (%)" />
        </LineChart>
      </Card>
    </div>
  )
}
JSX

# 5️⃣ Atualizar docker-compose.yaml (caso ainda não tenha Prometheus)
if ! grep -q "prometheus" docker-compose.yaml; then
cat >> docker-compose.yaml <<'YAML'

  prometheus:
    image: prom/prometheus:latest
    container_name: trisla-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
YAML
fi

# 6️⃣ Finalização
echo "✅ NASP Metrics Integration upgrade completed."
echo "➡️  Access http://localhost:5173/monitoring"
echo "➡️  Check API metrics at http://localhost:8000/nasp/metrics"
