# Limitações

## PHY / UE

- Attach UE não faz parte da validação NASP documentada nesta SSOT.
- UERANSIM e srsRAN ZMQ RF não constituem par RF comprovado para célula/attach na mesma stack (evidências em `evidencias_gnb_real/rfsim_validation_05w2/` e correlatos).
- srsUE (srsRAN_4G) com ZMQ: build e arranque documentados; seleção de célula end-to-end com o gNB do projeto exige mais alinhamento PHY/versões (evidência em `evidencias_gnb_real/srsue_05z/`).

## Justificativa

NASP, no protótipo experimental descrito, opera na camada de orquestração e integração de serviços (incluindo N2), não na caracterização da camada física.

## Impacto

Não invalida a validação de orquestração TriSLA ↔ Core ↔ RAN (N2) no escopo declarado.
