# 🧭 Guia de Melhores Práticas — Execução e Implantação TriSLA

## 📍 Contexto Atual

- **Laptop local:** utilizado para gerar código, executar prompts e interagir com IAs.  
- **Servidor NASP (UNISINOS):** ambiente remoto com cluster Kubernetes ativo.  
- Acesso remoto via:
  ```bash
  ssh porvir5g@ppgca.unisinos.br
  # (solicita senha)
  ssh node006  # acesso direto ao node1
  ```
- Cluster ativo:
  ```bash
  root@node1:~# kubectl get nodes
  NAME    STATUS   ROLES           AGE    VERSION
  node1   Ready    control-plane   352d   v1.28.15
  node2   Ready    control-plane   352d   v1.31.1
  ```

---

## 🧠 1️⃣ Ambiente de Desenvolvimento Local (Laptop)

### 🔹 Função
O laptop é o **centro de orquestração e integração IA ↔ NASP**.  
Todo o código, documentação e prompts são gerados e testados **localmente** antes do deploy remoto.

### 🔹 Ferramentas Recomendadas

| Tipo | Opção | Motivo |
|------|--------|--------|
| Editor de código | **Cursor** ou **VSCode** | Integração direta com ChatGPT/Claude e Markdown. |
| Terminal | **VSCode Terminal** ou **Warp** | Execução de Git, SSH e Helm integrada. |
| Versionamento | **Git + GitHub** | Controle completo de versões e histórico de WUs. |
| CLI Kubernetes | `kubectl`, `helm`, `k9s` | Testes e deploy remoto no NASP. |

> 💡 **Recomendação:** o Cursor com ChatGPT integrado é o ambiente ideal para executar os prompts e gerar código com rastreabilidade total.

---

## 🤖 2️⃣ Integração com IA (ChatGPT, Claude, Gemini)

### 🔹 Fluxo Ideal
1. Gerar e testar código localmente com IA.  
2. Validar artefatos (`YAML`, `Protobuf`, `Python`, `Helm`).  
3. Versionar no GitHub.  
4. Implantar no NASP via `helm` ou `kubectl`.

### 🔹 IAs Indicadas

| Fase | IA Recomendada | Motivo |
|------|----------------|--------|
| Desenvolvimento e geração de código | **ChatGPT (GPT‑5)** | Precisão técnica e integração com o Cursor. |
| Revisão e auditoria de WUs | **Claude 3.5 Sonnet** | Leitura contextual longa e análise de conformidade. |
| Interpretação contextual ampla | **Gemini 1.5 Pro** | Excelente para integração e raciocínio sobre múltiplos arquivos. |

> 🧩 Use ChatGPT para execução (Automation_Master_Prompt) e Claude para validação (Automation_Supervisor_Prompt).

---

## 💻 3️⃣ Fluxo de Desenvolvimento (Local → GitHub → NASP)

### 🔹 Etapas

1. **Gerar código localmente** com IA (usando os prompts oficiais).  
2. **Validar e testar** artefatos localmente:  
   ```bash
   pytest
   helm lint ./helm/sem_nsmf
   ```
3. **Versionar alterações**:
   ```bash
   git add .
   git commit -m "feat: WU‑003 sem_nsmf initial implementation"
   git push origin main
   ```
4. **Acessar o NASP via SSH**:
   ```bash
   ssh porvir5g@ppgca.unisinos.br
   cd ~/trisla-nasp
   git pull origin main
   ```
5. **Deployar módulo via Helm**:
   ```bash
   helm install sem-nsmf ./helm/sem_nsmf -n trisla-nsp
   kubectl get pods -n trisla-nsp
   ```

---

## ☁️ 4️⃣ Execução no NASP (Cluster Remoto)

### 🔹 Acesso SSH e Boas Práticas

1. **Nunca executar IA dentro do NASP.**  
   Use-as apenas localmente.  
