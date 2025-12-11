# Deploy do Módulo BESU no NASP

## 📋 Visão Geral

Este documento descreve o processo completo de deploy do módulo **Hyperledger Besu** no cluster NASP, integrado ao **BC-NSSMF** do TriSLA.

**Versão:** 3.7.10  
**Data:** 2025-01-15  
**Módulo:** BESU - Blockchain Client

---

## 🎯 Objetivo

Implementar e integrar o módulo BESU que está ausente localmente mas presente no pipeline blockchain do TriSLA (BC-NSSMF). O BESU deve:

- Subir BESU localmente (Docker ou containerd)
- Integrar com o BC-NSSMF via RPC (porta 8545/8547)
- Publicar o módulo no GitHub Container Registry (GHCR)
- Versionar junto do Helm Chart TriSLA
- Executar deploy automático no NASP

---

## 📦 Pré-requisitos

### No Ambiente Local (Desenvolvimento)

1. **Docker** instalado e rodando
2. **kubectl** configurado para o cluster NASP
3. **Helm 3.x** instalado
4. **Acesso SSH** ao node1 do cluster NASP
5. **Git** configurado com acesso ao repositório

### No Cluster NASP

1. **Namespace `trisla`** criado
2. **Secret `ghcr-secret`** configurado para pull de imagens do GHCR
3. **StorageClass** disponível para PVCs
4. **Port-forward** ou **Service** configurado para acesso ao BESU

---

## 🚀 Passo 1: Build e Push da Imagem BESU

### 1.1 Build Local (Opcional - para testes)

```bash
cd besu
docker build -t ghcr.io/abelisboa/trisla-besu:3.7.10 .
docker tag ghcr.io/abelisboa/trisla-besu:3.7.10 ghcr.io/abelisboa/trisla-besu:latest
```

### 1.2 Push para GHCR

```bash
# Login no GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u abelisboa --password-stdin

# Push
docker push ghcr.io/abelisboa/trisla-besu:3.7.10
docker push ghcr.io/abelisboa/trisla-besu:latest
```

### 1.3 Via GitHub Actions (Recomendado)

O workflow `.github/workflows/besu-ci.yml` faz o build e push automaticamente quando há mudanças em `besu/**`:

```bash
git add besu/
git commit -m "feat: adicionar módulo BESU integrado ao BC-NSSMF"
git push origin feature/besu-module
```

---

## 🧪 Passo 2: Testes Locais

### 2.1 Iniciar BESU Localmente

```bash
cd besu
./scripts/start_besu.sh
```

### 2.2 Validar BESU

```bash
./scripts/check_besu.sh
```

### 2.3 Testar RPC

```bash
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

**Resposta esperada:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "besu/v23.x.x..."
}
```

### 2.4 Testar Chain ID

```bash
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
```

**Resposta esperada:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x539"  # 1337 em decimal
}
```

---

## ☸️ Passo 3: Deploy no NASP via Helm

### 3.1 Acessar o Cluster NASP

```bash
ssh porvir5g@node1
cd /path/to/trisla-helm-chart
```

### 3.2 Atualizar Imagens (se necessário)

```bash
# Pull da imagem mais recente
docker pull ghcr.io/abelisboa/trisla-besu:3.7.10
```

### 3.3 Validar Helm Chart

```bash
helm lint ./helm/trisla
helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml
```

### 3.4 Aplicar Upgrade

```bash
# Reiniciar pods do BC-NSSMF para forçar reconexão
kubectl -n trisla delete pod -l app.kubernetes.io/component=bc-nssmf

# Deploy/Upgrade do Helm Chart
helm upgrade --install trisla ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --cleanup-on-fail \
  --debug \
  --wait \
  --timeout 10m
```

### 3.5 Validar Deploy

```bash
# Verificar pods
kubectl -n trisla get pods -l app.kubernetes.io/component=besu

# Verificar logs do BESU
kubectl -n trisla logs -l app.kubernetes.io/component=besu --tail=50

# Verificar service
kubectl -n trisla get svc trisla-besu

# Testar RPC via port-forward
kubectl -n trisla port-forward svc/trisla-besu 8545:8545 &
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

---

## ✅ Passo 4: Validação Completa

### 4.1 Verificar Integração BC-NSSMF ↔ BESU

