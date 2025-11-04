# TriSLA Portal - Guia de Troubleshooting

Este guia contém soluções para problemas comuns encontrados durante a instalação e operação do TriSLA Portal.

## 🔍 Problemas de Deploy

### 1. Erro de Pull de Imagem

**Sintoma:**
```
Failed to pull image "ghcr.io/abelisboa/trisla-api:latest": 
rpc error: code = Unknown desc = failed to resolve reference "ghcr.io/abelisboa/trisla-api:latest"
```

**Causa:** Credenciais do GHCR não configuradas ou incorretas.

**Solução:**
```bash
# Verificar se o secret existe
kubectl get secret ghcr-creds -n trisla-nsp

# Se não existir, criar
kubectl create secret docker-registry ghcr-creds \
  --docker-server=ghcr.io \
  --docker-username=SEU_USUARIO \
  --docker-password=SEU_PAT \
  --namespace=trisla-nsp

# Verificar se o secret está correto
kubectl get secret ghcr-creds -n trisla-nsp -o yaml
```

### 2. Pods em CrashLoopBackOff

**Sintoma:**
```
NAME                    READY   STATUS             RESTARTS   AGE
trisla-portal-xxx       0/2     CrashLoopBackOff   5          2m
```

**Diagnóstico:**
```bash
# Verificar logs do pod
kubectl logs -n trisla-nsp deployment/trisla-portal

# Verificar descrição do pod
kubectl describe pod -n trisla-nsp -l app=trisla-portal
```

**Possíveis Causas e Soluções:**

#### A. Erro de Módulo Python
```
ModuleNotFoundError: No module named 'apps'
```

**Solução:**
```bash
# Verificar se PYTHONPATH está configurado
kubectl get deployment trisla-portal -n trisla-nsp -o yaml | grep PYTHONPATH

# Se não estiver, atualizar o deployment
kubectl patch deployment trisla-portal -n trisla-nsp -p '{"spec":{"template":{"spec":{"containers":[{"name":"trisla-api","env":[{"name":"PYTHONPATH","value":"/app/apps/api"}]}]}}}}'
```

#### B. Erro de Porta
```
Address already in use
```

**Solução:**
```bash
# Verificar se há conflito de portas
kubectl get pods -n trisla-nsp -o wide

# Verificar configuração de portas no values.yaml
grep -A 5 -B 5 "containerPort" helm/trisla-portal/values.yaml
```

### 3. Erro de Conexão Redis

**Sintoma:**
```
redis.exceptions.ConnectionError: Error -2 connecting to redis:6379. Name or service not known.
```

**Solução:**
```bash
# Verificar se Redis está rodando
kubectl get pods -n trisla-nsp | grep redis

# Se não estiver, criar deployment do Redis
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: trisla-nsp
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7.4.6-alpine
        ports:
        - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: trisla-nsp
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
EOF
```

## 🔧 Problemas de Configuração

### 1. Erro de Validação Helm

**Sintoma:**
```
Error: template: trisla-portal/templates/deployment.yaml:XX:XX: 
executing "trisla-portal/templates/deployment.yaml" at <.Values.backend.containerPort>: 
nil pointer evaluating interface {}.containerPort
```

**Solução:**
```bash
# Verificar se values.yaml está correto
helm template trisla-portal ./helm/trisla-portal --values ./helm/trisla-portal/values.yaml

# Verificar se todos os valores obrigatórios estão definidos
grep -A 10 "backend:" helm/trisla-portal/values.yaml
```

### 2. Erro de Namespace

**Sintoma:**
```
Error: namespaces "trisla-nsp" not found
```

**Solução:**
```bash
# Criar namespace
kubectl create namespace trisla-nsp

# Ou usar --create-namespace no helm
helm install trisla-portal ./helm/trisla-portal --namespace trisla-nsp --create-namespace
```

### 3. Erro de Recursos

**Sintoma:**
```
0/3 nodes are available: 3 Insufficient cpu, 3 Insufficient memory
```

**Solução:**
```bash
# Verificar recursos disponíveis
kubectl describe nodes

# Ajustar recursos no values.yaml
# Reduzir requests e limits
resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 50m
    memory: 64Mi
```

## 🌐 Problemas de Rede

### 1. Port-Forward Não Funciona

**Sintoma:**
```
Unable to connect to the server: dial tcp 127.0.0.1:8080: connect: connection refused
```

**Solução:**
```bash
# Verificar se o serviço existe
kubectl get services -n trisla-nsp

# Verificar se o pod está rodando
kubectl get pods -n trisla-nsp

# Tentar port-forward novamente
kubectl port-forward -n trisla-nsp svc/sem-nsmf 8080:8080
```

### 2. Erro de DNS

**Sintoma:**
```
Name or service not known
```

**Solução:**
```bash
# Verificar se o CoreDNS está funcionando
kubectl get pods -n kube-system | grep coredns

# Verificar resolução DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup redis.trisla-nsp.svc.cluster.local
```

