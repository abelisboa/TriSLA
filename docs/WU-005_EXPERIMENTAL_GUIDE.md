# 🧪 WU-005 — Guia de Avaliação Experimental TriSLA@NASP

**Data:** 2025-10-17  
**Responsável:** Abel José Rodrigues Lisboa  
**Ambiente:** NASP@UNISINOS

---

## 🎯 OBJETIVO

Executar a avaliação experimental completa da arquitetura TriSLA no ambiente NASP, validando o comportamento integrado dos módulos SEM-NSMF, ML-NSMF e BC-NSSMF em cenários controlados de requisição, decisão e enforcement de SLAs em redes 5G/O-RAN.

---

## 🧩 ESTRUTURA DOS EXPERIMENTOS

### Arquitetura Experimental

```
┌─────────────────────────────────────────────────────────────┐
│                    NASP Environment                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  SEM-NSMF    │  │  ML-NSMF     │  │  BC-NSSMF    │     │
│  │  Semantic    │  │  AI/ML       │  │  Blockchain  │     │
│  │  Processing  │  │  Prediction  │  │  Enforcement │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         │                 │                  │             │
│         └─────────────────┼──────────────────┘             │
│                           │                                │
│                  ┌────────▼────────┐                       │
│                  │  Integration    │                       │
│                  │  Gateway        │                       │
│                  └─────────────────┘                       │
│                           │                                │
│                  ┌────────▼────────┐                       │
│                  │  Monitoring     │                       │
│                  │  & Metrics      │                       │
│                  └─────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo Experimental

1. **Entrada:** Intent em linguagem natural
2. **Processamento Semântico:** SEM-NSMF → NEST
3. **Predição ML:** ML-NSMF → Viabilidade + XAI
4. **Enforcement:** BC-NSSMF → Smart Contract
5. **Observação:** Monitoring → Métricas + Logs

---

## 🎯 CENÁRIOS EXPERIMENTAIS

### Cenário 1: URLLC (Ultra-Reliable Low-Latency Communications)

**Aplicação:** Telemedicina - Cirurgia Remota Assistida por Robô

**SLOs:**
- Latência p99: < 10ms
- Confiabilidade: > 99.999%
- Jitter: < 2ms
- Taxa de erro: < 0.1%

**Intent de Teste:**
```json
{
  "request": "cirurgia remota",
  "sla_requirements": {
    "latency_max": "10ms",
    "reliability_min": "99.999%",
    "jitter_max": "2ms"
  }
}
```

**Métricas Esperadas:**
- Latência p99: 8-10ms
- Confiabilidade: 99.999%+
- Jitter: < 2ms
- Throughput: 50 Mbps

### Cenário 2: eMBB (Enhanced Mobile Broadband)

**Aplicação:** Streaming 4K + Realidade Aumentada

**SLOs:**
- Throughput: ≥ 1 Gbps
- Latência p99: < 50ms
- Confiabilidade: > 99.9%
- Taxa de erro: < 1%

**Intent de Teste:**
```json
{
  "request": "streaming 4k",
  "sla_requirements": {
    "throughput_min": "1000Mbps",
    "latency_max": "50ms",
    "reliability_min": "99.9%"
  }
}
```

**Métricas Esperadas:**
- Throughput: 1-1.5 Gbps
- Latência p99: 30-50ms
- Confiabilidade: 99.9%+
- Uso de recursos: Alto

### Cenário 3: mMTC (Massive Machine Type Communications)

**Aplicação:** Sensores IoT Industriais (10,000 dispositivos)

**SLOs:**
- Conexões simultâneas: ≥ 10,000
- Latência p99: < 100ms
- Taxa de conexão: > 98%
- Eficiência energética: Bateria > 10 anos

**Intent de Teste:**
```json
{
  "request": "iot massivo",
  "sla_requirements": {
    "device_count": "10000",
    "latency_max": "100ms",
    "connection_rate_min": "98%"
  }
}
```

**Métricas Esperadas:**
- Conexões simultâneas: 10,000+
- Latência p99: 80-100ms
- Taxa de conexão: 98%+
- Throughput/dispositivo: 1-2 kbps

---

## 🧠 HIPÓTESES A VALIDAR

### H1: SLA Awareness (SEM-NSMF)
**Hipótese:** O módulo SEM-NSMF converte intenções em linguagem natural para NESTs com precisão ≥ 95%.

**Métricas de Validação:**
- Taxa de mapeamento correto: ≥ 95%
- Tempo de processamento semântico: < 100ms
- Validação de NESTs gerados: 100%

**Evidências:**
- Logs de processamento semântico
- NESTs gerados e validados
- Tempo de resposta do SEM-NSMF

### H2: Decision Intelligence (ML-NSMF)
**Hipótese:** O módulo ML-NSMF prediz violações de SLA com acurácia ≥ 90% e explica decisões via XAI.

**Métricas de Validação:**
- Precisão das predições LSTM: ≥ 90%
- Confiança das predições: ≥ 85%
- Feature importance (SHAP): Documentado
- Tempo de inferência: < 200ms

**Evidências:**
- Logs de predições ML
- Explicações SHAP
- Métricas de confiança

### H3: Smart Enforcement (BC-NSSMF)
**Hipótese:** O módulo BC-NSSMF executa contratos inteligentes com compliance ≥ 99% e rastreabilidade completa.

**Métricas de Validação:**
- Taxa de compliance contratual: ≥ 99%
- Tempo de execução de contratos: < 500ms
- Rastreabilidade de transações: 100%
- Precisão dos oracles: ≥ 95%

**Evidências:**
- Logs de contratos blockchain
- Transações registradas
- Compliance reports

---

## 📊 MÉTRICAS E KPIs

### Métricas de SLA por Cenário

| Métrica | URLLC | eMBB | mMTC |
|---------|-------|------|------|
| Latência p99 | < 10ms | < 50ms | < 100ms |
| Throughput | 50 Mbps | ≥ 1 Gbps | 1-2 kbps/device |
| Confiabilidade | > 99.999% | > 99.9% | > 98% |
| Jitter | < 2ms | < 10ms | < 20ms |
| Taxa de erro | < 0.1% | < 1% | < 5% |

### Métricas de Sistema

| Métrica | Valor Esperado |
|---------|----------------|
| CPU Usage | < 80% por pod |
| Memory Usage | < 1Gi por pod |
| Pod Restarts | 0 |
| Network I/O | Conforme SLO |
| Uptime | 100% |

### Métricas de IA/ML

| Métrica | Valor Esperado |
|---------|----------------|
| Precisão LSTM | ≥ 90% |
| Confiança predição | ≥ 85% |
| Tempo inferência | < 200ms |
| SHAP explanations | Documentadas |

### Métricas de Blockchain

| Métrica | Valor Esperado |
|---------|----------------|
| Compliance rate | ≥ 99% |
| Transaction time | < 500ms |
| Oracle accuracy | ≥ 95% |
| Traceability | 100% |

---

## 🛠️ FERRAMENTAS E SCRIPTS

### Scripts de Automação

1. **`run_experiments.sh`** — Execução automatizada dos 3 cenários
   - Duração: 90 minutos (30 min por cenário)
   - Carga: 1, 10, 100 req/s respectivamente
   - Coleta automática de métricas

2. **`collect_metrics.sh`** — Coleta contínua de métricas
   - Intervalo: 10 segundos
   - Métricas: CPU, Memory, Network
   - Exportação: CSV format

3. **`generate_report.sh`** — Geração do relatório final
   - Consolidação de resultados
   - Análise estatística
   - Validação de hipóteses

### Comandos de Monitoramento

```bash
# Status dos pods TriSLA
kubectl get pods -n trisla-nsp -o wide

