# TriSLA — campanha de evidências finais (fechamento)

Objetivo: executar uma única campanha reprodutível que gera CSV/Parquet, rastreio `kubectl` por módulo, gaps documentados, figuras mínimas e relatório final sob um diretório `evidencias_resultados_trisla_final/run_<UTC>/`.

## Scripts

| Script | Função |
|--------|--------|
| `scripts/e2e/trisla_full_closure_campaign.py` | Orquestra auditoria K8s, validação HTTP, matriz PRB × cenários, concorrência leve |
| `scripts/e2e/trisla_full_closure_validation.py` | Wrapper `--mode trace` |
| `scripts/e2e/trisla_xai_validation.py` | Wrapper `--mode xai` |
| `scripts/e2e/trisla_multidomain_snapshot.py` | Wrapper `--mode multi` |
| `scripts/generate_full_closure_figures.py` | Lê `processed/final_dataset.csv` e gera PNG + `FIGURE_SIGNAL_REPORT.md` |

## Variáveis de ambiente

- `TRISLA_BACKEND_URL` — API do portal-backend (ex. `http://localhost:18006`)
- `TRISLA_PRB_URL` — simulador PRB (ex. `http://localhost:18110`)
- `TRISLA_PRB_SCRAPE_WAIT_S` — espera após mudar PRB (default 45)
- `TRISLA_K8S_NAMESPACE` — default `trisla`
- `TRISLA_CLOSURE_REPS` — repetições por cenário (default 10 na campanha; use 1–2 para smoke)
- `TRISLA_CLOSURE_MODE` — alternativa ao `--mode` (`full` \| `trace` \| `xai` \| `multi`)

## Saídas principais (por run)

- `manifests/MANIFESTO.json`
- `processed/final_dataset.csv`, `trace_e2e.csv`, `multidomain_snapshots.csv`, `xai_validation.csv` (filtro)
- `processed/GAPS_REPORT.md`, `processed/FIGURE_SIGNAL_REPORT.md`
- `docs/FINAL_REPORT.md`
- `audit/`, `validation/`, `raw/`

Detalhe operacional: ver `docs/TRISLA_MASTER_RUNBOOK.md` (secção campanha de fechamento).
