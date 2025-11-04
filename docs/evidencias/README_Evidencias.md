# Guia de Evidências — TriSLA

Este diretório armazena **todas as evidências visuais e textuais** relacionadas às Unidades de Trabalho (WUs) do projeto **TriSLA@NASP**.

---

## 📁 Estrutura Recomendada

```
docs/
└── evidencias/
    ├── WU-001_bootstrap/
    │   ├── WU-001_log_execucao.txt
    │   ├── WU-001_grafana.png
    │   └── WU-001_dashboard_prometheus.png
    ├── WU-002_contracts/
    │   ├── WU-002_teste_contratos.png
    │   ├── WU-002_resultados_pytest.txt
    │   └── WU-002_openapi_schema.png
    ├── WU-003_sem_csmf/
    │   ├── WU-003_nest_exemplo.png
    │   ├── WU-003_logs_sem_csmf.txt
    │   └── WU-003_pipeline.png
    └── README_Evidencias.md
```

Cada subpasta deve conter **evidências diretas** da execução da WU correspondente.

---

## 📜 Tipos de Evidência Aceitos

| Tipo | Extensão | Descrição |
|------|-----------|------------|
| **Logs de Execução** | `.txt`, `.log` | Saídas de terminal, CI/CD, Pytest, Fabric, Helm, etc. |
| **Capturas de Painéis** | `.png`, `.jpg`, `.svg` | Prints de Grafana, Prometheus, Jaeger, Fabric Explorer. |
| **Tabelas e Relatórios** | `.csv`, `.xlsx` | Métricas extraídas, SLOs, resultados de teste. |
| **Arquivos de Configuração** | `.yaml`, `.json` | Exportações de dashboards, manifests ou templates. |

---

## 🧩 Convenções de Nomenclatura

- Todos os arquivos devem começar com o **ID da WU**, por exemplo:  
  - `WU-003_pipeline.png`  
  - `WU-005_logs_fabric.txt`
- Os nomes devem ser descritivos e curtos (máx. 6 palavras).  
- Evite espaços e caracteres especiais.

---

## 🧾 Regras de Versionamento

1. **Evidências devem ser commitadas juntas com a WU correspondente.**  
   Exemplo: ao concluir `WU-002_contracts.md`, inclua também `docs/evidencias/WU-002_contracts/`.

2. **Nunca sobrescrever evidências antigas.**  
   Em caso de nova execução, criar arquivos com sufixo incremental (`_v2`, `_retest`, etc.).

3. **Arquivos grandes (>10 MB)** devem ser armazenados externamente (ex: Google Drive, Git LFS) e linkados no relatório da WU.

4. **Logs confidenciais** (tokens, senhas, IPs) devem ser anonimizados antes de commit.

---

## 📊 Exemplos de Evidências

### Exemplo 1 — Log de execução ML-NSMF

```
2025-10-20 14:32:15 | ML-NSMF | Predição executada | latência=42 ms | p99 | OK
2025-10-20 14:32:16 | ML-NSMF | SHAP explanation | feature=throughput | weight=0.43
```

### Exemplo 2 — Print de Dashboard Grafana

Arquivo: `WU-004_ml_nsmf_grafana.png`  
Legenda sugerida:
> Figura X – Dashboard ML-NSMF com métricas p99 e taxa de erro.  
> Fonte: Ambiente NASP / Prometheus (2025).

---

## 🧠 Boas Práticas

- Inserir uma seção “📊 Evidências” dentro de cada `STATE/WU-*.md`, com links para os arquivos deste diretório.  
- Nomear imagens e logs de forma consistente.  
- Manter um padrão visual e textual entre WUs.  
- Garantir que todos os logs sigam o formato do **Apêndice H** (timestamp | módulo | interface | métrica | valor | status | explicação).

---

📅 **Data:** 2025-10-16  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP – UNISINOS / Mestrado em Computação Aplicada
