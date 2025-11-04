---
title: "Workflow Oficial de Desenvolvimento TriSLA@NASP"
author: "Abel José Rodrigues Lisboa"
project: "Dissertação de Mestrado – TriSLA: Uma Arquitetura SLA-Aware Baseada em IA, Ontologia e Contratos Inteligentes para Garantia de SLA em Redes 5G/O-RAN"
institution: "UNISINOS – Programa de Pós-Graduação em Computação Aplicada"
date: "2025-10-16"
tags: ["TriSLA", "NASP", "Workflow", "5G", "O-RAN", "IA", "Ontologia", "Blockchain", "UNISINOS"]
version: "1.0"
---

# 🚀 Workflow Oficial de Desenvolvimento TriSLA@NASP
*(Totalmente alinhado à Proposta_de_Dissertação_Abel-6.pdf)*

---

## 🔹 Visão Geral

Este workflow define o **processo completo de desenvolvimento, integração, validação e observabilidade** da arquitetura **TriSLA** dentro do **NASP (Network Automation & Slicing Platform)** já operacional.

A execução segue integralmente os **Capítulos 4–7 e Apêndices A–H** da proposta oficial, aplicando as melhores práticas de **DevOps, MLOps e AIOps**, com rastreabilidade e conformidade acadêmica.

---

## 🧩 FASE 0 — Estrutura e Preparação do Ambiente

**Objetivo:** Estabelecer base de desenvolvimento segura, modular e reprodutível.

| Componente | Ação |
|-------------|------|
| **Repositório Git** | Criar repositório monorepo `trisla-nasp` com branches `main`, `develop`, `feature/*`. |
| **CI/CD** | Configurar pipeline GitHub Actions/GitLab CI: build → test → deploy → observability. |
| **Infraestrutura Base** | Kubernetes + Helm + Prometheus + Grafana + OpenTelemetry. |
| **Controle de Acesso** | Aplicar políticas RBAC e secrets NASP para módulos internos. |
| **Documentação** | `docs/` com estrutura ABNT + Capítulos 4–7 + Apêndices. |

---

## ⚙️ FASE 1 — Ontologia e Módulo SEM-CSMF

**Objetivo:** Interpretar requisições em linguagem natural e convertê-las em templates NEST compatíveis com NASP.

| Etapa | Atividade |
|-------|------------|
| **Modelagem Ontológica** | Criar ontologia TriSLA (OWL/SWRL) com domínios: SLA, Slice, Recurso, Decisão, Contrato. |
| **Raciocínio Semântico** | Implementar motor de inferência (OWLReady2 ou Apache Jena). |
| **Mapeamento NL → NEST** | Pipeline PLN (spaCy + Sentence-BERT) para reconhecimento de intenção. |
| **Validação** | Converter NEST canônico → subset NASP (Apêndice G.2). |
| **Teste** | Entradas reais: “cirurgia remota”, “controle industrial”, “IoT massivo”. |

📘 **Saída:** NEST validado e compatível com APIs NASP.

---

## 🔮 FASE 2 — Módulo ML-NSMF (Predição e Decisão com XAI)

**Objetivo:** Antecipar violações de SLA e recomendar ações preventivas com explicabilidade.

| Etapa | Atividade |
|-------|------------|
| **Coleta de Dados** | Consumir métricas do NASP (latência, jitter, perda, throughput, disponibilidade). |
| **Treinamento** | Rede **LSTM** com janelas temporais para prever degradação SLA. |
| **Explicabilidade (XAI)** | Integrar **SHAP** para justificar predições. |
| **Integração** | Expor API gRPC (I-02) + Consumer Kafka (I-03). |
| **Monitoramento** | Dashboards em Grafana com métricas p99 e erro. |

📘 **Saída:** Previsões e explicações SLA-aware em tempo real.

---

## ⛓️ FASE 3 — Módulo BC-NSSMF (Contratos Inteligentes e Compliance)

**Objetivo:** Garantir execução contratual e rastreabilidade com blockchain.

| Etapa | Atividade |
|-------|------------|
| **DLT Base** | Implantar **Hyperledger Fabric** (peer/orderer, CA, chaincode). |
| **Smart Contracts** | Desenvolver contratos SLA-aware com cláusulas automáticas de verificação. |
| **Oracles** | Implementar REST oracles (I-04) para eventos NWDAF/NASP. |
| **Auditoria** | Registro automático de logs (Apêndice H). |
| **Compliance** | Validação via Proof of Compliance e rastreabilidade (Apêndice F). |

📘 **Saída:** Smart contracts executáveis e auditáveis.

---

## 🧠 FASE 4 — Mecanismo de Decisão e SLA-Agent Layer

**Objetivo:** Fechar o loop de decisão TriSLA e coordenar ações nos domínios RAN, Transporte e Core.

