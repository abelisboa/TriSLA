# PROMPT S3 — BC-NSSMF (NASP)

## Contexto

Este prompt orienta a execução NASP do Sprint 3 (BC-NSSMF) da arquitetura TriSLA. Todas as operações são executadas no ambiente experimental NASP via acesso SSH ao node006.

**Pré-requisito obrigatório:** PROMPT_S3_LOCAL.md deve ter sido executado com sucesso.

**Ambiente NASP:**
- **SSH Host:** `node006`
- **Diretório de deploy:** `/home/porvir5g/gtp5g/trisla`
- **Namespace:** `trisla`
- **Helm Chart:** `helm/trisla/`

---

## Objetivo

Implantar, validar e coletar evidências experimentais do módulo **BC-NSSMF** no ambiente NASP, garantindo:

1. **Deploy via Helm** no cluster Kubernetes do NASP
2. **Validação de rollout** (pods em Running)
3. **Deploy do Smart Contract** na rede Besu
4. **Validação de transações on-chain** (criar SLA, ativar, reportar violação)
5. **Validação de eventos on-chain** (SlaCreated, SlaActivated, etc.)
6. **Validação de integração** com Decision Engine
7. **Coleta de evidências** (logs, métricas, tx hashes, eventos)
8. **Registro de evidências** na documentação técnica

---

## Pré-condições

1. ✅ Sprint 3 LOCAL concluído com sucesso
2. ✅ Imagem publicada no GHCR: `ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.11` (versão canônica)
3. ✅ Acesso SSH ao node006 do NASP
4. ✅ kubectl configurado e conectado ao cluster NASP
5. ✅ Helm 3.12+ instalado no node006
6. ✅ Namespace `trisla` criado no cluster
7. ✅ Secret `ghcr-secret` configurado no namespace
8. ✅ **Besu deployado e funcional** no cluster (pré-requisito crítico)

---

## Escopo NASP

### Incluído
- Deploy via Helm no cluster NASP
- Verificação de rollout e saúde dos pods
- Deploy do Smart Contract na rede Besu
- Testes funcionais (REST API de blockchain)
- Validação de transações on-chain
- Validação de eventos on-chain
- Validação de integração com Decision Engine
- Coleta de logs, métricas, tx hashes e eventos
- Evidências experimentais para documentação

### Excluído
- Modificações no código fonte
- Build de imagens
- Push para registry
- Alterações no Helm chart (apenas deploy)

---

## Paths e Artefatos NASP

| Artefato | Path NASP |
|----------|-----------|
| **Diretório de deploy** | `/home/porvir5g/gtp5g/trisla` |
| **Helm chart** | `/home/porvir5g/gtp5g/trisla/helm/trisla/` |
| **Logs coletados** | `/home/porvir5g/gtp5g/trisla/logs/` |
| **Evidências** | Documentar em `docs/technical/03_BC_NSSMF.md` |

---

## Passos Numerados

### 1. Conexão SSH ao NASP

```bash
# Conectar ao node006
ssh node006

# Verificar diretório de trabalho
cd /home/porvir5g/gtp5g/trisla
pwd
```

### 2. Verificação do Ambiente NASP

```bash
# Verificar kubectl conectado
kubectl cluster-info
kubectl get nodes

# Verificar namespace trisla
kubectl get namespace trisla

# Verificar secret do GHCR
kubectl get secret ghcr-secret -n trisla
```

### 3. Verificação do Besu (Pré-requisito Crítico)

```bash
# Verificar se Besu está deployado e rodando
kubectl get pods -n trisla -l app=besu

# Verificar service do Besu
kubectl get svc -n trisla -l app=besu

# Verificar RPC endpoint do Besu
BESU_SVC=$(kubectl get svc -n trisla -l app=besu -o jsonpath='{.items[0].metadata.name}')
BESU_RPC_URL="http://${BESU_SVC}.trisla.svc.cluster.local:8545"

echo "Besu RPC URL: $BESU_RPC_URL"

# Testar conectividade com Besu (via port-forward)
BESU_POD=$(kubectl get pods -n trisla -l app=besu -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward -n trisla $BESU_POD 8545:8545 &
BESU_PORT_FORWARD_PID=$!
sleep 3

# Testar RPC do Besu
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

kill $BESU_PORT_FORWARD_PID
```

### 4. Verificação da Imagem no GHCR

