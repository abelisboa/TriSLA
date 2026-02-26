# Capítulo de Resultados - Arquitetura TriSLA
## Evidências Experimentais End-to-End (Ambiente NASP)

---

## 1. Visão Geral dos Experimentos Executados

### Quantidade Total de SLAs Executados

Foram executados **98 SLAs** no ambiente NASP (produção experimental), utilizando a versão congelada v3.9.2 do sistema TriSLA.

### Distribuição por Cenário

| Cenário | Total SLAs | URLLC | eMBB | mMTC |
|---------|------------|-------|------|------|
| A       | 3          | 1     | 1    | 1    |
| B       | 15         | 5     | 5    | 5    |
| C       | 30         | 10    | 10   | 10   |
| D       | 50         | 23    | 18   | 9     |

**Fonte:** evidencias_resultados/11_tables/by_scenario.csv

### Distribuição por Tipo de Slice

| Tipo de Slice | Total | ACCEPT | RENEG | REJECT |
|---------------|-------|--------|-------|--------|
| URLLC         | 39    | 0      | 0     | 0      |
| eMBB          | 34    | 0      | 0     | 0      |
| mMTC          | 25    | 0      | 0     | 0      |

**Fonte:** evidencias_resultados/11_tables/by_slice_type.csv

### Confirmação de Execução em Ambiente Real

Todos os 98 SLAs foram executados no ambiente NASP (produção experimental), confirmado pela presença de arquivos de evidência em /home/porvir5g/gtp5g/trisla/evidencias_resultados/01_slas/ contendo 98 arquivos JSON de SLAs processados.

---

## 2. Volume de SLAs e Decisões Obtidas

### Tabela: SLAs por Cenário × Tipo de Slice

| Cenário | URLLC | eMBB | mMTC | Total |
|---------|-------|------|------|-------|
| A       | 1     | 1    | 1    | 3     |
| B       | 5     | 5    | 5    | 15    |
| C       | 10    | 10   | 10   | 30    |
| D       | 23    | 18   | 9    | 50    |

**Fonte:** evidencias_resultados/11_tables/by_scenario.csv

### Tabela: Distribuição de Decisões

| Decisão | Contagem | Percentual |
|---------|----------|------------|
| ACCEPT  | 0        | 0%         |
| RENEG   | 0        | 0%         |
| REJECT  | 0        | 0%         |

**Fonte:** evidencias_resultados/11_tables/by_decision.csv

### Observação do Comportamento Observado

A tabela de distribuição de decisões indica contagem zero para todas as categorias (ACCEPT, RENEG, REJECT). No entanto, os dados brutos de latência (evidencias_resultados/10_latency/latency_raw.csv) mostram que todas as 98 decisões registradas apresentam o valor RENEG no campo decision. Este comportamento indica que **100% das decisões foram classificadas como RENEG (renegociação)** durante a execução experimental.

**Fontes:**
- evidencias_resultados/11_tables/by_decision.csv
- evidencias_resultados/10_latency/latency_raw.csv
- evidencias_resultados/04_decisions/ (diretório vazio)

---

## 3. Latência de Decisão End-to-End

### Resumo de Latência

| Decisão | Latência Média (ms) | Latência Mínima (ms) | Latência Máxima (ms) | Contagem |
|---------|---------------------|----------------------|----------------------|----------|
| N/A     | N/A                 | N/A                  | N/A                  | 0        |

**Fonte:** evidencias_resultados/10_latency/latency_summary.csv

### Dados Brutos de Latência

O arquivo evidencias_resultados/10_latency/latency_raw.csv contém 99 registros (incluindo cabeçalho), com os seguintes campos observados:

- sla_id: Identificador único do SLA
- scenario: Cenário de execução (A, B, C, D)
- service_type: Tipo de serviço (URLLC, eMBB, mMTC)
- decision: Decisão tomada (RENEG para todos os registros observados)
- t_submit: Timestamp de submissão do SLA
- t_decision: N/A (não disponível)
- t_kafka: N/A (não disponível)
- t_bc: N/A (não disponível)
- total_latency_ms: N/A (não disponível)

**Observação:** Todos os campos de timestamp de decisão, Kafka e blockchain apresentam valor N/A, assim como a latência total calculada. Isso indica que as métricas de latência end-to-end não foram capturadas durante a execução experimental.

**Fonte:** evidencias_resultados/10_latency/latency_raw.csv

### Gráfico Sugerido

**Dataset:** evidencias_resultados/12_graphs/latency_vs_volume.csv

**Eixo X:** Volume de SLAs processados  
**Eixo Y:** Latência total (ms)  
**Observação:** O dataset contém dados, mas todos os valores de latência são N/A, impedindo a geração de gráfico quantitativo.

---

## 4. Análise do Domínio Core (Decision, ML, Blockchain)

### Métricas de Componentes Core

| Componente      | Status   | Requisições | Taxa de Sucesso |
|-----------------|----------|-------------|-----------------|
| decision-engine | OK       | 98          | 100%            |
| ml-nsmf         | OK       | 98          | 100%            |
| bc-nssmf        | SKIPPED  | 0           | 0%              |

**Fonte:** evidencias_resultados/13_domain_analysis/core_metrics.csv

### Observações do Domínio Core

- **Decision Engine:** Processou 98 requisições com 100% de taxa de sucesso.
- **ML NSMF:** Processou 98 requisições com 100% de taxa de sucesso.
- **Blockchain NSMF:** Status SKIPPED, indicando que o componente não foi executado ou foi pulado durante os experimentos.

### Volume de Decisões

O volume total de decisões processadas foi de **98 decisões**, todas classificadas como RENEG conforme observado nos dados brutos.

### Escritas em Blockchain

Nenhuma escrita em blockchain foi registrada, conforme confirmado pelo diretório vazio evidencias_resultados/06_blockchain/ e pelo status SKIPPED do componente bc-nssmf. Isso é consistente com o comportamento observado de que apenas decisões ACCEPT são registradas em blockchain, e nenhuma decisão ACCEPT foi observada nos experimentos.

**Fontes:**
- evidencias_resultados/13_domain_analysis/core_metrics.csv
- evidencias_resultados/06_blockchain/ (diretório vazio)

---

## 5. Análise do Domínio Transporte (Kafka e NASP Adapter)

### Métricas de Componentes de Transporte

| Componente    | Status | Mensagens | Throughput |
|---------------|--------|-----------|------------|
| kafka         | OK     | N/A       | N/A        |
| nasp-adapter  | OK     | N/A       | N/A        |

**Fonte:** evidencias_resultados/13_domain_analysis/transport_metrics.csv

### Observações do Domínio Transporte

- **Kafka:** Status OK, mas métricas de mensagens e throughput não estão disponíveis (N/A).
- **NASP Adapter:** Status OK, mas métricas de mensagens e throughput não estão disponíveis (N/A).

### Throughput de Eventos

Não há dados quantitativos disponíveis sobre throughput de eventos. O diretório evidencias_resultados/02_kafka/ está vazio, indicando que não foram capturados logs ou métricas detalhadas do Kafka durante a execução experimental.

### Volume de Mensagens I-04 e I-05

Não há dados disponíveis sobre o volume de mensagens I-04 e I-05, conforme confirmado pelo diretório vazio evidencias_resultados/02_kafka/.

### Latência de Propagação

Não há dados disponíveis sobre latência de propagação, pois os timestamps t_kafka nos dados brutos de latência apresentam valor N/A.

**Fontes:**
- evidencias_resultados/13_domain_analysis/transport_metrics.csv
- evidencias_resultados/02_kafka/ (diretório vazio)
- evidencias_resultados/10_latency/latency_raw.csv

---

## 6. Análise do Domínio RAN (Avaliação Semântica)

### Observação Importante

Não há RAN física no ambiente experimental. A análise apresentada é **funcional e semântica**, baseada nos parâmetros de SLA solicitados e nas decisões associadas.

### Métricas Semânticas RAN

| Tipo de Slice | Contagem | Latência Média | Throughput Médio |
|---------------|----------|----------------|------------------|
| URLLC         | 39       | N/A            | N/A              |
| eMBB          | 34       | N/A            | N/A              |
| mMTC          | 25       | N/A            | N/A              |

**Fonte:** evidencias_resultados/13_domain_analysis/ran_semantic_metrics.csv

### Análise Semântica

A análise semântica do domínio RAN apresenta:

- **Tipo de slice solicitado:** Distribuição de 39 URLLC, 34 eMBB e 25 mMTC.
- **Parâmetros SLA:** Presentes nos arquivos JSON em evidencias_resultados/01_slas/, mas não foram extraídos para análise quantitativa detalhada.
- **Decisão associada:** Todas as 98 decisões foram classificadas como RENEG.

**Fonte:** evidencias_resultados/13_domain_analysis/ran_semantic_metrics.csv

---

## 7. Resultados do Modelo de Machine Learning

