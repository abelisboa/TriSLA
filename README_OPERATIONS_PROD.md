# TriSLA — Guia de Operações em Produção

## 1. Introdução

### 1.1 Objetivo do Documento

Este documento fornece instruções completas para implantar, operar e manter o **TriSLA** (Triple-SLA) em ambiente de produção real, especificamente no **NASP** (Network Automation & Slicing Platform). O guia cobre desde a preparação inicial do ambiente até operações diárias, troubleshooting e boas práticas de segurança.

### 1.2 Visão Geral do TriSLA em Produção

O **TriSLA** é uma arquitetura SLA-Aware, explicável e automatizada para garantia de Service Level Agreements em redes 5G/O-RAN. Em produção, o sistema opera como um conjunto de microserviços distribuídos no Kubernetes, integrando:

- **SEM-CSMF**: Interpretação semântica de intenções de tenant e geração de NEST (Network Slice Template)
- **ML-NSMF**: Predição de violações de SLA usando modelos LSTM com explicação (XAI)
- **Decision Engine**: Motor de decisão automatizado baseado em regras e ML
- **BC-NSSMF**: Execução de smart contracts em blockchain para registro imutável de SLAs
- **SLA-Agent Layer**: Agentes federados para coleta de métricas em RAN, Transport e Core
- **NASP Adapter**: Integração com a plataforma NASP para execução de ações reais
- **UI Dashboard**: Interface visual para monitoramento e administração

### 1.3 Pré-requisitos

Antes de iniciar o deploy, certifique-se de que o operador possui:

- **Acesso ao cluster NASP** com permissões de administrador
- **kubectl** configurado e conectado ao cluster (versão ≥ 1.26)
- **Helm** instalado (versão ≥ 3.12)
- **Ansible** instalado (versão ≥ 2.14) — opcional, para automação
- **Acesso ao GitHub Container Registry (GHCR)** com token válido
- **Conhecimento básico** de Kubernetes, Helm, e arquitetura 5G/O-RAN
- **Credenciais de acesso** ao ambiente NASP (endpoints, tokens, certificados)

---

## 2. Requisitos de Infraestrutura

### 2.1 NASP Cluster

O TriSLA requer um cluster Kubernetes configurado com:

- **Versão Kubernetes**: ≥ 1.26
- **CNI**: Calico (recomendado para políticas de rede)
- **StorageClass**: Configurada e funcional (para volumes persistentes)
- **Ingress Controller**: Nginx ou similar (para exposição de serviços)
- **RBAC**: Habilitado e configurado

**Validação do cluster:**

```bash
kubectl cluster-info
kubectl get nodes
kubectl get storageclass
kubectl get ingressclass
```

### 2.2 Recursos Computacionais Mínimos

| Componente | CPU Request | Memory Request | CPU Limit | Memory Limit | Replicas |
|------------|-------------|----------------|-----------|--------------|----------|
| SEM-CSMF | 500m | 512Mi | 2000m | 2Gi | 2 |
| ML-NSMF | 1000m | 1Gi | 4000m | 4Gi | 2 |
| Decision Engine | 500m | 512Mi | 2000m | 2Gi | 2 |
| BC-NSSMF | 500m | 512Mi | 2000m | 2Gi | 2 |
| SLA-Agent Layer | 500m | 512Mi | 2000m | 2Gi | 3 |
| NASP Adapter | 500m | 512Mi | 2000m | 2Gi | 2 |
| UI Dashboard | 100m | 128Mi | 500m | 512Mi | 2 |
| Kafka | 1000m | 2Gi | 4000m | 4Gi | 3 |
| Prometheus | 500m | 1Gi | 2000m | 4Gi | 1 |
| Grafana | 100m | 256Mi | 500m | 1Gi | 1 |
| OTLP Collector | 200m | 256Mi | 1000m | 1Gi | 1 |

**Total estimado por nó (mínimo):**
- CPU: ~8 cores
- Memory: ~16 GiB
- Storage: ~50 GiB (para volumes persistentes)

### 2.3 Acesso ao Registry GHCR

O TriSLA utiliza imagens Docker hospedadas no GitHub Container Registry. É necessário:

1. **Criar um Personal Access Token (PAT) no GitHub** com permissões:
   - `read:packages` (para pull de imagens)
   - `write:packages` (se for necessário fazer push)

2. **Registrar o token como Secret no Kubernetes** (ver seção 4.2)

### 2.4 Ferramentas Necessárias no Operador

Instale as seguintes ferramentas na máquina do operador:

```bash
# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Ansible (opcional)
pip install ansible
```

**Validação:**

```bash
kubectl version --client
helm version
ansible --version  # se instalado
```

---

## 3. Arquitetura TriSLA — Visão Operacional

### 3.1 SEM-CSMF (Semantic Communication Service Management Function)

**Função**: Processa intenções de tenant em linguagem natural e gera NEST (Network Slice Template) usando ontologia OWL.

**Endpoints**:
- REST API: `http://sem-csmf:8080`
- Health: `http://sem-csmf:8080/health`
- gRPC: `sem-csmf:50051` (Interface I-01)

**Dependências**:
- PostgreSQL (banco de dados de intenções e NESTs)
- Kafka (mensageria)
- Decision Engine (via gRPC)

**Variáveis de ambiente críticas**:
- `DATABASE_URL`: String de conexão PostgreSQL
- `DECISION_ENGINE_GRPC`: Endpoint gRPC do Decision Engine
- `KAFKA_BOOTSTRAP_SERVERS`: Lista de brokers Kafka
- `OTLP_ENDPOINT`: Endpoint do coletor OpenTelemetry

