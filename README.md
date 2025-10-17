# 🚀 Guia Rápido de Execução — TriSLA@NASP

Este guia explica **passo a passo** como abrir e executar o projeto **TriSLA@NASP** no ambiente **Cursor** ou **VSCode**, 
com integração IA (ChatGPT/Claude) e deploy real no **NASP (UNISINOS)**.

---

## 🧱 1️⃣ Estrutura do Projeto

```
trisla-nasp/
├── README.md
├── README_EXEC.md  ← (este guia)
├── PROMPTS/        ← Prompts de automação e geração IA
├── STATE/          ← Unidades de Trabalho (WU-000 → WU-005)
├── helm/           ← Helm charts da TriSLA
├── docs/evidencias/← Logs e resultados
├── src/            ← Códigos e scripts dos módulos
└── automation/     ← Scripts auxiliares
```

---

## ⚙️ 2️⃣ Pré-Requisitos

- Acesso SSH ao NASP:  
  ```bash
  ssh porvir5g@ppgca.unisinos.br
  ssh node006
  ```

- `kubectl`, `helm` e `git` instalados.  
- Contexto Kubernetes ativo:
  ```bash
  kubectl config current-context
  kubectl get nodes -o wide
  ```

- Namespace `trisla-nsp` já criado e ativo (verificado na WU-000).

---

## 🧠 3️⃣ Execução no Cursor

### Passo 1 – Abrir o projeto
- Abra o Cursor → “**Open Folder**” → selecione `trisla-nasp/`  
- Aguarde a indexação dos arquivos.

### Passo 2 – Abrir o prompt principal
- Abra o arquivo:
  ```
  PROMPTS/Prompt_Mestre_Automacao.md
  ```
- Esse é o ponto de partida para as WUs (Work Units).

### Passo 3 – Interagir com a IA
- Use **ChatGPT** ou **Claude** dentro do Cursor para executar as instruções contidas nas WUs:
  - Exemplo: copiar comandos do `STATE/WU-001_Bootstrap_TriSLA_NASP.md` e executar no terminal do NASP.
- Sempre **mantenha o mesmo arquivo aberto** para continuar o contexto da IA (evita perda de estado).

---

## 🧩 4️⃣ Fluxo de Execução

| Etapa | Arquivo | Ação Principal |
|-------|----------|----------------|
| 🟢 **WU-000** | `STATE/WU-000_pre_check.md` | Validar ambiente NASP e criar namespace `trisla-nsp`. |
| ⚙️ **WU-001** | `STATE/WU-001_Bootstrap_TriSLA_NASP.md` | Sincronizar repositório GitOps e helm repos. |
| 🏗️ **WU-002** | `STATE/WU-002_Deploy_Core_Modules_TriSLA_NASP.md` | Fazer deploy dos módulos SEM‑NSMF, ML‑NSMF, BC‑NSSMF. |
| 🔗 **WU-003** | `STATE/WU-003_Integration_NASP_Core_TriSLA.md` | Ativar interfaces O1, A1, E2, NWDAF e sincronizar com SMO. |
| 📊 **WU-004** | `STATE/WU-004_Tests_and_Observability_TriSLA.md` | Validar métricas, logs e KPIs via Prometheus/NWDAF. |
| 🧮 **WU-005** | `STATE/WU-005_Avaliacao_Experimental_TriSLA.md` | Executar cenários URLLC/eMBB/mMTC e gerar resultados. |

---

## 💾 5️⃣ Registro de Evidências

- Todas as evidências (logs, métricas, prints) devem ser salvas dentro de:
  ```
  docs/evidencias/<WU_nome>/
  ```
- Exemplo:
  ```bash
  kubectl get pods -A > docs/evidencias/WU-002_deploy_core/kubectl_get_pods.txt
  ```

- Ao final de cada execução, atualize o índice:
  ```bash
  nano STATE/000_INDEX.md
  ```
  e marque a WU como ✅ **Concluída**.

---

## 🧩 6️⃣ Boas Práticas de Execução

- **Sempre execute apenas uma WU por vez.**
- **Evite abrir novos prompts IA fora do arquivo atual.**
- **Salve e confirme (commit)** após cada WU bem-sucedida:
  ```bash
  git add .
  git commit -m "Finalizada WU-002 — Deploy Core"
  git push origin main
  ```
- Antes de qualquer upgrade Helm:
  ```bash
  helm list -A | grep trisla
  ```
- Logs importantes:
  ```bash
  kubectl get pods -n trisla-nsp
  kubectl logs -n trisla-nsp <pod_name>
  ```

---

## 📘 7️⃣ Dúvidas Frequentes

| Pergunta | Resposta |
|-----------|-----------|
| Posso pular uma WU? | ❌ Não. Elas são sequenciais e dependentes. |
| Posso executar tudo de uma vez? | ❌ Não. Execute e valide cada WU individualmente. |
| Onde ficam os resultados finais? | Em `docs/evidencias/WU-005_avaliacao/`. |
| O que fazer se perder conexão SSH? | Reabra e continue no mesmo WU e arquivo. |

---

## ✅ 8️⃣ Próximo Passo

Após concluir a WU-005:
- Consolide os dados e gráficos.  
- Gere o relatório técnico final (Capítulo 8 da dissertação).  
- Execute o script de conformidade:
  ```bash
  python automation/supervisor/supervisor_check.py
  ```

---

📅 **Última atualização:** 16/10/2025  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