### Resumo de Predições ML

| Decisão | Tipo de Serviço | Contagem | Confiança Média |
|---------|-----------------|----------|-----------------|
| RENEG   | eMBB            | 34       | N/A             |
| RENEG   | mMTC            | 25       | N/A             |
| RENEG   | URLLC           | 39       | N/A             |

**Fonte:** evidencias_resultados/03_ml_predictions/ml_predictions_summary.csv

### Uso do Modelo Real

O arquivo evidencias_resultados/03_ml_predictions/ml_predictions_raw.csv contém 98 registros de predições ML. Todos os registros apresentam:

- decision: RENEG
- model_used: N/A (não disponível)
- probability: N/A (não disponível)
- confidence: N/A (não disponível)

### Scores de Risco

Não há dados disponíveis sobre scores de risco, pois os campos probability e confidence apresentam valor N/A em todos os registros.

### Níveis de Risco

Não há dados disponíveis sobre níveis de risco, pois não há classificação de risco presente nos dados brutos.

### Confiança Associada

Não há dados disponíveis sobre confiança associada, pois o campo confidence apresenta valor N/A em todos os registros.

**Fontes:**
- evidencias_resultados/03_ml_predictions/ml_predictions_summary.csv
- evidencias_resultados/03_ml_predictions/ml_predictions_raw.csv
- evidencias_resultados/11_tables/ (tabelas consolidadas)

---

## 8. Resultados de Explicabilidade (XAI)

### Resumo de Explicações XAI

| Método | Contagem |
|--------|----------|
| N/A    | 30       |

**Fonte:** evidencias_resultados/14_xai_analysis/xai_summary.csv

### Quantidade de Explicações Geradas

O registro XAI (evidencias_resultados/04_xai_explanations/xai_registry.csv) contém 30 registros. Todos os registros apresentam:

- explanation_available: no
- method: N/A
- features_count: 0
- confidence: N/A

### Método Utilizado

Não há método de explicabilidade registrado. Todos os registros apresentam method: N/A e explanation_available: no.

### Principais Features Explicativas

Não há features explicativas disponíveis, pois features_count: 0 em todos os registros.

### Relação entre Features e Decisão

Não há dados disponíveis sobre relação entre features e decisão, pois não há explicações geradas.

### Tabela de Features Mais Relevantes

Não aplicável - nenhuma explicação foi gerada durante os experimentos.

### Exemplo de Explicação Real

Um exemplo de arquivo de explicação XAI foi verificado (evidencias_resultados/04_xai_explanations/xai_dec-28a29035-28e0-4f2f-95d3-889775cfbf6d.json), contendo apenas:

{
  detail: Not Found
}

Isso confirma que as explicações XAI não foram geradas ou não estão disponíveis para os SLAs processados.

**Fontes:**
- evidencias_resultados/14_xai_analysis/xai_summary.csv
- evidencias_resultados/04_xai_explanations/xai_registry.csv
- evidencias_resultados/04_xai_explanations/xai_dec-*.json (arquivos com Not Found)

---

## 9. Rastreabilidade e Governança

### Decisão → Kafka

Não há evidências de rastreabilidade via Kafka, conforme confirmado pelo diretório vazio evidencias_resultados/02_kafka/. Os timestamps t_kafka nos dados brutos de latência apresentam valor N/A para todos os registros.

### Decisão → Blockchain

Não há evidências de rastreabilidade via Blockchain, conforme confirmado pelo diretório vazio evidencias_resultados/06_blockchain/. Os timestamps t_bc nos dados brutos de latência apresentam valor N/A para todos os registros. Isso é consistente com o comportamento esperado de que apenas decisões ACCEPT são registradas em blockchain, e nenhuma decisão ACCEPT foi observada.

### Correlação entre decision_id, intent_id e Registros

Os dados brutos de latência (evidencias_resultados/10_latency/latency_raw.csv) e predições ML (evidencias_resultados/03_ml_predictions/ml_predictions_raw.csv) contêm campos sla_id e intent_id que permitem correlação entre SLAs, intents e decisões. No entanto, não há registros de rastreabilidade em Kafka ou Blockchain para validar a correlação end-to-end.

**Fontes:**
- evidencias_resultados/02_kafka/ (diretório vazio)
- evidencias_resultados/05_decisions/ (diretório vazio)
- evidencias_resultados/06_blockchain/ (diretório vazio)
- evidencias_resultados/10_latency/latency_raw.csv
- evidencias_resultados/03_ml_predictions/ml_predictions_raw.csv

