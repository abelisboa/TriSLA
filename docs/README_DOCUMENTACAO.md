# 🛰️ Documentação TriSLA — Apêndices e Integração Overleaf

## 🔹 Estrutura dos Apêndices no GitHub

Os apêndices técnicos (A–H) foram migrados para:

`/docs/apendices/`

Cada apêndice corresponde diretamente à versão acadêmica no Overleaf.

### Lista de Apêndices

- **Apêndice A** — [Catálogo de Interfaces Internas I-*](apendices/APENDICE_A_INTERFACES.md)
- **Apêndice B** — [Mapeamento NWDAF ↔ NASP](apendices/APENDICE_B_NWDAF_NASP.md)
- **Apêndice C** — [Contratos de API e Exemplos](apendices/APENDICE_C_APIS_EXEMPLOS.md)
- **Apêndice D** — [Testes de Contrato](apendices/APENDICE_D_TESTES_CONTRATO.md)
- **Apêndice E** — [Diretrizes de Observabilidade e SLOs](apendices/APENDICE_E_OBSERVABILIDADE_SLOs.md)
- **Apêndice F** — [Matriz de Rastreabilidade](apendices/APENDICE_F_RASTREABILIDADE.md)
- **Apêndice G** — [Listagens de Código](apendices/APENDICE_G_LISTAGENS_CODIGO.md)
- **Apêndice H** — [Plano de Execução e Logs de Observabilidade](apendices/APENDICE_H_EXECUCAO_LOGS.md)

## 🔹 Sincronização Automática

O script `scripts/sync_appendices_to_overleaf.py` converte os arquivos Markdown (.md)
em LaTeX (.tex) e os copia para:

**Windows:**
- `C:/Users/USER/Documents/Dissertacao_TriSLA/Overleaf/apendices/`

**WSL:**
- `/mnt/c/Users/USER/Documents/Dissertacao_TriSLA/Overleaf/apendices/`

A sincronização também é executada automaticamente via GitHub Actions
quando qualquer arquivo em `docs/apendices/**` é alterado.

### Execução Manual

```bash
# No Windows (PowerShell)
python scripts/sync_appendices_to_overleaf.py

# No Linux/WSL
python3 scripts/sync_appendices_to_overleaf.py
```

## 🔹 Benefícios

✅ **Versionamento e rastreabilidade completos** dos apêndices

✅ **Alinhamento automático** entre código e texto acadêmico

✅ **Atualização contínua** (GitHub → Overleaf → PDF final)

## 🔹 Fluxo de Trabalho

1. **Edição**: Modifique qualquer apêndice em `/docs/apendices/*.md`
2. **Commit**: Faça commit e push no GitHub
3. **Automação**: O workflow GitHub Actions executa automaticamente
4. **Conversão**: Gera `.tex` equivalente e sincroniza com Overleaf
5. **Compilação**: Overleaf recompila a dissertação com conteúdo atualizado
6. **Resultado**: PDF final permanece 100% alinhado à base técnica e código

## 🔹 Integração com Código

Os apêndices referenciam diretamente o código-fonte do repositório:

- `/apps/sem_csmf/` — Módulo SEM-CSMF
- `/apps/ml_nsmf/` — Módulo ML-NSMF
- `/apps/bc_nssmf/` — Módulo BC-NSSMF
- `/apps/agents/` — Agents e Decision Engine
- `/apps/api/` — APIs REST (OpenAPI)
- `/schemas/` — Schemas Kafka e eventos

Mantendo rastreabilidade completa entre documentação acadêmica e implementação.

