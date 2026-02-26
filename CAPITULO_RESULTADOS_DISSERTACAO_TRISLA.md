# Capítulo de Resultados - Arquitetura TriSLA
## Evidências Experimentais End-to-End (Ambiente NASP)

---

## 1. Introdução ao Capítulo

Este capítulo apresenta os resultados experimentais obtidos a partir da execução de 98 SLAs (Service Level Agreements) no ambiente NASP (Network as a Service Platform), utilizando a arquitetura TriSLA versão v3.9.2 em modo de produção experimental. Os experimentos foram conduzidos com o objetivo de avaliar o desempenho end-to-end do sistema de decisão automatizada de SLAs, incluindo componentes de Machine Learning, explicabilidade (XAI), rastreabilidade via Kafka e registro imutável via Blockchain.

O escopo da avaliação abrange quatro cenários experimentais (A, B, C e D) com diferentes volumes de carga, distribuídos entre três tipos de slice de rede: URLLC (Ultra-Reliable Low-Latency Communication), eMBB (enhanced Mobile Broadband) e mMTC (massive Machine Type Communication). Todos os dados apresentados neste capítulo são rastreáveis a arquivos de evidência coletados durante a execução experimental, sem inferências ou estimativas.

**Versão do Sistema:** v3.9.2  
**Ambiente:** NASP (Produção Experimental)  
**Data de Execução:** 2026-01-21  
**Fonte de Evidências:** /home/porvir5g/gtp5g/trisla/evidencias_resultados/

---

## 2. Visão Geral dos Experimentos Executados

### 2.1. Quantidade Total de SLAs

Foram executados **98 SLAs** no ambiente NASP, utilizando a versão congelada v3.9.2 do sistema TriSLA. A confirmação da execução é validada pela presença de 98 arquivos JSON de SLAs processados no diretório evidencias_resultados/01_slas/.

**Fonte:** evidencias_resultados/01_slas/ (98 arquivos JSON)

### 2.2. Distribuição por Cenário Experimental

Os experimentos foram organizados em quatro cenários com volumes crescentes de carga:

| Cenário | Total SLAs | URLLC | eMBB | mMTC |
|---------|------------|-------|------|------|
| A       | 3          | 1     | 1    | 1    |
| B       | 15         | 5     | 5    | 5    |
| C       | 30         | 10    | 10   | 10   |
| D       | 50         | 23    | 18   | 9     |

**Fonte:** evidencias_resultados/11_tables/by_scenario.csv

### 2.3. Distribuição por Tipo de Slice

A distribuição dos 98 SLAs por tipo de slice de rede é apresentada na Tabela 2.2:

| Tipo de Slice | Total | Percentual |
|---------------|-------|------------|
| URLLC         | 39    | 39.8%      |
| eMBB          | 34    | 34.7%      |
| mMTC          | 25    | 25.5%      |

**Fonte:** evidencias_resultados/11_tables/by_slice_type.csv

### 2.4. Pipeline End-to-End Avaliado

O pipeline end-to-end avaliado compreende os seguintes componentes:

1. **Submissão de SLA:** Recepção e validação inicial do SLA
2. **Decision Engine:** Motor de decisão principal
3. **ML-NSMF:** Modelo de Machine Learning para predição de risco
4. **XAI:** Sistema de explicabilidade (SHAP)
5. **BC-NSSMF:** Componente de Blockchain (apenas para decisões ACCEPT)
6. **Kafka:** Sistema de mensageria para rastreabilidade
7. **NASP Adapter:** Adaptador para integração com a plataforma NASP

**Fonte:** evidencias_resultados/13_domain_analysis/core_metrics.csv

---

## 3. Volume de SLAs e Decisões

### 3.1. Tabela Consolidada: SLAs por Cenário × Tipo de Slice

| Cenário | URLLC | eMBB | mMTC | Total |
|---------|-------|------|------|-------|
| A       | 1     | 1    | 1    | 3     |
| B       | 5     | 5    | 5    | 15    |
| C       | 10    | 10   | 10   | 30    |
| D       | 23    | 18   | 9    | 50    |

**Fonte:** evidencias_resultados/11_tables/by_scenario.csv

### 3.2. Distribuição de Decisões Obtidas

