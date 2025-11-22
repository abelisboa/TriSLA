# TriSLA — Guia de Troubleshooting

## 1. Introdução ao Troubleshooting do TriSLA

### 1.1 Objetivo deste Documento

Este guia fornece procedimentos sistemáticos para diagnosticar e resolver problemas comuns no TriSLA em ambiente de produção. O documento cobre desde problemas simples de configuração até falhas complexas de integração entre módulos.

### 1.2 Metodologia de Troubleshooting

Siga esta ordem ao investigar problemas:

1. **Identificar o sintoma**: O que está falhando? Qual módulo?
2. **Verificar logs**: Sempre comece pelos logs do módulo afetado
3. **Verificar saúde do pod**: Status do pod, readiness, liveness
4. **Verificar dependências**: Serviços externos (PostgreSQL, Kafka, NASP)
5. **Verificar configuração**: Values.yaml, Secrets, ConfigMaps
6. **Verificar rede**: Conectividade, DNS, Network Policies
7. **Aplicar solução**: Baseada na causa raiz identificada
8. **Validar correção**: Confirmar que o problema foi resolvido

### 1.3 Níveis de Severidade

| Severidade | Descrição | Ação Imediata |
|------------|-----------|---------------|
| **Crítico** | Sistema completamente inoperante | Investigar imediatamente, considerar rollback |
| **Alto** | Funcionalidade principal comprometida | Investigar dentro de 1 hora |
| **Médio** | Funcionalidade secundária afetada | Investigar dentro de 4 horas |
| **Baixo** | Impacto mínimo, degradação de performance | Investigar dentro de 24 horas |

---

## 2. Ferramentas de Diagnóstico Recomendadas

### 2.1 Ferramentas Kubernetes Nativas

**kubectl (essencial):**

```bash
# Versão do kubectl
kubectl version --client

# Contexto atual
kubectl config current-context

# Listar todos os recursos no namespace
kubectl get all -n trisla

# Descrever recursos detalhadamente
kubectl describe <resource> <name> -n trisla
```

**kubectl debug (para pods problemáticos):**

```bash
# Criar pod de debug
kubectl debug <pod-name> -n trisla -it --image=busybox -- sh
```

### 2.2 Ferramentas de Rede

**Testar conectividade:**

```bash
# Testar DNS
kubectl run -it --rm debug --image=busybox --restart=Never -n trisla -- \
  nslookup sem-csmf.trisla.svc.cluster.local

# Testar conectividade TCP
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -n trisla -- \
  nc -zv sem-csmf.trisla.svc.cluster.local 8080

# Testar conectividade gRPC
kubectl run -it --rm debug --image=grpcurl/grpcurl --restart=Never -n trisla -- \
  grpcurl -plaintext decision-engine:50051 list
```

### 2.3 Ferramentas de Observabilidade

**Prometheus queries úteis:**

```promql
# Taxa de erro por módulo
rate(http_requests_total{status=~"5.."}[5m])

# Latência p99
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# Uso de CPU por pod
container_cpu_usage_seconds_total{pod=~"sem-csmf-.*"}

# Uso de memória por pod
container_memory_working_set_bytes{pod=~"sem-csmf-.*"}
```

**Grafana dashboards:**

- Acessar: `http://grafana.trisla.local:3000`
- Dashboards principais:
  - TriSLA Overview
  - Module Metrics
  - Network Metrics
  - SLO Compliance

### 2.4 Scripts de Diagnóstico do Repositório

```bash
# Validação completa de produção
./scripts/validate-production-real.sh

# Validação de infraestrutura NASP
./scripts/validate-nasp-infra.sh

# Teste de conexões entre módulos
./scripts/test-module-connections.sh

# Validação E2E
./scripts/validate-e2e-pipeline.sh
```

---

## 3. Diagnóstico por Módulo

### 3.1 SEM-CSMF (Semantic Communication Service Management Function)

#### Sintomas Comuns

- Pod em estado `CrashLoopBackOff`
- Health endpoint retornando 500
- NEST não sendo gerado
- Erro de conexão com PostgreSQL
- Erro de conexão com Decision Engine (gRPC)

#### Diagnóstico Passo a Passo

**1. Verificar status do pod:**

```bash
kubectl get pods -n trisla -l app=sem-csmf
kubectl describe pod <pod-name> -n trisla
```

**2. Verificar logs:**

```bash
# Logs recentes
kubectl logs -n trisla -l app=sem-csmf --tail=100

# Logs de container anterior (se crashou)
kubectl logs -n trisla -l app=sem-csmf --previous

# Logs em tempo real
kubectl logs -n trisla -l app=sem-csmf -f
```

**3. Testar health endpoint:**

```bash
# Via port-forward
kubectl port-forward -n trisla svc/sem-csmf 8080:8080

# Em outro terminal
curl http://localhost:8080/health

# Ou diretamente no pod
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=sem-csmf -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://localhost:8080/health
```

**4. Verificar conexão com PostgreSQL:**

```bash
# Testar conexão do pod
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=sem-csmf -o jsonpath='{.items[0].metadata.name}') -- \
  python -c "import psycopg2; conn = psycopg2.connect('postgresql://trisla:password@postgres:5432/trisla'); print('OK')"
```

**5. Verificar conexão gRPC com Decision Engine:**

```bash
# Testar gRPC
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=sem-csmf -o jsonpath='{.items[0].metadata.name}') -- \
  grpcurl -plaintext decision-engine:50051 list
```

#### Problemas Comuns e Soluções

**Problema: Pod em CrashLoopBackOff**

```bash
# Verificar logs do container anterior
kubectl logs <pod-name> -n trisla --previous

# Causas comuns:
# 1. Erro de configuração (DATABASE_URL inválido)
# 2. Secret não encontrado
# 3. Erro de importação de módulos Python
# 4. Porta já em uso (improvável em Kubernetes)

# Solução: Verificar ConfigMap e Secrets
kubectl get configmap sem-csmf-config -n trisla -o yaml
kubectl get secret sem-csmf-secrets -n trisla -o yaml
```

