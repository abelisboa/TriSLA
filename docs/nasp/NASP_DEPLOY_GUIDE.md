# TriSLA — NASP Deployment Guide

## 1. NASP Environment Introduction

### 1.1 NASP Overview

**NASP** (Network Automation & Slicing Platform) is a platform for network automation designed for network slicing management in 5G/O-RAN environments. The NASP environment consists of a Kubernetes cluster with high availability installed via **Kubespray**, using **Calico** as CNI (Container Network Interface) and a complete observability stack based on **Prometheus** and **Grafana**.

### 1.2 NASP Cluster Architecture

The NASP cluster is composed of:

- **Node1**: Control node (control plane) e worker
- **Node2**: Control node (control plane) e worker
- **Additional workers**: Opcionalmente, nós worker dedicados podem ser adicionados

Each node runs:
- Kubernetes (instalado via Kubespray)
- Calico CNI para networking
- Prometheus Operator para observabilidade
- Ingress Controller (Nginx) para exposição de serviços

### 1.3 Document Objective

This guide provides step-by-step instructions to deploy **TriSLA** in the NASP environment, covering from initial preparation to complete deployment validation. The document assumes that the operator has administrative access to the NASP cluster and basic knowledge of Kubernetes, Helm and 5G/O-RAN networks.

---

## 2. Cluster Architecture

### 2.1 Node1 and Node2

#### Node1 (Control Plane + Worker)

**Typical specifications:**
- **IP**: Configured on interface `my5g` (ex: 192.168.10.16)
- **Function**: Control plane and worker
- **Resources**: Minimum 8 cores CPU, 16 GiB RAM, 100 GiB storage
- **Services**: etcd, kube-apiserver, kube-controller-manager, kube-scheduler, kubelet, kube-proxy
- **Deploy**: TriSLA deployment is executed locally on this node

**Verification (run locally on node1):**

```bash
# Verificar status do Kubernetes
kubectl get nodes
kubectl get pods -n kube-system
```

#### Node2 (Control Plane + Worker)

**Typical specifications:**
- **IP**: Configured on interface `my5g` (ex: 192.168.10.17)
- **Function**: Control plane and worker
- **Resources**: Minimum 8 cores CPU, 16 GiB RAM, 100 GiB storage
- **Services**: etcd, kube-apiserver, kube-controller-manager, kube-scheduler, kubelet, kube-proxy

**Nota:** O deploy é feito localmente no node1, mas o cluster inclui o node2 como parte do control plane.

### 2.2 Kubespray

O cluster NASP é instalado usando **Kubespray**, uma ferramenta de instalação e configuração de clusters Kubernetes. O Kubespray utiliza Ansible para automatizar a instalação.

**Características da instalação Kubespray:**
- Kubernetes versão ≥ 1.26
- Alta disponibilidade do control plane
- etcd clusterizado
- Configuração de rede via Calico
- RBAC habilitado por padrão

**Verificar instalação Kubespray:**

```bash
# Verificar versão do Kubernetes
kubectl version --short

# Verificar componentes do control plane
kubectl get pods -n kube-system | grep -E "etcd|kube-apiserver|kube-controller|kube-scheduler"
```

### 2.3 Calico

**Calico** é o CNI (Container Network Interface) utilizado no cluster NASP. Ele fornece:

- **Networking**: Conectividade entre pods e serviços
- **Network Policies**: Controle de tráfego entre pods
- **IPAM**: Gerenciamento de endereços IP
- **BGP**: Roteamento entre nós (opcional)

**Verificar Calico:**

```bash
# Verificar pods do Calico
kubectl get pods -n kube-system -l k8s-app=calico-node

# Verificar status do Calico
kubectl get nodes -o wide

# Verificar Network Policies
kubectl get networkpolicies --all-namespaces
```

**Configuração típica do Calico no NASP:**

```yaml
# ConfigMap do Calico (exemplo)
apiVersion: v1
kind: ConfigMap
metadata:
  name: calico-config
  namespace: kube-system
data:
  calico_backend: "bird"
  veth_mtu: "1440"
  cni_network_config: |
    {
      "name": "k8s-pod-network",
      "cniVersion": "0.3.1",
      "plugins": [
        {
          "type": "calico",
          "log_level": "info",
          "datastore_type": "kubernetes",
          "nodename": "__KUBERNETES_NODE_NAME__",
          "mtu": __CNI_MTU__,
          "ipam": {
            "type": "calico-ipam"
          },
          "policy": {
            "type": "k8s"
          }
        }
      ]
    }
```

### 2.4 Storage

O cluster NASP utiliza **StorageClass** para provisionamento dinâmico de volumes persistentes. A StorageClass padrão é tipicamente configurada como `local-path` ou `nfs`.

**Verificar Storage:**

```bash
# Listar StorageClasses
kubectl get storageclass

# Verificar StorageClass padrão
kubectl get storageclass -o jsonpath='{.items[?(@.metadata.annotations.storageclass\.kubernetes\.io/is-default-class=="true")].metadata.name}'

# Verificar volumes persistentes
kubectl get pv
kubectl get pvc --all-namespaces
```

