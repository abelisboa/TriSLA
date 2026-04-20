# Evidência — Auditoria XAI em Runtime (TriSLA NASP)

**Data:** 2026-03-18  
**Namespace:** trisla  
**Regras:** Sem alteração de código, sem build, sem deploy. Apenas auditoria e evidência técnica.

---

## 1. Evidência logs portal-backend

**Comando:** `kubectl -n trisla logs deployment/trisla-portal-backend --tail=300`

**Resultado (trecho relevante após submit real):**
```
2026-03-18 23:29:04,230 - httpx - INFO - HTTP Request: POST http://trisla-sem-csmf:8080/api/v1/interpret "HTTP/1.1 200 OK"
2026-03-18 23:29:04,368 - httpx - INFO - HTTP Request: POST http://trisla-sem-csmf:8080/api/v1/intents "HTTP/1.1 200 OK"
INFO:     127.0.0.1:41088 - "POST /api/v1/sla/submit HTTP/1.1" 200 OK
```

**Conclusão:** O portal-backend recebe POST /api/v1/sla/submit, chama interpret e intents no SEM-CSMF (ambos 200 OK) e responde 200. Não há log do corpo da resposta de /submit; o contrato SLASubmitResponse inclui os campos reasoning, confidence, domains, metadata (evidência de código já documentada). Os valores desses campos vêm do `result` retornado pelo SEM-CSMF (response.json() de /intents).

---

## 2. Evidência logs SEM-CSMF

**Comando:** `kubectl -n trisla logs deployment/trisla-sem-csmf --tail=300`

**Resultado (trecho relevante):**
```
INFO:     10.233.75.56:53888 - "POST /api/v1/interpret HTTP/1.1" 200 OK
Erro HTTP ao comunicar com Decision Engine: 422 Client Error: Unprocessable Entity for url: http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate
INFO:     10.233.75.56:53900 - "POST /api/v1/intents HTTP/1.1" 200 OK
```

**Conclusão:** O SEM-CSMF atende /interpret e /intents com 200. Na chamada ao Decision Engine (POST /evaluate) o SEM-CSMF recebe **422 Unprocessable Entity**. Em caso de erro HTTP (422), o decision_engine_client retorna o bloco de exceção com reasoning=None, confidence=None, domains=None, metadata=None. Portanto o IntentResponse é montado com esses campos nulos e o portal-backend repassa null na SLASubmitResponse. Não há perda de contrato no SEM-CSMF; os valores são nulos porque a resposta do DE não foi 200.

---

## 3. Evidência logs Decision Engine

**Comando:** `kubectl -n trisla logs deployment/trisla-decision-engine --tail=300`

**Resultado (trecho relevante):**
```
INFO:     10.233.102.165:55850 - "POST /evaluate HTTP/1.1" 422 Unprocessable Entity
```

**Conclusão:** O Decision Engine responde **422 Unprocessable Entity** ao POST /evaluate. Isso indica falha de validação do body (ex.: schema SLAEvaluateInput). Enquanto o DE retornar 422, não há payload de sucesso (reasoning, confidence, domains, metadata, decision_snapshot, system_xai_explanation) para o SEM-CSMF consumir. O runbook (TRISLA_MASTER_RUNBOOK.md) já documenta: "SEM-CSMF envia payload sem campo intent" e "Campo obrigatório no body: intent". A 422 é consistente com payload enviado não conforme ao contrato esperado pelo /evaluate.

---

## 4. Payload submit real (teste curl)

**Comando (após port-forward trisla-portal-backend 8001:8001):**
```bash
curl -s http://localhost:8001/api/v1/sla/submit \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
  "template_id":"urllc-basic",
  "tenant_id":"default",
  "form_values":{
    "service_name":"URLLC low latency"
  }
}' | jq .
```

