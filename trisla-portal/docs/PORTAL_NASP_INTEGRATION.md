# Portal TriSLA - Integração com NASP

## Visão Geral

O Portal TriSLA é uma aplicação "leve" que atua como uma "janela" para o NASP (Network Automation Service Platform). O Portal não contém lógica de simulação ou mock dos módulos NASP - todas as operações passam exclusivamente pelos serviços reais do NASP.

## Arquitetura

```
┌─────────────────┐
│  Portal TriSLA  │
│  (Frontend +    │
│   Backend)       │
└────────┬────────┘
         │
         │ HTTP (port-forward)
         │
┌────────▼─────────────────────────────────────┐
│  NASP TriSLA (Kubernetes Cluster)             │
│  ┌─────────────┐  ┌─────────────┐            │
│  │ SEM-CSMF    │  │ ML-NSMF     │            │
│  │ :8080       │  │ :8081       │            │
│  └─────────────┘  └─────────────┘            │
│  ┌─────────────┐  ┌─────────────┐            │
│  │ Decision    │  │ BC-NSSMF    │            │
│  │ Engine      │  │ :8083       │            │
│  │ :8082       │  └─────────────┘            │
│  └─────────────┘  ┌─────────────┐            │
│                    │ SLA-Agent   │            │
│                    │ Layer       │            │
│                    │ :8084       │            │
│                    └─────────────┘            │
└───────────────────────────────────────────────┘
```

## Configuração

### Port-Forwards no node1

Para conectar o Portal local aos módulos NASP remotos, os seguintes port-forwards devem estar ativos no node1:

```bash
# SEM-CSMF
kubectl port-forward -n trisla svc/trisla-sem-csmf 8080:8080

# ML-NSMF
kubectl port-forward -n trisla svc/trisla-ml-nsmf 8081:8081

# Decision Engine
kubectl port-forward -n trisla svc/trisla-decision-engine 8082:8082

# BC-NSSMF
kubectl port-forward -n trisla svc/trisla-bc-nssmf 8083:8083

# SLA-Agent Layer
kubectl port-forward -n trisla svc/trisla-sla-agent-layer 8084:8084
```

### Variáveis de Ambiente

O Portal usa as seguintes variáveis de ambiente para configurar as URLs dos módulos NASP:

| Variável | Default | Descrição |
|----------|---------|-----------|
| `NASP_SEM_CSMF_URL` | `http://localhost:8080` | URL do módulo SEM-CSMF |
| `NASP_ML_NSMF_URL` | `http://localhost:8081` | URL do módulo ML-NSMF |
| `NASP_DECISION_URL` | `http://localhost:8082` | URL do módulo Decision Engine |
| `NASP_BC_NSSMF_URL` | `http://localhost:8083` | URL do módulo BC-NSSMF |
| `NASP_SLA_AGENT_URL` | `http://localhost:8084` | URL do módulo SLA-Agent Layer |

**Nota**: Os defaults são configurados para o cenário de port-forward local. Em outros cenários (NASP direto, sem port-forward), ajuste as URLs para apontar para o IP/hostname do NASP.

### Arquivo .env

Crie um arquivo `.env` na raiz do backend com as variáveis necessárias:

```env
# NASP Module URLs
NASP_SEM_CSMF_URL=http://localhost:8080
NASP_ML_NSMF_URL=http://localhost:8081
NASP_DECISION_URL=http://localhost:8082
NASP_BC_NSSMF_URL=http://localhost:8083
NASP_SLA_AGENT_URL=http://localhost:8084

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
API_RELOAD=true
```

## Endpoints do Portal

### Health Check

**GET** `/health`