## 📊 Problemas de Monitoramento

### 1. Prometheus Não Coleta Métricas

**Sintoma:**
```
No targets found
```

**Solução:**
```bash
# Verificar se o ServiceMonitor existe
kubectl get servicemonitor -n trisla-nsp

# Verificar se o Prometheus está configurado
kubectl get prometheus -n monitoring

# Verificar se o namespace está sendo monitorado
kubectl get prometheus -n monitoring -o yaml | grep -A 5 -B 5 "serviceMonitorSelector"
```

### 2. Grafana Não Acessível

**Sintoma:**
```
Unable to connect to Grafana
```

**Solução:**
```bash
# Verificar se o Grafana está rodando
kubectl get pods -n monitoring | grep grafana

# Verificar o serviço
kubectl get services -n monitoring | grep grafana

# Port-forward para Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

## 🔄 Problemas de RQ Worker

### 1. RQ Worker Não Processa Jobs

**Sintoma:**
```
Jobs ficam em estado "queued" indefinidamente
```

**Solução:**
```bash
# Verificar se o RQ Worker está rodando
kubectl get pods -n trisla-nsp | grep rq-worker

# Verificar logs do RQ Worker
kubectl logs -n trisla-nsp deployment/rq-worker

# Verificar se Redis está acessível
kubectl exec -n trisla-nsp deployment/rq-worker -- python3 -c "import redis; r = redis.Redis(host='redis', port=6379); print(r.ping())"
```

### 2. Erro de Conexão RQ

**Sintoma:**
```
ConnectionError: Error -2 connecting to redis:6379
```

**Solução:**
```bash
# Verificar se Redis está rodando
kubectl get pods -n trisla-nsp | grep redis

# Verificar conectividade
kubectl exec -n trisla-nsp deployment/rq-worker -- nc -zv redis 6379
```

## 🚨 Problemas de Performance

### 1. Alto Uso de CPU

**Sintoma:**
```
CPU usage > 80%
```

**Solução:**
```bash
# Verificar uso de recursos
kubectl top pods -n trisla-nsp

# Ajustar recursos
kubectl patch deployment trisla-portal -n trisla-nsp -p '{"spec":{"template":{"spec":{"containers":[{"name":"trisla-api","resources":{"limits":{"cpu":"1000m"},"requests":{"cpu":"500m"}}}]}}}}'
```

### 2. Alto Uso de Memória

**Sintoma:**
```
Memory usage > 80%
```

**Solução:**
```bash
# Verificar uso de memória
kubectl top pods -n trisla-nsp

# Ajustar recursos
kubectl patch deployment trisla-portal -n trisla-nsp -p '{"spec":{"template":{"spec":{"containers":[{"name":"trisla-api","resources":{"limits":{"memory":"1Gi"},"requests":{"memory":"512Mi"}}}]}}}}'
```

## 🔍 Comandos de Diagnóstico

### Verificar Status Geral
```bash
# Status dos pods
kubectl get pods -n trisla-nsp -o wide

# Status dos serviços
kubectl get services -n trisla-nsp

# Status dos deployments
kubectl get deployments -n trisla-nsp

# Eventos recentes
kubectl get events -n trisla-nsp --sort-by='.lastTimestamp'
```

### Verificar Logs
```bash
# Logs de todos os pods
kubectl logs -n trisla-nsp --all-containers=true

# Logs de um pod específico
kubectl logs -n trisla-nsp deployment/trisla-portal

# Logs em tempo real
kubectl logs -f -n trisla-nsp deployment/trisla-portal
```

### Verificar Recursos
```bash
# Uso de recursos dos pods
kubectl top pods -n trisla-nsp

# Uso de recursos dos nodes
kubectl top nodes

# Descrição detalhada de um pod
kubectl describe pod -n trisla-nsp -l app=trisla-portal
```

### Verificar Rede
```bash
# Testar conectividade
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -qO- http://sem-nsmf.trisla-nsp.svc.cluster.local:8080/api/v1/health

# Verificar DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup sem-nsmf.trisla-nsp.svc.cluster.local
```

## 📞 Suporte

Se você encontrar um problema que não está listado aqui:

1. Verifique os logs do sistema
2. Execute o script de validação: `./scripts/validate_trisla.sh`
3. Consulte a documentação do Kubernetes
4. Abra uma issue no GitHub com:
   - Descrição detalhada do problema
   - Logs relevantes
   - Configuração do ambiente
   - Passos para reproduzir

## 🔗 Links Úteis

- [Kubernetes Troubleshooting](https://kubernetes.io/docs/tasks/debug-application-cluster/)
- [Helm Troubleshooting](https://helm.sh/docs/troubleshooting/)
- [Prometheus Troubleshooting](https://prometheus.io/docs/guides/troubleshooting/)
- [Redis Troubleshooting](https://redis.io/docs/management/troubleshooting/)

