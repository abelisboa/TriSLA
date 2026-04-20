# TRISLA — DIRETRIZES TÉCNICAS PARA REATIVAÇÃO DA RAN REAL E VALIDAÇÃO DO FLUXO E2E

## 1. OBJETIVO

Estabelecer regras formais e obrigatórias para:

* reativação da cadeia real do NASP
* validação completa do fluxo decisório TriSLA
* eliminação de fontes artificiais de telemetria
* garantia de integridade científica da coleta

---

## 2. PRINCÍPIO ARQUITETURAL (IMUTÁVEL)

A arquitetura TriSLA segue:

```
SLA Request → TriSLA → Decision → (ACCEPT?) → NASP → RAN/Core/Transporte → Métricas → Prometheus → TriSLA
```

### Regras:

* TriSLA SEMPRE decide antes da orquestração
* NASP SÓ executa em caso de ACCEPT
* Métricas só são válidas se oriundas da execução real

---

## 3. REGRA CRÍTICA — RAN REAL OBRIGATÓRIA

É PROIBIDO:

* usar PRB Simulator
* usar valores fixos
* usar override manual

É OBRIGATÓRIO:

* UERANSIM ativo
* srsRAN/srsenb funcional
* core 5G operacional

---

## 4. CADEIA REAL DO NASP (OBRIGATÓRIA)

```
UERANSIM → srsRAN/srsenb → Core (AMF/SMF/UPF) → Tráfego → PRB → Prometheus → TriSLA
```

---

## 5. CONDIÇÕES MÍNIMAS DE OPERAÇÃO

Antes de qualquer coleta:

### RAN

* gNB/srsenb em estado Running
* UE conectado (attach realizado)

### CORE

* AMF, SMF, UPF ativos
* sessões estabelecidas

### TELEMETRIA

* PRB visível no Prometheus
* PRB variável

---

## 6. VALIDAÇÃO DO FLUXO DECISÓRIO

### 6.1 ACCEPT

Deve obrigatoriamente:

* acionar NASP
* criar slice
* ativar recursos RAN/Core
* gerar métricas reais

Se não houver métricas:

→ ACCEPT inválido

---

### 6.2 REJECT

Deve:

* NÃO acionar NASP
* NÃO gerar métricas de execução
* retornar decisão coerente

---

### 6.3 RENEGOTIATE

Deve:

* NÃO executar orquestração completa
* refletir limitação de recursos
* manter consistência com ML + policy

---

## 7. GATE CIENTÍFICO (OBRIGATÓRIO)

Antes da coleta:

```
std(ran_prb_utilization) > 0.01
```

E:

* PRB responde à carga
* PRB aparece no backend
* PRB aparece no submit

Se qualquer falhar:

→ COLETA PROIBIDA

---

## 8. VALIDAÇÃO DO CAMINHO ACCEPT → NASP → RAN

Para cada ACCEPT:

Deve existir evidência de:

* `nasp_orchestration_status = SUCCESS`
* ativação de recursos
* geração de métricas reais
* PRB não constante

---

## 9. PROIBIÇÕES (ANTI-REGRESSÃO)

❌ Não usar fallback artificial
❌ Não simular dados
❌ Não alterar arquitetura
❌ Não ignorar gate científico
❌ Não gerar figuras sem validação

---

## 10. CRITÉRIO DE VALIDADE DO DATASET

Um dataset só é válido se:

* contém tri-classe (A/R/R)
* contém PRB dinâmico
* contém métricas reais
* contém evidência NASP
* passa no gate científico

---

## 11. OBJETIVO FINAL

Garantir que:

* TriSLA decide corretamente
* NASP executa corretamente
* RAN responde corretamente
* métricas refletem o sistema real

---

## 12. RESULTADO ESPERADO

Após aplicação destas diretrizes:

* coleta E2E válida
* figuras IEEE de alto nível
* evidência científica robusta
* dissertação consistente

---

FIM DO DOCUMENTO