**Exemplo de StorageClass (local-path):**

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-path
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: rancher.io/local-path
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
```

### 2.5 Prometheus Stack

O cluster NASP inclui uma stack completa de observabilidade:

- **Prometheus**: Coleta e armazena métricas
- **Grafana**: Visualização de métricas e dashboards
- **Alertmanager**: Gerenciamento de alertas
- **Node Exporter**: Métricas de nós
- **kube-state-metrics**: Métricas do estado do Kubernetes

**Verificar Prometheus Stack:**

```bash
# Verificar pods do Prometheus
kubectl get pods -n monitoring | grep prometheus

# Verificar pods do Grafana
kubectl get pods -n monitoring | grep grafana

# Verificar ServiceMonitors
kubectl get servicemonitor --all-namespaces
```

**Acessar Prometheus:**

```bash
# Port-forward
kubectl port-forward -n monitoring svc/prometheus-k8s 9090:9090

# Acessar: http://localhost:9090
```

**Acessar Grafana:**

```bash
# Port-forward
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Acessar: http://localhost:3000
# Credenciais padrão: admin/admin (alterar em produção)
```

---

## 3. Pré-requisitos para Deploy

### 3.1 Requisitos de Acesso

Antes de iniciar o deploy, o operador deve possuir:

- **Acesso local ao node1 do NASP** (você já está dentro do node1)
- **Acesso ao kubeconfig** do cluster (arquivo `/etc/kubernetes/admin.conf` ou equivalente)
- **Acesso à rede NASP** para comunicação com endpoints RAN, Transport e Core
- **Credenciais do GitHub** para acesso ao GHCR (GitHub Container Registry)

### 3.2 Requisitos de Software

**No node1 do NASP (onde o deploy é executado):**

- **kubectl** versão ≥ 1.26 (já instalado via Kubespray)
- **Helm** versão ≥ 3.12 (instalar se não estiver presente)
- **Ansible** versão ≥ 2.14 (opcional, para automação)
- **Docker** ou **containerd** (já configurado)
- **Calico CNI** (já instalado)
- **Python 3** (para scripts auxiliares)

### 3.3 Requisitos de Recursos

**Por nó (Node1/Node2):**
- **CPU**: Mínimo 8 cores (recomendado 16 cores)
- **Memória**: Mínimo 16 GiB (recomendado 32 GiB)
- **Storage**: Mínimo 100 GiB (recomendado 200 GiB)

**Total do cluster:**
- **CPU**: Mínimo 16 cores (distribuídos entre Node1 e Node2)
- **Memória**: Mínimo 32 GiB (distribuída entre Node1 e Node2)
- **Storage**: Mínimo 200 GiB (para volumes persistentes)

### 3.4 Requisitos de Rede

- **Conectividade entre nós**: Node1 e Node2 devem se comunicar via interface `my5g`
- **Conectividade com NASP**: Cluster deve ter acesso aos endpoints NASP (RAN, Transport, Core)
- **DNS**: Resolução DNS funcional (CoreDNS configurado)
- **Portas abertas**: Portas padrão do Kubernetes (6443, 10250, etc.)

---

## 4. Preparação

### 4.1 Acesso Local

**O deploy do TriSLA é feito localmente no node1 do NASP.**

Você já está dentro do node1 do NASP.

**Verificar acesso ao cluster:**

```bash
# Verificar se kubectl está configurado
kubectl cluster-info

# Verificar nós do cluster
kubectl get nodes

# Verificar acesso ao kubeconfig
kubectl config view
```

### 4.2 Kubectl

**O kubeconfig já está disponível localmente no node1:**

```bash
# Verificar kubeconfig padrão
kubectl config view

# Se necessário, configurar KUBECONFIG
export KUBECONFIG=/etc/kubernetes/admin.conf

# Verificar acesso
kubectl cluster-info
kubectl get nodes
```

**Verificar contexto:**

```bash
# Verificar contexto atual
kubectl config current-context

# Listar contextos
kubectl config get-contexts

# Alternar contexto se necessário
kubectl config use-context <context-name>
```

### 4.3 Helm

**Instalar Helm no Node1 (se não estiver instalado):**

```bash
# Conectar ao Node1
# Executar localmente no node1

# Baixar e instalar Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verificar instalação
helm version
```

**Instalar Helm na máquina do operador:**

```bash
# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# macOS
brew install helm

# Windows (via Chocolatey)
choco install kubernetes-helm

