# SESSION_WU005_INIT.md  
### Fase: WU-005 — Avaliação Experimental TriSLA@NASP  
**Autor:** Abel Lisboa  
**Ambiente:** NASP Kubernetes (node1/node2 – Dell R430)  
**Data:** 2025-10-17  
**Versão:** 2025.10 – Fase Experimental  

---

## 🎯 OBJETIVO GERAL
Executar a **avaliação experimental da arquitetura TriSLA** no ambiente NASP, validando o comportamento integrado dos módulos SEM-NSMF, ML-NSMF e BC-NSSMF em cenários controlados de requisição, decisão e enforcement de SLAs em redes 5G/O-RAN.

---

## 🧩 CONTEXTO OPERACIONAL
O ambiente NASP encontra-se estabilizado e auditado (vide `/tmp/nasp_env_final_report.txt`), com:
- Kubernetes 1.28.15 (node1) e 1.31.1 (node2) operacionais;  
- CRI-O + Multus + Calico ativos;  
- Namespaces ativos: `trisla-nsp`, `nonrtric`, `semantic`, `open5gs`, `monitoring`;  
- Pods TriSLA executando (AI-Layer, Blockchain-Layer, Integration-Layer, Semantic-Layer, Monitoring-Layer).  

---

## ⚙️ ARQUITETURA EXPERIMENTAL
A Fase WU-005 executará experimentos com base em três eixos:
1. **SLA Awareness** — entrada semântica via módulo SEM-NSMF e ontologia TriSLA.  
2. **Decision Intelligence** — predição e validação com ML-NSMF (LSTM, XAI, federated reasoning).  
3. **Smart Enforcement** — verificação de conformidade e logging por contratos inteligentes (BC-NSSMF).  

Os experimentos seguem as recomendações dos Apêndices A, E e H da proposta técnica.  

---

## 🧠 RECURSOS E ESTRUTURA

### Ambiente de Execução
- **Cluster:** NASP@UNISINOS (2 nodes Dell R430)
- **Namespace:** `trisla-nsp`
- **Módulos ativos:** 5 (SEM, ML, BC, Integration, Monitoring)
- **Observabilidade:** Prometheus + Grafana + Jaeger + Loki

### Estrutura de Dados
```
/home/porvir5g/gtp5g/trisla-nsp/
├── experiments/
│   ├── scenarios/
│   │   ├── urllc/
│   │   ├── embb/
│   │   └── mmtc/
│   ├── data/
│   │   ├── intents/
│   │   ├── predictions/
│   │   └── contracts/
│   └── results/
│       ├── metrics/
│       ├── logs/
│       └── reports/
└── scripts/
    ├── run_experiments.sh
    ├── collect_metrics.sh
    └── generate_report.sh
```

---

## 🎯 CENÁRIOS EXPERIMENTAIS

### Cenário 1: URLLC (Ultra-Reliable Low-Latency Communications)
**Aplicação:** Telemedicina - Cirurgia Remota Assistida por Robô
- **SLOs:** Latência < 10ms, Confiabilidade > 99.999%, Jitter < 2ms
- **Carga:** 1 requisição/s por 30 minutos
- **Métricas:** p99 latência, taxa de erro, compliance contratual

### Cenário 2: eMBB (Enhanced Mobile Broadband)
**Aplicação:** Streaming 4K + Realidade Aumentada
- **SLOs:** Throughput ≥ 1 Gbps, Latência < 50ms, Confiabilidade > 99.9%
- **Carga:** 10 requisições/s por 30 minutos
- **Métricas:** throughput, latência média, uso de recursos

### Cenário 3: mMTC (Massive Machine Type Communications)
**Aplicação:** Sensores IoT Industriais
- **SLOs:** 10k conexões simultâneas, Latência < 100ms, Taxa conexão > 98%
- **Carga:** 100 requisições/s por 30 minutos
- **Métricas:** conexões simultâneas, eficiência energética, escalabilidade

---

## 📊 MÉTRICAS E KPIs

### Métricas de SLA
- **Latência:** p50, p90, p95, p99 (ms)
- **Throughput:** Mbps/Gbps por cenário
- **Confiabilidade:** uptime, packet loss, error rate
- **Jitter:** variação de latência
- **Disponibilidade:** % de tempo operacional

### Métricas de IA/ML
- **Precisão de predição:** acurácia do modelo LSTM
- **Confiança:** score de confiança das predições
- **Explicabilidade:** SHAP feature importance
- **Tempo de inferência:** latência do modelo ML

### Métricas de Blockchain
- **Compliance rate:** % de contratos cumpridos
- **Transaction time:** tempo de criação/validação
- **Block confirmation:** tempo de confirmação
- **Oracle accuracy:** precisão dos oracles NWDAF

### Métricas de Sistema
- **CPU usage:** % por pod e node
- **Memory usage:** MiB/GiB por pod
- **Network I/O:** throughput de rede
- **Pod restarts:** número de reinicializações

---

## 🔬 METODOLOGIA EXPERIMENTAL

### Fase 1: Preparação (5 min)
1. Verificar status dos pods TriSLA
2. Validar conectividade entre módulos
3. Configurar coleta de métricas
4. Inicializar observabilidade

