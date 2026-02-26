# Ambiente Experimental TriSLA

## Objetivo Científico

Este ambiente experimental foi criado para permitir a avaliação reprodutível e rastreável do sistema TriSLA, especificamente para cenários de carga incremental com slices eMBB.

O objetivo é coletar evidências empíricas sobre:
- Tempo de decisão de admissão de SLA
- Tempo end-to-end (submissão → decisão → registro)
- Taxa de aceitação/rejeição/renegociação
- Comportamento do sistema sob carga progressiva (5, 10, 20 SLAs simultâneos)

## Princípios Fundamentais

### 1. Reprodutibilidade
Todos os experimentos devem ser executáveis de forma idêntica em diferentes momentos, garantindo que resultados possam ser validados e replicados.

### 2. Rastreabilidade
Cada execução experimental gera:
- Timestamps precisos (client-side e server-side)
- Correlation IDs únicos por SLA
- Logs completos preservados
- Métricas brutas sem agregação prévia

### 3. Isolamento
**REGRA ABSOLUTA:** Nenhum código do TriSLA é modificado durante experimentos.
- `apps/` permanece intocado
- `helm/` permanece intocado
- `docs/` permanece intocado (exceto este diretório)
- Apenas dados experimentais são gerados em `experiments/`

## Cenários Experimentais

### C1 - eMBB (Enhanced Mobile Broadband)

Cenários de carga incremental com slices eMBB:

- **C1_eMBB_5:** 5 SLAs simultâneos
- **C1_eMBB_10:** 10 SLAs simultâneos
- **C1_eMBB_20:** 20 SLAs simultâneos

Cada cenário testa a capacidade do sistema de processar múltiplas solicitações de SLA em paralelo, medindo:
- Latência de decisão
- Throughput do sistema
- Estabilidade sob carga

## Estrutura do Ambiente

```
experiments/
├── README.md                 # Este arquivo
├── PROMPT_CONTROL.md         # Protocolo de execução experimental
├── templates/                # Templates YAML de cenários
├── generators/               # Scripts de geração de carga
├── collectors/                # Scripts de coleta de dados
├── analysis/                 # Scripts de análise offline
└── reports/                  # Relatórios e resultados
```

## Fluxo Experimental

### 1. Preparação (Template)
- Selecionar template YAML do cenário desejado
- Validar configurações (quantidade, intervalo, métricas)

### 2. Execução
- Executar `generators/submit_slas.py` com template selecionado
- SLAs são submetidos via API HTTP existente
- Timestamps e correlation IDs são registrados

### 3. Coleta
- Executar `collectors/prometheus_collector.py` para métricas
- Executar `collectors/logs_collector.py` para logs
- Dados brutos são salvos sem processamento

### 4. Análise
- Executar `analysis/compute_metrics.py` sobre dados brutos
- Calcular métricas agregadas (p50, p95, média)
- Gerar estatísticas descritivas

### 5. Relatório
- Documentar resultados em `reports/`
- Incluir dados brutos e análise
- Preparar para uso em dissertação/artigo

## Regras de Execução

1. **Nunca executar múltiplos cenários simultaneamente**
2. **Sempre validar resultados de um cenário antes de iniciar o próximo**
3. **Preservar todos os dados brutos (não deletar)**
4. **Documentar qualquer anomalia observada**
5. **Seguir rigorosamente o PROMPT_CONTROL.md**

## Dependências

- Python 3.8+
- Acesso ao cluster Kubernetes (kubectl configurado)
- Acesso ao Prometheus (endpoint configurado)
- API do TriSLA disponível e funcional

## Notas Importantes

- Este ambiente **NÃO modifica** o código do TriSLA
- Todos os scripts são **conservadores** (sem retries automáticos, sem paralelização agressiva)
- Dados são coletados de forma **não intrusiva**
- Análise é feita **offline** para não impactar o sistema

## Próximos Passos

1. Revisar `PROMPT_CONTROL.md` antes de qualquer execução
2. Validar templates em `templates/`
3. Executar FASE 0 (Pré-check) conforme protocolo
4. Proceder com execução incremental e validada

---

**Última atualização:** 2025-01-27  
**Versão:** 1.0.0

