# Análise Completa dos Resultados Experimentais TriSLA A2

## 📋 Descrição

Este módulo realiza a análise completa dos resultados experimentais do TriSLA A2, gerando:

- ✅ Conversão JSONL → CSV
- ✅ Estatísticas detalhadas (média, mediana, P95, P99)
- ✅ Gráficos (CDF, BoxPlot, Time-series, Barras, Heatmap)
- ✅ Tabelas LaTeX para dissertação
- ✅ Relatório acadêmico completo (Capítulo 7)

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- pip

### Dependências

```bash
pip install -r analysis/requirements.txt
```

Ou manualmente:

```bash
pip install pandas matplotlib seaborn numpy
```

## 📂 Estrutura de Diretórios

```
analysis/
├── analyze_trisla_a2_results.py  # Script principal
├── requirements.txt               # Dependências Python
├── README.md                      # Este arquivo
├── csv/                           # Arquivos CSV gerados
├── plots/                         # Gráficos PNG gerados
├── tables/                        # Tabelas LaTeX geradas
└── report/                        # Relatório acadêmico (Markdown)
```

## 🔧 Uso

### 1. Preparar arquivos de resultados

Coloque os arquivos JSONL no diretório `results/`:

```
results/
├── basic_*.jsonl
├── urlcc_*.jsonl
└── mixed_135_*.jsonl
```

### 2. Executar análise

```bash
python analysis/analyze_trisla_a2_results.py
```

### 3. Resultados gerados

Após a execução, os seguintes arquivos serão criados:

#### CSV (analysis/csv/)
- `basic_*.csv` - Dados normalizados do cenário básico
- `urlcc_*.csv` - Dados normalizados do cenário URLLC
- `mixed_135_*.csv` - Dados normalizados do cenário misto
- `comparison_table.csv` - Tabela comparativa

#### Gráficos (analysis/plots/)
- `cdf_latency_total.png` - CDF de latência total
- `boxplot_latency_total.png` - BoxPlot comparativo
- `timeseries_latency.png` - Evolução temporal
- `barplot_module_latency.png` - Latência por módulo

#### Tabelas LaTeX (analysis/tables/)
- `tabela1_estatisticas_gerais.tex` - Estatísticas gerais
- `tabela2_estatisticas_modulos.tex` - Estatísticas por módulo
- `tabela3_distribuicao_status.tex` - Distribuição de status
- `comparison_table.md` - Tabela comparativa (Markdown)

#### Relatório (analysis/report/)
- `Capitulo7_Resultados_TriSLA_A2.md` - Capítulo 7 completo

## 📊 Formato Esperado dos Dados JSONL

Cada linha do arquivo JSONL deve ser um objeto JSON válido com as seguintes chaves (ou variações):

```json
{
  "intent_id": "intent-001",
  "service_type": "URLLC",
  "timestamp_received": "2024-11-30T19:09:19Z",
  "timestamp_decision": "2024-11-30T19:09:20Z",
  "timestamp_completed": "2024-11-30T19:09:21Z",
  "latency_total_ms": 2000,
  "latency_sem_csmf_ms": 500,
  "latency_ml_nsmf_ms": 300,
  "latency_decision_engine_ms": 800,
  "latency_bc_nssmf_ms": 400,
  "status_final": "ACCEPTED",
  "module_error": null
}
```

O script normaliza automaticamente variações de nomes de chaves.

## 📈 Métricas Calculadas

### Por Cenário
- Total de intents processadas
- Latência total: média, mediana, P95, P99, máximo, mínimo
- Latência por módulo: SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF
- Distribuição de status: ACCEPTED, RENEGOTIATED, REJECTED, ERROR

### Comparações
- Comparação entre cenários (basic × urlcc × mixed135)
- Análise de gargalos por módulo
- Taxa de sucesso/erro

## 📝 Relatório Acadêmico

O relatório gerado (`Capitulo7_Resultados_TriSLA_A2.md`) inclui:

1. **Introdução ao Experimento**
   - Descrição dos cenários
   - Objetivos das métricas

2. **Metodologia**
   - Coleta de dados
   - Pipeline interno do TriSLA

3. **Resultados Quantitativos**
   - Tabelas estatísticas
   - Análise de percentis
   - Taxa de rejeições/renegociações

4. **Análise por Tipo de Slice**
   - URLLC
   - eMBB
   - mMTC

5. **Avaliação por Módulo**
   - SEM-CSMF
   - ML-NSMF
   - Decision Engine
   - BC-NSSMF

6. **Discussão dos Resultados**
   - Gargalos identificados
   - Escalabilidade
   - Previsibilidade
   - Comportamento sob carga

7. **Conclusão**
   - Resumo estatístico
   - Impacto no TriSLA
   - Trabalho futuro

## 🔍 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'matplotlib'"

```bash
pip install matplotlib seaborn numpy pandas
```

### Arquivos JSONL vazios

Verifique se os arquivos em `results/` contêm dados válidos. O script processará apenas arquivos não-vazios.

### Erro ao gerar gráficos

Se NumPy não estiver disponível, os gráficos serão pulados, mas CSV, tabelas e relatório ainda serão gerados.

## 📦 Exportação Final

Após gerar todos os resultados, você pode criar um ZIP:

```bash
# No Linux/Mac
zip -r analysis_complete_TrislaA2.zip analysis/

# No Windows (PowerShell)
Compress-Archive -Path analysis/* -DestinationPath analysis_complete_TrislaA2.zip
```

## 📚 Referências

- TriSLA A2 Documentation
- NASP Environment Guide
- LaTeX Table Formatting (booktabs package)

---

**Versão**: 1.0  
**Data**: 2024-11-30  
**Autor**: TriSLA Analysis Tool




