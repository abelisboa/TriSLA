# Troubleshooting BESU - TriSLA

## 🔍 Problema: RPC não responde após iniciar o container

### Diagnóstico

Se o BESU não está respondendo no RPC (porta 8545), siga estes passos:

### 1. Verificar Logs do Container

```bash
docker logs trisla-besu-dev --tail 50
```

**Problemas comuns:**
- Erro de genesis.json inválido
- Erro de consenso (IBFT2 sem validadores)
- Porta já em uso
- Problemas de permissão no volume

### 2. Verificar Status do Container

```bash
docker ps -a | grep besu
docker inspect trisla-besu-dev --format '{{.State.Status}}'
```

### 3. Testar RPC Dentro do Container

```bash
docker exec trisla-besu-dev curl -s -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

Se funcionar dentro do container mas não externamente, o problema é no mapeamento de portas.

### 4. Verificar Portas

```bash
# Verificar portas do container
docker port trisla-besu-dev

# Verificar se a porta está em uso
netstat -tlnp | grep 8545
# ou
ss -tlnp | grep 8545
```

### 5. Usar Script de Diagnóstico

```bash
cd besu
./scripts/diagnose_besu.sh
```

## 🔧 Soluções Comuns

### Problema: Genesis.json com IBFT2 sem validadores

**Solução:** O `genesis.json` foi atualizado para usar consenso simples (sem IBFT2) para desenvolvimento local.

Se precisar usar IBFT2, gere o `extraData` corretamente:

```bash
# Criar arquivo validators.json
echo '["0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1"]' > validators.json

# Gerar extraData
docker run --rm hyperledger/besu:latest rlp encode --from=validators.json
```

### Problema: Container inicia mas RPC não responde

**Possíveis causas:**
1. BESU ainda está sincronizando (aguarde mais tempo)
2. Genesis.json inválido
3. Problema com volume de dados

**Solução:**
```bash
# Parar e remover tudo
docker-compose -f docker-compose-besu.yaml down
docker volume rm besu_besu-data

# Reiniciar
docker-compose -f docker-compose-besu.yaml up -d

# Aguardar 30-60 segundos e testar
sleep 30
curl -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

### Problema: Porta 8545 já em uso

**Solução:**
```bash
# Encontrar processo usando a porta
lsof -i :8545
# ou
netstat -tlnp | grep 8545

# Parar o processo ou mudar a porta no docker-compose-besu.yaml
```

### Problema: Erro de permissão no volume

**Solução:**
```bash
# Remover volume e recriar
docker volume rm besu_besu-data
docker-compose -f docker-compose-besu.yaml up -d
```

## 📋 Configuração Atual

### Genesis.json
- **Chain ID:** 1337
- **Consenso:** Proof of Work simples (sem IBFT2/Clique)
- **Conta pré-financiada:** `0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1`

### Docker Compose
- **RPC HTTP:** 8545
- **RPC WS:** 8546
- **P2P:** 30303
- **Miner:** Habilitado (FAST strategy)

## ✅ Validação Final

Após corrigir, valide:

```bash
# 1. Container rodando
docker ps | grep besu

# 2. RPC respondendo
curl -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'

# 3. Chain ID correto
curl -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
# Deve retornar: "0x539" (1337 em hex)
```

## 🆘 Ainda com problemas?

1. Execute o diagnóstico completo:
   ```bash
   cd besu && ./scripts/diagnose_besu.sh
   ```

2. Verifique os logs completos:
   ```bash
   docker logs trisla-besu-dev
   ```

3. Reinicie do zero:
   ```bash
   docker-compose -f docker-compose-besu.yaml down
   docker volume rm besu_besu-data
   docker-compose -f docker-compose-besu.yaml up -d
   ```

---

*Última atualização: 2025-01-15*

