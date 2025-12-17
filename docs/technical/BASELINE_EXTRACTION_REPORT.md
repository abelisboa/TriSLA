# RELATÓRIO DE EXTRAÇÃO DO BASELINE
## Tabela Módulo → Path → Dockerfile → Image → Helm

**Data**: 2025-01-15  
**Fonte**: `AUDITORIA_ESTRUTURAL_LOCAL_TRISLA.md`  
**Validação**: Estrutura real do repositório

---

## TABELA BASELINE EXTRAÍDA

| Módulo | Path Local | Dockerfile | Imagem | Helm Chart | Namespace |
|--------|-----------|------------|--------|------------|-----------|
| **SEM-CSMF** | `apps/sem-csmf/` | `apps/sem-csmf/Dockerfile` | `ghcr.io/abelisboa/trisla-sem-csmf:nasp-a2` | `helm/trisla/` | `trisla` |
| **ML-NSMF** | `apps/ml-nsmf/` | `apps/ml-nsmf/Dockerfile` | `ghcr.io/abelisboa/trisla-ml-nsmf:nasp-a2` | `helm/trisla/` | `trisla` |
| **BC-NSSMF** | `apps/bc-nssmf/` | `apps/bc-nssmf/Dockerfile` | `ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.11` ⚠️ | `helm/trisla/` | `trisla` |
| **SLA-Agent Layer** | `apps/sla-agent-layer/` | `apps/sla-agent-layer/Dockerfile` | `ghcr.io/abelisboa/trisla-sla-agent-layer:nasp-a2` | `helm/trisla/` | `trisla` |
| **Decision Engine** | `apps/decision-engine/` | `apps/decision-engine/Dockerfile` | `ghcr.io/abelisboa/trisla-decision-engine:nasp-a2` | `helm/trisla/` | `trisla` |
| **NASP Adapter** | `apps/nasp-adapter/` | `apps/nasp-adapter/Dockerfile` | `ghcr.io/abelisboa/trisla-nasp-adapter:nasp-a2` | `helm/trisla/` | `trisla` |
| **Besu** | `besu/` | `besu/Dockerfile` | `hyperledger/besu:23.10.1` ✅ | `helm/trisla-besu/` | `trisla` |

---

## VALIDAÇÃO DE CONSISTÊNCIA

### ✅ Validações Bem-Sucedidas

1. **Paths Locais**: Todos os paths existem e contêm código fonte
2. **Dockerfiles**: Todos os Dockerfiles existem e são buildáveis
3. **Helm Charts**: Chart principal `helm/trisla/` existe e contém templates para todos os módulos
4. **Namespace**: Todos os módulos usam namespace `trisla`
5. **Besu**: Tag fixa `23.10.1` confirmada (não usa `latest`)

### ⚠️ Inconsistências Detectadas

#### 1. Tag BC-NSSMF Inconsistente ✅ CORRIGIDO (PASSO 0)
- **Versão canônica**: `v3.7.11`
- **Status**: Padronizada em `helm/trisla/values.yaml` e documentação
- **Data correção**: 2025-01-15

#### 2. Besu usando `latest` no Values.yaml ✅ CORRIGIDO (PASSO 0)
- **Versão canônica**: `23.10.1`
- **Status**: Corrigido em `helm/trisla/values.yaml` (duas ocorrências)
- **Data correção**: 2025-01-15

---

## DETALHAMENTO POR MÓDULO

### SEM-CSMF
- **Porta**: `8080`
- **Replicas**: `2`
- **Status**: ✅ Consistente

### ML-NSMF
- **Porta**: `8081`
- **Replicas**: `2`
- **KAFKA_ENABLED**: `false`
- **Status**: ✅ Consistente

### BC-NSSMF
- **Porta**: `8083`
- **Replicas**: `2`
- **BC_ENABLED**: `true` (se Besu habilitado)
- **TRISLA_RPC_URL**: `http://trisla-besu:8545`
- **Status**: ⚠️ Tag inconsistente (ver acima)

### SLA-Agent Layer
- **Porta**: `8084`
- **Replicas**: `3`
- **Status**: ✅ Consistente

### Decision Engine
- **Porta**: `8082`
- **Replicas**: `2`
- **Status**: ✅ Consistente

### Besu
- **RPC HTTP**: `8545`
- **RPC WS**: `8546`
- **P2P**: `30303`
- **Chain ID**: `1337`
- **Status**: ⚠️ Tag `latest` no values.yaml (corrigir)

---

## PROMPTS GERADOS

Os seguintes prompts foram gerados com base neste baseline:

1. ✅ `docs/technical/PROMPT_S1_SEM_CSMF.md`
2. ✅ `docs/technical/PROMPT_S2_ML_NSMF.md`
3. ✅ `docs/technical/PROMPT_S3_BC_NSSMF.md`
4. ✅ `docs/technical/PROMPT_S4_SLA_AGENT.md`
5. ✅ `docs/technical/PROMPT_S5_OBS_ADAPTATION.md`

---

## CONTEXTO FIXO APLICADO

Todos os prompts seguem o contexto fixo:

- **Diretório raiz local**: `C:\Users\USER\Documents\TriSLA-clean`
- **Build sempre local**
- **Deploy sempre via**: `ssh node006 → /home/porvir5g/gtp5g/trisla`
- **Proibido usar imagens "latest"**
- **Helm é a única forma de deploy**
- **Namespace**: `trisla`

---

## PRÓXIMOS PASSOS

1. ✅ **PASSO 0 concluído**: Todas as inconsistências corrigidas (2025-01-15)
   - BC-NSSMF: `v3.7.11` (versão canônica)
   - Besu: `23.10.1` (versão canônica)
   - Observabilidade: Tags versionadas (Kafka 3.6.1, OTEL 0.92.0, Prometheus v2.49.1, Grafana 10.2.3)
2. ✅ **Executar prompts**: Usar os 10 prompts gerados (5 sprints × 2: LOCAL e NASP) para execução dos sprints técnicos

---

**FIM DO RELATÓRIO**

