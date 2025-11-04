# WU-001 — Bootstrap e Integração GitOps TriSLA@NASP
## Inicialização Oficial do Ambiente TriSLA no NASP

---

| Campo | Informação |
|--------|-------------|
| Data | 16/10/2025 |
| Responsável | Abel José Rodrigues Lisboa |
| Cluster | NASP – UNISINOS |
| Namespace | trisla-nsp |
| Objetivo | Estabelecer a integração GitOps entre o repositório TriSLA@NASP e o cluster Kubernetes, validando o ambiente e preparando o ciclo contínuo de implantação. |

---

## 🧩 1️⃣ Contexto e Objetivo

Esta Unidade de Trabalho (WU) estabelece o **Bootstrap GitOps** do projeto TriSLA no NASP.  
O objetivo é garantir que o cluster Kubernetes opere em sincronia com o repositório GitHub (`trisla-nasp`), permitindo versionamento, auditoria e implantação contínua das próximas fases.

---

## ⚙️ 2️⃣ Pré-Requisitos Confirmados

| Item | Status |
|------|---------|
| Cluster NASP validado (WU‑000) | ✅ Concluído |
| Namespace `trisla-nsp` ativo | ✅ Confirmado |
| Acesso SSH ao NASP | ✅ Operacional |
| Conexão GitHub disponível | ✅ Configurada |
| Helm e kubectl instalados | ✅ Validados |

---

## 🧱 3️⃣ Estrutura Inicial do Projeto no NASP

### 🔹 Clonar o repositório oficial
```bash
cd /home/porvir5g/
git clone https://github.com/abel-lisboa/trisla-nasp.git
cd trisla-nasp
```

### 🔹 Validar estrutura local
```bash
ls -R | head -n 50
```
**Esperado:** diretórios `PROMPTS/`, `STATE/`, `docs/`, `helm/`, `src/` e `automation/`

---

## 🔁 4️⃣ Configuração do GitOps Local

### 🔹 Configurar usuário Git (se necessário)
```bash
git config --global user.name "Abel Lisboa"
git config --global user.email "abel.lisboa@unisinos.br"
```

### 🔹 Atualizar e sincronizar o repositório
```bash
git pull origin main
git status
```

### 🔹 Confirmar branches
```bash
git branch -a
```
**Padrão:** `main` para produção, `feature/WU-*` para unidades de trabalho em andamento.

---

## 📦 5️⃣ Configuração de Helm Repositories

### 🔹 Adicionar e atualizar repositório Helm local
```bash
helm repo add trisla https://abel-lisboa.github.io/trisla-nasp/
helm repo update
helm search repo trisla
```

### 🔹 Validar contexto ativo
```bash
kubectl config current-context
kubectl config set-context --current --namespace=trisla-nsp
kubectl get ns | grep trisla
```

**Resultado esperado:**
```
trisla-nsp   Active
```

---

## 🚀 6️⃣ Teste de Conectividade e Preparação para Deploy

### 🔹 Verificar pods atuais
```bash
kubectl get pods -n trisla-nsp
```
Deve retornar lista **vazia** neste momento.

### 🔹 Validar cluster geral
```bash
helm list -A
kubectl get nodes -o wide
```

### 🔹 Registrar evidência
```bash
kubectl get all -A > docs/evidencias/WU-001_bootstrap/nasp_state_after_bootstrap.txt
```

---

## 🧩 7️⃣ Estrutura de CI/CD Inicial (GitHub Actions)

Criar (ou confirmar) workflow no GitHub:
```
.github/workflows/deploy.yml
```

Exemplo mínimo:
```yaml
name: Deploy TriSLA
on:
  workflow_dispatch:
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Helm Deploy
        run: |
          helm upgrade --install trisla ./helm/trisla -n trisla-nsp
```

---

## 📊 8️⃣ Evidências e Logs

Salvar os seguintes artefatos:
```
docs/evidencias/WU-001_bootstrap/
 ├── nasp_state_after_bootstrap.txt
 ├── helm_repo_status.txt
 ├── kubectl_context.txt
 └── git_sync_log.txt
```

---

## ✅ 9️⃣ Critérios de Aceitação

| Critério | Status Esperado |
|-----------|------------------|
| Repositório GitHub clonado e sincronizado | ✅ |
| Namespace `trisla-nsp` confirmado ativo | ✅ |
| Repositório Helm atualizado | ✅ |
| CI/CD configurado e funcional | ✅ |
| Snapshot salvo em evidências | ✅ |

---

## 🧾 10️⃣ Conclusão

A execução da WU‑001 estabelece a base **GitOps** para o projeto TriSLA@NASP.  
O cluster está sincronizado com o repositório, preparado para receber as próximas Unidades de Trabalho (WU‑002 e WU‑003).

📅 **Data:** 16/10/2025  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