2. Configure **autenticação SSH sem senha**:  
   ```bash
   ssh-keygen -t ed25519
   ssh-copy-id porvir5g@ppgca.unisinos.br
   ```
3. Operar como **usuário não-root** sempre que possível.  
4. Criar **namespace dedicado**:
   ```bash
   kubectl create namespace trisla-nsp
   ```

---

## 🔄 5️⃣ Integração GitHub ↔ NASP (GitOps)

### 🔹 Estrutura Recomendável

```
.github/workflows/
 ├── ci.yml          # Testes e lint locais
 ├── lint.yml        # Validação YAML/Helm/Python
 └── deploy.yml      # Deploy manual via Helm
```

### 🔹 Boas Práticas

- Manter `main` estável.  
- Usar branches `feature/WU‑###`.  
- Fazer PR e revisão antes de merge.  
- Automatizar deploy apenas após aprovação manual.

---

## 🧩 6️⃣ Melhores Práticas Gerais e Ajustes Recomendados

| Tema | Melhor Prática | Aplicação |
|------|----------------|------------|
| Execução de IA | Local via Cursor/VSCode | Nunca rodar IA no cluster. |
| Controle de versão | GitHub com branches curtos | Cada WU = 1 branch → 1 PR. |
| Fluxo de validação | IA gera → humano revisa → cluster aplica | Evita falhas. |
| Logs e evidências | Salvar em `docs/evidencias/` | Rastreabilidade ABNT. |
| Auditoria | Rodar `Automation_Supervisor_Prompt.md` semanalmente | Confirma coerência. |
| Backups | Sincronizar com Git (`pull/push`) | Segurança de dados. |

---

## 🔁 7️⃣ Fluxo Completo Resumido

```
[Laptop + IA]
   ↓  (Automation_Master_Prompt)
Gerar código/testes/docs
   ↓
Commit & Push → GitHub
   ↓
[NASP via SSH]
Pull + Helm/K8s Deploy
   ↓
Coletar métricas/logs
   ↓
[Laptop]
Executar Supervisor IA → Auditoria
```

---

## 🧱 8️⃣ Ajustes Sugeridos nos Prompts Existentes

| Arquivo | Ajuste Recomendado |
|----------|--------------------|
| `Automation_Master_Prompt.md` | Adicionar opção “modo offline” para uso sem cluster. |
| `Automation_Supervisor_Prompt.md` | Incluir verificação automática das pastas de evidência. |
| `Automation_Continuity_Guide.md` | Adicionar instrução de `git push/pull` após cada WU. |
| `README.md` | Incluir seção “Deploy no NASP” com comandos Helm. |
| `Workflow_Oficial_TriSLA_NASP.md` | Criar Fase 9 – *GitOps & Deploy Automático*. |

---

## 📊 9️⃣ Resumo Estratégico Final

| Função | Ferramenta | Local |
|---------|-------------|--------|
| Execução IA | Cursor + ChatGPT/Claude | Laptop |
| Edição/Versionamento | VSCode + Git | Laptop |
| Workflow/Controle | GitHub | Nuvem |
| Deploy | SSH + Helm/K8s | NASP |
| Auditoria | Claude (Supervisor) | Laptop |
| Evidências | `docs/evidencias/` | GitHub |

---

## ✅ Conclusão

A implantação ideal da **TriSLA no NASP** segue o modelo:

1. **Desenvolvimento local com IA.**  
2. **Versionamento e controle via GitHub.**  
3. **Deploy remoto via SSH/Helm.**  
4. **Auditoria contínua com IA supervisora.**

Esse fluxo garante um ambiente:

- 🔐 **Seguro:** IA nunca roda no cluster.  
- 🧾 **Rastreável:** GitOps e evidências.  
- ⚙️ **Simples:** Workflow unificado e documentado.  
- 🎓 **Científico:** Logs e métricas ABNT para dissertação.

---

📅 **Data:** 2025‑10‑16  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