```bash
# Verificar que a imagem existe e está acessível
kubectl run test-image-pull --image=ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.11 --rm -it --restart=Never --namespace=trisla --command -- echo "Image pull test"
```

### 5. Atualização do Helm Chart (se necessário)

```bash
# Navegar para o chart
cd /home/porvir5g/gtp5g/trisla/helm/trisla

# Verificar values.yaml
cat values.yaml | grep -A 15 "bcNssmf:"

# Confirmar que a tag está correta:
#   image:
#     repository: trisla-bc-nssmf
#     tag: v3.7.11  # Versão canônica padronizada no PASSO 0
# Verificar que TRISLA_RPC_URL será injetado automaticamente

# Validar chart
helm lint .
```

### 6. Deploy via Helm

```bash
# Deploy ou upgrade do BC-NSSMF
helm upgrade --install trisla . \
  --namespace trisla \
  --set bcNssmf.enabled=true \
  --set bcNssmf.image.tag=v3.7.11 \
  --set besu.enabled=true \
  --wait \
  --timeout 5m

# Verificar status do release
helm list -n trisla
helm status trisla -n trisla
```

### 7. Verificação de Rollout

```bash
# Verificar pods do BC-NSSMF
kubectl get pods -n trisla -l app=bc-nssmf

# Verificar status detalhado
kubectl describe pod -n trisla -l app=bc-nssmf

# Verificar logs iniciais
kubectl logs -n trisla -l app=bc-nssmf --tail=100

# Aguardar pods em Running (máximo 2 replicas)
kubectl wait --for=condition=ready pod -l app=bc-nssmf -n trisla --timeout=300s
```

### 8. Verificação de Serviços

```bash
# Verificar service
kubectl get svc -n trisla -l app=bc-nssmf

# Verificar endpoints
kubectl get endpoints -n trisla -l app=bc-nssmf

# Verificar porta exposta (8083)
kubectl get svc -n trisla -l app=bc-nssmf -o jsonpath='{.items[0].spec.ports[*].port}'
```

### 9. Validação de Conexão com Besu

```bash
# Obter nome do pod
POD_NAME=$(kubectl get pods -n trisla -l app=bc-nssmf -o jsonpath='{.items[0].metadata.name}')

# Verificar variáveis de ambiente (TRISLA_RPC_URL)
kubectl exec -n trisla $POD_NAME -- env | grep -i "rpc\|besu"

# Verificar conectividade com Besu
kubectl exec -n trisla $POD_NAME -- nslookup trisla-besu.trisla.svc.cluster.local

# Verificar logs de conexão
kubectl logs -n trisla $POD_NAME | grep -i "besu\|rpc\|connection\|blockchain"
```

### 10. Deploy do Smart Contract

```bash
# Port-forward para acesso local
kubectl port-forward -n trisla $POD_NAME 8083:8083 &
PORT_FORWARD_PID=$!
sleep 3

# Verificar se o contrato já foi deployado (consultar contract_address.json)
# Se não, fazer deploy via API ou script interno
curl -X POST http://localhost:8083/api/v1/contract/deploy \
  -H "Content-Type: application/json" \
  -d '{}' | jq .

# Verificar resposta contém:
# - contract_address
# - tx_hash
# - block_number

# Salvar endereço do contrato
CONTRACT_ADDRESS=$(curl -s -X POST http://localhost:8083/api/v1/contract/deploy -H "Content-Type: application/json" -d '{}' | jq -r '.contract_address')
echo "Contract Address: $CONTRACT_ADDRESS"
```

### 11. Testes Funcionais REST API

```bash
# Teste de health check
curl -v http://localhost:8083/health

# Teste de criar SLA
CREATE_RESPONSE=$(curl -s -X POST http://localhost:8083/api/v1/sla/create \
  -H "Content-Type: application/json" \
  -d '{
    "sla_id": "test-sla-001",
    "customer": "test-customer",
    "service_name": "test-service",
    "slos": [
      {"name": "latency", "value": 10, "threshold": 5},
      {"name": "throughput", "value": 1000, "threshold": 800}
    ]
  }' | jq .)

echo "$CREATE_RESPONSE"
# Verificar resposta contém:
# - sla_id
# - tx_hash
# - contract_address
# - status

# Salvar tx_hash
TX_HASH=$(echo "$CREATE_RESPONSE" | jq -r '.tx_hash')
echo "Transaction Hash: $TX_HASH"

# Teste de ativar SLA
curl -X POST http://localhost:8083/api/v1/sla/activate \
  -H "Content-Type: application/json" \
  -d "{\"sla_id\": \"test-sla-001\"}" | jq .

# Teste de consultar status
curl -s http://localhost:8083/api/v1/sla/status/test-sla-001 | jq .
```

