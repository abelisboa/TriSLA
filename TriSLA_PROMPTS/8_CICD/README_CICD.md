# README - CI/CD Pipeline

**TriSLA – Continuous Integration and Continuous Deployment**

---

## 🎯 Função do Módulo

O **CI/CD Pipeline** é responsável por:

1. **Automatizar testes** (unit, integration, E2E, security, load)
2. **Build de imagens Docker** para todos os módulos
3. **Push para GHCR** (GitHub Container Registry)
4. **Deploy automático** via Helm charts
5. **Quality gates** antes de merge
6. **Notificações** de status

---

## 📥 Entradas

### 1. Código Fonte

- Código de todos os módulos
- Testes automatizados
- Configurações (Helm, Docker, etc.)

### 2. Triggers

- **Push** para branches (main, develop)
- **Pull Requests**
- **Tags** (v1.0.0, etc.)
- **Manual** (workflow_dispatch)

---

## 📤 Saídas

### 1. Imagens Docker

- `ghcr.io/owner/sem-csmf:latest`
- `ghcr.io/owner/ml-nsmf:latest`
- `ghcr.io/owner/decision-engine:latest`
- `ghcr.io/owner/bc-nssmf:latest`
- `ghcr.io/owner/nasp-adapter:latest`

### 2. Relatórios

- **Testes** - Cobertura, resultados
- **Segurança** - Vulnerabilidades
- **Performance** - Métricas de carga
- **Deploy** - Status de deployment

---

## 🔗 Integrações

### GitHub Actions

**Workflows:**
- `unit-tests.yml` - Testes unitários
- `integration-tests.yml` - Testes de integração
- `e2e-tests.yml` - Testes E2E
- `security-tests.yml` - Testes de segurança
- `load-tests.yml` - Testes de carga
- `build-push.yml` - Build e push
- `ci-cd.yml` - Pipeline completo

### GitHub Container Registry (GHCR)

**Fluxo:**
1. Build de imagens Docker
2. Push para GHCR
3. Tagging semântico (v1.0.0)

### Kubernetes / Helm

**Fluxo:**
1. Deploy via Helm charts
2. Validação de deployment
3. Health checks

---

## 🎯 Responsabilidades

1. **Automação** de testes e builds
2. **Quality gates** antes de merge
3. **Versionamento** semântico
4. **Deploy automático** para staging/production
5. **Rollback** automático em caso de falha
6. **Notificações** (Slack, Email)

---

## 🔄 Relação com Decision Engine

O CI/CD Pipeline **não se comunica diretamente** com o Decision Engine:

- **Testa:** Todos os módulos, incluindo Decision Engine
- **Deploya:** Todos os módulos, incluindo Decision Engine
- **Relação:** Indireta (via testes e deploy)

---

## 📋 Requisitos Técnicos

### Tecnologias

- **GitHub Actions** - CI/CD platform
- **Docker** - Containerização
- **GitHub Container Registry** - Image registry
- **Helm** - Kubernetes package manager
- **Kubernetes** - Orchestration

### Dependências

- **Todos os módulos** - Para build e deploy
- **4_TESTS** - Para execução de testes
- **Infraestrutura** - Para deploy

---

## 📚 Referências à Dissertação

- **Capítulo 5** - Implementação e Validação
- **CI/CD** - Automação e qualidade
- **DevOps** - Práticas de desenvolvimento

---

## ✔ Pipeline Completo e Documentado

