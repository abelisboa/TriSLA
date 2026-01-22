# S6.13D — FIX NASP Adapter + Blockchain E2E

**Data:** 2025-12-21  
**Versões (imagens/tags):**
- Decision Engine: v3.7.27
- ML-NSMF: v3.7.27
- NASP Adapter: v3.7.10
- SLA-Agent Layer: nasp-a2
- BC-NSSMF: v3.7.18
- Besu: v3.7.11

**ACCEPT (decision_id):** dec-184d1edd-006b-45b9-9221-3d0e3bc5896e

## Causa raiz do Adapter

**Problema inicial:** "All connection attempts failed" ao chamar NASP Adapter

**Causa identificada:** Decision Engine não tinha env var `NASP_ADAPTER_URL` configurada, então tentava usar URL padrão (provavelmente localhost:8085) que não funcionava no ambiente Kubernetes.

**Correção aplicada (Helm/Config):** Adicionada env var `NASP_ADAPTER_URL=http://trisla-nasp-adapter:8085` no deployment do Decision Engine via `kubectl patch deployment`.

## Evidências (logs)

### Adapter

**Logs do Decision Engine após correção:**
```
2025-12-21 17:02:22,016 - src.main - INFO - 🚀 Encaminhando ACCEPT para NASP Adapter: decision_id=dec-184d1edd-006b-45b9-9221-3d0e3bc5896e
2025-12-21 17:02:22,017 - nasp_adapter_client - INFO - 🔷 [NSI] Instanciando NSI: nsi-184d1edd-643a79 (serviceProfile=eMBB)
2025-12-21 17:02:22,022 - httpx - INFO - HTTP Request: POST http://trisla-nasp-adapter:8085/api/v1/nsi/instantiate "HTTP/1.1 404 Not Found"
2025-12-21 17:02:22,023 - nasp_adapter_client - ERROR - ❌ Erro HTTP ao chamar NASP Adapter: Client error '404 Not Found' for url 'http://trisla-nasp-adapter:8085/api/v1/nsi/instantiate'
```

**Status:** ✅ Conectividade resolvida. ❌ Endpoint inexistente.

**Endpoints disponíveis no NASP Adapter (via OpenAPI):**
- `POST /api/v1/nasp/actions` - Executa ação real no NASP (I-07)
- `GET /api/v1/nasp/metrics` - Coleta métricas reais do NASP (I-07)
- `GET /health` - Health check

**Endpoint chamado pelo Decision Engine:** `POST /api/v1/nsi/instantiate` (❌ não existe)

### SLA-Agent

**Logs coletados:** Nenhuma atividade relacionada ao ACCEPT encontrada, pois o fluxo não progrediu além do NASP Adapter devido ao erro 404.

### BC-NSSMF

**Logs coletados:** Nenhuma atividade relacionada ao ACCEPT encontrada, pois o fluxo não progrediu além do NASP Adapter devido ao erro 404.

### Besu

**RPC Status:**
- Chain ID: 0x539
- Block Number: 0x0
- Status: ✅ RPC funcional

## Resultado final

**Status:** ⚠️ **PARCIAL - Conectividade Resolvida, Mas Contrato REST Incorreto**

### ✅ Sucessos

1. **Conectividade ao NASP Adapter:** RESOLVIDA
   - Decision Engine agora alcança o NASP Adapter via `http://trisla-nasp-adapter:8085`
   - Não há mais "All connection attempts failed"

2. **ACCEPT obtido:** Decision Engine gerou decisão ACCEPT internamente (decision_id: dec-184d1edd-006b-45b9-9221-3d0e3bc5896e)

3. **Infraestrutura:** Todos os pods READY, Besu RPC funcional

### ❌ Limitação Identificada

**Problema de Contrato REST:**
- Decision Engine chama: `POST /api/v1/nsi/instantiate`
- NASP Adapter oferece: `POST /api/v1/nasp/actions`
- **Incompatibilidade de endpoint impede progressão do fluxo**

Como o protocolo S6.13D proíbe alteração de contratos REST, esta limitação não foi corrigida nesta fase.

### Próximos passos

1. **Alinhar contrato REST:** Decision Engine e NASP Adapter precisam usar o mesmo endpoint
   - Opção A: Decision Engine usar `/api/v1/nasp/actions`
   - Opção B: NASP Adapter implementar `/api/v1/nsi/instantiate`
   - Opção C: Criar alias/mapeamento no NASP Adapter

2. **Após alinhamento:** Revalidar fluxo completo até blockchain

3. **Validar SLA-Agent → BC-NSSMF → Besu:** Apenas após NASP Adapter funcionar corretamente

---

**Documento gerado em:** 2025-12-21  
**Protocolo:** S6.13D - FIX NASP Adapter + Blockchain E2E  
**Status:** ⚠️ **PARCIAL - Conectividade Resolvida, Contrato REST Incorreto**

