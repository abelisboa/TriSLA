# Metodologia de Validação e Escopo Experimental — TriSLA

**Versão:** S4.0  
**Data:** 2025-01-27  
**Objetivo:** Definir metodologia de validação, escopo experimental e critérios de avaliação

---

## 📋 Sumário

1. [Visão Geral](#-visão-geral)
2. [Metodologia de Validação](#-metodologia-de-validação)
3. [Escopo Experimental](#-escopo-experimental)
4. [Cenários de Teste](#-cenários-de-teste)
5. [Métricas e KPIs](#-métricas-e-kpis)
6. [Critérios de Sucesso](#-critérios-de-sucesso)

---

## 🎯 Visão Geral

A metodologia de validação do TriSLA foi projetada para demonstrar, de forma quantitativa e rastreável, o comportamento da arquitetura nos três eixos principais:

- **E1 — Eixo Semântico**: Validação da interpretação semântica e geração de NEST
- **E2 — Eixo Preditivo/Decisão**: Validação de predições ML e decisões automatizadas
- **E3 — Eixo Contratual**: Validação de registro em blockchain e auditoria

### Princípios da Metodologia

1. **Reprodutibilidade**: Todos os testes são controlados e reproduzíveis
2. **Rastreabilidade**: Dados brutos são coletados antes de qualquer agregação
3. **Transparência**: Metodologia clara e documentada
4. **Validação Real**: Testes em ambiente NASP real, não simulado

---

## 🔬 Metodologia de Validação

### Fases de Validação

#### Fase 1: Validação Funcional

**Objetivo**: Validar que cada módulo funciona corretamente isoladamente.

**Métodos**:
- Testes unitários por módulo
- Testes de integração entre módulos
- Validação de interfaces I-01 a I-07

**Critérios**:
- ✅ Todos os módulos respondem corretamente
- ✅ Interfaces funcionam conforme especificação
- ✅ Sem erros críticos

#### Fase 2: Validação de Pipeline End-to-End

**Objetivo**: Validar o fluxo completo desde a recepção de intent até a execução no NASP.

**Métodos**:
- Testes E2E automatizados
- Validação de fluxo completo (I-01 → I-07)
- Verificação de rastreabilidade (correlation IDs)

**Critérios**:
- ✅ Fluxo completo executado sem falhas
- ✅ Tempo total < 30 segundos (end-to-end)
- ✅ Rastreabilidade completa

#### Fase 3: Validação Experimental

**Objetivo**: Coletar dados quantitativos para demonstrar comportamento da arquitetura.

**Métodos**:
- Execução de cenários controlados
- Coleta de métricas via Prometheus
- Análise estatística de resultados

**Critérios**:
- ✅ Dados coletados para todos os cenários
- ✅ Métricas validadas e consistentes
- ✅ Análise estatística concluída

---

## 🧪 Escopo Experimental

### Ambiente de Teste

**Plataforma**: NASP (Network Automation & Slicing Platform)
- Ambiente real de rede 5G/O-RAN
- Domínios: RAN, Transport, Core
- Observabilidade: Prometheus, Grafana, Loki

**Configuração**:
- Namespace: `trisla`
- Versão: v3.7.10
- Modo: Produção real (não simulação)

### Tipos de SLA Testados

#### eMBB (Enhanced Mobile Broadband)
- **Foco**: Throughput alto
- **Métricas**: Throughput (Mbps), latência (ms)
- **Cenários**: 5, 10, 20 SLAs simultâneos

#### URLLC (Ultra-Reliable Low-Latency Communications)
- **Foco**: Latência ultra-baixa e confiabilidade
- **Métricas**: Latência (ms), jitter (ms), confiabilidade (%)
- **Cenários**: 3, 6, 10 SLAs simultâneos

#### mMTC (massive Machine-Type Communications)
- **Foco**: Escalabilidade e volume
- **Métricas**: Número de dispositivos, taxa de eventos
- **Cenários**: 10, 20, 50 SLAs simultâneos

---

## 📊 Cenários de Teste

### Cenário C1: eMBB — Throughput

**Objetivo**: Validar comportamento sob carga de throughput.

**Configuração**:
- 5 SLAs simultâneos (subcenário C1.1)
- 10 SLAs simultâneos (subcenário C1.2)
- 20 SLAs simultâneos (subcenário C1.3)

**Métricas coletadas**:
- Tempo de decisão (ms)
- Taxa de aceitação (%)
- Throughput médio (Mbps)
- Uso de recursos (CPU, memória)

### Cenário C2: URLLC — Latência

**Objetivo**: Validar comportamento sob requisitos de latência rigorosos.

**Configuração**:
- 3 SLAs simultâneos (subcenário C2.1)
- 6 SLAs simultâneos (subcenário C2.2)
- 10 SLAs simultâneos (subcenário C2.3)

**Métricas coletadas**:
- Latência end-to-end (ms)
- Jitter lógico (ms)
- Taxa de violações (%)
- Tempo de resposta do sistema (ms)

### Cenário C3: mMTC — Escalabilidade

**Objetivo**: Validar escalabilidade e volume de eventos.

**Configuração**:
- 10 SLAs simultâneos (subcenário C3.1)
- 20 SLAs simultâneos (subcenário C3.2)
- 50 SLAs simultâneos (subcenário C3.3)

**Métricas coletadas**:
- Taxa de processamento (SLAs/segundo)
- Volume de eventos (eventos/segundo)
- Escalabilidade do sistema
- Uso de recursos sob carga

### Cenário C4: Stress Test

**Objetivo**: Validar comportamento sob carga extrema.

**Configuração**:
- 100 SLAs simultâneos
- 200 SLAs simultâneos
- 500 SLAs simultâneos

**Métricas coletadas**:
- Taxa de falhas (%)
- Degradação de performance
- Recuperação após carga
- Limites do sistema

---

## 📈 Métricas e KPIs

### Métricas de Performance

| Métrica | Descrição | Target |
|---------|-----------|--------|
| **Latência End-to-End** | Tempo total do fluxo (I-01 → I-07) | < 30s (p95) |
| **Tempo de Decisão** | Tempo para decisão do Decision Engine | < 5s (p95) |
| **Tempo de Predição ML** | Tempo de inferência do ML-NSMF | < 500ms (p95) |
| **Throughput** | Taxa de SLAs processados | > 10 SLAs/s |

### Métricas de Qualidade

| Métrica | Descrição | Target |
|---------|-----------|--------|
| **Taxa de Aceitação** | % de SLAs aceitos | > 80% |
| **Taxa de Violações** | % de SLAs violados | < 5% |
| **Acurácia ML** | Acurácia das predições | > 85% |
| **Disponibilidade** | Uptime do sistema | > 99.9% |

### KPIs 3GPP e O-RAN

| KPI | Descrição | Target |
|-----|-----------|--------|
| **Latência de RAN** | Latência no domínio RAN | < 10ms (URLLC) |
| **Throughput de RAN** | Throughput no domínio RAN | > 100Mbps (eMBB) |
| **Confiabilidade** | Taxa de sucesso | > 99.999% (URLLC) |
| **Disponibilidade** | Uptime do slice | > 99.9% |

---

## ✅ Critérios de Sucesso

### Critérios Funcionais

- ✅ Todos os módulos operacionais
- ✅ Interfaces I-01 a I-07 funcionando
- ✅ Fluxo end-to-end completo
- ✅ Sem erros críticos

### Critérios de Performance

- ✅ Latência end-to-end < 30s (p95)
- ✅ Throughput > 10 SLAs/s
- ✅ Tempo de decisão < 5s (p95)
- ✅ Disponibilidade > 99.9%

### Critérios de Qualidade

- ✅ Taxa de aceitação > 80%
- ✅ Taxa de violações < 5%
- ✅ Acurácia ML > 85%
- ✅ Rastreabilidade completa

### Critérios de Escalabilidade

- ✅ Sistema suporta 100+ SLAs simultâneos
- ✅ Degradação gradual (não catastrófica)
- ✅ Recuperação automática após carga

---

## 📚 Referências

### Documentação Relacionada

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Arquitetura completa
- **[experimentos/CENARIOS_EXPERIMENTAIS.md](experimentos/CENARIOS_EXPERIMENTAIS.md)** — Cenários detalhados
- **[experimentos/RESULTADOS_BRUTOS.md](experimentos/RESULTADOS_BRUTOS.md)** — Resultados experimentais

### Padrões e Especificações

- **3GPP TS 28.541**: Network Slice Management
- **O-RAN WG1**: Architecture and Interfaces
- **ETSI NFV**: Network Functions Virtualisation

---

**Última atualização**: 2025-01-27  
**Versão**: S4.0

