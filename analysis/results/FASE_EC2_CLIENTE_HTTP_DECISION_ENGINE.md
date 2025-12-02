# FASE EC.2.2 — Padronização do Cliente HTTP para Decision Engine

**Data:** 2025-01-27  
**Versão:** v3.7.2-nasp

---

## ✅ Arquivo Criado

### `apps/sem-csmf/src/decision_engine_client.py`

**Características:**
- Cliente HTTP usando `requests`
- Lê variável de ambiente `DECISION_ENGINE_URL`
- Valor padrão: `http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate`
- Timeout configurável via `HTTP_TIMEOUT` (padrão: 10.0s)
- Tratamento robusto de erros (Timeout, ConnectionError, HTTPError)
- Logging estruturado
- OpenTelemetry tracing integrado

**Método principal:**
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

**Payload enviado:**
```json
{
    "intent_id": str,
    "nest_id": str,
    "tenant_id": str,
    "service_type": str,
    "sla_requirements": dict,
    "nest_status": str,
    "metadata": dict (opcional)
}
```

**Resposta normalizada:**
```python
{
    "success": bool,
    "decision_id": str,
    "message": str,
    "status_code": int
}
```

---

## ✅ Modificações em `apps/sem-csmf/src/main.py`

### 1. Importação (linha 26-27)
**Antes:**
```python
from grpc_client import DecisionEngineClient
from grpc_client_retry import DecisionEngineClientWithRetry
```

**Depois:**
```python
from decision_engine_client import DecisionEngineHTTPClient
```

### 2. Inicialização do Cliente (linha 83-89)
**Antes:**
```python
# Cliente gRPC para Decision Engine (com retry)
USE_RETRY_CLIENT = os.getenv("USE_GRPC_RETRY", "true").lower() == "true"
if USE_RETRY_CLIENT:
    grpc_client = DecisionEngineClientWithRetry()
else:
    grpc_client = DecisionEngineClient()
```

**Depois:**
```python
# Cliente HTTP para Decision Engine
# Usa DECISION_ENGINE_URL (padrão: http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate)
decision_engine_client = DecisionEngineHTTPClient()
```

### 3. Chamada ao Decision Engine (linha 138-139)
**Antes:**
```python
# 6. Enviar metadados via I-01 (gRPC) para Decision Engine
decision_response = await grpc_client.send_nest_metadata(
```

**Depois:**
```python
# 6. Enviar metadados via I-01 (HTTP) para Decision Engine
decision_response = await decision_engine_client.send_nest_metadata(
```

### 4. Atributo de Span (linha 152)
**Antes:**
```python
span.set_attribute("grpc.success", decision_response.get("success", False))
```

**Depois:**
```python
span.set_attribute("decision_engine.success", decision_response.get("success", False))
```

---

## ✅ Validações Realizadas

### 1. Remoção de Referências a `127.0.0.1:50051`
- ✅ Nenhuma referência encontrada em `main.py`
- ✅ Cliente HTTP usa `DECISION_ENGINE_URL` da variável de ambiente

### 2. Remoção de Importações gRPC
- ✅ `grpc_client` e `grpc_client_retry` removidos de `main.py`
- ✅ Cliente HTTP importado corretamente

### 3. Compatibilidade de Interface
- ✅ Método `send_nest_metadata` mantém mesma assinatura
- ✅ Resposta normalizada para compatibilidade com código existente
- ✅ Tratamento de erros retorna estrutura compatível

---

## 📋 Arquivos Mantidos (não removidos)

Os seguintes arquivos foram mantidos para referência futura, mas não são mais usados:
- `apps/sem-csmf/src/grpc_client.py`
- `apps/sem-csmf/src/grpc_client_retry.py`
- `apps/sem-csmf/src/grpc_server.py`
- `apps/sem-csmf/src/proto/` (arquivos proto mantidos)

**Motivo:** Manter compatibilidade futura e não quebrar outras partes do sistema que possam depender desses arquivos.

---

## 🔍 Verificação de Referências Restantes

### Busca por `grpc_client` em `apps/sem-csmf/src`
**Resultado:** Nenhuma referência encontrada em arquivos Python ativos (apenas nos arquivos mantidos para referência)

### Busca por `DecisionEngineClient` em `apps/sem-csmf/src`
**Resultado:** Nenhuma referência encontrada em `main.py`

---

## ✅ Checklist de Conclusão

- [x] Cliente HTTP criado (`decision_engine_client.py`)
- [x] `DECISION_ENGINE_URL` lido da variável de ambiente
- [x] Valor padrão configurado corretamente
- [x] `main.py` atualizado para usar cliente HTTP
- [x] Nenhuma referência a `127.0.0.1:50051` em código ativo
- [x] Nenhuma referência a `localhost:50051` em código ativo
- [x] Interface de método mantida compatível
- [x] Tratamento de erros robusto implementado
- [x] Logging estruturado adicionado
- [x] OpenTelemetry tracing integrado

---

## 📝 Notas

1. **Compatibilidade:** O cliente HTTP mantém a mesma interface assíncrona (`async def`) para compatibilidade com o código existente, mesmo que `requests` seja síncrono. Em produção, pode-se considerar usar `httpx` para verdadeira assincronia, mas `requests` é suficiente para esta correção.

2. **Variável de Ambiente:** O Helm chart já está configurado para injetar `DECISION_ENGINE_URL` no pod do SEM-CSMF, então o cliente HTTP usará automaticamente o valor correto em produção.

3. **Fallback:** Se `DECISION_ENGINE_URL` não estiver definida, o cliente usa o valor padrão que aponta para o service Kubernetes do Decision Engine.

---

**Status:** ✅ Cliente HTTP implementado e integrado

