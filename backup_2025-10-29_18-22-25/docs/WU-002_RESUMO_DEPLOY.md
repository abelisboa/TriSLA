# 🚀 WU-002 — Resumo do Deploy Core Modules

**Data:** 2025-10-17  
**Status:** ✅ **PREPARADO PARA EXECUÇÃO**  
**Responsável:** Abel José Rodrigues Lisboa

---

## ✅ ARQUIVOS CRIADOS

### 📁 Manifestos YAML (5 arquivos)

| Arquivo | Caminho | Status |
|---------|---------|--------|
| SEM-NSMF | `helm/deployments/trisla-semantic.yaml` | ✅ |
| ML-NSMF | `helm/deployments/trisla-ai.yaml` | ✅ |
| BC-NSSMF | `helm/deployments/trisla-blockchain.yaml` | ✅ |
| Integration | `helm/deployments/trisla-integration.yaml` | ✅ |
| Monitoring | `helm/deployments/trisla-monitoring.yaml` | ✅ |

### 📜 Scripts e Documentação

| Arquivo | Descrição | Status |
|---------|-----------|--------|
| `scripts/deploy_core.sh` | Script automatizado de deploy | ✅ |
| `docs/WU-002_DEPLOY_INSTRUCTIONS.md` | Instruções completas | ✅ |
| `docs/WU-002_COMANDOS_RAPIDOS.sh` | Comandos prontos para uso | ✅ |
| `docs/evidencias/WU-002_deploy_core/README.md` | Guia de evidências | ✅ |

**Total: 9 arquivos criados**

---

## 🎯 CARACTERÍSTICAS DOS DEPLOYMENTS

### Configurações Padrão

- **Réplicas:** 1 por deployment
- **Restart Policy:** Always
- **Image Pull Policy:** IfNotPresent
- **Namespace:** trisla-nsp

### Recursos Configurados

| Módulo | CPU Request | CPU Limit | Memory Request | Memory Limit |
|--------|-------------|-----------|----------------|--------------|
| SEM-NSMF | 250m | 500m | 256Mi | 512Mi |
| ML-NSMF | 250m | 500m | 512Mi | 1Gi |
| BC-NSSMF | 250m | 500m | 256Mi | 512Mi |
| Integration | 250m | 500m | 256Mi | 512Mi |
| Monitoring | 250m | 500m | 256Mi | 512Mi |

### Health Checks Configurados

Todos os módulos possuem:
- ✅ **Liveness Probe** (HTTP GET /health)
- ✅ **Readiness Probe** (HTTP GET /ready)
- ✅ Timeouts e thresholds configurados

---

## 🔌 PORTAS E SERVIÇOS

| Módulo | HTTP Port | gRPC Port | Outros |
|--------|-----------|-----------|--------|
| SEM-NSMF | 8080 | 9090 | - |
| ML-NSMF | 8080 | 9090 | - |
| BC-NSSMF | 7070 | 9090 | 7051 (Fabric) |
| Integration | 8080 | 9090 | - |
| Monitoring | 8080 | 9090 | 14268 (Traces) |

---

## 🚀 COMO EXECUTAR O DEPLOY

### Opção 1: Script Automatizado (Recomendado)

```bash
# No servidor NASP
cd /home/porvir5g/gtp5g/trisla-nsp
./scripts/deploy_core.sh
```

### Opção 2: Deploy Manual

```bash
# No servidor NASP
cd /home/porvir5g/gtp5g/trisla-nsp
kubectl apply -f helm/deployments/ -n trisla-nsp
```

### Opção 3: Deploy Módulo por Módulo

```bash
kubectl apply -f helm/deployments/trisla-semantic.yaml -n trisla-nsp
kubectl apply -f helm/deployments/trisla-ai.yaml -n trisla-nsp
kubectl apply -f helm/deployments/trisla-blockchain.yaml -n trisla-nsp
kubectl apply -f helm/deployments/trisla-integration.yaml -n trisla-nsp
kubectl apply -f helm/deployments/trisla-monitoring.yaml -n trisla-nsp
```