# Métricas em tempo real
kubectl top pods -n trisla-nsp

# Logs dos módulos
kubectl logs -n trisla-nsp -l app=trisla-ai --tail=100

# Health checks
kubectl exec -n trisla-nsp deploy/trisla-semantic-layer -- \
  curl -s http://localhost:8080/health

# Teste de comunicação
kubectl exec -n trisla-nsp deploy/trisla-integration-layer -- \
  curl -s http://trisla-semantic:8080/health
```

---

## 📋 CHECKLIST DE EXECUÇÃO

### Pré-requisitos
- [ ] Pods TriSLA em status Running (5 pods)
- [ ] Conectividade entre módulos validada
- [ ] Observabilidade ativa (Prometheus/Grafana)
- [ ] Scripts de experimento preparados
- [ ] Estrutura de dados criada
- [ ] Namespace `trisla-nsp` ativo

### Execução dos Cenários
- [ ] Cenário URLLC executado (30 min, 1 req/s)
- [ ] Cenário eMBB executado (30 min, 10 req/s)
- [ ] Cenário mMTC executado (30 min, 100 req/s)
- [ ] Métricas coletadas continuamente
- [ ] Logs exportados
- [ ] Contratos blockchain validados

### Pós-processamento
- [ ] Análise estatística realizada
- [ ] Hipóteses H1, H2, H3 validadas
- [ ] Relatório final gerado
- [ ] Evidências documentadas
- [ ] Resultados consolidados
- [ ] Conformidade SLA calculada

---

## 📁 ESTRUTURA DE RESULTADOS

### Diretórios de Saída

```
experiments/results/
├── metrics/
│   ├── pod_metrics.csv
│   ├── node_metrics.csv
│   ├── prometheus_export.json
│   └── nwdaf_metrics.json
├── logs/
│   ├── urllc_scenario.log
│   ├── embb_scenario.log
│   ├── mmtc_scenario.log
│   └── trisla_modules.log
├── contracts/
│   ├── urllc_contracts.json
│   ├── embb_contracts.json
│   └── mmtc_contracts.json
├── scenarios/
│   ├── urllc_results.json
│   ├── embb_results.json
│   └── mmtc_results.json
└── reports/
    ├── experimental_summary.md
    ├── hypothesis_validation.json
    └── WU-005_FINAL_REPORT.md