**Problema: Health endpoint retornando 500**

```bash
# Verificar logs específicos de erro
kubectl logs -n trisla -l app=sem-csmf | grep -i "error\|exception\|traceback"

# Verificar variáveis de ambiente
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=sem-csmf -o jsonpath='{.items[0].metadata.name}') -- \
  env | grep -E "DATABASE|DECISION|KAFKA|OTLP"
```

**Problema: NEST não sendo gerado**

```bash
# Verificar logs de processamento de intents
kubectl logs -n trisla -l app=sem-csmf | grep -i "intent\|nest"

# Verificar banco de dados
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- \
  psql -U trisla -d trisla -c "SELECT * FROM intents ORDER BY created_at DESC LIMIT 5;"
```

### 3.2 ML-NSMF (Machine Learning Network Slice Management Function)

#### Sintomas Comuns

- Pod não iniciando
- Predições não sendo geradas
- Modelo ML não carregando
- Alta latência em predições
- Erro de memória (OOMKilled)

#### Diagnóstico Passo a Passo

**1. Verificar status e recursos:**

```bash
kubectl get pods -n trisla -l app=ml-nsmf
kubectl top pod -n trisla -l app=ml-nsmf
```

**2. Verificar logs:**

```bash
kubectl logs -n trisla -l app=ml-nsmf --tail=100
```

**3. Verificar carregamento do modelo:**

```bash
kubectl logs -n trisla -l app=ml-nsmf | grep -i "model\|load\|predictor"
```

**4. Testar endpoint de predição:**

```bash
# Port-forward
kubectl port-forward -n trisla svc/ml-nsmf 8081:8081

# Testar predição
curl -X POST http://localhost:8081/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"metrics": {"cpu": 0.8, "memory": 0.7, "latency": 15}}'
```

#### Problemas Comuns e Soluções

**Problema: OOMKilled (Out of Memory)**

```bash
# Verificar limites de memória
kubectl describe pod <pod-name> -n trisla | grep -A 5 "Limits"

# Aumentar limite de memória no values.yaml
mlNsmf:
  resources:
    limits:
      memory: 8Gi  # Aumentar de 4Gi para 8Gi
```

**Problema: Modelo não carregando**

```bash
# Verificar logs de carregamento
kubectl logs -n trisla -l app=ml-nsmf | grep -i "model\|file not found\|permission"

# Verificar se modelo está no volume
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=ml-nsmf -o jsonpath='{.items[0].metadata.name}') -- \
  ls -la /app/models/
```

**Problema: Predições lentas**

```bash
# Verificar métricas de latência
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=prometheus -o jsonpath='{.items[0].metadata.name}') -- \
  wget -qO- 'http://localhost:9090/api/v1/query?query=histogram_quantile(0.99,rate(ml_nsmf_prediction_duration_seconds_bucket[5m]))'

# Verificar uso de CPU
kubectl top pod -n trisla -l app=ml-nsmf
```

### 3.3 Decision Engine

#### Sintomas Comuns

- Pod não respondendo
- Decisões não sendo tomadas
- Erro de conexão com ML-NSMF
- Erro de conexão com BC-NSSMF
- gRPC server não iniciando

#### Diagnóstico Passo a Passo

**1. Verificar status:**

```bash
kubectl get pods -n trisla -l app=decision-engine
kubectl describe pod <pod-name> -n trisla
```

**2. Verificar logs:**

```bash
# Logs principais
kubectl logs -n trisla -l app=decision-engine --tail=100

# Logs do servidor gRPC (se separado)
kubectl logs -n trisla -l app=decision-engine | grep -i "grpc\|gRPC"
```

**3. Testar endpoints:**

```bash
# REST API
kubectl port-forward -n trisla svc/decision-engine 8082:8082
curl http://localhost:8082/health

# gRPC
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  grpcurl -plaintext localhost:50051 list
```

**4. Verificar conexões com dependências:**

```bash
# ML-NSMF
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://ml-nsmf:8081/health

# BC-NSSMF
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://bc-nssmf:8083/health
```

#### Problemas Comuns e Soluções

**Problema: gRPC server não iniciando**

```bash
# Verificar logs específicos de gRPC
kubectl logs -n trisla -l app=decision-engine | grep -i "grpc\|50051\|port"

# Verificar se porta está em uso
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  netstat -tlnp | grep 50051

# Verificar variável de ambiente
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  env | grep GRPC_PORT
```

**Problema: Decisões não sendo tomadas**

```bash
# Verificar logs de decisões
kubectl logs -n trisla -l app=decision-engine | grep -i "decision\|ACCEPT\|REJECT\|RENEGOTIATE"

# Verificar se está recebendo intents
kubectl logs -n trisla -l app=decision-engine | grep -i "intent\|nest"

# Verificar Kafka consumer
kubectl logs -n trisla -l app=decision-engine | grep -i "kafka\|consumer\|message"
```

### 3.4 BC-NSSMF (Blockchain Network Slice Subnet Management Function)

#### Sintomas Comuns

- Pod não conectando à blockchain
- Smart contracts não sendo deployados
- Transações falhando
- Erro de chave privada
- Erro de conexão com GoQuorum/Besu

#### Diagnóstico Passo a Passo

**1. Verificar status:**

```bash
kubectl get pods -n trisla -l app=bc-nssmf
kubectl describe pod <pod-name> -n trisla
```

**2. Verificar logs:**

```bash
kubectl logs -n trisla -l app=bc-nssmf --tail=100
```

**3. Verificar conexão com blockchain:**

```bash
# Testar conexão com nó blockchain
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=bc-nssmf -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://besu-node:8545 -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

**4. Verificar smart contracts:**

```bash
# Verificar logs de deploy
kubectl logs -n trisla -l app=bc-nssmf | grep -i "contract\|deploy\|address"

# Verificar se contrato está no ConfigMap
kubectl get configmap bc-nssmf-config -n trisla -o yaml | grep -i "contract"
```

#### Problemas Comuns e Soluções

**Problema: Erro de chave privada**

```bash
# Verificar se secret existe
kubectl get secret blockchain-keys -n trisla

# Verificar se chave está sendo carregada
kubectl logs -n trisla -l app=bc-nssmf | grep -i "private.*key\|key.*error"

# Verificar formato da chave
kubectl get secret blockchain-keys -n trisla -o jsonpath='{.data.private-key}' | base64 -d | head -c 20
```

**Problema: Transações falhando**

```bash
# Verificar logs de transações
kubectl logs -n trisla -l app=bc-nssmf | grep -i "transaction\|tx\|error"

# Verificar nonce
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=bc-nssmf -o jsonpath='{.items[0].metadata.name}') -- \
  python -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('http://besu-node:8545')); print(w3.eth.get_transaction_count('0x...'))"
```

### 3.5 SLA-Agent Layer

#### Sintomas Comuns

- Agentes não coletando métricas
- Erro de conexão com NASP
- Métricas não sendo publicadas no Kafka
- Agentes RAN/Transport/Core falhando

#### Diagnóstico Passo a Passo

**1. Verificar status de todos os agentes:**

```bash
kubectl get pods -n trisla -l app=sla-agent-layer
```

**2. Verificar logs por domínio:**

```bash
# Agente RAN
kubectl logs -n trisla -l app=sla-agent-layer | grep -i "ran\|RAN"

# Agente Transport
kubectl logs -n trisla -l app=sla-agent-layer | grep -i "transport"

# Agente Core
kubectl logs -n trisla -l app=sla-agent-layer | grep -i "core"
```

**3. Verificar coleta de métricas:**

```bash
# Verificar logs de coleta
kubectl logs -n trisla -l app=sla-agent-layer | grep -i "metric\|collect"

# Verificar publicação no Kafka
kubectl logs -n trisla -l app=sla-agent-layer | grep -i "kafka\|publish\|produce"
```

**4. Testar conectividade com NASP:**

```bash
# Via NASP Adapter
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://localhost:8085/api/v1/metrics/ran
```

#### Problemas Comuns e Soluções

**Problema: Agentes não coletando métricas**

```bash
# Verificar configuração de endpoints NASP
kubectl get configmap nasp-adapter-config -n trisla -o yaml | grep -i "endpoint\|nasp"

# Verificar conectividade
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=sla-agent-layer -o jsonpath='{.items[0].metadata.name}') -- \
  curl -k https://<NASP_RAN_ENDPOINT>/api/v1/metrics
```

**Problema: Métricas não sendo publicadas**

```bash
# Verificar conexão com Kafka
kubectl logs -n trisla -l app=sla-agent-layer | grep -i "kafka.*error\|connection.*refused"

# Verificar tópico Kafka
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=kafka -o jsonpath='{.items[0].metadata.name}') -- \
  kafka-topics.sh --list --bootstrap-server localhost:9092 | grep -i "metric\|sla"
```

### 3.6 NASP Adapter

#### Sintomas Comuns

- Pod não conectando ao NASP
- Ações não sendo executadas
- Erro de autenticação com NASP
- Timeout em requisições

#### Diagnóstico Passo a Passo

**1. Verificar status:**

```bash
kubectl get pods -n trisla -l app=nasp-adapter
kubectl describe pod <pod-name> -n trisla
```

**2. Verificar logs:**

```bash
kubectl logs -n trisla -l app=nasp-adapter --tail=100
```

**3. Verificar configuração NASP:**

```bash
# Verificar endpoints configurados
kubectl get configmap nasp-adapter-config -n trisla -o yaml

# Verificar secrets de autenticação
kubectl get secret nasp-credentials -n trisla
```

**4. Testar conectividade:**

```bash
# Testar endpoints NASP
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  curl -k https://<NASP_RAN_ENDPOINT>/health

# Verificar token de autenticação
kubectl logs -n trisla -l app=nasp-adapter | grep -i "auth\|token\|401\|403"
```

#### Problemas Comuns e Soluções

**Problema: Erro de autenticação (401/403)**

```bash
# Verificar token no secret
kubectl get secret nasp-credentials -n trisla -o jsonpath='{.data.auth-token}' | base64 -d

# Verificar logs de autenticação
kubectl logs -n trisla -l app=nasp-adapter | grep -i "unauthorized\|forbidden\|401\|403"

# Verificar se token expirou
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  curl -k -H "Authorization: Bearer $(cat /etc/secrets/auth-token)" \
  https://<NASP_RAN_ENDPOINT>/api/v1/status
```

**Problema: Timeout em requisições**

```bash
# Verificar logs de timeout
kubectl logs -n trisla -l app=nasp-adapter | grep -i "timeout\|timed.*out"

# Verificar conectividade de rede
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  ping -c 3 <NASP_RAN_ENDPOINT_IP>

# Verificar DNS
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  nslookup <NASP_RAN_ENDPOINT>
```

---

## 4. Problemas Comuns

### 4.1 gRPC Falhando (Interface I-01)

#### Sintomas

- Erro "Connection refused" ao conectar via gRPC
- Erro "Deadline exceeded" em chamadas gRPC
- gRPC server não iniciando

#### Diagnóstico

```bash
# Verificar se servidor gRPC está rodando
kubectl logs -n trisla -l app=decision-engine | grep -i "grpc.*start\|50051"

# Testar conectividade gRPC
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=sem-csmf -o jsonpath='{.items[0].metadata.name}') -- \
  grpcurl -plaintext decision-engine:50051 list

# Verificar se porta está aberta
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  netstat -tlnp | grep 50051
```

#### Soluções

**Problema: Porta não está escutando**

```bash
# Verificar variável de ambiente GRPC_PORT
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  env | grep GRPC_PORT

# Verificar logs de erro
kubectl logs -n trisla -l app=decision-engine | grep -i "error\|exception" | tail -20