Retorna o status básico do Portal:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "nasp_reachable": null,
  "nasp_details_url": "/nasp/diagnostics"
}
```

### Diagnóstico NASP

**GET** `/nasp/diagnostics`

Retorna o estado de conectividade com todos os módulos NASP:

```json
{
  "sem_csmf": {
    "reachable": true,
    "latency_ms": 12.5,
    "detail": null,
    "status_code": 200
  },
  "ml_nsmf": {
    "reachable": true,
    "latency_ms": 15.2,
    "detail": null,
    "status_code": 200
  },
  "decision": {
    "reachable": true,
    "latency_ms": 20.1,
    "detail": null,
    "status_code": 200
  },
  "bc_nssmf": {
    "reachable": true,
    "latency_ms": 25.3,
    "detail": null,
    "status_code": 200,
    "rpc_connected": true
  },
  "sla_agent": {
    "reachable": true,
    "latency_ms": 18.7,
    "detail": null,
    "status_code": 200
  }
}
```

### Submissão de SLA

**POST** `/api/v1/sla/submit`

Submete um SLA através da pipeline completa NASP:

1. **SEM-CSMF**: Interpreta template e gera NEST
2. **ML-NSMF**: Avalia capacidades e recursos
3. **Decision Engine**: Decisão final (ACCEPT/REJECT)
4. **BC-NSSMF**: Registro no blockchain (com retries e resiliência)
5. **SLA-Agent Layer**: Coleta métricas iniciais (apenas se ACCEPT)

**Request**:
```json
{
  "template_id": "urllc-template-001",
  "tenant_id": "default",
  "form_values": {
    "type": "URLLC",
    "latency": 10,
    "reliability": 99.99,
    "availability": 99.99
  }
}
```

**Response**:
```json
{
  "decision": "ACCEPT",
  "reason": "Recursos suficientes disponíveis",
  "justification": "Recursos suficientes disponíveis",
  "sla_id": "sla-12345",
  "timestamp": "2025-01-15T10:30:00Z",
  "intent_id": "intent-67890",
  "service_type": "URLLC",
  "sla_requirements": {...},
  "ml_prediction": {...},
  "blockchain_tx_hash": "0x1234...",
  "tx_hash": "0x1234...",
  "sla_hash": "abc123...",
  "status": "ok",
  "sem_csmf_status": "OK",
  "ml_nsmf_status": "OK",
  "bc_status": "CONFIRMED",
  "sla_agent_status": "OK",
  "block_number": 12345,
  "nest_id": "nest-abc"
}
```

## Resiliência e Tratamento de Erros

### BC-NSSMF - Retries e Backoff

O endpoint `/register-sla` do BC-NSSMF implementa resiliência robusta:

- **Retries**: Mínimo de 3 tentativas
- **Backoff**: Exponencial simples (1s, 2s, 3s)
- **Timeout**: 5 segundos (connect + read)
- **Tratamento diferenciado de erros**:
  - **Erro de conexão/timeout**: `reason: "connection_error"` - Problema de port-forward ou NASP offline
  - **Erro 503 com JSON**: `reason: "nasp_degraded"` - BC-NSSMF em modo degraded, RPC Besu não disponível
  - **Erro 4xx**: `reason: "invalid_payload"` - Problema de validação do payload

### Mensagens de Erro Estruturadas

O backend retorna erros estruturados para facilitar o tratamento no frontend:

```json
{
  "detail": {
    "success": false,
    "phase": "blockchain",
    "reason": "connection_error" | "nasp_degraded" | "invalid_payload" | "unknown",
    "detail": "Mensagem humana legível"
  }
}
```

O frontend interpreta esses erros e exibe mensagens claras ao usuário:

- **connection_error**: "Falha ao contatar o módulo BC-NSSMF (Blockchain). Verifique se o NASP está acessível."
- **nasp_degraded**: "Módulo NASP em modo degradado: [detalhes]"
- **invalid_payload**: "Erro de validação: [detalhes]"

## Diagnóstico Automático

### Startup

Ao iniciar o backend, um diagnóstico leve é executado automaticamente:

- Testa conectividade com SEM-CSMF e BC-NSSMF
- Loga resultados (INFO ou WARNING)
- Não bloqueia o startup se houver falhas

### Logs

O Portal loga claramente os estados dos módulos NASP:

- ✅ **Sucesso**: `✅ SEM-CSMF acessível (latência: 12.5ms)`
- ⚠️ **Aviso**: `⚠️ BC-NSSMF não acessível no startup: [detalhes]`
- ❌ **Erro**: `❌ BC-NSSMF: erro de conexão (provável problema de port-forward ou NASP offline)`

## Checklist de Validação

Use este checklist para validar que o Portal está configurado corretamente:

- [ ] **Port-forwards ativos em node1**: 8080-8084
- [ ] **Backend rodando**: `http://localhost:8001`
- [ ] **GET /health**: Retorna `status=ok`
- [ ] **GET /nasp/diagnostics**: Todos os módulos com `reachable=true`
- [ ] **Envio de SLA de teste**: Pipeline completa SEM → ML → Decision → BC → SLA-Agent
- [ ] **Hash de transação**: Registrado no log após submissão bem-sucedida

