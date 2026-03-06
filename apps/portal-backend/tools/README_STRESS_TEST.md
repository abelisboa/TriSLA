# Stress Test - Submissão de SLA

Script para executar testes de carga no endpoint de submissão de SLA do Portal TriSLA.

## Uso

```bash
# Executar com 20 requisições (padrão)
python backend/tools/stress_sla_submit.py

# Executar com N requisições
python backend/tools/stress_sla_submit.py 50

# Executar com URL customizada
python backend/tools/stress_sla_submit.py 20 http://localhost:8001
```

## Requisitos

- Backend rodando em `http://localhost:8001` (ou URL especificada)
- NASP acessível via port-forwards (8080-8084)
- Python 3.7+ com `httpx` instalado

## Métricas Coletadas

### Taxa de Sucesso
- Percentual de requisições bem-sucedidas
- Total de requisições válidas vs. falhadas

### Latência
- **Média**: Latência média de todas as requisições
- **Mediana**: Latência mediana
- **Mínima**: Menor latência observada
- **Máxima**: Maior latência observada

### Falhas por Módulo
- Contagem de falhas por módulo NASP:
  - SEM-CSMF
  - ML-NSMF
  - Decision Engine
  - BC-NSSMF
  - SLA-Agent Layer

### Comportamentos de Retry
- Detecção de retries (latência > 10s ou timeout)
- Taxa de retries observada
- Análise de padrões de retry

### Status por Módulo
- OK: Requisições bem-sucedidas
- ERROR: Requisições com erro
- UNKNOWN: Status desconhecido

### Tipos de Erro
- `connection_error`: Erro de conexão com NASP
- `nasp_degraded`: NASP em modo degraded
- `timeout`: Timeout na requisição
- `service_unavailable`: Serviço indisponível (503)

## Exemplo de Saída

```
======================================================================
STRESS TEST - Submissão de SLA
======================================================================

Executando 20 requisições paralelas...
Backend URL: http://localhost:8001

======================================================================
PROCESSANDO RESULTADOS
======================================================================

======================================================================
RESULTADOS DO STRESS TEST
======================================================================

Taxa de Sucesso:
  ✅ 95.0% (19/20)

Latência:
  ℹ️  Média: 1250.50ms
  ℹ️  Mediana: 1200.00ms
  ℹ️  Mínima: 800.00ms
  ℹ️  Máxima: 3500.00ms

Throughput:
  ℹ️  Total de requisições: 20
  ℹ️  Tempo total: 3.50s
  ℹ️  Requisições/segundo: 5.71

Falhas por Módulo:
  ✅ Nenhuma falha de módulo detectada

Status por Módulo:
  ✅ SEM_CSMF: 20 OK, 0 ERROR, 0 UNKNOWN (100.0% OK)
  ✅ ML_NSMF: 20 OK, 0 ERROR, 0 UNKNOWN (100.0% OK)
  ✅ DECISION: 20 OK, 0 ERROR, 0 UNKNOWN (100.0% OK)
  ✅ BC_NSSMF: 20 OK, 0 ERROR, 0 UNKNOWN (100.0% OK)
  ✅ SLA_AGENT: 20 OK, 0 ERROR, 0 UNKNOWN (100.0% OK)

Comportamentos de Retry:
  ✅ Nenhum retry detectado (0.0%)
```

## Relatório JSON

O script gera um relatório detalhado em JSON: `backend/stress_test_report.json`

Estrutura do relatório:
```json
{
  "timestamp": "2025-01-15T10:30:00",
  "total_requests": 20,
  "requests": [...],
  "summary": {
    "success_rate": 95.0,
    "latency": {
      "average_ms": 1250.50,
      "median_ms": 1200.00,
      "min_ms": 800.00,
      "max_ms": 3500.00
    },
    "module_failures": {},
    "retry_rate": 0.0,
    "error_types": {}
  }
}
```

## Interpretação dos Resultados

### Taxa de Sucesso
- **≥ 95%**: Excelente - Sistema estável
- **80-94%**: Bom - Algumas falhas transitórias
- **< 80%**: Crítico - Problemas de conectividade ou NASP

### Latência
- **< 2s**: Excelente - Resposta rápida
- **2-5s**: Aceitável - Pode indicar carga
- **> 5s**: Lento - Possíveis retries ou problemas de rede

### Retries
- **0%**: Ideal - Nenhum retry necessário
- **1-10%**: Aceitável - Alguns retries por falhas transitórias
- **> 10%**: Crítico - Muitos retries, verificar conectividade NASP

## Troubleshooting

### Erro: "Não foi possível conectar ao backend"
- Verificar se o backend está rodando: `curl http://localhost:8001/health`
- Verificar se a porta está correta

### Taxa de sucesso baixa
- Verificar port-forwards NASP (8080-8084)
- Verificar logs do backend
- Verificar status do NASP: `curl http://localhost:8001/nasp/diagnostics`

### Muitos retries detectados
- Verificar conectividade com BC-NSSMF
- Verificar logs do backend para erros de conexão
- Verificar se o Besu está acessível

## Notas

- O script executa requisições **em paralelo** (não sequencial)
- Timeout padrão: 60 segundos por requisição
- Retries são detectados indiretamente (latência > 10s ou timeout)
- Para análise detalhada de retries, verificar logs do backend




