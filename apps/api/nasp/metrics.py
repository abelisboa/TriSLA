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
