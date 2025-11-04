# TriSLA – Ambiente de Produção

## 1. Estrutura

O TriSLA é composto por seis módulos principais e um dashboard opcional:

- API (FastAPI)
- UI (React/Vite)
- AI (Motor Inteligente)
- Semantic (Ontologia)
- Blockchain (Smart Contracts)
- Monitoring (Prometheus/Grafana)
- Dashboard (Frontend/Backend visual, opcional)

## 2. Execução local

```bash
ENABLE_DASHBOARD=true docker compose up -d
```

## 3. Build

```bash
# Build completo
./release/build.sh

# Build apenas do dashboard
./release/build_dashboard.sh
```

## 4. Publicação

```bash
./release/push_to_github.sh
```



---
## Conteúdo de EXECUTION_GUIDE.md


# 🧠 TriSLA Portal — Execution Guide

## Passos automáticos
1. Build de módulos (AI, NLP, Fabric, Monitoring, UI)
2. Criação do ambiente Docker Compose
3. Validação dos containers (healthcheck)
4. Geração de templates NEST (dinâmico)
5. Resumo final no WORKFLOW_SUMMARY.md

O progresso será mostrado no arquivo DEPLOYMENT_STATUS.md.

