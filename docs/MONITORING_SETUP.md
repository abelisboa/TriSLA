# 🧩 TriSLA Portal — Monitoring & Híbrido Metrics Setup Guide

**Author:** Abel Lisboa (TriSLA Híbrido Project)  
**Version:** 2.0  
**Last Update:** October 24, 2025  

---

## 📘 Overview

The **TriSLA Portal Monitoring Module** enables unified observability across all TriSLA components — Semantic (SEM-NSMF), AI Decision (ML-NSMF), Blockchain (BC-NSSMF), and Worker subsystems.  
It provides **real-time metrics** from both **local simulation** and **Híbrido production environments**, with automatic detection and fallback modes.

Supported metrics include:
- **Latency (ms)**
- **Jitter (ms)**
- **Packet Loss (%)**
- **Availability (%)**

Collected data is visualized in the **/monitoring** dashboard and stored by **Prometheus**.

---

## ⚙️ Architecture Overview

```
┌───────────────────────────────┐
│        TriSLA Portal          │
│ ┌──────────┬───────────────┐ │
│ │ FastAPI  │  React UI     │ │
│ │ (API)    │  (Dashboard)  │ │
│ └────┬─────┴─────┬─────────┘ │
│      │           │           │
│  ┌───▼───┐   ┌───▼───┐       │
│  │ Redis │ ← │ Worker│       │
│  └───┬───┘   └───┬───┘       │
│      │           │           │
│      ▼           ▼           │
│  Prometheus ←─────┘           │
│ (Local + Híbrido Hybrid)         │
└───────────────────────────────┘
```

---

## 🧰 Requirements

| Component | Purpose | Default Port |
|------------|----------|--------------|
| **FastAPI** | Exposes Híbrido metric endpoints | `8000` |
| **UI (React + Nginx)** | Dashboard visualization | `5173` |
| **Redis** | Job queue for async data retrieval | `6379` |
| **Worker (RQ)** | Background Híbrido metric importer | – |
| **Prometheus** | Metrics collection and query engine | `9090` |

---

## 🚀 Installation

```bash
docker compose build api ui worker prometheus
docker compose up -d
```

---

## 📡 Prometheus Configuration

File: `monitoring/prometheus.yml`

```yaml
global:
  scrape_interval: 5s
  evaluation_interval: 5s

scrape_configs:
  - job_name: 'trisla-api'
    static_configs:
      - targets: ['trisla-api:8000']

  - job_name: 'trisla-worker'
    static_configs:
      - targets: ['trisla-worker:8000']

  - job_name: 'hibrido-prometheus'
    metrics_path: /metrics
    static_configs:
      - targets: ['hibrido-prometheus.monitoring.svc.cluster.local:9090']
        labels:
          source: "Híbrido"

  - job_name: 'trisla-local-metrics'
    metrics_path: /metrics
    static_configs:
      - targets: ['localhost:8000']
        labels:
          source: "Local"
```

---

## 🔄 Hybrid Mode (Auto-Detection)

TriSLA Portal automatically switches between two modes:

| Mode | Detection Rule | Description |
|-------|----------------|--------------|
| **Híbrido Mode** | Cluster environment with reachable Híbrido Prometheus | Collects live Híbrido metrics |
| **Local Fallback** | Híbrido not reachable | Simulates data locally |

Environment variables:
```yaml
TRISLA_MODE=auto
PROM_URL=http://hibrido-prometheus.monitoring.svc.cluster.local:9090/api/v1/query
```

---

## 📊 Access Points

| Interface | URL | Description |
|------------|-----|-------------|
| **Monitoring UI** | http://localhost:5173/monitoring | Charts and status |
| **Prometheus Console** | http://localhost:9090 | Direct queries |
| **API Metrics** | http://localhost:8000/hibrido/metrics | JSON endpoint |

---

## 🔍 Test Example

```bash
curl http://localhost:8000/hibrido/metrics
```

Expected:
```json
{
  "status": "success",
  "mode": "Local Fallback",
  "metrics": {
    "latency_ms": 4.93,
    "jitter_ms": 0.42,
    "packet_loss": 0.001,
    "availability": 99.98
  }
}
```

---

## 🧠 Troubleshooting

| Symptom | Cause | Fix |
|----------|--------|-----|
| Prometheus not starting | File was a directory | Recreate `prometheus.yml` |
| Híbrido data missing | Híbrido unreachable | Local fallback active |
| Charts blank | Worker not pushing | Restart `trisla-worker` |

---

## 🪪 License & Research Context

Part of the **TriSLA Research Project**, under **UNISINOS / PPGCA**, validating SLA-Aware orchestration in 5G/O-RAN Híbrido environments.

Use limited to academic and research validation.

---

**Maintainer:** [Abel Lisboa](https://github.com/abelisboa)  
**Repository:** [TriSLA-Portal](https://github.com/abelisboa/TriSLA-Portal)
