# AUDITORIA PROMPT_09 — CORRECAO CIRURGICA srsENB

## 1) Erro original

- Pod `srsenb` em `ImagePullBackOff` no namespace `srsran`.
- Imagem configurada no deployment: `softwareradiosystems/srsran:latest`.
- Evidencia de evento: `Back-off pulling image "softwareradiosystems/srsran:latest"`.

## 2) Causa raiz

- Causa raiz primaria: imagem originalmente referenciada no deployment era invalida/inacessivel para uso operacional no cluster (falha de pull recorrente).
- Classificacao PROMPT_09: **CASO A (imagem invalida/nao disponivel)**.
- Durante a correcao, foram identificadas imagens alternativas que puxavam, mas nao eram compatíveis com runtime esperado:
  - `softwareradiosystems/srsran-project:release_avx2-latest`: nao contem `srsenb` 4G compativel com o comando legado (`/usr/local/bin/srsenb`) e gerou falhas de runtime.
  - `docker.io/qoherent/srsenb:1.0`: contem `srsenb`, mas falhou por dependencia de biblioteca (`libsrsran_rf.so.0` ausente em runtime no pod).

## 3) Correcao aplicada (somente srsenb)

1. Atualizacao de imagem no deployment `srsenb` para uma imagem funcional de `srsenb`:
   - `docker.io/snslab/srsenb:latest`
2. Remocao de `command/args` hardcoded do deployment para utilizar o launcher nativo da imagem.
3. `rollout restart` + `rollout status` ate conclusao bem-sucedida.

Nenhum modulo TriSLA foi alterado. Nenhum simulador foi reintroduzido.

## 4) Imagem final utilizada

- Deployment `srsenb`:
  - `docker.io/snslab/srsenb:latest`

## 5) Evidencia de pod Running

Saida validada:

- `kubectl get pods -n srsran -o wide`
  - `srsenb-8464bdd4f7-pvr6p   1/1   Running   0   ...   node2`

## 6) Evidencia de logs

Saida validada:

- `kubectl logs -n srsran -l app=srsenb --tail=200`
  - Impressao de variaveis de ambiente e inicializacao:
  - `Waiting for the 5G-EmPOWER Runtime to come up...`

Nao foram observadas falhas de pull apos a correcao final.

## 7) Evidencia de PRB dinamico

Teste de 5 amostras:

- `curl -s http://127.0.0.1:18001/api/v1/prometheus/summary | jq '.ran_prb_utilization'`
  - `sample_1=null`
  - `sample_2=null`
  - `sample_3=null`
  - `sample_4=null`
  - `sample_5=null`

Conclusao desta fase: **PRB ainda ausente (nao dinamico)**.

## 8) Decisao final

- `srsenb`: **RESTAURADO para Running (1/1)**.
- Gate final PROMPT_09: **BLOQUEADO**.

Motivo do bloqueio residual:

- Embora o `srsenb` tenha sido recuperado de `ImagePullBackOff` para `Running`, o backend ainda recebe `ran_prb_utilization=null`, logo os criterios de `PRB presente + PRB variavel` nao foram satisfeitos.
- Necessario proximo passo operacional focado em integracao/telemetria RAN->Prometheus (sem regressao) para liberar coleta E2E.
