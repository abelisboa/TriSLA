#!/usr/bin/env python3
# ================================================================
#  deploy_watcher.py — Monitor de Deploy TriSLA@NASP
#  Autor: Abel Lisboa | Projeto: TriSLA@NASP
#  Data: Outubro/2025
# ================================================================

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[1] / "docs" / "evidencias"
LOG_FILE = LOG_DIR / "deploy_watch_log.json"
NAMESPACES = [
    "trisla",
    "trisla-nsp",
    "trisla-ai",
    "trisla-blockchain",
    "trisla-integration",
    "trisla-monitoring",
    "trisla-semantic",
]

REFRESH_INTERVAL = 20  # segundos


def run_command(cmd):
    """Executa um comando shell e retorna a saída limpa."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Erro: {e.stderr.strip()}"


def print_colored(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m",
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")


def get_pod_status():
    """Consulta o estado dos pods TriSLA em todos os namespaces relevantes."""
    all_status = {}

    for ns in NAMESPACES:
        cmd = f"kubectl get pods -n {ns} -o json"
        result = run_command(cmd)
        if result.startswith("Erro"):
            all_status[ns] = {"error": result}
            continue

        try:
            pods = json.loads(result)["items"]
        except Exception:
            all_status[ns] = {"error": "Falha ao parsear JSON"}
            continue

        ns_status = []
        for pod in pods:
            name = pod["metadata"]["name"]
            phase = pod["status"].get("phase", "Unknown")
            restarts = pod["status"].get("containerStatuses", [{}])[0].get("restartCount", 0)
            ns_status.append({"name": name, "phase": phase, "restarts": restarts})
        all_status[ns] = ns_status

    return all_status


def save_log(status):
    """Salva snapshot JSON com timestamp."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": status,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def display_status(status):
    """Mostra os resultados no terminal."""
    print("\n==============================")
    print_colored(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "blue")
    print("==============================")

    for ns, pods in status.items():
        if "error" in pods:
            print_colored(f"[{ns}] {pods['error']}", "red")
            continue

        if not pods:
            print_colored(f"[{ns}] (sem pods)", "yellow")
            continue

        print_colored(f"\nNamespace: {ns}", "yellow")
        for pod in pods:
            color = "green" if pod["phase"] == "Running" else "red"
            print_colored(f"  {pod['name']}  →  {pod['phase']}  (Restarts: {pod['restarts']})", color)


def main():
    print_colored("\n🚀 Iniciando monitoramento de deploy TriSLA@NASP...", "blue")
    print_colored(f"Atualização a cada {REFRESH_INTERVAL}s\n", "yellow")

    try:
        while True:
            status = get_pod_status()
            display_status(status)
            save_log(status)
            time.sleep(REFRESH_INTERVAL)
    except KeyboardInterrupt:
        print_colored("\n🛑 Monitoramento interrompido pelo usuário.\n", "yellow")


if __name__ == "__main__":
    main()
