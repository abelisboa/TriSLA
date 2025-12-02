# Guia de Análise — TriSLA A2 Resultados Experimentais

## 📋 Visão Geral

Este diretório contém o pipeline completo de análise dos resultados experimentais do TriSLA A2, incluindo:

- Normalização de dados JSONL → CSV
- Cálculo de estatísticas (média, mediana, P95, P99)
- Geração de gráficos (CDF, BoxPlot, Time-series, Barras)
- Tabelas LaTeX para dissertação
- Relatório acadêmico completo (Capítulo 7)
- Dashboard Grafana para visualização

---

## 🚀 Fluxo de Trabalho Recomendado

### 1. Executar Testes no NASP

```bash
# No NASP (node1)
cd /home/porvir5g/gtp5g/trisla
# Executar testes e coletar resultados
```

### 2. Copiar JSONL para Repositório Local

```bash
# Copiar arquivos JSONL de tests/results/ do NASP para:
# ./tests/results/
```

### 3. Executar Pipeline Completo

```bash
cd analysis
python scripts/run_full_analysis.py
```

Este comando executa automaticamente:
- Normalização de dados (JSONL → CSV)
- Cálculo de estatísticas
- Geração de gráficos
- Criação de tabelas LaTeX
- Geração do relatório acadêmico

### 4. Importar Dashboard no Grafana

1. Acesse o Grafana (geralmente em `http://<grafana-url>:3000`)
2. Vá em **Dashboards** → **Import**
3. Selecione o arquivo: `monitoring/grafana/dashboards/trisla_a2_results.json`
4. **IMPORTANTE**: Substitua os placeholders de métricas pelos nomes reais do Prometheus
5. Salve o dashboard

### 5. Atualizar Capítulo na Dissertação

1. Abra `analysis/report/Capitulo_Resultados_TriSLA_A2.md`
2. Revise e ajuste o texto conforme necessário
3. Converta para LaTeX (usando pandoc ou manualmente)
4. Integre no documento principal da dissertação

---

## 📂 Estrutura de Diretórios

```
analysis/
├── scripts/
│   ├── normalize_results.py      # Normalização JSONL → CSV
│   └── run_full_analysis.py      # Pipeline completo
├── csv/
│   ├── merged_all_intents.csv     # Todos os intents consolidados
│   ├── merged_basic.csv           # Cenário BASIC
│   ├── merged_urlcc_batch.csv     # Cenário URLLC_BATCH
│   └── merged_mixed_135.csv       # Cenário MIXED_135
├── plots/
│   ├── latency_cdf_overall.png
│   ├── latency_boxplot_by_service_type.png
│   ├── status_distribution_bar.png
│   ├── pipeline_latency_stacked.png
│   └── bert_distribution_by_service_type.png (se disponível)
├── tables/
│   ├── estatisticas_gerais.csv / .tex
│   ├── estatisticas_por_service_type.csv / .tex
│   ├── estatisticas_por_modulo.csv / .tex
│   └── distribuicao_status.csv / .tex
└── report/
    ├── INVENTARIO_DADOS_TRISLA_A2.md
    ├── Capitulo_Resultados_TriSLA_A2.md
    └── README_ANALISE_TRISLA_A2.md (este arquivo)
```

---

## 🔧 Scripts Disponíveis

### `normalize_results.py`

**Função**: Converte arquivos JSONL para CSV normalizado

**Uso**:
```bash
cd analysis
python scripts/normalize_results.py
```

**Entrada**: `tests/results/*.jsonl`

**Saída**: 
- `analysis/csv/merged_all_intents.csv`
- `analysis/csv/merged_<cenario>.csv`

**Funcionalidades**:
- Detecta automaticamente cenários (BASIC, URLLC_BATCH, MIXED_135)
- Normaliza campos (status → status_final, etc.)
- Trata campos ausentes (latência, timestamps)
- Infere service_type do cenário

### `run_full_analysis.py`

**Função**: Pipeline completo de análise

**Uso**:
```bash
cd analysis
python scripts/run_full_analysis.py
```

**Processo**:
1. Chama `normalize_results.py` internamente
2. Carrega CSV consolidado
3. Calcula estatísticas
4. Gera gráficos PNG
5. Cria tabelas CSV/LaTeX
6. Gera relatório acadêmico

**Saídas**: Todas as saídas listadas na estrutura de diretórios acima

---

## 📊 Métricas Calculadas

### Estatísticas Gerais

- Total de intents processadas
- Latência total: média, mediana, desvio-padrão, P95, P99, mínimo, máximo

### Por Tipo de Serviço

- Mesmas estatísticas de latência
- Contagem de intents
- Taxa de sucesso (ACCEPTED / total)
- BERT médio e P95 (se disponível)

