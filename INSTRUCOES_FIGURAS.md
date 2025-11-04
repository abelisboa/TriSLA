# Instruções para Criar Figuras no LaTeX

## Métodos Recomendados

### 1. Diagramas com TikZ (Recomendado)

```latex
\usepackage{tikz}
\usetikzlibrary{shapes,arrows,positioning,calc}

% Exemplo: Figura 1 - Arquitetura TriSLA
\begin{figure}[h]
\centering
\begin{tikzpicture}[
    block/.style={rectangle, draw, text width=3cm, text centered, 
                  minimum height=1cm, fill=blue!20},
    module/.style={rectangle, draw, text width=2.5cm, text centered,
                  minimum height=0.8cm, fill=green!20},
    arrow/.style={->, >=stealth, thick}
]

% Módulos TriSLA
\node[module] (sem) at (0,4) {SEM-NSMF};
\node[module] (ml) at (0,2) {ML-NSMF};
\node[module] (bc) at (0,0) {BC-NSSMF};

% NASP Platform
\node[block] (nasp) at (4,2) {NASP Platform};

% Conexões
\draw[arrow] (sem) -- (ml);
\draw[arrow] (ml) -- (bc);
\draw[arrow] (bc) -- (nasp);

\end{tikzpicture}
\caption{TriSLA Architecture}
\label{fig:architecture}
\end{figure}
```

### 2. Gráficos com PGFPlots

```latex
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}

% Exemplo: Figura 4 - Resultados Experimentais
\begin{figure}[h]
\centering
\begin{tikzpicture}
\begin{axis}[
    ybar,
    bar width=0.6cm,
    width=10cm,
    height=6cm,
    xlabel={Scenario},
    ylabel={Latency p99 (ms)},
    symbolic x coords={URLLC,eMBB,mMTC},
    xtick=data,
    ymin=0,
    ymax=100
]
\addplot coordinates {(URLLC,9.8) (eMBB,44.7) (mMTC,95.2)};
\end{axis}
\end{tikzpicture}
\caption{Latency p99 Comparison}
\label{fig:latency}
\end{figure}
```

### 3. Tabelas com booktabs

```latex
\usepackage{booktabs}

\begin{table}[h]
\centering
\caption{Experimental Results}
\label{tab:results}
\begin{tabular}{lccc}
\toprule
\textbf{Metric} & \textbf{URLLC} & \textbf{eMBB} & \textbf{mMTC} \\
\midrule
Latency p99 (ms) & 9.8 & 44.7 & 95.2 \\
Throughput (Mbps) & 52 & 1,285 & 18 \\
Reliability (\%) & 99.9992 & 99.97 & 98.7 \\
\bottomrule
\end{tabular}
\end{table}
```

---

## Ferramentas Alternativas

### 1. Draw.io / Diagrams.net
- Exportar como PDF ou PNG
- Importar no LaTeX com `\includegraphics`

### 2. PlantUML
- Gera diagramas a partir de código texto
- Integração com LaTeX via `minted` ou imagem

### 3. Python (Matplotlib/Seaborn)
- Criar gráficos programaticamente
- Exportar como PDF/EPS para LaTeX

---

## Arquivos de Figuras Necessários

1. **trisla_architecture.pdf** - Arquitetura de alto nível
2. **operational_flow.pdf** - Fluxo operacional 6 fases
3. **integration_interfaces.pdf** - Interfaces de integração
4. **experimental_results.pdf** - Gráficos de resultados
5. **xai_shap_importance.pdf** - Feature importance SHAP
6. **ml_decision_pipeline.pdf** - Pipeline de decisão ML
7. **blockchain_lifecycle.pdf** - Ciclo de vida blockchain
8. **slo_compliance_chart.pdf** - Gráfico compliance SLO
9. **comparison_matrix.pdf** - Matriz de comparação

---

## Checklist de Figuras

- [ ] Figura 1: Arquitetura TriSLA
- [ ] Figura 2: Fluxo Operacional (6 fases)
- [ ] Figura 3: Integração com NASP
- [ ] Figura 4: Resultados Experimentais (gráficos)
- [ ] Figura 5: XAI Feature Importance
- [ ] Figura 6: Pipeline ML-NSMF
- [ ] Figura 7: Blockchain Lifecycle
- [ ] Figura 8: SLO Compliance Chart
- [ ] Figura 9: Comparison Matrix
- [ ] Todas as figuras têm captions
- [ ] Todas as figuras são referenciadas no texto
- [ ] Formato adequado para Elsevier (PDF/EPS)