# Verificar instalação
helm version
```

**Configurar Helm para usar o kubeconfig:**

```bash
# Helm usa automaticamente o KUBECONFIG configurado
export KUBECONFIG=~/.kube/nasp-config
helm list --all-namespaces
```

### 4.4 GHCR Secret

**Criar Personal Access Token no GitHub:**

1. Acessar: https://github.com/settings/tokens
2. Clicar em "Generate new token (classic)"
3. Selecionar escopos: `read:packages`, `write:packages` (se necessário)
4. Gerar token e copiar (não será exibido novamente)

**Criar secret no Kubernetes:**

```bash
# Criar secret para GHCR
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USERNAME> \
  --docker-password=<GITHUB_PAT_TOKEN> \
  --docker-email=<GITHUB_EMAIL> \
  --namespace=trisla

# Verificar secret criado
kubectl get secret ghcr-secret -n trisla

# Testar pull de imagem (opcional)
kubectl run test-pull --image=ghcr.io/abelisboa/trisla-sem-csmf:latest \
  --rm -it --restart=Never -n trisla -- echo "Pull successful"
```

**Nota**: O namespace `trisla` será criado na seção de pre-flight. Se ainda não existir, criar primeiro:

```bash
kubectl create namespace trisla
```

### 4.5 Testes de Conectividade

**Testar conectividade entre nós (executar localmente no node1):**

```bash
# Verificar nós do cluster
kubectl get nodes -o wide

# Testar conectividade via pod de teste
kubectl run -it --rm test-ping --image=busybox --restart=Never -- ping -c 3 <NODE2_IP>
```
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
grep

**Testar conectividade com NASP:**

```bash
# Testar endpoints NASP (ajustar conforme configuração)
curl -k https://<NASP_RAN_ENDPOINT>/health
curl -k https://<NASP_TRANSPORT_ENDPOINT>/health
curl -k https://<NASP_CORE_ENDPOINT>/health
```

**Testar DNS:**

```bash
# Criar pod de teste
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  nslookup kubernetes.default

# Testar resolução de serviços
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  nslookup kube-dns.kube-system.svc.cluster.local
```

**Testar storage:**

```bash
# Verificar StorageClass
kubectl get storageclass

# Criar PVC de teste
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: test-pvc
  namespace: default
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
  storageClassName: local-path
EOF

# Verificar PVC
kubectl get pvc test-pvc

# Limpar teste
kubectl delete pvc test-pvc
```

---

## 5. Pre-flight Completo

### 5.1 Pre-flight Manual

**Verificar versão do Kubernetes:**

```bash
kubectl version --short
# Deve retornar versão ≥ 1.26
```

**Verificar nodes:**

```bash
kubectl get nodes -o wide
# Ambos Node1 e Node2 devem estar em estado Ready
```

**Verificar componentes do control plane:**

```bash
kubectl get pods -n kube-system | grep -E "etcd|kube-apiserver|kube-controller|kube-scheduler"
# Todos devem estar Running
```

**Verificar Calico:**

```bash
# Verificar pods do Calico
kubectl get pods -n kube-system -l k8s-app=calico-node

# Verificar status do Calico
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}'
```

**Verificar DNS:**

```bash
# Testar DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  nslookup kubernetes.default

# Verificar CoreDNS
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

**Verificar StorageClass:**

```bash
# Listar StorageClasses
kubectl get storageclass

# Verificar se há StorageClass padrão
kubectl get storageclass -o jsonpath='{.items[?(@.metadata.annotations.storageclass\.kubernetes\.io/is-default-class=="true")].metadata.name}'
```

**Verificar recursos disponíveis:**

```bash
# Verificar recursos dos nós
kubectl top nodes

# Verificar capacidade dos nós
kubectl describe nodes | grep -A 5 "Allocated resources"
```

**Verificar Helm:**

```bash
# Verificar versão do Helm
helm version

# Verificar se Helm pode acessar o cluster
helm list --all-namespaces
```

**Verificar acesso ao GHCR:**

```bash
# Testar pull de imagem
docker pull ghcr.io/abelisboa/trisla-sem-csmf:latest
# Ou via kubectl
kubectl run test-ghcr --image=ghcr.io/abelisboa/trisla-sem-csmf:latest \
  --rm -it --restart=Never -- echo "GHCR access OK"
```

### 5.2 Pre-flight Automático (Ansible)

**Executar playbook de pre-flight:**

```bash
# Navegar para diretório do Ansible
cd TriSLA-clean/ansible

# Editar inventory.yaml com IPs corretos
vim inventory.yaml
# Atualizar:
#   - ansible_host para Node1 e Node2
#   - Outras variáveis conforme necessário

# Executar pre-flight
ansible-playbook -i inventory.yaml playbooks/pre-flight.yml
```

**Verificar saída do pre-flight:**

O playbook deve validar:
- Versão do Kubernetes
- Status do Calico
- DNS funcional
- StorageClass disponível
- Helm instalado
- Acesso ao GHCR (se token fornecido)

**Exemplo de saída esperada:**

```
TASK [Resumo do pré-flight]
ok: [node1] => {
    "msg": "Pré-Flight Check Completo:\n- Kubernetes: v1.26.0\n- Helm: v3.12.0\n- Calico: 2/2 pods\n- StorageClass: 1\n- Namespace: Não existe"
}
```

### 5.3 Criar Namespace

