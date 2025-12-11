# Correções Aplicadas ao Módulo BESU

## 📋 Resumo

Correções aplicadas para resolver problemas de inicialização do BESU e scripts com CRLF.

## ✅ Problemas Corrigidos

### 1. Erro CRLF nos Scripts
**Problema:** Scripts tinham terminações de linha Windows (CRLF) causando erro `'bash\r': No such file or directory`

**Solução:**
```bash
find besu/scripts -name "*.sh" -exec sed -i 's/\r//g' {} \;
```

**Scripts corrigidos:**
- ✅ `besu/scripts/start_besu.sh`
- ✅ `besu/scripts/check_besu.sh`
- ✅ `besu/scripts/validate_besu.sh`
- ✅ `besu/scripts/diagnose_besu.sh`

### 2. Conflito de Opções no BESU
**Problema:** BESU falhava com erro:
```
ERROR | Besu | Failed to start Besu: --network option and --genesis-file option can't be used at the same time.
```

**Causa:** O `docker-compose-besu.yaml` tinha `--network=dev` (implícito) e `--genesis-file` ao mesmo tempo.

**Solução:** Removida a opção `--network-id=1337` do comando, mantendo apenas `--genesis-file`.

**Arquivo modificado:**
- ✅ `besu/docker-compose-besu.yaml`

### 3. Configuração do Genesis.json
**Problema:** Genesis.json estava configurado para IBFT2 sem validadores.

**Solução:** Simplificado para usar consenso Proof of Work simples (sem IBFT2/Clique) para desenvolvimento local.

**Arquivo modificado:**
- ✅ `besu/genesis.json`

## 🔧 Configuração Final

### docker-compose-besu.yaml
```yaml
command:
  - --data-path=/opt/besu/data
  - --genesis-file=/opt/besu/genesis.json
  - --rpc-http-enabled=true
  - --rpc-http-host=0.0.0.0
  - --rpc-http-port=8545
  - --miner-enabled
  - --miner-coinbase=0x0000000000000000000000000000000000000001
  - --logging=INFO
  - --rpc-http-enabled=true
  - --rpc-http-host=0.0.0.0
  - --rpc-http-port=8545
  - --rpc-ws-enabled=true
  - --rpc-ws-host=0.0.0.0
  - --rpc-ws-port=8546
  - --host-allowlist="*"
  - --sync-mode=FULL
  - --rpc-http-api=ETH,NET,WEB3,ADMIN,DEBUG
  - --rpc-http-cors-origins=*
```

**Nota:** Removido `--network-id=1337` pois não pode ser usado com `--genesis-file`.

### genesis.json
- **Chain ID:** 1337 (definido no config)
- **Consenso:** Proof of Work simples
- **Conta pré-financiada:** `0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1`

## 🧪 Validação

Após as correções, valide:

```bash
# 1. Corrigir CRLF (se necessário)
find besu/scripts -name "*.sh" -exec sed -i 's/\r//g' {} \;

# 2. Reiniciar BESU
cd besu
docker-compose -f docker-compose-besu.yaml down
docker volume rm besu_besu-data
docker-compose -f docker-compose-besu.yaml up -d

# 3. Aguardar inicialização (30-60 segundos)
sleep 30

# 4. Testar RPC
curl -X POST http://127.0.0.1:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'

# 5. Executar diagnóstico
./scripts/diagnose_besu.sh
```

## 📝 Arquivos Modificados

1. ✅ `besu/docker-compose-besu.yaml` - Removido `--network-id=1337`
2. ✅ `besu/genesis.json` - Simplificado (sem IBFT2)
3. ✅ `besu/scripts/*.sh` - CRLF corrigido
4. ✅ `besu/scripts/diagnose_besu.sh` - Novo script de diagnóstico
5. ✅ `besu/TROUBLESHOOTING.md` - Guia de troubleshooting

## 🚀 Próximos Passos

1. **Testar BESU:**
   ```bash
   cd besu
   ./scripts/start_besu.sh
   ./scripts/check_besu.sh
   ```

2. **Validar integração com BC-NSSMF:**
   ```bash
   ./scripts/validate_besu.sh
   ```

3. **Se ainda houver problemas:**
   ```bash
   ./scripts/diagnose_besu.sh
   docker logs trisla-besu-dev
   ```

## ⚠️ Notas Importantes

- **PoW Deprecated:** O BESU mostra aviso de que PoW está deprecated, mas funciona para desenvolvimento local
- **IBFT2:** Se precisar usar IBFT2 em produção, gere o `extraData` corretamente com validadores
- **Network ID:** Não use `--network` ou `--network-id` quando usar `--genesis-file`

---

*Última atualização: 2025-01-15*

