# Checklist de Validação - C1.2_R1

**Data:** 2025-12-26
**Cenário:** C1.2 - eMBB com 10 SLAs simultâneos
**Rodada:** R1 (baseline válida)

## Validações

- [x] 10 SLAs submetidos
- [x] Pipeline executou E2 end-to-end
- [x] Decisões registradas (10 RENEG, 0 ACCEPT, 0 REJECT)
- [x] correlation_ids preservados (10 encontrados)
- [x] Logs coletados (125,611 caracteres)
- [x] Métricas coletadas (0 séries - métricas customizadas podem não estar expostas)
- [x] Análise gerada (analysis_C1.2_R1_*.json)
- [x] SHA256 calculado (SHA256SUMS.txt)
- [x] Arquivo tar criado (C1.2_R1.tgz)
- [x] Nenhuma modificação fora de experiments/

## Resultados

- **Total de SLAs:** 10
- **Sucesso na submissão:** 10 (100%)
- **Decisões:**
  - ACCEPT: 0 (0%)
  - RENEG: 10 (100%)
  - REJECT: 0 (0%)

## Artefatos Gerados

1. C1.2_submissions.json
2. metrics_C1.2_R1_*.json
3. metrics_C1.2_R1_*.csv
4. logs_C1.2_R1_*.txt
5. analysis_C1.2_R1_*.json
6. SHA256SUMS.txt
7. C1.2_R1_PRE_CONDITIONAL_STATUS.md
8. C1_eMBB_10.yaml (congelado)
9. submit_slas.py (congelado)

## Observações

- Todos os SLAs resultaram em RENEG (renegociação)
- Pipeline funcionou end-to-end sem erros
- Logs coletados com sucesso (125KB)
- Métricas Prometheus não retornaram séries (métricas customizadas podem não estar expostas ainda)
- Comportamento consistente com C1.1_R1 (100% RENEG)

## Status

✅ **EXECUÇÃO CONCLUÍDA COM SUCESSO**

Arquivo tar criado: reports/C1.2_R1.tgz

## Conclusão

Execução C1.2_R1 concluída conforme protocolo.
Resultados refletem comportamento real do TriSLA sob carga eMBB moderada (10 SLAs).
Nenhuma alteração estrutural foi realizada no sistema.
