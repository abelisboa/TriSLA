# 🚀 WU-002 — Deploy Core Modules TriSLA@NASP

**Data:** 2025-10-17  
**Responsável:** Abel José Rodrigues Lisboa  
**Ambiente:** NASP@UNISINOS

---

## 📋 INSTRUÇÕES DE DEPLOY

### 🎯 Objetivo

Implantar os 5 módulos principais do TriSLA no cluster NASP:
1. **SEM-NSMF** — Camada Semântica e Ontológica
2. **ML-NSMF** — Camada de Inteligência Artificial
3. **BC-NSSMF** — Camada Blockchain
4. **Integration Layer** — Gateway de Integração
5. **Monitoring Layer** — Observabilidade

---

## 🔧 PRÉ-REQUISITOS

✅ Acesso SSH ao servidor NASP (`ssh porvir5g@node1`)  
✅ Kubeconfig configurado (`~/.kube/config-nasp`)  
✅ Namespace `trisla-nsp` criado  
✅ Kubectl e Helm instalados  
✅ Acesso ao GitHub Container Registry (ghcr.io)

---

## 📁 ESTRUTURA DE ARQUIVOS GERADOS

```
/home/porvir5g/gtp5g/trisla-nsp/
├── helm/
│   └── deployments/
│       ├── trisla-semantic.yaml      ✅ Criado
│       ├── trisla-ai.yaml            ✅ Criado
│       ├── trisla-blockchain.yaml    ✅ Criado
│       ├── trisla-integration.yaml   ✅ Criado
│       └── trisla-monitoring.yaml    ✅ Criado
├── scripts/
│   └── deploy_core.sh                ✅ Criado
├── docs/
│   └── evidencias/WU-002_deploy_core/
└── logs/
    └── deploy_core.log
```

---

## 🚀 PROCEDIMENTO DE DEPLOY

### Passo 1: Conectar ao servidor NASP

```bash
ssh porvir5g@node1
cd /home/porvir5g/gtp5g
```

### Passo 2: Criar a estrutura de diretórios

```bash
mkdir -p trisla-nsp/{helm/deployments,scripts,docs/evidencias/WU-002_deploy_core,logs}
cd trisla-nsp
```

### Passo 3: Transferir os arquivos

Transfira os seguintes arquivos do repositório local para o servidor:

```bash
# No seu computador local (Windows)
scp -r helm/deployments/*.yaml porvir5g@node1:/home/porvir5g/gtp5g/trisla-nsp/helm/deployments/
scp scripts/deploy_core.sh porvir5g@node1:/home/porvir5g/gtp5g/trisla-nsp/scripts/
```

### Passo 4: Configurar permissões

```bash
# No servidor NASP
cd /home/porvir5g/gtp5g/trisla-nsp
chmod +x scripts/deploy_core.sh
```

### Passo 5: Verificar o kubeconfig

```bash
# Verificar conectividade com o cluster
kubectl cluster-info
kubectl get nodes

# Verificar/criar namespace
kubectl get namespace trisla-nsp || kubectl create namespace trisla-nsp
```

### Passo 6: Executar o deploy

```bash
# Executar o script de deploy
cd /home/porvir5g/gtp5g/trisla-nsp
./scripts/deploy_core.sh
```

---

## 🔍 VERIFICAÇÃO DO DEPLOY

### Verificar status dos pods

```bash
kubectl get pods -n trisla-nsp
```

**Resultado esperado:**
```
NAME                                        READY   STATUS    RESTARTS   AGE
trisla-semantic-layer-xxxxxx                1/1     Running   0          2m
trisla-ai-layer-xxxxxx                      1/1     Running   0          2m
trisla-blockchain-layer-xxxxxx              1/1     Running   0          2m
trisla-integration-layer-xxxxxx             1/1     Running   0          2m
trisla-monitoring-layer-xxxxxx              1/1     Running   0          2m
```

### Verificar serviços

```bash
kubectl get svc -n trisla-nsp
```

