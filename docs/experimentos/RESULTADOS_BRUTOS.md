# Resultados Brutos - Experimentos TriSLA

## Data de Execução
ter 23 dez 2025 15:52:46 -03

## Cenários Executados

### C1 — eMBB
- **C1.1**: 5 SLAs simultâneos
- **C1.2**: 10 SLAs simultâneos

### C2 — URLLC
- **C2.1**: 3 SLAs simultâneos
- **C2.2**: 6 SLAs simultâneos

### C3 — mMTC
- **C3.1**: 10 SLAs simultâneos
- **C3.2**: 20 SLAs simultâneos

## Métricas Coletadas

### Dados Brutos
- dados_brutos/embb_5_metrics.csv
- dados_brutos/embb_10_metrics.csv
- dados_brutos/urllc_3_metrics.csv
- dados_brutos/urllc_6_metrics.csv
- dados_brutos/mmtc_10_metrics.csv
- dados_brutos/mmtc_20_metrics.csv

### Tabelas Consolidadas
- tabelas/TABELA_1_TEMPO_DECISAO.md
- tabelas/TABELA_2_TAXA_RENEG.md
- tabelas/TABELA_3_ESCALABILIDADE.md

### Rastreabilidade
- TRACEABILITY_MATRIX.md

## Quantidade de Amostras

- **Total de SLAs submetidos**: 54
  - eMBB: 15 (5 + 10)
  - URLLC: 9 (3 + 6)
  - mMTC: 30 (10 + 20)

## Observações Técnicas

- Todos os SLAs foram processados com sucesso
- Sistema manteve estabilidade durante todos os cenários
- Tempo de resposta consistente (~0.15s) independente da carga
- Taxa de RENEG observada em todos os cenários (comportamento esperado do sistema)

**Nota**: Este documento contém apenas dados brutos, sem interpretação ou análise conclusiva.
