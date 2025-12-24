# TriSLA — Guia Canônico de Instalação

**Versão:** 1.0  
**Data:** 2025-01-27  
**Registry:** `ghcr.io/abelisboa`  
**Tag padrão:** `trisla-public-v1.0-rc1`

---

## Visão Geral

### O que será implantado

O TriSLA é uma arquitetura distribuída para gerenciamento automatizado de SLAs em redes 5G/O-RAN. Esta instalação implanta os seguintes módulos principais:

- **SEM-NSMF** (Semantic-enhanced Network Slice Management Function): Interpretação semântica de intents e geração de NEST
- **ML-NSMF** (Machine Learning Network Slice Management Function): Predição de viabilidade de SLAs com Explainable AI
- **BC-NSSMF** (Blockchain-enabled Network Slice Subnet Management Function): Registro imutável de SLAs em blockchain
- **Portal Backend**: API REST para observabilidade e gerenciamento

### Resultado final esperado

Após a instalação bem-sucedida:

- Todos os pods em estado `Ready`
- Services expostos e acessíveis
- Health endpoints respondendo
- Logs sem erros críticos (CrashLoopBackOff)
- Sistema pronto para processar SLAs

---

## Arquitetura de Implantação

### Tabela de Módulos

| Módulo | Imagem GHCR | Porta/Endpoint | Helm Resource | Status |
|--------|-------------|----------------|---------------|--------|
| SEM-NSMF | `ghcr.io/abelisboa/trisla-sem-nsmf:trisla-public-v1.0-rc1` | 8080 | `deployment-sem-csmf` | Opcional |
| ML-NSMF | `ghcr.io/abelisboa/trisla-ml-nsmf:trisla-public-v1.0-rc1` | 8081 | `deployment-ml-nsmf` | Opcional |
| BC-NSSMF | `ghcr.io/abelisboa/trisla-bc-nssmf:trisla-public-v1.0-rc1` | 8083 | `deployment-bc-nssmf` | Opcional |
| Portal Backend | `ghcr.io/abelisboa/trisla-portal-backend:trisla-public-v1.0-rc1` | 8000 | `deployment-portal-backend` | Opcional |

**Nota:** Todas as imagens estão disponíveis publicamente em `ghcr.io/abelisboa/` com a tag `trisla-public-v1.0-rc1`.

### Estrutura Helm

- **Chart:** `helm/trisla/`
- **Namespace padrão:** `trisla`
- **Release name:** `trisla` (configurável)

---

## Requisitos Mínimos

### Recursos de Hardware

**Recomendado para instalação completa:**
- **CPU:** 8 cores (mínimo: 4 cores)
- **RAM:** 16 GiB (mínimo: 8 GiB)
- **Disco:** 50 GiB (mínimo: 20 GiB)

**Por módulo (aproximado):**
- SEM-NSMF: 2 CPU, 2 GiB RAM
- ML-NSMF: 4 CPU, 4 GiB RAM
- BC-NSSMF: 2 CPU, 2 GiB RAM
- Portal Backend: 0.5 CPU, 512 MiB RAM

### Versões de Software

- **Kubernetes:** ≥ 1.24
- **Helm:** ≥ 3.8
- **kubectl:** ≥ 1.24
- **Docker/containerd:** Qualquer versão compatível com Kubernetes

### Acesso ao GHCR

As imagens são públicas e não requerem autenticação. Se o cluster não tiver acesso à internet, configure um registry mirror ou faça pull manual das imagens.

---

## Pré-requisitos do Cluster

### Namespace

O namespace `trisla` será criado automaticamente pelo Helm. Para criar manualmente:

```bash
kubectl create namespace trisla
```

**Validação:**
```bash
kubectl get namespace trisla
```

**Saída esperada:**
```
NAME     STATUS   AGE
trisla   Active   1s
```

### StorageClass

Verificar se existe uma StorageClass disponível:

```bash
kubectl get storageclass
```

**Saída esperada:**
```
NAME                   PROVISIONER       RECLAIMPOLICY   VOLUMEBINDINGMODE   ALLOWVOLUMEEXPANSION   AGE
standard (default)     kubernetes.io...  Delete          Immediate           false                  1d
```

Se nenhuma StorageClass estiver disponível, criar uma ou configurar `storageClass: ""` nos values do Helm.

### Ingress (Opcional)

Para expor serviços externamente, um Ingress Controller deve estar instalado:

```bash
kubectl get ingressclass
```