A análise dos dados brutos de latência (evidencias_resultados/10_latency/latency_raw.csv) revela que todos os 98 SLAs processados resultaram em decisão **RENEG** (renegociação). A distribuição formal de decisões registrada é:

| Decisão | Contagem | Percentual |
|---------|----------|------------|
| ACCEPT  | 0        | 0%         |
| RENEG   | 98       | 100%       |
| REJECT  | 0        | 0%         |

**Fonte:** evidencias_resultados/10_latency/latency_raw.csv (análise dos 98 registros)

### 3.3. Distribuição de Decisões por Tipo de Slice

| Tipo de Slice | Total | ACCEPT | RENEG | REJECT |
|---------------|-------|--------|-------|--------|
| URLLC         | 39    | 0      | 39    | 0      |
| eMBB          | 34    | 0      | 34    | 0      |
| mMTC          | 25    | 0      | 25    | 0      |

**Fonte:** evidencias_resultados/11_tables/by_slice_type.csv (com correção baseada em latency_raw.csv)

### 3.4. Observações sobre o Padrão de Decisões

**Resultado Observado:** 100% das decisões foram classificadas como RENEG, indicando que o sistema identificou necessidade de renegociação para todos os SLAs submetidos durante os experimentos.

**Limitação Observada:** A ausência de decisões ACCEPT ou REJECT impede a avaliação do comportamento do sistema em cenários de aceitação direta ou rejeição completa. Este padrão uniforme pode estar relacionado aos parâmetros dos SLAs submetidos ou às configurações do modelo de Machine Learning.

---

## 4. Latência de Decisão End-to-End

### 4.1. Resumo de Latência

A análise dos dados de latência revela que as métricas de tempo end-to-end não foram capturadas durante a execução experimental. O arquivo de resumo de latência apresenta:

| Decisão | Latência Média (ms) | Latência Mínima (ms) | Latência Máxima (ms) | Contagem |
|---------|---------------------|----------------------|----------------------|----------|
| N/A     | N/A                 | N/A                  | N/A                  | 0        |

**Fonte:** evidencias_resultados/10_latency/latency_summary.csv

### 4.2. Análise dos Dados Brutos de Latência

O arquivo evidencias_resultados/10_latency/latency_raw.csv contém 98 registros (excluindo cabeçalho), com os seguintes campos:

- **sla_id:** Identificador único do SLA (presente em todos os registros)
- **scenario:** Cenário de execução (A, B, C, D) - presente em todos os registros
- **service_type:** Tipo de serviço (URLLC, eMBB, mMTC) - presente em todos os registros
- **decision:** Decisão tomada (RENEG para todos os 98 registros)
- **t_submit:** Timestamp de submissão do SLA - presente
- **t_decision:** Timestamp de decisão - **N/A em todos os registros**
- **t_kafka:** Timestamp de publicação no Kafka - **N/A em todos os registros**
- **t_bc:** Timestamp de registro no Blockchain - **N/A em todos os registros**
- **total_latency_ms:** Latência total calculada - **N/A em todos os registros**

**Fonte:** evidencias_resultados/10_latency/latency_raw.csv

### 4.3. Limitações Observadas na Métrica de Latência

**Limitação Crítica:** Todos os campos de timestamp de decisão, Kafka e Blockchain apresentam valor N/A, assim como a latência total calculada. Isso impede a análise quantitativa da latência end-to-end do sistema.

**Possíveis Causas:** (1) Os timestamps não foram capturados durante a execução; (2) Os componentes de rastreabilidade (Kafka, Blockchain) não registraram eventos; (3) A instrumentação de métricas de tempo não estava ativa.

### 4.4. Gráfico Sugerido

**Dataset:** evidencias_resultados/12_graphs/latency_vs_volume.csv

**Eixo X:** Volume de SLAs processados  
**Eixo Y:** Latência total (ms)  
**Status:** Não aplicável - todos os valores de latência são N/A, impedindo a geração de gráfico quantitativo.

---

## 5. Análise do Domínio Core

### 5.1. Métricas de Componentes Core

| Componente      | Status   | Requisições Processadas | Taxa de Sucesso |
|-----------------|----------|-------------------------|-----------------|
| decision-engine | OK       | 98                      | 100%            |
| ml-nsmf         | OK       | 98                      | 100%            |
| bc-nssmf        | SKIPPED  | 0                       | N/A             |

