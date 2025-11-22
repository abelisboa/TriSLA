# 07 — MASTER-PROMPT-CORRETOR v6.0

**Documento Oficial — Correção, Validação e Padronização de Prompts TriSLA**  
**2025 — Abel Lisboa**

---

## 🎯 Finalidade

Este é o prompt oficial para **corrigir, validar, padronizar e alinhar todos os prompts do TriSLA**, garantindo consistência técnica, DevOps e organizacional entre todas as pastas da estrutura `TriSLA_PROMPTS/`.

Ele serve como:

- Auditor automático de prompts
- Validador de estrutura e naming convention
- Normalizador de conteúdo
- Suporte para reorganização futura
- Garante alinhamento com o MASTER_ORCHESTRATOR v6.0

---

## 🧠 Funções principais do MASTER-PROMPT-CORRETOR

### 1. **Padronizar nomes**

- `NN_NOME_DO_ARQUIVO.md`
- Sem espaços extras
- Sem acentos desnecessários
- Numeração coerente (00-99)
- Letras maiúsculas em palavras compostas

### 2. **Corrigir conteúdo**

- Títulos padronizados
- Header inicial obrigatório
- Estrutura de seções consistente
- Evitar duplicações
- Adotar terminologia DevOps TriSLA

### 3. **Validar estrutura**

- Conferir se cada pasta possui README.md
- Validar se há arquivos órfãos
- Detectar arquivos LEGACY
- Detectar arquivos não referenciados

### 4. **Detectar conflitos**

- Duplicações de conteúdo
- Versões antigas
- Nomes inconsistentes
- Prompts divergentes da estrutura v6.0

---

## 🧩 Workflow completo do Corretor

### 1. Varredura da estrutura

- Escanear tudo em `TriSLA_PROMPTS/`
- Gerar inventário JSON
- Detectar padrões incorretos

### 2. Correção automática

- Corrigir nomes quando seguro
- Sugerir renomeações quando crítico
- Normalizar seções internas
- Padronizar títulos e numeradores

### 3. Validação de conformidade DevOps

- Conferir integração com o DevOps Consolidator v6.0
- Checar presença das seções obrigatórias
- Checar referência cruzada dos módulos

### 4. Geração de relatórios

- `RELATORIO_CORRECAO_PROMPTS.md`
- `RELATORIO_INCONSISTENCIAS.md`
- `RELATORIO_ALINHAMENTO_DEVOPS.md`

---

## ✔️ Estrutura que o Corretor deve impor

### Cada prompt deve conter:

1. **Título oficial padronizado**
   - Formato: `# NN — NOME_DO_PROMPT`
   - Numeração consistente (00-99)

2. **Finalidade e contexto**
   - Objetivo claro
   - Contexto de uso
   - Quando executar

3. **Escopo**
   - O que será gerado/criado
   - Módulos afetados
   - Dependências

4. **Instruções operacionais**
   - Passo a passo claro
   - Comandos específicos
   - Validações obrigatórias

5. **Fluxo DevOps (se aplicável)**
   - Integração com CI/CD
   - Deploy considerations
   - Ambiente (Local vs NASP)

6. **Dependências**
   - Pré-requisitos
   - Módulos necessários
   - Ordem de execução

7. **Checklist**
   - Itens obrigatórios
   - Validações
   - Critérios de sucesso

8. **Versão**
   - Numero da versão
   - Data de atualização
   - Autor

9. **Histórico de alterações**
   - Mudanças significativas
   - Versões anteriores

---

## 📌 Seções obrigatórias

Todo arquivo deve seguir esta estrutura mínima:

```markdown
# NN — NOME_DO_PROMPT

**Versão:** X.X  
**Data:** YYYY-MM-DD  
**Autor:** Nome/Auto-gerado

---

## 1. Objetivo

Descrição clara do objetivo do prompt.

## 2. Contexto

Contexto de uso e quando executar.

## 3. Escopo

O que será gerado/criado/modificado.

## 4. Instruções

Passo a passo detalhado.

## 5. Validação

Como validar o resultado.

## 6. Checklist

- [ ] Item 1
- [ ] Item 2

---

**Versão:** X.X  
**Última atualização:** YYYY-MM-DD
```

---

## 🔍 Regras de Nomenclatura

### Arquivos de Prompt

| Padrão | Exemplo | Status |
|--------|---------|--------|
| `NN_NOME.md` | `20_SEM_CSMF.md` | ✅ Correto |
| `NN_NOME_DO_PROMPT.md` | `21_ONTOLOGIA_OWL.md` | ✅ Correto |
| `README.md` | `README.md` | ✅ Permitido |
| `NOME.md` | `ONTOLOGIA.md` | ❌ Incorreto |
| `nome.md` | `sem_csmf.md` | ❌ Incorreto |
| `NOME_PROMPT.md` | `SEM_CSMF_PROMPT.md` | ❌ Incorreto (falta numeração) |

### Pastas