### 12. Validação de Transações On-Chain

```bash
# Verificar transação no Besu (via RPC)
BESU_POD=$(kubectl get pods -n trisla -l app=besu -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward -n trisla $BESU_POD 8545:8545 &
BESU_PORT_FORWARD_PID=$!
sleep 3

# Consultar transação
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getTransactionByHash\",\"params\":[\"$TX_HASH\"],\"id\":1}" | jq .

# Consultar receipt da transação
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getTransactionReceipt\",\"params\":[\"$TX_HASH\"],\"id\":1}" | jq .

kill $BESU_PORT_FORWARD_PID
```

### 13. Validação de Eventos On-Chain

```bash
# Consultar eventos do contrato
curl -X POST http://localhost:8083/api/v1/sla/events/test-sla-001 | jq .

# Verificar logs do contrato (eventos emitidos)
kubectl logs -n trisla $POD_NAME | grep -i "event\|SlaCreated\|SlaActivated"

# Consultar eventos via RPC do Besu
kubectl port-forward -n trisla $BESU_POD 8545:8545 &
BESU_PORT_FORWARD_PID=$!
sleep 3

# Filtrar eventos (ajustar endereço do contrato)
curl -X POST http://localhost:8545 \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"method\":\"eth_getLogs\",\"params\":[{\"address\":\"$CONTRACT_ADDRESS\",\"fromBlock\":\"latest\",\"toBlock\":\"latest\"}],\"id\":1}" | jq .

kill $BESU_PORT_FORWARD_PID
```

### 14. Teste de Violação de SLA

```bash
# Reportar violação de SLA
VIOLATION_RESPONSE=$(curl -s -X POST http://localhost:8083/api/v1/sla/violation \
  -H "Content-Type: application/json" \
  -d '{
    "sla_id": "test-sla-001",
    "slo_name": "latency",
    "actual_value": 15,
    "threshold": 5
  }' | jq .)

echo "$VIOLATION_RESPONSE"
# Verificar resposta contém:
# - sla_id
# - tx_hash
# - status (VIOLATED)

# Verificar evento de violação
curl -X POST http://localhost:8083/api/v1/sla/events/test-sla-001 | jq . | grep -i "violation"
```

### 15. Validação de Integração com Decision Engine

```bash
# Verificar se Decision Engine está deployado
kubectl get pods -n trisla -l app=decision-engine

# Verificar conectividade entre serviços
kubectl exec -n trisla $POD_NAME -- nslookup trisla-decision-engine.trisla.svc.cluster.local

# Verificar logs de tentativas de comunicação
kubectl logs -n trisla $POD_NAME | grep -i "decision\|grpc\|connection"
```

### 16. Coleta de Logs

```bash
# Criar diretório de logs (se não existir)
mkdir -p /home/porvir5g/gtp5g/trisla/logs

# Coletar logs completos
kubectl logs -n trisla -l app=bc-nssmf --tail=1000 > /home/porvir5g/gtp5g/trisla/logs/bc-nssmf-logs-$(date +%Y%m%d-%H%M%S).log

# Coletar logs de eventos
kubectl get events -n trisla --sort-by='.lastTimestamp' | grep bc-nssmf > /home/porvir5g/gtp5g/trisla/logs/bc-nssmf-events-$(date +%Y%m%d-%H%M%S).log
```

### 17. Coleta de Métricas

```bash
# Verificar métricas Prometheus expostas
kubectl exec -n trisla $POD_NAME -- wget -qO- http://localhost:8083/metrics | grep -i "trisla_bc"

# Coletar métricas via Prometheus (se disponível)
PROMETHEUS_POD=$(kubectl get pods -n monitoring -l app=prometheus -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || kubectl get pods -n trisla -l app=prometheus -o jsonpath='{.items[0].metadata.name}')

if [ ! -z "$PROMETHEUS_POD" ]; then
  kubectl port-forward -n monitoring $PROMETHEUS_POD 9090:9090 &
  PROM_PORT_FORWARD_PID=$!
  sleep 3
  
  # Query de métricas do BC-NSSMF
  curl "http://localhost:9090/api/v1/query?query=trisla_bc_nssmf_transactions_total" > /home/porvir5g/gtp5g/trisla/logs/bc-nssmf-metrics-$(date +%Y%m%d-%H%M%S).json
  
  kill $PROM_PORT_FORWARD_PID
fi
```

