# Regras para Prompts Futuros

1. Não inventar fluxos que contradizem este diretório sem nova evidência em `evidencias_gnb_real/`.
2. Seguir o pipeline descrito em `TRISLA_E2E_CANONICAL_FLOW.md`.
3. Não afirmar validação PHY/attach UE com base apenas na SSOT N2/NASP.
4. Citar apenas evidências existentes ou geradas no mesmo formato (logs, `analysis/`, relatórios).
5. Para gNB com Podman: preferir execução com `timeout` em primeiro plano; evitar assumir `podman run -d` equivalente sem verificar N2.
6. Não alterar arquitetura TriSLA/free5GC/kubelet salvo pedido explícito fora do âmbito documental.

## SSOT

O diretório `docs/TRISLA_EXPERIMENTAL_CANONICAL/` é a fonte de verdade para o protótipo experimental consolidado nesta data (ver `BUILD_TIMESTAMP.txt`).

## Documentação de produto vs experimental

Runbooks e guias Helm do projeto continuam em `docs/` e `helm/`; este diretório foca evidência e limites do ensaio com RAN real/containerizado e core free5GC.