### 3.2 ML-NSMF (Machine Learning Network Slice Management Function)

**Função**: Prediz violações de SLA usando modelos LSTM e fornece explicações (XAI) para decisões.

**Endpoints**:
- REST API: `http://ml-nsmf:8081`
- Health: `http://ml-nsmf:8081/health`

**Dependências**:
- Kafka (consumo de métricas e publicação de predições)
- OTLP Collector (exportação de métricas)

**Modelos ML**:
- Modelo LSTM pré-treinado para predição de violações
- Modelo XAI para explicação de predições

### 3.3 Decision Engine

**Função**: Motor de decisão automatizado que combina regras de negócio, predições ML e estado atual da rede para tomar decisões sobre slices.

**Endpoints**:
- REST API: `http://decision-engine:8082`
- gRPC: `decision-engine:50051` (Interface I-01)
- Health: `http://decision-engine:8082/health`

**Dependências**:
- SEM-CSMF (via gRPC)
- ML-NSMF (via REST)
- BC-NSSMF (via REST)
- Kafka (mensageria)

**Lógica de decisão**:
- Avalia predições de ML-NSMF
- Aplica regras de negócio configuráveis
- Consulta estado atual via SLA-Agent Layer
- Executa ações via NASP Adapter

### 3.4 BC-NSSMF (Blockchain Network Slice Subnet Management Function)

**Função**: Gerencia smart contracts em blockchain (GoQuorum/Besu) para registro imutável de SLAs e compliance.

**Endpoints**:
- REST API: `http://bc-nssmf:8083`
- Health: `http://bc-nssmf:8083/health`
- gRPC: `bc-nssmf:50051` (Interface I-07)

**Dependências**:
- Rede blockchain (GoQuorum ou Hyperledger Besu)
- Kafka (mensageria)
- OTLP Collector

**Smart Contracts**:
- `SLAContract.sol`: Contrato principal para registro de SLAs

### 3.5 SLA-Agent Layer

**Função**: Agentes federados que coletam métricas em tempo real de RAN, Transport e Core.

**Endpoints**:
- REST API: `http://sla-agent-layer:8084`
- Health: `http://sla-agent-layer:8084/health`

**Agentes**:
- **Agent RAN**: Coleta métricas de RAN (CPU, memória, throughput)
- **Agent Transport**: Coleta métricas de transporte (bandwidth, latency, jitter)
- **Agent Core**: Coleta métricas de core (connections, packets/sec, error rate)

**Dependências**:
- NASP Adapter (para acesso aos endpoints NASP)
- Kafka (publicação de métricas)
- OTLP Collector

### 3.6 NASP Adapter

**Função**: Adaptador que traduz ações do Decision Engine em chamadas reais à API NASP.

**Endpoints**:
- REST API: `http://nasp-adapter:8085`
- Health: `http://nasp-adapter:8085/health`

**Configuração NASP**:
- `NASP_RAN_ENDPOINT`: Endpoint da API NASP para RAN
- `NASP_TRANSPORT_ENDPOINT`: Endpoint da API NASP para Transport
- `NASP_CORE_ENDPOINT`: Endpoint da API NASP para Core
- `NASP_MODE`: `production` (não usar `mock` em produção)

**Dependências**:
- APIs NASP reais (não mocks)
- Kafka (consumo de ações)
- OTLP Collector

### 3.7 Observabilidade OTLP

**OpenTelemetry Collector**: Coleta traces, metrics e logs de todos os módulos e exporta para:
- **Prometheus**: Métricas
- **Grafana**: Visualização
- **Alertmanager**: Alertas baseados em SLO

**Endpoints**:
- gRPC: `otlp-collector:4317`
- HTTP: `otlp-collector:4318`

---

## 4. Preparação do Ambiente NASP

### 4.1 Criar Namespace `trisla`

```bash
kubectl create namespace trisla
kubectl label namespace trisla name=trisla
kubectl label namespace trisla environment=production
```

**Validação:**

```bash
kubectl get namespace trisla
```

### 4.2 Criar Secret GHCR

O secret é necessário para o Kubernetes fazer pull das imagens do GHCR.

**Método 1: Via kubectl (recomendado)**

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USERNAME> \
  --docker-password=<GITHUB_PAT_TOKEN> \
  --docker-email=<GITHUB_EMAIL> \
  --namespace=trisla
```

**Método 2: Via arquivo YAML (mais seguro)**

Crie um arquivo `ghcr-secret.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ghcr-secret
  namespace: trisla
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <BASE64_ENCODED_DOCKER_CONFIG>
```

Para gerar o base64:

```bash
echo -n '{"auths":{"ghcr.io":{"username":"<USERNAME>","password":"<TOKEN>","email":"<EMAIL>","auth":"<BASE64_USERNAME:TOKEN>"}}}' | base64 -w 0
```

Aplique o secret:

```bash
kubectl apply -f ghcr-secret.yaml
```

**Validação:**

```bash
kubectl get secret ghcr-secret -n trisla
```

### 4.3 Validar Cluster

Execute o script de pre-flight automático:

```bash
cd TriSLA-clean
./scripts/pre-flight-check.sh
```

Ou manualmente:

```bash
# Verificar nodes
kubectl get nodes -o wide

# Verificar storage
kubectl get storageclass

# Verificar DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kubernetes.default