**Fonte:** evidencias_resultados/13_domain_analysis/core_metrics.csv

### 5.2. Decision Engine

**Resultados Observados:**
- **Volume de Decisões:** 98 decisões processadas
- **Taxa de Sucesso:** 100%
- **Status Operacional:** OK durante toda a execução experimental

**Fonte:** evidencias_resultados/13_domain_analysis/core_metrics.csv

### 5.3. ML-NSMF (Machine Learning Network Slice Management Function)

**Resultados Observados:**
- **Volume de Predições:** 98 predições realizadas
- **Taxa de Sucesso:** 100%
- **Status Operacional:** OK durante toda a execução experimental
- **Modelo Utilizado:** Não disponível nos dados coletados (campo model_used: N/A)

**Fonte:** evidencias_resultados/03_ml_predictions/ml_predictions_raw.csv

**Limitação Observada:** Os campos probability e confidence apresentam valor N/A em todos os 98 registros, impedindo a análise quantitativa da confiança e probabilidade das predições do modelo de Machine Learning.

### 5.4. BC-NSSMF (Blockchain Network Slice Management Function)

**Resultados Observados:**
- **Status:** SKIPPED (não executado)
- **Volume de Escritas:** 0
- **Causa:** Nenhuma decisão ACCEPT foi observada, e o componente Blockchain é executado apenas para decisões ACCEPT

**Fonte:** evidencias_resultados/13_domain_analysis/core_metrics.csv  
**Confirmação:** evidencias_resultados/06_blockchain/ (diretório vazio)

**Observação:** O comportamento observado é consistente com a especificação do sistema, que registra decisões em Blockchain apenas quando a decisão é ACCEPT.

### 5.5. Volume de Decisões Processadas

O volume total de decisões processadas pelo domínio Core foi de **98 decisões**, todas classificadas como RENEG conforme observado nos dados brutos.

---

## 6. Análise do Domínio Transporte

### 6.1. Métricas de Componentes de Transporte

| Componente    | Status | Mensagens Processadas | Throughput |
|---------------|--------|----------------------|------------|
| kafka         | OK     | N/A                  | N/A        |
| nasp-adapter  | OK     | N/A                  | N/A        |

**Fonte:** evidencias_resultados/13_domain_analysis/transport_metrics.csv

### 6.2. Kafka

**Resultados Observados:**
- **Status Operacional:** OK
- **Mensagens Processadas:** Não disponível (N/A)
- **Throughput:** Não disponível (N/A)

**Fonte:** evidencias_resultados/13_domain_analysis/transport_metrics.csv

**Limitação Observada:** O diretório evidencias_resultados/02_kafka/ está vazio, indicando que não foram capturados logs ou métricas detalhadas do Kafka durante a execução experimental. Os timestamps t_kafka nos dados brutos de latência apresentam valor N/A para todos os registros.

### 6.3. NASP Adapter

**Resultados Observados:**
- **Status Operacional:** OK
- **Mensagens Processadas:** Não disponível (N/A)
- **Throughput:** Não disponível (N/A)

**Fonte:** evidencias_resultados/13_domain_analysis/transport_metrics.csv

### 6.4. Volume de Mensagens I-04 e I-05

**Limitação Observada:** Não há dados disponíveis sobre o volume de mensagens I-04 e I-05, conforme confirmado pelo diretório vazio evidencias_resultados/02_kafka/.

### 6.5. Latência de Propagação

**Limitação Observada:** Não há dados disponíveis sobre latência de propagação, pois os timestamps t_kafka nos dados brutos de latência apresentam valor N/A para todos os registros.

---

## 7. Análise do Domínio RAN (Avaliação Semântica)

### 7.1. Observação Importante sobre RAN Física

**Aviso Metodológico:** Não há RAN física no ambiente experimental. A análise apresentada é **funcional e semântica**, baseada nos parâmetros de SLA solicitados e nas decisões associadas, sem avaliação de desempenho físico da rede de acesso rádio.

### 7.2. Métricas Semânticas RAN