---

## 📋 PASSO A PASSO COMPLETO

### 1. Preparação (no seu computador Windows)

```bash
# Verificar arquivos criados
ls helm/deployments/
ls scripts/
ls docs/WU-002_*
```

### 2. Transferência para NASP

```bash
# Criar estrutura no servidor
ssh porvir5g@node1
mkdir -p /home/porvir5g/gtp5g/trisla-nsp/{helm/deployments,scripts,docs/evidencias/WU-002_deploy_core,logs}

# Transferir arquivos (do seu computador)
scp -r helm/deployments/*.yaml porvir5g@node1:/home/porvir5g/gtp5g/trisla-nsp/helm/deployments/
scp scripts/deploy_core.sh porvir5g@node1:/home/porvir5g/gtp5g/trisla-nsp/scripts/
```

### 3. Execução (no servidor NASP)

```bash
cd /home/porvir5g/gtp5g/trisla-nsp
chmod +x scripts/deploy_core.sh
./scripts/deploy_core.sh
```

### 4. Verificação

```bash
kubectl get pods -n trisla-nsp
kubectl get svc -n trisla-nsp
kubectl get all -n trisla-nsp
```

---

## ✅ RESULTADO ESPERADO

```
NAME                                        READY   STATUS    RESTARTS   AGE
trisla-semantic-layer-xxxxxx                1/1     Running   0          2m
trisla-ai-layer-xxxxxx                      1/1     Running   0          2m
trisla-blockchain-layer-xxxxxx              1/1     Running   0          2m
trisla-integration-layer-xxxxxx             1/1     Running   0          2m
trisla-monitoring-layer-xxxxxx              1/1     Running   0          2m
```

---

## 📊 EVIDÊNCIAS GERADAS

Após o deploy, os seguintes arquivos serão criados automaticamente:

```
/home/porvir5g/gtp5g/trisla-nsp/
├── logs/
│   └── deploy_core.log
└── docs/evidencias/WU-002_deploy_core/
    ├── deploy_log.txt
    ├── deploy_validation.json
    ├── pods_list.txt
    ├── services_list.txt
    ├── deployments_list.txt
    └── {pod-name}_describe.txt (5 arquivos)
```

---

## 🔧 TROUBLESHOOTING

### Imagens não encontradas?

As imagens usam `ghcr.io/trisla/trisla-*:latest`. Se não estiverem disponíveis:

```bash
# Usar imagens de teste (nginx)
kubectl set image deployment/trisla-semantic-layer -n trisla-nsp sem-nsmf=nginx:alpine
```

### Pods não iniciam?

```bash
# Ver logs
kubectl logs -n trisla-nsp deployment/trisla-semantic-layer

# Ver eventos
kubectl describe pod -n trisla-nsp {pod-name}
```

### Namespace não existe?

```bash
kubectl create namespace trisla-nsp
```

---

## 🧹 ROLLBACK

Se necessário remover tudo:

```bash
kubectl delete -f helm/deployments/ -n trisla-nsp
```

---

## 📞 SUPORTE

- **Documentação completa:** `docs/WU-002_DEPLOY_INSTRUCTIONS.md`
- **Comandos rápidos:** `docs/WU-002_COMANDOS_RAPIDOS.sh`
- **Contato:** abel.lisboa@unisinos.br

---

## ✅ CHECKLIST DE VALIDAÇÃO

- [ ] Arquivos YAML criados (5)
- [ ] Script de deploy criado
- [ ] Documentação completa
- [ ] Arquivos transferidos para NASP
- [ ] Namespace `trisla-nsp` existe
- [ ] Script executado com sucesso
- [ ] 5 pods em Running
- [ ] 5 services criados
- [ ] Health checks respondendo
- [ ] Evidências coletadas
- [ ] Logs salvos

---

📅 **Criado em:** 17/10/2025  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada




