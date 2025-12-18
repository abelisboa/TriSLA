# BC-NSSMF — Especificação Técnica e Implementação

**Versão:** v3.7.16 (Sprint S3.4 - Helm Chart Modular e Idempotente)  
**Data:** 2025-12-17  
**Imagem Docker:** `ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.16`

## 1. Objetivo do módulo
Formalizar SLAs como Smart Contracts executáveis e auditáveis, assegurando:
- deploy e execução em rede Besu (Hyperledger)
- vínculo SLA ↔ contrato ↔ transações
- logs e eventos on-chain para auditoria
- Integração com Decision Engine via Interface I-04

## 2. Arquitetura on-chain

### 2.1 Infraestrutura Blockchain — Consolidação Besu (Sprint S3.5.1)

**Hyperledger Besu:**
- **Versão:** `23.10.1` (compatível com Besu ≥ 23.x)
- **Imagem:** `hyperledger/besu:23.10.1`
- **Rede:** Dev network (cria blocos automaticamente)
- **RPC JSON-RPC:** Porta `8545` (HTTP)
- **RPC WebSocket:** Porta `8546` (opcional)
- **P2P:** Porta `30303` (opcional)

**⚠️ Dependência BC-NSSMF → Besu:**
- BC-NSSMF depende de RPC Besu funcional para operações on-chain
- Health semântico do BC-NSSMF cobre ausência de Besu:
  - `READY`: RPC e contrato disponíveis
  - `DEGRADED_RPC`: RPC Besu indisponível
  - `DEGRADED_CONTRACT`: Contrato não encontrado
  - `ERROR`: Erro crítico

**Flags de configuração (Sprint S3.3 - Consolidação):**
```bash
besu \
  --network=dev \
  --rpc-http-enabled=true \
  --rpc-http-host=0.0.0.0 \
  --rpc-http-port=8545 \
  --rpc-http-api=ETH,NET,WEB3 \
  --host-allowlist="*" \
  --rpc-http-cors-origins="*"
```

**⚠️ Flags removidas (obsoletas):**
- ❌ `--miner-enabled` (dev network não precisa de mineração explícita)
- ❌ `--miner-coinbase` (não necessário)
- ❌ `--miner-extra-data` (não necessário)

**Helm Chart:**
- **Deployment:** `helm/trisla/templates/deployment-besu.yaml`
- **Service:** `helm/trisla/templates/service-besu.yaml`
- **ConfigMap:** `helm/trisla/templates/configmap-besu.yaml` (genesis)
- **PVC:** `helm/trisla/templates/pvc-besu.yaml` (persistência)

**Labels consistentes (Pod ↔ Service):**
```yaml
labels:
  app: besu
  component: blockchain
```

**Health Checks:**
- **LivenessProbe:** TCP socket na porta 8545
- **ReadinessProbe:** TCP socket na porta 8545

**Garantias de idempotência (Sprint S3.3):**
- ✅ Deploy isolado do Besu via Helm
- ✅ RPC 8545 funcional por design
- ✅ Service resolve corretamente os Pods
- ✅ Labels Pod ↔ Service alinhados
- ✅ Nenhuma flag obsoleta presente
- ✅ Helm é idempotente (install/uninstall/reinstall)
- ✅ Nenhuma correção manual necessária

**Dependência explícita para BC-NSSMF:**
- BC-NSSMF assume RPC estável em `http://trisla-besu:8545`
- Configuração via `TRISLA_RPC_URL` quando `besu.enabled=true`
- Health previsível para consumidores (BC-NSSMF)

### 2.2 RPC endpoints
- RPC HTTP: `http://trisla-besu:8545` (ClusterIP)
- RPC WebSocket: `ws://trisla-besu:8546` (opcional)
- Contas e chaves (tratamento seguro via `BC_PRIVATE_KEY`)
- ChainId: `1337` (configurado no genesis)

## 3. Modelo de contrato

### 3.1 Smart Contract Solidity
- **Arquivo:** `apps/bc-nssmf/src/contracts/SLAContract.sol`
- **Versão Solidity:** `^0.8.20`
- **Licença:** MIT

