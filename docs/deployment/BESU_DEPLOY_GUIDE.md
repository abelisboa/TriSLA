# Guia de Deploy do Módulo BESU - TriSLA

**Versão:** 3.7.10  
**Data:** 2025-01-15  
**Módulo:** Hyperledger Besu - Blockchain Client

---

## 📋 Sumário

1. [Visão Geral](#visão-geral)
2. [Pré-requisitos](#pré-requisitos)
3. [Deploy Local (Docker)](#deploy-local-docker)
4. [Deploy no Kubernetes (NASP)](#deploy-no-kubernetes-nasp)
5. [Validação](#validação)
6. [Troubleshooting](#troubleshooting)
7. [Rollback](#rollback)

---

## 🎯 Visão Geral

O módulo BESU fornece a infraestrutura blockchain permissionada necessária para o BC-NSSMF registrar SLAs on-chain. Ele implementa uma blockchain Ethereum permissionada usando Hyperledger Besu.

### Características

- **Blockchain Permissionada**: Hyperledger Besu
- **Chain ID**: 1337
- **Consenso**: IBFT2 (modo dev)
- **RPC Endpoint**: HTTP na porta 8545
- **Persistência**: Volume persistente para dados da blockchain

---

## ✅ Pré-requisitos

### Local (Docker)

- Docker Desktop ou Docker Engine
- Docker Compose (opcional)
- `curl` para testes

### Kubernetes (NASP)

- Cluster Kubernetes acessível
- `kubectl` configurado
- `helm` v3.x instalado
- Acesso ao namespace `trisla`
- StorageClass configurado (para persistência)

---

## 🐳 Deploy Local (Docker)

### 1. Iniciar BESU

```bash
cd besu
./scripts/start_besu.sh
```

O script irá:
- Verificar Docker
- Parar container existente (se houver)
- Iniciar BESU via docker-compose
- Aguardar inicialização (30s)
- Validar RPC HTTP

### 2. Verificar Status

```bash
./scripts/check_besu.sh
```

Saída esperada:
```
✅ [TriSLA] Container BESU está rodando
✅ [TriSLA] RPC OK - Versão: besu/v23.x.x/...
📋 [TriSLA] Chain ID: 0x539
💰 [TriSLA] Saldo conta padrão: 0xffffffffffffffffffffffffffffffffffffffff (...)
✅ [TriSLA] BESU está operacional!
```

### 3. Validar Integração com BC-NSSMF

```bash
./scripts/validate_besu.sh
```

### 4. Parar BESU

```bash
docker stop trisla-besu-dev
docker rm trisla-besu-dev
```

---

## ☸️ Deploy no Kubernetes (NASP)

### 1. Preparar Valores

O arquivo `helm/trisla/values-nasp.yaml` já contém a configuração do BESU:

```yaml
besu:
  enabled: true
  image:
    repository: hyperledger/besu
    tag: latest
  persistence:
    enabled: true
    size: 20Gi
```

### 2. Atualizar Imagens (se necessário)

```bash
# Se usar imagem customizada do GHCR
docker pull ghcr.io/abelisboa/trisla-besu:3.7.10
```

### 3. Acessar Cluster NASP

```bash
ssh porvir5g@node1
```

### 4. Aplicar Upgrade do Helm Chart

```bash
cd /path/to/TriSLA-clean

# Validar chart
helm lint helm/trisla
helm template trisla helm/trisla -f helm/trisla/values-nasp.yaml --debug

# Aplicar upgrade
helm upgrade --install trisla ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --cleanup-on-fail \
  --debug \
  --wait \
  --timeout 10m
```

### 5. Verificar Deploy

```bash
# Verificar pods
kubectl -n trisla get pods -l app.kubernetes.io/component=besu

# Verificar serviço
kubectl -n trisla get svc -l app.kubernetes.io/component=besu

# Ver logs
kubectl -n trisla logs -f deployment/trisla-besu

# Verificar PVC
kubectl -n trisla get pvc -l app.kubernetes.io/component=besu
```

### 6. Testar RPC

```bash
# Port-forward
kubectl -n trisla port-forward svc/trisla-besu 8545:8545

# Em outro terminal, testar RPC
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

Resposta esperada:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "besu/v23.x.x/linux-x86_64/openjdk-java-17"
}
```

---

## ✅ Validação

### 1. Verificar BESU

```bash
# Local
./besu/scripts/check_besu.sh

# Kubernetes
kubectl -n trisla exec -it deployment/trisla-besu -- \
  curl -X POST http://localhost:8545 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

### 2. Verificar BC-NSSMF

```bash
# Health check
curl http://localhost:8083/health

# Deve retornar:
# {
#   "status": "healthy",
#   "rpc_connected": true,
#   "enabled": true
# }
```

### 3. Testar Registro de SLA

```bash
curl -X POST http://localhost:8083/bc/register \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "test-tenant",
    "serviceName": "test-sla",
    "slaHash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
    "slos": [
      {"name": "latency", "value": 10, "threshold": 20}
    ]
  }'
```

Resposta esperada:
```json
{
  "status": "ok",
  "tx": "0x5678...efgh"
}
```

---

## 🛠️ Troubleshooting

### Problema: BESU não inicia

**Sintomas:**
- Container para imediatamente
- Logs mostram erro de genesis.json

**Solução:**
```bash
# Verificar genesis.json
cat besu/genesis.json | jq .

# Verificar logs
docker logs trisla-besu-dev
# ou
kubectl -n trisla logs deployment/trisla-besu
```

### Problema: BC-NSSMF não conecta ao BESU

**Sintomas:**
- BC-NSSMF retorna `"rpc_connected": false`
- Erro: "BC-NSSMF está em modo degraded"

**Solução:**
1. Verificar se BESU está rodando:
   ```bash
   kubectl -n trisla get pods -l app.kubernetes.io/component=besu
   ```

2. Verificar variáveis de ambiente do BC-NSSMF:
   ```bash
   kubectl -n trisla get deployment trisla-bc-nssmf -o yaml | grep -A 20 env
   ```

3. Testar conectividade:
   ```bash
   kubectl -n trisla exec -it deployment/trisla-bc-nssmf -- \
     curl -X POST http://trisla-besu:8545 \
       -H "Content-Type: application/json" \
       -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
   ```

4. Verificar serviço:
   ```bash
   kubectl -n trisla get svc trisla-besu
   kubectl -n trisla describe svc trisla-besu
   ```

### Problema: PVC não é criado

**Sintomas:**
- Pod fica em `Pending`
- Evento: "no persistent volumes available"

**Solução:**
1. Verificar StorageClass:
   ```bash
   kubectl get storageclass
   ```

2. Ajustar `values-nasp.yaml`:
   ```yaml
   besu:
     persistence:
       storageClass: "nome-do-storageclass"
   ```

3. Ou desabilitar persistência (não recomendado para produção):
   ```yaml
   besu:
     persistence:
       enabled: false
   ```

---

## 🔄 Rollback

### Rollback do Helm

```bash
# Ver histórico
helm history trisla -n trisla

# Rollback para versão anterior
helm rollback trisla <revision-number> -n trisla

# Rollback para última versão estável
helm rollback trisla -n trisla
```

### Rollback Manual

```bash
# Parar BESU
kubectl -n trisla scale deployment trisla-besu --replicas=0

# Remover recursos
kubectl -n trisla delete deployment trisla-besu
kubectl -n trisla delete svc trisla-besu
kubectl -n trisla delete configmap trisla-besu-genesis
kubectl -n trisla delete pvc trisla-besu-data  # CUIDADO: apaga dados!
```

---

## 📊 Monitoramento

### Métricas

O BESU expõe métricas via RPC:

```bash
# Block number
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# Peer count
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"net_peerCount","params":[],"id":1}'
```

### Logs Estruturados

Os logs do BESU incluem:
- Inicialização da blockchain
- Criação de blocos
- Conexões RPC
- Erros e warnings

---

## 📚 Referências

- [Hyperledger Besu Documentation](https://besu.hyperledger.org/)
- [TriSLA BC-NSSMF Guide](../bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md)
- [Helm Chart Documentation](../../helm/trisla/README.md)

---

*Última atualização: 2025-01-15*