**Criar namespace `trisla`:**

```bash
# Criar namespace
kubectl create namespace trisla

# Adicionar labels
kubectl label namespace trisla name=trisla
kubectl label namespace trisla environment=production

# Verificar namespace criado
kubectl get namespace trisla
```

**Ou via Ansible:**

```bash
ansible-playbook -i inventory.yaml playbooks/setup-namespace.yml
```

---

## 6. Instalação Modular

### 6.1 SEM-CSMF

**Deploy do SEM-CSMF:**

```bash
# Criar ConfigMap com configurações
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: sem-csmf-config
  namespace: trisla
data:
  DATABASE_URL: "postgresql://trisla:trisla_password@postgres:5432/trisla"
  DECISION_ENGINE_GRPC: "decision-engine:50051"
  KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
  OTLP_ENDPOINT: "http://otlp-collector:4317"
  LOG_LEVEL: "INFO"
EOF

# Deploy via Helm (será feito na seção 7)
# Ou manualmente via kubectl (não recomendado em produção)
```

**Verificar deploy:**

```bash
# Verificar pod
kubectl get pods -n trisla -l app=sem-csmf

# Verificar logs
kubectl logs -n trisla -l app=sem-csmf --tail=50

# Testar health endpoint
kubectl port-forward -n trisla svc/sem-csmf 8080:8080
curl http://localhost:8080/health
```

### 6.2 ML-NSMF

**Deploy do ML-NSMF:**

```bash
# Criar ConfigMap
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: ml-nsmf-config
  namespace: trisla
data:
  KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
  OTLP_ENDPOINT: "http://otlp-collector:4317"
  LOG_LEVEL: "INFO"
EOF
```

**Verificar deploy:**

```bash
kubectl get pods -n trisla -l app=ml-nsmf
kubectl logs -n trisla -l app=ml-nsmf --tail=50
```

### 6.3 Decision Engine

**Deploy do Decision Engine:**

```bash
# Criar ConfigMap
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: decision-engine-config
  namespace: trisla
data:
  KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
  OTLP_ENDPOINT: "http://otlp-collector:4317"
  LOG_LEVEL: "INFO"
  GRPC_PORT: "50051"
EOF
```

**Verificar deploy:**

```bash
kubectl get pods -n trisla -l app=decision-engine
kubectl logs -n trisla -l app=decision-engine --tail=50

# Testar gRPC
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  grpcurl -plaintext localhost:50051 list
```

### 6.4 BC-NSSMF

**Deploy do BC-NSSMF:**

```bash
# Criar ConfigMap
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: bc-nssmf-config
  namespace: trisla
data:
  KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
  OTLP_ENDPOINT: "http://otlp-collector:4317"
  LOG_LEVEL: "INFO"
  BLOCKCHAIN_NETWORK: "besu"
  BLOCKCHAIN_ENDPOINT: "http://besu-node:8545"
EOF
```

**Verificar deploy:**

```bash
kubectl get pods -n trisla -l app=bc-nssmf
kubectl logs -n trisla -l app=bc-nssmf --tail=50
```

### 6.5 NASP Adapter

**Deploy do NASP Adapter:**

```bash
# Criar ConfigMap
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: nasp-adapter-config
  namespace: trisla
data:
  KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
  OTLP_ENDPOINT: "http://otlp-collector:4317"
  LOG_LEVEL: "INFO"
  NASP_MODE: "production"
  NASP_RAN_ENDPOINT: "https://<NASP_RAN_ENDPOINT>/api/v1"
  NASP_TRANSPORT_ENDPOINT: "https://<NASP_TRANSPORT_ENDPOINT>/api/v1"
  NASP_CORE_ENDPOINT: "https://<NASP_CORE_ENDPOINT>/api/v1"
EOF

# Criar Secret com token NASP
kubectl create secret generic nasp-credentials \
  --from-literal=auth-token="<NASP_AUTH_TOKEN>" \
  --namespace=trisla
```

**Verificar deploy:**

```bash
kubectl get pods -n trisla -l app=nasp-adapter
kubectl logs -n trisla -l app=nasp-adapter --tail=50
```

### 6.6 SLA-Agent Layer

**Deploy do SLA-Agent Layer:**

```bash
# Criar ConfigMap
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: sla-agent-layer-config
  namespace: trisla
data:
  KAFKA_BOOTSTRAP_SERVERS: "kafka:9092"
  OTLP_ENDPOINT: "http://otlp-collector:4317"
  LOG_LEVEL: "INFO"
EOF
```

**Verificar deploy:**

```bash
kubectl get pods -n trisla -l app=sla-agent-layer
kubectl logs -n trisla -l app=sla-agent-layer --tail=50
```

**Nota**: A instalação modular acima é apenas para referência. O deploy completo via Helm (seção 7) é o método recomendado em produção.

---

## 7. Deploy Completo com Helm

### 7.1 Preparar values-nasp.yaml

