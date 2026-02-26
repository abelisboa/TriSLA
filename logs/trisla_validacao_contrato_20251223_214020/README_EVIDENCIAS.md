# Evidências - Solicitação Controlada de SLAs ACCEPT para Validação Contratual (TriSLA)

**Data de Execução:** ter 23 dez 2025 21:41:10 -03
**Ambiente:** NASP (node006)
**Diretório:** $OUTPUT_DIR

## Resumo Executivo

Foram submetidos 6 SLAs controlados conforme especificação:
- 2 eMBB
- 2 URLLC  
- 2 mMTC

## Resultados das Submissões

### Decisões Obtidas

| SLA | Tipo | Decisão | Status | BC-NSSMF | Hash Transação |
|-----|------|---------|--------|----------|----------------|
| eMBB #1 | eMBB | RENEG | RENEGOTIATION_REQUIRED | SKIPPED | null |
| eMBB #2 | eMBB | RENEG | RENEGOTIATION_REQUIRED | SKIPPED | null |
| URLLC #1 | URLLC | RENEG | RENEGOTIATION_REQUIRED | SKIPPED | null |
| URLLC #2 | URLLC | RENEG | RENEGOTIATION_REQUIRED | SKIPPED | null |
| mMTC #1 | mMTC | RENEG | RENEGOTIATION_REQUIRED | SKIPPED | null |
| mMTC #2 | mMTC | RENEG | RENEGOTIATION_REQUIRED | SKIPPED | null |

### Análise

**Decisão:** Todos os SLAs receberam decisão RENEG (renegociação necessária)

**Justificativa:** Rule rule-002 matched: sla_compliance < 0.9

**Comportamento do BC-NSSMF:** 
- Status: SKIPPED (não acionado)
- Motivo: Gate lógico preservado - BC-NSSMF só é acionado em decisões ACCEPT

**Blockchain:**
- Nenhuma transação registrada (esperado, pois não houve ACCEPT)
- Hash de transação: null para todos os SLAs

## Evidências Coletadas

### Arquivos Disponíveis

Para cada SLA foram coletados:
- `*_request.json` - Payload enviado
- `*_response.json` - Resposta completa da API
- `*_decision_engine.log` - Logs do Decision Engine (últimas 100 linhas)
- `*_bc_nssmf.log` - Logs do BC-NSSMF (últimas 100 linhas)
- `*_besu.log` - Logs do Besu (últimas 100 linhas)

### Observações Importantes

1. **Gate Lógico Funcionando:** O BC-NSSMF foi corretamente não acionado para decisões RENEG, conforme especificação.

2. **Decision Engine Operacional:** Todos os SLAs foram processados pelo Decision Engine, que aplicou as regras de decisão corretamente.

3. **BC-NSSMF em CrashLoopBackOff:** O pod BC-NSSMF estava em estado CrashLoopBackOff durante a execução, mas isso não afetou o comportamento esperado (não deveria ser acionado para RENEG).

4. **Parâmetros dos SLAs:** Os parâmetros foram definidos como "deliberadamente viáveis" no PROMPT, mas o Decision Engine determinou que sla_compliance < 0.9, resultando em RENEG.

## Próximos Passos Recomendados

1. **Ajustar Parâmetros dos SLAs:** Para obter decisões ACCEPT, pode ser necessário ajustar os parâmetros dos SLAs para valores mais conservadores ou verificar as regras do Decision Engine.

2. **Verificar Regras do Decision Engine:** Investigar a regra rule-002 e o cálculo de sla_compliance para entender por que os SLAs não atingiram o threshold de 0.9.

3. **Corrigir BC-NSSMF:** Resolver o problema do CrashLoopBackOff do BC-NSSMF para quando houver decisões ACCEPT.

4. **Repetir Experimento:** Após ajustes, repetir o experimento para validar o fluxo completo ACCEPT → Blockchain.

## Estrutura de Arquivos

```
$OUTPUT_DIR/
├── embb_01_request.json
├── embb_01_response.json
├── embb_01_decision_engine.log
├── embb_01_bc_nssmf.log
├── embb_01_besu.log
├── embb_02_*
├── urllc_01_*
├── urllc_02_*
├── mmtc_01_*
├── mmtc_02_*
└── README_EVIDENCIAS.md
```

---
**Status:** ✅ Execução concluída - Evidências coletadas conforme procedimento
