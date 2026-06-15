# Validação N2 (NGAP)

## Critérios

- SCTP Accept (AMF)
- NGSetupRequest (AMF)
- NG-Setup response (AMF)

## Resultado

Cumpridos nos ensaios registados em `evidencias_gnb_real/nasp_validation_06/`.

O extrato copiado para este pacote canónico está em `N2_NGAP_EVIDENCE.txt` (linhas filtradas do AMF; inclui sequências repetidas de associações de teste).

## Conclusão

Integração RAN ↔ Core validada ao nível da interface N2 (NGAP sobre SCTP), alinhada ao escopo de orquestração NASP, sem exigir attach UE nem validação PHY.