# Reiniciar pod
kubectl delete pod -n trisla -l app=decision-engine
```

**Problema: mTLS falhando**

```bash
# Verificar certificados
kubectl get secret decision-engine-tls -n trisla

# Verificar logs de TLS
kubectl logs -n trisla -l app=decision-engine | grep -i "tls\|certificate\|ssl"

# Verificar configuração de mTLS no values.yaml
kubectl get configmap decision-engine-config -n trisla -o yaml | grep -i "tls\|mtls"
```

### 4.2 Kafka Sem Consumir Mensagens

#### Sintomas

- Mensagens acumulando no tópico
- Consumer lag aumentando
- Módulos não processando mensagens

#### Diagnóstico

```bash
# Verificar consumer groups
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=kafka -o jsonpath='{.items[0].metadata.name}') -- \
  kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Verificar lag por consumer group
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=kafka -o jsonpath='{.items[0].metadata.name}') -- \
  kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group decision-engine-consumer --describe

# Verificar logs de consumer
kubectl logs -n trisla -l app=decision-engine | grep -i "kafka.*consumer\|message.*received"
```

#### Soluções

**Problema: Consumer não está conectado**

```bash
# Verificar configuração de Kafka
kubectl get configmap kafka-config -n trisla -o yaml

# Verificar variáveis de ambiente
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  env | grep KAFKA

# Reiniciar consumer
kubectl delete pod -n trisla -l app=decision-engine
```

**Problema: Tópico não existe**

```bash
# Listar tópicos
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=kafka -o jsonpath='{.items[0].metadata.name}') -- \
  kafka-topics.sh --list --bootstrap-server localhost:9092

# Criar tópico se necessário
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=kafka -o jsonpath='{.items[0].metadata.name}') -- \
  kafka-topics.sh --create --bootstrap-server localhost:9092 \
  --topic trisla-intents --partitions 3 --replication-factor 3
```

### 4.3 Smart Contract Não Sendo Atualizado

#### Sintomas

- Transações falhando
- Estado do contrato não mudando
- Erro "revert" ou "out of gas"

#### Diagnóstico

```bash
# Verificar logs de transações
kubectl logs -n trisla -l app=bc-nssmf | grep -i "transaction\|tx\|revert\|gas"

# Verificar último bloco
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=bc-nssmf -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://besu-node:8545 -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'

# Verificar transação específica
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=bc-nssmf -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://besu-node:8545 -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getTransactionReceipt","params":["<tx_hash>"],"id":1}'
```

#### Soluções

**Problema: Gas insuficiente**

```bash
# Verificar gas limit configurado
kubectl get configmap bc-nssmf-config -n trisla -o yaml | grep -i "gas"

# Aumentar gas limit no código ou ConfigMap
# Editar values.yaml:
bcNssmf:
  env:
    GAS_LIMIT: "5000000"  # Aumentar conforme necessário
```

**Problema: Contrato não encontrado**

```bash
# Verificar endereço do contrato
kubectl get configmap bc-nssmf-config -n trisla -o yaml | grep -i "contract.*address"

# Verificar se contrato foi deployado
kubectl logs -n trisla -l app=bc-nssmf | grep -i "contract.*deploy\|address"
```

### 4.4 ML-NSMF Sem Resposta

#### Sintomas

- Timeout em requisições de predição
- Health endpoint não respondendo
- Pod em estado "NotReady"

#### Diagnóstico

```bash
# Verificar status do pod
kubectl get pods -n trisla -l app=ml-nsmf

# Verificar recursos (pode estar sem memória)
kubectl top pod -n trisla -l app=ml-nsmf

# Verificar logs
kubectl logs -n trisla -l app=ml-nsmf --tail=100

# Testar health
kubectl port-forward -n trisla svc/ml-nsmf 8081:8081
curl http://localhost:8081/health
```

#### Soluções

**Problema: OOMKilled**

```bash
# Aumentar limite de memória
# Editar values.yaml:
mlNsmf:
  resources:
    limits:
      memory: 8Gi  # Aumentar conforme necessário
```

**Problema: Modelo não carregando**

```bash
# Verificar se modelo existe
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=ml-nsmf -o jsonpath='{.items[0].metadata.name}') -- \
  ls -la /app/models/

# Verificar logs de carregamento
kubectl logs -n trisla -l app=ml-nsmf | grep -i "model\|load"
```

### 4.5 SEM-CSMF Não Gerando NEST

#### Sintomas

- Intents sendo recebidos mas NEST não gerado
- Erro na geração de NEST
- Timeout no processamento

#### Diagnóstico

```bash
# Verificar logs de intents
kubectl logs -n trisla -l app=sem-csmf | grep -i "intent\|nest"

# Verificar banco de dados
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- \
  psql -U trisla -d trisla -c "SELECT id, tenant_id, status, created_at FROM intents ORDER BY created_at DESC LIMIT 10;"

# Verificar ontologia
kubectl logs -n trisla -l app=sem-csmf | grep -i "ontology\|owl\|parse"
```

#### Soluções

**Problema: Ontologia não encontrada**

```bash
# Verificar se arquivo de ontologia existe
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=sem-csmf -o jsonpath='{.items[0].metadata.name}') -- \
  ls -la /app/ontology/

# Verificar ConfigMap
kubectl get configmap sem-csmf-config -n trisla -o yaml | grep -i "ontology"
```

**Problema: Erro de parsing**

```bash
# Verificar logs de erro
kubectl logs -n trisla -l app=sem-csmf | grep -i "error\|exception\|traceback" | tail -50

# Verificar formato do intent
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- \
  psql -U trisla -d trisla -c "SELECT intent_text FROM intents ORDER BY created_at DESC LIMIT 1;"
```

### 4.6 Decision Engine Travado

#### Sintomas

- Decisões não sendo tomadas
- Pod não respondendo
- CPU em 100%

#### Diagnóstico

```bash
# Verificar uso de recursos
kubectl top pod -n trisla -l app=decision-engine