### 3.2 Estados do SLA (enum SLAState) - Sprint S3.1
Estados formais do ciclo de vida SLA-aware:
- `CREATED` (0) - SLA criado no blockchain
- `ACTIVE` (1) - SLA ativo e em execução
- `VIOLATED` (2) - SLA violado (SLO não atendido)
- `RENEGOTIATED` (3) - SLA renegociado após violação
- `CLOSED` (4) - SLA fechado (finalizado)

**Regras de transição:**
- `CREATED` → `ACTIVE` (via `activateSLA`)
- `ACTIVE` → `VIOLATED` (via `reportViolation`)
- `ACTIVE` → `CLOSED` (via `closeSLA`)
- `VIOLATED` → `RENEGOTIATED` (via `renegotiateSLA`)
- `RENEGOTIATED` → `ACTIVE` (via `activateSLA`)
- `RENEGOTIATED` → `CLOSED` (via `closeSLA`)
- `VIOLATED` → `CLOSED` (via `closeSLA`)

### 3.3 Eventos (Sprint S3.1)
- `SLACreated(bytes32 indexed slaId, address indexed owner)` - Emitido ao criar SLA
- `SLAActivated(bytes32 indexed slaId)` - Emitido ao ativar SLA
- `SLAViolated(bytes32 indexed slaId, string reason)` - Emitido ao reportar violação
- `SLARenegotiated(bytes32 indexed slaId)` - Emitido ao renegociar SLA
- `SLACLOSED(bytes32 indexed slaId)` - Emitido ao fechar SLA

### 3.4 Funções públicas (Sprint S3.1)
- `createSLA(bytes32 slaId) returns (bool)` - Cria novo SLA no blockchain
- `activateSLA(bytes32 slaId) returns (bool)` - Ativa SLA (CREATED → ACTIVE)
- `reportViolation(bytes32 slaId, string calldata reason) returns (bool)` - Reporta violação (ACTIVE → VIOLATED)
- `renegotiateSLA(bytes32 slaId) returns (bool)` - Renegocia SLA (VIOLATED/ACTIVE → RENEGOTIATED)
- `closeSLA(bytes32 slaId) returns (bool)` - Fecha SLA (qualquer estado → CLOSED)
- `getSLA(bytes32 slaId) returns (SLA memory)` - Obtém dados completos do SLA
- `getSLAState(bytes32 slaId) returns (SLAState)` - Obtém apenas o estado atual

### 3.5 Estruturas (Sprint S3.1)
```solidity
struct SLA {
    bytes32 slaId;
    address owner;
    SLAState state;
    uint256 createdAt;
    uint256 updatedAt;
}
```

**Modificadores:**
- `slaExists(bytes32 slaId)` - Verifica se SLA existe
- `validStateTransition(bytes32 slaId, SLAState newState)` - Valida transição de estado

## 4. Integração com Decision Engine (Interface I-04)

### 4.1 Endpoints REST (Sprint S3.1 - SLA-aware)

**Novos endpoints do ciclo de vida SLA:**
- **POST /api/v1/sla/create** - Cria novo SLA no blockchain
  - **Body:** `SLACreateRequest` com `slaId` (string hex)
  - **Response:** `{status: "ok", tx_hash, block_number, sla_id}`
- **POST /api/v1/sla/activate** - Ativa SLA (CREATED → ACTIVE)
  - **Body:** `SLAActivateRequest` com `slaId`
  - **Response:** `{status: "ok", tx_hash, block_number, sla_id}`
- **POST /api/v1/sla/violate** - Reporta violação (ACTIVE → VIOLATED)
  - **Body:** `SLAViolateRequest` com `slaId` e `reason`
  - **Response:** `{status: "ok", tx_hash, block_number, sla_id}`
- **POST /api/v1/sla/renegotiate** - Renegocia SLA (VIOLATED/ACTIVE → RENEGOTIATED)
  - **Body:** `SLARenegotiateRequest` com `slaId`
  - **Response:** `{status: "ok", tx_hash, block_number, sla_id}`
