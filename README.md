# 🚀 TriSLA Portal  
**Public web interface and API for the TriSLA 5G/O-RAN SLA-aware architecture**

---

## 🧩 Overview
The **TriSLA Portal** provides:
- 🌐 Web interface (UI) for SLA visualisation  
- ⚙️ FastAPI backend for slice orchestration and integration with TriSLA Core  
- ☁️ Docker Compose for local or cloud deployment  

This repository contains the public components (UI + API) of the TriSLA architecture.

---

## ⚙️ Requirements
- Docker ≥ 27  
- Python ≥ 3.11  
- Node.js ≥ 18  
- Optional: Kubernetes + Helm ≥ 3.10

---

## 🧰 Quick Start
```bash
git clone https://github.com/abelisboa/TriSLA-Portal.git
cd TriSLA-Portal
docker compose up -d
```

**Access:**
- **API**: http://localhost:8000/docs
- **UI**: http://localhost:5173

---

## 📡 Integration

The Portal connects to public TriSLA images:
- `ghcr.io/abelisboa/trisla-ai:latest`
- `ghcr.io/abelisboa/trisla-semantic:latest`
- `ghcr.io/abelisboa/trisla-blockchain:latest`
- `ghcr.io/abelisboa/trisla-monitoring:latest`

---

## 🧠 About TriSLA

TriSLA (Trustworthy, Reasoned, Intelligent SLA-Aware Architecture) integrates:
- **Semantic reasoning** (SEM-NSMF),
- **Machine learning decisions** (ML-NSMF),
- **Blockchain-based SLA enforcement** (BC-NSSMF),
- **Observability** (NWDAF-like).

---

## 📘 Thesis Reference:
*"TriSLA: Uma Arquitetura SLA-Aware Baseada em IA, Ontologia e Contratos Inteligentes para Garantia de SLA em Redes 5G/O-RAN"* — UNISINOS PPGCA, 2025.

---

## 🪪 License
MIT License © 2025 Abel Lisboa