### 18. Registro de Evidências

```bash
# Documentar evidências em docs/technical/03_BC_NSSMF.md
# Incluir:
# - Versão da imagem deployada
# - Status dos pods
# - Endereço do contrato deployado
# - Tx hash de deploy
# - Tx hashes de transações de teste
# - Eventos on-chain capturados
# - Resultados dos testes funcionais
# - Métricas coletadas
# - Evidência de integração com Decision Engine
# - Screenshots ou outputs de comandos
```

### 19. Validação de SLOs (se aplicável)

```bash
# Verificar SLOs definidos para BC-NSSMF
# Consultar docs/technical/06_OBSERVABILITY_SLO.md

# Verificar métricas de latência de transação
# Verificar taxa de erro
# Verificar disponibilidade
```

---

## Evidências Obrigatórias

### Checklist de Conclusão NASP

- [ ] Deploy via Helm executado com sucesso
- [ ] Pods do BC-NSSMF em estado Running (2 replicas)
- [ ] Besu deployado e acessível
- [ ] Conexão com Besu validada
- [ ] Smart Contract deployado na rede Besu
- [ ] Endereço do contrato registrado
- [ ] Service criado e endpoints funcionais
- [ ] Health check respondendo (HTTP 200)
- [ ] REST API funcional (criar, ativar, consultar SLA)
- [ ] Transações on-chain validadas (tx hashes confirmados)
- [ ] Eventos on-chain capturados (SlaCreated, SlaActivated, etc.)
- [ ] Teste de violação de SLA executado
- [ ] Integração com Decision Engine validada
- [ ] Logs coletados e salvos
- [ ] Métricas Prometheus expostas e coletadas
- [ ] Evidências documentadas em `docs/technical/03_BC_NSSMF.md`
- [ ] Tx hashes e endereços de contrato salvos

### Artefatos Coletados

1. **Logs**: `/home/porvir5g/gtp5g/trisla/logs/bc-nssmf-logs-*.log`
2. **Métricas**: `/home/porvir5g/gtp5g/trisla/logs/bc-nssmf-metrics-*.json`
3. **Eventos**: `/home/porvir5g/gtp5g/trisla/logs/bc-nssmf-events-*.log`
4. **Endereço do contrato**: Salvo em documentação
5. **Tx hashes**: Salvos em documentação
6. **Documentação atualizada**: `docs/technical/03_BC_NSSMF.md`

---

## Critério de Conclusão

O Sprint 3 NASP está concluído quando:

1. ✅ BC-NSSMF deployado e rodando no cluster NASP
2. ✅ Smart Contract deployado na rede Besu
3. ✅ Transações on-chain funcionando (tx hashes confirmados)
4. ✅ Eventos on-chain capturados e validados
5. ✅ Todos os testes funcionais passando
6. ✅ Integração com Decision Engine validada
7. ✅ Observabilidade funcionando (métricas, logs, traces)
8. ✅ Evidências experimentais coletadas e documentadas
9. ✅ Endereço do contrato e tx hashes registrados

---

## Troubleshooting

### Besu não acessível
```bash
# Verificar pods do Besu
kubectl get pods -n trisla -l app=besu

# Verificar logs do Besu
kubectl logs -n trisla -l app=besu --tail=100

# Verificar service do Besu
kubectl get svc -n trisla -l app=besu
```

### Contrato não deploya
```bash
# Verificar logs de erro
kubectl logs -n trisla -l app=bc-nssmf | grep -i "error\|exception\|contract\|deploy"

# Verificar conectividade com Besu
kubectl exec -n trisla $POD_NAME -- env | grep -i "rpc"
```

### Transações falham
```bash
# Verificar logs de erro
kubectl logs -n trisla -l app=bc-nssmf | grep -i "transaction\|tx\|error"

# Verificar saldo da conta (se necessário)
# Verificar nonce
```

---

## Próximo Passo

Após conclusão do S3 NASP, prosseguir para **PROMPT_S4_LOCAL.md** (SLA-Agent Layer).

---

**FIM DO PROMPT S3 NASP**