```bash
# Verificar variáveis de ambiente do BC-NSSMF
kubectl -n trisla get deployment trisla-bc-nssmf -o yaml | grep -A 5 "BESU_RPC_URL"

# Deve conter:
# - BESU_RPC_URL: "http://trisla-besu:8545"
# - TRISLA_RPC_URL: "http://trisla-besu:8545"
```

### 4.2 Testar Registro de SLA

```bash
# Via port-forward do BC-NSSMF
kubectl -n trisla port-forward svc/trisla-bc-nssmf 8083:8083 &

# Registrar SLA de teste
curl -X POST http://localhost:8083/bc/register \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "tenant-001",
    "serviceName": "SLA-Test",
    "slaHash": "0x1234567890abcdef",
    "slos": [
      {"name": "latency", "value": 10, "threshold": 20}
    ]
  }'
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "tx": "0x..."
}
```

### 4.3 Verificar Transação no BESU

```bash
# Via port-forward do BESU
kubectl -n trisla port-forward svc/trisla-besu 8545:8545 &

# Consultar último bloco
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["latest",true],"id":1}'
```

---

## 🔧 Troubleshooting

### Problema: BESU não inicia

**Sintomas:**
- Pod em `CrashLoopBackOff`
- Logs mostram erro de genesis.json

**Solução:**
```bash
# Verificar logs
kubectl -n trisla logs -l app.kubernetes.io/component=besu

# Verificar ConfigMap do genesis
kubectl -n trisla get configmap trisla-besu-genesis -o yaml

# Verificar PVC
kubectl -n trisla get pvc trisla-besu-data
```

### Problema: BC-NSSMF não conecta ao BESU

**Sintomas:**
- BC-NSSMF em modo degraded
- Erro "RPC Besu não disponível"

**Solução:**
```bash
# Verificar service do BESU
kubectl -n trisla get svc trisla-besu

# Verificar DNS interno
kubectl -n trisla run -it --rm debug --image=busybox --restart=Never -- nslookup trisla-besu

# Testar conectividade
kubectl -n trisla run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl -X POST http://trisla-besu:8545 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

### Problema: PVC não monta

**Sintomas:**
- Pod em `Pending`
- Eventos mostram "waiting for volume"

**Solução:**
```bash
# Verificar StorageClass
kubectl get storageclass

# Verificar PVC
kubectl -n trisla describe pvc trisla-besu-data

# Se necessário, ajustar values-nasp.yaml:
# besu.persistence.storageClass: "local-path"  # ou outro disponível
```

---

## 📊 Monitoramento

### Métricas do BESU

```bash
# Verificar uso de recursos
kubectl -n trisla top pod -l app.kubernetes.io/component=besu

# Verificar eventos
kubectl -n trisla get events --sort-by='.lastTimestamp' | grep besu
```

### Logs Estruturados

```bash
# Logs em tempo real
kubectl -n trisla logs -f -l app.kubernetes.io/component=besu

# Últimos 100 linhas
kubectl -n trisla logs -l app.kubernetes.io/component=besu --tail=100
```

---

## 🔄 Rollback

Se necessário fazer rollback:

```bash
# Listar releases
helm list -n trisla

# Rollback para versão anterior
helm rollback trisla <revision-number> -n trisla

# Ou remover completamente
helm uninstall trisla -n trisla
```

---

## 📝 Checklist Final

- [ ] Imagem BESU buildada e publicada no GHCR
- [ ] Helm chart validado (`helm lint`)
- [ ] Templates renderizados corretamente (`helm template`)
- [ ] Deploy executado com sucesso
- [ ] Pods do BESU em `Running`
- [ ] Service expondo porta 8545
- [ ] RPC respondendo corretamente
- [ ] BC-NSSMF conectado ao BESU
- [ ] Registro de SLA funcionando
- [ ] Transações aparecendo no blockchain
- [ ] Logs sem erros críticos
- [ ] Recursos (CPU/Memória) dentro dos limites

---

## 🔗 Referências

- **Documentação BESU:** https://besu.hyperledger.org/
- **Helm Chart TriSLA:** `helm/trisla/`
- **BC-NSSMF Guide:** `docs/bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md`
- **NASP Deploy Guide:** `docs/nasp/TRISLA_NASP_DEPLOY_GUIDE.md`

---

*Última atualização: 2025-01-15*
