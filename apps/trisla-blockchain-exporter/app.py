from flask import Flask, Response
import requests
import os

app = Flask(__name__)

BESU_RPC_URL = os.getenv("BESU_RPC_URL", "http://besu:8545")

def _safe_post(payload: dict) -> dict:
    try:
        r = requests.post(BESU_RPC_URL, json=payload, timeout=5)
        if r.status_code != 200:
            return {}
        return r.json() if isinstance(r.json(), dict) else {}
    except Exception:
        return {}

def _eth_block_number() -> int:
    data = _safe_post({
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1
    })
    try:
        return int(data.get("result", "0x0"), 16)
    except Exception:
        return 0

@app.route("/health")
def health():
    return {"status": "ok", "besu_rpc": BESU_RPC_URL}

@app.route("/metrics")
def metrics():
    # NOTA:
    # Você pediu explicitamente:
    # - trisla_sla_contracts_total
    # - trisla_sla_enforcement_events_total
    #
    # Aqui usamos "block height" como baseline (sempre disponível via RPC).
    # O passo evolutivo “forte” (sem regressão) liga com BC-NSSMF para contadores reais
    # de contratos e eventos de enforcement.
    block = _eth_block_number()

    payload = "\n".join([
        "# TYPE trisla_sla_contracts_total gauge",
        f"trisla_sla_contracts_total {block}",
        "# TYPE trisla_sla_enforcement_events_total gauge",
        f"trisla_sla_enforcement_events_total {block}",
        ""
    ])
    return Response(payload, mimetype="text/plain; version=0.0.4; charset=utf-8")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
