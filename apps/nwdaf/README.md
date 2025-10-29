# TriSLA NWDAF (Network Data Analytics Function)

## Visão Geral

O **NWDAF (Network Data Analytics Function)** é um componente central do TriSLA que implementa a função de análise de dados de rede conforme especificação 3GPP TS 23.288. Ele é responsável por coletar, analisar e processar dados de rede de múltiplas fontes para fornecer insights, predições e detecção de anomalias.

## Funcionalidades Principais

### 🔍 **Análise de Performance de Rede**
- Monitoramento de componentes do 5G Core (AMF, SMF, UPF, PCF, UDM, AUSF, NRF, NSSF)
- Análise de métricas de RAN (células, rádio, tráfego, handover, recursos)
- Monitoramento de transporte (links, largura de banda, latência, pacotes, QoS)
- Análise de aplicações (slices, UEs, métricas de serviço)

### 🔮 **Predição de QoS**
- Predição de latência, throughput, confiabilidade, jitter e perda de pacotes
- Suporte a perfis de QoS (URLLC, eMBB, mMTC)
- Análise de conformidade com requisitos de SLA
- Geração de recomendações baseadas em predições

### 📊 **Análise de Tráfego**
- Identificação de padrões de tráfego (burst, steady, periódico, esporádico)
- Análise de tendências de tráfego
- Análise de distribuição por slices
- Detecção de picos e anomalias de tráfego

### 🚨 **Detecção de Anomalias**
- Detecção de degradação de performance
- Identificação de picos de tráfego
- Detecção de falhas de conexão
- Identificação de esgotamento de recursos
- Detecção de anomalias de latência e perda de pacotes

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        NWDAF                                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Network   │  │    QoS      │  │   Traffic   │        │
│  │  Analyzer   │  │  Predictor  │  │  Analyzer   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Anomaly   │  │  Interface  │  │   Models    │        │
│  │  Detector   │  │   NWDAF     │  │   Data      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Estrutura do Projeto

```
apps/nwdaf/
├── main.py                    # Aplicação principal do NWDAF
├── models/
│   └── data_models.py         # Modelos de dados
├── analytics/
│   ├── network_analyzer.py    # Analisador de performance
│   ├── qos_predictor.py       # Preditor de QoS
│   ├── traffic_analyzer.py    # Analisador de tráfego
│   └── anomaly_detector.py    # Detector de anomalias
├── interfaces/
│   └── nwdaf_interface.py     # Interface de comunicação
├── requirements.txt           # Dependências Python
├── Dockerfile                 # Containerização
└── README.md                  # Este arquivo
```

## Instalação e Configuração

### 1. **Requisitos**
- Python 3.11+
- Docker
- Kubernetes
- Helm

### 2. **Instalação Local**
```bash
# Clonar o repositório
git clone https://github.com/abelisboa/TriSLA-Portal.git
cd TriSLA-Portal/apps/nwdaf

# Instalar dependências
pip install -r requirements.txt

# Executar o NWDAF
python main.py
```

### 3. **Instalação com Docker**
```bash
# Construir imagem
docker build -t trisla-nwdaf:latest .

# Executar container
docker run -p 8080:8080 trisla-nwdaf:latest
```

### 4. **Instalação com Kubernetes**
```bash
# Instalar com Helm
helm install nwdaf helm/nwdaf -n trisla

# Verificar status
kubectl get pods -l app.kubernetes.io/name=nwdaf -n trisla
```

## Configuração

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `NWDAF_ID` | ID único do NWDAF | `nwdaf-001` |
| `LOG_LEVEL` | Nível de log | `INFO` |
| `ANALYSIS_INTERVAL` | Intervalo de análise (s) | `30` |
| `CACHE_SIZE` | Tamanho do cache | `1000` |
| `MAX_HISTORY_SIZE` | Tamanho máximo do histórico | `10000` |

### Configuração de Thresholds

```yaml
thresholds:
  cpuUsage: 80          # % de utilização de CPU
  memoryUsage: 85       # % de utilização de memória
  latency: 50           # ms de latência máxima
  packetLoss: 0.01      # % de perda de pacotes
  throughput: 0.8       # % de utilização de throughput
  availability: 99.0    # % de disponibilidade
```

### Perfis de QoS

```yaml
qosProfiles:
  urllc:
    latencyRequirement: 1.0        # ms
    reliabilityRequirement: 99.999 # %
    throughputRequirement: 1.0     # Mbps
    jitterRequirement: 0.1         # ms
    packetLossRequirement: 0.00001 # %
  embb:
    latencyRequirement: 10.0       # ms
    reliabilityRequirement: 99.9   # %
    throughputRequirement: 1000.0  # Mbps
    jitterRequirement: 1.0         # ms
    packetLossRequirement: 0.001   # %
  mmtc:
    latencyRequirement: 100.0      # ms
    reliabilityRequirement: 99.0   # %
    throughputRequirement: 1.0     # Mbps
    jitterRequirement: 10.0        # ms
    packetLossRequirement: 0.01    # %
```

## API Endpoints

### **Health Check**
```http
GET /health
```

### **Readiness Check**
```http
GET /ready
```

### **Status do NWDAF**
```http
GET /api/v1/status
```

### **Métricas**
```http
GET /api/v1/metrics
```

### **Análises**
```http
GET /api/v1/analytics
POST /api/v1/analytics
```

### **Predições**
```http
GET /api/v1/predictions
POST /api/v1/predictions
```

### **Anomalias**
```http
GET /api/v1/anomalies
POST /api/v1/anomalies
```

### **Insights**
```http
GET /api/v1/insights
```

## Uso

### 1. **Inicialização**
```python
from apps.nwdaf.main import create_nwdaf

# Criar e inicializar NWDAF
nwdaf = await create_nwdaf("nwdaf-001")
await nwdaf.initialize()
await nwdaf.start()
```

### 2. **Análise de Dados**
```python
# Coletar dados de rede
network_data = await nwdaf._collect_network_data()

# Realizar análises
analytics = await nwdaf._perform_analyses(network_data)
```

### 3. **Obter Insights**
```python
# Obter insights consolidados
insights = await nwdaf.get_network_insights()
print(f"Saúde da rede: {insights['network_health']}")
```

### 4. **Monitoramento**
```python
# Obter status
status = nwdaf.get_status()
print(f"NWDAF rodando: {status['running']}")
```

## Monitoramento

### **Métricas do Prometheus**
- `nwdaf_analyses_total`: Total de análises realizadas
- `nwdaf_predictions_total`: Total de predições geradas
- `nwdaf_anomalies_total`: Total de anomalias detectadas
- `nwdaf_processing_time_seconds`: Tempo de processamento
- `nwdaf_confidence_score`: Score de confiança das análises

### **Logs**
```bash
# Ver logs do NWDAF
kubectl logs -l app.kubernetes.io/name=nwdaf -n trisla

# Ver logs em tempo real
kubectl logs -f -l app.kubernetes.io/name=nwdaf -n trisla
```

### **Dashboards**
- Grafana dashboard para visualização de métricas
- Alertas automáticos para anomalias críticas
- Relatórios de performance e QoS

## Troubleshooting

### **Problemas Comuns**

1. **NWDAF não inicia**
   ```bash
   # Verificar logs
   kubectl logs -l app.kubernetes.io/name=nwdaf -n trisla
   
   # Verificar recursos
   kubectl describe pod -l app.kubernetes.io/name=nwdaf -n trisla
   ```

2. **Análises não funcionam**
   ```bash
   # Verificar conectividade
   kubectl exec -it <nwdaf-pod> -n trisla -- curl http://localhost:8080/health
   
   # Verificar configuração
   kubectl get configmap nwdaf-config -n trisla -o yaml
   ```

3. **Alta utilização de recursos**
   ```bash
   # Verificar métricas
   kubectl top pods -l app.kubernetes.io/name=nwdaf -n trisla
   
   # Ajustar recursos no values.yaml
   ```

### **Comandos Úteis**

```bash
# Testar NWDAF
./scripts/test_nwdaf.sh

# Verificar status
kubectl get all -l app.kubernetes.io/name=nwdaf -n trisla

# Reiniciar NWDAF
kubectl rollout restart deployment/nwdaf -n trisla

# Escalar NWDAF
kubectl scale deployment nwdaf --replicas=3 -n trisla
```

## Desenvolvimento

### **Estrutura de Código**
- **`main.py`**: Aplicação principal e orquestração
- **`models/`**: Modelos de dados e estruturas
- **`analytics/`**: Módulos de análise especializados
- **`interfaces/`**: Comunicação com outros módulos

### **Adicionando Novos Analisadores**
1. Criar classe no diretório `analytics/`
2. Implementar métodos de análise
3. Adicionar ao `main.py`
4. Atualizar testes

### **Adicionando Novas Métricas**
1. Definir modelo em `models/data_models.py`
2. Implementar coleta de dados
3. Adicionar processamento
4. Atualizar documentação

## Contribuição

1. Fork o repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](../../LICENSE) para detalhes.

## Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação completa
- Entre em contato com a equipe TriSLA

---

**TriSLA NWDAF** - Network Data Analytics Function para 5G
