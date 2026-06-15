# TriSLA Canonical Pipeline (SSOT)

## Fluxo End-to-End Validado

1. SLA Submit
2. SEM-NSMF (interpretação semântica)
3. ML-NSMF (predição)
4. Decision Engine
5. NASP Adapter
6. Core (free5GC)
7. RAN (srsRAN gNB)
8. NGAP (N2 interface)

## Evidência (nível orquestração / CN–RAN)

- NGSetupRequest / NG-Setup response confirmados nos logs do AMF (ver `N2_VALIDATION.md` e `N2_NGAP_EVIDENCE.txt`).
- gNB (`srsran-zmq:local`) com N2 até IP do pod AMF e `bind_addr: 0.0.0.0` (evidência em `evidencias_gnb_real/nasp_validation_06/`).
- SCTP ativo entre host e AMF.

## Fora do escopo desta SSOT

- Attach UE
- Validação PHY / RF / sincronização
