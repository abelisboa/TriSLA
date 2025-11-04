# 🤖 Automation_Master_Prompt.md
## Automação Completa do Projeto TriSLA
*(Executa o fluxo do README.md com base na estrutura real do repositório)*

---

## 🧠 Objetivo

Permitir que a IA (ChatGPT, Claude ou outra) **leia a estrutura da pasta TriSLA@NASP**, compreenda o estado atual do projeto e **execute automaticamente a próxima WU (Work Unit)** conforme descrito no arquivo `README.md`.

---

## 🚀 Instruções de Uso

1. Abra uma nova conversa com a IA.  
2. Cole **todo o conteúdo deste arquivo** no início da conversa.  
3. Garanta que a IA tenha acesso à pasta local `trisla-nasp/`.  
4. Diga:  
   > “Leia a pasta TriSLA@NASP e execute automaticamente a próxima WU conforme o README.md.”

A IA então irá:
- Ler `STATE/000_INDEX.md` para identificar a próxima WU a executar.  
- Carregar contexto do `README.md`, `docs/Referencia_Tecnica_TriSLA.md` e `Workflow_Oficial_TriSLA_NASP.md`.  
- Gerar código, testes ou documentação conforme o escopo.  
- Atualizar os arquivos de estado e evidências.

---

## 🔍 Contexto e Estrutura Esperada

```
trisla-nasp/
├── PROMPTS/
│   ├── MASTER_PROMPT.md
│   ├── SESSION_TEMPLATE.md
│   ├── TASK_SPEC_TEMPLATE.md
│   ├── CODEGEN_TEMPLATE.md
│   ├── TESTS_CONTRACT_TEMPLATE.md
│   └── HELM_DEPLOY_TEMPLATE.md
├── STATE/
│   ├── 000_INDEX.md
│   ├── 001_TEMPLATE_WU.md
│   └── (outros arquivos WU-*.md)
├── docs/
│   ├── Referencia_Tecnica_TriSLA.md
│   ├── evidencias/
│   │   └── README_Evidencias.md
├── Workflow_Oficial_TriSLA_NASP.md
├── TriSLA_NASP_Prompt.md
└── README.md
```

---

## 🧩 Passos Internos da IA

1. **Ler o índice (`STATE/000_INDEX.md`)**  
   - Identificar a WU com status “🔜 Planejado” ou “⏳ Em progresso”.  
   - Carregar fase e escopo do Workflow.

2. **Preparar contexto**  
   - Ler `README.md`, `docs/Referencia_Tecnica_TriSLA.md` e `Workflow_Oficial_TriSLA_NASP.md`.  
   - Carregar os templates de prompt adequados da pasta `PROMPTS/`.

3. **Executar a WU**  
   - Montar automaticamente:  
     `[SESSION HEADER]` + `[TASK SPEC]` + `[CODEGEN|TEST|HELM TEMPLATE]`.  
   - Gerar código, testes ou documentação conforme a fase.  
   - Aplicar logs e métricas (p99, erro, SLO).

4. **Gerar relatório de execução**  
   - Criar novo arquivo `STATE/WU-NNN_<nome>.md`, com base em `001_TEMPLATE_WU.md`.  
   - Preencher campos: contexto, ações, resultados, métricas, evidências, próximos passos.

5. **Atualizar progresso**  
   - Editar `STATE/000_INDEX.md` para marcar a WU como concluída.  
   - Criar pasta `docs/evidencias/WU-NNN_<nome>/` e salvar logs/prints.

6. **Anunciar o próximo passo**  
   - Indicar qual será a próxima WU planejada.  
   - Exibir resumo do progresso total (quantas WUs concluídas).

---

## ⚙️ Regras de Execução

- Trabalhar em modo **differences-first** (listar DIFFs antes dos arquivos).  
- **Nunca alterar** conteúdo conceitual do projeto.  
- Usar **apenas** tecnologias listadas na Referência Técnica.  
- Gerar código **determinístico e rastreável** (commits pequenos).  
- **Não sobrescrever** WUs anteriores — criar novas.  
- Seguir padrões ABNT e formato de logs (Apêndice H).  
- Utilizar `docs/Referencia_Tecnica_TriSLA.md` como **única fonte técnica**.

---

## 🧠 Ciclo de Automação

```
Detectar WU pendente
   ↓
Carregar contexto
   ↓
Gerar código/testes/docs
   ↓
Executar e registrar resultados
   ↓
Atualizar STATE/ e evidências
   ↓
Anunciar próxima WU
```

---

## 🔒 Regras de Segurança

- Não incluir chaves, tokens ou senhas reais.  
- Anonimizar logs antes de salvá-los.  
- Não enviar PDFs ou arquivos externos completos — apenas trechos relevantes.  
- Garantir que os arquivos gerados sejam compatíveis com Linux/UTF‑8.

---

## ✅ Resultado Esperado

Após a execução, a IA deve ter:

- Criado ou atualizado o arquivo `STATE/WU-NNN_<nome>.md`.  
- Atualizado o índice `STATE/000_INDEX.md`.  
- Gerado evidências em `docs/evidencias/WU-NNN_<nome>/`.  
- Informado o **próximo passo** (nova WU planejada).  
- Mantido rastreabilidade completa do ciclo.

---

📅 **Data:** 2025‑10‑16  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
