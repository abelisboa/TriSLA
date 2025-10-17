# ⚙️ Guia de Continuidade de Execução com IA — TriSLA@NASP

## 🎯 Objetivo
Este guia explica **como iniciar, pausar e continuar** o desenvolvimento do projeto **TriSLA@NASP** utilizando IAs (ChatGPT, Claude, Gemini, etc.) com o **Automation_Master_Prompt.md**.  
Ele garante que o projeto possa ser retomado a qualquer momento sem perda de progresso.

---

## 🧩 1️⃣ Primeira Execução — Inicialização do Projeto

### 🔹 Passos
1. Abra uma nova conversa com a IA.  
2. Cole o conteúdo completo do arquivo:  
   `PROMPTS/Automation_Master_Prompt.md`
3. Após colar, digite o comando:  
   ```
   Leia a pasta TriSLA@NASP e execute automaticamente a próxima WU conforme o README.md.
   ```
4. A IA irá:
   - Ler toda a estrutura do repositório.  
   - Localizar o arquivo `STATE/000_INDEX.md`.  
   - Identificar a **primeira WU planejada** (ex.: WU‑001).  
   - Iniciar automaticamente a execução dessa WU.

---

## 🧠 2️⃣ Durante a Execução

Durante o processo, a IA gera:

| Arquivo | Finalidade |
|----------|-------------|
| `STATE/WU-001_*.md` | Registro completo da WU executada. |
| `STATE/000_INDEX.md` | Atualização do status das WUs. |
| `docs/evidencias/WU-001_*/` | Logs, prints e métricas da execução. |

Quando a WU termina, a IA informa **a próxima WU a ser executada** (por exemplo, WU‑002).

---

## ⚠️ 3️⃣ Se a Execução for Interrompida

Caso a sessão encerre (por limite de tokens, queda de conexão, etc.), **não reinicie do zero**.

### 🔹 Passos para Continuar
1. Abra uma **nova conversa** com a IA.  
2. Cole novamente o conteúdo completo de:  
   `PROMPTS/Automation_Master_Prompt.md`
3. Em seguida, informe o ponto de retomada:  
   ```
   Continue a execução da última WU em progresso, lendo o arquivo:
   STATE/WU-001_bootstrap.md
   e considerando o estado atual descrito em STATE/000_INDEX.md.
   ```
4. A IA irá:
   - Ler o histórico da WU.  
   - Reconstruir o contexto.  
   - Retomar a execução exatamente do ponto onde parou.  
   - Atualizar o mesmo arquivo e logs.

> ⚙️ **Dica:** Sempre reutilize o mesmo arquivo de WU até que esteja concluído.  
> Só crie o próximo (ex.: `STATE/WU-002_*.md`) quando a WU atual for validada.

---

## 🧭 4️⃣ Regra Geral de Continuidade

| Situação | Ação |
|-----------|------|
| Primeira execução | Cole o `Automation_Master_Prompt.md` completo e execute o comando de leitura da pasta. |
| Sessão interrompida | Cole novamente o `Automation_Master_Prompt.md` e diga: “Continue a execução lendo STATE/WU‑XXX.md.” |
| Próxima WU | Após concluir a anterior, diga: “Inicie a WU‑00X conforme Workflow Oficial.” |
| Reexecução com falha | Peça: “Reanalise o log em docs/evidencias/WU‑XXX/ e corrija mantendo o mesmo STATE/WU‑XXX.md.” |

---

## 🧩 5️⃣ Uso do Supervisor

Após concluir pelo menos uma WU, execute:
```
Leia a pasta TriSLA@NASP e gere um relatório de conformidade usando:
PROMPTS/Automation_Supervisor_Prompt.md
```
A IA irá:
- Ler todos os arquivos `STATE/WU-*`.  
- Comparar com `STATE/000_INDEX.md` e `docs/Referencia_Tecnica_TriSLA.md`.  
- Gerar o relatório `STATE/supervisor_<data>.md` com alertas e recomendações.

---

## ✅ 6️⃣ Boas Práticas

- Nunca apague WUs antigas (elas representam marcos de progresso).  
- Sempre salve os arquivos locais após cada execução.  
- Se trocar de IA (ChatGPT → Claude), basta reenviar o `Automation_Master_Prompt.md` e pedir:  
  ```
  Leia a pasta TriSLA@NASP e retome a execução a partir do estado atual.
  ```
- Faça backup periódico das pastas `STATE/` e `docs/evidencias/`.  
- Documente toda execução de WU com prints e logs padronizados.

---

## 🧠 7️⃣ Exemplo Completo de Continuação

**Situação:** a IA parou no meio da WU‑002 (Contratos I‑01 a I‑07).

### No novo prompt, cole:
```
[Automation_Master_Prompt.md]
Continue a execução da WU‑002_contracts,
usando o arquivo STATE/WU‑002_contracts.md
e considerando o progresso atual descrito em STATE/000_INDEX.md.
Se necessário, consulte docs/Referencia_Tecnica_TriSLA.md.
```

A IA vai:
- Ler o arquivo da WU.  
- Retomar a geração de código/testes.  
- Atualizar o mesmo arquivo e logs.  
- Marcar a WU como concluída no índice.

---

## 🧾 8️⃣ Resultado Esperado

Seguindo este processo, você garante que:
- Nenhuma sessão perderá contexto.  
- O progresso será sempre rastreável.  
- A IA pode ser trocada ou pausada sem prejuízo.  
- Todos os resultados ficam registrados em `STATE/` e `docs/evidencias/`.

---

📅 **Data:** 2025‑10‑16  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
