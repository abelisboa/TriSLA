from flask import Flask, Response
import subprocess
import json
import os

app = Flask(__name__)

IPERF_SERVER = os.getenv("IPERF_SERVER", "localhost")
IPERF_PORT = os.getenv("IPERF_PORT", "5201")

# Observação: aqui adotamos um baseline seguro.
# - Se iperf3 não estiver acessível, exporta 0 e continua vivo (não derruba o pod).
# - O objetivo é garantir estabilidade e observabilidade contínua.
def _iperf_mbps() -> float:
    try:
        # -J = JSON; -c = client; -p = porta
        out = subprocess.check_output(
            ["iperf3", "-c", IPERF_SERVER, "-p", str(IPERF_PORT), "-J"],
            stderr=subprocess.DEVNULL,
            timeout=8
        )
        j = json.loads(out.decode("utf-8", errors="ignore"))
        bps = j["end"]["sum_received"]["bits_per_second"]
        return float(bps) / 1_000_000.0
    except Exception:
        return 0.0

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/metrics")
def metrics():
    throughput_mbps = _iperf_mbps()

    # NOTA IMPORTANTE:
    # você pediu explicitamente essas 2 métricas.
    # "trisla_slice_bandwidth_usage" aqui fica como proxy do throughput (baseline).
    # No passo evolutivo (sem regressão), podemos substituir por leitura real por-slice.
    payload = "\n".join([
        "# TYPE trisla_iperf_throughput_mbps gauge",
        f"trisla_iperf_throughput_mbps {throughput_mbps}",
        "# TYPE trisla_slice_bandwidth_usage gauge",
        f"trisla_slice_bandwidth_usage {throughput_mbps}",
        ""
    ])
    return Response(payload, mimetype="text/plain; version=0.0.4; charset=utf-8")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