# Verificar logs
kubectl logs -n trisla -l app=decision-engine --tail=100

# Verificar threads (deadlock?)
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  ps aux | grep python
```

#### Soluções

**Problema: Deadlock ou loop infinito**

```bash
# Reiniciar pod
kubectl delete pod -n trisla -l app=decision-engine

# Verificar logs após reinício
kubectl logs -n trisla -l app=decision-engine -f
```

**Problema: Dependência travada**

```bash
# Verificar conexões com dependências
kubectl logs -n trisla -l app=decision-engine | grep -i "ml-nsmf\|bc-nssmf\|timeout"

# Testar dependências individualmente
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=decision-engine -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://ml-nsmf:8081/health
```

---

## 5. Falhas em Deploy / Helm

### 5.1 Helm Install/Upgrade Falhando

#### Sintomas

- Erro ao executar `helm install` ou `helm upgrade`
- Timeout durante deploy
- Recursos não sendo criados

#### Diagnóstico

```bash
# Verificar sintaxe do chart
helm lint ./helm/trisla

# Dry-run para ver o que seria criado
helm install trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml \
  --dry-run --debug

# Verificar histórico de releases
helm history trisla -n trisla
```

#### Soluções

**Problema: Erro de sintaxe YAML**

```bash
# Validar YAML
yamllint ./helm/trisla/values-nasp.yaml

# Verificar templates
helm template trisla ./helm/trisla --values ./helm/trisla/values-nasp.yaml
```

**Problema: Timeout**

```bash
# Aumentar timeout
helm upgrade trisla ./helm/trisla \
  --namespace trisla \
  --values ./helm/trisla/values-nasp.yaml \
  --timeout 20m \
  --wait
```

**Problema: Recursos não criados**

```bash
# Verificar eventos do Kubernetes
kubectl get events -n trisla --sort-by='.lastTimestamp'

# Verificar se namespace existe
kubectl get namespace trisla

# Verificar permissões RBAC
kubectl auth can-i create deployments -n trisla
```

### 5.2 Rollback Necessário

#### Procedimento de Rollback

```bash
# Ver histórico de releases
helm history trisla -n trisla

# Rollback para versão anterior
helm rollback trisla <revision-number> -n trisla

# Ou rollback para última versão estável
helm rollback trisla -n trisla

# Verificar status após rollback
kubectl get pods -n trisla
helm status trisla -n trisla
```

---

## 6. Falhas de Readiness/Liveness

### 6.1 Pods Não Ficando Ready

#### Sintomas

- Pods em estado "0/1 Ready" ou "0/2 Ready"
- Readiness probe falhando
- Pods sendo removidos do Service

#### Diagnóstico

```bash
# Verificar status dos pods
kubectl get pods -n trisla

# Descrever pod para ver detalhes do probe
kubectl describe pod <pod-name> -n trisla | grep -A 10 "Readiness"

# Verificar eventos
kubectl get events -n trisla --sort-by='.lastTimestamp' | grep <pod-name>

# Testar endpoint de readiness manualmente
kubectl exec -n trisla -it <pod-name> -- curl http://localhost:8080/ready
```

#### Soluções

**Problema: Endpoint de readiness não implementado**

```bash
# Verificar se endpoint existe
kubectl exec -n trisla -it <pod-name> -- curl http://localhost:8080/ready

# Se não existir, implementar no código ou ajustar probe
# Editar deployment:
readinessProbe:
  httpGet:
    path: /health  # Usar /health se /ready não existir
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
```

**Problema: Readiness probe muito restritivo**

```bash
# Ajustar probe no values.yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30  # Aumentar delay inicial
  periodSeconds: 10        # Aumentar período
  timeoutSeconds: 5        # Aumentar timeout
  failureThreshold: 3      # Aumentar threshold de falhas
```

### 6.2 Pods Sendo Reiniciados (Liveness)

#### Sintomas

- Pods reiniciando constantemente
- Restart count aumentando
- Liveness probe falhando

#### Diagnóstico

```bash
# Verificar restart count
kubectl get pods -n trisla -o wide

# Ver logs do container anterior
kubectl logs <pod-name> -n trisla --previous

# Verificar liveness probe
kubectl describe pod <pod-name> -n trisla | grep -A 10 "Liveness"
```

#### Soluções

**Problema: Aplicação travada**

```bash
# Verificar logs para identificar causa
kubectl logs <pod-name> -n trisla --previous | tail -100

# Ajustar liveness probe se muito agressivo
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 60  # Dar mais tempo para iniciar
  periodSeconds: 30
  timeoutSeconds: 10
  failureThreshold: 3
```

---

## 7. Falhas de Configuração em values.yaml

### 7.1 Valores Inválidos

#### Sintomas

- Pods não iniciando
- Erro de parsing de configuração
- Comportamento inesperado

#### Diagnóstico

```bash
# Validar values.yaml
helm lint ./helm/trisla --values ./helm/trisla/values-nasp.yaml

# Ver valores renderizados
helm template trisla ./helm/trisla --values ./helm/trisla/values-nasp.yaml

# Verificar ConfigMaps gerados
kubectl get configmap -n trisla -o yaml
```

#### Soluções

**Problema: Valores obrigatórios faltando**

```bash
# Verificar valores obrigatórios no README
# Preencher valores faltantes em values-nasp.yaml:
naspAdapter:
  env:
    NASP_RAN_ENDPOINT: "https://<ENDPOINT>"  # ⚠️ OBRIGATÓRIO
    NASP_AUTH_TOKEN: "<TOKEN>"                # ⚠️ OBRIGATÓRIO
```

**Problema: Tipos incorretos**

```bash
# Verificar tipos no values.yaml
# Exemplo: replicas deve ser número, não string
semCsmf:
  replicas: 2  # ✅ Correto
  # replicas: "2"  # ❌ Incorreto
