# TriSLA — Guia de Instalação Completa para Produção

## 1. Introduction

### 1.1 Objetivo this Documento

This document provides instruções completas e automatizadas para instalar o **TriSLA** (Triple-SLA) in production environment real no **NASP** (Network Automation & Slicing Platform). O guia cobre múltiplos métodos de instalação, desde scripts automatizados até pipelines CI/CD completos.

### 1.2 Methods de Instalação Disponíveis

O TriSLA pode ser instalado através dos seguintes métodos:

1. **Scripts Automatizados**: Instalação rápida via scripts bash
2. **Docker Compose**: Instalação local para desenvolvimento e testes
3. **Helm Charts**: Instalação em Kubernetes (método recomendado para produção)
4. **Ansible Playbooks**: Instalação automatizada e idempotente
5. **CI/CD Pipeline**: Instalação automatizada via GitHub Actions

### 1.3 Pré-requisitos Gerais

Antes de iniciar qualquer método de instalação, certifique-se de possuir:

- **Acesso ao cluster Kubernetes** (NASP ou outro)
- **kubectl** configurado e conectado ao cluster (versão ≥ 1.26)
- **Helm** instalado (versão ≥ 3.12) — para métodos Helm
- **Docker** ou **containerd** — para métodos Docker Compose
- **Ansible** instalado (versão ≥ 2.14) — para métodos Ansible
- **Acesso ao GitHub Container Registry (GHCR)** — para pull de imagens
- **Credenciais do NASP** — para integration com a plataforma

### 1.4 Estrutura do Documento

Este documento está organizado por método de instalação, permitindo que o operador escolha o método mais adequado ao seu ambiente. Cada section é independente e pode ser seguida isoladamente.

---

## 2. Fluxo de Instalação em Alto Nível

### 2.1 Visão Geral do Processo

O processo de instalação do TriSLA segue os seguintes passos principais:

```
1. Preparação do Ambiente
   ├── Verifiesr pré-requisitos
   ├── Configurar acesso ao cluster
   ├── Criar secrets necessários
   └── Validar conectividade

2. Configuração
   ├── Detectar configurações de rede
   ├── Gerar arquivos de configuração
   └── Validar configurações

3. Deploy
   ├── Instalar dependências (PostgreSQL, Kafka)
   ├── Instalar módulos TriSLA
   └── Configurar observabilidade

4. Validação
   ├── Verifiesr saúde dos pods
   ├── Testar endpoints
   ├── Validar integration com NASP
   └── Executar testes E2E

5. Finalização
   ├── Configurar monitoramento
   ├── Configurar alertas
   └── Documentar instalação
```

### 2.2 Ordem Recomendada de Instalação

Para instalação em produção, recomenda-se a seguinte ordem:

1. **Preparação**: Executar pre-flight checks
2. **Configuração**: Auto-configurar ou configurar manualmente
3. **Deploy**: Escolher método (Helm recomendado)
4. **Validação**: Executar validações automáticas
5. **Testes**: Executar testes E2E
6. **Monitoramento**: Configurar observabilidade

### 2.3 Decisão de Method

**Use Scripts Automatizados quando:**
- Precisa de instalação rápida
- Ambiente padrão NASP
- Primeira instalação

**Use Docker Compose quando:**
- Ambiente de desenvolvimento
- Testes locais
- Não possui cluster Kubernetes

**Use Helm quando:**
- Produção real
- Precisa de controle granular
- Ambiente Kubernetes padrão

**Use Ansible quando:**
- Múltiplos ambientes
- Precisa de idempotência
- Automação completa

**Use CI/CD quando:**
- Deploy automatizado
- Integração contínua
- Múltiplos ambientes

---

## 3. Instalação via Scripts do Repositório

### 3.1 Visão Geral dos Scripts

O repositório TriSLA inclui scripts automatizados para facilitar a instalação:

- `auto-config-nasp.sh`: Auto-configuração do ambiente NASP
- `deploy-trisla-nasp.sh`: Deploy completo do TriSLA
- `validate-nasp-infra.sh`: Validação da infraestrutura

### 3.2 auto-config-nasp.sh

**Objetivo**: Detectar automaticamente configurações de rede do NASP e gerar arquivos de configuração.

**Uso:**

