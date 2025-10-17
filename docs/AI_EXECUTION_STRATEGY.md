# 📘 AI_EXECUTION_STRATEGY.md  
**Guia Oficial de Execução de IAs — TriSLA@NASP**  
Versão: 1.0 — Outubro/2025  
Autor: Abel Lisboa  

---

## 🎯 Objetivo

Este documento define **a estratégia oficial de uso das IAs integradas no Cursor Pro** para o desenvolvimento, implantação e validação da arquitetura **TriSLA@NASP**, garantindo que cada modelo de IA seja utilizado na função ideal conforme suas capacidades técnicas.

---

## 🧠 Modelos Disponíveis no Cursor Pro (2025)

| Modelo | Provedor | Versão | Características principais |
|---------|-----------|---------|------------------------------|
| **GPT-5-Pro** | OpenAI | 2025.10 | Geração de código avançado, YAML, Helm, automação Python, integração com NASP. |
| **Claude 3.7 Sonnet** | Anthropic | 2025.09 | Raciocínio lógico e análise de dependências entre módulos. |
| **Gemini 2.5 Pro** | Google | 2025.09 | Capacidade de leitura de logs e JSON extensos, ideal para observabilidade e validação. |
| **Gemini 2.5 Flash** | Google | 2025.09 | Versão leve, rápida e econômica; ideal para testes incrementais. |

---

## ⚙️ Configuração Recomendada no Cursor

Acesse:
```
Settings → Models
```

Ative os seguintes modelos:
```
✅ gpt-5-pro
✅ claude-3.7-sonnet
✅ gemini-2.5-pro
⚙️ gemini-2.5-flash (opcional)
```

Em seguida, defina:
```
Default Model → Auto
```

Assim, o Cursor escolhe automaticamente o modelo mais adequado para cada tipo de tarefa, com base no contexto do arquivo aberto.

---

## 🔧 Como Funciona o Modo “Auto”

O **modo Auto** permite que o Cursor detecte automaticamente o tipo de conteúdo e o tipo de tarefa para selecionar o modelo ideal:

| Tipo de tarefa | IA selecionada automaticamente | Motivo |
|-----------------|-------------------------------|--------|
| Geração de código (Python, YAML, Helm) | GPT-5-Pro | Alta precisão sintática e compatibilidade com Kubernetes. |
| Raciocínio entre múltiplos arquivos ou módulos | Claude 3.7 Sonnet | Contexto amplo e lógica consistente. |
| Leitura de logs, JSONs ou métricas Prometheus | Gemini 2.5 Pro | Capacidade massiva de contexto. |
| Resposta rápida ou debug local | Gemini 2.5 Flash | Execução leve e imediata. |

---

## 🧩 Quando Usar Seleção Manual

O modo automático é eficiente, mas **determinadas etapas do TriSLA** exigem controle manual para garantir precisão técnica.

| Situação | Modelo recomendado | Motivo técnico |
|-----------|--------------------|----------------|
| Deploy e scripts de automação (Helm, YAML, Bash) | GPT-5-Pro | Garante estrutura e sintaxe corretas. |
| Integração entre módulos (semantic, ML, blockchain) | GPT-5-Pro | Coerência e compatibilidade entre APIs. |
| Análise e geração de relatórios técnicos | Claude 3.7 Sonnet | Melhor interpretação de dependências e resultados. |
| Leitura de logs e observabilidade NASP | Gemini 2.5 Pro | Leitura eficiente de dados e métricas volumosas. |
| Debug incremental rápido | Gemini 2.5 Flash | Baixa latência e custo reduzido. |

---

## 🧭 Estratégia por Etapa (WU)

| Etapa | Modo | IA recomendada | Função principal |
|--------|------|----------------|------------------|
| **WU-000 / WU-001** — Pré-check e Bootstrap | Auto | GPT-5-Pro | Verificação de ambiente e inicialização. |
| **WU-002** — Deploy Core Modules | Manual | GPT-5-Pro + Claude 3.7 | Geração de manifests, Helm charts e lógica intermodular. |
| **WU-003** — Integração NASP Core | Manual | GPT-5-Pro | Criação de scripts Python e APIs gRPC. |
| **WU-004** — Testes e Observabilidade | Manual | Gemini 2.5 Pro | Leitura e análise de logs e métricas. |
| **WU-005** — Avaliação Experimental | Manual | Claude 3.7 + Gemini 2.5 Pro | Interpretação de resultados e relatórios técnicos. |

---

## 💡 Boas Práticas

1. **Mantenha o modo “Auto” ativado** para tarefas gerais e interações rápidas.  
2. **Selecione manualmente a IA** ao iniciar WUs críticas (deploy, integração, validação).  
3. Sempre **indique no log ou checklist** qual IA foi usada para cada operação (documentar em `EXEC_CHECKLIST.md`).  
4. Durante execução contínua (via `PROMPT_MESTRE_UNIFICADO.md`), **verifique o modelo ativo no topo do chat**:
   ```
   🤖 GPT-5-Pro is active
   ```

---

## 🧾 Diagnóstico de Sessão

Para confirmar qual IA está sendo usada em tempo real:
1. Pressione `Ctrl + I` (Ask AI).  
2. No topo da janela, verifique:
   ```
   Agent: GPT-5-Pro (Auto)
   ```
3. Se desejar mudar manualmente, clique e escolha o modelo apropriado.

---

## ✅ Conclusão

A combinação ideal para execução do TriSLA@NASP é:

| Função | Modelo | Resultado |
|---------|---------|------------|
| Geração de código e automação | **GPT-5-Pro** | Precisão e estabilidade |
| Raciocínio entre módulos | **Claude 3.7 Sonnet** | Coerência e contexto |
| Observabilidade e auditoria | **Gemini 2.5 Pro** | Leitura e análise profunda |
| Testes rápidos | **Gemini 2.5 Flash** | Velocidade e leveza |

---

📌 **Resumo:**  
> Deixe o modo Auto ativado como padrão,  
> e troque manualmente apenas em etapas críticas (WU-002 → WU-005).  