# Verificar conectividade de rede
kubectl run -it --rm debug --image=busybox --restart=Never -- ping -c 3 8.8.8.8
```

### 4.4 Verificar Conectividade Interna

Antes do deploy, valide que os serviços NASP estão acessíveis:

```bash
# Testar conectividade com endpoints NASP
curl -k https://<NASP_RAN_ENDPOINT>/health
curl -k https://<NASP_TRANSPORT_ENDPOINT>/health
curl -k https://<NASP_CORE_ENDPOINT>/health
```

**Nota**: Ajuste os endpoints conforme sua configuração NASP real.

### 4.5 Rodar Pre-flight Automático

O playbook Ansible inclui validações automáticas:

```bash
cd TriSLA-clean/ansible
ansible-playbook -i inventory.yaml playbooks/pre-flight.yml
```

Este playbook verifica:
- Versão do Kubernetes
- Disponibilidade de recursos
- StorageClass configurada
- Ingress Controller disponível
- Conectividade de rede
- Acesso ao GHCR

---

## 5. Configuração dos Valores Helm

### 5.1 Exemplo Completo de `values-nasp.yaml`

Crie um arquivo `values-nasp.yaml` com as configurações específicas do seu ambiente NASP:

```yaml
# ============================================
# TriSLA Helm Chart - Values para NASP
# ============================================

global:
  imageRegistry: ghcr.io/abelisboa
  imagePullSecrets:
    - name: ghcr-secret
  namespace: trisla

# Network Configuration (ajustar conforme NASP)
network:
  interface: "eth0"  # Interface de rede principal do cluster
  nodeIP: "192.168.10.16"  # IP do nó Kubernetes (ajustar)
  gateway: "192.168.10.1"  # Gateway padrão (ajustar)

# SEM-CSMF
semCsmf:
  enabled: true
  image:
    repository: trisla-sem-csmf
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8080
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi
  replicas: 2
  env:
    DATABASE_URL: "postgresql://trisla:trisla_password@postgres:5432/trisla"
    DECISION_ENGINE_GRPC: "decision-engine:50051"
    KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
    OTLP_ENDPOINT: "http://otlp-collector:4317"
    LOG_LEVEL: "INFO"
    ENABLE_AUTH: "true"
    JWT_SECRET_KEY: "<GERAR_SECRET_KEY_SEGURO>"  # ⚠️ ALTERAR

# ML-NSMF
mlNsmf:
  enabled: true
  image:
    repository: trisla-ml-nsmf
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8081
  resources:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi
  replicas: 2
  env:
    KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
    OTLP_ENDPOINT: "http://otlp-collector:4317"
    LOG_LEVEL: "INFO"

# Decision Engine
decisionEngine:
  enabled: true
  image:
    repository: trisla-decision-engine
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8082
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi
  replicas: 2
  env:
    KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
    OTLP_ENDPOINT: "http://otlp-collector:4317"
    LOG_LEVEL: "INFO"
    GRPC_PORT: "50051"

# BC-NSSMF
bcNssmf:
  enabled: true
  image:
    repository: trisla-bc-nssmf
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8083
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi
  replicas: 2
  env:
    KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
    OTLP_ENDPOINT: "http://otlp-collector:4317"
    LOG_LEVEL: "INFO"
    BLOCKCHAIN_NETWORK: "besu"  # ou "goquorum"
    BLOCKCHAIN_ENDPOINT: "http://besu-node:8545"  # Ajustar conforme blockchain

# SLA-Agent Layer
slaAgentLayer:
  enabled: true
  image:
    repository: trisla-sla-agent-layer
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8084
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi
  replicas: 3
  env:
    KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
    OTLP_ENDPOINT: "http://otlp-collector:4317"
    LOG_LEVEL: "INFO"

# NASP Adapter
naspAdapter:
  enabled: true
  image:
    repository: trisla-nasp-adapter
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8085
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi
  replicas: 2
  env:
    KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
    OTLP_ENDPOINT: "http://otlp-collector:4317"
    LOG_LEVEL: "INFO"
    NASP_MODE: "production"  # ⚠️ NÃO usar "mock" em produção
    NASP_RAN_ENDPOINT: "https://<NASP_RAN_ENDPOINT>/api/v1"  # ⚠️ AJUSTAR
    NASP_TRANSPORT_ENDPOINT: "https://<NASP_TRANSPORT_ENDPOINT>/api/v1"  # ⚠️ AJUSTAR
    NASP_CORE_ENDPOINT: "https://<NASP_CORE_ENDPOINT>/api/v1"  # ⚠️ AJUSTAR
    NASP_AUTH_TOKEN: "<NASP_AUTH_TOKEN>"  # ⚠️ Usar Secret do Kubernetes

# UI Dashboard
uiDashboard:
  enabled: true
  image:
    repository: trisla-ui-dashboard
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 80
  ingress:
    enabled: true
    className: nginx
    hosts:
      - host: trisla.nasp.local  # ⚠️ AJUSTAR conforme DNS
        paths:
          - path: /
            pathType: Prefix
    tls:
      - secretName: trisla-tls
        hosts:
          - trisla.nasp.local
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
  replicas: 2
  env:
    REACT_APP_API_BASE_URL: "http://sem-csmf:8080"
    REACT_APP_PROMETHEUS_URL: "http://prometheus:9090"
    REACT_APP_GRAFANA_URL: "http://grafana:3000"

# Kafka
kafka:
  enabled: true
  image:
    repository: apache/kafka
    tag: "3.5.0"
  replicas: 3
  storage:
    size: 20Gi
    storageClass: "standard"  # ⚠️ AJUSTAR conforme StorageClass