```bash
# Navegar para o diretório do repositório
cd TriSLA-clean

# Executar auto-configuração
./scripts/auto-config-nasp.sh
```

**O que o script faz:**

1. Detecta interface de rede principal (`my5g`)
2. Identifica IP do nó Kubernetes
3. Identifica gateway padrão
4. Gera `configs/generated/trisla_values_autogen.yaml`
5. Gera `configs/generated/inventory_autogen.yaml` (Ansible)
6. Gera trechos para `values-nasp.yaml`

**Saída esperada:**

```
🔍 Coletando informações do NASP...
Interface física principal detectada: my5g
IP utilizado pelo Kubernetes: 192.168.10.16
Gateway default: 192.168.10.1
✅ Configurações geradas em: configs/generated/
```

**Arquivos gerados:**

```bash
# Verifiesr arquivos gerados
ls -la configs/generated/

# Ver conteúdo do values gerado
cat configs/generated/trisla_values_autogen.yaml
```

**Integração com values-nasp.yaml:**

```bash
# Copiar configurações geradas para values-nasp.yaml
cat configs/generated/trisla_values_autogen.yaml >> helm/trisla/values-nasp.yaml

# Ou usar diretamente
cp configs/generated/trisla_values_autogen.yaml helm/trisla/values-nasp.yaml
```

### 3.3 deploy-trisla-nasp.sh

**Objetivo**: Deploy completo e automatizado do TriSLA no NASP.

**Uso básico:**

```bash
# Deploy completo (recomendado)
./scripts/deploy-trisla-nasp.sh --pre-flight --helm-install --health-check
```

**Opções disponíveis:**

```bash
# Apenas pre-flight
./scripts/deploy-trisla-nasp.sh --pre-flight

# Apenas instalação Helm
./scripts/deploy-trisla-nasp.sh --helm-install

# Upgrade Helm
./scripts/deploy-trisla-nasp.sh --helm-upgrade

# Health check após deploy
./scripts/deploy-trisla-nasp.sh --health-check

# Exibir logs
./scripts/deploy-trisla-nasp.sh --logs

# Todas as opções
./scripts/deploy-trisla-nasp.sh --pre-flight --helm-install --health-check --logs
```

**Variáveis de ambiente:**

```bash
# Configurar variáveis antes de executar
export TRISLA_NAMESPACE=trisla
export TRISLA_HELM_RELEASE=trisla
export TRISLA_VALUES_FILE=helm/trisla/values-nasp.yaml
export GHCR_REGISTRY=ghcr.io/abelisboa

# Executar script
./scripts/deploy-trisla-nasp.sh --helm-install
```

**Fluxo do script:**

1. **Pre-flight checks** (se `--pre-flight`):
   - Verifies kubectl
   - Verifies Helm
   - Verifies cluster Kubernetes
   - Verifies namespace
   - Verifies secrets

2. **Deploy Helm** (se `--helm-install` ou `--helm-upgrade`):
   - Valida Helm chart
   - Executa `helm upgrade --install`
   - Waits pods ficarem prontos

3. **Health check** (se `--health-check`):
   - Verifies status dos pods
   - Testa health endpoints
   - Valida conectividade

4. **Logs** (se `--logs`):
   - Exibe logs dos módulos
   - Exibe eventos do Kubernetes

**Exemplo de saída:**

```
[INFO] 🔍 Executando pre-flight checks...
[INFO] ✅ kubectl encontrado
[INFO] ✅ Helm encontrado
[INFO] ✅ Cluster Kubernetes acessível
[INFO] 🚀 Iniciando deploy do TriSLA...
[INFO] ✅ Deploy concluído com sucesso
[INFO] 🔍 Executando health checks...
[INFO] ✅ Todos os módulos estão saudáveis
```

### 3.4 validate-nasp-infra.sh

**Objetivo**: Validar infraestrutura NASP antes e após instalação.

**Uso:**

```bash
# Validação completa
./scripts/validate-nasp-infra.sh

# Validação específica
./scripts/validate-nasp-infra.sh --network
./scripts/validate-nasp-infra.sh --storage
./scripts/validate-nasp-infra.sh --dns
```

**O que o script valida:**

1. **Rede**:
   - Conectividade entre nós
   - Calico funcionando
   - Network Policies