O arquivo `helm/trisla/values-nasp.yaml` é o arquivo canônico para deploy no NASP e já existe no repositório.

**Se necessário, descobrir endpoints NASP:**

```bash
# Descobrir endpoints reais do NASP
./scripts/discover-nasp-endpoints.sh

# Editar values-nasp.yaml com endpoints descobertos
vim helm/trisla/values-nasp.yaml
```

**Exemplo de `values-nasp.yaml` completo:**

```yaml
# ============================================
# TriSLA Helm Chart - Values para NASP
# ============================================

global:
  imageRegistry: ghcr.io/abelisboa
  imagePullSecrets:
    - name: ghcr-secret
  namespace: trisla

# Network Configuration (NASP específico)
network:
  interface: "my5g"
  nodeIP: "192.168.10.16"  # IP do Node1 (ajustar)
  gateway: "192.168.10.1"  # Gateway (ajustar)

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
    BLOCKCHAIN_NETWORK: "besu"
    BLOCKCHAIN_ENDPOINT: "http://besu-node:8545"

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
    NASP_MODE: "production"
    NASP_RAN_ENDPOINT: "https://<NASP_RAN_ENDPOINT>/api/v1"
    NASP_TRANSPORT_ENDPOINT: "https://<NASP_TRANSPORT_ENDPOINT>/api/v1"
    NASP_CORE_ENDPOINT: "https://<NASP_CORE_ENDPOINT>/api/v1"
  envFrom:
    - secretRef:
        name: nasp-credentials

# Kafka
kafka:
  enabled: true
  image:
    repository: apache/kafka
    tag: "3.5.0"
  replicas: 3
  storage:
    size: 20Gi
    storageClass: "local-path"

# PostgreSQL
postgres:
  enabled: true
  image:
    repository: postgres
    tag: "15-alpine"
  storage:
    size: 10Gi
    storageClass: "local-path"
  env:
    POSTGRES_DB: "trisla"
    POSTGRES_USER: "trisla"
    POSTGRES_PASSWORD: "<GERAR_SENHA_SEGURA>"

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

# Production Settings
production:
  enabled: true
  simulationMode: false
  useRealServices: true
  executeRealActions: true
```

**⚠️ IMPORTANTE**: Ajustar os seguintes valores antes do deploy:
- `network.nodeIP`: IP do Node1
- `network.gateway`: Gateway da rede
- `naspAdapter.env.NASP_*_ENDPOINT`: Endpoints reais do NASP
- `postgres.env.POSTGRES_PASSWORD`: Senha segura
- Criar secret `nasp-credentials` com token NASP

### 7.2 Validar Helm Chart

**Validar sintaxe do chart:**

```bash
# Lint do chart
helm lint ./helm/trisla

# Template do chart (ver o que será criado)
helm template trisla ./helm/trisla \
  --values ./helm/trisla/values-nasp.yaml \
  --debug
```

**Dry-run do deploy:**

```bash
# Dry-run para verificar sem aplicar
helm install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --dry-run \
  --debug
```

### 7.3 Executar Deploy

**Deploy inicial:**

```bash
# Deploy completo
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --wait \
  --timeout 15m
```

**Explicação dos parâmetros:**
- `upgrade --install`: Instala se não existir, atualiza se existir
- `--namespace trisla`: Namespace onde será instalado
- `--create-namespace`: Cria o namespace se não existir
- `--values`: Arquivo de valores customizado
- `--wait`: Aguarda recursos ficarem prontos
- `--timeout 15m`: Timeout de 15 minutos

**Deploy com rollback automático:**

```bash
# Deploy com rollback automático em caso de falha
helm upgrade --install trisla ./helm/trisla \
  --namespace trisla \
  --create-namespace \
  --values ./helm/trisla/values-nasp.yaml \
  --atomic \
  --wait \
  --timeout 15m
```

### 7.4 Verificar Status do Deploy

**Verificar status do release:**

```bash
# Status do release
helm status trisla -n trisla

# Histórico de releases
helm history trisla -n trisla

# Listar recursos criados
helm get manifest trisla -n trisla
```

**Verificar pods:**

```bash
# Status de todos os pods
kubectl get pods -n trisla

# Status detalhado
kubectl get pods -n trisla -o wide

# Verificar pods por módulo
kubectl get pods -n trisla -l app=sem-csmf
kubectl get pods -n trisla -l app=ml-nsmf
kubectl get pods -n trisla -l app=decision-engine
kubectl get pods -n trisla -l app=bc-nssmf
kubectl get pods -n trisla -l app=sla-agent-layer
kubectl get pods -n trisla -l app=nasp-adapter
```

---

## 8. Estrutura Esperada dos Pods

### 8.1 Pods dos Módulos TriSLA

Após o deploy bem-sucedido, a seguinte estrutura de pods deve estar presente:

| Módulo | Replicas Esperadas | Status Esperado | Porta |
|--------|-------------------|-----------------|-------|
| `sem-csmf-*` | 2 | Running | 8080 |
| `ml-nsmf-*` | 2 | Running | 8081 |
| `decision-engine-*` | 2 | Running | 8082 (REST), 50051 (gRPC) |
| `bc-nssmf-*` | 2 | Running | 8083 |
| `sla-agent-layer-*` | 3 | Running | 8084 |
| `nasp-adapter-*` | 2 | Running | 8085 |
| `ui-dashboard-*` | 2 | Running | 80 |

### 8.2 Pods de Infraestrutura

| Componente | Replicas Esperadas | Status Esperado | Porta |
|------------|-------------------|-----------------|-------|
| `kafka-*` | 3 | Running | 9092 |
| `postgres-*` | 1 | Running | 5432 |
| `otlp-collector-*` | 1 | Running | 4317 (gRPC), 4318 (HTTP) |
| `prometheus-*` | 1 | Running | 9090 |
| `grafana-*` | 1 | Running | 3000 |
| `alertmanager-*` | 1 | Running | 9093 |

### 8.3 Verificação Completa

**Comando para verificar todos os pods:**

```bash
# Listar todos os pods no namespace trisla
kubectl get pods -n trisla

# Verificar readiness
kubectl get pods -n trisla -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\t"}{.status.containerStatuses[0].ready}{"\n"}{end}'

# Contar pods por status
kubectl get pods -n trisla --no-headers | awk '{print $3}' | sort | uniq -c
```

**Estrutura esperada de Services:**

```bash
# Listar services
kubectl get svc -n trisla

# Deve haver services para:
# - sem-csmf
# - ml-nsmf
# - decision-engine
# - bc-nssmf
# - sla-agent-layer
# - nasp-adapter
# - ui-dashboard
# - kafka
# - postgres
# - otlp-collector
# - prometheus
# - grafana
# - alertmanager
```

---

## 9. Validações Após Deploy

### 9.1 Validação de Saúde dos Pods

**Verificar todos os pods em Running:**

```bash
# Verificar pods não Running
kubectl get pods -n trisla --field-selector=status.phase!=Running

# Se houver pods problemáticos, investigar
kubectl describe pod <pod-name> -n trisla
kubectl logs <pod-name> -n trisla --previous
```

**Verificar readiness e liveness:**

```bash
# Verificar readiness
kubectl get pods -n trisla -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[?(@.type=="Ready")].status}{"\n"}{end}'

# Verificar liveness
kubectl get pods -n trisla -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.containerStatuses[0].ready}{"\n"}{end}'
```

### 9.2 Validação de Endpoints

**Testar health endpoints:**

```bash
# SEM-CSMF
kubectl port-forward -n trisla svc/sem-csmf 8080:8080 &
curl http://localhost:8080/health

# ML-NSMF
kubectl port-forward -n trisla svc/ml-nsmf 8081:8081 &
curl http://localhost:8081/health

# Decision Engine
kubectl port-forward -n trisla svc/decision-engine 8082:8082 &
curl http://localhost:8082/health

# BC-NSSMF
kubectl port-forward -n trisla svc/bc-nssmf 8083:8083 &
curl http://localhost:8083/health

# SLA-Agent Layer
kubectl port-forward -n trisla svc/sla-agent-layer 8084:8084 &
curl http://localhost:8084/health

# NASP Adapter
kubectl port-forward -n trisla svc/nasp-adapter 8085:8085 &
curl http://localhost:8085/health
```

### 9.3 Validação de Conectividade

**Testar comunicação entre módulos:**

```bash
# Do SEM-CSMF para Decision Engine (gRPC)
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=sem-csmf -o jsonpath='{.items[0].metadata.name}') -- \
  grpcurl -plaintext decision-engine:50051 list

# Do Decision Engine para ML-NSMF (REST)
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://ml-nsmf:8081/health

# Do Decision Engine para BC-NSSMF (REST)
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://bc-nssmf:8083/health
```

**Testar Kafka:**

```bash
# Verificar tópicos Kafka
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=kafka -o jsonpath='{.items[0].metadata.name}') -- \
  kafka-topics.sh --list --bootstrap-server localhost:9092

# Verificar consumer groups
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=kafka -o jsonpath='{.items[0].metadata.name}') -- \
  kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list
```

**Testar PostgreSQL:**

```bash
# Conectar ao PostgreSQL
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- \
  psql -U trisla -d trisla -c "SELECT version();"
```

### 9.4 Validação de Integração com NASP

**Testar conectividade com NASP:**

```bash
# Via NASP Adapter
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  curl -k https://<NASP_RAN_ENDPOINT>/health

# Verificar logs de conexão
kubectl logs -n trisla -l app=nasp-adapter | grep -i "nasp\|connection\|error"
```

### 9.5 Validação de Observabilidade

**Verificar Prometheus:**

```bash
# Port-forward Prometheus
kubectl port-forward -n trisla svc/prometheus 9090:9090

# Acessar: http://localhost:9090
# Verificar targets: http://localhost:9090/targets
```

**Verificar Grafana:**