| Tipo de Slice | Contagem | Latência Média | Throughput Médio |
|---------------|----------|----------------|------------------|
| URLLC         | 39       | N/A            | N/A              |
| eMBB          | 34       | N/A            | N/A              |
| mMTC          | 25       | N/A            | N/A              |

**Fonte:** evidencias_resultados/13_domain_analysis/ran_semantic_metrics.csv

### 7.3. Análise Semântica por Tipo de Slice

**URLLC (Ultra-Reliable Low-Latency Communication):**
- **Volume:** 39 SLAs (39.8% do total)
- **Decisões:** 39 RENEG (100% do tipo)
- **Parâmetros SLA:** Presentes nos arquivos JSON em evidencias_resultados/01_slas/

**eMBB (enhanced Mobile Broadband):**
- **Volume:** 34 SLAs (34.7% do total)
- **Decisões:** 34 RENEG (100% do tipo)
- **Parâmetros SLA:** Presentes nos arquivos JSON em evidencias_resultados/01_slas/

**mMTC (massive Machine Type Communication):**
- **Volume:** 25 SLAs (25.5% do total)
- **Decisões:** 25 RENEG (100% do tipo)
- **Parâmetros SLA:** Presentes nos arquivos JSON em evidencias_resultados/01_slas/

### 7.4. Impacto na Decisão

**Resultado Observado:** Todos os tipos de slice resultaram em decisão RENEG, sem distinção quantitativa observável nos dados coletados. A análise dos parâmetros SLA específicos (latência, throughput, confiabilidade) não foi extraída para análise quantitativa detalhada.

**Fonte:** evidencias_resultados/01_slas/ (98 arquivos JSON com parâmetros SLA completos)

---

## 8. Resultados do Modelo de Machine Learning

### 8.1. Resumo de Predições ML

| Decisão | Tipo de Serviço | Contagem | Confiança Média |
|---------|-----------------|----------|-----------------|
| RENEG   | eMBB            | 34       | N/A             |
| RENEG   | mMTC            | 25       | N/A             |
| RENEG   | URLLC           | 39       | N/A             |

**Fonte:** evidencias_resultados/03_ml_predictions/ml_predictions_summary.csv

### 8.2. Uso do Modelo Real vs Fallback

**Resultados Observados:**
- **Total de Predições:** 98 predições realizadas
- **Modelo Utilizado:** Não disponível (campo model_used: N/A em todos os registros)
- **Uso de Fallback:** Não determinável a partir dos dados coletados

**Fonte:** evidencias_resultados/03_ml_predictions/ml_predictions_raw.csv

**Limitação Observada:** O campo model_used apresenta valor N/A em todos os 98 registros, impedindo a determinação se o modelo de Machine Learning real foi utilizado ou se foi aplicado um mecanismo de fallback.

### 8.3. Distribuição de Scores e Confiança

**Limitação Observada:** Os campos probability e confidence apresentam valor N/A em todos os 98 registros de predições ML, impedindo a análise quantitativa de:
- Distribuição de scores de risco
- Níveis de confiança associados às predições
- Correlação entre confiança e decisão final

**Fonte:** evidencias_resultados/03_ml_predictions/ml_predictions_raw.csv

### 8.4. Observações sobre o Modelo de Machine Learning

**Resultado Observado:** O componente ML-NSMF processou 98 requisições com 100% de taxa de sucesso, indicando que o componente operou sem falhas durante a execução experimental.

**Limitação Observada:** A ausência de métricas de confiança, probabilidade e identificação do modelo utilizado impede a avaliação qualitativa e quantitativa do desempenho do modelo de Machine Learning.

---

## 9. Resultados de Explicabilidade (XAI)

### 9.1. Resumo de Explicações XAI

| Método | Contagem |
|--------|----------|
| N/A    | 30       |

**Fonte:** evidencias_resultados/14_xai_analysis/xai_summary.csv

### 9.2. Quantidade de Explicações Geradas

**Resultados Observados:**
- **Tentativas de Geração:** 30 SLAs tiveram tentativas de geração de explicação XAI
- **Explicações Disponíveis:** 0 (nenhuma explicação foi gerada com sucesso)
- **Taxa de Sucesso:** 0%

**Fonte:** evidencias_resultados/04_xai_explanations/xai_registry.csv

### 9.3. Método Utilizado