### Comandos de Validação

```bash
# 1. Verificar health do Portal
curl http://localhost:8001/health

# 2. Verificar diagnóstico NASP
curl http://localhost:8001/nasp/diagnostics

# 3. Testar submissão de SLA
curl -X POST http://localhost:8001/api/v1/sla/submit \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "urllc-template-001",
    "tenant_id": "default",
    "form_values": {
      "type": "URLLC",
      "latency": 10,
      "reliability": 99.99
    }
  }'
```

## Princípios de Design

1. **NASP-First**: O Portal não contém lógica de simulação ou mock dos módulos NASP
2. **Resiliência**: Tratamento robusto de falhas transitórias (port-forward, latência)
3. **Diagnóstico**: Exposição clara do estado de conectividade com o NASP
4. **Configurabilidade**: Todas as URLs configuráveis via variáveis de ambiente
5. **Leveza**: Portal apenas orquestra chamadas ao NASP, monta payloads e exibe resultados

## Troubleshooting

### Erro: "BC-NSSMF offline"

**Causa**: Port-forward não está ativo ou NASP não está acessível

**Solução**:
1. Verificar se o port-forward está ativo: `kubectl get pods -n trisla`
2. Verificar conectividade: `curl http://localhost:8083/health`
3. Reiniciar port-forward se necessário

### Erro: "BC-NSSMF está em modo degraded. RPC Besu não disponível"

**Causa**: BC-NSSMF não consegue conectar ao Besu (blockchain)

**Solução**:
1. Verificar status do BC-NSSMF: `curl http://localhost:8083/health`
2. Verificar logs do BC-NSSMF no cluster
3. Verificar se o Besu está rodando e acessível

### Erro: "Timeout ao contatar o módulo BC-NSSMF"

**Causa**: Latência alta ou port-forward instável

**Solução**:
1. O Portal já implementa retries automáticos
2. Verificar latência de rede
3. Considerar aumentar timeout se necessário (não recomendado)

## Arquivos Modificados

### Backend

- `backend/src/config.py`: Configuração centralizada com variáveis de ambiente
- `backend/src/services/nasp.py`: Resiliência para BC-NSSMF com retries
- `backend/src/services/nasp_health.py`: Módulo de diagnóstico NASP (novo)
- `backend/src/schemas/nasp_diagnostics.py`: Schemas para diagnóstico (novo)
- `backend/src/main.py`: Endpoints `/health` e `/nasp/diagnostics`, diagnóstico no startup

### Frontend

- `frontend/src/lib/api.ts`: Melhor tratamento de erros estruturados

## Referências

- [Arquitetura do Portal](../docs/ARCHITECTURE_v4.0.md)
- [Guia de API](../docs/API_ARCHITECTURE.md)
- [Manual do Usuário](../docs/MANUAL_USUARIO.md)




