# BASELINE_SUMMARY — Extração Estrutural TriSLA

**Data de Extração:** 2025-01-15  
**Fonte:** Estrutura real do repositório + `docs/technical/BASELINE_EXTRACTION_REPORT.md`  
**Validação:** Paths, Dockerfiles e Helm charts verificados

---

## TABELA BASELINE EXTRAÍDA

| Módulo | Path Local | Dockerfile | Imagem Docker | Helm Chart | Namespace | Porta | Replicas |
|--------|-----------|------------|---------------|------------|-----------|-------|----------|
| **SEM-CSMF** | `apps/sem-csmf/` | `apps/sem-csmf/Dockerfile` | `ghcr.io/abelisboa/trisla-sem-csmf:nasp-a2` | `helm/trisla/` | `trisla` | 8080 | 2 |
| **ML-NSMF** | `apps/ml-nsmf/` | `apps/ml-nsmf/Dockerfile` | `ghcr.io/abelisboa/trisla-ml-nsmf:nasp-a2` | `helm/trisla/` | `trisla` | 8081 | 2 |
| **BC-NSSMF** | `apps/bc-nssmf/` | `apps/bc-nssmf/Dockerfile` | `ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.11` ✅ | `helm/trisla/` | `trisla` | 8083 | 2 |
| **Decision Engine** | `apps/decision-engine/` | `apps/decision-engine/Dockerfile` | `ghcr.io/abelisboa/trisla-decision-engine:nasp-a2` | `helm/trisla/` | `trisla` | 8082 | 2 |
| **SLA-Agent Layer** | `apps/sla-agent-layer/` | `apps/sla-agent-layer/Dockerfile` | `ghcr.io/abelisboa/trisla-sla-agent-layer:nasp-a2` | `helm/trisla/` | `trisla` | 8084 | 3 |
| **NASP Adapter** | `apps/nasp-adapter/` | `apps/nasp-adapter/Dockerfile` | `ghcr.io/abelisboa/trisla-nasp-adapter:nasp-a2` | `helm/trisla/` | `trisla` | 8085 | 2 |
| **UI Dashboard** | `apps/ui-dashboard/` | `apps/ui-dashboard/Dockerfile` | `ghcr.io/abelisboa/trisla-ui-dashboard:nasp-a2` | `helm/trisla/` | `trisla` | 80 | 2 |
| **Besu** | `besu/` | `besu/Dockerfile` | `hyperledger/besu:23.10.1` ✅ | `helm/trisla/` (subchart) | `trisla` | 8545/8546 | 1 |

---

## VALIDAÇÃO DE CONSISTÊNCIA

### ✅ Validações Bem-Sucedidas

1. **Paths Locais**: Todos os paths existem e contêm código fonte
2. **Dockerfiles**: Todos os Dockerfiles existem nos paths corretos
3. **Helm Chart**: Chart principal `helm/trisla/` existe e contém templates para todos os módulos
4. **Namespace**: Todos os módulos usam namespace `trisla`
5. **Besu Dockerfile**: Usa tag fixa `23.10.1` (não usa `latest`)

### ✅ CORREÇÕES APLICADAS (PASSO 0)

**Data:** 2025-01-15  
**Status:** Todas as inconsistências corrigidas

#### 1. Tag BC-NSSMF Unificada ✅
- **Versão canônica**: `v3.7.11`
- **Status**: Padronizada em `helm/trisla/values.yaml` e documentação
- **Motivo**: Build report, release e correções documentadas nesta versão

#### 2. Besu com Tag Fixa ✅
- **Versão canônica**: `23.10.1`
- **Status**: Corrigido em `helm/trisla/values.yaml` (duas ocorrências)
- **Motivo**: Reprodutibilidade experimental e aderência a boas práticas DevOps

#### 3. Componentes de Observabilidade com Tags Versionadas ✅
- **Kafka**: `3.6.1` ✅
- **OpenTelemetry Collector**: `0.92.0` ✅
- **Prometheus**: `v2.49.1` ✅
- **Grafana**: `10.2.3` ✅
- **Status**: Todas as tags `latest` removidas e substituídas por versões fixas
- **Motivo**: Reprodutibilidade experimental e conformidade com regras do projeto

---

## CONTEXTO FIXO APLICADO