# PostgreSQL
postgres:
  enabled: true
  image:
    repository: postgres
    tag: "15-alpine"
  storage:
    size: 10Gi
    storageClass: "standard"  # ⚠️ AJUSTAR conforme StorageClass
  env:
    POSTGRES_DB: "trisla"
    POSTGRES_USER: "trisla"
    POSTGRES_PASSWORD: "<GERAR_SENHA_SEGURA>"  # ⚠️ Usar Secret do Kubernetes

# OpenTelemetry Collector
otelCollector:
  enabled: true
  image:
    repository: otel/opentelemetry-collector
    tag: latest
  service:
    type: ClusterIP
    ports:
      grpc: 4317
      http: 4318

# Prometheus
prometheus:
  enabled: true
  image:
    repository: prom/prometheus
    tag: latest
  storage:
    size: 50Gi
    storageClass: "standard"  # ⚠️ AJUSTAR conforme StorageClass
  retention: "30d"

# Grafana
grafana:
  enabled: true
  image:
    repository: grafana/grafana
    tag: latest
  adminPassword: "<GERAR_SENHA_SEGURA>"  # ⚠️ ALTERAR
  storage:
    size: 5Gi
    storageClass: "standard"  # ⚠️ AJUSTAR conforme StorageClass

# Alertmanager
alertmanager:
  enabled: true
  image:
    repository: prom/alertmanager
    tag: latest
  storage:
    size: 1Gi
    storageClass: "standard"  # ⚠️ AJUSTAR conforme StorageClass

# Production Settings
production:
  enabled: true
  simulationMode: false
  useRealServices: true
  executeRealActions: true
```

### 5.2 Campos Obrigatórios

Os seguintes campos **devem** ser ajustados antes do deploy:

1. **`network.nodeIP`**: IP do nó Kubernetes principal
2. **`network.gateway`**: Gateway padrão da rede
3. **`naspAdapter.env.NASP_RAN_ENDPOINT`**: Endpoint real da API NASP para RAN
4. **`naspAdapter.env.NASP_TRANSPORT_ENDPOINT`**: Endpoint real da API NASP para Transport
5. **`naspAdapter.env.NASP_CORE_ENDPOINT`**: Endpoint real da API NASP para Core
6. **`naspAdapter.env.NASP_AUTH_TOKEN`**: Token de autenticação NASP (usar Secret)
7. **`semCsmf.env.JWT_SECRET_KEY`**: Chave secreta para JWT (gerar aleatoriamente)
8. **`postgres.env.POSTGRES_PASSWORD`**: Senha do PostgreSQL (usar Secret)
9. **`grafana.adminPassword`**: Senha do administrador Grafana
10. **`uiDashboard.ingress.hosts[0].host`**: Hostname do dashboard (ajustar DNS)

### 5.3 Configurações Opcionais

- **Recursos (CPU/Memory)**: Ajustar conforme capacidade do cluster
- **Replicas**: Aumentar para alta disponibilidade
- **StorageClass**: Ajustar conforme storage disponível
- **Ingress TLS**: Configurar certificados SSL/TLS

### 5.4 Referência aos Templates

Os templates Helm estão localizados em `helm/trisla/templates/`:

- `deployment-*.yaml`: Deployments dos módulos
- `service-*.yaml`: Services Kubernetes
- `configmap.yaml`: ConfigMaps com configurações
- `secret-ghcr.yaml`: Secret para GHCR
- `ingress.yaml`: Ingress para UI Dashboard
- `namespace.yaml`: Namespace `trisla`

---

## 6. Deploy TriSLA com Helm

### 6.1 Comando Principal do Deploy

**Deploy inicial:**

```bash
cd TriSLA-clean
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 10m
```

**Explicação dos parâmetros:**

- `upgrade --install`: Instala se não existir, atualiza se existir
- `--namespace trisla`: Namespace onde será instalado
- `--create-namespace`: Cria o namespace se não existir
- `--values`: Arquivo de valores customizado
- `--wait`: Aguarda os recursos ficarem prontos
- `--timeout 10m`: Timeout de 10 minutos

### 6.2 Deploy com Validação Automática (`--atomic`)

Para garantir rollback automático em caso de falha:

```bash
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --atomic \
  --wait \
  --timeout 10m
```

O parâmetro `--atomic` faz rollback automático se o deploy falhar.

### 6.3 Processo de Upgrade

Para atualizar o TriSLA com novas versões:

```bash
# 1. Atualizar valores (se necessário)
vim ./helm/trisla/values-nasp.yaml

# 2. Validar o chart
helm lint ./helm/trisla

# 3. Dry-run para verificar mudanças
helm upgrade trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml \
  --dry-run \
  --debug

# 4. Aplicar upgrade
helm upgrade trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 10m
```

### 6.4 Rollback Automático

Se o deploy falhar ou houver problemas:

```bash
# Listar histórico de releases
helm history trisla -n trisla

# Rollback para versão anterior
helm rollback trisla <REVISION_NUMBER> -n trisla

# Rollback para última versão estável
helm rollback trisla -n trisla
```

**Rollback manual (se necessário):**

```bash
# Deletar release atual
helm uninstall trisla -n trisla

# Reinstalar versão anterior (se tiver backup)
helm install trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml.backup
```

---

## 7. Verificação Pós-Deploy

### 7.1 Lista de Pods Esperados

Após o deploy, os seguintes pods devem estar em estado `Running`:

```bash
kubectl get pods -n trisla
```

**Pods esperados:**

| Pod | Replicas Esperadas | Status Esperado |
|-----|-------------------|-----------------|
| `sem-csmf-*` | 2 | Running |
| `ml-nsmf-*` | 2 | Running |
| `decision-engine-*` | 2 | Running |
| `bc-nssmf-*` | 2 | Running |
| `sla-agent-layer-*` | 3 | Running |
| `nasp-adapter-*` | 2 | Running |
| `ui-dashboard-*` | 2 | Running |
| `kafka-*` | 3 | Running |
| `postgres-*` | 1 | Running |
| `otlp-collector-*` | 1 | Running |
| `prometheus-*` | 1 | Running |
| `grafana-*` | 1 | Running |
| `alertmanager-*` | 1 | Running |

### 7.2 Comandos para Verificar Cada Módulo

**SEM-CSMF:**

```bash
# Verificar pods
kubectl get pods -n trisla -l app=sem-csmf

