# 03 – Mapa de Dependências TriSLA

**Mapeamento Completo de Dependências entre Módulos, Interfaces e Componentes**

---

## 🎯 Objetivo

Este documento mapeia todas as **dependências técnicas, funcionais e operacionais** entre os módulos da arquitetura TriSLA, garantindo:

- Ordem correta de desenvolvimento
- Identificação de pontos de integração
- Validação de interfaces
- Rastreabilidade de dependências
- Planejamento de testes

---

## 📊 Diagrama de Dependências

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARQUITETURA TRI-SLA                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐
│  1_INFRA   │ (Base - Sem dependências)
└─────────────┘
      │
      ▼
┌─────────────┐
│ 2_SEMANTICA│ (SEM-CSMF)
│            │ Depende de: 1_INFRA
└─────────────┘
      │ I-01 (gRPC)
      ▼
┌─────────────┐
│ 3_ML        │ (ML-NSMF)
│            │ Depende de: 2_SEMANTICA (I-02)
└─────────────┘
      │ I-03 (Kafka)
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DECISION ENGINE (Central)                     │
│                                                                 │
│  Consome:                                                       │
│  - I-01 (SEM-CSMF) → NEST + Metadados                         │
│  - I-02 (ML-NSMF) → Previsão de viabilidade                    │
│  - I-03 (ML-NSMF) → Score de risco                            │
│                                                                 │
│  Gera:                                                          │
│  - Decisão: AC/RENEG/REJ                                       │
│                                                                 │
│  Chama:                                                         │
│  - I-04 (BC-NSSMF) → Registro on-chain                        │
│  - I-06 (SLA-Agent Layer) → Ações corretivas                 │
│  - I-07 (NASP Adapter) → Provisionamento                      │
└─────────────────────────────────────────────────────────────────┘
      │
      ├─── I-04 ───► ┌─────────────┐
      │              │ 4_BLOCKCHAIN│ (BC-NSSMF)
      │              │             │ Depende de: Decision Engine
      │              └─────────────┘
      │
      ├─── I-06 ───► ┌─────────────┐
      │              │ SLA-Agent   │ (3_ML/24_SLA_AGENT_LAYER)
      │              │             │ Depende de: Decision Engine
      │              └─────────────┘
      │
      └─── I-07 ───► ┌─────────────┐
                     │ 6_NASP      │ (NASP Adapter)
                     │             │ Depende de: Decision Engine, 1_INFRA
                     └─────────────┘
                           │
                           ▼
                     ┌─────────────┐
                     │   NASP      │ (Infraestrutura Real)
                     │  (External) │
                     └─────────────┘

┌─────────────┐
│ 5_INTERFACES│ (I-01 a I-07)
│             │ Depende de: Todos os módulos acima
└─────────────┘

┌─────────────┐
│ 7_SLO       │ (SLO Reports)
│             │ Depende de: 6_NASP, 4_BLOCKCHAIN
└─────────────┘

┌─────────────┐
│ 8_CICD      │ (CI/CD Pipeline)
│             │ Depende de: Todos os módulos
└─────────────┘