**Limitação Observada:** Não há método de explicabilidade registrado. Todos os 30 registros no arquivo xai_registry.csv apresentam:
- **explanation_available:** no
- **method:** N/A
- **features_count:** 0
- **confidence:** N/A

**Fonte:** evidencias_resultados/04_xai_explanations/xai_registry.csv

### 9.4. Features Mais Relevantes

**Limitação Observada:** Não há features explicativas disponíveis, pois features_count: 0 em todos os registros. Não é possível determinar quais features do modelo de Machine Learning são mais relevantes para as decisões tomadas.

### 9.5. Exemplos de Explicações Reais

**Análise de Arquivos de Explicação XAI:**

Foram verificados 30 arquivos JSON de explicação XAI no diretório evidencias_resultados/04_xai_explanations/. Todos os arquivos apresentam o mesmo conteúdo:



**Resultado Observado:** As explicações XAI não foram geradas ou não estão disponíveis para os SLAs processados. O endpoint de explicabilidade pode não estar disponível ou não estar funcional durante a execução experimental.

**Fonte:** evidencias_resultados/04_xai_explanations/xai_dec-*.json (30 arquivos verificados)

### 9.6. Observações sobre Explicabilidade

**Limitação Crítica:** A ausência completa de explicações XAI impede a avaliação da explicabilidade do sistema, que é um componente fundamental da arquitetura TriSLA. Não é possível determinar:
- Quais features são mais relevantes para as decisões
- Como o modelo de Machine Learning justifica suas predições
- A relação entre features e decisões finais

---

## 10. Rastreabilidade e Governança

### 10.1. Rastreabilidade via Kafka

**Resultados Observados:**
- **Status do Componente:** OK (conforme core_metrics.csv)
- **Evidências de Rastreabilidade:** Nenhuma

**Limitação Observada:** Não há evidências de rastreabilidade via Kafka, conforme confirmado por:
1. Diretório vazio: evidencias_resultados/02_kafka/
2. Timestamps t_kafka: N/A em todos os 98 registros de latência

**Fonte:** evidencias_resultados/02_kafka/ (diretório vazio)  
**Fonte:** evidencias_resultados/10_latency/latency_raw.csv (t_kafka: N/A)

### 10.2. Rastreabilidade via Blockchain

**Resultados Observados:**
- **Status do Componente:** SKIPPED (não executado)
- **Evidências de Rastreabilidade:** Nenhuma

**Limitação Observada:** Não há evidências de rastreabilidade via Blockchain, conforme confirmado por:
1. Diretório vazio: evidencias_resultados/06_blockchain/
2. Timestamps t_bc: N/A em todos os 98 registros de latência
3. Nenhuma decisão ACCEPT observada (Blockchain é executado apenas para ACCEPT)

**Fonte:** evidencias_resultados/06_blockchain/ (diretório vazio)  
**Fonte:** evidencias_resultados/10_latency/latency_raw.csv (t_bc: N/A)

**Observação:** O comportamento observado é consistente com a especificação do sistema, que registra decisões em Blockchain apenas quando a decisão é ACCEPT.

### 10.3. Correlação entre decision_id, intent_id e Registros

**Resultados Observados:**
- **Campos Disponíveis:** sla_id, intent_id presentes nos dados brutos
- **Correlação SLA → Decisão:** Possível via campos sla_id e intent_id
- **Correlação Decisão → Kafka:** Não possível (sem registros Kafka)
- **Correlação Decisão → Blockchain:** Não possível (sem registros Blockchain)

**Fonte:** evidencias_resultados/10_latency/latency_raw.csv  
**Fonte:** evidencias_resultados/03_ml_predictions/ml_predictions_raw.csv

**Limitação Observada:** Não há registros de rastreabilidade em Kafka ou Blockchain para validar a correlação end-to-end completa do pipeline de decisão.

### 10.4. Observações sobre Governança

**Resultado Observado:** Os dados brutos permitem rastreabilidade parcial via campos sla_id e intent_id, permitindo correlacionar SLAs submetidos com decisões tomadas.

**Limitação Observada:** A ausência de rastreabilidade via Kafka e Blockchain impede a validação completa da trilha de auditoria end-to-end do sistema.

---

## 11. Síntese dos Resultados