```

### 7.2 Secrets Não Configurados

#### Sintomas

- Erro "secret not found"
- Autenticação falhando
- Imagens não sendo puxadas

#### Diagnóstico

```bash
# Verificar secrets
kubectl get secrets -n trisla

# Verificar se secret está sendo referenciado
kubectl get deployment sem-csmf -n trisla -o yaml | grep -i secret

# Verificar se secret existe
kubectl get secret ghcr-secret -n trisla
```

#### Soluções

**Problema: Secret não existe**

```bash
# Criar secret
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<USERNAME> \
  --docker-password=<TOKEN> \
  --docker-email=<EMAIL> \
  --namespace=trisla
```

**Problema: Secret com valores incorretos**

```bash
# Atualizar secret
kubectl delete secret ghcr-secret -n trisla
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<USERNAME> \
  --docker-password=<NEW_TOKEN> \
  --docker-email=<EMAIL> \
  --namespace=trisla

# Reiniciar pods para usar novo secret
kubectl rollout restart deployment -n trisla
```

---

## 8. Falhas no NASP (Node1/Node2)

### 8.1 Conectividade com NASP

#### Sintomas

- Timeout ao conectar com NASP
- Erro "Connection refused"
- Erro de DNS

#### Diagnóstico

```bash
# Testar conectividade de rede
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  ping -c 3 <NASP_NODE_IP>

# Testar DNS
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  nslookup <NASP_ENDPOINT>

# Testar endpoint HTTP
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  curl -k https://<NASP_ENDPOINT>/health
```

#### Soluções

**Problema: DNS não resolvendo**

```bash
# Verificar configuração DNS do cluster
kubectl get configmap coredns -n kube-system -o yaml

# Adicionar entrada no /etc/hosts do pod (temporário)
kubectl exec -n trisla -it <pod-name> -- sh -c "echo '<IP> <HOSTNAME>' >> /etc/hosts"
```

**Problema: Firewall bloqueando**

```bash
# Verificar Network Policies
kubectl get networkpolicies -n trisla

# Verificar se egress está permitido
kubectl describe networkpolicy <policy-name> -n trisla | grep -A 20 "Egress"
```

### 8.2 Autenticação com NASP

#### Sintomas

- Erro 401 (Unauthorized)
- Erro 403 (Forbidden)
- Token expirado

#### Diagnóstico

```bash
# Verificar token no secret
kubectl get secret nasp-credentials -n trisla -o jsonpath='{.data.auth-token}' | base64 -d

# Verificar logs de autenticação
kubectl logs -n trisla -l app=nasp-adapter | grep -i "auth\|401\|403"

# Testar token manualmente
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=nasp-adapter -o jsonpath='{.items[0].metadata.name}') -- \
  curl -k -H "Authorization: Bearer $(cat /etc/secrets/auth-token)" \
  https://<NASP_ENDPOINT>/api/v1/status
```

#### Soluções

**Problema: Token expirado**

```bash
# Obter novo token do NASP
# Atualizar secret
kubectl create secret generic nasp-credentials \
  --from-literal=auth-token="<NEW_TOKEN>" \
  --namespace=trisla \
  --dry-run=client -o yaml | kubectl apply -f -

# Reiniciar pods
kubectl rollout restart deployment nasp-adapter -n trisla
```

---

## 9. Falhas de Rede (Calico, DNS, Cluster Networking)

### 9.1 Problemas com Calico

#### Sintomas

- Pods não conseguindo se comunicar
- Network Policies não funcionando
- Erro de conectividade entre pods

#### Diagnóstico

```bash
# Verificar status do Calico
kubectl get pods -n kube-system | grep calico

# Verificar logs do Calico
kubectl logs -n kube-system -l k8s-app=calico-node --tail=50

# Verificar Network Policies
kubectl get networkpolicies -n trisla
```

#### Soluções

**Problema: Calico não está rodando**

```bash
# Reiniciar Calico
kubectl delete pod -n kube-system -l k8s-app=calico-node

# Verificar se reiniciou
kubectl get pods -n kube-system | grep calico
```

**Problema: Network Policy muito restritiva**

```bash
# Verificar política
kubectl get networkpolicy <policy-name> -n trisla -o yaml

# Temporariamente desabilitar para teste
kubectl delete networkpolicy <policy-name> -n trisla

# Se funcionar, ajustar política para ser menos restritiva
```

### 9.2 Problemas de DNS

#### Sintomas

- Resolução de nomes falhando
- Erro "no such host"
- Timeout em resolução DNS

#### Diagnóstico

```bash
# Verificar CoreDNS
kubectl get pods -n kube-system | grep coredns

# Verificar logs do CoreDNS
kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50

# Testar resolução DNS
kubectl run -it --rm debug --image=busybox --restart=Never -n trisla -- \
  nslookup kubernetes.default
```

#### Soluções

**Problema: CoreDNS não está rodando**

```bash
# Reiniciar CoreDNS
kubectl delete pod -n kube-system -l k8s-app=kube-dns

# Verificar se reiniciou
kubectl get pods -n kube-system | grep coredns
```

**Problema: Configuração DNS incorreta**

```bash
# Verificar ConfigMap do CoreDNS
kubectl get configmap coredns -n kube-system -o yaml

# Editar se necessário
kubectl edit configmap coredns -n kube-system
```

### 9.3 Problemas de Cluster Networking

#### Sintomas

- Pods não conseguindo se comunicar entre si
- Services não resolvendo
- Ingress não funcionando

#### Diagnóstico

```bash
# Verificar nodes
kubectl get nodes -o wide

# Verificar serviços
kubectl get svc -n trisla

# Testar conectividade entre pods
kubectl run -it --rm debug1 --image=busybox --restart=Never -n trisla -- \
  ping -c 3 <POD_IP>

# Verificar endpoints
kubectl get endpoints -n trisla
```

#### Soluções

**Problema: Service sem endpoints**

```bash
# Verificar se pods têm labels corretos
kubectl get pods -n trisla --show-labels

