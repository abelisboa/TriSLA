# TriSLA v3.4.0 - NASP Deployment Runbook

**Versão:** 3.4.0  
**Data:** 2025-01-22  
**Ambiente:** NASP Cluster (Kubernetes)

---

## 📋 Visão Geral

Este runbook descreve o processo completo de deploy do TriSLA v3.4.0 no ambiente NASP (Network Automation Service Platform), um cluster Kubernetes com 2 nodes.

---

## 🎯 Pré-requisitos

### 1. Acesso ao Cluster NASP

- ✅ Acesso SSH aos nodes do cluster
- ✅ Acesso `kubectl` configurado
- ✅ Permissões de deploy no namespace `trisla`

### 2. Ferramentas Necessárias

- ✅ Helm 3.8+
- ✅ Ansible 2.9+
- ✅ Docker (para validação local)
- ✅ `kubectl` configurado

### 3. Recursos do Cluster

- ✅ Mínimo 2 nodes Kubernetes
- ✅ CNI configurado (Calico recomendado)
- ✅ StorageClass disponível
- ✅ Ingress Controller (Nginx recomendado)

---

## 📦 Passo 1: Preparação do Ambiente

### 1.1 Clonar o Repositório

```bash
git clone https://github.com/abelisboa/TriSLA.git
cd TriSLA
git checkout v3.4.0
```

### 1.2 Executar Pré-Check do Cluster NASP

**⚠️ IMPORTANTE:** Execute este script no node1 do NASP antes de iniciar o deploy.

```bash
# No node1 do NASP
bash scripts/pre-check-nasp.sh
```

Este script realiza:
- ✅ Verificação dos nodes do cluster
- ✅ Criação de StorageClass (NFS) se necessário
- ✅ Correção de CoreDNS pendente
- ✅ Habilitação do node2 (uncordon)
- ✅ Criação do namespace `trisla`
- ✅ Criação de ServiceAccount e RBAC
- ✅ Validação/reinstalação do stack Prometheus/Grafana
- ✅ Validação final do cluster

**Nota:** Ajuste o IP do servidor NFS (`NFS_SERVER`) no script se necessário.

### 1.2 Configurar Acesso ao GHCR

```bash
# Criar secret para pull de imagens do GHCR
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GHCR_USERNAME> \
  --docker-password=<GHCR_TOKEN> \
  --namespace=trisla
```

### 1.3 Validar Imagens GHCR

```bash
# Executar script de auditoria
python3 scripts/audit_ghcr_images.py

# Verificar matriz de imagens
cat docs/ghcr/IMAGES_GHCR_MATRIX.md
```

---

## 🔧 Passo 2: Configuração dos Values

### 2.1 Preencher values-nasp.yaml

```bash
# Usar script interativo
./scripts/fill_values_production.sh

# Ou editar manualmente
nano nasp/values-nasp.yaml
```

**Campos obrigatórios a preencher:**

- `network.nodeIP` - IP do node principal
- `network.interface` - Interface de rede NASP
- `naspAdapter.naspEndpoints.*` - Endpoints reais do NASP
- `security.jwtSecretKey` - Secret JWT para autenticação
- `postgresql.passwordSecret` - Secret do PostgreSQL

### 2.2 Validar Configuração

```bash
# Validar sintaxe YAML
yamllint nasp/values-nasp.yaml

# Validar Helm chart
helm lint helm/trisla -f nasp/values-nasp.yaml
```

---

## 🚀 Passo 3: Deploy Automático (Recomendado)

### 3.1 Deploy com Script Automatizado

**⚠️ RECOMENDADO:** Use o script automatizado que faz deploy, detecta erros e corrige automaticamente.

```bash
# No node1 do NASP
bash scripts/deploy-trisla-nasp-auto.sh
```

Este script:
- ✅ Valida todos os pré-requisitos
- ✅ Corrige erros automaticamente (namespace, secrets, storage, etc.)
- ✅ Monitora pods em tempo real
- ✅ Valida logs de cada módulo
- ✅ Gera relatório completo em Markdown

**Log completo:** `/tmp/trisla-deploy.log`  
**Relatório:** `/tmp/trisla-deploy-report-*.md`

### 3.2 Deploy Manual com Helm (Alternativa)

Se preferir fazer deploy manual:

```bash
helm upgrade --install trisla-portal \
  ./helm/trisla \
  -n trisla \
  -f ./nasp/values-nasp.yaml \
  --timeout 15m \
  --wait \
  --debug
```

## 🚀 Passo 4: Deploy com Ansible (Opcional)

### 3.1 Configurar Inventory

```bash
# Editar inventory com IPs reais (não commitar)
nano ansible/inventory-nasp.yaml
```

### 3.2 Executar Pre-flight Checks