### Fase 2: Execução dos Cenários (90 min)
1. **URLLC:** 30 minutos de carga
2. **eMBB:** 30 minutos de carga
3. **mMTC:** 30 minutos de carga

### Fase 3: Coleta e Análise (15 min)
1. Exportar métricas Prometheus
2. Coletar logs estruturados
3. Validar contratos blockchain
4. Gerar relatório consolidado

---

## 🛠️ FERRAMENTAS E SCRIPTS

### Scripts de Automação
- `run_experiments.sh` — Execução automatizada dos 3 cenários
- `collect_metrics.sh` — Coleta de métricas Prometheus/NWDAF
- `generate_report.sh` — Geração do relatório final
- `validate_sla.sh` — Validação de conformidade SLA

### Comandos de Monitoramento
```bash
# Status dos pods
kubectl get pods -n trisla-nsp -o wide

# Métricas em tempo real
kubectl top pods -n trisla-nsp

# Logs dos módulos
kubectl logs -n trisla-nsp -l app=trisla-ai --tail=100

# Health checks
kubectl exec -n trisla-nsp deploy/trisla-semantic-layer -- curl -s http://localhost:8080/health
```

---

## 📈 HIPÓTESES A VALIDAR

### H1: SLA Awareness
**Hipótese:** O módulo SEM-NSMF converte intenções em linguagem natural para NESTs com precisão ≥ 95%.

**Métricas:**
- Taxa de mapeamento correto
- Tempo de processamento semântico
- Validação de NESTs gerados

### H2: Decision Intelligence
**Hipótese:** O módulo ML-NSMF prediz violações de SLA com acurácia ≥ 90% e explica decisões via XAI.

**Métricas:**
- Precisão das predições LSTM
- Confiança das predições
- Feature importance (SHAP)
- Tempo de inferência

### H3: Smart Enforcement
**Hipótese:** O módulo BC-NSSMF executa contratos inteligentes com compliance ≥ 99% e rastreabilidade completa.

**Métricas:**
- Taxa de compliance contratual
- Tempo de execução de contratos
- Rastreabilidade de transações
- Precisão dos oracles

---

## 📋 CHECKLIST DE EXECUÇÃO

### Pré-requisitos
- [ ] Pods TriSLA em status Running
- [ ] Conectividade entre módulos validada
- [ ] Observabilidade ativa (Prometheus/Grafana)
- [ ] Scripts de experimento preparados
- [ ] Estrutura de dados criada

### Execução
- [ ] Cenário URLLC executado (30 min)
- [ ] Cenário eMBB executado (30 min)
- [ ] Cenário mMTC executado (30 min)
- [ ] Métricas coletadas
- [ ] Logs exportados
- [ ] Contratos validados

### Pós-processamento
- [ ] Análise estatística realizada
- [ ] Hipóteses validadas
- [ ] Relatório gerado
- [ ] Evidências documentadas
- [ ] Resultados consolidados

---

## 📊 ESTRUTURA DE RESULTADOS

### Arquivos de Saída
```
experiments/results/
├── metrics/
│   ├── prometheus_export.json
│   ├── nwdaf_metrics.json
│   └── system_metrics.csv
├── logs/
│   ├── urllc_scenario.log
│   ├── embb_scenario.log
│   ├── mmtc_scenario.log
│   └── trisla_modules.log
├── contracts/
│   ├── urllc_contracts.json
│   ├── embb_contracts.json
│   └── mmtc_contracts.json
└── reports/
    ├── experimental_summary.md
    ├── hypothesis_validation.json
    └── performance_analysis.csv
```

---

## 🎯 CRITÉRIOS DE SUCESSO

### Conformidade SLA
- URLLC: 6/7 métricas dentro do SLO
- eMBB: 7/7 métricas dentro do SLO
- mMTC: 8/8 métricas dentro do SLO

### Performance do Sistema
- Uptime: 100% durante experimentos
- Pod restarts: 0
- Latência média: < 50ms
- Throughput: conforme SLOs

### Validação de Hipóteses
- H1: Precisão semântica ≥ 95%
- H2: Acurácia ML ≥ 90%
- H3: Compliance blockchain ≥ 99%

---

## 📞 SUPORTE E CONTATO

**Responsável:** Abel José Rodrigues Lisboa  
**Email:** abel.lisboa@unisinos.br  
**Instituição:** UNISINOS — Mestrado em Computação Aplicada  
**Projeto:** TriSLA@NASP

**Ambiente:** NASP@UNISINOS  
**Cluster:** node1/node2 (Dell R430)  
**Namespace:** trisla-nsp

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ Validar ambiente NASP
2. ✅ Preparar scripts de experimento
3. ✅ Configurar coleta de métricas
4. ✅ Executar cenários experimentais
5. ✅ Coletar e analisar resultados
6. ✅ Gerar relatório final
7. ✅ Documentar evidências

---

**🎯 SESSION WU-005 INICIALIZADA E PRONTA PARA EXECUÇÃO! 🎯**

📅 17/10/2025 | 👤 Abel José Rodrigues Lisboa | 🏛️ UNISINOS