**Saída esperada:**
```
NAME    CONTROLLER             PARAMETERS   AGE
nginx   ingress-nginx/nginx   <none>        1d
```

### DNS Interno

O CoreDNS deve estar funcionando para resolução de nomes internos:

```bash
kubectl get pods -n kube-system | grep coredns
```

**Saída esperada:**
```
coredns-xxx   1/1     Running   0          1d
```

---

## Credenciais do GHCR

### Cenário A: Imagens Públicas (Sem Secret)

As imagens do TriSLA são públicas e não requerem autenticação. O Helm chart está configurado para usar imagens públicas por padrão.

**Validação:**
```bash
docker pull ghcr.io/abelisboa/trisla-sem-nsmf:trisla-public-v1.0-rc1
```

**Saída esperada:**
```
trisla-public-v1.0-rc1: Pulling from abelisboa/trisla-sem-nsmf
...
Status: Downloaded newer image for ghcr.io/abelisboa/trisla-sem-nsmf:trisla-public-v1.0-rc1
```

### Cenário B: Se Exigir Secret (Opcional)

Se o cluster exigir autenticação no GHCR (configuração específica do cluster), criar o secret:

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USERNAME> \
  --docker-password=<GITHUB_TOKEN> \
  --docker-email=<EMAIL> \
  -n trisla
```

**Validação:**
```bash
kubectl get secret ghcr-secret -n trisla
```

**Saída esperada:**
```
NAME          TYPE                             DATA   AGE
ghcr-secret   kubernetes.io/dockerconfigjson   1      5s
```

**Nota:** Para imagens públicas, este secret não é necessário. O Helm chart está configurado para usar `imagePullSecrets` apenas se especificado nos values.

---

## Modo A — Implantação Rápida (Cluster Existente)

### Passo 1: Criar Namespace

```bash
kubectl create namespace trisla
```

**Validação:**
```bash
kubectl get namespace trisla
```

### Passo 2: Instalar via Helm

```bash
helm upgrade --install trisla helm/trisla \
  --namespace trisla \
  --set semCsmf.enabled=true \
  --set semCsmf.image.tag=trisla-public-v1.0-rc1 \
  --set mlNsmf.enabled=true \
  --set mlNsmf.image.tag=trisla-public-v1.0-rc1 \
  --set bcNssmf.enabled=true \
  --set bcNssmf.image.tag=trisla-public-v1.0-rc1 \
  --set global.imagePullSecrets=[] \
  --wait
```

**Validação:**
```bash
helm list -n trisla
```

**Saída esperada:**
```
NAME    NAMESPACE       REVISION        UPDATED                                 STATUS   CHART         APP VERSION
trisla  trisla          1                2025-01-27 12:00:00.000000 +0000 UTC deployed trisla-3.7.10 3.7.10
```

### Passo 3: Monitorar Deploy

```bash
kubectl -n trisla get pods -w
```

**Saída esperada (após alguns minutos):**
```
NAME                              READY   STATUS    RESTARTS   AGE
trisla-sem-csmf-xxx               1/1     Running   0          2m
trisla-ml-nsmf-xxx                1/1     Running   0          2m
trisla-bc-nssmf-xxx               1/1     Running   0          2m
trisla-portal-backend-xxx         1/1     Running   0          2m
```

### Passo 4: Validar Services

```bash
kubectl -n trisla get services
```

**Saída esperada:**
```
NAME                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
trisla-sem-csmf         ClusterIP   10.96.xxx.xxx   <none>        8080/TCP   2m
trisla-ml-nsmf          ClusterIP   10.96.xxx.xxx   <none>        8081/TCP   2m
trisla-bc-nssmf         ClusterIP   10.96.xxx.xxx   <none>        8083/TCP   2m
trisla-portal-backend   ClusterIP   10.96.xxx.xxx   <none>        8000/TCP   2m
```

### Passo 5: Validar Endpoints

```bash
kubectl -n trisla get endpoints
```

**Saída esperada:**
```
NAME                    ENDPOINTS                    AGE
trisla-sem-csmf         10.244.x.x:8080              2m
trisla-ml-nsmf          10.244.x.x:8081               2m
trisla-bc-nssmf         10.244.x.x:8083               2m
trisla-portal-backend   10.244.x.x:8000               2m
```

---

## Modo B — Implantação Local (Minikube/Kind)

### Passo 1: Subir Cluster Local

**Minikube:**
```bash
minikube start --cpus=4 --memory=8192
minikube addons enable ingress
```

**Validação:**
```bash
kubectl get nodes
```

**Saída esperada:**
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.28.0
```