```bash
ansible-playbook -i ansible/inventory-nasp.yaml \
  ansible/playbooks/pre-flight.yml
```

### 3.3 Criar Namespace

```bash
ansible-playbook -i ansible/inventory-nasp.yaml \
  ansible/playbooks/setup-namespace.yml
```

### 3.4 Deploy do TriSLA

```bash
ansible-playbook -i ansible/inventory-nasp.yaml \
  ansible/playbooks/deploy-trisla-nasp.yml \
  -e "values_file=nasp/values-nasp.yaml"
```

### 3.5 Validar Deploy

```bash
ansible-playbook -i ansible/inventory-nasp.yaml \
  ansible/playbooks/validate-cluster.yml
```

---

## 🔍 Passo 4: Validação Pós-Deploy

### 4.1 Verificar Pods

```bash
kubectl get pods -n trisla

# Todos os pods devem estar em estado Running
```

### 4.2 Verificar Serviços

```bash
kubectl get svc -n trisla

# Verificar que todos os serviços estão expostos
```

### 4.3 Verificar Logs

```bash
# Logs do SEM-CSMF
kubectl logs -n trisla -l app=sem-csmf --tail=50

# Logs do Decision Engine
kubectl logs -n trisla -l app=decision-engine --tail=50

# Logs do NASP-Adapter
kubectl logs -n trisla -l app=nasp-adapter --tail=50
```

### 4.4 Testar Interfaces

```bash
# I-02: SEM-CSMF REST API
curl http://<SEM_CSMF_SERVICE>:8080/health

# I-01: Decision Engine gRPC (requer grpcurl)
grpcurl -plaintext <DECISION_ENGINE_SERVICE>:50051 list

# I-07: NASP-Adapter REST API
curl http://<NASP_ADAPTER_SERVICE>:8085/health
```

---

## 🔄 Passo 5: Rollback (se necessário)

### 5.1 Verificar Histórico do Helm

```bash
helm history trisla -n trisla
```

### 5.2 Executar Rollback

```bash
# Rollback para versão anterior
helm rollback trisla <REVISION> -n trisla

# Ou rollback para versão específica
helm rollback trisla 1 -n trisla
```

---

## 📊 Passo 6: Monitoramento

### 6.1 Acessar Prometheus

```bash
# Port-forward para acesso local
kubectl port-forward -n trisla svc/prometheus 9090:9090

# Acessar: http://localhost:9090
```

### 6.2 Acessar Grafana

```bash
# Port-forward para acesso local
kubectl port-forward -n trisla svc/grafana 3000:3000

# Acessar: http://localhost:3000
# Credenciais padrão: admin/admin
```

### 6.3 Verificar Métricas

```bash
# Métricas do SEM-CSMF
curl http://<SEM_CSMF_SERVICE>:8080/metrics

# Métricas do Decision Engine
curl http://<DECISION_ENGINE_SERVICE>:8082/metrics
```

---

## 🐛 Troubleshooting

### Problema: Pods em CrashLoopBackOff

```bash
# Verificar logs
kubectl logs -n trisla <POD_NAME> --previous

# Verificar eventos
kubectl describe pod -n trisla <POD_NAME>
```

### Problema: Imagens não encontradas

```bash
# Verificar secret do GHCR
kubectl get secret ghcr-secret -n trisla

# Re-criar secret se necessário
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GHCR_USERNAME> \
  --docker-password=<GHCR_TOKEN> \
  --namespace=trisla \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Problema: Serviços não acessíveis

```bash
# Verificar NetworkPolicies
kubectl get networkpolicies -n trisla

# Verificar Ingress
kubectl get ingress -n trisla
```

---

## 📝 Checklist de Validação

- [ ] Todos os pods em estado Running
- [ ] Todos os serviços expostos corretamente
- [ ] Interface I-01 (gRPC) acessível
- [ ] Interface I-02 (REST SEM-CSMF) acessível
- [ ] Interface I-07 (REST NASP-Adapter) acessível
- [ ] Kafka topics criados
- [ ] PostgreSQL conectado
- [ ] Prometheus coletando métricas
- [ ] Grafana dashboards funcionando
- [ ] NASP endpoints configurados corretamente

---

## 🔗 Referências

- **Documentação Completa:** `docs/nasp/NASP_DEPLOY_RUNBOOK.md`
- **Checklist Pré-Deploy:** `docs/nasp/NASP_PREDEPLOY_CHECKLIST_v3.4.md`
- **Guia de Values:** `docs/deployment/VALUES_PRODUCTION_GUIDE.md`
- **Matriz de Imagens:** `docs/ghcr/IMAGES_GHCR_MATRIX.md`

---

**Versão do Runbook:** 3.4.0  
**Última Atualização:** 2025-01-22

