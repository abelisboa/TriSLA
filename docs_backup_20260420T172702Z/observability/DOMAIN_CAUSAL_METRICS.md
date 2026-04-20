# Domain Causal Metrics - TriSLA v3.9.3

## Contrato Causal para Observabilidade por Domínio

Este documento define formalmente as métricas por domínio que são utilizadas para explicar causalidade de decisões SLA no TriSLA v3.9.3.

**Objetivo:** Permitir resposta explícita à pergunta "Por que este SLA foi RENEG?" através de observabilidade causal por domínio.

---

## Métricas por Domínio

### Domínio RAN (Radio Access Network)

| Métrica | Unidade | SLA-aware | Descrição | Threshold Típico |
|---------|---------|-----------|-----------|------------------|
|  | % | ✅ | Utilização de CPU dos recursos RAN | < 70% |
|  | ms | ✅ | Latência end-to-end no RAN | < 20ms (URLLC) |
|  | ms | ✅ | Variação de latência | < 5ms (URLLC) |
|  | % | ✅ | Taxa de confiabilidade | > 99.9% (URLLC) |
|  | % | ✅ | Utilização de PRBs (Physical Resource Blocks) | < 80% |

**Fonte:** Coletado via Prometheus ( metrics) e NASP Adapter.

---

### Domínio Transport (Transport Network)

| Métrica | Unidade | SLA-aware | Descrição | Threshold Típico |
|---------|---------|-----------|-----------|------------------|
|  | Mbps | ✅ | Largura de banda disponível | > 100 Mbps (eMBB) |
|  | Mbps | ✅ | Throughput downlink | > 100 Mbps (eMBB) |
|  | Mbps | ✅ | Throughput uplink | > 50 Mbps (eMBB) |
|  | % | ✅ | Taxa de perda de pacotes | < 0.1% (eMBB) |

**Fonte:** Coletado via Prometheus ( metrics) e NASP Adapter.

---

### Domínio Core

| Métrica | Unidade | SLA-aware | Descrição | Threshold Típico |
|---------|---------|-----------|-----------|------------------|
|  | % | ✅ | Utilização de CPU dos recursos Core | < 80% |
|  | % | ✅ | Utilização de memória | < 80% |
|  | % | ✅ | Disponibilidade do Core | > 99% (mMTC) |
|  | ms | ✅ | Tempo de setup de sessão | < 100ms |
|  | % | ✅ | Taxa de sucesso de attach (mMTC) | > 95% (mMTC) |
|  | events/s | ✅ | Throughput de eventos (mMTC) | > 1000 events/s |

**Fonte:** Coletado via Prometheus ( metrics) e NASP Adapter.

---

## Mapeamento SLA → Métricas Críticas

### URLLC (Ultra-Reliable Low Latency Communication)
- **Métricas dominantes:** , ,  (RAN)
- **Threshold mínimo:** 
- **Domínio crítico:** RAN

### eMBB (Enhanced Mobile Broadband)
- **Métricas dominantes:** , ,  (Transport)
- **Threshold mínimo:** 
- **Domínio crítico:** Transport

### mMTC (Massive Machine Type Communication)
- **Métricas dominantes:** , ,  (Core)
- **Threshold mínimo:** 
- **Domínio crítico:** Core

---

## Formato de Snapshot Causal

Cada snapshot causal deve seguir o formato:



---

## Compliance por Domínio

O compliance por domínio é calculado como:



Onde cada  é calculado conforme o tipo de métrica:
- **Métricas "menor é melhor" (latency, jitter, packet_loss, cpu_utilization):**
  

- **Métricas "maior é melhor" (throughput, reliability, availability):**
  

O  global é então:


---

## Notas de Implementação

1. **Não altera lógica decisória:** Este contrato apenas expõe causalidade já existente.
2. **Backward compatible:** Não quebra funcionalidades existentes.
3. **Feature-flagável:** Pode ser desabilitado sem impacto.
4. **Isolado:** Código em módulos separados (, ).

---

**Versão:** 1.0  
**Data:** 2026-01-27  
**TriSLA Version:** v3.9.3
