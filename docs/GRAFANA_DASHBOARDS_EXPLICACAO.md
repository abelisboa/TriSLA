# Explicação: Dashboards vs Métricas no Grafana

## ✅ **MÉTRICAS JÁ SÃO COLETADAS EM TEMPO REAL**

As métricas do TriSLA e NASP **já estão sendo coletadas automaticamente** pelo Prometheus:

### Como funciona:

1. **Prometheus do NASP** → Coleta métricas em tempo real (intervalo: 5s)
2. **Services expõem `/metrics`** → TriSLA Portal, Decision Engine, NWDAF, etc.
3. **Grafana consulta Prometheus** → Mostra métricas em tempo real via queries PromQL

### Configuração já existente:

```yaml
# Prometheus já configurado para coletar:
- job_name: 'nasp-prometheus'
  targets: ['nasp-prometheus.monitoring.svc.cluster.local:9090']
  
- job_name: 'trisla-api'
  targets: ['trisla-api:8000']
  
- job_name: 'decision-engine'
  targets: ['decision-engine:8080']
```

---

## 📊 **O QUE IMPORTA SÃO OS DASHBOARDS (VISUALIZAÇÕES)**

O que precisamos importar são **templates de visualização** (dashboards), não as métricas!

### Diferença:

| Item | O que é | Status |
|------|---------|--------|
| **Métricas** | Dados coletados do sistema | ✅ Já funcionando em tempo real |
| **Dashboards** | Visualizações/gráficos/templates | ⚠️ Precisa importar |

### Por que importar dashboards?

**Sem importar dashboards:**
- Você teria que criar manualmente cada gráfico no Grafana
- Ter que escrever todas as queries PromQL manualmente
- Configurar cada painel, cores, limites, etc.

**Com dashboards importados:**
- ✅ Visualizações prontas e organizadas
- ✅ Queries PromQL já configuradas
- ✅ Gráficos modernos e responsivos
- ✅ Links entre dashboards
- ✅ Variáveis interativas (templates)

---

## 🔄 **COMO FUNCIONA (Fluxo Real)**

```
┌─────────────────┐
│  TriSLA Services│
│  (expoem /metrics)
└────────┬────────┘
         │ Métricas HTTP
         ▼
┌─────────────────┐
│  Prometheus     │  ← Coleta automática (5s)
│  (NASP)         │
└────────┬────────┘
         │ Consulta em tempo real
         ▼
┌─────────────────┐
│  Grafana        │  ← Dashboard consulta Prometheus
│  (Dashboards)   │     Mostra dados em tempo real
└─────────────────┘
```

### Exemplo prático:

1. **TriSLA API** expõe: `http_request_total{method="POST"}`
2. **Prometheus** coleta automaticamente (a cada 5s)
3. **Dashboard Grafana** consulta: `rate(http_request_total[5m])`
4. **Gráfico atualiza** em tempo real conforme métricas chegam

---

## 🎯 **O QUE FAZER**

### ✅ Métricas (NÃO precisa fazer nada)
- Já estão sendo coletadas automaticamente
- Funcionam em tempo real
- Prometheus do NASP já configurado

### ⚠️ Dashboards (PRECISA importar)
- Importar templates de visualização
- Uma vez importado, dashboards consultam Prometheus automaticamente
- Métricas aparecem em tempo real nos gráficos

---

## 📋 **CHECKLIST**

- [x] Prometheus coletando métricas → **Já configurado**
- [x] Services expondo `/metrics` → **Já configurado**
- [ ] Dashboards importados no Grafana → **Fazer agora**
- [ ] Datasource Prometheus configurado → **Verificar se está OK**

---

## 🔍 **VERIFICAR MÉTRICAS EM TEMPO REAL**

### Via Prometheus:

```bash
# Consultar métricas diretamente do Prometheus
curl -s "http://nasp-prometheus.monitoring.svc.cluster.local:9090/api/v1/query?query=up{job=~'trisla.*'}" | jq .
```

### Via Grafana (após importar dashboards):

1. Abrir dashboard no Grafana
2. Métricas aparecem automaticamente em tempo real
3. Refresh automático a cada 10s-30s
4. Gráficos atualizam conforme novas métricas chegam

---

## 💡 **RESUMO**

> **Métricas = Dados** → Já funcionando ✅  
> **Dashboards = Visualização** → Precisa importar ⚠️  
> **Tempo Real = Automático** → Após importar dashboards, tudo funciona em tempo real ✅

Após importar os dashboards, eles **consultam o Prometheus em tempo real** automaticamente. Não há necessidade de "importar métricas" - elas já estão sendo coletadas!