### 11.1. Principais Achados Quantitativos

1. **Volume de Execução:** 98 SLAs executados com sucesso no ambiente NASP (produção experimental)

2. **Distribuição por Cenário:**
   - Cenário A: 3 SLAs (3.1%)
   - Cenário B: 15 SLAs (15.3%)
   - Cenário C: 30 SLAs (30.6%)
   - Cenário D: 50 SLAs (51.0%)

3. **Distribuição por Tipo de Slice:**
   - URLLC: 39 SLAs (39.8%)
   - eMBB: 34 SLAs (34.7%)
   - mMTC: 25 SLAs (25.5%)

4. **Comportamento de Decisão:** 100% das decisões foram classificadas como RENEG (renegociação)

5. **Taxa de Sucesso dos Componentes Core:**
   - Decision Engine: 100% (98/98 requisições)
   - ML-NSMF: 100% (98/98 requisições)
   - BC-NSSMF: SKIPPED (não executado)

### 11.2. Padrões Observados

1. **Uniformidade de Decisões:** Todos os 98 SLAs resultaram em decisão RENEG, indicando comportamento uniforme do sistema de decisão independentemente do cenário ou tipo de slice.

2. **Confiabilidade Operacional:** Os componentes Decision Engine e ML-NSMF apresentaram 100% de taxa de sucesso, indicando estabilidade operacional durante a execução experimental.

3. **Ausência de Métricas de Latência:** Todas as métricas de latência end-to-end apresentam valor N/A, indicando que não foram capturadas durante a execução.

4. **Ausência de Explicações XAI:** Nenhuma explicação XAI foi gerada, apesar da presença de 30 tentativas documentadas.

5. **Ausência de Rastreabilidade:** Não há evidências de rastreabilidade via Kafka ou Blockchain nos dados coletados.

### 11.3. Consistência dos Dados

**Consistência Observada:**
- O número total de SLAs (98) é consistente entre todos os arquivos de evidência
- A distribuição por cenário e tipo de slice é consistente entre diferentes fontes de dados
- Todos os registros de decisão apresentam valor RENEG de forma consistente

**Inconsistências Observadas:**
- A tabela by_decision.csv apresenta contagem zero para todas as categorias, enquanto os dados brutos de latência mostram 98 decisões RENEG
- Esta inconsistência pode ser atribuída a um problema na geração da tabela consolidada

**Fonte para Verificação:** evidencias_resultados/11_tables/by_decision.csv vs evidencias_resultados/10_latency/latency_raw.csv

---

## 12. Limitações Observadas

As limitações apresentadas nesta seção são baseadas exclusivamente nas evidências coletadas, sem justificativas arquiteturais ou projeções futuras.

### 12.1. Limitações de Métricas de Latência

**Limitação:** Todas as métricas de latência end-to-end apresentam valor N/A, incluindo:
- Latência de submissão até decisão (t_submit → t_decision)
- Latência de decisão até Kafka (t_decision → t_kafka)
- Latência de decisão até Blockchain (t_decision → t_bc)
- Latência total calculada (total_latency_ms)

**Evidência:** evidencias_resultados/10_latency/latency_raw.csv (98 registros, todos com valores N/A)

**Impacto:** Impossibilidade de avaliar o desempenho temporal do sistema e a latência end-to-end do pipeline de decisão.

### 12.2. Limitações de Métricas de Machine Learning

**Limitação:** Os campos de métricas ML apresentam valor N/A em todos os registros:
- model_used: N/A (modelo utilizado não identificado)
- probability: N/A (probabilidade não disponível)
- confidence: N/A (confiança não disponível)

**Evidência:** evidencias_resultados/03_ml_predictions/ml_predictions_raw.csv (98 registros)

**Impacto:** Impossibilidade de avaliar a confiança, probabilidade e identificação do modelo de Machine Learning utilizado nas predições.

### 12.3. Limitações de Explicabilidade (XAI)

**Limitação:** Nenhuma explicação XAI foi gerada durante os experimentos:
- explanation_available: no (em todos os 30 registros)
- method: N/A
- features_count: 0
- confidence: N/A

**Evidência:** evidencias_resultados/04_xai_explanations/xai_registry.csv (30 registros)  
**Evidência:** evidencias_resultados/04_xai_explanations/xai_dec-*.json (30 arquivos com Not Found)