2. **Storage**:
   - StorageClass disponível
   - PVCs podem ser criados
   - Espaço disponível

3. **DNS**:
   - CoreDNS funcionando
   - Resolução de nomes
   - Resolução de serviços

4. **Kubernetes**:
   - Nodes em estado Ready
   - Control plane funcionando
   - RBAC configurado

**Exemplo de saída:**

```
🔍 Validando infraestrutura NASP...
✅ Rede: OK
✅ Storage: OK
✅ DNS: OK
✅ Kubernetes: OK
✅ Infraestrutura validada com sucesso
```

### 3.5 Instalação Completa via Scripts

**Fluxo completo recomendado:**

```bash
# 1. Auto-configurar ambiente
./scripts/auto-config-nasp.sh

# 2. Validar infraestrutura
./scripts/validate-nasp-infra.sh

# 3. Deploy completo
./scripts/deploy-trisla-nasp.sh --pre-flight --helm-install --health-check

# 4. Validar após deploy
./scripts/validate-nasp-infra.sh
```

---

## 4. Instalação via Docker Compose (Modo Local)

### 4.1 Visão Geral

O Docker Compose é ideal para instalação local, desenvolvimento e testes. Não é recomendado para produção, mas é útil para validação antes do deploy em Kubernetes.

### 4.2 Pré-requisitos

```bash
# Verifiesr Docker
docker --version
docker-compose --version

# Verifiesr se Docker está rodando
docker ps
```

### 4.3 Instalação

**Passo 1: Preparar ambiente**

```bash
# Navegar para diretório do repositório
cd TriSLA-clean

# Verifiesr docker-compose.yml
cat docker-compose.yml
```

**Passo 2: Configurar variáveis de ambiente**

```bash
# Criar arquivo .env (opcional)
cat <<EOF > .env
POSTGRES_PASSWORD=trisla_password
JWT_SECRET_KEY=$(openssl rand -base64 32)
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
OTLP_ENDPOINT=http://otlp-collector:4317
EOF
```

**Passo 3: Iniciar serviços**

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verifiesr status
docker-compose ps

# Ver logs
docker-compose logs -f
```

**Passo 4: Verifiesr serviços**

```bash
# Verifiesr saúde dos serviços
curl http://localhost:8080/health  # SEM-CSMF
curl http://localhost:8081/health  # ML-NSMF
curl http://localhost:8082/health  # Decision Engine
curl http://localhost:8083/health  # BC-NSSMF
curl http://localhost:8084/health  # SLA-Agent Layer
curl http://localhost:8085/health  # NASP Adapter

# Verifiesr Prometheus
curl http://localhost:9090/-/healthy

# Verifiesr Grafana
curl http://localhost:3000/api/health
```

### 4.4 Configuração Avançada

**Modificar docker-compose.yml:**

```yaml
# Exemplo: Aumentar recursos do ML-NSMF
ml-nsmf:
  deploy:
    resources:
      limits:
        cpus: '4'
        memory: 4G
      reservations:
        cpus: '1'
        memory: 1G
```

**Variáveis de ambiente por serviço:**

```yaml
sem-csmf:
  environment:
    - LOG_LEVEL=DEBUG
    - DATABASE_URL=postgresql://trisla:trisla_password@postgres:5432/trisla
    - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

### 4.5 Parar e Limpar

```bash
# Parar serviços
docker-compose stop

# Parar e remover containers
docker-compose down

# Parar, remover containers e volumes
docker-compose down -v

# Remover imagens também
docker-compose down --rmi all
```

### 4.6 Limitações do Docker Compose

- **Não é adequado para produção**: Falta alta disponibilidade
- **Recursos limitados**: Depende dos recursos da máquina local
- **Sem auto-scaling**: Não escala automaticamente
- **Sem Network Policies**: Menor isolamento de rede

---

## 5. Instalação via Helm (Produção)

### 5.1 Visão Geral

Helm é o método **recomendado** para instalação em produção. Oferece controle granular, versionamento e facilita upgrades e rollbacks.

### 5.2 Pré-requisitos

```bash
# Verifiesr Helm
helm version

# Verifiesr acesso ao cluster
kubectl cluster-info
kubectl get nodes
```

### 5.3 Preparação

**Passo 1: Criar namespace**

