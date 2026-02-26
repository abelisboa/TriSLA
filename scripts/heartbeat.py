#!/usr/bin/env python3
"""
TriSLA - HEARTBEAT CHECKER

Script de verificação de saúde dos módulos principais do TriSLA.
Pode ser executado standalone ou importado por outros scripts
(ex.: ready-report.py).

Saída:
- Print humano legível no stdout.
- Código de saída:
    0 = HEALTHY
    1 = DEGRADED/ERROR
"""

import json
import socket
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone


def http_check(name: str, url: str, timeout: float = 3.0):
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            if 200 <= status < 300:
                return {
                    "name": name,
                    "type": "http",
                    "target": url,
                    "status": "OK",
                    "detail": f"HTTP {status}",
                }
            return {
                "name": name,
                "type": "http",
                "target": url,
                "status": "ERROR",
                "detail": f"HTTP {status}",
            }
    except Exception as e:
        return {
            "name": name,
            "type": "http",
            "target": url,
            "status": "ERROR",
            "detail": f"{type(e).__name__}: {e}",
        }


def tcp_check(name: str, host: str, port: int, timeout: float = 3.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {
                "name": name,
                "type": "tcp",
                "target": f"{host}:{port}",
                "status": "OK",
                "detail": "TCP connect OK",
            }
    except Exception as e:
        return {
            "name": name,
            "type": "tcp",
            "target": f"{host}:{port}",
            "status": "ERROR",
            "detail": f"{type(e).__name__}: {e}",
        }


def besu_check(name: str = "besu", url: str = "http://127.0.0.1:8545", timeout: float = 3.0):
    """
    Faz uma chamada JSON-RPC simples para eth_blockNumber.
    Usa apenas stdlib (sem web3.py).
    """
    import urllib.request

    payload = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            j = json.loads(body)
            if "result" in j:
                return {
                    "name": name,
                    "type": "jsonrpc",
                    "target": url,
                    "status": "OK",
                    "detail": f"eth_blockNumber={j['result']}",
                }
            return {
                "name": name,
                "type": "jsonrpc",
                "target": url,
                "status": "ERROR",
                "detail": f"Resposta sem campo 'result': {body[:120]}",
            }
    except Exception as e:
        return {
            "name": name,
            "type": "jsonrpc",
            "target": url,
            "status": "ERROR",
            "detail": f"{type(e).__name__}: {e}",
        }


def compute_overall_status(results):
    """
    Regra simples:
    - Se todos OK -> HEALTHY
    - Se pelo menos 1 OK e 1 ERROR -> DEGRADED
    - Se todos ERROR -> ERROR
    """
    if not results:
        return "ERROR"
    oks = sum(1 for r in results if r["status"] == "OK")
    errs = sum(1 for r in results if r["status"] == "ERROR")
    if errs == 0 and oks > 0:
        return "HEALTHY"
    if oks > 0 and errs > 0:
        return "DEGRADED"
    return "ERROR"


def run_all_checks():
    checks = []

    # HTTP health endpoints
    checks.append(http_check("sem-csmf", "http://127.0.0.1:8080/health"))
    checks.append(http_check("ml-nsmf", "http://127.0.0.1:8081/health"))
    checks.append(http_check("decision-engine", "http://127.0.0.1:8082/health"))

    # Blockchain (Besu)
    checks.append(besu_check("besu", "http://127.0.0.1:8545"))

    # Kafka
    checks.append(tcp_check("kafka", "127.0.0.1", 9092))

    # OTLP Collector (gRPC)
    checks.append(tcp_check("otel-collector-grpc", "127.0.0.1", 4317))

    # Prometheus
    checks.append(http_check("prometheus", "http://127.0.0.1:9090/-/healthy"))

    overall = compute_overall_status(checks)
    now = datetime.now(timezone.utc).isoformat()

    return {
        "timestamp": now,
        "overall_status": overall,
        "checks": checks,
    }


def main():
    result = run_all_checks()

    # Impressão compacta e legível
    print(f"[TriSLA HEARTBEAT] {result['timestamp']} — STATUS GERAL: {result['overall_status']}")
    for r in result["checks"]:
        print(f" - {r['name']:<18} [{r['status']}]  -> {r['detail']}")

    # Retornar código de saída conforme status
    status = result["overall_status"]
    if status == "HEALTHY":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

