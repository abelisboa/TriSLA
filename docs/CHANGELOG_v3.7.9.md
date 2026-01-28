# Changelog TriSLA v3.7.9

**Data de Release:** 2025-01-XX  
**Status:** ✅ Release Completo

---

## 🎯 Resumo da Release

A versão **3.7.9** integra **observability completa** em todos os módulos Python do TriSLA, fornecendo métricas Prometheus e traces OpenTelemetry para monitoramento end-to-end do sistema.

---

## ✨ Novas Funcionalidades

### Observability Integrada

- ✅ **Métricas Prometheus**: Todos os módulos expõem métricas em `/metrics`
- ✅ **Traces OpenTelemetry**: Traces distribuídos com propagação de contexto
- ✅ **Instrumentação Automática**: FastAPI e gRPC instrumentados automaticamente
- ✅ **Propagação de Contexto**: Suporte a B3 e TraceContext

### Build e Deploy

- ✅ **Scripts Automatizados**: Build e push automatizados de todas as imagens
- ✅ **Helm Values Atualizados**: Tags atualizadas para `3.7.9` no `values-nasp.yaml`
- ✅ **Documentação Completa**: Guias atualizados para build, push e deploy

---

## 🔧 Mudanças Técnicas

### Dependências

**Adicionadas:**
- `opentelemetry-api>=1.24.0`
- `opentelemetry-sdk>=1.24.0`
- `opentelemetry-instrumentation-fastapi>=0.44b0`
- `opentelemetry-exporter-otlp-proto-grpc>=1.24.0`
- `opentelemetry-instrumentation-grpc>=0.44b0`
- `opentelemetry-propagator-b3>=1.24.0`
- `prometheus_client>=0.20.0`

**Removidas:**
- `opentelemetry-propagator-tracecontext>=1.24.0` (não existe como pacote separado; incluído no `opentelemetry-api`)

**Corrigidas:**
- Conflito de versões OpenTelemetry no `sem-csmf` (atualizado `opentelemetry-instrumentation-fastapi` de `0.42b0` para `>=0.44b0`)

### Estrutura de Arquivos

**Novos arquivos:**
```
apps/{module}/src/observability/
├── __init__.py
├── metrics.py          # Métricas Prometheus
├── tracing_base.py     # Setup base OpenTelemetry
└── tracing.py          # Traces específicos do módulo
```

### Imagens Docker

**Tags atualizadas:**
- Todas as imagens agora usam tag `3.7.9`
- Tags `latest` também atualizadas

**Módulos construídos:**
1. `trisla-sem-csmf:3.7.9`
2. `trisla-ml-nsmf:3.7.9`
3. `trisla-decision-engine:3.7.9`
4. `trisla-bc-nssmf:3.7.9`
5. `trisla-sla-agent-layer:3.7.9`

---

## 🐛 Correções

### Build

- ✅ **Corrigido conflito de dependências OpenTelemetry** no `sem-csmf`
- ✅ **Removida dependência inexistente** `opentelemetry-propagator-tracecontext`
- ✅ **Alinhadas versões** de `opentelemetry-instrumentation-fastapi` em todos os módulos

### Helm

- ✅ **Atualizado `values-nasp.yaml`** com tags `3.7.9` para todos os módulos Python
- ✅ **Mantidas configurações** de `naspAdapter` e `uiDashboard` (não construídos na v3.7.9)

---

## 📚 Documentação

### Novos Documentos

- ✅ `docs/OBSERVABILITY_v3.7.9.md` — Guia completo de observability
- ✅ `docs/deployment/DEPLOY_v3.7.9.md` — Guia de deploy v3.7.9
- ✅ `VALIDACAO_BUILD_3.7.9_PROXIMOS_PASSOS.md` — Validação e próximos passos
- ✅ `ATUALIZACAO_HELM_VALUES_3.7.9.md` — Confirmação de atualização Helm
- ✅ `ANALISE_ERROS_BUILD_3.7.9.md` — Análise de erros e correções
- ✅ `CORRECAO_APLICADA_SEM_CSMF_3.7.9.md` — Correção aplicada no sem-csmf

### Documentos Atualizados

- ✅ `README.md` — Versão atualizada para 3.7.9, seção de build/push adicionada
- ✅ `docs/ghcr/GHCR_PUBLISH_GUIDE.md` — Atualizado com informações v3.7.9

---

## 🚀 Próximos Passos

### Deploy no NASP

1. ✅ **Imagens construídas** e disponíveis no GHCR
2. ✅ **Helm values atualizados** com tags `3.7.9`
3. ⏳ **Deploy no NASP** via Helm
4. ⏳ **Validação pós-deploy** (health checks, métricas, traces)

### Validação

- ⏳ Verificar health checks de todos os módulos
- ⏳ Validar métricas Prometheus expostas
- ⏳ Validar traces OpenTelemetry sendo enviados
- ⏳ Testar interfaces I-01 a I-07

---

## 📊 Estatísticas

- **Módulos instrumentados:** 5/5 (100%)
- **Imagens construídas:** 5/5 (100%)
- **Imagens no GHCR:** 5/5 (100%)
- **Helm values atualizados:** ✅ Sim
- **Documentação:** ✅ Completa

---

## 🔗 Links Relacionados

- **Guia de Observability**: [`docs/OBSERVABILITY_v3.7.9.md`](OBSERVABILITY_v3.7.9.md)
- **Guia de Deploy**: [`docs/deployment/DEPLOY_v3.7.9.md`](deployment/DEPLOY_v3.7.9.md)
- **Validação Build**: [`VALIDACAO_BUILD_3.7.9_PROXIMOS_PASSOS.md`](../../VALIDACAO_BUILD_3.7.9_PROXIMOS_PASSOS.md)
- **Guia GHCR**: [`docs/ghcr/GHCR_PUBLISH_GUIDE.md`](ghcr/GHCR_PUBLISH_GUIDE.md)

---

**Status:** ✅ Release v3.7.9 completo e documentado














