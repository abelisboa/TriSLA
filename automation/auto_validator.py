#!/usr/bin/env python3
# ================================================================
#  auto_validator.py — Validador Automático de Deploy TriSLA@NASP
#  Autor: Abel Lisboa | Projeto: TriSLA@NASP
#  Data: Outubro/2025
# ================================================================

import json
from pathlib import Path
from datetime import datetime
from statistics import mean

LOG_FILE = Path(__file__).resolve().parents[1] / "docs" / "evidencias" / "deploy_watch_log.json"
REPORT_FILE = Path(__file__).resolve().parents[1] / "docs" / "evidencias" / "validation_report.json"

TARGET_NAMESPACES = [
    "trisla-nsp",
    "trisla-ai",
    "trisla-semantic",
    "trisla-blockchain",
    "trisla-integration",
    "trisla-monitoring",
]

TARGET_MODULES = [
    "semantic-layer",
    "ai-layer",
    "blockchain-layer",
    "integration-layer",
    "monitoring",
]

# ---------------------------------------------------------------
def print_colored(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m",
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")


def load_logs():
    if not LOG_FILE.exists():
        print_colored(f"❌ Arquivo de log não encontrado: {LOG_FILE}", "red")
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = [json.loads(line.strip()) for line in f if line.strip()]
    return lines


def analyze_status(logs):
    """Analisa todas as amostras e gera estatísticas de disponibilidade."""
    if not logs:
        print_colored("⚠️ Nenhum log encontrado para análise.", "yellow")
        return {}

    summary = {ns: {"samples": 0, "running": 0, "pods": set()} for ns in TARGET_NAMESPACES}
    timestamps = []

    for entry in logs:
        timestamps.append(entry["timestamp"])
        for ns, pods in entry["status"].items():
            if ns not in summary or "error" in pods:
                continue
            for pod in pods:
                name = pod.get("name", "")
                phase = pod.get("phase", "")
                summary[ns]["samples"] += 1
                summary[ns]["pods"].add(name)
                if phase == "Running":
                    summary[ns]["running"] += 1

    # Calcular percentual de sucesso
    for ns, data in summary.items():
        if data["samples"] == 0:
            data["availability"] = 0.0
        else:
            data["availability"] = round((data["running"] / data["samples"]) * 100, 2)

    total_availability = mean([v["availability"] for v in summary.values()])
    summary["__meta__"] = {
        "start": timestamps[0] if timestamps else "N/A",
        "end": timestamps[-1] if timestamps else "N/A",
        "total_samples": len(logs),
        "avg_availability": round(total_availability, 2),
    }

    return summary


def generate_report(summary):
    """Gera relatório JSON e imprime resumo no terminal."""
    if not summary:
        return

    Path(REPORT_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4, ensure_ascii=False)

    meta = summary["__meta__"]
    print_colored("\n--- RELATÓRIO DE VALIDAÇÃO TRI﻿SLA@NASP ---", "blue")
    print_colored(f"Período analisado: {meta['start']} → {meta['end']}", "yellow")
    print_colored(f"Amostras coletadas: {meta['total_samples']}", "yellow")
    print_colored(f"Disponibilidade média: {meta['avg_availability']}%", "green" if meta["avg_availability"] >= 90 else "red")

    for ns, data in summary.items():
        if ns == "__meta__":
            continue
        color = "green" if data["availability"] >= 90 else "red"
        print_colored(f"  {ns:<20} → {data['availability']}%", color)

    # Avaliação geral
    if meta["avg_availability"] >= 90:
        print_colored("\n✅ Validação bem-sucedida: todos os módulos TriSLA operacionais.\n", "green")
    else:
        print_colored("\n⚠️ Validação incompleta: verifique pods com falhas no relatório JSON.\n", "yellow")


def main():
    print_colored("\n🔍 Iniciando validação automática TriSLA@NASP...\n", "blue")
    logs = load_logs()
    summary = analyze_status(logs)
    generate_report(summary)


if __name__ == "__main__":
    main()
