# Referência Técnica – TriSLA
*(Baseada nos Capítulos 4, 5, 6, 7 e Apêndices A–H da Proposta_de_Dissertação_Abel-6.pdf)*

---

## 1. Introdução Técnica

A **TriSLA (Trustworthy, Reasoned and Intelligent SLA Architecture)** é uma arquitetura modular projetada para garantir a **validação e execução automatizada de SLAs (Service Level Agreements)** em redes **5G/O-RAN**.  
Seu objetivo é permitir que uma solicitação de SLA seja interpretada, analisada e validada automaticamente, antes e durante a operação, em três dimensões: **semântica, inteligente e contratual**.

A implantação é feita dentro do ambiente **NASP (Network Automation & Slicing Platform)**, já existente e operacional, responsável por fornecer infraestrutura de slicing e coleta de telemetria de rede.

A TriSLA é composta por três módulos principais:

| Módulo | Função Principal | Tecnologias |
|---------|------------------|-------------|
| **SEM-CSMF (Semantic CSMF)** | Interpreta intenções em linguagem natural e gera templates NEST/NASP. | Ontologia OWL/SWRL, NLP, Protégé, Sentence-BERT |
| **ML-NSMF (Machine Learning NSMF)** | Prediz disponibilidade de recursos e possíveis violações de SLA com IA explicável. | LSTM, SHAP, Telemetria NASP |
| **BC-NSSMF (Blockchain NSSMF)** | Formaliza e executa contratos inteligentes SLA-aware com rastreabilidade. | Hyperledger Fabric, Oracles REST |

Os módulos comunicam-se por interfaces internas (I-*), definidas no Apêndice A.

---

## 2. Arquitetura TriSLA (Capítulo 4)

### 2.1 Estrutura Geral
A arquitetura segue o modelo 3GPP/ETSI SMO, com três camadas hierárquicas:
- **CSMF:** Comunicação semântica com o usuário (SEM-CSMF).
- **NSMF:** Decisão inteligente e preditiva (ML-NSMF).
- **NSSMF:** Execução e compliance contratual (BC-NSSMF).

A comunicação entre módulos e o NASP ocorre por APIs REST/gRPC/Kafka, todas documentadas como **interfaces I-01 a I-07**.

### 2.2 Fluxo Operacional (6 fases)
1. **Intenção** → entrada em linguagem natural.  
2. **Interpretação** → SEM-CSMF converte para NEST canônico.  
3. **Mapeamento** → NEST convertido para subset NASP.  
4. **Predição** → ML-NSMF estima viabilidade SLA-aware.  
5. **Formalização** → BC-NSSMF cria smart contract.  
6. **Execução e observabilidade** → monitoramento contínuo via NASP.

### 2.3 SLA-Agent Layer
Camada federada com agentes **RAN**, **Transporte** e **Core**. Cada agente monitora métricas específicas do domínio e comunica-se com o Decision Engine central.

### 2.4 Integração com NASP
- Deploy em contêineres (Docker/Kubernetes).  
- Comunicação via Kafka, REST e gRPC.  
- Telemetria exportada pelo NASP → Prometheus → ML-NSMF.  
- Decisões e logs → armazenados no ledger Fabric.

---

## 3. Metodologia de Avaliação (Capítulo 5)

A validação da TriSLA é dividida em **três eixos experimentais (E1–E3)**:

| Eixo | Módulo | Objetivo | Métricas |
|------|---------|-----------|-----------|
| **E1 – Semântico** | SEM-CSMF | Validar precisão da interpretação e geração NEST. | Taxa de mapeamento correto (≥100%) |
| **E2 – Inteligente** | ML-NSMF + Decision Engine | Avaliar predição de violação de SLA e explicabilidade. | Erro < 5%, p99 < SLO |
| **E3 – Contratual** | BC-NSSMF | Avaliar automação contratual e rastreabilidade. | 100% contratos auditáveis |

### 3.1 Métricas gerais
- **Latência média (ms)**  
- **Jitter (ms)**  
- **Disponibilidade (%)**  
- **Taxa de erro (≤1%)**  
- **Tempo de decisão (ms)**  
- **Confiabilidade (R² > 0.95)**

### 3.2 Fontes de dados
- NASP → Prometheus (telemetria contínua)  
- Logs → OTel Collector  
- Contratos e oracles → Hyperledger Fabric

### 3.3 Ferramentas de validação
- Prometheus / Grafana / Jaeger  
- Pytest / Postman / Robot Framework  
- Fabric Explorer (auditoria)

---

## 4. Integração e Validação (Capítulos 6 e 7)

### 4.1 Implantação gradual
A integração é realizada em três etapas principais:
1. Deploy modular (SEM-CSMF, ML-NSMF, BC-NSSMF).  
2. Ativação dos agentes federados e observabilidade.  
3. Execução dos cenários URLLC, eMBB e mMTC.