**Resultado esperado:**
```
NAME                   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)
trisla-semantic        ClusterIP   10.96.x.x       <none>        8080/TCP,9090/TCP
trisla-ai              ClusterIP   10.96.x.x       <none>        8080/TCP,9090/TCP
trisla-blockchain      ClusterIP   10.96.x.x       <none>        7070/TCP,9090/TCP
trisla-integration     ClusterIP   10.96.x.x       <none>        8080/TCP,9090/TCP
trisla-monitoring      ClusterIP   10.96.x.x       <none>        8080/TCP,9090/TCP
```

### Verificar logs de um pod

```bash
kubectl logs -n trisla-nsp deployment/trisla-semantic-layer --tail=20
```

### Testar comunicação interna

```bash
# Teste de health check do SEM-NSMF
kubectl exec -n trisla-nsp deploy/trisla-semantic-layer -- curl -s http://localhost:8080/health

# Teste de comunicação entre módulos
kubectl exec -n trisla-nsp deploy/trisla-integration-layer -- curl -s http://trisla-semantic:8080/health
```

---

## 📊 EVIDÊNCIAS COLETADAS

Após o deploy bem-sucedido, os seguintes arquivos são gerados automaticamente:

```
docs/evidencias/WU-002_deploy_core/
├── deploy_log.txt                    # Log completo do deploy
├── deploy_validation.json            # Resumo em JSON
├── pods_list.txt                     # Lista de pods
├── services_list.txt                 # Lista de serviços
├── deployments_list.txt              # Lista de deployments
└── {pod-name}_describe.txt           # Descrição de cada pod
```

---

## 🔧 COMANDOS ÚTEIS

### Verificar recursos de um pod

```bash
kubectl top pods -n trisla-nsp
```

### Ver eventos do namespace

```bash
kubectl get events -n trisla-nsp --sort-by='.lastTimestamp'
```

### Reiniciar um deployment

```bash
kubectl rollout restart deployment/trisla-semantic-layer -n trisla-nsp
```

### Ver logs em tempo real

```bash
kubectl logs -n trisla-nsp -f deployment/trisla-ai-layer
```

### Descrever um pod (debugging)

```bash
kubectl describe pod -n trisla-nsp trisla-semantic-layer-xxxxx
```

---

## ⚠️ TROUBLESHOOTING

### Problema: Pod em status ImagePullBackOff

**Causa:** Imagens Docker não disponíveis no ghcr.io

**Solução:**
```bash
# Verificar se as imagens existem ou usar imagens mock para teste
kubectl set image deployment/trisla-semantic-layer -n trisla-nsp \
  sem-nsmf=nginx:alpine
```

### Problema: Pod em status CrashLoopBackOff

**Causa:** Aplicação falhando ao iniciar

**Solução:**
```bash
# Ver logs do pod
kubectl logs -n trisla-nsp trisla-semantic-layer-xxxxx

# Ver eventos
kubectl describe pod -n trisla-nsp trisla-semantic-layer-xxxxx
```

### Problema: Namespace não encontrado

**Solução:**
```bash
kubectl create namespace trisla-nsp
```

### Problema: Permissão negada ao executar script

**Solução:**
```bash
chmod +x scripts/deploy_core.sh
```

---

## 🧹 ROLLBACK (se necessário)

Para remover todos os deployments:

```bash
# Deletar todos os recursos do namespace
kubectl delete -f helm/deployments/ -n trisla-nsp

# Ou deletar o namespace inteiro (cuidado!)
kubectl delete namespace trisla-nsp
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

- [ ] Todos os 5 pods em status `Running`
- [ ] Todos os pods com `READY 1/1`
- [ ] 0 restarts nos pods
- [ ] Todos os serviços criados (5 services)
- [ ] Health checks respondendo (HTTP 200)
- [ ] Logs sem erros críticos
- [ ] Evidências coletadas em `docs/evidencias/WU-002_deploy_core/`
- [ ] Log de deploy salvo em `logs/deploy_core.log`

---

## 📞 SUPORTE

Em caso de problemas:
1. Verificar logs: `logs/deploy_core.log`
2. Verificar eventos: `kubectl get events -n trisla-nsp`
3. Contatar: Abel Lisboa (abel.lisboa@unisinos.br)

---

📅 **Criado em:** 17/10/2025  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS




