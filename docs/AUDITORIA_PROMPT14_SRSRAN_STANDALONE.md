# AUDITORIA PROMPT_14 — ATIVACAO REAL DO srsRAN (STANDALONE)

## Resultado executivo

- Objetivo executado com abordagem controlada e evidencias completas em `evidencias/prompt14_20260401T150000Z`.
- Estrategia aplicada: **A (imagem standalone existente)**.
- Imagem standalone testada por digest remoto: `docker.io/qoherent/srsenb@sha256:a398d09ecb657217531dcec7b150afc21b4ed7b4011f27a47f9ef9b6203aaf67`.
- O runtime deixou de exibir o loop do EmPOWER, porem falhou na inicializacao real do radio (`Error initializing radio`), entrando em `CrashLoopBackOff`.
- Para evitar regressao operacional do ambiente, o deployment foi restaurado para baseline funcional anterior (`docker.io/snslab/srsenb:latest`, pod `Running 1/1`).
- **Decisao final PROMPT_14: BLOQUEADO**.

## 1) Runtime anterior descartado (evidencia da causa raiz)

Evidencias (fase 1):

- `srsenb_logs_before.txt`: repeticao de `Waiting for the 5G-EmPOWER Runtime to come up...`
- `srsenb_ps_before.txt`: ausencia de processo real `srsenb` (somente `launcher.sh`/`sleep`)

Causa raiz formal:

- imagem/runtime dependente de 5G-EmPOWER;
- pod `Running` sem scheduler RAN real ativo.

## 2) Estrategia escolhida

Escolha conforme regra do prompt:

- **Estrategia A** (preferencial): usar imagem standalone ja existente.
- Imagem selecionada: `docker.io/qoherent/srsenb:1.0`.
- Digest remoto verificado por registry: `sha256:a398d09ecb657217531dcec7b150afc21b4ed7b4011f27a47f9ef9b6203aaf67`.

## 3) Mudancas minimas realizadas

No `Deployment/srsenb` (temporariamente durante o teste):

- imagem por digest remoto;
- comando direto: `/usr/local/bin/srsenb --config_file=/etc/srsran/enb.conf`;
- `LD_LIBRARY_PATH=/usr/local/lib`;
- preservacao de volume de config (`/etc/srsran/enb.conf`) e portas.

## 4) Evidencia tecnica do teste standalone

Pod novo (`srsenb-cf8fb8c7f-gf47g`) entrou em `CrashLoopBackOff`.

Logs capturados (`srsenb_logs_after_fix2.txt`) mostram inicializacao real do binario e falha de runtime:

- `--- Software Radio Systems LTE eNodeB ---`
- `Reading configuration file /etc/srsran/enb.conf...`
- `connect(): Connection refused`
- `Supported RF device list: zmq file`
- `[zmq] Error: No device 'args' option has been set`
- `Error initializing radio.`

Interpretacao:

- o binario standalone executa de fato;
- porem nao consegue abrir frontend RF (nem `zmq`, nem `file`) com a configuracao atual;
- nao alcanca estado operacional de eNB.

## 5) Evidencia de conexao com core e UERANSIM

- Core free5GC (AMF/SMF/UPF/NRF) permaneceu `Running` (`core_pods_after_fix2.txt`).
- UERANSIM permaneceu `Running` (`ueransim_pods_after_fix2.txt`).
- Nao houve evidencia de S1 setup/attach via `srsenb` standalone testado (devido falha de radio).

## 6) Acao de seguranca (sem regressao)

Como o teste standalone degradou disponibilidade de `srsenb`:

- foi executada restauracao do baseline conhecido para manter ambiente operacional:
  - `docker.io/snslab/srsenb:latest`
  - estado final: `srsenb` `Running 1/1` (`srsenb_pods_restored_snslab.txt`)

Observacao:

- baseline restaurado volta a dependencia do runtime EmPOWER (problema original ainda aberto), mas evita regressao do ambiente enquanto se prepara proxima correcao.

## 7) Imagem final usada no ambiente (apos restauracao)

- `docker.io/snslab/srsenb:latest` (baseline restaurado).

## 8) Decisao final (gate PROMPT_14)

Criticidade do gate:

- `srsenb Running`: **SIM** (apos restauracao)
- processo real `srsenb` ativo em modo standalone estavel: **NAO**
- ausencia de dependencia EmPOWER: **NAO** (apos restauracao)
- conexao plausivel com core em runtime standalone: **NAO comprovada**

### STATUS FINAL

- ❌ **BLOQUEADO**

Motivo final:

- A estrategia A comprovou binario standalone iniciando, mas sem frontend RF configurado/compativel no ambiente atual (`zmq/file args ausentes`), impedindo operacao real do eNB.
