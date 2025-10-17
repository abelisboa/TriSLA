# 🤖 README_AUTOMATION.md  
## Módulo de Automação — TriSLA@NASP  
Versão: 1.0 — Outubro/2025  
Autor: Abel Lisboa  

---

## 🧩 Visão Geral

O módulo de automação do **TriSLA@NASP** fornece mecanismos de verificação, monitoramento e validação contínua da implantação do sistema em ambiente NASP (cluster Kubernetes).  
Ele é composto por **três scripts principais** localizados na pasta `automation/`.

| Script | Função principal |
|---------|------------------|
| `supervisor_check.py` | Verifica integridade da estrutura do projeto TriSLA. |
| `deploy_watcher.py` | Monitora o estado dos pods TriSLA nos namespaces Kubernetes. |
| `auto_validator.py` | Analisa logs de implantação e calcula métricas de disponibilidade. |

---

## ⚙️ 1️⃣ supervisor_check.py — Verificação Estrutural

### 🔍 Função
Garante que todas as pastas e arquivos obrigatórios do projeto estão presentes e acessíveis, conforme `PROJECT_STRUCTURE_CHECK.md`.

### ▶️ Comando
```bash
python automation/supervisor_check.py