# Verificar logs
kubectl logs -n trisla -l app=sem-csmf --tail=50

# Testar health endpoint
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=sem-csmf -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://localhost:8080/health
```

**ML-NSMF:**

```bash
kubectl get pods -n trisla -l app=ml-nsmf
kubectl logs -n trisla -l app=ml-nsmf --tail=50
```

**Decision Engine:**

```bash
kubectl get pods -n trisla -l app=decision-engine
kubectl logs -n trisla -l app=decision-engine --tail=50
```

**BC-NSSMF:**

```bash
kubectl get pods -n trisla -l app=bc-nssmf
kubectl logs -n trisla -l app=bc-nssmf --tail=50
```

**SLA-Agent Layer:**

```bash
kubectl get pods -n trisla -l app=sla-agent-layer
kubectl logs -n trisla -l app=sla-agent-layer --tail=50
```

**NASP Adapter:**

```bash
kubectl get pods -n trisla -l app=nasp-adapter
kubectl logs -n trisla -l app=nasp-adapter --tail=50
```

### 7.3 Checagem de Readiness e Liveness

**Verificar readiness:**

```bash
kubectl get pods -n trisla -o wide
kubectl describe pod <POD_NAME> -n trisla
```

Todos os pods devem ter `READY` como `1/1` ou `2/2` (conforme replicas).

**Verificar liveness probes:**

```bash
# Verificar eventos
kubectl get events -n trisla --sort-by='.lastTimestamp'

# Verificar probes
kubectl get pods -n trisla -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}'
```

### 7.4 Validação da Infraestrutura NASP

**Testar conectividade com NASP:**

```bash
# Via NASP Adapter
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://localhost:8085/health

# Verificar logs de conexão
kubectl logs -n trisla -l app=nasp-adapter | grep -i "nasp\|connection\|error"
```

**Validar endpoints NASP:**

```bash
# Testar endpoints via port-forward (se necessário)
kubectl port-forward -n trisla svc/nasp-adapter 8085:8085

# Em outro terminal
curl http://localhost:8085/health
```

---

## 8. Configuração do Monitoring

### 8.1 Exportação OTLP

Todos os módulos TriSLA exportam métricas, traces e logs via OpenTelemetry. O OTLP Collector está configurado para:

- **Receber**: gRPC (porta 4317) e HTTP (porta 4318)
- **Exportar para Prometheus**: Métricas
- **Exportar para Grafana**: Visualização

**Verificar OTLP Collector:**

```bash
kubectl get pods -n trisla -l app=otlp-collector
kubectl logs -n trisla -l app=otlp-collector --tail=50
```

### 8.2 Prometheus Rules

As regras de alerta estão configuradas em `monitoring/prometheus/rules/`. Principais alertas:

- **SLA Violation**: Violação de SLA detectada
- **Module Down**: Módulo TriSLA indisponível
- **High Latency**: Latência elevada entre módulos
- **Kafka Lag**: Atraso no processamento de mensagens Kafka

**Aplicar regras:**

```bash
kubectl apply -f monitoring/prometheus/rules/ -n trisla
```

**Verificar regras ativas:**

```bash
# Via Prometheus UI (port-forward)
kubectl port-forward -n trisla svc/prometheus 9090:9090
# Acessar http://localhost:9090/alerts
```

### 8.3 Dashboards Grafana

Dashboards pré-configurados estão em `monitoring/grafana/dashboards/`:

- **TriSLA Overview**: Visão geral do sistema
- **SLO Compliance**: Compliance de SLAs
- **Module Metrics**: Métricas por módulo
- **Network Metrics**: Métricas de rede

**Acessar Grafana:**

```bash
# Port-forward
kubectl port-forward -n trisla svc/grafana 3000:3000

# Acessar http://localhost:3000
# Usuário: admin
# Senha: (conforme values-nasp.yaml)
```

**Importar dashboards:**

Os dashboards são importados automaticamente via ConfigMap. Verificar:

```bash
kubectl get configmap -n trisla | grep grafana
```

### 8.4 Alertas Críticos

Alertas críticos configurados:

1. **SLA Violation Critical**: Violação de SLA com impacto crítico
2. **Module Crash Loop**: Pod em crash loop
3. **Database Connection Failure**: Falha de conexão com PostgreSQL
4. **Kafka Unavailable**: Kafka indisponível
5. **NASP Adapter Failure**: Falha na comunicação com NASP

**Configurar notificações (Alertmanager):**

Edite `monitoring/alertmanager/config.yml` e aplique:

```bash
kubectl apply -f monitoring/alertmanager/config.yml -n trisla
```

### 8.5 SLO Reports

O módulo de SLO Reports gera relatórios automáticos de compliance. Localização:

```bash
# Executar script de geração
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=slo-reports -o jsonpath='{.items[0].metadata.name}') -- \
  python /app/generate_slo_report.py

# Relatórios são salvos em volume persistente
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=slo-reports -o jsonpath='{.items[0].metadata.name}') -- \
  ls -la /reports