```bash
# Criar namespace
kubectl create namespace trisla

# Adicionar labels
kubectl label namespace trisla name=trisla environment=production
```

**Passo 2: Criar secrets**

```bash
# Secret para GHCR
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USERNAME> \
  --docker-password=<GITHUB_PAT_TOKEN> \
  --docker-email=<GITHUB_EMAIL> \
  --namespace=trisla

# Secret para NASP (se necessário)
kubectl create secret generic nasp-credentials \
  --from-literal=auth-token="<NASP_AUTH_TOKEN>" \
  --namespace=trisla
```

**Passo 3: Preparar values-nasp.yaml**

```bash
# Copiar template
cp helm/trisla/values.yaml helm/trisla/values-nasp.yaml

# Editar valores
vim helm/trisla/values-nasp.yaml

# Ou usar auto-config
./scripts/auto-config-nasp.sh
cat configs/generated/trisla_values_autogen.yaml >> helm/trisla/values-nasp.yaml
```

### 5.4 Instalação

**Method 1: Instalação inicial**

```bash
# Validar chart
helm lint ./helm/trisla

# Dry-run
helm install trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml \
  --dry-run \
  --debug

# Instalação real
helm install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

**Method 2: Upgrade/Install (recomendado)**

```bash
# Upgrade ou install (idempotente)
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

**Method 3: Com rollback automático**

```bash
# Com rollback automático em caso de falha
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --atomic \
  --wait \
  --timeout 15m
```

### 5.5 Verifiesção

```bash
# Verifiesr status do release
helm status trisla -n trisla

# Verifiesr pods
kubectl get pods -n trisla

# Verifiesr serviços
kubectl get svc -n trisla

# Verifiesr ingress
kubectl get ingress -n trisla
```

### 5.6 Configurações Avançadas

**Instalação com múltiplos values files:**

```bash
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values.yaml \
  --values ./helm/trisla/values-nasp.yaml \
  --values ./helm/trisla/values-nasp.yaml
```

**Instalação com set de valores:**

```bash
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --set semCsmf.replicas=3 \
  --set mlNsmf.resources.limits.memory=8Gi \
  --values ./helm/trisla/values-nasp.yaml
```

---

## 6. Instalação via Ansible (Opcional, mas Detalhado)

### 6.1 Visão Geral

Ansible oferece instalação automatizada, idempotente e repetível. Ideal para múltiplos ambientes e automação completa.

### 6.2 Pré-requisitos

```bash
# Instalar Ansible
pip install ansible

# Verifiesr instalação
ansible --version

# Instalar coleções necessárias
ansible-galaxy collection install kubernetes.core
```

### 6.3 Configuração do Inventory

**Editar inventory.yaml:**

```bash
cd TriSLA-clean/ansible
vim inventory.yaml
```

**Exemplo de inventory.yaml:**

```yaml
all:
  children:
    nasp_nodes:
      hosts:
        node1:
          ansible_host: 192.168.10.16
          iface: my5g
        node2:
          ansible_host: 192.168.10.17
          iface: my5g
    
    control_plane:
      hosts:
        node1: {}
        node2: {}
  
  vars:
    ansible_user: root
    ansible_ssh_common_args: '-o StrictHostKeyChecking=no'
    trisla_namespace: trisla
    trisla_image_registry: ghcr.io/abelisboa
```

### 6.4 Executar Playbooks

**Pre-flight:**

```bash
# Executar pre-flight checks
ansible-playbook -i inventory.yaml playbooks/pre-flight.yml
```

**Setup de namespace:**

```bash
# Criar namespace
ansible-playbook -i inventory.yaml playbooks/setup-namespace.yml
```

**Deploy completo:**

```bash
# Deploy completo do TriSLA
ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml
```

**Validação:**

```bash
# Validar cluster
ansible-playbook -i inventory.yaml playbooks/validate-cluster.yml
```

### 6.5 Variáveis do Ansible

**Editar group_vars/all.yml:**

```yaml
trisla:
  namespace: trisla
  image_registry: ghcr.io/abelisboa
  version: latest
  helm_chart_path: ./helm/trisla
  values_file: ./helm/trisla/values-nasp.yaml
```

**Variáveis de ambiente:**