### 4.2 Observabilidade
- Coleta por **OpenTelemetry (OTel)**.  
- Métricas exportadas → Prometheus.  
- Dashboards em Grafana (p99, erro, XAI, BC, agentes).  
- Logs padronizados (Apêndice H).

### 4.3 Closed Loop (Ciclo de Decisão)
Ciclo operacional da TriSLA:
```
Intenção → Análise → Decisão → Execução → Observação → Ajuste
```
O loop é contínuo e autoajustável conforme as medições do NASP.

### 4.4 Validação experimental
Cenários testados:
- **URLLC:** latência crítica.  
- **eMBB:** alto throughput.  
- **mMTC:** IoT massivo.  

Cada cenário executa contratos SLA-aware monitorados por métricas em tempo real.

---

## 5. Apêndices Técnicos (A–H)

### A. Interfaces Internas (I-*)
| Interface | Origem → Destino | Tipo | Descrição |
|------------|------------------|------|-----------|
| I-01 | SEM-CSMF → ML-NSMF | gRPC | Envia templates NEST validados |
| I-02 | ML-NSMF → Decision Engine | gRPC | Predições e resultados XAI |
| I-03 | NASP → ML-NSMF | Kafka | Telemetria em tempo real |
| I-04 | BC-NSSMF ↔ Oracles | REST | Dados externos e eventos de rede |
| I-05 | SLA-Agent Layer ↔ Decision Engine | Kafka | Observabilidade multi-domínio |
| I-06 | Decision Engine ↔ NASP API | REST | Ativação e ajustes de slice |
| I-07 | Gateway público NASP | REST | Entrada e visualização TriSLA |

### B. Mapeamento NWDAF ↔ NASP
Compatibilidade semântica entre dados do NWDAF (3GPP) e métricas do NASP, permitindo equivalência entre modelos de telemetria.

### C. Contratos de API
Cada interface I-* possui contrato formal em OpenAPI, Protobuf ou Avro, com:
- Campos obrigatórios e opcionais.  
- Segurança (mTLS, JWT).  
- Políticas de timeout e retry.  
- Logs e auditoria em cada transação.

### D. Testes de Contrato
Incluem:
- Validação de esquema.  
- Autenticação e autorização.  
- Casos positivos/negativos.  
- Assertivas SLO (latência p99, erro < 1%).

### E. Observabilidade e SLOs
Formato de log (Apêndice H):
```
timestamp | módulo | interface | métrica | valor | unidade | status | explicação
```
Monitoramento com alertas automáticos para violações de SLA.

### F. Matriz de Rastreabilidade
Relaciona commits → interfaces → testes → KPIs → dashboards, garantindo transparência total.

### G. Listagens de Código
Implementações em Python e YAML:
- Ontologia (SEM-CSMF).  
- LSTM + SHAP (ML-NSMF).  
- Chaincode (BC-NSSMF).  
- Decision Engine.  
- Conectores NASP.

### H. Plano de Execução e Logs
- Implantação via Helm/Kubernetes.  
- Observabilidade com Prometheus, Grafana e OTel.  
- Logs auditáveis e padronizados.  
- Dashboards organizados por domínio (RAN, Transporte, Core).

---

## 6. Diretrizes de Conformidade

| Categoria | Padrão de Referência |
|------------|----------------------|
| Arquitetura | 3GPP TS 28.541, ETSI ZSM 010 |
| Modelagem Semântica | GSMA NG.127, NG.116 |
| IA Explicável | SHAP, LIME, XAI IEEE 7001 |
| Blockchain | Hyperledger Fabric 2.x |
| Observabilidade | OpenTelemetry, Prometheus |
| Segurança | TLS 1.3, OAuth2.0, RBAC, JWT |
| Documentação | ABNT NBR 6023 / UNISINOS Monografia |

---

## 7. Glossário Técnico

| Termo | Definição |
|--------|------------|
| **TriSLA** | Arquitetura SLA-aware baseada em IA, Ontologia e Blockchain. |
| **NASP** | Network Automation & Slicing Platform (plataforma de slicing e automação). |
| **SLA-aware** | Capacidade de compreender, monitorar e agir com base em SLAs formalizados. |
| **NEST** | Network Slice Type Template (modelo GSMA para requisitos de slice). |
| **Ontologia** | Modelo semântico que define conceitos e relações do domínio SLA/5G. |
| **LSTM** | Rede Neural Recorrente para previsão temporal. |
| **SHAP** | Técnica de explicabilidade de IA baseada em valores de Shapley. |
| **Smart Contract** | Contrato executável em blockchain que garante automação e auditoria. |
| **Closed Loop** | Ciclo contínuo de observação e ação automatizada. |
| **SLO** | Service Level Objective, métrica operacional do SLA. |
| **I-*** | Interfaces internas da arquitetura TriSLA. |

---

📅 **Data:** 2025-10-16  
👤 **Responsável:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP – UNISINOS / Mestrado em Computação Aplicada