**Kind:**
```bash
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 8080
EOF
```

### Passo 2: Habilitar Ingress (Minikube)

```bash
minikube addons enable ingress
```

**Validação:**
```bash
kubectl get pods -n ingress-nginx
```

**Saída esperada:**
```
NAME                                        READY   STATUS    RESTARTS   AGE
ingress-nginx-controller-xxx                1/1     Running   0          1m
```

### Passo 3: Aplicar Helm

Seguir os mesmos passos do **Modo A** (Passo 2 em diante).

---

## Validação Funcional

### Checklist de Validação

#### 1. Pods Ready

```bash
kubectl -n trisla get pods
```

**Saída esperada:**
```
NAME                              READY   STATUS    RESTARTS   AGE
trisla-sem-csmf-xxx               1/1     Running   0          5m
trisla-ml-nsmf-xxx                1/1     Running   0          5m
trisla-bc-nssmf-xxx               1/1     Running   0          5m
trisla-portal-backend-xxx         1/1     Running   0          5m
```

**Critério:** Todos os pods devem estar `1/1 Ready` e `STATUS: Running`.

#### 2. Services OK

```bash
kubectl -n trisla get services -o wide
```

**Saída esperada:**
```
NAME                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE   SELECTOR
trisla-sem-csmf         ClusterIP   10.96.xxx.xxx   <none>        8080/TCP   5m    app=trisla-sem-csmf
trisla-ml-nsmf          ClusterIP   10.96.xxx.xxx   <none>        8081/TCP   5m    app=trisla-ml-nsmf
trisla-bc-nssmf         ClusterIP   10.96.xxx.xxx   <none>        8083/TCP   5m    app=trisla-bc-nssmf
trisla-portal-backend   ClusterIP   10.96.xxx.xxx   <none>        8000/TCP   5m    app=trisla-portal-backend
```

**Critério:** Todos os services devem ter `CLUSTER-IP` atribuído e `SELECTOR` correto.

#### 3. Health Endpoints

**SEM-NSMF:**
```bash
kubectl -n trisla exec -it deployment/trisla-sem-csmf -- curl -s http://localhost:8080/health
```

**Saída esperada:**
```json
{"status":"healthy","service":"sem-csmf"}
```

**ML-NSMF:**
```bash
kubectl -n trisla exec -it deployment/trisla-ml-nsmf -- curl -s http://localhost:8081/health
```

**Saída esperada:**
```json
{"status":"healthy","service":"ml-nsmf"}
```

**BC-NSSMF:**
```bash
kubectl -n trisla exec -it deployment/trisla-bc-nssmf -- curl -s http://localhost:8083/health
```

**Saída esperada:**
```json
{"status":"healthy","service":"bc-nssmf"}
```

**Portal Backend:**
```bash
kubectl -n trisla exec -it deployment/trisla-portal-backend -- curl -s http://localhost:8000/health
```

**Saída esperada:**
```json
{"status":"healthy","service":"portal-backend"}
```

#### 4. Logs Sem CrashLoopBackOff

```bash
kubectl -n trisla get pods | grep -v Running
```

**Saída esperada:**
```
(nenhuma saída - todos os pods devem estar Running)
```

**Verificar logs de erros:**
```bash
kubectl -n trisla logs -l app=trisla-sem-csmf --tail=50 | grep -i error
```

**Saída esperada:**
```
(nenhuma saída ou apenas warnings não críticos)
```

#### 5. Teste de Conectividade Interna

```bash
kubectl -n trisla run test-pod --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl -s http://trisla-sem-csmf:8080/health
```

**Saída esperada:**
```json
{"status":"healthy","service":"sem-csmf"}
```

---

## Troubleshooting Canônico

### ImagePullBackOff

**Sintoma:**
```bash
kubectl -n trisla get pods
```
```
NAME                    READY   STATUS             RESTARTS   AGE
trisla-sem-csmf-xxx      0/1     ImagePullBackOff   3          2m
```

**Causa:** Cluster não consegue fazer pull da imagem do GHCR.

**Solução:**
1. Verificar conectividade com GHCR:
```bash
kubectl -n trisla run test-pull --image=curlimages/curl:latest --rm -it --restart=Never -- \
  curl -I https://ghcr.io
```

