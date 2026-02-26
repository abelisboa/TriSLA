# AUDITORIA DEVOPS — EVIDÊNCIAS TriSLA v3.8.1

## Objetivo
Validar se as evidências coletadas são consistentes, reais e suficientes para:
- gerar resultados e gráficos
- permitir publicação (GitHub/GHCR) sem regressão

## Saídas
- GATE_FINAL_STATUS.txt
- Dataset para gráficos: OUT/DATASET_DECISOES.csv
- Relatórios por fase: FASE*.txt
- Listas: JSON_VALIDOS/INVALIDOS, SLA_IDS, erros, cross-check

## Local
- Evidências: /home/porvir5g/gtp5g/trisla/evidencias_resultados_v3.8.1
- Auditoria: /home/porvir5g/gtp5g/trisla/auditoria_evidencias_v3.8.1_20260119_194112

## Gate
[FASE 10] GATE FINAL
GATE_FINAL_STATUS=FAIL
FAIL_COUNT=6

## Resumo numérico
- Total arquivos: 16
- Vazios: 0
- JSON: 3 (inválidos: 0)
- Portal decision_ids: 3
- Kafka decision_ids (heurístico): 0
- ML fallback linhas: 6
- DE erros linhas: 28
- Dataset linhas: 1

## Principais artefatos
- CHECKSUMS_EVIDENCIAS.sha256
- OUT/DATASET_DECISOES.csv
- DE_ERRORS.txt
- ML_FALLBACK.txt
- SLA_FALHAS.txt
- CROSS_MISSING_IN_KAFKA.txt / CROSS_MISSING_IN_DE.txt
