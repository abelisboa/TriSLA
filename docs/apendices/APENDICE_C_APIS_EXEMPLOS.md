# 📘 Apêndice C — Contratos de API e Exemplos

Contém os contratos REST (OpenAPI), gRPC (Protobuf) e Kafka (JSON).

Arquivos reais disponíveis em:

- `apps/api/openapi.yaml`
- `apps/decision/trisla.v1.proto`
- `schemas/risk_event.json`

Exemplo REST (I-06):

```bash
curl -X POST https://agent.core.local/v1/agent/core/reconfigure \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"policyId":"latency-guard","params":{"p99":25},"deadlineMs":1500}'
```

