#!/usr/bin/env bash
set -euo pipefail

BASE="/home/porvir5g/gtp5g/trisla"
cd "$BASE"

echo "=============================="
echo "FASE B — Integrar RTT real no MDCE"
echo "=============================="

FILE="apps/nasp-adapter/src/metrics_collector.py"

if ! grep -q "probe_duration_seconds" "$FILE"; then
  echo "Inserindo coleta de RTT via Prometheus..."

  cat >> "$FILE" <<'PY'

# ============================
# RTT REAL VIA BLACKBOX
# ============================

def _collect_transport_rtt_prometheus():
    try:
        prom_url = os.getenv(
            "PROMETHEUS_URL",
            "http://monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090"
        )

        query = 'max by (job) (probe_duration_seconds{job="probe/monitoring/trisla-transport-tcp-probe"}) * 1000'
        resp = requests.get(
            f"{prom_url}/api/v1/query",
            params={"query": query},
            timeout=5
        )

        data = resp.json()
        if data["status"] != "success":
            return None

        results = data["data"]["result"]
        if not results:
            return None

        return float(results[0]["value"][1])

    except Exception:
        return None
PY

else
  echo "RTT já parece integrado."
fi

echo "Agora integrando no collect_all()..."

sed -i '/transport = {/a\        "rtt_p95_ms": _collect_transport_rtt_prometheus(),' apps/nasp-adapter/src/metrics_collector.py

echo "Atualizando capacity_accounting.py..."

cat >> apps/nasp-adapter/src/capacity_accounting.py <<'PY'

# ============================
# RTT CHECK POR SLICE
# ============================

def _check_transport_sla(slice_type, multidomain):
    rtt = multidomain.get("transport", {}).get("rtt_p95_ms")
    if rtt is None:
        return True, []

    limits = {
        "URLLC": 20,
        "eMBB": 80,
        "mMTC": 150
    }

    threshold = limits.get(slice_type, 100)

    if rtt > threshold:
        return False, [f"transport_rtt_exceeded:{rtt}ms>{threshold}ms"]

    return True, []
PY

echo "Integrando RTT check no ledger_check..."

sed -i '/return False, reasons/i\    ok_transport, rtt_reasons = _check_transport_sla(slice_type, multidomain)\n    if not ok_transport:\n        reasons.extend(rtt_reasons)\n        return False, reasons' apps/nasp-adapter/src/capacity_accounting.py

echo "Build nova imagem..."

TAG="v3.9.23-rtt"
docker build -t ghcr.io/abelisboa/trisla-nasp-adapter:${TAG} apps/nasp-adapter
docker push ghcr.io/abelisboa/trisla-nasp-adapter:${TAG}

echo "Atualizando Helm..."
helm upgrade trisla helm/trisla -n trisla --set naspAdapter.image.tag=${TAG}

kubectl rollout status deployment/trisla-nasp-adapter -n trisla

echo "=============================="
echo "FASE B CONCLUÍDA"
echo "=============================="
