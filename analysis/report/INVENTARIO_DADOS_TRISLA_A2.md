# Inventário de Dados — TriSLA A2

**Data de geração**: 2024-11-30  
**Ambiente**: NASP (node1)  
**Versão do Sistema**: TriSLA A2

---

## 📂 Arquivos JSONL Encontrados

### Diretório: `tests/results/`

| Arquivo | Tamanho | Linhas | Cenário Detectado | Observações |
|---------|---------|--------|-------------------|-------------|
| basic_20251130_190919.jsonl | 0 bytes | 0 | BASIC | Arquivo vazio |
| basic_20251130_195546.jsonl | 674 bytes | 1 | BASIC | ✅ Dados válidos |
| basic_20251130_195621.jsonl | 712 bytes | 1 | BASIC | ✅ Dados válidos |
| basic_20251130_195952.jsonl | 701 bytes | 1 | BASIC | ✅ Dados válidos |
| basic_20251130_201512.jsonl | 697 bytes | 1 | BASIC | ✅ Dados válidos |
| mixed_135_20251130_191056.jsonl | 0 bytes | 0 | MIXED_135 | Arquivo vazio |
| mixed_135_20251130_200103.jsonl | 95,278 bytes | 135 | MIXED_135 | ✅ Dados válidos |
| mixed_135_20251130_201622.jsonl | 94,742 bytes | 135 | MIXED_135 | ✅ Dados válidos |
| urlcc_batch_20251130_190939.jsonl | 0 bytes | 0 | URLLC_BATCH | Arquivo vazio |
| urlcc_batch_20251130_195955.jsonl | 14,138 bytes | 20 | URLLC_BATCH | ✅ Dados válidos |
| urlcc_batch_20251130_201515.jsonl | 14,061 bytes | 20 | URLLC_BATCH | ✅ Dados válidos |

**Total de arquivos**: 11  
**Arquivos com dados**: 8  
**Arquivos vazios**: 3

---

## 📊 Estrutura dos Dados JSONL

### Campos Identificados

Os registros JSONL contêm os seguintes campos:

- `intent_id`: Identificador único da intent (ex.: "basic-1764544512-15916")
- `status`: Status final ("accepted", "rejected", etc.)
- `nest_id`: Identificador do NEST gerado (ex.: "nest-basic-1764544512-15916")
- `message`: Mensagem de resultado (pode conter erros)

### Campos Ausentes (Normalizados)

Os seguintes campos não estão presentes nos JSONL originais, mas serão inferidos/normalizados:

- `service_type`: Inferido do nome do arquivo/cenário
- `scenario`: Detectado automaticamente (BASIC, URLLC_BATCH, MIXED_135)
- `latency_total_ms`: Não disponível nos dados originais
- `latency_sem_csmf_ms`: Não disponível nos dados originais
- `latency_ml_nsmf_ms`: Não disponível nos dados originais
- `latency_decision_engine_ms`: Não disponível nos dados originais
- `latency_bc_nssmf_ms`: Não disponível nos dados originais
- `timestamp_received`: Não disponível nos dados originais
- `timestamp_decision`: Não disponível nos dados originais
- `timestamp_completed`: Não disponível nos dados originais
- `bert` / `ber`: Não disponível nos dados originais

### Observações

1. **Campos de latência ausentes**: Os dados coletados não incluem métricas de latência por módulo. Isso pode ser resolvido:
   - Coletando métricas do Prometheus/Grafana
   - Instrumentando o código para logar timestamps
   - Usando traces do OpenTelemetry

2. **Status normalizado**: O campo `status` será normalizado para:
   - `ACCEPTED` (quando status = "accepted")
   - `REJECTED` (quando status = "rejected")
   - `ERROR` (quando houver erro na mensagem)

3. **Erros detectados**: Muitos registros contêm mensagens de erro relacionadas a:
   - Falha de conexão gRPC com Decision Engine
   - Status Code UNAVAILABLE
   - Connection refused

---

## 📁 Arquivos CSV Gerados

Após execução do `normalize_results.py`, os seguintes CSVs serão criados:

- `analysis/csv/merged_all_intents.csv` - Todos os intents consolidados
- `analysis/csv/merged_basic.csv` - Intents do cenário BASIC
- `analysis/csv/merged_urlcc_batch.csv` - Intents do cenário URLLC_BATCH
- `analysis/csv/merged_mixed_135.csv` - Intents do cenário MIXED_135

---

## ⚠️ Incoerências e Limitações

1. **Arquivos vazios**: 3 arquivos estão vazios (0 bytes). Possíveis causas:
   - Testes não executados completamente
   - Erro durante coleta de dados
   - Arquivos criados mas não populados

2. **Falta de métricas de latência**: Os dados não contêm informações de latência, limitando análises de desempenho.

3. **Erros de conexão**: Muitos registros indicam falhas de comunicação com Decision Engine via gRPC.

4. **Falta de timestamps**: Sem timestamps, não é possível analisar evolução temporal.

---

## 🔧 Recomendações

1. **Instrumentação adicional**: Adicionar logging de latências e timestamps nos módulos
2. **Coleta de métricas Prometheus**: Integrar com Prometheus para coletar métricas de latência
3. **Traces OpenTelemetry**: Usar OpenTelemetry para rastreamento distribuído
4. **Validação de dados**: Implementar validação antes de salvar JSONL

---

**Última atualização**: 2024-11-30





