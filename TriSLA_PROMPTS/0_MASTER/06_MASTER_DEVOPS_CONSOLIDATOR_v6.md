# 📘 TriSLA — MASTER-DEVOPS-CONSOLIDATOR v6.0

**Documento Oficial — Fluxo DevOps Unificado (Local → GitHub → NASP)**  
**2025 — Abel Lisboa**

---

## 🧭 1. Objetivo Geral

Este documento consolida todo o fluxo DevOps oficial do projeto TriSLA, integrando:

- Desenvolvimento local
- Execução via LLM (prompts)
- Build CI/CD
- Publicação GHCR
- Deploy no NASP (node1/node2)
- Integração com agentes RAN / CORE / TRANSPORT
- Observabilidade OTLP
- Smart Contracts
- Testes (unit, integration, E2E)

Este arquivo substitui e unifica todas as versões anteriores do MASTER-ORCHESTRATOR.

---

## 🔄 2. Arquitetura DevOps Consolidada

### 📌 Fluxo principal

```
┌──────────────┐      ┌────────────────┐      ┌──────────────────────┐
│  LOCAL DEV    │ ---> │  REPOSITÓRIO   │ ---> │   NASP (node1/node2) │
│  Sandbox/LLM  │      │   GitHub/GHCR   │      │   (Deploy real)      │
└──────────────┘      └────────────────┘      └──────────────────────┘
       │                       │                         │
       ▼                       ▼                         ▼
 Build local            Build CI/CD GHCR        Helm + Ansible Deploy
 Testes                 Scan de images          Agentes + NASP Adapter
 LLM Prompts            Releases Automáticas     Closed-loop Assurance
```

---

## 📁 3. Estrutura Consolidada dos Prompts

```
TriSLA_PROMPTS/
│
├── 0_MASTER/
│   ├── 00_MASTER_PLANEJAMENTO.md
│   ├── 01_ORDEM_EXECUCAO.md
│   ├── 02_CHECKLIST.md
│   ├── 03_MASTER_CLEANUP_ORCHESTRATOR.md
│   └── 06_MASTER_DEVOPS_CONSOLIDATOR_v6.md   ← ESTE ARQUIVO
│
├── 1_INFRA/
├── 2_SEMANTICA/
├── 3_ML/
├── 4_BLOCKCHAIN/
├── 5_INTERFACES/
├── 6_DEPLOY/
├── 7_NASP/
├── 8_SLO/
└── 9_VALIDACAO/
```

---

## 🧱 4. Regras de Ouro do Repositório TriSLA

### 4.1 Diretórios críticos (protegidos)

- `apps/sem-csmf/`
- `apps/ml-nsmf/`
- `apps/decision-engine/`
- `apps/bc-nssmf/`
- `apps/sla-agent-layer/`
- `apps/nasp-adapter/`
- `blockchain/`
- `monitoring/`
- `helm/trisla/`
- `ansible/`
- `tests/`

### 4.2 Diretórios voláteis (limpáveis)

- `__pycache__/`
- `.pytest_cache/`
- `logs/`
- `*.bak`
- `*.log`
- `tmp/`

### 4.3 Diretórios que exigem decisão manual

- `src/` (duplicação de sem-csmf)
- `apps/*/backup/`
- `helm/*/*.bak`

---

## 🧪 5. Pipelines TriSLA

### 5.1 Pipeline LOCAL (Sandbox)

**Executado por:**

```bash
./TRISLA_AUTO_RUN.sh
```

**Inclui:**

- SEM-CSMF
- ML-NSMF
- Decision Engine
- BC-NSSMF
- Besu
- Kafka (opcional)
- Smart Contracts
- OTLP Collector
- Testes unitários, integração e E2E parcial

**⚠️ Não executa localmente:**

- NASP Adapter
- SLA-Agent Layer
- Prometheus real
- Métricas reais

### 5.2 Pipeline NASP (Produção Experimental)

**Executado via:**

```bash
ansible-playbook ansible/deploy-trisla-nasp.yml
helm upgrade --install trisla ...
```

**Inclui:**

- NASP Adapter
- SLA-Agent-Layer
- Prometheus real
- Grafana real
- Closed-loop assurance completo

---

## 🧩 6. MASTER-PROMPT-ORCHESTRATOR v6

**Executado no Cursor:**

```bash
cursor run TriSLA_PROMPTS/0_MASTER/06_MASTER_DEVOPS_CONSOLIDATOR_v6.json
```

---

## 🚀 7. Fluxo DevOps Completo

1. Gerar código via prompts
2. Testes locais
3. Build local
4. Publicação GHCR
5. Deploy NASP
6. Monitoramento OTLP
7. Auditoria final

---

## 🛰️ 8. Integração dos Agentes (RAN, CORE, TRANSPORT)

**Localização:**

- `apps/sla-agent-layer/src/agent_ran.py`
- `apps/sla-agent-layer/src/agent_core.py`
- `apps/sla-agent-layer/src/agent_transport.py`

**Somente ativos no NASP.**

---

## 📈 9. SLO / SLA / Auditoria

**Métricas:**

- Latência (p50/p95/p99)
- Disponibilidade
- Viabilidade do slice
- Correções aplicadas
- Violação x reação

---

## 🏁 10. Checklist Final

- [ ] Prompts reorganizados
- [ ] Pipelines funcionando
- [ ] Estrutura limpa
- [ ] Agentes ativos
- [ ] Observabilidade ativa
- [ ] CI/CD funcionando
- [ ] Deploy NASP OK

---

**✔️ MASTER-DEVOPS-CONSOLIDATOR v6.0 — CONCLUÍDO**