**Resposta real (200 OK):**
```json
{
  "intent_id": "e5be9583-1e67-4210-95f2-22d8fce1b838",
  "service_type": null,
  "sla_requirements": null,
  "ml_prediction": null,
  "decision": "REJECT",
  "justification": "",
  "reason": "",
  "blockchain_tx_hash": null,
  "tx_hash": null,
  "sla_hash": null,
  "timestamp": null,
  "status": "accepted",
  "sla_id": null,
  "nest_id": "nest-e5be9583-1e67-4210-95f2-22d8fce1b838",
  "sem_csmf_status": "ERROR",
  "ml_nsmf_status": "ERROR",
  "bc_status": "ERROR",
  "sla_agent_status": "SKIPPED",
  "block_number": null,
  "reasoning": null,
  "confidence": null,
  "domains": null,
  "metadata": null
}
```

**Conclusão:** O contrato SLASubmitResponse **entrega** os campos reasoning, confidence, domains e metadata. Neste teste eles vêm **null** porque o Decision Engine retornou 422 e o SEM-CSMF preencheu o IntentResponse com o retorno de exceção do client (todos null). Não há perda de contrato no portal-backend; há ausência de dados XAI na origem (DE 422).

---

## 5. Diagnóstico científico final

### 5.1 XAI já responde à pergunta da pesquisa?

**Parcialmente.** O contrato ponta a ponta (backend → frontend) está preparado: SLASubmitResponse e Template exibem reasoning, confidence, domains, metadata e decision_snapshot. No runtime atual, esses campos chegam **null** quando o Decision Engine devolve 422. Quando o DE retornar 200 com body válido (reasoning, confidence, domains, metadata), o fluxo já repassa até o frontend sem nova perda.

### 5.2 Os três domínios aparecem?

**Quando o DE retornar 200:** sim, na lista `domains` e em `metadata.decision_snapshot.domains` (RAN, Transport, Core). No teste atual (DE 422) não há payload de sucesso, então domains e metadata vêm null.

### 5.3 A origem da decisão está explicada?

**Quando o DE retornar 200:** sim, via `reasoning` e opcionalmente `metadata.system_xai_explanation`. No cenário 422, reasoning vem null.

### 5.4 Há rastreabilidade real por domínio?

**Quando o DE retornar 200:** sim, via `metadata.decision_snapshot.domains` (estrutura por RAN, Transport, Core com status e métricas). No cenário 422, metadata é null.

### 5.5 Blockchain aparece associado?

No payload de submit, tx_hash, block_number e bc_status estão no contrato; no teste vieram null (sem registro em blockchain no fluxo atual e sem resposta 200 do DE com metadata).

---

## 6. Camada em que ocorre a “perda” (valores null)

**Não é perda de contrato.** Os campos existem no contrato em todas as camadas.

**Causa dos valores null no runtime auditado:**

1. **Decision Engine** responde **422 Unprocessable Entity** ao POST /evaluate (validação do body falha; runbook indica obrigatoriedade do campo `intent`).
2. **SEM-CSMF** ao receber 422 usa o bloco de exceção do decision_engine_client e retorna reasoning, confidence, domains, metadata como **null** no IntentResponse.
3. **Portal-backend** repassa fielmente o `result` (SLASubmitResponse com os quatro campos null).
4. **Frontend** recebe e exibe os campos (podendo mostrar "—" quando null).

**Resposta direta:** a “falta” de valores XAI no teste real tem origem no **decision-engine** (resposta 422). Não há perda adicional em sem-csmf, portal-backend ou frontend; quando o DE retornar 200 com body completo, o fluxo está preparado para propagar XAI até o frontend.

---

## 7. Resumo para Runbook

- **XAI Runtime Audit Completed:** 2026-03-18.
- **Template Frontend Scientific XAI validated:** Contrato e UI (reasoning, confidence, domains, metadata, decision_snapshot, ml_risk_score, ml_risk_level) validados; valores preenchidos dependem de POST /evaluate retornar 200 com payload conforme SLAEvaluateInput (incl. campo `intent` quando obrigatório).
