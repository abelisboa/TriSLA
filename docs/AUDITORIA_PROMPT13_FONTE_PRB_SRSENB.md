# AUDITORIA PROMPT_13 — FONTE DE PRB NO srsENB (LOGS, CONFIG, SCHEDULER, RUNTIME)

## Escopo

- Auditoria profunda em modo somente leitura.
- Sem alteracao de codigo, sem alteracao de deployment, sem novos dados E2E.

## 1) Logs analisados (FASE 1)

Arquivo coletado:

- `srsenb_full_logs.txt` (`kubectl logs --tail=2000`)

Resultado de busca por `prb|rb|resource|sched|alloc|util|dl|ul`:

- Unica linha relevante encontrada: `n_prb=50`
- Nenhuma linha de uso dinamico:
  - sem `PRB usage`
  - sem `RB allocated X/Y`
  - sem counters de scheduler DL/UL

Interpretacao:

- `n_prb=50` representa configuracao/capacidade da celula, nao utilizacao em tempo real.

## 2) Nivel de log (FASE 2)

No arquivo ativo `/etc/srsran/enb.conf`:

- `[log]`
  - `all_level = warning`
  - `filename = /tmp/enb.log`

Conclusao:

- nivel `warning` reduz fortemente visibilidade de scheduler/MAC/PHY.
- stdout atual nao mostra telemetria de PRB.

## 3) Configuracao srsRAN (FASE 3)

Arquivos encontrados:

- `/etc/srsran/enb.conf`
- `/etc/srsran/rr.conf`
- `/etc/srsran/drb.conf`
- `/etc/srsran/sib.conf`

Pontos relevantes:

- `n_prb = 50` configurado.
- secao `[scheduler]` presente, mas parametros de telemetria/trace estao comentados (default).
- secao `[expert]` documenta opcoes de metrics/report, porem sem ativacao explicita no arquivo atual.

## 4) Saida em tempo real (FASE 4)

`kubectl logs -f` mostrou repetidamente:

- `Waiting for the 5G-EmPOWER Runtime to come up...`

Nao apareceu nenhuma saida dinamica de PRB/RB/scheduler durante observacao.

## 5) Interfaces e sockets (FASE 5)

`ss -ltnup` dentro do pod:

- sem listeners TCP/UDP de processo srsenb no momento da auditoria.

Correlacao com Prometheus:

- tentativa de scrape direto em `:9092/metrics` retornava `connection refused` (auditoria anterior).

## 6) Arquivos internos de metricas (FASE 6)

Inspecao de `/tmp`, `/var/log`, `/run` e glob de arquivos `*stat*|*metric*|*report*|*log*`:

- nao foi evidenciado arquivo de metricas PRB ativo para coleta.
- o caminho configurado de log (`/tmp/enb.log`) nao apresentou evidencia util de PRB na auditoria atual.

## 7) Processo srsenb e runtime (FASE 7)

`ps aux` no pod mostrou:

- `/bin/bash /launcher.sh`
- `sleep 10` (loop)
- **nao** mostrou processo `srsenb` ativo.

`/launcher.sh`:

- executa `./dns_replace.sh`
- tenta subir `./srsRAN/build/srsenb/src/srsenb &`
- faz `wait` no child

Evidencia combinada:

- estado `Running` do pod nao implica stack RAN operacional completa.
- runtime fica aguardando dependencia externa (`5G-EmPOWER Runtime`), sem gerar telemetria de PRB.

## 8) Classificacao A/B/C (FASE 8)

- **CASO A (PRB em logs): NAO**
- **CASO B (RB allocation para calculo indireto): NAO**
- **CASO C (PRB nao aparece em nenhum lugar utilizavel): SIM**

## 9) Decisao tecnica (FASE 9)

Decisao: **C — instrumentacao minima no codigo/runtime do srsRAN**.

Justificativa:

- nao ha sinal de PRB/RB dinamico no log atual;
- nao ha processo `srsenb` efetivamente ativo produzindo dados de scheduler;
- nao ha interface/arquivo interno utilizavel para extracao indireta no estado observado.

## 10) Resposta final objetiva

**PRB E ACESSIVEL?**  
- **NAO**, no runtime atual auditado.

**COMO EXTRAIR? (metodo exato)**  
- No estado atual: **nao ha metodo de extracao apenas por regex/log scraping**.
- Caminho tecnico necessario: habilitar instrumentacao no runtime que realmente execute o scheduler do `srsenb` e exponha counters (log estruturado ou endpoint), entao ajustar parser para esse formato real.
