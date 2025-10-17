# TASK_SPEC_TEMPLATE.md

[TASK SPEC]

**Work Unit (WU):** WU-<número> — <título curto da tarefa>  
**Objetivo:** Descrever de forma mensurável o objetivo técnico da unidade de trabalho.  

**Contexto mínimo:**
- Referência: Proposta_de_Dissertação_Abel-6.pdf (Cap. <X>, Apêndice <Y>).
- Arquivos-alvo: <lista de diretórios/arquivos envolvidos>.
- Interfaces I-* relevantes: <I-01, I-02, ...>.
- SLOs / Logs / Métricas aplicáveis.

**Entregáveis:**
- Código novo ou alterado (em conformidade com o Workflow Oficial TriSLA@NASP).
- Testes (contrato + unitário).
- Dashboards / Helm charts / documentação ABNT (se aplicável).
- Atualização em `STATE/` e `docs/`.

**Critérios de Aceitação:**
- Testes de contrato e unitários devem ser aprovados.
- Logs e observabilidade devem seguir formato do Apêndice H.
- Código deve respeitar padrões da proposta (sem alterar conceitos).
- Documentação ABNT atualizada com rastreabilidade completa.

**Observações:**
- Trabalhar com diferença mínima (diff-first).
- Escopo limitado ao definido no SESSION HEADER.
- Gerar resultados determinísticos e reprodutíveis.