```bash
# Passar variáveis via linha de comando
ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml \
  -e "trisla_namespace=trisla" \
  -e "trisla_image_registry=ghcr.io/abelisboa"
```

### 6.6 Vantagens do Ansible

- **Idempotência**: Executar múltiplas vezes produz o mesmo resultado
- **Repetibilidade**: Mesmo resultado em diferentes ambientes
- **Automação completa**: Cobre todo o processo de instalação
- **Inventário centralizado**: Gerencia múltiplos ambientes

---

## 7. Instalação via CI/CD (GitHub Actions)

### 7.1 Visão Geral

GitHub Actions permite instalação automatizada via pipeline CI/CD. Ideal para deploy contínuo e múltiplos ambientes.

### 7.2 Estrutura do Workflow

**File: `.github/workflows/deploy-production.yml`**

```yaml
name: Deploy TriSLA to Production

on:
  push:
    branches:
      - main
    paths:
      - 'helm/**'
      - '.github/workflows/deploy-production.yml'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy'
        required: true
        default: 'production'
        type: choice
        options:
          - production
          - staging

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment || 'production' }}
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Setup kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.26.0'
      
      - name: Setup Helm
        uses: azure/setup-helm@v3
        with:
          version: 'v3.12.0'
      
      - name: Configure kubeconfig
        run: |
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > $HOME/.kube/config
          kubectl cluster-info
      
      - name: Create namespace
        run: |
          kubectl create namespace trisla --dry-run=client -o yaml | kubectl apply -f -
      
      - name: Create GHCR secret
        run: |
          kubectl create secret docker-registry ghcr-secret \
            --docker-server=ghcr.io \
            --docker-username=${{ secrets.GHCR_USERNAME }} \
            --docker-password=${{ secrets.GHCR_TOKEN }} \
            --docker-email=${{ secrets.GHCR_EMAIL }} \
            --namespace=trisla \
            --dry-run=client -o yaml | kubectl apply -f -
      
      - name: Deploy with Helm
        run: |
          helm upgrade --install trisla ./helm/trisla \
            --namespace trisla \
            --create-namespace \
            --values ./helm/trisla/values-nasp.yaml \
            --wait \
            --timeout 15m
      
      - name: Verify deployment
        run: |
          kubectl get pods -n trisla
          kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=trisla -n trisla --timeout=5m
      
      - name: Health check
        run: |
          ./scripts/validate-production-real.sh
```

### 7.3 Configurar Secrets no GitHub

**Secrets necessários:**

1. `KUBECONFIG`: Configuração do cluster Kubernetes (base64 encoded)
2. `GHCR_USERNAME`: Usuário do GitHub
3. `GHCR_TOKEN`: Personal Access Token do GitHub
4. `GHCR_EMAIL`: Email do GitHub

**Como configurar:**

1. Acessar: `https://github.com/<repo>/settings/secrets/actions`
2. Adicionar cada secret
3. Workflow usará automaticamente

### 7.4 Executar Deploy

**Method 1: Push para main**

```bash
# Push para branch main dispara deploy automático
git push origin main
```

**Method 2: Workflow dispatch**

1. Acessar: `https://github.com/<repo>/actions`
2. Selecionar workflow "Deploy TriSLA to Production"
3. Clicar em "Run workflow"
4. Selecionar ambiente
5. Executar

### 7.5 Monitoramento do Deploy

**Ver logs do workflow:**

1. Acessar: `https://github.com/<repo>/actions`
2. Clicar no workflow run
3. Ver logs de cada step

**Notificações:**

```yaml
# Adicionar notificações ao workflow
- name: Notify on success
  if: success()
  uses: 8398a7/action-slack@v3
  with:
    status: success
    text: 'TriSLA deployed successfully!'
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    text: 'TriSLA deployment failed!'
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 8. Atualização de Versão

### 8.1 Atualização via Helm

**Method 1: Atualizar values e fazer upgrade**

```bash
# 1. Atualizar values-nasp.yaml com nova versão
vim helm/trisla/values-nasp.yaml
# Alterar: tag: "v1.1.0"

# 2. Fazer upgrade
helm upgrade trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

**Method 2: Atualizar apenas imagens**

```bash
# Atualizar tag de imagem específica
helm upgrade trisla ./helm/trisla \
  --namespace trisla \
  --set semCsmf.image.tag=v1.1.0 \
  --reuse-values \
  --wait
```

