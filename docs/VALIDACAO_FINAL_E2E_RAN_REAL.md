# VALIDACAO FINAL E2E RAN REAL (PROMPT_08)

## FASE 0 — leitura obrigatoria
- Documento lido: `docs/TRISLA_DIRETRIZES_RAN_E2E.md`

## FASE 1 — garantir RAN real
- Estado observado: **FALHA** (srsenb em ImagePullBackOff; ueransim em Running)
- Core AMF/SMF/UPF: **OK**

## FASE 2 — bloquear simulador
- `trisla-prb-simulator` escalado para 0 replicas: **OK**

## FASE 3 — validar PRB real
- Amostras válidas de PRB (query backend): []
- `std(ran_prb_utilization) = 0.000000`
- Critério `std > 0.01`: **FALHA**

## FASE 4 — teste ACCEPT
- decision=None, nasp_orchestration_status=None, prb=None

## FASE 5 — teste REJECT
- decision=None, nasp_orchestration_status=None, prb=None

## FASE 6 — teste RENEGOTIATE
- decision=None, nasp_orchestration_status=None, prb=None

## FASE 8 — liberacao para coleta
- ran_ativa=False
- core_ativo=True
- prb_dinamico=False
- accept_orquestra=False
- reject_nao_orquestra=True
- renegotiate_consistente=False

## STATUS FINAL
- **BLOQUEADO**
- Motivo principal: gate cientifico falhou (PRB sem variabilidade) e RAN real (srsenb) indisponível.