# Verificar selector do Service
kubectl get svc sem-csmf -n trisla -o yaml | grep -A 5 selector

# Labels devem corresponder
```

---

## 10. Falhas de GHCR

### 10.1 Imagens Não Sendo Puxadas

#### Sintomas

- Pods em estado "ImagePullBackOff"
- Erro "unauthorized" ou "pull access denied"
- Timeout ao puxar imagens

#### Diagnóstico

```bash
# Verificar status dos pods
kubectl get pods -n trisla

# Ver detalhes do erro
kubectl describe pod <pod-name> -n trisla | grep -A 10 "Events"

# Verificar secret
kubectl get secret ghcr-secret -n trisla
```

#### Soluções

**Problema: Secret não configurado**

```bash
# Criar secret
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USERNAME> \
  --docker-password=<GITHUB_TOKEN> \
  --docker-email=<EMAIL> \
  --namespace=trisla
```

**Problema: Token inválido ou expirado**

```bash
# Gerar novo token no GitHub
# Atualizar secret
kubectl delete secret ghcr-secret -n trisla
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USERNAME> \
  --docker-password=<NEW_TOKEN> \
  --docker-email=<EMAIL> \
  --namespace=trisla

# Deletar pods para forçar novo pull
kubectl delete pod -n trisla --all
```

**Problema: Imagem não existe ou tag incorreta**

```bash
# Verificar se imagem existe no GHCR
# Acessar: https://github.com/abelisboa/TriSLA/pkgs/container/trisla-sem-csmf

# Verificar tag no values.yaml
kubectl get deployment sem-csmf -n trisla -o yaml | grep image:
```

---

## 11. Falhas de Prometheus / Grafana

### 11.1 Prometheus Não Coletando Métricas

#### Sintomas

- Métricas não aparecendo no Prometheus
- Targets em estado "Down"
- Erro de scraping

#### Diagnóstico

```bash
# Verificar status do Prometheus
kubectl get pods -n trisla -l app=prometheus

# Verificar logs
kubectl logs -n trisla -l app=prometheus --tail=50

# Verificar targets
kubectl port-forward -n trisla svc/prometheus 9090:9090
# Acessar: http://localhost:9090/targets
```

#### Soluções

**Problema: ServiceMonitor não configurado**

```bash
# Verificar ServiceMonitors
kubectl get servicemonitor -n trisla

# Criar ServiceMonitor se necessário
# Ver exemplo em monitoring/prometheus/
```

**Problema: Endpoints não expondo métricas**

```bash
# Verificar se /metrics está disponível
kubectl port-forward -n trisla svc/sem-csmf 8080:8080
curl http://localhost:8080/metrics
```

### 11.2 Grafana Não Carregando Dashboards

#### Sintomas

- Dashboards não aparecendo
- Erro ao conectar com Prometheus
- Dados não sendo exibidos

#### Diagnóstico

```bash
# Verificar status do Grafana
kubectl get pods -n trisla -l app=grafana

# Verificar logs
kubectl logs -n trisla -l app=grafana --tail=50

# Verificar ConfigMaps de dashboards
kubectl get configmap -n trisla | grep grafana
```

#### Soluções

**Problema: Data source não configurado**

```bash
# Verificar ConfigMap de datasource
kubectl get configmap grafana-datasource -n trisla -o yaml

# Verificar se Prometheus está acessível
kubectl exec -n trisla -it $(kubectl get pod -n trisla -l app=grafana -o jsonpath='{.items[0].metadata.name}') -- \
  curl http://prometheus:9090/api/v1/status/config
```

**Problema: Dashboards não provisionados**

```bash
# Verificar ConfigMap de dashboards
kubectl get configmap grafana-dashboards -n trisla

# Recriar se necessário
kubectl apply -f monitoring/grafana/dashboards/
```

---

## 12. Como Coletar Logs Detalhados

### 12.1 Logs de Todos os Módulos

```bash
# Coletar logs de todos os módulos
for module in sem-csmf ml-nsmf decision-engine bc-nssmf sla-agent-layer nasp-adapter; do
  echo "=== Logs de $module ==="
  kubectl logs -n trisla -l app=$module --tail=100 > logs-$module-$(date +%Y%m%d-%H%M%S).log
done
```

### 12.2 Logs com Contexto

```bash
# Logs com timestamps e contexto
kubectl logs -n trisla -l app=sem-csmf --timestamps --tail=1000 > sem-csmf-detailed.log

# Logs de container anterior (se crashou)
kubectl logs -n trisla -l app=sem-csmf --previous --timestamps > sem-csmf-previous.log
```

### 12.3 Logs de Infraestrutura

```bash
# Logs do Kafka
kubectl logs -n trisla -l app=kafka --tail=100 > kafka.log

# Logs do PostgreSQL
kubectl logs -n trisla -l app=postgres --tail=100 > postgres.log

# Logs do OTLP Collector
kubectl logs -n trisla -l app=otlp-collector --tail=100 > otlp-collector.log
```

### 12.4 Logs de Eventos do Kubernetes

```bash
# Eventos do namespace
kubectl get events -n trisla --sort-by='.lastTimestamp' > events-$(date +%Y%m%d-%H%M%S).log

# Eventos de um pod específico
kubectl get events -n trisla --field-selector involvedObject.name=<pod-name> > pod-events.log
```

### 12.5 Script de Coleta Completa

```bash
#!/bin/bash
# collect-all-logs.sh

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_DIR="trisla-logs-$TIMESTAMP"
mkdir -p "$LOG_DIR"

echo "Coletando logs do TriSLA..."

# Logs de módulos
for module in sem-csmf ml-nsmf decision-engine bc-nssmf sla-agent-layer nasp-adapter; do
  kubectl logs -n trisla -l app=$module --tail=1000 --timestamps > "$LOG_DIR/$module.log" 2>&1
done

