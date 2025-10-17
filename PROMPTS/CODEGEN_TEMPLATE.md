# CODEGEN_TEMPLATE.md

[CODE GENERATION PROMPT]

Use este template quando desejar que a IA gere código novo ou altere código existente.

**Instruções:**  
1. Colar o `SESSION HEADER` e o `TASK SPEC`.  
2. Solicitar à IA que trabalhe em modo *differences-first*, ou seja:  
   - Liste primeiro os **DIFFs** de cada arquivo.  
   - Depois, apresente os **arquivos completos** (novos/alterados).  
3. A IA deve incluir:  
   - Comandos de build e teste.  
   - Comando de rollback (ex: `git restore`).  
   - Indicação clara do **próximo passo** sugerido.  
4. O código deve:  
   - Cumprir contratos I-* e SLOs correspondentes.  
   - Estar de acordo com a Proposta (Cap. 4–7).  
   - Ter comentários técnicos e logs conforme Apêndice H.  