- **POST /api/v1/sla/close** - Fecha SLA (qualquer estado → CLOSED)
  - **Body:** `SLACloseRequest` com `slaId`
  - **Response:** `{status: "ok", tx_hash, block_number, sla_id}`
- **GET /api/v1/sla/status/{sla_id}** - Obtém status de SLA
  - **Response:** `SLAResponse` com `slaId`, `owner`, `state`, `stateName`, `createdAt`, `updatedAt`

**Endpoints legados (compatibilidade):**
- **POST /api/v1/register-sla** - Registra SLA (contrato antigo)
- **POST /api/v1/update-sla-status** - Atualiza status (contrato antigo)
- **GET /api/v1/get-sla/{sla_id}** - Obtém SLA (contrato antigo)

### 4.2 Fluxo de integração (Sprint S3.1)
1. **Criação:** Decision Engine ou sistema externo cria SLA via `POST /api/v1/sla/create`
   - Evento `SLACreated` é emitido on-chain
   - Estado inicial: `CREATED`
2. **Ativação:** SLA é ativado via `POST /api/v1/sla/activate`
   - Evento `SLAActivated` é emitido
   - Estado: `ACTIVE`
3. **Monitoramento:** Durante execução, métricas são coletadas
4. **Violação (se detectada):** Sistema reporta violação via `POST /api/v1/sla/violate`
   - Evento `SLAViolated` é emitido com motivo
   - Estado: `VIOLATED`
5. **Renegociação (opcional):** SLA pode ser renegociado via `POST /api/v1/sla/renegotiate`
   - Evento `SLARenegotiated` é emitido
   - Estado: `RENEGOTIATED`
   - Pode retornar para `ACTIVE` após renegociação
6. **Encerramento:** SLA é fechado via `POST /api/v1/sla/close`
   - Evento `SLACLOSED` é emitido
   - Estado: `CLOSED` (final)
7. **Auditoria:** Todos os eventos são imutáveis e auditáveis on-chain

### 4.3 Modo Degraded
- Se RPC Besu não disponível, serviço entra em modo degraded
- Endpoints retornam 503 (Service Unavailable)
- Health check indica `status: "degraded"`
- Configuração via `BC_ENABLED=false` (padrão em desenvolvimento)

## 5. Evidências exigidas
- [ ] contrato (.sol) versionado
- [ ] endereço do contrato
- [ ] tx hash de deploy
- [ ] evento emitido com intent_id/sla_id
- [ ] consulta ao contrato provando estado

## 6. Testes
- testes de contrato (unit)
- testes E2E (deploy + evento)

## 7. Segurança e auditoria
- gestão de segredos
- logs
- assinaturas
- trilha de auditoria

## 5. Observabilidade

### 5.1 Métricas Prometheus (Sprint S3.1)
- **Endpoint:** `GET /metrics`
- **Métricas gerais:**
  - `trisla_bc_transactions_total{contract_type, status}` - Contador de transações
  - `trisla_bc_failures_total{error_type}` - Contador de falhas
  - `trisla_bc_commit_latency_ms` - Histograma de latência de commit
  - `trisla_bc_transactions_latency_ms` - Histograma de latência de transações
  - `trisla_bc_block_height` - Altura atual do bloco
  - `trisla_bc_pending_transactions` - Transações pendentes
- **Métricas SLA-aware (Sprint S3.1):**
  - `trisla_bc_sla_created_total` - Total de SLAs criados
  - `trisla_bc_sla_activated_total` - Total de SLAs ativados
  - `trisla_bc_sla_violated_total` - Total de violações reportadas
  - `trisla_bc_sla_renegotiated_total` - Total de SLAs renegociados