# Logs de infraestrutura
kubectl logs -n trisla -l app=kafka --tail=1000 --timestamps > "$LOG_DIR/kafka.log" 2>&1
kubectl logs -n trisla -l app=postgres --tail=1000 --timestamps > "$LOG_DIR/postgres.log" 2>&1
kubectl logs -n trisla -l app=prometheus --tail=1000 --timestamps > "$LOG_DIR/prometheus.log" 2>&1

# Status de recursos
kubectl get all -n trisla -o yaml > "$LOG_DIR/resources.yaml"
kubectl get events -n trisla --sort-by='.lastTimestamp' > "$LOG_DIR/events.log"

# Descrever pods problemáticos
kubectl get pods -n trisla -o json | jq '.items[] | select(.status.phase != "Running") | .metadata.name' | \
  xargs -I {} kubectl describe pod {} -n trisla > "$LOG_DIR/problematic-pods.log"

echo "Logs coletados em: $LOG_DIR"
```

---

## 13. Scripts Úteis do Repositório

### 13.1 Scripts de Validação

```bash
# Validação completa de produção
./scripts/validate-production-real.sh

# Validação de infraestrutura NASP
./scripts/validate-nasp-infra.sh

# Validação E2E
./scripts/validate-e2e-pipeline.sh

# Validação local
./scripts/validate-local.sh
```

### 13.2 Scripts de Deploy

```bash
# Deploy completo no NASP
./scripts/deploy-trisla-nasp.sh

# Deploy com validação
./scripts/deploy-completo-nasp.sh
```

### 13.3 Scripts de Teste

```bash
# Teste de conexões entre módulos
./scripts/test-module-connections.sh

# Teste E2E completo
./scripts/complete-e2e-test.sh

# Teste de API
./scripts/test-api.ps1
```

### 13.4 Scripts de Diagnóstico

```bash
# Pre-flight check
./scripts/pre-flight-check.sh

# Verificar estrutura
./scripts/verify-structure.ps1

# Verificar imagens GHCR
./scripts/verify-images-ghcr.ps1
```

### 13.5 Scripts de Manutenção

```bash
# Rollback
./scripts/rollback.sh

# Backup PostgreSQL
./scripts/backup-postgres.sh

# Restore PostgreSQL
./scripts/restore-postgres.sh
```

---

## 14. Checklist Final de Troubleshooting Rápido

### 14.1 Checklist Inicial (5 minutos)

- [ ] Verificar status geral: `kubectl get all -n trisla`
- [ ] Verificar pods problemáticos: `kubectl get pods -n trisla | grep -v Running`
- [ ] Verificar eventos recentes: `kubectl get events -n trisla --sort-by='.lastTimestamp' | tail -20`
- [ ] Verificar logs do módulo afetado: `kubectl logs -n trisla -l app=<module> --tail=50`
- [ ] Verificar recursos: `kubectl top pods -n trisla`

### 14.2 Checklist de Dependências (10 minutos)

- [ ] PostgreSQL está rodando: `kubectl get pods -n trisla -l app=postgres`
- [ ] Kafka está rodando: `kubectl get pods -n trisla -l app=kafka`
- [ ] OTLP Collector está rodando: `kubectl get pods -n trisla -l app=otlp-collector`
- [ ] DNS está funcionando: `kubectl run -it --rm debug --image=busybox --restart=Never -n trisla -- nslookup kubernetes.default`
- [ ] Conectividade de rede: `kubectl run -it --rm debug --image=busybox --restart=Never -n trisla -- ping -c 3 8.8.8.8`

### 14.3 Checklist de Configuração (10 minutos)

- [ ] Secrets existem: `kubectl get secrets -n trisla`
- [ ] ConfigMaps existem: `kubectl get configmaps -n trisla`
- [ ] Values.yaml válido: `helm lint ./helm/trisla --values ./helm/trisla/values-nasp.yaml`
- [ ] ImagePullSecrets configurado: `kubectl get deployment -n trisla -o yaml | grep imagePullSecrets`
- [ ] Variáveis de ambiente corretas: `kubectl exec -n trisla -it <pod> -- env | grep -E "DATABASE|KAFKA|NASP"`

### 14.4 Checklist de Rede (10 minutos)

- [ ] Services existem: `kubectl get svc -n trisla`
- [ ] Endpoints configurados: `kubectl get endpoints -n trisla`
- [ ] Network Policies: `kubectl get networkpolicies -n trisla`
- [ ] Ingress configurado: `kubectl get ingress -n trisla`
- [ ] Port-forward funciona: `kubectl port-forward -n trisla svc/<service> <port>:<port>`

### 14.5 Checklist de Observabilidade (5 minutos)

- [ ] Prometheus rodando: `kubectl get pods -n trisla -l app=prometheus`
- [ ] Grafana rodando: `kubectl get pods -n trisla -l app=grafana`
- [ ] Métricas sendo coletadas: Acessar Prometheus UI e verificar targets
- [ ] Dashboards carregando: Acessar Grafana UI

### 14.6 Checklist de Ação Imediata (Crítico)

Se sistema completamente inoperante:

- [ ] Coletar logs completos: Executar `collect-all-logs.sh`
- [ ] Verificar último deploy: `helm history trisla -n trisla`
- [ ] Considerar rollback: `helm rollback trisla -n trisla`
- [ ] Verificar recursos do cluster: `kubectl top nodes`
- [ ] Verificar eventos críticos: `kubectl get events -n trisla --sort-by='.lastTimestamp' | grep -i "error\|fail\|crash"`

---

## Conclusão

Este guia fornece uma abordagem sistemática para troubleshooting do TriSLA. Sempre comece pelos logs e status básicos, depois avance para diagnósticos mais específicos conforme necessário.

**Lembre-se:**
- Sempre coletar logs antes de fazer mudanças
- Documentar problemas e soluções encontradas
- Testar soluções em ambiente de desenvolvimento primeiro quando possível
- Manter backups e pontos de restauração

**Última atualização:** 2025-01-XX  
**Versão do documento:** 1.0.0  
**Versão do TriSLA:** 1.0.0