┌─────────────┐
│ 4_TESTS     │ (Testes)
│             │ Depende de: Todos os módulos
└─────────────┘
```

---

## 🔗 Dependências Detalhadas por Módulo

### 1. SEM-CSMF (2_SEMANTICA)

**Dependências:**
- ✅ **1_INFRA** - Infraestrutura base (PostgreSQL, Kafka, gRPC)
- ✅ **Ontologia OWL** - Arquivo `.owl` desenvolvido em Protégé
- ✅ **Bibliotecas:** RDFLib, OWLReady2, spaCy/NLTK

**Fornece:**
- ✅ **I-01** (gRPC) → Decision Engine: NEST + Metadados

**Ordem de desenvolvimento:**
1. Infraestrutura base (1_INFRA)
2. Ontologia OWL
3. SEM-CSMF
4. Decision Engine (para receber I-01)

---

### 2. ML-NSMF (3_ML)

**Dependências:**
- ✅ **2_SEMANTICA** - Recebe NEST via I-02 (Kafka)
- ✅ **6_NASP** - Coleta métricas reais do NASP
- ✅ **Bibliotecas:** TensorFlow/Keras, scikit-learn, SHAP, LIME

**Fornece:**
- ✅ **I-02** (Kafka) → Decision Engine: Previsão de viabilidade
- ✅ **I-03** (Kafka) → Decision Engine: Score de risco

**Ordem de desenvolvimento:**
1. SEM-CSMF (para receber NEST)
2. NASP Adapter (para métricas)
3. ML-NSMF
4. Decision Engine (para receber I-02 e I-03)

---

### 3. Decision Engine (2_SEMANTICA/22_DECISION_ENGINE)

**Dependências:**
- ✅ **2_SEMANTICA** - Recebe NEST via I-01 (gRPC)
- ✅ **3_ML** - Recebe previsões via I-02 e I-03 (Kafka)
- ✅ **4_BLOCKCHAIN** - Chama I-04 para registro on-chain
- ✅ **3_ML/24_SLA_AGENT_LAYER** - Chama I-06 para ações corretivas
- ✅ **6_NASP** - Chama I-07 para provisionamento

**Fornece:**
- ✅ **Decisão** (AC/RENEG/REJ) para todos os módulos downstream

**Ordem de desenvolvimento:**
1. SEM-CSMF (I-01)
2. ML-NSMF (I-02, I-03)
3. Decision Engine
4. BC-NSSMF (I-04)
5. SLA-Agent Layer (I-06)
6. NASP Adapter (I-07)

---

### 4. BC-NSSMF (4_BLOCKCHAIN)

**Dependências:**
- ✅ **Decision Engine** - Recebe decisão AC via I-04
- ✅ **7_SLO** - Recebe violações para registro on-chain
- ✅ **Blockchain** - Hyperledger Besu/GoQuorum
- ✅ **Smart Contracts** - Solidity

**Fornece:**
- ✅ **Registro on-chain** de SLAs
- ✅ **Auditoria imutável** de violações

**Ordem de desenvolvimento:**
1. Decision Engine (I-04)
2. Blockchain infrastructure
3. Smart Contracts
4. BC-NSSMF

---

### 5. SLA-Agent Layer (3_ML/24_SLA_AGENT_LAYER)

**Dependências:**
- ✅ **Decision Engine** - Recebe comandos via I-06
- ✅ **6_NASP** - Executa ações nos domínios (RAN, Transport, Core)

**Fornece:**
- ✅ **Ações corretivas** nos domínios da rede

**Ordem de desenvolvimento:**
1. Decision Engine (I-06)
2. NASP Adapter (para execução)
3. SLA-Agent Layer

---

### 6. NASP Adapter (6_NASP)

**Dependências:**
- ✅ **Decision Engine** - Recebe comandos via I-07
- ✅ **1_INFRA** - Conectividade com NASP
- ✅ **NASP** - Serviços reais (RAN, Transport, Core)

**Fornece:**
- ✅ **Provisionamento** de slices no NASP
- ✅ **Coleta de métricas** do NASP
- ✅ **Execução de ações** no NASP

**Ordem de desenvolvimento:**
1. Infraestrutura NASP (1_INFRA)
2. Decision Engine (I-07)
3. NASP Adapter

---

### 7. SLO Reports (7_SLO)

**Dependências:**
- ✅ **6_NASP** - Coleta métricas
- ✅ **4_BLOCKCHAIN** - Registra violações on-chain
- ✅ **Prometheus** - Armazena métricas
- ✅ **Grafana** - Visualização

**Fornece:**
- ✅ **Relatórios de SLO** para auditoria

**Ordem de desenvolvimento:**
1. NASP Adapter (métricas)
2. BC-NSSMF (registro)
3. Prometheus/Grafana
4. SLO Reports

---

### 8. Interfaces (5_INTERFACES)

**Dependências:**
- ✅ **Todos os módulos** - Define contratos de comunicação

**Fornece:**
- ✅ **Especificações** de todas as interfaces I-01 a I-07

**Ordem de desenvolvimento:**
1. Definir interfaces antes de implementar módulos
2. Validar interfaces durante desenvolvimento
3. Testar interfaces em integração

---

### 9. Testes (4_TESTS)

**Dependências:**
- ✅ **Todos os módulos** - Testa funcionalidade

**Fornece:**
- ✅ **Validação** de todos os módulos

**Ordem de desenvolvimento:**
1. Unit Tests (após cada módulo)
2. Integration Tests (após integrações)
3. E2E Tests (após stack completo)

---

### 10. CI/CD (8_CICD)

**Dependências:**
- ✅ **Todos os módulos** - Automatiza build e deploy

**Fornece:**
- ✅ **Pipeline** de CI/CD completo

**Ordem de desenvolvimento:**
1. Após todos os módulos implementados
2. Configurar workflows
3. Integrar com GitHub Actions

---

## 📋 Matriz de Dependências

| Módulo | Depende de | Fornece para | Interface |
|--------|------------|--------------|-----------|
| **SEM-CSMF** | 1_INFRA | Decision Engine | I-01 (gRPC) |
| **ML-NSMF** | SEM-CSMF, NASP | Decision Engine | I-02, I-03 (Kafka) |
| **Decision Engine** | SEM-CSMF, ML-NSMF | BC-NSSMF, SLA-Agent, NASP | I-01, I-02, I-03 (in) / I-04, I-06, I-07 (out) |
| **BC-NSSMF** | Decision Engine, SLO | - | I-04 |
| **SLA-Agent** | Decision Engine, NASP | - | I-06 |
| **NASP Adapter** | Decision Engine, 1_INFRA | SLO, ML-NSMF | I-07 |
| **SLO Reports** | NASP, BC-NSSMF | - | - |

---

## 🔄 Fluxo de Dependências

### Fluxo Principal (Happy Path)

```
1. Intent → SEM-CSMF
   └─ Depende: 1_INFRA, Ontologia OWL