### 5.2 OpenTelemetry (Traces)
- **Service Name:** `trisla-bc-nssmf`
- **Version:** `3.7.14`
- **Endpoint:** Configurável via `OTEL_EXPORTER_OTLP_ENDPOINT`
- **Spans instrumentados (Sprint S3.1):**
  - `create_sla` - Criação de SLA
  - `activate_sla` - Ativação de SLA
  - `violate_sla` - Reporte de violação
  - `renegotiate_sla` - Renegociação de SLA
  - `close_sla` - Fechamento de SLA
  - `get_sla_status` - Consulta de status
  - `register_sla_i04` - Registro de SLA (legado)
  - `update_sla_status_i04` - Atualização de status (legado)
  - `get_sla_i04` - Consulta de SLA (legado)
- **Atributos:** `trisla.transaction.hash`, `trisla.bc.block_number`, `trisla.sla.customer`

### 5.3 Logs estruturados
- **Formato:** JSON estruturado
- **Informações registradas:**
  - tx_hash de transações
  - sla_id
  - block_number
  - Erros e exceções
  - Status de conexão RPC

## 6. Configuração RPC

### 6.1 Variáveis de ambiente
- `BC_ENABLED` - Habilita/desabilita blockchain (padrão: `false`)
- `BC_RPC_URL` - URL do RPC Besu (ex: `http://besu:8545`)
- `BC_PRIVATE_KEY` - Chave privada para assinatura de transações (obrigatória se BC_ENABLED=true)
- `OTLP_ENABLED` - Habilita exportação OTEL (padrão: `false`)
- `OTEL_EXPORTER_OTLP_ENDPOINT` - Endpoint do OTEL Collector

### 6.2 Gestão de chaves
- **Nenhuma chave hardcoded** - Todas via variáveis de ambiente
- **Assinatura local** - Usa `eth-account` para assinar transações localmente
- **Fallback:** Se BC_PRIVATE_KEY não configurada, tenta usar `eth_accounts` (modo desenvolvimento)

## 7. Docker e Deployment

### 7.1 Imagem Docker
- **Registry:** `ghcr.io/abelisboa`
- **Imagem:** `ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.16` (Sprint S3.2 - Consolidação)
- **Base:** `python:3.10-slim`
- **Porta:** 8083
- **Dockerfile:** `apps/bc-nssmf/Dockerfile`

### 7.2 Helm Chart
- **Chart:** `helm/trisla`
- **Values:** `helm/trisla/values.yaml`
- **Configuração:**
```yaml
bcNssmf:
  enabled: true
  image:
    repository: ghcr.io/abelisboa/trisla-bc-nssmf
    tag: v3.7.16
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8083
  replicas: 2
```

## 8. Limitações do modo LOCAL

### 8.1 O que NÃO é exigido no LOCAL
- ❌ Deploy no Kubernetes
- ❌ Execução no NASP
- ❌ Prometheus Server real
- ❌ OTEL Collector real
- ❌ Cálculo de SLO
- ❌ Besu LOCAL obrigatório (opcional)

### 8.2 O que É exigido no LOCAL
- ✅ Smart Contract válido
- ✅ Código BC-NSSMF revisado
- ✅ Observabilidade instrumentada (código pronto)
- ✅ Imagem Docker construída
- ✅ Imagem publicada no GHCR
- ✅ Helm chart validado
- ✅ Documentação atualizada

