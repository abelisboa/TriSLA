# README Geral - TriSLA_PROMPTS

**Documentação Central do Projeto TriSLA**

---

## 📋 Visão Geral

O **TriSLA (Triple-SLA)** é uma arquitetura completa para gerenciamento de Service Level Agreements (SLAs) em redes 5G, integrando:

- **Semântica** (SEM-CSMF) - Interpretação de intenções e geração de NEST
- **Machine Learning** (ML-NSMF) - Previsão de viabilidade de SLAs
- **Blockchain** (BC-NSSMF) - Registro imutável e auditoria on-chain
- **Decision Engine** - Orquestração central de decisões
- **NASP Integration** - Integração com infraestrutura real 5G

---

## 🗂️ Estrutura do Diretório

```
TriSLA_PROMPTS/
├── 0_MASTER/          # Planejamento e estratégia
├── 1_INFRA/           # Infraestrutura NASP
├── 2_SEMANTICA/       # SEM-CSMF e Decision Engine
├── 3_ML/              # ML-NSMF e SLA-Agent Layer
├── 4_BLOCKCHAIN/      # BC-NSSMF
├── 4_TESTS/           # Testes (Unit, Integration, E2E, Security, Load)
├── 5_INTERFACES/      # Interfaces I-01 a I-07
├── 6_NASP/            # Integração NASP
├── 7_SLO/             # SLO Reports
├── 8_CICD/            # CI/CD Pipeline
└── 9_VALIDACAO/       # Validação final
```

---

## 🚀 Início Rápido

### 1. Leia a Ordem de Execução

Consulte `0_MASTER/01_ORDEM_EXECUCAO.md` para entender a sequência correta de desenvolvimento.

### 2. Entenda as Dependências

Consulte `0_MASTER/03_MAPA_DEPENDENCIAS_TRISLA.md` para mapear dependências entre módulos.

### 3. Execute os Prompts em Ordem

Siga a ordem definida em `01_ORDEM_EXECUCAO.md`, começando pela infraestrutura base.

---

## 📚 Documentação por Módulo

- **SEM-CSMF:** `2_SEMANTICA/README_SEM.md`
- **ML-NSMF:** `3_ML/README_ML.md`
- **BC-NSSMF:** `4_BLOCKCHAIN/README_BLOCKCHAIN.md`
- **Testes:** `4_TESTS/README_TESTS.md`
- **NASP:** `6_NASP/README_NASP.md`
- **SLO:** `7_SLO/README_SLO.md`
- **CI/CD:** `8_CICD/README_CICD.md`

---

## 🔗 Referências

- Dissertação - Capítulos 4 e 5
- 3GPP TS 28.541 - Network Resource Model
- Interfaces I-01 a I-07

---

## ✔ Documentação Completa