2. SEM-CSMF → NEST → Decision Engine (I-01)
   └─ Depende: SEM-CSMF implementado

3. SEM-CSMF → NEST → ML-NSMF (I-02)
   └─ Depende: SEM-CSMF, NASP Adapter (métricas)

4. ML-NSMF → Previsão → Decision Engine (I-02, I-03)
   └─ Depende: ML-NSMF implementado

5. Decision Engine → Decisão AC → BC-NSSMF (I-04)
   └─ Depende: Decision Engine, BC-NSSMF

6. Decision Engine → Comando → NASP Adapter (I-07)
   └─ Depende: Decision Engine, NASP Adapter

7. NASP Adapter → Provisionamento → NASP
   └─ Depende: NASP Adapter, 1_INFRA

8. NASP → Métricas → SLO Reports
   └─ Depende: NASP Adapter, Prometheus

9. SLO Reports → Violação → BC-NSSMF
   └─ Depende: SLO Reports, BC-NSSMF
```

---

## ⚠️ Dependências Críticas

### 1. Decision Engine é Central

- **Todas as decisões** passam pelo Decision Engine
- **Ponto único de falha** - Requer alta disponibilidade
- **Ordem obrigatória:** SEM-CSMF e ML-NSMF antes do Decision Engine

### 2. NASP Adapter é Crítico

- **Única interface** com infraestrutura real
- **Depende de:** 1_INFRA configurada corretamente
- **Ordem obrigatória:** Infraestrutura antes do Adapter

### 3. Blockchain é Isolado

- **Depende apenas** do Decision Engine e SLO Reports
- **Pode ser desenvolvido** em paralelo com outros módulos
- **Ordem:** Após Decision Engine

---

## ✅ Ordem Recomendada de Desenvolvimento

### Fase 1: Infraestrutura Base
1. 1_INFRA - Infraestrutura NASP
2. 5_INTERFACES - Definir interfaces

### Fase 2: Módulos Core
3. 2_SEMANTICA - SEM-CSMF
4. 3_ML - ML-NSMF
5. 2_SEMANTICA/22_DECISION_ENGINE - Decision Engine

### Fase 3: Módulos de Execução
6. 4_BLOCKCHAIN - BC-NSSMF
7. 3_ML/24_SLA_AGENT_LAYER - SLA-Agent Layer
8. 6_NASP - NASP Adapter

### Fase 4: Observabilidade e Relatórios
9. 7_SLO - SLO Reports
10. 3_OBS - Observability

### Fase 5: Testes e CI/CD
11. 4_TESTS - Testes
12. 8_CICD - CI/CD Pipeline

---

## 📚 Referências

- 3GPP TS 28.541 - Network Resource Model
- Interfaces I-01 a I-07 (5_INTERFACES)
- Ordem de Execução (01_ORDEM_EXECUCAO.md)

---

## ✔ Pronto para uso no Cursor

