# Solução Final - Problema BESU

## 🔍 Problema Identificado

O BESU estava falhando com o erro:
```
ERROR | Besu | Failed to start Besu: --network option and --genesis-file option can't be used at the same time.
```

## ✅ Correções Aplicadas

### 1. Removido `--network-id=1337` do docker-compose
O arquivo `besu/docker-compose-besu.yaml` foi corrigido para **NÃO** incluir `--network-id` ou `--network`, usando apenas `--genesis-file`.

### 2. Scripts CRLF corrigidos
Todos os scripts em `besu/scripts/` foram corrigidos para usar LF (Unix).

### 3. Volume de dados limpo
O volume antigo pode conter configurações que causam conflito.

## 🚀 Solução Passo a Passo

### Opção 1: Usar Docker Compose (Recomendado)

```bash
cd besu

# 1. Parar e remover tudo
docker-compose -f docker-compose-besu.yaml down -v
docker volume rm besu_besu-data 2>/dev/null || true

# 2. Corrigir CRLF nos scripts (se necessário)
find scripts -name "*.sh" -exec sed -i 's/\r//g' {} \;

# 3. Iniciar BESU
docker-compose -f docker-compose-besu.yaml up -d

# 4. Aguardar inicialização (30-60 segundos)
sleep 30

# 5. Verificar logs
docker logs trisla-besu-dev --tail 30

# 6. Testar RPC
curl -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

### Opção 2: Usar Docker Diretamente (Alternativa)

Se o docker-compose ainda tiver problemas, use o script de teste direto:

```bash
cd besu
bash test-besu-direct.sh
```

Ou execute manualmente:

```bash
# Parar container existente
docker stop trisla-besu-dev 2>/dev/null || true
docker rm trisla-besu-dev 2>/dev/null || true
docker volume rm besu_besu-data 2>/dev/null || true

# Criar volume
docker volume create besu_besu-data

# Executar BESU
docker run -d \
  --name trisla-besu-dev \
  -p 8545:8545 \
  -p 8546:8546 \
  -p 30303:30303 \
  -v besu_besu-data:/opt/besu/data \
  -v "$(pwd)/genesis.json:/opt/besu/genesis.json:ro" \
  hyperledger/besu:latest \
  --data-path=/opt/besu/data \
  --genesis-file=/opt/besu/genesis.json \
  --rpc-http-enabled=true \
  --rpc-http-host=0.0.0.0 \
  --rpc-http-port=8545 \
  --miner-enabled \
  --miner-coinbase=0x0000000000000000000000000000000000000001 \
  --logging=INFO \
  --rpc-http-enabled=true \
  --rpc-http-host=0.0.0.0 \
  --rpc-http-port=8545 \
  --rpc-ws-enabled=true \
  --rpc-ws-host=0.0.0.0 \
  --rpc-ws-port=8546 \
  --host-allowlist="*" \
  --sync-mode=FULL \
  --rpc-http-api=ETH,NET,WEB3,ADMIN,DEBUG \
  --rpc-http-cors-origins=*

# Aguardar e testar
sleep 30
curl -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

## ✅ Validação

Após iniciar, verifique:

1. **Container rodando:**
   ```bash
   docker ps | grep besu
   ```

2. **Logs sem erro:**
   ```bash
   docker logs trisla-besu-dev --tail 20
   ```
   Não deve aparecer o erro sobre `--network` e `--genesis-file`.

3. **RPC respondendo:**
   ```bash
   curl -X POST http://127.0.0.1:8545 \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
   ```
   Deve retornar JSON com `"result"` contendo a versão do Besu.

4. **Chain ID correto:**
   ```bash
   curl -X POST http://127.0.0.1:8545 \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
   ```
   Deve retornar `"0x539"` (1337 em hex).

## 🔧 Arquivos Corrigidos

- ✅ `besu/docker-compose-besu.yaml` - Removido `--network-id=1337`
- ✅ `besu/genesis.json` - Simplificado (sem IBFT2)
- ✅ `besu/scripts/*.sh` - CRLF corrigido
- ✅ `besu/test-besu-direct.sh` - Script alternativo criado

## ⚠️ Nota Importante

O **Dockerfile** ainda contém `--network=dev` no CMD, mas ele **NÃO** está sendo usado pelo docker-compose (que usa `hyperledger/besu:latest` diretamente). Se você construir uma imagem customizada do Dockerfile, remova a linha `--network=dev` do CMD.

---

*Última atualização: 2025-01-15*