| Padrão | Exemplo | Status |
|--------|---------|--------|
| `N_CATEGORIA` | `0_MASTER` | ✅ Correto |
| `N_CATEGORIA` | `1_INFRA` | ✅ Correto |
| `CATEGORIA` | `MASTER` | ❌ Incorreto |
| `n_categoria` | `1_infra` | ❌ Incorreto |

---

## 🔄 Padrões de Conteúdo

### Headers Padronizados

**Título principal:**
```markdown
# NN — NOME_DO_PROMPT
```

**Títulos de seção:**
```markdown
## N. Nome da Seção

### N.N Subseção

#### N.N.N Subsubseção
```

### Terminologia TriSLA

**Módulos:**
- SEM-CSMF (não "sem_csmf" ou "SemCsmf")
- ML-NSMF (não "ml_nsmf" ou "MlNsmf")
- Decision Engine (não "decision_engine" ou "DecisionEngine")
- BC-NSSMF (não "bc_nssmf" ou "BcNssmf")
- SLA-Agent Layer (não "sla_agent_layer")
- NASP Adapter (não "nasp_adapter")

**Ambientes:**
- Local (sandbox/desenvolvimento)
- NASP (produção experimental)

**Interfaces:**
- I-01, I-02, I-03, I-04, I-05, I-06, I-07

---

## 🚨 Detecção de Problemas

### Problemas Comuns Detectados

1. **Nomes inconsistentes**
   - Arquivos sem numeração
   - Numeração fora de ordem
   - Nomes com espaços ou caracteres especiais

2. **Conteúdo duplicado**
   - Prompts com conteúdo similar
   - Versões antigas não removidas
   - Seções repetidas

3. **Falta de estrutura**
   - Ausência de seções obrigatórias
   - Headers inconsistentes
   - Falta de versionamento

4. **Desalinhamento DevOps**
   - Prompts não alinhados com v6.0
   - Referências a versões antigas
   - Falta de integração com pipeline

---

## 🔧 Ações de Correção

### Correções Automáticas (Seguras)

1. **Renomeação de arquivos**
   - Adicionar numeração se ausente
   - Normalizar espaços para underscores
   - Converter para maiúsculas se necessário

2. **Padronização de headers**
   - Adicionar título padronizado
   - Inserir metadata (versão, data)
   - Estruturar seções obrigatórias

3. **Limpeza de conteúdo**
   - Remover espaços extras
   - Normalizar quebras de linha
   - Padronizar formatação

### Correções Sugeridas (Requerem Revisão)

1. **Reorganização de conteúdo**
   - Mover seções para locais corretos
   - Consolidar conteúdo duplicado
   - Separar concerns diferentes

2. **Atualização de referências**
   - Atualizar links para versão v6.0
   - Corrigir referências cruzadas
   - Atualizar exemplos obsoletos

---

## 📊 Relatórios Gerados

### 1. RELATORIO_CORRECAO_PROMPTS.md

**Conteúdo:**
- Lista de correções aplicadas
- Arquivos renomeados
- Conteúdo padronizado
- Headers adicionados/modificados

### 2. RELATORIO_INCONSISTENCIAS.md

**Conteúdo:**
- Duplicações detectadas
- Conflitos de nomenclatura
- Conteúdo divergente
- Versões antigas encontradas

### 3. RELATORIO_ALINHAMENTO_DEVOPS.md

**Conteúdo:**
- Status de alinhamento com v6.0
- Prompts atualizados
- Prompts que precisam atualização
- Integração com pipeline

---

## 🎯 Execução do Corretor

### Modo Manual

```bash
# Revisar relatórios de auditoria
cat TriSLA_PROMPTS/RELATORIO_AUDITORIA_PROMPTS_v1.md

# Executar correções sugeridas
python scripts/correct-prompts.py --dry-run

# Aplicar correções
python scripts/correct-prompts.py --apply
```

### Modo Automático (Cursor)

```bash
# Executar correção via Cursor
cursor run TriSLA_PROMPTS/0_MASTER/07_MASTER_PROMPT_CORRETOR.json
```

---

## ✅ Checklist de Conformidade

Cada prompt deve atender:

- [ ] Nome segue padrão `NN_NOME.md`
- [ ] Título padronizado presente
- [ ] Seções obrigatórias presentes
- [ ] Terminologia TriSLA correta
- [ ] Referências atualizadas (v6.0)
- [ ] Versão e data presentes
- [ ] Checklist incluído
- [ ] Sem duplicações
- [ ] Sem arquivos LEGACY
- [ ] Alinhado com DevOps Consolidator v6.0

---

## 🔗 Integração com MASTER-ORCHESTRATOR v6.0

Este corretor está **totalmente alinhado** com:

- `06_MASTER_DEVOPS_CONSOLIDATOR_v6.md` - Estrutura DevOps
- `01_ORDEM_EXECUCAO.md` - Ordem de execução
- `02_CHECKLIST_GLOBAL.md` - Checklist global
- `03_ESTRATEGIA_EXECUCAO.md` - Estratégia de execução

**Garantias:**
- Nomenclatura consistente
- Estrutura padronizada
- Conteúdo alinhado
- Integração DevOps completa

