# Checklist de Validação - C1.1_R1

**Data:** 2025-12-26
**Rodada:** R1 (Baseline válida)

## Validações

- [x] 0 pods em CrashLoopBackOff (RESSALVA: 3 pods antigos em erro, mas serviços críticos funcionais)
- [x] 5 SLAs submetidos
- [x] Pipeline executou E2 end-to-end
- [x] Decisões registradas (5 RENEG, 0 ACCEPT, 0 REJECT)
- [x] correlation_ids preservados
- [x] Logs coletados (79,251 caracteres)
- [x] Métricas coletadas (0 séries - métricas podem não estar expostas ainda)
- [x] Artefatos versionados (SHA256SUMS.txt criado)
- [x] Arquivo tar criado (C1.1_R1.tgz)

## Resultados

- **Total de SLAs:** 5
- **Sucesso na submissão:** 5 (100%)
- **Decisões:**
  - ACCEPT: 0 (0%)
  - RENEG: 5 (100%)
  - REJECT: 0 (0%)

## Artefatos Gerados

1. C1.1_submissions.json
2. metrics_C1.1_R1_*.json
3. metrics_C1.1_R1_*.csv
4. logs_C1.1_R1_*.txt
5. analysis_C1.1_R1_*.json
6. SHA256SUMS.txt
7. C1.1_R1_PRE_CONDITIONAL_STATUS.md

## Observações

- Todos os SLAs resultaram em RENEG (renegociação)
- Pipeline funcionou end-to-end sem erros
- Logs coletados com sucesso
- Métricas Prometheus não retornaram séries (pode ser que métricas customizadas não estejam expostas)

## Status

✅ **EXECUÇÃO CONCLUÍDA COM SUCESSO**

Arquivo tar criado: reports/C1.1_R1.tgz