### Por Módulo do Pipeline

- Latência média e P95/P99 de:
  - SEM-CSMF
  - ML-NSMF
  - Decision Engine
  - BC-NSSMF

### Distribuição de Status

- Contagem absoluta e percentual de:
  - ACCEPTED
  - RENEGOTIATED
  - REJECTED
  - ERROR

### Erros por Módulo

- Top N tipos de erro
- Relação com tipo de serviço

---

## 📈 Gráficos Gerados

### 1. `latency_cdf_overall.png`

**Tipo**: CDF (Cumulative Distribution Function)  
**Descrição**: Distribuição acumulada de latência total  
**Uso**: Avaliar previsibilidade e outliers

### 2. `latency_boxplot_by_service_type.png`

**Tipo**: BoxPlot  
**Descrição**: Comparação de latência entre URLLC, eMBB, mMTC  
**Uso**: Identificar diferenças de desempenho por tipo de slice

### 3. `status_distribution_bar.png`

**Tipo**: Gráfico de Barras  
**Descrição**: Distribuição de status final  
**Uso**: Visualizar taxa de sucesso/rejeição

### 4. `pipeline_latency_stacked.png`

**Tipo**: Gráfico de Barras  
**Descrição**: Latência média por módulo  
**Uso**: Identificar gargalos do pipeline

### 5. `bert_distribution_by_service_type.png`

**Tipo**: Gráfico de Barras (se BERT disponível)  
**Descrição**: BERT médio por tipo de serviço  
**Uso**: Avaliar qualidade de sinal

---

## 📋 Tabelas LaTeX

Todas as tabelas são geradas em dois formatos:

- **CSV**: Para edição e revisão
- **LaTeX**: Pronto para uso na dissertação

### Tabelas Disponíveis

1. **estatisticas_gerais.tex**: Estatísticas gerais de latência
2. **estatisticas_por_service_type.tex**: Comparação por tipo de serviço
3. **estatisticas_por_modulo.tex**: Latência por módulo
4. **distribuicao_status.tex**: Distribuição de status

**Uso no LaTeX**:
```latex
\input{analysis/tables/estatisticas_gerais.tex}
```

---

## 📝 Relatório Acadêmico

### `Capitulo_Resultados_TriSLA_A2.md`

Relatório completo em Markdown, pronto para conversão para LaTeX.

**Estrutura**:
1. Introdução
2. Metodologia
3. Resultados Quantitativos
4. Análise por Tipo de Slice
5. Avaliação por Módulo
6. Discussão dos Resultados
7. Conclusão

**Conversão para LaTeX**:
```bash
pandoc analysis/report/Capitulo_Resultados_TriSLA_A2.md -o capitulo7.tex
```

---

## 🎛️ Dashboard Grafana

### Localização

`monitoring/grafana/dashboards/trisla_a2_results.json`

### Painéis Incluídos

1. **Latência Total por Tipo de Serviço (P95)**
2. **Distribuição de Status Final**
3. **Latência por Módulo (P95)**
4. **BERT por Tipo de Serviço** (se disponível)
5. **Tabela de Intents Recentes**
6. **Taxa de Requisições por Segundo**
7. **Taxa de Erro por Módulo**

### ⚠️ IMPORTANTE: Substituir Placeholders

O dashboard contém **placeholders** de métricas Prometheus. Antes de usar:

1. Identifique os nomes reais das métricas no Prometheus
2. Substitua no JSON:
   - `trisla_intent_latency_ms_bucket` → nome real do histograma
   - `trisla_intent_status_total` → nome real do counter
   - `trisla_bert_value` → nome real da métrica BERT (ou remova se não existir)
   - etc.

### Como Identificar Métricas Reais

```bash
# No Prometheus ou via API
curl http://prometheus:9090/api/v1/label/__name__/values | grep trisla
```

---

## 🔍 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'pandas'"

```bash
pip install pandas matplotlib seaborn numpy
```

### Arquivos JSONL vazios

Verifique se os testes foram executados corretamente no NASP e se os arquivos foram copiados completamente.

### Gráficos não gerados

Se matplotlib não estiver disponível, os gráficos serão pulados, mas CSV, tabelas e relatório ainda serão gerados.

### Métricas Prometheus não encontradas

O dashboard Grafana usa placeholders. Substitua pelos nomes reais das métricas ou ajuste as queries PromQL.

---

## 📚 Referências

- TriSLA A2 Documentation
- NASP Environment Guide
- Prometheus Query Language (PromQL)
- Grafana Dashboard JSON Schema

---

**Versão**: 1.0  
**Data**: 2024-11-30  
**Autor**: TriSLA Analysis Pipeline





