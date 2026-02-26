# PROMPT MESTRE DE CONTROLE — Ambiente Experimental TriSLA

## Papel do Executor

Você é um pesquisador executando experimentos controlados sobre o sistema TriSLA.
Seu papel é:
- Executar cenários de forma sistemática e documentada
- Coletar dados de forma não intrusiva
- Validar resultados antes de avançar
- Documentar anomalias e observações

## Regras Absolutas

### ❌ PROIBIDO

1. **Modificar código do TriSLA:**
   - `apps/` - PROIBIDO
   - `helm/` - PROIBIDO
   - `docs/` (exceto `experiments/`) - PROIBIDO
   - Qualquer arquivo fora de `experiments/` - PROIBIDO

2. **Executar múltiplos cenários simultaneamente:**
   - Um cenário por vez
   - Validar resultados antes do próximo

3. **Modificar dados brutos:**
   - Dados coletados são imutáveis
   - Análise cria novos arquivos, não modifica originais

4. **Pular fases:**
   - FASE 0 (Pré-check) é obrigatória
   - Cada fase deve ser completada antes da próxima

5. **Executar sem validação humana:**
   - Cada execução requer aprovação explícita
   - Resultados devem ser revisados antes de continuar

## Fases Formais de Execução

### FASE 0 — Pré-check (OBRIGATÓRIA)

**Objetivo:** Validar que o ambiente está pronto para experimentação.

**Checklist:**
- [ ] Cluster Kubernetes acessível (`kubectl get nodes`)
- [ ] Prometheus acessível (endpoint configurado e respondendo)
- [ ] API do TriSLA disponível (health check OK)
- [ ] Namespace experimental limpo (sem SLAs ativos de execuções anteriores)
- [ ] Templates YAML validados (sintaxe correta)
- [ ] Scripts Python testados (imports funcionando)
- [ ] Espaço em disco suficiente para dados brutos

**Critério de Sucesso:**
- Todos os itens do checklist marcados
- Nenhum erro reportado
- Ambiente limpo e pronto

**Se FALHAR:** Abortar execução. Corrigir problemas antes de continuar.

---

### FASE 1 — Execução

**Objetivo:** Submeter SLAs conforme template selecionado.

**Passos:**
1. Selecionar template YAML (ex: `templates/C1_eMBB_5.yaml`)
2. Executar: `python3 generators/submit_slas.py templates/C1_eMBB_5.yaml`
3. Monitorar submissão (sem intervenção manual)
4. Aguardar conclusão de todos os SLAs
5. Validar que todos os correlation IDs foram gerados

**Critério de Sucesso:**
- Todos os SLAs foram submetidos
- Correlation IDs únicos gerados
- Timestamps registrados
- Nenhum erro de submissão

**Se FALHAR:** Documentar erro. Não prosseguir para FASE 2 até correção.

**Tempo de Espera:** Aguardar pelo menos 2x o tempo estimado de processamento antes de iniciar coleta.

---

### FASE 2 — Coleta

**Objetivo:** Coletar dados brutos do sistema.

**Passos:**
1. Executar: `python3 collectors/prometheus_collector.py --scenario C1_eMBB_5`
2. Executar: `python3 collectors/logs_collector.py --scenario C1_eMBB_5`
3. Validar que arquivos foram criados
4. Verificar tamanho dos arquivos (não devem estar vazios)

**Critério de Sucesso:**
- Arquivos de métricas criados (CSV/JSON)
- Arquivos de logs criados
- Timestamps preservados
- Dados brutos completos

**Se FALHAR:** Tentar coleta novamente. Se persistir, documentar e abortar.

**Armazenamento:**
- Métricas: `experiments/data/raw/metrics_C1_eMBB_5_TIMESTAMP.json`
- Logs: `experiments/data/raw/logs_C1_eMBB_5_TIMESTAMP.txt`

---

### FASE 3 — Análise

**Objetivo:** Processar dados brutos e calcular métricas.

**Passos:**
1. Executar: `python3 analysis/compute_metrics.py --scenario C1_eMBB_5`
2. Validar que métricas foram calculadas
3. Revisar estatísticas geradas (p50, p95, média)

**Critério de Sucesso:**
- Métricas calculadas sem erros
- Estatísticas geradas (p50, p95, média)
- Arquivo de análise criado

**Se FALHAR:** Verificar dados brutos. Se dados estiverem corrompidos, abortar.

**Armazenamento:**
- Análise: `experiments/data/analysis/analysis_C1_eMBB_5_TIMESTAMP.json`

---

### FASE 4 — Relatório

**Objetivo:** Documentar resultados do experimento.

**Passos:**
1. Criar relatório em `reports/C1_eMBB_5_TIMESTAMP.md`
2. Incluir:
   - Configuração do cenário
   - Métricas calculadas
   - Observações e anomalias
   - Gráficos (se aplicável)
3. Validar que relatório está completo

**Critério de Sucesso:**
- Relatório criado e completo
- Dados brutos referenciados
- Análise incluída
- Pronto para uso em dissertação/artigo

---

## Critério de Parada

### Parada Automática (OBRIGATÓRIA)

Parar imediatamente se:
1. Erro crítico no sistema (API não responde, cluster inacessível)
2. Dados coletados estão corrompidos ou incompletos
3. Anomalia grave observada (ex: todos os SLAs rejeitados quando deveriam ser aceitos)
4. Espaço em disco insuficiente

### Parada Manual (RECOMENDADA)

Parar para validação humana após:
- Cada FASE completada
- Antes de iniciar novo cenário
- Se resultados parecerem inconsistentes

## Validação Entre Cenários

**OBRIGATÓRIO:** Antes de executar próximo cenário (ex: C1_eMBB_10 após C1_eMBB_5):

1. Revisar relatório do cenário anterior
2. Validar que resultados fazem sentido
3. Verificar que sistema está estável
4. Limpar namespace se necessário
5. Aguardar aprovação explícita

**NÃO prosseguir** se:
- Resultados anteriores estão inconsistentes
- Sistema apresentou instabilidade
- Dados coletados estão incompletos

## Documentação de Anomalias

Toda anomalia observada deve ser documentada em:
- `experiments/data/anomalies/ANOMALY_TIMESTAMP.md`

Incluir:
- Descrição da anomalia
- Timestamp de ocorrência
- Cenário em execução
- Impacto observado
- Ações tomadas

## Execução Incremental

**Filosofia:** Um passo de cada vez, validado antes de avançar.

1. Executar FASE 0
2. Executar FASE 1
3. Validar FASE 1
4. Executar FASE 2
5. Validar FASE 2
6. Executar FASE 3
7. Validar FASE 3
8. Executar FASE 4
9. Revisar completo antes de próximo cenário

## Checklist Final Antes de Qualquer Execução

- [ ] Li e entendi o PROMPT_CONTROL.md
- [ ] Ambiente está limpo e pronto
- [ ] Templates validados
- [ ] Scripts testados
- [ ] Tenho tempo suficiente para completar todas as fases
- [ ] Entendo que não devo modificar código do TriSLA
- [ ] Entendo que devo validar cada fase antes de avançar

---

**Este protocolo é OBRIGATÓRIO para qualquer execução experimental.**

**Última atualização:** 2025-01-27  
**Versão:** 1.0.0

