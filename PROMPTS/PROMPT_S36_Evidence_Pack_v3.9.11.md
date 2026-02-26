# PROMPT_S36 — Evidence Pack v3.9.11 (Read-Only)

**Data:** 2026-01-28T23:56:20Z  
**Ambiente:** NASP (node006)  
**Namespace:** trisla  
**Versão:** v3.9.11 (congelada)

---

## Objetivo

Coletar evidências E2E completas do TriSLA v3.9.11 para produção de tabelas e gráficos científicos, sem realizar nenhuma alteração no sistema.

📌 **Este prompt é READ-ONLY**  
📌 **Não altera código, imagens, regras ou thresholds**  
📌 **Sistema está congelado em v3.9.11**

---

## Estrutura de Evidências



---

## FASE 1 — Coleta E2E Completa

### 1.1 Submissões Controladas

Submeter SLAs em cenários distintos:

**Cenário A:** 1 SLA por tipo (URLLC, eMBB, mMTC)  
**Cenário B:** 5 SLAs por tipo  
**Cenário C:** 10 SLAs por tipo  
**Cenário D:** Stress (≥50 SLAs mistos)

Para cada SLA:
- Salvar resposta completa em 
- Registrar no :
  - timestamp, scenario, type, sla_id, intent_id, decision, status, http_code
- Coletar evento Kafka correspondente (se disponível)

### 1.2 Extração de Dados ML

Para cada resposta:
- Extrair  completo
- Salvar em 
- Criar :
  - sla_id, risk_score, risk_level, viability_score, confidence
- Criar :
  - sla_id, risk_score, sla_compliance, real_metrics_count

### 1.3 Coleta XAI

Para cada SLA:
- Extrair explicação XAI completa
- Salvar em 
- Criar :
  - sla_id, feature_name, importance, domain
- Agrupar por domínio em 

---

## FASE 2 — Tabelas Científicas

### 2.1 Decisões por Cenário/Slice

Criar :

| Cenário | Tipo | Total | ACCEPT | RENEG | REJECT | Taxa ACCEPT |
|---------|------|-------|--------|-------|---------|-------------|
| A       | URLLC| 1     | X      | Y     | Z      | %          |
| A       | eMBB | 1     | ...    | ...   | ...    | ...        |
| ...     | ...  | ...   | ...    | ...   | ...    | ...        |

### 2.2 Métricas por Domínio

Criar :

| Domínio | Métricas Disponíveis | Métricas Usadas | Taxa Uso |
|---------|---------------------|-----------------|----------|
| RAN     | X                   | Y               | %        |
| Transporte | ...              | ...             | ...      |
| Core    | ...                 | ...             | ...      |

### 2.3 Variação de Compliance

Criar :

| Métrica | Mínimo | Máximo | Média | Desvio Padrão |
|---------|--------|--------|-------|---------------|
| risk_score | ... | ... | ... | ... |
| sla_compliance | ... | ... | ... | ... |
| real_metrics_count | ... | ... | ... | ... |

---

## FASE 3 — Gráficos Científicos

### 3.1 Latência por Slice/Cenário

**Arquivo:** 

- Eixo X: Tipo de slice (URLLC, eMBB, mMTC)
- Eixo Y: Latência (ms)
- Séries: Por cenário (A, B, C, D)
- Tipo: Box plot ou violin plot

### 3.2 CDF (Cumulative Distribution Function)

**Arquivo:** 

- Eixo X: Latência (ms)
- Eixo Y: Probabilidade acumulada (0-1)
- Séries: Por tipo de slice

### 3.3 Distribuição de Risco/Confiança

**Arquivo:** 

- Eixo X: risk_score (0-1)
- Eixo Y: Frequência
- Tipo: Histograma ou KDE
- Séries: Por risk_level (low, medium, high)

### 3.4 XAI Top Features

**Arquivo:** 

- Eixo X: Feature name
- Eixo Y: Importance (0-1)
- Tipo: Bar chart horizontal
- Top 10 features por importância média

### 3.5 Radar por Domínio

**Arquivo:** 

- Eixos: Domínios (RAN, Transporte, Core)
- Valores: Métricas disponíveis/usadas
- Tipo: Radar chart

### 3.6 Recursos por Módulo

**Arquivo:** 

- Eixo X: Módulo (decision-engine, ml-nsmf, etc.)
- Eixo Y: Uso de recursos (%)
- Séries: CPU, Memory
- Tipo: Stacked bar chart

---

## FASE 4 — Coleta de Métricas Reais

### 4.1 Métricas por Domínio

Criar :

- domain, metric_name, available, used, time_range_minutes

### 4.2 Disponibilidade de Métricas

Criar :

- sla_id, total_metrics_available, metrics_used_count, availability_rate

### 4.3 Uso de Métricas Reais

Criar :

- sla_id, real_metrics_count, real_metrics_list, time_range_minutes

---

## FASE 5 — Performance e Latência

### 5.1 Latência por Slice

Criar :

- slice_type, scenario, sla_id, latency_ms, p50, p95, p99

### 5.2 Latência por Cenário

Criar :

- scenario, total_slas, avg_latency_ms, min_latency_ms, max_latency_ms

### 5.3 Recursos por Módulo

Criar :

- module, cpu_usage_percent, memory_usage_percent, timestamp

---

## FASE 6 — Logs e Rastreabilidade

### 6.1 Logs do Decision Engine

Coletar logs recentes:


### 6.2 Logs do ML-NSMF

Coletar logs recentes:


### 6.3 Eventos Kafka

Se disponível, coletar eventos Kafka:


---

## FASE 7 — Relatório Final

Criar  contendo:

1. **Resumo Executivo**
   - Total de SLAs processados
   - Distribuição de decisões
   - Taxa de sucesso

2. **Análise ML**
   - Distribuição de risk_score
   - Variação de compliance
   - Uso de métricas reais

3. **Análise XAI**
   - Features mais importantes
   - Contexto por domínio
   - Correlação com decisões

4. **Performance**
   - Latência por slice/cenário
   - Uso de recursos
   - Disponibilidade de métricas

5. **Gráficos e Tabelas**
   - Referências a todos os gráficos gerados
   - Tabelas resumo

6. **Conclusões**
   - Validação do sistema v3.9.11
   - Evidências de funcionamento correto
   - Recomendações (se aplicável)

---

## FASE 8 — Checksums e Validação

Gerar checksums de todos os arquivos:



---

## Critérios de Sucesso

✅ Todas as evidências coletadas  
✅ Todas as tabelas geradas  
✅ Todos os gráficos gerados  
✅ Relatório final completo  
✅ Checksums validados  
✅ Nenhuma alteração no sistema realizada

---

## Notas Importantes

- Este prompt é **READ-ONLY** - não altera nada no sistema
- Sistema está **congelado em v3.9.11**
- Todas as evidências devem ser coletadas do estado atual
- Gráficos devem ser gerados usando Python/Matplotlib ou ferramenta similar
- Tabelas devem estar em formato Markdown para fácil leitura
- Todos os arquivos devem ter checksums para integridade

---

**Status:** Pronto para execução  
**Versão do Sistema:** v3.9.11 (congelada)  
**Data de Execução:** A definir
