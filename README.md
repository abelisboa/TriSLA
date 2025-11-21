# TriSLA — Uma Arquitetura Baseada em Inteligência Artificial, Ontologia e Contratos Inteligentes para Garantia de SLA em Redes 5G/O-RAN

**TriSLA** é uma arquitetura **SLA-Aware, explicável e automatizada** que integra:

- **Interpretação Semântica (SEM-CSMF)**
- **Predição Inteligente (ML-NSMF com XAI)**
- **Decisão Automatizada (Decision Engine)**
- **Execução Contratual em Blockchain (BC-NSSMF)**
- **Agentes Federados RAN / Transport / Core**
- **Observabilidade OTLP + Prometheus + Grafana**
- **Integração com ambiente NASP (5G/O-RAN)**

TriSLA representa uma abordagem moderna, auditável e de laço-fechado (closed-loop assurance) para o gerenciamento inteligente de network slices 5G/O-RAN.

---

## 📦 Componentes Principais

```
apps/
├── sem-csmf/         # Interpretação Semântica + Ontologia
├── ml-nsmf/          # Predição LSTM + XAI
├── decision-engine/  # Motor de decisão SLA-aware
├── bc-nssmf/         # Smart Contracts (GoQuorum/Besu)
├── sla-agent-layer/  # Agentes federados RAN/Core/Transport
├── nasp-adapter/     # Integração com NASP
└── ui-dashboard/     # Dashboard visual
```

---

## 🧪 Execução Local (Sandbox)

```bash
./TRISLA_AUTO_RUN.sh
```

**Pipeline v8.0 inclui:**
- SEM-CSMF ✔
- ML-NSMF ✔
- Decision Engine ✔
- Smart Contracts ✔
- BC-NSSMF ✔
- OTLP Collector ✔
- HEARTBEAT ✔
- READY REPORT ✔
- E2E Validator ✔

---

## 🚀 Build & Publicação GHCR

```bash
# SEM-CSMF
docker build -t ghcr.io/abelisboa/trisla-sem-csmf:latest apps/sem-csmf/
docker push ghcr.io/abelisboa/trisla-sem-csmf:latest

# ML-NSMF
docker build -t ghcr.io/abelisboa/trisla-ml-nsmf:latest apps/ml-nsmf/
docker push ghcr.io/abelisboa/trisla-ml-nsmf:latest

# Decision Engine
docker build -t ghcr.io/abelisboa/trisla-decision-engine:latest apps/decision-engine/
docker push ghcr.io/abelisboa/trisla-decision-engine:latest

# BC-NSSMF
docker build -t ghcr.io/abelisboa/trisla-bc-nssmf:latest apps/bc-nssmf/
docker push ghcr.io/abelisboa/trisla-bc-nssmf:latest

# SLA-Agent Layer
docker build -t ghcr.io/abelisboa/trisla-sla-agent-layer:latest apps/sla-agent-layer/
docker push ghcr.io/abelisboa/trisla-sla-agent-layer:latest

# NASP Adapter
docker build -t ghcr.io/abelisboa/trisla-nasp-adapter:latest apps/nasp-adapter/
docker push ghcr.io/abelisboa/trisla-nasp-adapter:latest

# UI Dashboard
docker build -t ghcr.io/abelisboa/trisla-ui-dashboard:latest apps/ui-dashboard/
docker push ghcr.io/abelisboa/trisla-ui-dashboard:latest
```

---

## 🎁 Helm Chart

```bash
# Empacotar
helm package helm/trisla/

# Publicar
helm push trisla-*.tgz oci://ghcr.io/abelisboa/helm-charts
```

---

## 📄 Licença

**MIT License**

Copyright (c) 2025 Abel Lisboa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🏷️ TriSLA v1.0.0 — Release Oficial

Esta é a primeira versão pública e consolidada do TriSLA, alinhada à dissertação de mestrado e ao ambiente operacional NASP.

**Principais características:**
- ✅ Arquitetura modular e extensível
- ✅ Integração completa com NASP
- ✅ Observabilidade end-to-end (OTLP)
- ✅ Smart Contracts para registro imutável de SLAs
- ✅ Closed-loop assurance automatizado
- ✅ Pipeline DevOps completo (v8.0)

---

## 📚 Documentação

Consulte a documentação completa em:
- `docs/` — Documentação técnica
- `TriSLA_PROMPTS/` — Prompts e guias de desenvolvimento
- `helm/trisla/README.md` — Guia de deployment via Helm

---

## 🤝 Contribuindo

Este é um projeto acadêmico. Para contribuições, por favor entre em contato através do repositório GitHub.

---

**TriSLA v1.0.0** — Desenvolvido como parte da dissertação de mestrado em Engenharia de Sistemas e Computação.