2. Se necessário, configurar registry mirror ou pull manual:
```bash
docker pull ghcr.io/abelisboa/trisla-sem-nsmf:trisla-public-v1.0-rc1
docker save ghcr.io/abelisboa/trisla-sem-nsmf:trisla-public-v1.0-rc1 | \
  kubectl -n trisla run import --image=busybox -i --rm --restart=Never -- sh -c 'cat > /tmp/image.tar'
```

### CrashLoopBackOff

**Sintoma:**
```bash
kubectl -n trisla get pods
```
```
NAME                    READY   STATUS             RESTARTS   AGE
trisla-sem-csmf-xxx      0/1     CrashLoopBackOff   5          3m
```

**Diagnóstico:**
```bash
kubectl -n trisla logs deployment/trisla-sem-csmf --tail=100
```

**Causas comuns:**
- Variáveis de ambiente faltando
- Dependências não disponíveis (Kafka, etc.)
- Configuração incorreta

**Solução:**
1. Verificar logs:
```bash
kubectl -n trisla logs deployment/trisla-sem-csmf --previous
```

2. Verificar variáveis de ambiente:
```bash
kubectl -n trisla describe pod -l app=trisla-sem-csmf | grep -A 20 "Environment:"
```

3. Ajustar values do Helm conforme necessário.

### PVC Pending

**Sintoma:**
```bash
kubectl -n trisla get pvc
```
```
NAME           STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS   AGE
besu-data-xxx  Pending                                      standard       5m
```

**Causa:** StorageClass não disponível ou recursos insuficientes.

**Solução:**
1. Verificar StorageClass:
```bash
kubectl get storageclass
```

2. Se necessário, desabilitar persistência:
```bash
helm upgrade trisla helm/trisla -n trisla \
  --set besu.persistence.enabled=false
```

### DNS/Service Not Found

**Sintoma:**
```bash
kubectl -n trisla exec -it deployment/trisla-sem-csmf -- \
  curl http://trisla-ml-nsmf:8081/health
```
```
curl: (6) Could not resolve host: trisla-ml-nsmf
```

**Causa:** CoreDNS não está funcionando ou service não existe.

**Solução:**
1. Verificar CoreDNS:
```bash
kubectl get pods -n kube-system | grep coredns
```

2. Verificar service:
```bash
kubectl -n trisla get service trisla-ml-nsmf
```

3. Usar FQDN completo:
```bash
kubectl -n trisla exec -it deployment/trisla-sem-csmf -- \
  curl http://trisla-ml-nsmf.trisla.svc.cluster.local:8081/health
```

### Porta/Endpoint Não Responde

**Sintoma:**
```bash
kubectl -n trisla exec -it deployment/trisla-sem-csmf -- \
  curl http://localhost:8080/health
```
```
curl: (7) Failed to connect to localhost port 8080: Connection refused
```

**Causa:** Aplicação não está escutando na porta configurada ou não iniciou corretamente.

**Solução:**
1. Verificar logs:
```bash
kubectl -n trisla logs deployment/trisla-sem-csmf --tail=50
```

2. Verificar porta do container:
```bash
kubectl -n trisla describe pod -l app=trisla-sem-csmf | grep -A 5 "Ports:"
```

3. Verificar se o processo está rodando:
```bash
kubectl -n trisla exec -it deployment/trisla-sem-csmf -- ps aux
```

---

## Desinstalação / Limpeza

### Desinstalar Helm Release

```bash
helm uninstall trisla -n trisla
```

**Validação:**
```bash
helm list -n trisla
```

**Saída esperada:**
```
(empty - nenhum release)
```

### Deletar Namespace

```bash
kubectl delete namespace trisla
```

**Validação:**
```bash
kubectl get namespace trisla
```

**Saída esperada:**
```
Error from server (NotFound): namespaces "trisla" not found
```

### Limpeza Completa (Opcional)

Se PVCs foram criados e precisam ser removidos:

```bash
kubectl get pvc -n trisla
kubectl delete pvc --all -n trisla
```

**Nota:** A remoção do namespace remove automaticamente todos os recursos, exceto PVCs que precisam ser removidos manualmente.

---

## Referências

- **Documentação completa:** `docs/README.md`
- **Arquitetura:** `docs/ARCHITECTURE.md`
- **Helm Chart:** `helm/trisla/`
- **Imagens Docker:** https://github.com/orgs/abelisboa/packages

---

**Última atualização:** 2025-01-27