- **Diretório raiz local**: `C:\Users\USER\Documents\TriSLA-clean` (Windows) ou `/mnt/c/Users/USER/Documents/TriSLA-clean` (WSL)
- **Registry**: `ghcr.io/abelisboa`
- **Namespace Kubernetes**: `trisla`
- **Helm Chart**: `helm/trisla/`
- **Build**: Sempre local
- **Deploy**: Sempre manual via `ssh node006 → cd /home/porvir5g/gtp5g/trisla`
- **Proibição**: Tags `latest` não permitidas
- **Ambiente experimental**: NASP

---

## DETALHAMENTO POR MÓDULO

### SEM-CSMF
- **Path**: `apps/sem-csmf/`
- **Porta**: `8080`
- **Replicas**: `2`
- **Imagem**: `ghcr.io/abelisboa/trisla-sem-csmf:nasp-a2`
- **Status**: ✅ Consistente

### ML-NSMF
- **Path**: `apps/ml-nsmf/`
- **Porta**: `8081`
- **Replicas**: `2`
- **Imagem**: `ghcr.io/abelisboa/trisla-ml-nsmf:nasp-a2`
- **KAFKA_ENABLED**: `false` (modo degraded)
- **Status**: ✅ Consistente

### BC-NSSMF
- **Path**: `apps/bc-nssmf/`
- **Porta**: `8083`
- **Replicas**: `2`
- **Imagem**: `ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.11` ✅
- **TRISLA_RPC_URL**: `http://trisla-besu:8545` (configurado automaticamente se Besu habilitado)
- **Status**: ✅ Versão canônica padronizada no PASSO 0

### Decision Engine
- **Path**: `apps/decision-engine/`
- **Porta**: `8082`
- **Replicas**: `2`
- **Imagem**: `ghcr.io/abelisboa/trisla-decision-engine:nasp-a2`
- **Status**: ✅ Consistente

### SLA-Agent Layer
- **Path**: `apps/sla-agent-layer/`
- **Porta**: `8084`
- **Replicas**: `3`
- **Imagem**: `ghcr.io/abelisboa/trisla-sla-agent-layer:nasp-a2`
- **Status**: ✅ Consistente

### NASP Adapter
- **Path**: `apps/nasp-adapter/`
- **Porta**: `8085`
- **Replicas**: `2`
- **Imagem**: `ghcr.io/abelisboa/trisla-nasp-adapter:nasp-a2`
- **Status**: ✅ Consistente

### UI Dashboard
- **Path**: `apps/ui-dashboard/`
- **Porta**: `80`
- **Replicas**: `2`
- **Imagem**: `ghcr.io/abelisboa/trisla-ui-dashboard:nasp-a2`
- **Ingress**: Habilitado (`trisla.local`)
- **Status**: ✅ Consistente

### Besu
- **Path**: `besu/`
- **RPC HTTP**: `8545`
- **RPC WS**: `8546`
- **P2P**: `30303`
- **Chain ID**: `1337`
- **Replicas**: `1`
- **Imagem**: `hyperledger/besu:23.10.1` ✅
- **Status**: ✅ Versão canônica padronizada no PASSO 0 (Dockerfile e values.yaml sincronizados)

---

## MAPEAMENTO SPRINT → MÓDULOS

| Sprint | Módulo Principal | Módulos Relacionados | Observações |
|--------|------------------|----------------------|-------------|
| **S1** | SEM-CSMF | - | Ontologia, GST→NEST, NLP |
| **S2** | ML-NSMF | - | LSTM, XAI, métricas Prometheus |
| **S3** | BC-NSSMF | Besu | Smart Contracts, eventos on-chain |
| **S4** | SLA-Agent Layer | NASP Adapter | Agentes RAN/Transport/Core, NSI/NSSI |
| **S5** | Observability + Adaptação | Decision Engine, Prometheus, Grafana, OTEL | SLOs, dashboards, loop de adaptação |

---

## PRÓXIMOS PASSOS

1. ✅ **PASSO 0 concluído**: Todas as inconsistências corrigidas (2025-01-15)
2. ✅ **Executar prompts**: Usar os 10 prompts gerados (5 sprints × 2: LOCAL e NASP)
3. ✅ **Baseline limpo**: Pronto para execução dos sprints técnicos

---

**FIM DO BASELINE_SUMMARY**

