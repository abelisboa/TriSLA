# FASE EC.2.1 — Localização do Código de Chamada ao Decision Engine

**Data:** 2025-01-27  
**Versão:** v3.7.2-nasp

---

## 🔍 Busca por Referências

### 1. Busca por `127.0.0.1`
**Resultado:** Nenhuma ocorrência encontrada

### 2. Busca por `50051`
**Resultado:** 3 ocorrências encontradas

| Arquivo | Linha | Conteúdo |
|---------|-------|----------|
| `apps/sem-csmf/src/grpc_server.py` | 42 | `def serve(port=50051):` |
| `apps/sem-csmf/src/grpc_client_retry.py` | 30 | `"localhost:50051"` |
| `apps/sem-csmf/src/grpc_client.py` | 27 | `"localhost:50051"  # Padrão para desenvolvimento local` |

### 3. Busca por `grpc` (case-insensitive)
**Resultado:** 79 ocorrências encontradas

**Arquivos principais:**
- `apps/sem-csmf/src/main.py` — Importa e usa clientes gRPC
- `apps/sem-csmf/src/grpc_client.py` — Cliente gRPC básico
- `apps/sem-csmf/src/grpc_client_retry.py` — Cliente gRPC com retry
- `apps/sem-csmf/src/grpc_server.py` — Servidor gRPC (I-01)
- `apps/sem-csmf/src/proto/proto/i01_interface_pb2_grpc.py` — Código gerado do proto

---

## 📋 Arquivos Identificados

### Arquivo Principal: `apps/sem-csmf/src/main.py`

**Linha 26-27:** Importação dos clientes gRPC
```python
from grpc_client import DecisionEngineClient
from grpc_client_retry import DecisionEngineClientWithRetry
```

**Linha 83-89:** Inicialização do cliente
```python
USE_RETRY_CLIENT = os.getenv("USE_GRPC_RETRY", "true").lower() == "true"
if USE_RETRY_CLIENT:
    grpc_client = DecisionEngineClientWithRetry()
else:
    grpc_client = DecisionEngineClient()
```

**Linha 138-147:** Chamada ao Decision Engine
```python
# 6. Enviar metadados via I-01 (gRPC) para Decision Engine
decision_response = await grpc_client.send_nest_metadata(
    intent_id=intent.intent_id,
    nest_id=nest.nest_id,
    tenant_id=intent.tenant_id,
    service_type=intent.service_type.value,
    sla_requirements=intent.sla_requirements.dict(),
    nest_status=nest.status.value,
    metadata=metadata
)
```

### Arquivo: `apps/sem-csmf/src/grpc_client.py`

**Linha 25-28:** Configuração do endpoint gRPC
```python
DECISION_ENGINE_GRPC = os.getenv(
    "DECISION_ENGINE_GRPC",
    "localhost:50051"  # Padrão para desenvolvimento local
)
```

**Linha 45-121:** Método `send_nest_metadata` que envia via gRPC

### Arquivo: `apps/sem-csmf/src/grpc_client_retry.py`

**Linha 28-31:** Configuração do endpoint gRPC
```python
DECISION_ENGINE_GRPC = os.getenv(
    "DECISION_ENGINE_GRPC",
    "localhost:50051"
)
```

**Linha 125-211:** Método `send_nest_metadata` com retry logic

---

## 🎯 Função Principal de Chamada

**Função:** `send_nest_metadata`

**Localização:** 
- `apps/sem-csmf/src/grpc_client.py` (linha 45)
- `apps/sem-csmf/src/grpc_client_retry.py` (linha 125)

**Assinatura:**
```python
async def send_nest_metadata(
    self,
    intent_id: str,
    nest_id: str,
    tenant_id: Optional[str],
    service_type: str,
    sla_requirements: Dict[str, Any],
    nest_status: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

**Uso em `main.py`:**
- Linha 139: `decision_response = await grpc_client.send_nest_metadata(...)`

---

## 📊 Resumo

| Item | Valor |
|------|-------|
| Arquivos com referências gRPC | 5 principais |
| Função principal de chamada | `send_nest_metadata` |
| Local de uso | `main.py` linha 139 |
| Endpoint padrão atual | `localhost:50051` |
| Variável de ambiente atual | `DECISION_ENGINE_GRPC` |
| Variável de ambiente desejada | `DECISION_ENGINE_URL` |

---

## ✅ Próximos Passos

1. Criar `apps/sem-csmf/src/decision_engine_client.py` com cliente HTTP
2. Substituir importação e uso em `main.py`
3. Remover ou manter clientes gRPC (manter para compatibilidade futura, mas não usar)
4. Validar que `DECISION_ENGINE_URL` é lida corretamente

---

**Status:** ✅ Localização concluída

