# Relatórios Experimentais - TriSLA

## Estrutura de Relatórios

Os relatórios experimentais devem seguir uma estrutura padronizada para facilitar uso posterior em dissertação ou artigos científicos.

## Convenção de Nomenclatura

### Formato
```
{SCENARIO_ID}_{TIMESTAMP}.md
```

### Exemplos
- `C1_eMBB_5_20250127_143022.md`
- `C1_eMBB_10_20250127_150530.md`
- `C1_eMBB_20_20250127_161245.md`

## Estrutura Esperada de Relatório

### 1. Cabeçalho
```markdown
# Relatório Experimental - {SCENARIO_ID}

**Data:** YYYY-MM-DD HH:MM:SS UTC
**Cenário:** {SCENARIO_ID}
**Executor:** {nome/identificação}
**Ambiente:** {cluster, namespace, versão}
```

### 2. Configuração do Experimento
- Template utilizado
- Parâmetros de execução (quantidade, intervalo, timeout)
- Perfil de SLA (tipo, QoS requirements)

### 3. Métricas Coletadas

#### 3.1 Tempo de Decisão
- Estatísticas: média, p50, p95, p99, min, max
- Distribuição (se aplicável)
- Comparação com valores esperados

#### 3.2 Tempo End-to-End
- Estatísticas: média, p50, p95, p99, min, max
- Breakdown por componente (se disponível)

#### 3.3 Taxa de Aceitação
- Total de SLAs submetidos
- Aceitos / Rejeitados / Renegociados
- Percentuais

### 4. Observações e Anomalias
- Comportamentos inesperados
- Erros observados
- Degradação de performance (se houver)
- Referência a arquivos de anomalias (se aplicável)

### 5. Dados Brutos Referenciados
- Caminhos para arquivos de submissões
- Caminhos para métricas do Prometheus
- Caminhos para logs coletados
- Caminhos para análise gerada

### 6. Gráficos (Opcional)
- Gráficos de distribuição de tempos
- Gráficos de taxa de aceitação
- Gráficos de carga ao longo do tempo

### 7. Conclusões
- Resumo dos resultados principais
- Comparação com expectativas
- Próximos passos (se aplicável)

## Separação de Dados

### Dados Brutos
Armazenados em: `experiments/data/raw/`
- **NÃO devem ser modificados**
- Preservados para validação e replicação
- Incluem:
  - Submissões (JSON)
  - Métricas Prometheus (JSON/CSV)
  - Logs (TXT)

### Análise Processada
Armazenados em: `experiments/data/analysis/`
- Resultados de processamento
- Estatísticas calculadas
- Podem ser recalculados a partir de dados brutos

### Relatórios
Armazenados em: `experiments/reports/`
- Documentação textual
- Interpretação dos resultados
- Prontos para uso em dissertação/artigo

## Uso em Dissertação/Artigo

### Citação de Dados
Ao referenciar resultados experimentais:

1. **Citar o relatório completo:**
   > "Conforme relatório experimental C1_eMBB_5_20250127_143022.md, o tempo médio de decisão foi de X ms com p95 de Y ms."

2. **Referenciar dados brutos:**
   > "Dados brutos disponíveis em experiments/data/raw/submissions_C1_eMBB_5_20250127_143022.json"

3. **Incluir análise:**
   > "Análise estatística disponível em experiments/data/analysis/analysis_C1_eMBB_5_20250127_143022.json"

### Reprodutibilidade
Para garantir reprodutibilidade:

1. Incluir versão do template utilizado
2. Incluir versão do sistema (TriSLA)
3. Incluir configuração do ambiente
4. Referenciar todos os dados brutos utilizados

## Template de Relatório

Ver exemplo em: `experiments/reports/TEMPLATE.md` (se disponível)

## Validação de Relatório

Antes de considerar um relatório completo, verificar:

- [ ] Todas as seções obrigatórias preenchidas
- [ ] Dados brutos referenciados e acessíveis
- [ ] Métricas calculadas e apresentadas
- [ ] Anomalias documentadas (se houver)
- [ ] Conclusões coerentes com dados

---

**Última atualização:** 2025-01-27  
**Versão:** 1.0.0

