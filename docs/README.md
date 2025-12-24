# Documentação TriSLA

**TriSLA — Trustworthy, Reasoned and Intelligent SLA Architecture**

Bem-vindo à documentação completa do projeto TriSLA. Este diretório contém toda a documentação técnica, arquitetural e operacional do sistema.

---

## 📋 Índice

1. [Visão Geral](#-visão-geral)
2. [Mapa de Leitura](#-mapa-de-leitura)
3. [Documentação por Módulo](#-documentação-por-módulo)
4. [Documentação Técnica](#-documentação-técnica)
5. [Guias Operacionais](#-guias-operacionais)
6. [Relatórios e Evidências](#-relatórios-e-evidências)

---

## 🎯 Visão Geral

O **TriSLA** é uma arquitetura distribuída e inteligente para gerenciamento automatizado de Service Level Agreements (SLAs) em redes 5G/O-RAN. A arquitetura integra:

- **Interpretação Semântica** (SEM-NSMF): Processamento de intenções usando ontologias OWL
- **Machine Learning** (ML-NSMF): Predição de viabilidade com Explainable AI (XAI)
- **Decisão Automatizada**: Motor de decisão baseado em regras e ML
- **Blockchain** (BC-NSSMF): Registro imutável de SLAs para auditoria
- **Agentes Federados**: Execução distribuída em domínios RAN, Transport e Core
- **Portal de Observabilidade**: Interface web para visualização e gerenciamento

### Documentação Principal

- **[Arquitetura Completa](ARCHITECTURE.md)** — Visão geral da arquitetura TriSLA
- **[Metodologia](METHODOLOGY.md)** — Metodologia de validação e escopo experimental
- **[Qualificação](QUALIFICATION.md)** — Escopo de qualificação e defesa

---

## 🗺️ Mapa de Leitura

### Para Entender a Arquitetura

1. **Iniciantes**: Comece por [ARCHITECTURE.md](ARCHITECTURE.md) para visão geral
2. **Desenvolvedores**: Consulte [deployment/DEVELOPER_GUIDE.md](deployment/DEVELOPER_GUIDE.md)
3. **Operadores**: Veja [deployment/README_OPERATIONS_PROD.md](deployment/README_OPERATIONS_PROD.md)

### Para Trabalhar com Módulos Específicos

Cada módulo possui sua própria documentação:

- **[SEM-NSMF](sem-csmf/)** — Interpretação semântica e geração de NEST
- **[ML-NSMF](ml-nsmf/)** — Predição de viabilidade e XAI
- **[BC-NSSMF](bc-nssmf/)** — Blockchain e smart contracts
- **[Portal](portal/)** — Interface web e observabilidade

### Para Deploy e Operação

- **[Guia Canônico de Instalação](deployment/TRISLA_INSTALLATION_GUIDE.md)** — Instalação pública via Helm
- **[Deploy NASP](nasp/NASP_DEPLOY_GUIDE.md)** — Guia completo de deploy no NASP
- **[Valores de Produção](deployment/VALUES_PRODUCTION_GUIDE.md)** — Configuração de produção
- **[Troubleshooting](reports/TROUBLESHOOTING_TRISLA.md)** — Solução de problemas

---

## 📚 Documentação por Módulo

### SEM-NSMF (Semantic-enhanced Network Slice Management Function)

**Localização**: [`sem-csmf/`](sem-csmf/)

**Documentos principais**:
- [README.md](sem-csmf/README.md) — Visão geral e guia de leitura
- [SEM_CSMF_COMPLETE_GUIDE.md](sem-csmf/SEM_CSMF_COMPLETE_GUIDE.md) — Guia completo
- [ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md](sem-csmf/ontology/ONTOLOGY_IMPLEMENTATION_GUIDE.md) — Ontologia OWL

**Funcionalidades**:
- Recepção de intents de alto nível
- Interpretação semântica usando ontologias OWL
- Geração de Network Slice Templates (NEST)
- Integração com Decision Engine e ML-NSMF

### ML-NSMF (Machine Learning Network Slice Management Function)

**Localização**: [`ml-nsmf/`](ml-nsmf/)

**Documentos principais**:
- [README.md](ml-nsmf/README.md) — Visão geral e guia de leitura
- [ML_NSMF_COMPLETE_GUIDE.md](ml-nsmf/ML_NSMF_COMPLETE_GUIDE.md) — Guia completo

**Funcionalidades**:
- Predição de viabilidade de SLAs
- Explainable AI (XAI) com SHAP/LIME
- Modelo Random Forest treinado
- Integração via Kafka (I-03)

### BC-NSSMF (Blockchain-enabled Network Slice Subnet Management Function)

**Localização**: [`bc-nssmf/`](bc-nssmf/)

**Documentos principais**:
- [README.md](bc-nssmf/README.md) — Visão geral e guia de leitura
- [BC_NSSMF_COMPLETE_GUIDE.md](bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md) — Guia completo

**Funcionalidades**:
- Registro de SLAs em blockchain (Hyperledger Besu)
- Smart contracts Solidity
- Auditoria imutável
- Integração via Kafka (I-04)

### Portal (TriSLA Observability Portal)

**Localização**: [`portal/`](portal/)

**Documentos principais**:
- [README.md](portal/README.md) — Visão geral
- [backend.md](portal/backend.md) — Arquitetura do backend
- [frontend.md](portal/frontend.md) — Arquitetura do frontend

**Funcionalidades**:
- Interface web para visualização de SLAs
- Dashboards de observabilidade
- Criação de SLAs via PLN e Templates NEST
- XAI visualizado

---

## 🔧 Documentação Técnica

### Arquitetura

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Arquitetura completa do TriSLA
- **[architecture/](architecture/)** — Diagramas e especificações detalhadas

### Interfaces

- **I-01 a I-07**: Documentação das interfaces internas (ver README.md raiz do projeto)

### Observabilidade

- **[OBSERVABILITY_v3.7.10.md](OBSERVABILITY_v3.7.10.md)** — Stack de observabilidade
- **[monitoring/](../monitoring/)** — Configuração de Prometheus, Grafana, etc.

### Segurança

- **[security/SECURITY_HARDENING.md](security/SECURITY_HARDENING.md)** — Hardening de segurança

---

## 📖 Guias Operacionais

### Deploy

- **[NASP_DEPLOY_GUIDE.md](nasp/NASP_DEPLOY_GUIDE.md)** — Deploy completo no NASP
- **[NASP_DEPLOY_RUNBOOK.md](nasp/NASP_DEPLOY_RUNBOOK.md)** — Runbook operacional
- **[DEPLOY_v3.7.10.md](deployment/DEPLOY_v3.7.10.md)** — Guia de deploy (versão específica)
- **[BESU_DEPLOY_GUIDE.md](deployment/BESU_DEPLOY_GUIDE.md)** — Deploy do Besu (blockchain)

### Configuração

- **[VALUES_PRODUCTION_GUIDE.md](deployment/VALUES_PRODUCTION_GUIDE.md)** — Valores de produção
- **[INSTALL_FULL_PROD.md](deployment/INSTALL_FULL_PROD.md)** — Instalação completa

### Desenvolvimento

- **[DEVELOPER_GUIDE.md](deployment/DEVELOPER_GUIDE.md)** — Guia para desenvolvedores
- **[CONTRIBUTING.md](deployment/CONTRIBUTING.md)** — Guia de contribuição

### Operações

- **[README_OPERATIONS_PROD.md](deployment/README_OPERATIONS_PROD.md)** — Operações em produção
- **[TROUBLESHOOTING_TRISLA.md](reports/TROUBLESHOOTING_TRISLA.md)** — Troubleshooting

---

## 📊 Relatórios e Evidências

### Relatórios Técnicos

- **[reports/](reports/)** — Relatórios técnicos e de validação
- **[VALIDATION_REPORT_FINAL.md](reports/VALIDATION_REPORT_FINAL.md)** — Relatório final de validação

### Evidências Experimentais

- **[experimentos/](experimentos/)** — Resultados experimentais
- **[CENARIOS_EXPERIMENTAIS.md](experimentos/CENARIOS_EXPERIMENTAIS.md)** — Cenários experimentais
- **[RESULTADOS_BRUTOS.md](experimentos/RESULTADOS_BRUTOS.md)** — Resultados brutos

### Changelogs

- **[CHANGELOG_v3.7.10.md](CHANGELOG_v3.7.10.md)** — Changelog da versão 3.7.10
- **[CHANGELOG_v3.7.9.md](CHANGELOG_v3.7.9.md)** — Changelog da versão 3.7.9

---

## 🔗 Links Rápidos

### Documentação Externa

- **Repositório Principal**: [README.md](../README.md)
- **Helm Charts**: [helm/trisla/README.md](../helm/trisla/README.md)
- **Testes**: [tests/README.md](../tests/README.md)
- **Monitoring**: [monitoring/README.md](../monitoring/README.md)

### Documentação do Portal

A documentação completa do Portal está consolidada em [`portal/`](portal/), mas também pode ser encontrada em [`../trisla-portal/docs/`](../trisla-portal/docs/).

---

## 📝 Convenções

### Nomenclatura

- **SEM-NSMF**: Módulo de interpretação semântica (paths: `sem-csmf/`)
- **ML-NSMF**: Módulo de machine learning
- **BC-NSSMF**: Módulo de blockchain
- **Interfaces**: I-01 a I-07 (conforme especificação O-RAN)

### Versões

- **Versão atual**: v3.7.10
- **Documentação**: Sempre referenciar versão específica quando aplicável

---

## 🆘 Precisa de Ajuda?

1. **Problemas de Deploy**: Consulte [TROUBLESHOOTING_TRISLA.md](reports/TROUBLESHOOTING_TRISLA.md)
2. **Dúvidas sobre Módulos**: Veja os READMEs específicos de cada módulo
3. **Questões de Arquitetura**: Consulte [ARCHITECTURE.md](ARCHITECTURE.md)
4. **Metodologia**: Veja [METHODOLOGY.md](METHODOLOGY.md)

---

**Última atualização**: 2025-01-27  
**Versão da documentação**: S4.0

