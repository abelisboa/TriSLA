# Cenários Experimentais - TriSLA

## C1 — eMBB
- **5 SLAs simultâneos**: Teste de estabilidade moderada
- **10 SLAs simultâneos**: Teste de carga média
- **Métrica foco**: Tempo de decisão e estabilidade

## C2 — URLLC
- **3 SLAs simultâneos**: Teste de latência baixa
- **6 SLAs simultâneos**: Teste de latência sob carga
- **Métrica foco**: Latência e jitter lógico

## C3 — mMTC
- **10 SLAs simultâneos**: Teste de volume moderado
- **20 SLAs simultâneos**: Teste de volume alto
- **Métrica foco**: Escalabilidade e volume de eventos

## Payloads Base
- eMBB: latency_max=50ms, availability_min=95%
- URLLC: latency_max=10ms, availability_min=99.9%
- mMTC: latency_max=100ms, availability_min=90%
