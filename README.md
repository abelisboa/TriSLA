# TriSLA Portal - Sistema de Orquestração SLA-Aware para Redes 5G/O-RAN

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Kubernetes](https://img.shields.io/badge/kubernetes-1.28+-blue.svg)](https://kubernetes.io/)
[![Docker](https://img.shields.io/badge/docker-24.0+-blue.svg)](https://www.docker.com/)
[![Helm](https://img.shields.io/badge/helm-3.12+-blue.svg)](https://helm.sh/)

## 📋 Visão Geral

O **TriSLA Portal** é um sistema abrangente de orquestração SLA-aware para redes 5G/O-RAN, integrando tecnologias de Inteligência Artificial, Ontologia Semântica e Blockchain para fornecer gerenciamento inteligente de slices de rede.

### 🎯 Características Principais

- **Orquestração Inteligente**: Gerenciamento automático de slices 5G baseado em SLA
- **Integração Multi-Tecnologia**: IA, Ontologia Semântica e Blockchain
- **Observabilidade Completa**: Monitoramento em tempo real com Prometheus/Grafana
- **Arquitetura Microserviços**: Deploy nativo em Kubernetes
- **API RESTful**: Interface programática para integração
- **Interface Web**: Dashboard intuitivo para operadores

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TriSLA UI     │    │   TriSLA API    │    │   RQ Worker     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (Background)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │     Redis       │              │
         │              │   (Message Q)   │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SEM-NSMF      │    │   ML-NSMF       │    │   BC-NSSMF      │
│  (Semantic)     │    │   (AI/ML)       │    │  (Blockchain)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Início Rápido

### Pré-requisitos

- **Kubernetes**: 1.28+ (testado com kubeadm)
- **Helm**: 3.12+
- **Docker/Podman**: 24.0+
- **Ansible**: 2.14+ (para automação)
- **Git**: 2.40+

### Instalação Rápida

1. **Clone o repositório**:
```bash
git clone https://github.com/abelisboa/TriSLA-Portal.git
cd TriSLA-Portal
```

2. **Configure as credenciais do GHCR**:
```bash
# Crie um Personal Access Token no GitHub
# https://github.com/settings/tokens
kubectl create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=SEU_USUARIO \
  --docker-password=SEU_PAT \
  --namespace=trisla-nsp
```

3. **Deploy com Helm**:
```bash
# Instalar dependências
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Deploy do TriSLA Portal
helm install trisla-portal ./helm/trisla-portal \
  --namespace trisla-nsp \
  --create-namespace \
  --values ./helm/trisla-portal/values-example.yaml
```

4. **Verificar instalação**:
```bash
kubectl get pods -n trisla-nsp
kubectl get services -n trisla-nsp
```

## 📖 Documentação Detalhada

### Configuração

#### 1. Arquivo de Valores Helm (`values.yaml`)

```yaml
# Configurações principais
namespace: trisla-nsp
replicaCount: 1

# Backend (FastAPI)
backend:
  image: ghcr.io/abelisboa/trisla-api:latest
  pullPolicy: IfNotPresent
  containerPort: 8000
  env:
    PYTHONPATH: "/app/apps/api"
    REDIS_HOST: "redis"
    REDIS_PORT: "6379"

# Frontend (Nginx)
frontend:
  image: nginx:alpine
  pullPolicy: IfNotPresent
  containerPort: 80
  service:
    port: 5173

# Redis
redis:
  image: redis:7.4.6-alpine
  pullPolicy: IfNotPresent
  containerPort: 6379

# RQ Worker
rqWorker:
  image: ghcr.io/abelisboa/trisla-api:latest
  pullPolicy: IfNotPresent
  command: ["python3", "-c"]
  args: ["import rq; from rq import Worker; import redis; r = redis.Redis(host='redis', port=6379); w = Worker(['default'], connection=r); w.work()"]

# Recursos
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi

# Image Pull Secrets
imagePullSecrets:
  - name: ghcr-creds
```

#### 2. Inventário Ansible (`inventory.yaml`)

```yaml
all:
  children:
    k8s_cluster:
      hosts:
        node1:
          ansible_host: 192.168.10.16
          ansible_user: porvir5g
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
        node2:
          ansible_host: 192.168.10.17
          ansible_user: porvir5g
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
        node3:
          ansible_host: 192.168.10.18
          ansible_user: porvir5g
          ansible_ssh_private_key_file: ~/.ssh/id_rsa
```

### Deploy com Ansible

```bash
# Deploy completo automatizado
ansible-playbook -i inventory.yaml playbooks/03_deploy_trisla.yml

# Verificar status
ansible-playbook -i inventory.yaml playbooks/04_verify_and_monitor.yml
```

## 🧪 Testes e Validação

### Cenários de Teste

O sistema foi validado com os seguintes cenários:

1. **URLLC (Ultra-Reliable Low-Latency Communications)**
   - Cirurgia remota
   - Latência: < 10ms
   - Confiabilidade: 99.9%

2. **eMBB (Enhanced Mobile Broadband)**
   - Streaming 4K
   - Largura de banda: 1 Gbps
   - Latência: < 50ms

3. **mMTC (Massive Machine Type Communications)**
   - IoT massivo
   - Conexões: 10.000+
   - Latência: < 100ms

### Scripts de Teste

```bash
# Executar todos os testes
./scripts/run_experiments.sh

# Teste específico de cenário
curl -X POST http://localhost:8080/api/v1/slices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-urllc",
    "type": "URLLC",
    "requirements": {
      "latency": 10,
      "reliability": 99.9
    }
  }'

# Validação do sistema
./scripts/validate_trisla.sh
```

## 📊 Monitoramento e Observabilidade

### Prometheus + Grafana

```bash
# Instalar Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Acessar Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Usuário: admin, Senha: prom-operator
```

### Métricas Disponíveis

- **Performance**: Tempo de resposta, throughput
- **Recursos**: CPU, memória, rede
- **SLA**: Taxa de sucesso, latência
- **Jobs**: Status de processamento RQ

## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro de Pull de Imagem
```bash
# Verificar credenciais
kubectl get secret ghcr-creds -n trisla-nsp -o yaml

# Recriar secret
kubectl delete secret ghcr-creds -n trisla-nsp
kubectl create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=SEU_USUARIO \
  --docker-password=SEU_PAT \
  --namespace=trisla-nsp
```

#### 2. Pods em CrashLoopBackOff
```bash
# Verificar logs
kubectl logs -n trisla-nsp deployment/trisla-portal

# Verificar descrição
kubectl describe pod -n trisla-nsp -l app=trisla-portal
```

#### 3. Erro de Conexão Redis
```bash
# Verificar se Redis está rodando
kubectl get pods -n trisla-nsp | grep redis

# Verificar logs do Redis
kubectl logs -n trisla-nsp deployment/redis
```

### Logs e Debugging

```bash
# Logs em tempo real
kubectl logs -f -n trisla-nsp deployment/trisla-portal

# Executar comando no pod
kubectl exec -it -n trisla-nsp deployment/trisla-portal -- /bin/bash

# Verificar eventos
kubectl get events -n trisla-nsp --sort-by='.lastTimestamp'
```

## 📈 Resultados Experimentais

### Performance Validada

- **Taxa de Sucesso**: 100% (8/8 jobs processados)
- **Tempo Médio de Processamento**: ~5 segundos
- **Disponibilidade**: 100% durante os testes
- **Uso de Recursos**: Otimizado (CPU: 2m, Memória: 39Mi)

### Cenários Testados

| Cenário | Tipo | Latência | Confiabilidade | Status |
|---------|------|----------|----------------|--------|
| Cirurgia Remota | URLLC | < 10ms | 99.9% | ✅ Sucesso |
| Streaming 4K | eMBB | < 50ms | 99.5% | ✅ Sucesso |
| IoT Massivo | mMTC | < 100ms | 99.0% | ✅ Sucesso |
| Load Test 1-5 | Misto | < 60ms | 99.8% | ✅ Sucesso |

## 🤝 Contribuição

### Como Contribuir

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código

- **Python**: PEP 8
- **JavaScript/React**: ESLint + Prettier
- **YAML**: Yamllint
- **Docker**: Best practices

## 📚 Referências

- [5G Architecture](https://www.3gpp.org/specifications/releases)
- [O-RAN Alliance](https://www.o-ran.org/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- **Abel Lisboa** - *Desenvolvimento e Pesquisa* - [@abelisboa](https://github.com/abelisboa)
- **NASP-UNISINOS** - *Infraestrutura e Suporte*

## 🙏 Agradecimentos

- Laboratório NASP-UNISINOS
- Comunidade 5G/O-RAN
- Contribuidores do projeto

---

**TriSLA Portal** - Orquestração Inteligente para Redes 5G/O-RAN 🚀