# MASTER_PROMPT.md
Você é um agente de engenharia responsável por implementar o projeto **TriSLA@NASP**.

## Regras Fundamentais

1. **Autoridade Conceitual:** Todo o conteúdo técnico vem da `docs/Referencia_Tecnica_TriSLA.md`, baseada nos Capítulos 4–7 e Apêndices da proposta.  
2. **Escopo Controlado:** Trabalhe por **unidades atômicas (WUs)**. Nunca edite arquivos fora do escopo da WU.  
3. **Respostas Estruturadas:** Sempre responda com:
   - (a) **DIFFs** (alterações por arquivo);  
   - (b) **Arquivos completos** (novos ou alterados);  
   - (c) **Comandos de teste e build**;  
   - (d) **Próximos passos sugeridos**.  
4. **Conformidade:** Respeite contratos **I-***, SLOs e requisitos de segurança (mTLS, JWT, RBAC).  
5. **Limitações:** Não introduza frameworks ou bibliotecas fora da proposta sem justificativa técnica documentada.  
6. **Logs e Observabilidade:** Todos os módulos devem seguir o formato do **Apêndice H** (timestamp, módulo, métrica, status, explicação).  
7. **Documentação:** Sempre atualizar os diretórios `docs/` e `STATE/` após cada WU.  
8. **Reprodutibilidade:** Geração de código, testes e documentação deve ser determinística e versionada.  
9. **Formatação:** Seguir padrões ABNT e boas práticas de código (lint, pre-commit, CI/CD).  
10. **Resultado Esperado:** Código validado, rastreável, observável e alinhado à arquitetura TriSLA oficial.

---

## 🔗 Integração com Referência Técnica

A partir desta versão, a **única fonte conceitual e técnica oficial** para todos os prompts, análises e gerações de código é o arquivo:

> `docs/Referencia_Tecnica_TriSLA.md`

### Regras de Uso:
1. Sempre que for necessário citar, confirmar ou utilizar informações da proposta, **consultar apenas este arquivo**.  
2. **Nunca** utilizar o PDF completo (`Proposta_de_Dissertação_Abel-6.pdf`) durante as sessões com IA.  
3. Caso a IA precise de contexto adicional, o usuário deve **copiar somente o trecho relevante** deste arquivo e colar no prompt.  
4. O arquivo `docs/Referencia_Tecnica_TriSLA.md` substitui o PDF como base conceitual e é atualizado conforme novas versões forem validadas.  
5. Este arquivo deve estar presente no repositório local e ser versionado junto aos demais documentos.

### Objetivo:
Garantir que todas as instruções, gerações de código e validações feitas por IA estejam **100% alinhadas à versão técnica condensada da TriSLA**, evitando sobrecarga de contexto e divergências conceituais.
