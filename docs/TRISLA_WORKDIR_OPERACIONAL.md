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