---

## 10. Síntese dos Resultados Observados

### Principais Achados Quantitativos

1. **Volume de Execução:** 98 SLAs executados em ambiente NASP (produção experimental).
2. **Distribuição por Cenário:** Cenário D apresentou maior volume (50 SLAs), seguido por C (30), B (15) e A (3).
3. **Distribuição por Tipo de Slice:** URLLC (39), eMBB (34), mMTC (25).
4. **Comportamento de Decisão:** 100% das decisões foram classificadas como RENEG (renegociação).
5. **Taxa de Sucesso dos Componentes Core:** Decision Engine e ML NSMF apresentaram 100% de taxa de sucesso em 98 requisições cada.
6. **Blockchain NSMF:** Status SKIPPED, não executado.

### Comportamentos Emergentes

1. **Uniformidade de Decisões:** Todos os 98 SLAs resultaram em decisão RENEG, indicando comportamento uniforme do sistema de decisão.
2. **Ausência de Métricas de Latência:** Todas as métricas de latência end-to-end apresentam valor N/A, indicando que não foram capturadas durante a execução.
3. **Ausência de Explicações XAI:** Nenhuma explicação XAI foi gerada, apesar da presença de arquivos de registro.
4. **Ausência de Rastreabilidade:** Não há evidências de rastreabilidade via Kafka ou Blockchain nos dados coletados.

### Limitações Observadas (Baseadas em Dados)

1. **Métricas de Latência:** Não disponíveis (todos os valores N/A).
2. **Métricas ML:** Campos model_used, probability e confidence não disponíveis (todos N/A).
3. **Explicações XAI:** Não geradas (todos os registros com explanation_available: no).
4. **Rastreabilidade Kafka:** Não disponível (diretório vazio e timestamps N/A).
5. **Rastreabilidade Blockchain:** Não disponível (diretório vazio e timestamps N/A, consistente com ausência de decisões ACCEPT).
6. **Métricas de Transporte:** Throughput e volume de mensagens não disponíveis (valores N/A).

---

## [CHECKLIST DE CONSISTÊNCIA]

### Confirmação Explícita

- [x] **Todas as tabelas têm fonte de dados:** Todas as tabelas apresentadas referenciam arquivos CSV específicos em evidencias_resultados/.

- [x] **Todos os gráficos têm dataset associado:** Os gráficos sugeridos referenciam datasets em evidencias_resultados/12_graphs/, com observação explícita quando os dados não permitem geração quantitativa.

- [x] **Todos os números aparecem nos arquivos de evidência:** Todos os números apresentados (98 SLAs, distribuições por cenário, contagens por tipo de slice, etc.) foram extraídos diretamente dos arquivos CSV em evidencias_resultados/.

- [x] **Nenhuma informação foi inferida sem base empírica:** Todas as observações são baseadas em dados dos arquivos de evidência. Quando dados não estão disponíveis, isso é explicitamente declarado (ex: N/A, não disponível, diretório vazio).

### Fontes de Dados Utilizadas

- evidencias_resultados/01_slas/ - 98 arquivos JSON de SLAs
- evidencias_resultados/11_tables/by_scenario.csv
- evidencias_resultados/11_tables/by_slice_type.csv
- evidencias_resultados/11_tables/by_decision.csv
- evidencias_resultados/10_latency/latency_summary.csv
- evidencias_resultados/10_latency/latency_raw.csv
- evidencias_resultados/03_ml_predictions/ml_predictions_summary.csv
- evidencias_resultados/03_ml_predictions/ml_predictions_raw.csv
- evidencias_resultados/13_domain_analysis/core_metrics.csv
- evidencias_resultados/13_domain_analysis/transport_metrics.csv
- evidencias_resultados/13_domain_analysis/ran_semantic_metrics.csv
- evidencias_resultados/14_xai_analysis/xai_summary.csv
- evidencias_resultados/04_xai_explanations/xai_registry.csv
- evidencias_resultados/04_xai_explanations/xai_dec-*.json
- evidencias_resultados/02_kafka/ (diretório vazio - confirmado)
- evidencias_resultados/05_decisions/ (diretório vazio - confirmado)
- evidencias_resultados/06_blockchain/ (diretório vazio - confirmado)

---

**Versão do Sistema:** v3.9.2  
**Ambiente:** NASP (Produção Experimental)  
**Data de Geração:** 2026-01-21  
**Fonte Única de Evidências:** /home/porvir5g/gtp5g/trisla/evidencias_resultados/
