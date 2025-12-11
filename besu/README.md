# Módulo BESU - TriSLA

Hyperledger Besu - Blockchain client para TriSLA BC-NSSMF

## 📋 Descrição

O módulo BESU fornece a infraestrutura blockchain permissionada para o BC-NSSMF registrar SLAs on-chain. Este módulo implementa um nó Ethereum permissionado usando Hyperledger Besu.

## 🏗️ Arquitetura

```
BC-NSSMF → BESU RPC (8545) → Blockchain Permissionada (Chain ID: 1337)
```

## 🚀 Início Rápido

### Local (Docker Compose)

```bash
cd besu
./scripts/start_besu.sh
```

### Verificar Status

```bash
./scripts/check_besu.sh
```

### Validar Integração

```bash
./scripts/validate_besu.sh
```

## 📦 Estrutura

```
besu/
├── Dockerfile              # Imagem Docker otimizada
├── genesis.json            # Configuração da blockchain (Chain ID: 1337)
├── docker-compose-besu.yaml
├── scripts/
│   ├── start_besu.sh      # Iniciar BESU localmente
│   ├── check_besu.sh      # Verificar status
│   └── validate_besu.sh   # Validar integração BC-NSSMF
└── README.md
```

## ⚙️ Configuração

### Portas

- **8545**: RPC HTTP (JSON-RPC)
- **8546**: RPC WebSocket
- **30303**: P2P (peer-to-peer)

### Chain ID

- **1337**: Chain ID padrão para desenvolvimento

### Conta Padrão

- **Endereço**: `0x90f8bf6a479f320ead074411a4b0e7944ea8c9c1`
- **Saldo**: Pré-financiado no genesis

## 🔧 Kubernetes/Helm

### Instalar via Helm

```bash
helm upgrade --install trisla ./helm/trisla \
  -n trisla \
  -f ./helm/trisla/values-nasp.yaml \
  --set besu.enabled=true
```

### Verificar Deploy

```bash
kubectl -n trisla get pods -l app.kubernetes.io/component=besu
kubectl -n trisla logs -l app.kubernetes.io/component=besu
```

### Testar RPC

```bash
kubectl -n trisla port-forward svc/trisla-besu 8545:8545
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

## 🔗 Integração com BC-NSSMF

O BC-NSSMF se conecta ao BESU via variáveis de ambiente:

```yaml
env:
  - name: TRISLA_RPC_URL
    value: "http://trisla-besu:8545"
  - name: BESU_RPC_URL
    value: "http://trisla-besu:8545"
  - name: BC_ENABLED
    value: "true"
  - name: TRISLA_CHAIN_ID
    value: "1337"
```

## 📊 Healthcheck

O BESU expõe healthcheck via JSON-RPC:

```bash
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"web3_clientVersion","id":1}'
```

## 🔒 Segurança

⚠️ **ATENÇÃO**: Esta configuração é para desenvolvimento. Em produção:

1. Habilitar autenticação RPC
2. Configurar CORS restritivo
3. Usar TLS para RPC
4. Configurar firewall para P2P
5. Usar chaves privadas seguras

## 📝 Logs

```bash
# Docker
docker logs -f trisla-besu-dev

# Kubernetes
kubectl -n trisla logs -f -l app.kubernetes.io/component=besu
```

## 🐛 Troubleshooting

### BESU não inicia

1. Verificar portas disponíveis: `netstat -tuln | grep 8545`
2. Verificar logs: `docker logs trisla-besu-dev`
3. Verificar genesis.json: `cat besu/genesis.json | jq`

### BC-NSSMF não conecta

1. Verificar serviço: `kubectl -n trisla get svc trisla-besu`
2. Verificar variáveis de ambiente do BC-NSSMF
3. Testar RPC manualmente: `curl -X POST http://trisla-besu:8545 ...`

## 📚 Referências

- [Hyperledger Besu Documentation](https://besu.hyperledger.org/)
- [TriSLA BC-NSSMF Guide](../docs/bc-nssmf/BC_NSSMF_COMPLETE_GUIDE.md)