**Method 3: Atualizar todas as imagens**

```bash
# Atualizar todas as imagens para nova versão
helm upgrade trisla ./helm/trisla \
  --namespace trisla \
  --set global.imageTag=v1.1.0 \
  --reuse-values \
  --wait
```

### 8.2 Atualização via Scripts

```bash
# Atualizar via script
export TRISLA_CHART_VERSION=v1.1.0
./scripts/deploy-trisla-nasp.sh --helm-upgrade --health-check
```

### 8.3 Atualização via Ansible

```bash
# Atualizar variável de versão
ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml \
  -e "trisla_version=v1.1.0"
```

### 8.4 Verifiesção Pós-Atualização

```bash
# Verifiesr versão dos pods
kubectl get pods -n trisla -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\n"}{end}'

# Verifiesr health
./scripts/validate-production-real.sh

# Verifiesr logs
kubectl logs -n trisla -l app=sem-csmf --tail=50
```

---

## 9. Rollback

### 9.1 Rollback via Helm

**Ver histórico de releases:**

```bash
# Listar histórico
helm history trisla -n trisla

# Ver detalhes de uma revisão
helm get manifest trisla -n trisla --revision 3
```

**Rollback para versão anterior:**

```bash
# Rollback para última versão estável
helm rollback trisla -n trisla

# Rollback para revisão específica
helm rollback trisla <revision-number> -n trisla

# Verifiesr status após rollback
helm status trisla -n trisla
kubectl get pods -n trisla
```

**Rollback com validação:**

```bash
# Rollback e aguardar
helm rollback trisla -n trisla --wait --timeout 10m

# Validar após rollback
./scripts/validate-production-real.sh
```

### 9.2 Rollback via Scripts

```bash
# Rollback via script
./scripts/rollback.sh

# Ou manualmente
helm rollback trisla -n trisla
```

### 9.3 Rollback Manual

**Se Helm não estiver disponível:**

```bash
# 1. Deletar release atual
helm uninstall trisla -n trisla

# 2. Reinstalar versão anterior
helm install trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml.backup \
  --version <previous-version>
```

### 9.4 Rollback de Dados

**Se necessário rollback de banco de dados:**

```bash
# Restaurar backup do PostgreSQL
./scripts/restore-postgres.sh <backup-file>

# Ou manualmente
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- \
  pg_restore -U trisla -d trisla < backup.sql
```

---

## 10. Migração de Dados (se Existir)

### 10.1 Backup Antes de Migração

**Backup do PostgreSQL:**

```bash
# Via script
./scripts/backup-postgres.sh

# Ou manualmente
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- \
  pg_dump -U trisla trisla > backup-$(date +%Y%m%d-%H%M%S).sql
```

**Backup de ConfigMaps e Secrets:**

```bash
# Backup de ConfigMaps
kubectl get configmap -n trisla -o yaml > configmaps-backup.yaml

# Backup de Secrets (sem dados sensíveis)
kubectl get secret -n trisla -o yaml > secrets-backup.yaml
```

### 10.2 Migração de Dados

**Migração do PostgreSQL:**

```bash
# 1. Fazer backup
./scripts/backup-postgres.sh

# 2. Parar aplicação (opcional, para migração sem downtime)
kubectl scale deployment sem-csmf -n trisla --replicas=0

# 3. Executar migrações (se houver)
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=sem-csmf -o jsonpath='{.items[0].metadata.name}') -- \
  python manage.py migrate

# 4. Reiniciar aplicação
kubectl scale deployment sem-csmf -n trisla --replicas=2
```

**Migração de Volumes Persistentes:**

```bash
# 1. Criar snapshot (se suportado)
kubectl create volumesnapshot postgres-snapshot \
  --source=persistentvolumeclaim/postgres-data \
  --namespace=trisla

# 2. Ou copiar dados manualmente
kubectl cp trisla/<pod-name>:/var/lib/postgresql/data ./postgres-data-backup
```

### 10.3 Validação Pós-Migração

```bash
# Verifiesr integridade dos dados
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- \
  psql -U trisla -d trisla -c "SELECT COUNT(*) FROM intents;"

# Verifiesr aplicação funcionando
curl http://localhost:8080/health
```

---

