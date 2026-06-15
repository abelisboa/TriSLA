# TRI-SLA WORKDIR OPERACIONAL (OBRIGATÓRIO)

## REGRA PRINCIPAL
TODO experimento deve seguir este fluxo:

1. Validar UE (uesimtun0)
2. Validar ICMP via túnel
3. Validar UDP iperf
4. Executar V8
5. Validar artefactos

## PROIBIDO
- Usar 8.8.8.8
- Usar podIP como peer
- Executar fora deste fluxo

### RAN Telemetry Policy

The use of simulators is generally avoided in TriSLA.

However, for RAN PRB metrics, due to the lack of a stable and observable PRB signal in the NASP RAN stack, a controlled simulator is used as a fallback mechanism.

This is a documented and accepted exception aligned with NASP capabilities.

## VARIÁVEIS OFICIAIS

TRISLA_P207_SERVER_IP=192.168.100.51
UE_INTERFACE=uesimtun0
UE_IP=10.1.0.x

## DOMÍNIOS

RAN → UERANSIM
TRANSPORT → ONOS / Mininet
CORE → free5GC

## VALIDAÇÃO

ICMP OK + UDP OK = permitido executar V8

---

# Q1_RUNTIME_STABLE_BASELINE

## Estado Oficial Congelado

Baseline oficial ativo:

Q1_RUNTIME_STABLE_BASELINE

Referência:
evidencias_FINAL_RUNTIME_BASELINE_Q1_20260506T203529Z

## Regra Operacional Obrigatória

Toda evolução futura do TriSLA deve partir EXCLUSIVAMENTE deste baseline validado.

Nenhuma evolução poderá:

- ignorar este baseline;
- bypassar SSOT;
- introduzir loaders artificiais;
- introduzir fallback mágico;
- alterar runtime sem evidência;
- quebrar rollback operacional.

## Fluxo Obrigatório

1. auditoria
2. RCA
3. patch mínimo
4. rollback plan
5. deploy digest-only
6. validação runtime
7. freeze operacional


---

# OTEL_STABILIZED

Estado consolidado após RCA + patch mínimo OTEL.

Resultado:
- OTEL estabilizado
- monitoring preservado
- Prometheus preservado
- TriSLA core preservado

Referência:
evidencias_q1_otel_stabilized_freeze_20260506T213837Z

