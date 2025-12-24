# TriSLA — Trustworthy, Reasoned and Intelligent SLA Architecture

**Versão Pública:** 1.0.0  
**Data de Publicação:** 2025-01-27  
**Licença:** MIT

---

## 📋 Resumo

O **TriSLA** é uma arquitetura distribuída e inteligente para gerenciamento automatizado de Service Level Agreements (SLAs) em redes 5G/O-RAN. A arquitetura integra técnicas de Processamento de Linguagem Natural (PLN), Machine Learning com Explainable AI (XAI), ontologias semânticas OWL e blockchain para fornecer um sistema completo de gerenciamento de SLAs com transparência, rastreabilidade e auditoria.

### Contribuições Científicas Principais

1. **Interpretação Semântica de Intents**: Uso de ontologias OWL para validação semântica de requisitos de SLA
2. **Predição de Viabilidade com XAI**: Modelo de Machine Learning (Random Forest) com explicações transparentes usando SHAP/LIME
3. **Registro Imutável em Blockchain**: Uso de Hyperledger Besu para auditoria e rastreabilidade de SLAs
4. **Arquitetura Federada**: Execução distribuída em múltiplos domínios (RAN, Transport, Core)
5. **Portal de Observabilidade**: Interface web completa para visualização e gerenciamento

---

## 🏗️ Arquitetura

O TriSLA é composto pelos seguintes módulos principais:

- **SEM-NSMF** (Semantic-enhanced Network Slice Management Function): Interpretação semântica de intents e geração de Network Slice Templates (NEST)
- **ML-NSMF** (Machine Learning Network Slice Management Function): Predição de viabilidade de SLAs com Explainable AI
- **Decision Engine**: Motor de decisão que agrega informações de múltiplas fontes
- **BC-NSSMF** (Blockchain-enabled Network Slice Subnet Management Function): Registro imutável de SLAs em blockchain
- **SLA-Agent Layer**: Execução distribuída em domínios de rede
- **Portal**: Interface web de observabilidade e gerenciamento

**Documentação completa da arquitetura:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## 📚 Documentação

A documentação completa está disponível em [`docs/`](docs/):

- **[README.md](docs/README.md)** — Mapa de leitura e índice completo
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** — Arquitetura detalhada do sistema
- **[METHODOLOGY.md](docs/METHODOLOGY.md)** — Metodologia de validação
- **[QUALIFICATION.md](docs/QUALIFICATION.md)** — Escopo de qualificação

### Documentação por Módulo

- **[SEM-NSMF](docs/sem-csmf/)** — Interpretação semântica e ontologias OWL
- **[ML-NSMF](docs/ml-nsmf/)** — Machine Learning e Explainable AI
- **[BC-NSSMF](docs/bc-nssmf/)** — Blockchain e smart contracts
- **[Portal](docs/portal/)** — Interface web e observabilidade

---

## 🔬 Escopo da Versão Pública

Esta versão pública contém:

- ✅ **Documentação completa** da arquitetura e metodologia
- ✅ **Código-fonte** dos módulos principais
- ✅ **Helm charts** para deploy em Kubernetes
- ✅ **Especificações** de interfaces e contratos
- ✅ **Guias de desenvolvimento** e contribuição

### Nota Importante

**Componentes blockchain e agentes são documentados conceitualmente; imagens Docker e execução real ocorrem em ambiente experimental controlado.**

Esta versão pública é adequada para:
- Revisão acadêmica e banca examinadora
- Reprodução conceitual da arquitetura
- Desenvolvimento e extensão do sistema
- Estudos e pesquisas relacionadas

---

## 🚀 Installation

Para instalar o TriSLA em um cluster Kubernetes, consulte o [Guia Canônico de Instalação](docs/deployment/TRISLA_INSTALLATION_GUIDE.md).

**Pré-requisitos:**
- Kubernetes ≥ 1.24
- Helm ≥ 3.8
- Acesso ao GHCR (`ghcr.io/abelisboa`)

**Instalação rápida:**
```bash
kubectl create namespace trisla
helm upgrade --install trisla helm/trisla \
  --namespace trisla \
  --set semCsmf.enabled=true \
  --set mlNsmf.enabled=true \
  --set bcNssmf.enabled=true \
  --set global.imagePullSecrets=[] \
  --wait
```

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.10+
- Kubernetes 1.24+ (para deploy completo)
- Docker (para desenvolvimento local)
- Helm 3.8+ (para deploy via Helm)

### Estrutura do Projeto

```
TriSLA/
├── apps/              # Módulos principais
│   ├── sem-csmf/     # SEM-NSMF
│   ├── ml-nsmf/      # ML-NSMF
│   ├── bc-nssmf/     # BC-NSSMF
│   ├── decision-engine/
│   └── ...
├── docs/              # Documentação completa
├── helm/              # Helm charts
└── README.md          # Este arquivo
```

### Desenvolvimento Local

Consulte [`docs/deployment/DEVELOPER_GUIDE.md`](docs/deployment/DEVELOPER_GUIDE.md) para instruções detalhadas de desenvolvimento local.

---

## 📖 Citação

Se você usar o TriSLA em sua pesquisa, por favor cite:

```bibtex
@software{trisla2025,
  title = {TriSLA - Trustworthy, Reasoned and Intelligent SLA Architecture},
  author = {TriSLA Project},
  year = {2025},
  version = {1.0.0},
  license = {MIT},
  url = {https://github.com/yourusername/trisla}
}
```

Ou use o arquivo [`CITATION.cff`](CITATION.cff) para citação automática.

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, consulte [`docs/deployment/CONTRIBUTING.md`](docs/deployment/CONTRIBUTING.md) para diretrizes de contribuição.

---

## 📧 Contato

Para questões acadêmicas ou técnicas, consulte a documentação em [`docs/`](docs/).

---

## 🔗 Links Úteis

- **Documentação Completa**: [`docs/README.md`](docs/README.md)
- **Arquitetura**: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- **Metodologia**: [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md)
- **Qualificação**: [`docs/QUALIFICATION.md`](docs/QUALIFICATION.md)

---

**Última atualização:** 2025-01-27  
**Versão:** 1.0.0 (Public Release)