## 9. Status de aderência à proposta
| Requisito | Situação | Evidência |
|---|---|---|
| Smart Contract válido | ✅ Implementado (S3.1) | `apps/bc-nssmf/src/contracts/SLAContract.sol` |
| Estados formais de SLA | ✅ Implementado (S3.1) | enum SLAState (CREATED, ACTIVE, VIOLATED, RENEGOTIATED, CLOSED) |
| Eventos on-chain | ✅ Implementado (S3.1) | SLACreated, SLAActivated, SLAViolated, SLARenegotiated, SLACLOSED |
| Regras de transição | ✅ Implementado (S3.1) | Modifiers `validStateTransition` com validação explícita |
| Funções ciclo de vida | ✅ Implementado (S3.1) | createSLA, activateSLA, reportViolation, renegotiateSLA, closeSLA |
| Integração Decision Engine (I-04) | ✅ Implementado | Endpoints REST em `main.py` (novos + legados) |
| Observabilidade instrumentada | ✅ Implementado (S3.1) | Métricas SLA-aware, traces e logs em `observability/` |
| Imagem Docker funcional | ✅ Construída (S3.2) | `ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.16` |
| Helm chart preparado | ✅ Atualizado (S3.2) | `helm/trisla/values.yaml` (tag v3.7.16) |
| Documentação atualizada | ✅ Atualizado (S3.2) | Este documento |
| Inicialização segura | ✅ Implementado (S3.2) | Health semântico (READY, DEGRADED_RPC, DEGRADED_CONTRACT, ERROR) |
| Robustez transações | ✅ Implementado (S3.2) | Retry com backoff exponencial, logs estruturados |
| Observabilidade consolidada | ✅ Implementado (S3.2) | Métricas finais congeladas, traces completos |
| Infraestrutura Besu consolidada | ✅ Implementado (S3.3) | Helm Chart idempotente, RPC 8545 funcional, flags atualizadas |
| Helm Chart modular e idempotente | ✅ Implementado (S3.4) | Guard clauses em todos os templates, valores padrão obrigatórios, isolamento funcional |

## 10. Consolidação Pós-NASP (Sprint S3.2)

### 10.1 Correções Aplicadas

**Inicialização Segura:**
- Health endpoint semântico com estados explícitos: `READY`, `DEGRADED_RPC`, `DEGRADED_CONTRACT`, `ERROR`
- Verificação de RPC Besu antes de inicializar serviço
- Verificação de contrato disponível antes de permitir operações SLA
- Nenhum endpoint SLA funciona se RPC ou contrato indisponível

**Robustez de Transações:**
- Retry com exponential backoff (3 tentativas, delay inicial 1s, fator 2.0)
- Timeout de 120s para `wait_for_transaction_receipt`
- Logs estruturados obrigatórios: `tx_hash`, `block_number`, `sla_id`, `customer`, `service_name`
- Erros claros no retorno REST (422 para business, 503 para infrastructure)

**Observabilidade Consolidada:**
- Métricas Prometheus finais congeladas:
  - `trisla_bc_transactions_total{contract_type, status}`
  - `trisla_bc_sla_created_total`
  - `trisla_bc_sla_activated_total`
  - `trisla_bc_sla_violated_total`
  - `trisla_bc_sla_renegotiated_total`
  - `trisla_bc_tx_latency_seconds` (métrica final consolidada)
- Spans OpenTelemetry em todas as operações:
  - `create_sla`, `activate_sla`, `violate_sla`, `renegotiate_sla`, `close_sla`, `get_sla_status`
- Trace ID presente nos logs estruturados

**Helm Chart:**
- `BC_ENABLED=true` por padrão (produção)
- `TRISLA_RPC_URL` sempre injetada quando `besu.enabled=true`
- Health checks não dependem de hacks manuais
- Labels consistentes entre Deployment e Service

### 10.2 Garantias de Idempotência

- **Imagem Docker:** Build idempotente - mesmo código gera mesma imagem
- **Helm Chart:** Templates geram manifests corretos sem ajustes manuais
- **Código Python:** Inicialização segura previne estados inválidos
- **Transações:** Retry com backoff garante entrega eventual

### 10.3 Versão Final Congelada

**v3.7.16** - Estado consolidado após validação NASP:
- Todas as correções do NASP incorporadas
- Código refletindo exatamente o estado funcional validado
- Nenhuma correção manual necessária em novos deploys
- Sistema pronto para qualquer cluster Kubernetes

### 10.4 Estado "Pronto para Qualquer Cluster"

O BC-NSSMF v3.7.16 está pronto para:
- ✅ Deploy idempotente em qualquer cluster Kubernetes
- ✅ Eliminação de hotfixes manuais
- ✅ Reprodutibilidade completa da arquitetura
- ✅ Integração com Besu via Helm Chart
- ✅ Observabilidade completa (Prometheus + OTEL)
- ✅ Fluxo on-chain robusto (sem estados inválidos)