| Etapa | Atividade |
|-------|------------|
| **Core de Decisão** | Implementar Decision Engine central que orquestra as respostas dos módulos SEM-, ML- e BC-. |
| **Agentes Federados** | Criar SLA-Agent Layer com agentes RAN, TN e Core (publicadores Kafka e APIs REST). |
| **Políticas de Ação** | Configurar política SLA-aware: aceitar, renegociar ou recusar requisições. |
| **Closed Loop** | Ciclo: Requisição → Análise → Execução → Observação → Ajuste. |
| **Persistência** | Registro contínuo de decisões e SLOs no ledger Fabric. |

📘 **Saída:** Decisões justificadas, ações automatizadas e compliance registrado.

---

## 📊 FASE 5 — Observabilidade e Telemetria Integrada

**Objetivo:** Garantir visibilidade completa e rastreabilidade dos SLOs definidos.

| Etapa | Atividade |
|-------|------------|
| **OpenTelemetry** | Coletor central para traces, métricas e logs estruturados. |
| **Prometheus + Grafana** | Dashboards com p99, erro, XAI, BC, agentes e compliance. |
| **Formato de Log** | Padrão do Apêndice H (campos: módulo, timestamp, métrica, status, explicação). |
| **Alertas Automáticos** | Regras SLA-aware para violações de latência e throughput. |
| **Armazenamento Longo Prazo** | Exportação de logs para NASP/ElasticSearch. |

📘 **Saída:** Observabilidade completa e integração direta com NASP dashboards.

---

## 🔁 FASE 6 — Implantação no NASP (Produção Controlada)

**Objetivo:** Integrar todos os módulos TriSLA ao NASP existente.

| Etapa | Ação |
|-------|------|
| **Orquestração** | Deploy via **Kubernetes + Helm** (um chart por módulo). |
| **Namespace** | `trisla-nsp` dedicado, isolado e seguro. |
| **Gateway NASP** | Exposição REST (I-07) para acesso externo e APIs de orquestração. |
| **Testes Automatizados** | CI/CD executa smoke tests + E2E (Apêndices D, F). |
| **Segurança** | TLS bidirecional, autenticação JWT e RBAC granular. |

📘 **Saída:** Sistema operacional e integrado com o NASP real.

---

## 🧩 FASE 7 — Validação Experimental e Métricas (Cap. 5)

**Objetivo:** Verificar o desempenho TriSLA nos três eixos de avaliação (E1–E3).

| Eixo | Módulo | Métricas-Chave | Resultado Esperado |
|------|---------|----------------|--------------------|
| **E1 – Semântico** | SEM-CSMF | Precisão de mapeamento (100%) | Mapeamento NEST validado |
| **E2 – Inteligente** | ML-NSMF + Decision Engine | Erro < 5%, p99 < SLO | Ações preventivas automáticas |
| **E3 – Contratual** | BC-NSSMF | Contratos válidos + logs auditáveis | Execução e compliance automatizado |

📘 **Saída:** Validação empírica dos pilares TriSLA.

---

## 📑 FASE 8 — Documentação e Rastreabilidade (Apêndices F–H)

**Objetivo:** Consolidar rastreabilidade, testes e documentação final.

| Componente | Ação |
|-------------|------|
| **Apêndice F** | Matriz: commits → I-* → testes → KPIs → dashboards. |
| **Apêndice G** | Referência cruzada com códigos, templates e scripts. |
| **Apêndice H** | Logs, observabilidade e métricas padronizadas. |
| **Documentação ABNT** | Atualizar resultados e fluxos no Cap. 5–7. |

📘 **Saída:** Documentação acadêmica completa e pronta para banca.

---

## 🧭 DIRETRIZES GERAIS DE BOAS PRÁTICAS

1. **Infraestrutura como Código (IaC):**  
   Kubernetes + Helm Charts versionados em `infra/`.

2. **Automação de Contratos:**  
   Todos os contratos (I-01… I-07) versionados em `contracts/`.

3. **Segurança Zero-Trust:**  
   Autenticação via mTLS, JWT e RBAC em todos os microserviços.

4. **CI/CD com Gates de SLO:**  
   Deploy só ocorre se p99, erro e disponibilidade atenderem metas.

5. **Reprodutibilidade Científica:**  
   Cada experimento gera relatório automático em Markdown/CSV.

6. **Compatibilidade Padronizada:**  
   3GPP TS 28.541, ETSI ZSM, O-RAN Alliance, GSMA NG.127.

---

## ✅ RESULTADO FINAL ESPERADO

> **TriSLA operacional e validada no NASP**, com integração entre módulos SEM-CSMF, ML-NSMF e BC-NSSMF, observabilidade completa, SLOs auditáveis e rastreabilidade garantida do ciclo **Intenção → Decisão → Execução → Observação → Compliance.**