```

---

## 9. Execução E2E do Fluxo TriSLA

### 9.1 Passo a Passo

O fluxo end-to-end do TriSLA segue os seguintes passos:

1. **Tenant envia intenção** → SEM-CSMF
2. **SEM-CSMF processa e gera NEST** → Decision Engine
3. **Decision Engine solicita predição** → ML-NSMF
4. **ML-NSMF retorna predição** → Decision Engine
5. **Decision Engine toma decisão** → BC-NSSMF (registro) + NASP Adapter (execução)
6. **NASP Adapter executa ações** → NASP (RAN/Transport/Core)
7. **SLA-Agent Layer coleta métricas** → Kafka → ML-NSMF (feedback loop)

### 9.2 Workflow de Tenant → SLA → Slice

**1. Criar intenção de tenant (via SEM-CSMF):**

```bash
curl -X POST http://<SEM-CSMF_ENDPOINT>/api/v1/intents \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-001",
    "intent": "Criar slice para aplicação de realidade aumentada com latência < 10ms e throughput > 1Gbps",
    "priority": "high"
  }'
```

**2. SEM-CSMF processa e gera NEST:**

```bash
# Verificar NEST gerado
curl http://<SEM-CSMF_ENDPOINT>/api/v1/nests/<NEST_ID>
```

**3. Decision Engine avalia e decide:**

```bash
# Verificar decisão
curl http://<DECISION_ENGINE_ENDPOINT>/api/v1/decisions/<DECISION_ID>
```

**4. BC-NSSMF registra SLA em blockchain:**

```bash
# Verificar contrato
curl http://<BC-NSSMF_ENDPOINT>/api/v1/contracts/<CONTRACT_ADDRESS>
```

**5. NASP Adapter executa ações:**

```bash
# Verificar ações executadas
curl http://<NASP_ADAPTER_ENDPOINT>/api/v1/actions
```

### 9.3 Integração com ML-NSMF

O ML-NSMF recebe métricas via Kafka e gera predições:

```bash
# Verificar predições
curl http://<ML-NSMF_ENDPOINT>/api/v1/predictions

# Verificar explicações (XAI)
curl http://<ML-NSMF_ENDPOINT>/api/v1/explanations/<PREDICTION_ID>
```

### 9.4 Smart Contracts (BC-NSSMF)

**Verificar contratos implantados:**

```bash
curl http://<BC-NSSMF_ENDPOINT>/api/v1/contracts

# Verificar compliance de SLA
curl http://<BC-NSSMF_ENDPOINT>/api/v1/contracts/<CONTRACT_ADDRESS>/compliance
```

### 9.5 KPIs e Logs

**KPIs principais:**

- **SLA Compliance Rate**: Taxa de compliance de SLAs
- **Prediction Accuracy**: Precisão das predições ML
- **Decision Latency**: Latência de decisões
- **Action Execution Time**: Tempo de execução de ações

**Acessar métricas:**

```bash
# Via Prometheus
kubectl port-forward -n trisla svc/prometheus 9090:9090
# Acessar http://localhost:9090 e consultar métricas:
# - trisla_sla_compliance_rate
# - trisla_prediction_accuracy
# - trisla_decision_latency_seconds
```

**Logs agregados:**

```bash
# Logs de todos os módulos
kubectl logs -n trisla -l app.kubernetes.io/name=trisla --tail=100

# Logs por módulo
kubectl logs -n trisla -l app=sem-csmf --tail=100
kubectl logs -n trisla -l app=ml-nsmf --tail=100
kubectl logs -n trisla -l app=decision-engine --tail=100
```

---

## 10. Operação Diária

### 10.1 Como Acompanhar o Estado dos Módulos

**Dashboard de status:**

```bash
# Via UI Dashboard
kubectl port-forward -n trisla svc/ui-dashboard 80:80
# Acessar http://localhost:80
```

**Via kubectl:**

```bash
# Status geral
kubectl get all -n trisla

# Status detalhado
kubectl get pods -n trisla -o wide
kubectl get svc -n trisla
kubectl get ingress -n trisla
```

**Via Prometheus/Grafana:**

```bash
# Acessar dashboards (ver seção 8.3)
```

### 10.2 Restart Seguro

**Restart de um módulo específico:**

```bash
# Deletar pod (Kubernetes recria automaticamente)
kubectl delete pod <POD_NAME> -n trisla

# Ou via rollout restart
kubectl rollout restart deployment/<DEPLOYMENT_NAME> -n trisla
```

**Restart de todos os módulos:**

```bash
# Restart via Helm (mantém configurações)
helm upgrade trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml \
  --reuse-values \
  --wait
```

**Restart com zero-downtime:**

Os deployments estão configurados com `strategy: RollingUpdate`, garantindo zero-downtime durante restarts.

### 10.3 Atualização de Imagens GHCR

**Atualizar imagem de um módulo:**

```bash
# 1. Atualizar tag no values-nasp.yaml
vim ./helm/trisla/values-nasp.yaml
# Alterar: tag: "v1.1.0" (nova versão)

# 2. Aplicar upgrade
helm upgrade trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml \
  --wait
```

**Forçar pull de imagens:**

```bash
# Atualizar imagePullPolicy para Always temporariamente
helm upgrade trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml \
  --set semCsmf.image.pullPolicy=Always \
  --wait
```

### 10.4 Coleta de Métricas

**Exportar métricas do Prometheus:**

```bash
# Via API do Prometheus
kubectl port-forward -n trisla svc/prometheus 9090:9090