```bash
# Port-forward Grafana
kubectl port-forward -n trisla svc/grafana 3000:3000

# Acessar: http://localhost:3000
# Credenciais: admin/admin (alterar em produção)
```

**Verificar métricas OTLP:**

```bash
# Verificar OTLP Collector
kubectl logs -n trisla -l app=otlp-collector --tail=50
```

### 9.6 Script de Validação Automática

**Executar script de validação:**

```bash
# Validação completa
./scripts/validate-production-real.sh

# Validação de infraestrutura NASP
./scripts/validate-nasp-infra.sh

# Validação E2E
./scripts/validate-e2e-pipeline.sh
```

---

## 10. Testes E2E no Cluster NASP

### 10.1 Teste de Fluxo Completo

**1. Criar intent via SEM-CSMF:**

```bash
# Port-forward SEM-CSMF
kubectl port-forward -n trisla svc/sem-csmf 8080:8080 &

# Criar intent
curl -X POST http://localhost:8080/api/v1/intents \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-001",
    "intent": "Criar slice para aplicação de realidade aumentada com latência < 10ms e throughput > 1Gbps",
    "priority": "high"
  }'
```

**2. Verificar NEST gerado:**

```bash
# Verificar NEST no banco de dados
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- \
  psql -U trisla -d trisla -c "SELECT id, tenant_id, status FROM intents ORDER BY created_at DESC LIMIT 5;"
```

**3. Verificar predição ML:**

```bash
# Verificar logs do ML-NSMF
kubectl logs -n trisla -l app=ml-nsmf | grep -i "predict\|prediction"
```

**4. Verificar decisão:**

```bash
# Verificar logs do Decision Engine
kubectl logs -n trisla -l app=decision-engine | grep -i "decision\|ACCEPT\|REJECT"
```

**5. Verificar registro em blockchain:**

```bash
# Verificar logs do BC-NSSMF
kubectl logs -n trisla -l app=bc-nssmf | grep -i "contract\|transaction\|blockchain"
```

**6. Verificar ação no NASP:**

```bash
# Verificar logs do NASP Adapter
kubectl logs -n trisla -l app=nasp-adapter | grep -i "action\|provision\|nasp"
```

### 10.2 Teste de Carga

**Executar teste de carga:**

```bash
# Via script
./scripts/run-load-test.ps1

# Ou manualmente
kubectl run -it --rm load-test --image=curlimages/curl --restart=Never -n trisla -- \
  sh -c "for i in \$(seq 1 100); do curl -X POST http://sem-csmf:8080/api/v1/intents -H 'Content-Type: application/json' -d '{\"tenant_id\":\"tenant-001\",\"intent\":\"Test intent $i\"}'; done"
```

### 10.3 Teste de Resiliência

**Testar failover:**

```bash
# Deletar um pod do SEM-CSMF
kubectl delete pod -n trisla -l app=sem-csmf --field-selector=status.phase=Running | head -1

# Verificar se outro pod assume
kubectl get pods -n trisla -l app=sem-csmf

# Verificar se serviço continua funcionando
kubectl port-forward -n trisla svc/sem-csmf 8080:8080 &
curl http://localhost:8080/health
```

---

## 11. Troubleshooting Específico do NASP

### 11.1 Problemas de Conectividade com NASP

**Sintoma**: NASP Adapter não consegue conectar aos endpoints NASP

**Diagnóstico:**

```bash
# Verificar logs
kubectl logs -n trisla -l app=nasp-adapter | grep -i "error\|connection\|timeout"

# Testar conectividade de rede
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  ping -c 3 <NASP_NODE_IP>

# Testar DNS
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  nslookup <NASP_ENDPOINT>
```

**Solução:**

```bash
# Verificar Network Policies
kubectl get networkpolicies -n trisla

# Verificar se egress está permitido
kubectl describe networkpolicy <policy-name> -n trisla | grep -A 20 "Egress"

# Se necessário, ajustar Network Policy para permitir egress para NASP
```

### 11.2 Problemas com Calico no NASP

**Sintoma**: Pods não conseguem se comunicar entre si

**Diagnóstico:**

```bash
# Verificar status do Calico
kubectl get pods -n kube-system -l k8s-app=calico-node

# Verificar logs do Calico
kubectl logs -n kube-system -l k8s-app=calico-node --tail=50

# Verificar BGP (se configurado)
kubectl exec -n kube-system -l k8s-app=calico-node -- calicoctl node status
```

**Solução:**

```bash
# Reiniciar pods do Calico
kubectl delete pod -n kube-system -l k8s-app=calico-node

# Verificar se reiniciou
kubectl get pods -n kube-system -l k8s-app=calico-node
```

### 11.3 Problemas com Storage no NASP

**Sintoma**: PVCs não sendo provisionados

**Diagnóstico:**

```bash
# Verificar PVCs pendentes
kubectl get pvc -n trisla

# Verificar eventos
kubectl describe pvc <pvc-name> -n trisla

# Verificar StorageClass
kubectl get storageclass
```

