# ==========================================
# ⚙️ TriSLA Portal Hybrid NASP Integration
# ==========================================
# Author: Abel Lisboa (TriSLA NASP Project)
# Purpose: Add hybrid auto-detection mode (local ↔ NASP) + fix compose
# ==========================================

echo "🚀 Starting TriSLA Portal Hybrid Mode upgrade..."

# 1️⃣ Corrigir docker-compose.yaml
sed -i '/^version:/d' docker-compose.yaml 2>/dev/null || true
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
echo "✅ docker-compose.yaml fix applied."

# 2️⃣ Atualizar endpoint NASP com modo híbrido
cat > apps/api/nasp/metrics.py <<'PYCODE'
from fastapi import APIRouter
import httpx, os, random

router = APIRouter(prefix="/nasp", tags=["NASP"])

@router.get("/metrics")
async def get_nasp_metrics():
    """Importa métricas do NASP, ou simula se offline (modo híbrido)."""
    metrics = {}
    env_mode = os.getenv("TRISLA_MODE", "auto")
    prometheus_url = os.getenv("PROM_URL", "http://nasp-prometheus.monitoring.svc.cluster.local:9090/api/v1/query")

    async def fetch_real_metrics():
        async with httpx.AsyncClient(timeout=5) as client:
            def q(expr):
                return client.get(prometheus_url, params={"query": expr})
            res_latency, res_jitter, res_loss, res_avail = await q("avg(latency_ms)"), await q("avg(jitter_ms)"), await q("avg(packet_loss)"), await q("avg(availability)")
            return {
                "latency_ms": float(res_latency.json()["data"]["result"][0]["value"][1]),
                "jitter_ms": float(res_jitter.json()["data"]["result"][0]["value"][1]),
                "packet_loss": float(res_loss.json()["data"]["result"][0]["value"][1]),
                "availability": float(res_avail.json()["data"]["result"][0]["value"][1])
            }

    async def generate_simulated():
        return {
            "latency_ms": round(random.uniform(4, 7), 2),
            "jitter_ms": round(random.uniform(0.3, 0.8), 2),
            "packet_loss": round(random.uniform(0.001, 0.01), 3),
            "availability": round(random.uniform(99.7, 99.99), 3)
        }

    try:
        if env_mode == "local":
            metrics = await generate_simulated()
            mode = "Local Simulation"
        elif env_mode == "nasp":
            metrics = await fetch_real_metrics()
            mode = "NASP (Real Data)"
        else:
            try:
                metrics = await fetch_real_metrics()
                mode = "NASP (Auto)"
            except Exception:
                metrics = await generate_simulated()
                mode = "Local Fallback"

        return {"status": "success", "mode": mode, "metrics": metrics}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
PYCODE

echo "✅ Hybrid NASP metrics API ready."

# 3️⃣ Atualizar página Monitoring.jsx com detecção automática
cat > apps/ui/src/pages/Monitoring.jsx <<'JSX'
import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from "recharts"

export default function Monitoring() {
  const [data, setData] = useState([])
  const [streaming, setStreaming] = useState(false)
  const [mode, setMode] = useState("Detecting...")

  const fetchMetrics = async () => {
    try {
      const res = await fetch("http://localhost:8000/nasp/metrics")
      const json = await res.json()
      if (json.status === "success") {
        const now = new Date().toLocaleTimeString()
        setMode(json.mode)
        setData(prev => [...prev.slice(-20), { time: now, ...json.metrics }])
      }
    } catch (err) {
      console.error("Failed to fetch metrics:", err)
    }
  }

  useEffect(() => {
    let interval
    if (streaming) interval = setInterval(fetchMetrics, 5000)
    return () => clearInterval(interval)
  }, [streaming])

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-2xl font-bold">TriSLA Portal — NASP Metrics ({mode})</h2>
      <div className="flex space-x-2">
        <button onClick={() => setStreaming(true)} className="bg-green-500 text-white px-4 py-2 rounded">Start Stream</button>
        <button onClick={() => setStreaming(false)} className="bg-red-500 text-white px-4 py-2 rounded">Stop Stream</button>
      </div>
      <Card className="mt-4">
        <LineChart width={900} height={320} data={data}>
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

echo "✅ Monitoring UI with hybrid mode ready."

# 4️⃣ Adicionar variável de ambiente no compose
if ! grep -q "TRISLA_MODE" docker-compose.yaml; then
cat >> docker-compose.yaml <<'YAML'
    environment:
      - TRISLA_MODE=auto
      - PROM_URL=http://nasp-prometheus.monitoring.svc.cluster.local:9090/api/v1/query
YAML
fi

# 5️⃣ Finalização
echo "✅ Hybrid NASP upgrade completed!"
echo "➡️  Access http://localhost:5173/monitoring"
echo "➡️  API: http://localhost:8000/nasp/metrics"