# Consultar métricas
curl 'http://localhost:9090/api/v1/query?query=trisla_sla_compliance_rate'
```

**Exportar logs:**

```bash
# Salvar logs em arquivo
kubectl logs -n trisla -l app=sem-csmf --tail=1000 > sem-csmf.log
kubectl logs -n trisla -l app=ml-nsmf --tail=1000 > ml-nsmf.log
```

---

## 11. Troubleshooting

### 11.1 Problemas Comuns

**Problema 1: Pods em estado `CrashLoopBackOff`**

```bash
# Verificar logs
kubectl logs <POD_NAME> -n trisla --previous

# Verificar eventos
kubectl describe pod <POD_NAME> -n trisla

# Verificar recursos
kubectl top pod <POD_NAME> -n trisla
```

**Causas comuns:**
- Falta de recursos (CPU/Memory)
- Erro de configuração (variáveis de ambiente)
- Falha de dependência (PostgreSQL, Kafka)

**Problema 2: Imagens não são puxadas do GHCR**

```bash
# Verificar secret
kubectl get secret ghcr-secret -n trisla

# Verificar imagePullSecrets no pod
kubectl describe pod <POD_NAME> -n trisla | grep -i "pull"

# Testar pull manual
kubectl run test-pull --image=ghcr.io/abelisboa/trisla-sem-csmf:latest --rm -it --restart=Never -n trisla
```

**Solução:**
- Recriar secret GHCR (ver seção 4.2)
- Verificar token GitHub

**Problema 3: Falha de conexão com NASP**

```bash
# Verificar logs do NASP Adapter
kubectl logs -n trisla -l app=nasp-adapter | grep -i "error\|connection\|nasp"

# Testar conectividade
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  curl -k https://<NASP_ENDPOINT>/health
```

**Solução:**
- Verificar endpoints NASP em `values-nasp.yaml`
- Verificar token de autenticação
- Verificar conectividade de rede

**Problema 4: Kafka não está disponível**

```bash
# Verificar pods Kafka
kubectl get pods -n trisla -l app=kafka

# Verificar logs
kubectl logs -n trisla -l app=kafka --tail=50

# Verificar storage
kubectl get pvc -n trisla | grep kafka
```

**Solução:**
- Verificar StorageClass
- Verificar recursos disponíveis
- Verificar configuração de replicas

### 11.2 Como Diagnosticar Falhas

**Script de diagnóstico automático:**

```bash
cd TriSLA-clean
./scripts/validate-production-real.sh
```

**Diagnóstico manual:**

```bash
# 1. Verificar saúde geral
kubectl get all -n trisla

# 2. Verificar eventos recentes
kubectl get events -n trisla --sort-by='.lastTimestamp' | tail -20

# 3. Verificar recursos
kubectl top nodes
kubectl top pods -n trisla

# 4. Verificar conectividade de rede
kubectl run -it --rm debug --image=busybox --restart=Never -n trisla -- \
  nslookup sem-csmf.trisla.svc.cluster.local

# 5. Verificar DNS
kubectl get svc -n trisla
```

### 11.3 Como Ver Logs por Módulo

**Logs em tempo real:**

```bash
# SEM-CSMF
kubectl logs -n trisla -l app=sem-csmf -f

# ML-NSMF
kubectl logs -n trisla -l app=ml-nsmf -f

# Decision Engine
kubectl logs -n trisla -l app=decision-engine -f

# BC-NSSMF
kubectl logs -n trisla -l app=bc-nssmf -f

# NASP Adapter
kubectl logs -n trisla -l app=nasp-adapter -f
```

**Logs de todos os pods:**

```bash
kubectl logs -n trisla -l app.kubernetes.io/name=trisla --tail=100
```

**Logs com filtro:**

```bash
# Apenas erros
kubectl logs -n trisla -l app=sem-csmf | grep -i "error\|exception\|fail"

# Apenas warnings
kubectl logs -n trisla -l app=sem-csmf | grep -i "warn"
```

### 11.4 Recovery Automático

O Kubernetes possui recovery automático via:

- **RestartPolicy**: `Always` (pods são reiniciados automaticamente)
- **LivenessProbe**: Reinicia pods se health check falhar
- **ReadinessProbe**: Remove pods do service se não estiverem prontos

**Verificar recovery:**

```bash
# Verificar restart count
kubectl get pods -n trisla -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].restartCount}{"\n"}{end}'

# Verificar eventos de restart
kubectl get events -n trisla | grep -i "restart\|backoff"
```

### 11.5 Ferramentas de Diagnóstico Fornecidas no Repositório

**Scripts úteis:**

```bash
# Validação de produção
./scripts/validate-production-real.sh

# Validação de infraestrutura NASP
./scripts/validate-nasp-infra.sh

# Validação E2E
./scripts/validate-e2e-pipeline.sh

# Verificação de estrutura
./scripts/verify-structure.ps1

# Teste de conexões entre módulos
./scripts/test-module-connections.sh
```

**Playbooks Ansible:**

```bash
# Validação completa
cd ansible
ansible-playbook -i inventory.yaml playbooks/validate-cluster.yml

# Deploy com validação
ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml
```

---

## 12. Boas Práticas de Segurança

### 12.1 Nunca Manter Tokens no Repositório

**⚠️ CRÍTICO**: Nunca commite tokens, senhas ou secrets no repositório Git.

**O que NÃO fazer:**

```yaml
# ❌ ERRADO
naspAdapter:
  env:
    NASP_AUTH_TOKEN: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # NUNCA FAZER ISSO
```

**O que fazer:**

```yaml
# ✅ CORRETO - Usar Secrets do Kubernetes
naspAdapter:
  env:
    NASP_AUTH_TOKEN:
      valueFrom:
        secretKeyRef:
          name: nasp-secrets
          key: auth-token