**Solução:**

```bash
# Verificar se há espaço disponível nos nós
kubectl describe nodes | grep -A 5 "Allocated resources"

# Verificar volumes locais (se usando local-path)
# Verificar storage localmente
df -h /opt/local-path-provisioner
kubectl get nodes -o jsonpath='{.items[*].status.capacity.storage}'
```

### 11.4 Problemas com Prometheus no NASP

**Sintoma**: Métricas não sendo coletadas

**Diagnóstico:**

```bash
# Verificar Prometheus
kubectl get pods -n monitoring -l app=prometheus

# Verificar ServiceMonitors
kubectl get servicemonitor --all-namespaces

# Verificar targets no Prometheus
kubectl port-forward -n monitoring svc/prometheus-k8s 9090:9090
# Acessar: http://localhost:9090/targets
```

**Solução:**

```bash
# Criar ServiceMonitor para módulos TriSLA
# Ver exemplo em monitoring/prometheus/
kubectl apply -f monitoring/prometheus/servicemonitors/
```

### 11.5 Problemas de Recursos

**Sintoma**: Pods sendo evicted ou OOMKilled

**Diagnóstico:**

```bash
# Verificar recursos dos nós
kubectl top nodes

# Verificar recursos dos pods
kubectl top pods -n trisla

# Verificar eventos de eviction
kubectl get events -n trisla --sort-by='.lastTimestamp' | grep -i "evict\|oom"
```

**Solução:**

```bash
# Ajustar recursos no values-nasp.yaml
# Aumentar limits conforme necessário
vim helm/trisla/values-nasp.yaml

# Aplicar atualização
helm upgrade trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml \
  --wait
```

---

## 12. Checklist Final do Operador

### 12.1 Pré-Deploy

- [ ] Acesso local ao node1 configurado (você já está dentro do node1)
- [ ] kubectl configurado e conectado ao cluster
- [ ] Helm instalado e funcionando
- [ ] GHCR secret criado no namespace trisla
- [ ] NASP credentials secret criado
- [ ] values-nasp.yaml preparado com valores corretos
- [ ] Pre-flight manual executado e validado
- [ ] Pre-flight automático (Ansible) executado com sucesso
- [ ] Namespace `trisla` criado

### 12.2 Deploy

- [ ] Helm chart validado (`helm lint`)
- [ ] Dry-run executado sem erros
- [ ] Deploy executado com sucesso
- [ ] Todos os pods em estado Running
- [ ] Todos os pods com readiness OK (1/1 ou 2/2)
- [ ] Services criados corretamente
- [ ] ConfigMaps e Secrets aplicados

### 12.3 Validação

- [ ] Health endpoints respondendo (todos os módulos)
- [ ] Comunicação entre módulos funcionando
- [ ] Kafka funcionando (tópicos criados, consumer groups ativos)
- [ ] PostgreSQL acessível e funcionando
- [ ] Integração com NASP funcionando
- [ ] OTLP Collector coletando métricas
- [ ] Prometheus coletando métricas dos módulos
- [ ] Grafana acessível e dashboards carregando

### 12.4 Testes E2E

- [ ] Teste de criação de intent executado com sucesso
- [ ] NEST gerado corretamente
- [ ] Predição ML funcionando
- [ ] Decisão sendo tomada
- [ ] Registro em blockchain funcionando
- [ ] Ação no NASP executada
- [ ] Teste de carga executado (opcional)
- [ ] Teste de resiliência executado (failover)

### 12.5 Documentação e Handover

- [ ] Logs coletados e arquivados
- [ ] Configurações documentadas
- [ ] Credenciais seguras armazenadas (não no repositório)
- [ ] Equipe treinada no uso do sistema
- [ ] Runbooks criados para operação
- [ ] Monitoramento configurado e alertas ativos

### 12.6 Checklist de Produção

- [ ] Backup do banco de dados configurado
- [ ] Rotação de logs configurada
- [ ] Retenção de métricas configurada
- [ ] Alertas críticos configurados
- [ ] Processo de atualização documentado
- [ ] Processo de rollback testado
- [ ] Documentação de troubleshooting disponível
- [ ] Contatos de suporte definidos

---

## Conclusão

This guide provides instruções completas para implantar o TriSLA in the NASP environment. Siga os passos na ordem apresentada e valide cada etapa antes de prosseguir para a próxima.

**Lembre-se:**
- Sempre validar pre-flight antes do deploy
- Coletar logs em caso de problemas
- Testar integração com NASP após deploy
- Manter documentação atualizada
- Executar testes E2E regularmente

**Última atualização:** 2025-01-XX  
**Versão do documento:** 1.0.0  
**Versão do TriSLA:** 1.0.0

**Referências:**
- `README_OPERATIONS_PROD.md`: Guia de operações em produção
- `TROUBLESHOOTING_TRISLA.md`: Guia de troubleshooting
- `SECURITY_HARDENING.md`: Guia de segurança e hardening