## 11. Validação Automática Pós-Instalação

### 11.1 Scripts de Validação

**Validação completa:**

```bash
# Executar validação completa
./scripts/validate-production-real.sh
```

**Validação por componente:**

```bash
# Validação de infraestrutura
./scripts/validate-nasp-infra.sh

# Validação E2E
./scripts/validate-e2e-pipeline.sh

# Validação local
./scripts/validate-local.sh
```

### 11.2 Validação Manual

**Verifiesr pods:**

```bash
# Todos os pods devem estar Running
kubectl get pods -n trisla

# Verifiesr readiness
kubectl get pods -n trisla -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}'
```

**Verifiesr serviços:**

```bash
# Todos os serviços devem ter endpoints
kubectl get svc -n trisla
kubectl get endpoints -n trisla
```

**Testar health endpoints:**

```bash
# Testar todos os health endpoints
for service in sem-csmf ml-nsmf decision-engine bc-nsmf sla-agent-layer nasp-adapter; do
  kubectl port-forward -n trisla svc/$service 8080:8080 &
  curl http://localhost:8080/health
  kill %1
done
```

### 11.3 Validação de Integração

**Testar fluxo E2E:**

```bash
# Executar teste E2E completo
./scripts/complete-e2e-test.sh

# Ou via script Python
python scripts/e2e_validator.py
```

**Verifiesr integration com NASP:**

```bash
# Testar conectividade
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  curl -k https://<NASP_ENDPOINT>/health
```

### 11.4 Validação de Observabilidade

**Verifiesr Prometheus:**

```bash
# Verifiesr targets
kubectl port-forward -n trisla svc/prometheus 9090:9090
# Acessar: http://localhost:9090/targets
```

**Verifiesr Grafana:**

```bash
# Verifiesr dashboards
kubectl port-forward -n trisla svc/grafana 3000:3000
# Acessar: http://localhost:3000
```

---

## 12. Checklist Final

### 12.1 Pré-Instalação

- [ ] Pré-requisitos verificados (kubectl, Helm, Docker, etc.)
- [ ] Acesso ao cluster Kubernetes configurado
- [ ] Secrets criados (GHCR, NASP)
- [ ] Configurações preparadas (values-nasp.yaml)
- [ ] Backup realizado (se atualização)

### 12.2 Instalação

- [ ] Method de instalação escolhido
- [ ] Pre-flight checks executados
- [ ] Deploy executado com sucesso
- [ ] Todos os pods em estado Running
- [ ] Todos os serviços criados

### 12.3 Pós-Instalação

- [ ] Health endpoints respondendo
- [ ] Comunicação entre módulos funcionando
- [ ] Integração com NASP funcionando
- [ ] Observabilidade configurada
- [ ] Testes E2E executados com sucesso

### 12.4 Documentação

- [ ] Instalação documentada
- [ ] Configurações documentadas
- [ ] Credenciais seguras (não no repositório)
- [ ] Runbooks criados
- [ ] Equipe treinada

### 12.5 Produção

- [ ] Monitoramento ativo
- [ ] Alertas configurados
- [ ] Backup automatizado
- [ ] Processo de atualização documentado
- [ ] Processo de rollback testado

---

## Conclusão

Este guia fornece múltiplos métodos para instalar o TriSLA em produção. Escolha o método mais adequado ao seu ambiente e siga as instruções passo a passo.

**Recomendações finais:**

- **Produção**: Use Helm (section 5)
- **Desenvolvimento**: Use Docker Compose (section 4)
- **Automação**: Use Ansible (section 6) ou CI/CD (section 7)
- **Rápido**: Use Scripts (section 3)

**Lembre-se:**

- Sempre executar pre-flight checks antes do deploy
- Validar instalação após deploy
- Manter backups regulares
- Documentar todas as mudanças
- Testar rollback antes de produção

**Última atualização:** 2025-01-XX  
**Versão do documento:** 1.0.0  
**Versão do TriSLA:** 1.0.0

**Referências:**
- `README_OPERATIONS_PROD.md`: Guia de operações
- `NASP_DEPLOY_GUIDE.md`: Guia específico para NASP
- `TROUBLESHOOTING_TRISLA.md`: Guia de troubleshooting
- `SECURITY_HARDENING.md`: Guia de segurança


