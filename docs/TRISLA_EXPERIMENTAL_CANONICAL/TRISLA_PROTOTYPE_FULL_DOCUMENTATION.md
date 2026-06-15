# TriSLA Prototype — Full Experimental Documentation

## Objetivo

Consolidar documentação formal do protótipo validado ao nível NASP/orquestração: TriSLA + NASP + free5GC + srsRAN gNB, com N2 operacional, sem obrigar PHY/UE.

## Arquitetura

TriSLA (aplicações de orquestração e decisão) + adaptação NASP + Core free5GC + RAN srsRAN (gNB).

## Pipeline

Ver `TRISLA_E2E_CANONICAL_FLOW.md`.

## Evidência N2

Ver `N2_VALIDATION.md` e ficheiro bruto `N2_NGAP_EVIDENCE.txt`.

## Execução reproduzível

Ver `REPRODUCIBLE_EXECUTION.md`.

## Limitações

Ver `LIMITATIONS.md`.

## Inventário de pastas de evidência

Ver `EVIDENCE_INDEX.md`.

## Estrutura do repositório (snapshot)

Ver `PROJECT_STRUCTURE.txt` (níveis limitados ou listagem recursiva).

## Conclusão

O sistema foi documentado como validado com sucesso no nível de orquestração da interface N2 (NGAP sobre SCTP) entre gNB e AMF, alinhado ao escopo NASP e à abstração da camada física.

Para o Capítulo de Protótipo: usar este diretório como base e referenciar `evidencias_gnb_real/nasp_validation_06/` para traço de auditoria.