```

### Arquivos de Evidência

| Arquivo | Descrição |
|---------|-----------|
| `experiments.log` | Log principal da execução |
| `experiment_config.json` | Configuração dos experimentos |
| `pod_metrics.csv` | Métricas de CPU/Memory dos pods |
| `node_metrics.csv` | Métricas dos nodes |
| `*_scenario.log` | Logs específicos de cada cenário |
| `*_results.json` | Resultados consolidados por cenário |
| `WU-005_FINAL_REPORT.md` | Relatório final completo |

---

## 🎯 CRITÉRIOS DE SUCESSO

### Conformidade SLA Global
- **URLLC:** 6/7 métricas dentro do SLO (85.7%)
- **eMBB:** 7/7 métricas dentro do SLO (100%)
- **mMTC:** 8/8 métricas dentro do SLO (100%)
- **Média geral:** ≥ 95% de conformidade

### Performance do Sistema
- **Uptime:** 100% durante experimentos
- **Pod restarts:** 0
- **Latência média:** < 50ms
- **Throughput:** Conforme SLOs por cenário

### Validação de Hipóteses
- **H1 (SEM-NSMF):** Precisão semântica ≥ 95%
- **H2 (ML-NSMF):** Acurácia ML ≥ 90%
- **H3 (BC-NSSMF):** Compliance blockchain ≥ 99%

---

## 🚀 COMO EXECUTAR

### Passo 1: Preparação

```bash
# Conectar ao NASP
ssh porvir5g@node1
cd /home/porvir5g/gtp5g/trisla-nsp

# Verificar pods TriSLA
kubectl get pods -n trisla-nsp

# Verificar conectividade
kubectl exec -n trisla-nsp deploy/trisla-semantic-layer -- \
  curl -s http://localhost:8080/health
```

### Passo 2: Execução Automatizada

```bash
# Executar experimentos completos
chmod +x scripts/run_experiments.sh
./scripts/run_experiments.sh
```

### Passo 3: Monitoramento

```bash
# Em outro terminal, monitorar progresso
tail -f experiments/results/experiments.log

# Ver métricas em tempo real
kubectl top pods -n trisla-nsp
```

### Passo 4: Análise

```bash
# Gerar relatório final
chmod +x scripts/generate_report.sh
./scripts/generate_report.sh

# Ver resultados
cat experiments/results/reports/WU-005_FINAL_REPORT.md
```

---

## ⚠️ TROUBLESHOOTING

### Problema: Pods não respondem

```bash
# Verificar status
kubectl get pods -n trisla-nsp
kubectl describe pod -n trisla-nsp {pod-name}

# Ver logs
kubectl logs -n trisla-nsp {pod-name}
```

### Problema: Métricas não coletadas

```bash
# Verificar Prometheus
kubectl get svc -n monitoring | grep prometheus

# Verificar port-forward
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
```

### Problema: Scripts não executam

```bash
# Verificar permissões
chmod +x scripts/*.sh

# Verificar dependências
which kubectl
which curl
which jq
```

---

## 📞 SUPORTE

**Responsável:** Abel José Rodrigues Lisboa  
**Email:** abel.lisboa@unisinos.br  
**Instituição:** UNISINOS — Mestrado em Computação Aplicada  
**Projeto:** TriSLA@NASP

**Ambiente:** NASP@UNISINOS  
**Cluster:** node1/node2 (Dell R430)  
**Namespace:** trisla-nsp

---

## 🎓 CONTRIBUIÇÃO PARA A DISSERTAÇÃO

Esta avaliação experimental fornece:

1. **Dados empíricos** dos três cenários representativos
2. **Validação das hipóteses** H1, H2, H3
3. **Demonstração de comportamento** SLA-aware
4. **Explicabilidade via SHAP** (XAI)
5. **Rastreabilidade via blockchain**
6. **Logs estruturados** conforme padrão do Apêndice H
7. **Métricas Prometheus e NWDAF** completas

---

**🎯 WU-005 PREPARADA PARA EXECUÇÃO EXPERIMENTAL! 🎯**

📅 17/10/2025 | 👤 Abel José Rodrigues Lisboa | 🏛️ UNISINOS