```

### 12.2 Como Criar GHCR Token Corretamente

**1. Criar Personal Access Token no GitHub:**

- Acesse: https://github.com/settings/tokens
- Clique em "Generate new token (classic)"
- Selecione escopos: `read:packages`, `write:packages`
- Gere o token e **copie imediatamente** (não será exibido novamente)

**2. Criar Secret no Kubernetes:**

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USERNAME> \
  --docker-password=<GITHUB_PAT_TOKEN> \
  --docker-email=<GITHUB_EMAIL> \
  --namespace=trisla
```

**3. Rotacionar token periodicamente:**

```bash
# Gerar novo token
# Atualizar secret
kubectl delete secret ghcr-secret -n trisla
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USERNAME> \
  --docker-password=<NOVO_TOKEN> \
  --docker-email=<GITHUB_EMAIL> \
  --namespace=trisla

# Reiniciar pods para usar novo secret
kubectl rollout restart deployment -n trisla
```

### 12.3 Política de Atualização

**Atualizações de segurança:**

- **Aplicar patches de segurança** imediatamente
- **Atualizar imagens base** regularmente (mensalmente)
- **Monitorar vulnerabilidades** via ferramentas de scanning

**Processo de atualização:**

```bash
# 1. Backup de valores
cp ./helm/trisla/values-nasp.yaml ./helm/trisla/values-nasp.yaml.backup

# 2. Atualizar valores
vim ./helm/trisla/values-nasp.yaml

# 3. Validar
helm lint ./helm/trisla
helm template trisla ./helm/trisla --values ./helm/trisla/values-nasp.yaml

# 4. Aplicar em ambiente de teste primeiro
helm upgrade trisla-test ./helm/trisla \
  --namespace trisla-test \
  --values ./helm/trisla/values-nasp.yaml

# 5. Validar em teste
# ... validações ...

# 6. Aplicar em produção
helm upgrade trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml \
  --atomic \
  --wait
```

### 12.4 Imagens Assinadas

**Verificar assinatura de imagens (se configurado):**

```bash
# Verificar se imagens são assinadas (requer cosign)
cosign verify ghcr.io/abelisboa/trisla-sem-csmf:latest
```

**Boas práticas:**

- Use imagens com tags específicas (não `latest` em produção)
- Verifique checksums de imagens
- Use image scanning (Trivy, Snyk)

---

## 13. Apêndice

### 13.1 Scripts Úteis

**Localização:** `TriSLA-clean/scripts/`

**Principais scripts:**

| Script | Descrição |
|-------|-----------|
| `deploy-trisla-nasp.sh` | Deploy completo no NASP |
| `validate-production-real.sh` | Validação de produção |
| `validate-nasp-infra.sh` | Validação de infraestrutura NASP |
| `test-module-connections.sh` | Teste de conexões entre módulos |
| `rollback.sh` | Rollback de deploy |
| `backup-postgres.sh` | Backup do banco PostgreSQL |
| `restore-postgres.sh` | Restauração do banco PostgreSQL |

**Uso:**

```bash
cd TriSLA-clean/scripts
chmod +x *.sh
./deploy-trisla-nasp.sh
```

### 13.2 Comandos Ansible Recomendados

**Localização:** `TriSLA-clean/ansible/`

**Playbooks principais:**

| Playbook | Descrição |
|----------|-----------|
| `deploy-trisla-nasp.yml` | Deploy completo |
| `pre-flight.yml` | Validação pré-deploy |
| `setup-namespace.yml` | Criação de namespace |
| `validate-cluster.yml` | Validação de cluster |

**Uso:**

```bash
cd TriSLA-clean/ansible
ansible-playbook -i inventory.yaml playbooks/deploy-trisla-nasp.yml
```

**Variáveis importantes (em `group_vars/all.yml`):**

```yaml
trisla:
  namespace: trisla
  image_registry: ghcr.io/abelisboa
  version: latest
```

### 13.3 Referência Cruzada com o Repositório

**Estrutura do repositório:**

```
TriSLA-clean/
├── apps/                    # Módulos TriSLA
│   ├── sem-csmf/
│   ├── ml-nsmf/
│   ├── decision-engine/
│   ├── bc-nssmf/
│   ├── sla-agent-layer/
│   ├── nasp-adapter/
│   └── ui-dashboard/
├── helm/trisla/            # Helm chart
│   ├── templates/
│   ├── values.yaml
│   └── Chart.yaml
├── monitoring/             # Configurações de observabilidade
│   ├── prometheus/
│   ├── grafana/
│   ├── alertmanager/
│   └── otel-collector/
├── ansible/                # Playbooks Ansible
│   ├── playbooks/
│   └── inventory.yaml
├── scripts/                # Scripts de automação
├── docker-compose.yml      # Para desenvolvimento local
├── README.md               # Documentação geral
└── README_OPERATIONS_PROD.md # Este documento
```

**Documentação adicional:**

- `README.md`: Visão geral do projeto
- `helm/trisla/README.md`: Guia do Helm chart
- `monitoring/README.md`: Guia de observabilidade
- `apps/*/README.md`: Documentação de cada módulo

---

## Conclusão

Este guia fornece todas as informações necessárias para operar o TriSLA em produção no ambiente NASP. Para suporte adicional, consulte a documentação técnica em `README.md` ou entre em contato através do repositório GitHub.

**Última atualização:** 2025-01-XX  
**Versão do documento:** 1.0.0  
**Versão do TriSLA:** 1.0.0