---

## 📝 Exemplo de Prompt Corrigido

### ANTES (Incorreto):

```markdown
# Prompt sem-csmf

Este prompt cria o módulo sem csmf.

Instruções:
- Criar módulo
- Adicionar código
- Testar
```

### DEPOIS (Correto):

```markdown
# 20 — SEM-CSMF

**Versão:** 1.0  
**Data:** 2025-01-21  
**Autor:** TriSLA Team

---

## 1. Objetivo

Criar e implementar o módulo SEM-CSMF (Semantic-Context Service Management Function) do TriSLA.

## 2. Contexto

Este prompt deve ser executado durante a fase de desenvolvimento do módulo SEM-CSMF, seguindo a ordem estabelecida em `01_ORDEM_EXECUCAO.md`.

## 3. Escopo

- Estrutura do módulo `apps/sem-csmf/`
- Implementação de gRPC server/client
- Integração com Kafka
- Parser de ontologia OWL
- Database models (SQLAlchemy)
- API REST

## 4. Instruções

### 4.1 Criar Estrutura

```bash
mkdir -p apps/sem-csmf/src
cd apps/sem-csmf
```

### 4.2 Implementar Módulos

- [ ] `main.py` - FastAPI app
- [ ] `grpc_server.py` - gRPC server
- [ ] `ontology/parser.py` - OWL parser
- [ ] `models/` - Database models

## 5. Validação

```bash
pytest tests/unit/test_sem_csmf.py -v
curl http://localhost:8080/health
```

## 6. Checklist

- [ ] Módulo criado em `apps/sem-csmf/`
- [ ] gRPC server funcional
- [ ] Kafka producer funcionando
- [ ] Ontology parser testado
- [ ] Testes unitários passando
- [ ] Health check respondendo

---

**Versão:** 1.0  
**Última atualização:** 2025-01-21
```

---

## 🏁 Conclusão

O **MASTER-PROMPT-CORRETOR v6.0** garante que todos os prompts do TriSLA estejam:

- ✅ Padronizados
- ✅ Consistentes
- ✅ Atualizados
- ✅ Alinhados com DevOps v6.0
- ✅ Prontos para uso

**Execução:** Revisar relatórios de auditoria e aplicar correções conforme necessário.

---

## 🔒 Segurança

O MASTER-PROMPT-CORRETOR **nunca apaga nada automaticamente**.

Todo rename crítico gera:

- Arquivo original preservado
- Relatório listando a sugestão
- Ação manual recomendada

**Princípios de segurança:**

1. **Backup automático:** Antes de qualquer renomeação, criar backup
2. **Modo dry-run:** Sempre executar primeiro em modo de simulação
3. **Validação manual:** Renomeações críticas requerem aprovação manual
4. **Histórico preservado:** Manter histórico de todas as alterações
5. **Rollback fácil:** Garantir possibilidade de reverter mudanças

**Exemplo de execução segura:**

```bash
# 1. Modo dry-run (simulação)
python scripts/correct-prompts.py --dry-run

# 2. Gerar backup antes de alterar
python scripts/correct-prompts.py --backup

# 3. Aplicar correções (após revisão)
python scripts/correct-prompts.py --apply --confirm
```

---

## 🧪 Validação Final

Após rodar o corretor:

- ✅ Todos os arquivos devem estar padronizados
- ✅ Zero duplicações
- ✅ Estrutura 100% alinhada ao DevOps v6.0
- ✅ Pronto para pacote GitHub + Deploy NASP

### Checklist de Validação Final

- [ ] Todos os arquivos seguem padrão `NN_NOME.md`
- [ ] Todos os prompts têm seções obrigatórias
- [ ] Terminologia TriSLA consistente em todos os arquivos
- [ ] Referências atualizadas para v6.0
- [ ] Nenhuma duplicação de conteúdo
- [ ] Nenhum arquivo LEGACY ativo
- [ ] README.md presente em cada categoria
- [ ] Estrutura alinhada com `06_MASTER_DEVOPS_CONSOLIDATOR_v6.md`
- [ ] Relatórios de correção gerados
- [ ] Validação de integração DevOps OK

### Comandos de Validação

```bash
# Validar nomenclatura
python scripts/validate-prompt-names.py

# Validar estrutura
python scripts/validate-prompt-structure.py

# Validar conteúdo
python scripts/validate-prompt-content.py

# Validar integração DevOps
python scripts/validate-devops-alignment.py
```

---

## 🔖 Versão

**v6.0** — Novembro/2025  
**Autor:** TriSLA  
**Pipeline:** MASTER-DEVOPS-CONSOLIDATOR v6.0

**Histórico de Versões:**

| Versão | Data | Mudanças |
|--------|------|----------|
| v6.0 | 2025-11-21 | Versão inicial consolidada |
| - | - | Alinhada com MASTER-DEVOPS-CONSOLIDATOR v6.0 |

---

**Versão:** 6.0  
**Última atualização:** 2025-11-21  
**Alinhado com:** MASTER-DEVOPS-CONSOLIDATOR v6.0

