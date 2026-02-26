# Cenário C4 — Stress Test (TriSLA)

## Pasta de Execução

OBRIGATÓRIO: Todos os comandos devem ser executados a partir de:
/home/porvir5g/gtp5g/trisla/experiments/C4_STRESS

## Objetivo

Avaliar o comportamento do sistema TriSLA sob carga extrema, identificando limites operacionais, degradação de performance e capacidade de recuperação.

## Subcenários

- C4.1: 100 SLAs simultâneos
- C4.2: 200 SLAs simultâneos
- C4.3: 500 SLAs simultâneos

## Métricas Coletadas

1. Taxa de falhas (%)
2. Tempo médio de decisão
3. Tempo end-to-end
4. Ocorrência de erros/timeouts
5. Códigos HTTP
6. Estabilidade dos pods

## Execução

ATENÇÃO: Execução deve ser feita MANUALMENTE quando autorizada.



## Arquivos Gerados

Para cada subcenário:
- results_C4_100.csv / results_C4_100.json
- results_C4_200.csv / results_C4_200.json
- results_C4_500.csv / results_C4_500.json

## Referências

- Script base: generators/submit_slas.py
- Coletor de métricas: collectors/prometheus_collector.py
- Coletor de logs: collectors/logs_collector.py
