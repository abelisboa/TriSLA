# BESU Local - TriSLA

Este diretório contém os arquivos necessários para construir e testar a imagem Docker oficial do BESU da TriSLA.

## Estrutura

- `Dockerfile`: Definição da imagem Docker do BESU
- `genesis.json`: Configuração inicial da blockchain privada
- `README_BESU_LOCAL.md`: Este arquivo

## Build e Teste

Siga as instruções abaixo para construir e testar a imagem localmente.

### FASE 3 - Build Manual

```bash
docker build -t trisla-besu:local ./besu
docker images | grep trisla-besu
```

### FASE 4 - Teste Manual

```bash
docker run -d --name besu-test \
  -p 8545:8545 \
  -p 8546:8546 \
  trisla-besu:local
```

**Teste RPC:**
```bash
curl -s -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"net_version","params":[],"id":1}'
```

**Esperado:** `"result": "1337"`

**Limpeza após teste:**
```bash
docker stop besu-test && docker rm besu-test
```

### FASE 5 - Publicação no GHCR

```bash
docker tag trisla-besu:local ghcr.io/abelisboa/trisla-besu:v3.7.10
docker push ghcr.io/abelisboa/trisla-besu:v3.7.10
```

**Nota:** Requer autenticação no GHCR:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u abelisboa --password-stdin
```

