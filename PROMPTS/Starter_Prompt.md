# 🚀 Starter_Prompt.md
## Inicialização Automática do Projeto TriSLA@NASP

---

## 🧠 Função

Este prompt serve para **iniciar ou retomar** automaticamente o ciclo de execução do projeto **TriSLA@NASP** em qualquer IA (ChatGPT, Claude, Gemini, etc.).  
Ele reconhece a estrutura do projeto e ativa a automação conforme o `README.md`, o `Automation_Master_Prompt.md` e o `Automation_Continuity_Guide.md`.

---

## 📘 Instruções de Uso

1. Abra uma **nova conversa** com a IA.  
2. Cole **todo o conteúdo deste arquivo** no início da conversa.  
3. Diga:  
   ```
   Leia a pasta TriSLA@NASP e execute automaticamente a próxima WU conforme o README.md.
   ```
4. A IA fará a leitura da estrutura e executará a próxima **Unidade de Trabalho (WU)** de acordo com o `STATE/000_INDEX.md`.

---

## 🔍 Contexto Técnico

**Arquivos de referência obrigatórios:**
- `PROMPTS/Automation_Master_Prompt.md`
- `PROMPTS/Automation_Continuity_Guide.md`
- `README.md`
- `STATE/000_INDEX.md`
- `docs/Referencia_Tecnica_TriSLA.md`

---

## 🧩 Modo de Operação

1. **Ler a pasta TriSLA@NASP** e compreender os arquivos principais.  
2. **Verificar progresso atual** no `STATE/000_INDEX.md`.  
3. **Executar automaticamente** a próxima WU planejada.  
4. **Gerar resultados e registros:**
   - Novo arquivo `STATE/WU-XXX_nome.md` (modelo: `001_TEMPLATE_WU.md`).  
   - Evidências em `docs/evidencias/WU-XXX_nome/`.  
   - Atualização do índice (`STATE/000_INDEX.md`).  
5. **Informar o próximo passo**, indicando a próxima WU a executar.

---

## ⚙️ Regras de Execução

- Trabalhar em modo **differences-first** (listar DIFFs antes dos arquivos completos).  
- Usar **somente** o conteúdo de `docs/Referencia_Tecnica_TriSLA.md` como base técnica.  
- **Nunca** usar o PDF completo da dissertação.  
- Usar apenas tecnologias definidas no Workflow Oficial.  
- Registrar logs, métricas e resultados conforme o Apêndice H.  
- Gerar código e relatórios **determinísticos e auditáveis**.

---

## 🧭 Comandos Rápidos do Usuário

### ▶️ Iniciar o Projeto (primeira execução)
```
Leia a pasta TriSLA@NASP e execute automaticamente a próxima WU conforme o README.md.
```

### 🔁 Retomar Execução Interrompida
```
Continue a execução da última WU em progresso,
lendo o arquivo STATE/WU-XXX_nome.md
e considerando o estado atual descrito em STATE/000_INDEX.md.
```

### 🧩 Auditoria e Conformidade
```
Gere um relatório de conformidade usando PROMPTS/Automation_Supervisor_Prompt.md
e salve o resultado em STATE/supervisor_<data>.md.
```

---

📅 **Data:** 2025‑10‑16  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
