# 📘 EXECUTION_READINESS_CHECKLIST.md  
**Guia de Preparação para Execução — TriSLA@NASP**  
Versão: 1.0 — Outubro/2025  
Autor: Abel Lisboa  

---

## 🎯 Objetivo

Garantir que o ambiente **NASP + Cursor + GitHub + IAs** esteja totalmente preparado antes da execução dos prompts de geração de código e implantação do projeto **TriSLA@NASP**.

---

## ✅ 1️⃣ Confirmação de Ambiente

Verifique cada item abaixo antes de iniciar a execução:

| Item | Comando / Ação | Resultado Esperado |
|------|------------------|--------------------|
| SSH NASP ativo | `ssh porvir5g@ppgca.unisinos.br` | Acesso sem senha |
| Cluster Kubernetes | `kubectl get nodes -o wide` | 2 nós “Ready” |
| Namespace TriSLA | `kubectl get ns | grep trisla` | `trisla-nsp Active` |
| Git sincronizado | `git pull origin main` | “Already up to date” |
| IA ativa no Cursor | Verificar barra lateral | `GPT-5-Pro active` |

💡 **Dica:** salve os resultados em `docs/evidencias/pre_exec_check.txt`.

---

## 🧭 2️⃣ Ordem Recomendada de Execução dos Prompts

| Etapa | Arquivo | Ação principal | Modelo sugerido |
|--------|----------|----------------|-----------------|
| 1️⃣ | `PROMPTS/PROMPT_MESTRE_UNIFICADO.md` | Inicializa sessão e contexto global | GPT-5-Pro |
| 2️⃣ | `STATE/WU-000_pre_check.md` | Verifica ambiente NASP e pré-requisitos | GPT-5-Pro |
| 3️⃣ | `STATE/WU-001_Bootstrap_TriSLA_NASP.md` | Prepara namespaces e secrets | GPT-5-Pro |
| 4️⃣ | `STATE/WU-002_Deploy_Core_Modules_TriSLA_NASP.md` | Implanta módulos TriSLA via Helm | GPT-5-Pro |
| 5️⃣ | `STATE/WU-003_Integration_NASP_Core_TriSLA.md` | Integra TriSLA ao NASP (API/gRPC) | GPT-5-Pro |
| 6️⃣ | `PROMPTS/Generate_UI_and_ControlLayer.md` | Gera UI, dashboards e backend | GPT-5-Pro |
| 7️⃣ | `STATE/WU-004_Tests_and_Observability_TriSLA.md` | KPIs e dashboards Grafana/Prometheus | Gemini 2.5 Pro |
| 8️⃣ | `STATE/WU-005_Avaliacao_Experimental_TriSLA.md` | Testes e validação experimental | Claude 3.7 Sonnet |

Após cada etapa:
```bash
git add .
git commit -m "WU-00X concluída"
git push origin main
```

---

## ⚙️ 3️⃣ Evitar Perda de Contexto (no Cursor)

- Não feche o chat durante execução de uma WU.  
- Se o contexto expirar, use `PROMPTS/Automation_Continuity_Guide.md`.  
- Reenvie `STATE/WU-00X_*.md` e `EXEC_CHECKLIST.md` ao retomar.  
- Prefira o modelo **GPT-5-Pro** para manter consistência entre arquivos.

---

## 🔐 4️⃣ Segurança e Limpeza no NASP

Antes de qualquer `helm install`:
```bash
kubectl get pods -A | grep trisla
```
Se houver pods antigos:
```bash
kubectl delete ns trisla trisla-ai trisla-blockchain trisla-integration trisla-monitoring trisla-semantic
```

> Use sempre o namespace `trisla-nsp` para novos deploys.

---

## 📊 5️⃣ Boas Práticas de Versionamento

- Commit após cada WU:
  ```bash
  git add .
  git commit -m "WU-002 concluída: Deploy TriSLA Core OK"
  git push origin main
  ```
- Evite `--force` em pushes.  
- Mantenha `EXEC_CHECKLIST.md` atualizado.  

---

## 🧠 6️⃣ Seleção Ideal de IAs no Cursor

| Ação | IA ideal | Motivo |
|-------|-----------|--------|
| Geração e refatoração de código | GPT-5-Pro | Precisão e estabilidade |
| Integração modular e raciocínio | Claude 3.7 Sonnet | Contexto entre módulos |
| Logs e observabilidade | Gemini 2.5 Pro | Capacidade de leitura massiva |
| Testes rápidos e ajustes | Gemini 2.5 Flash | Respostas imediatas |

**Modo “Auto” recomendado**, troque manualmente apenas em fases críticas (deploy e integração).

---

## 🧩 7️⃣ Verificação de Resultados

Após execução dos prompts:

```bash
kubectl get pods -n trisla-nsp
```

Todos os pods devem estar com status:
```
Running
```

Interface do TriSLA:
```
http://<NASP-IP>:32000/trisla
```

Evidências:
```
docs/evidencias/deploy_watch_log.json
docs/evidencias/validation_report.json
docs/UI_Architecture_TriSLA.md
```

---

## 🧾 8️⃣ Boas Práticas Finais

> Trate cada execução de prompt como um **experimento reprodutível**:  
> - Registre data, IA usada e commit Git.  
> - Salve logs e prints.  
> - Atualize evidências ao final de cada WU.

Essas informações fortalecem a **validade científica e técnica** da dissertação.

---

## 🚀 Pronto para Iniciar

✅ Todos os sistemas e arquivos estão prontos.  
👉 **Abra `PROMPTS/PROMPT_MESTRE_UNIFICADO.md` e inicie com GPT-5-Pro.**  
A IA conduzirá automaticamente a sequência de WUs conforme definido.

---

📘 *Fim do Guia — EXECUTION_READINESS_CHECKLIST.md*  
Versão oficial TriSLA@NASP — Preparação de Execução  