**Impacto:** Impossibilidade de avaliar a explicabilidade do sistema e determinar quais features são mais relevantes para as decisões.

### 12.4. Limitações de Rastreabilidade Kafka

**Limitação:** Não há evidências de rastreabilidade via Kafka:
- Diretório evidencias_resultados/02_kafka/ está vazio
- Timestamps t_kafka: N/A em todos os registros

**Evidência:** evidencias_resultados/02_kafka/ (diretório vazio)  
**Evidência:** evidencias_resultados/10_latency/latency_raw.csv (t_kafka: N/A)

**Impacto:** Impossibilidade de validar a trilha de eventos via Kafka e avaliar o throughput e latência de propagação de mensagens.

### 12.5. Limitações de Rastreabilidade Blockchain

**Limitação:** Não há evidências de rastreabilidade via Blockchain:
- Diretório evidencias_resultados/06_blockchain/ está vazio
- Timestamps t_bc: N/A em todos os registros
- Componente BC-NSSMF: SKIPPED (não executado)

**Evidência:** evidencias_resultados/06_blockchain/ (diretório vazio)  
**Evidência:** evidencias_resultados/10_latency/latency_raw.csv (t_bc: N/A)

**Impacto:** Impossibilidade de validar o registro imutável de decisões via Blockchain. Nota: Esta limitação é consistente com a ausência de decisões ACCEPT, que são as únicas registradas em Blockchain.

### 12.6. Limitações de Métricas de Transporte

**Limitação:** Métricas de transporte não estão disponíveis:
- Throughput: N/A
- Volume de mensagens: N/A
- Latência de propagação: N/A

**Evidência:** evidencias_resultados/13_domain_analysis/transport_metrics.csv

**Impacto:** Impossibilidade de avaliar o desempenho dos componentes de transporte (Kafka, NASP Adapter) e o volume de mensagens I-04/I-05 processadas.

### 12.7. Limitação de Diversidade de Decisões

**Limitação:** Todos os 98 SLAs resultaram em decisão RENEG, sem observação de decisões ACCEPT ou REJECT.

**Evidência:** evidencias_resultados/10_latency/latency_raw.csv (98 registros, todos com decision: RENEG)

**Impacto:** Impossibilidade de avaliar o comportamento do sistema em cenários de aceitação direta ou rejeição completa, e impossibilidade de validar o registro em Blockchain (que ocorre apenas para ACCEPT).

---

## Referências de Evidências

Todas as tabelas, números e observações apresentadas neste capítulo são rastreáveis aos seguintes arquivos de evidência:

### Diretórios de Evidência

- **SLAs Processados:** evidencias_resultados/01_slas/ (98 arquivos JSON)
- **Kafka:** evidencias_resultados/02_kafka/ (diretório vazio)
- **Predições ML:** evidencias_resultados/03_ml_predictions/
- **Explicações XAI:** evidencias_resultados/04_xai_explanations/
- **Decisões:** evidencias_resultados/05_decisions/ (diretório vazio)
- **Blockchain:** evidencias_resultados/06_blockchain/ (diretório vazio)
- **Status de Pods:** evidencias_resultados/07_pods_status/
- **Métricas:** evidencias_resultados/08_metrics/
- **Logs:** evidencias_resultados/09_logs/
- **Latência:** evidencias_resultados/10_latency/
- **Tabelas:** evidencias_resultados/11_tables/
- **Gráficos:** evidencias_resultados/12_graphs/
- **Análise por Domínio:** evidencias_resultados/13_domain_analysis/
- **Análise XAI:** evidencias_resultados/14_xai_analysis/
- **Integridade e Diagnósticos:** evidencias_resultados/15_integrity_and_diagnostics/

### Arquivos Específicos Referenciados

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
- evidencias_resultados/15_integrity_and_diagnostics/FINAL_GATE_REPORT.md

---

**Versão do Sistema:** v3.9.2  
**Ambiente:** NASP (Produção Experimental)  
**Data de Execução:** 2026-01-21  
**Data de Geração do Capítulo:** 2026-01-21  
**Fonte Única de Evidências:** /home/porvir5g/gtp5g/trisla/evidencias_resultados/
