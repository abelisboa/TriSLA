# 43 – Testes de Carga, Stress e Robustez Operacional  
**TriSLA – Avaliação Sob Alta Concurrency, Falhas e Saturação de Recursos**

---

## 🎯 Objetivo Geral
Avaliar a resiliência, escalabilidade e robustez da arquitetura TriSLA sob condições extremas ou próximas ao limite operacional.

Os testes têm o propósito de provar:
- comportamento sob alta carga  
- latência distribuída  
- limites de throughput dos módulos  
- capacidade de resiliência  
- estabilidade das interfaces gRPC, REST e Kafka  
- consumo de CPU/memória  
- comportamento da blockchain sob múltiplas transações  

---

# 1. Tipos de Testes a Realizar

## 🧪 **1. Teste de Carga (Load Test)**
Simular:
- 50 a 500 intenções simultâneas  
- 20 URLLC + 15 eMBB + 100 mMTC  
- repetição contínua por 15 minutos  

Ferramentas:
- Locust  
- K6  
- Vegeta  
- JMeter  

Validações:
- SEM-CSMF → latência < limite  
- ML-NSMF → resposta estável  
- Decision Engine → fila sem perda  
- BC-NSSMF → transações estáveis  
- NASP → provisionamento sem degradação crítica  

---

## 🧪 **2. Teste de Stress**
Objetivo:  
Forçar saturação para medir comportamento de falha controlada.

Cargas extremas:
- 1000 intenções simultâneas  
- 500 transações blockchain em sequência  
- 300 mudanças de status SLA  

Validações:
- Degradação controlada  
- Manutenção de integridade  
- Ausência de crash do Decision Engine  
- Blockchain continua propagando blocos  
- SLO Reporter funciona mesmo sob atraso  

---

## 🧪 **3. Teste de Robustez**
Simular falhas:

- queda de um nó Kubernetes  
- latência artificial (tc/netem)  
- falha na blockchain RPC  
- partição de rede  
- perda do exporter Prometheus  

Validações:
- reconfiguração automática  
- Decision Engine tenta fallback  
- BC-NSSMF reenvia transação  
- SEM/ML continuam funcionando  

---

## 🧪 **4. Teste de Confiabilidade Blockchain**
Medir:

- TPS (transactions per second)  
- tempo médio de bloco  
- falhas IBFT2  
- retransmissão de transações  
- comportamento sob forks benignos  

Resultados esperados:
- consenso estável  
- tx throughput > 50 tps (laboratório)  
- violação on-chain registrada mesmo sob stress  

---

# 2. Relatórios e Métricas
Gerar relatórios:

- CPU / RAM de cada módulo  
- Latência entre etapas  
- Estatísticas de falha  
- ESB / gRPC dumps  
- Métricas Prometheus  
- Logs Loki consolidados  

---

# 3. Critérios de Sucesso

- O sistema permanece funcional acima de 70% da carga nominal  
- Nenhuma perda de SLA on-chain  
- Todas as violações registradas  
- Nenhum crash do Decision Engine  
- Recuperação após falhas induzidas  

---

# 4. Evidências para a dissertação

- Gráficos comparativos (Grafana)  
- Estatísticas de previsão ML  
- Registros blockchain (tx_hash, blockNumber)  
- Relatórios Latência vs. Throughput  
- Logs de falha e recuperação  

---

# ✔ Pronto para implementação no Cursor
