# Instruções para Testar BESU

## ✅ Status Atual

O BESU foi iniciado com sucesso! O container está rodando, mas o RPC pode levar **60-90 segundos** para ficar completamente disponível após a inicialização.

## 🧪 Teste Manual

### 1. Verificar se o container está rodando

```bash
docker ps | grep besu
```

Deve mostrar o container `trisla-besu-dev` com status "Up".

### 2. Verificar logs (sem erros)

```bash
docker logs trisla-besu-dev --tail 30
```

**Não deve aparecer:**
- ❌ `ERROR | Besu | Failed to start Besu: --network option and --genesis-file option can't be used at the same time.`

**Deve aparecer:**
- ✅ `INFO | Besu | Starting Besu`
- ✅ `INFO | Besu | P2P started`
- ✅ `INFO | Besu | RPC HTTP service started`

### 3. Aguardar e testar RPC (aguarde 60-90 segundos após iniciar)

```bash
# Aguardar mais tempo
sleep 60

# Testar RPC
curl -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

**Resposta esperada:**
```json
{"jsonrpc":"2.0","id":1,"result":"besu/v23.x.x/linux-x86_64/openjdk-java-17"}
```

### 4. Usar script automatizado

```bash
cd besu
bash scripts/wait-and-test-besu.sh
```

Este script aguarda até 100 segundos (20 tentativas x 5 segundos) e testa automaticamente.

## 🔍 Diagnóstico

Se o RPC ainda não responder após 90 segundos:

### Verificar se a porta está escutando

```bash
# Dentro do container
docker exec trisla-besu-dev netstat -tlnp | grep 8545
# ou
docker exec trisla-besu-dev ss -tlnp | grep 8545
```

### Testar RPC dentro do container

```bash
docker exec trisla-besu-dev curl -s -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

Se funcionar dentro do container mas não externamente, o problema é no mapeamento de portas.

### Verificar mapeamento de portas

```bash
docker port trisla-besu-dev
```

Deve mostrar:
```
8545/tcp -> 0.0.0.0:8545
8546/tcp -> 0.0.0.0:8546
30303/tcp -> 0.0.0.0:30303
```

## ⏱️ Tempo de Inicialização

O BESU normalmente leva:
- **30-60 segundos** para iniciar completamente
- **60-90 segundos** para o RPC ficar totalmente disponível
- **90-120 segundos** para sincronizar completamente (se houver dados)

## ✅ Validação Completa

Após o RPC responder, teste também:

```bash
# 1. Chain ID
curl -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
# Deve retornar: "0x539" (1337 em hex)

# 2. Block Number
curl -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
# Deve retornar um número de bloco (ex: "0x0" ou maior)
```

## 🆘 Se Ainda Não Funcionar

1. **Reiniciar do zero:**
   ```bash
   cd besu
   docker-compose -f docker-compose-besu.yaml down -v
   docker volume rm besu_besu-data 2>/dev/null || true
   docker-compose -f docker-compose-besu.yaml up -d
   bash scripts/wait-and-test-besu.sh
   ```

2. **Usar script alternativo:**
   ```bash
   cd besu
   bash test-besu-direct.sh
   ```

3. **Verificar logs completos:**
   ```bash
   docker logs trisla-besu-dev
   ```

---

*Última atualização: 2025-01-15*

