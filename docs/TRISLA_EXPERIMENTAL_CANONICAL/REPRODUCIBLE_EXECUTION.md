# Execução Reproduzível (gNB + N2)

## Método validado

A partir do repositório `trisla`, com imagem `srsran-zmq:local` e configuração em evidência:

```bash
cd /path/to/trisla
timeout 55 podman run --rm --network host \
  -v "$(pwd)/evidencias_gnb_real/nasp_validation_06/analysis/gnb_config_used.txt:/gnb.yaml:ro" \
  srsran-zmq:local gnb -c /gnb.yaml
```

(Equivalente: `docker` se for alias Podman no host.)

## Observações críticas

- Em ambiente Podman rootless, `podman run -d` (detached) observou-se ficar preso em ZMQ à espera de amostras e **não** progredir até N2 da mesma forma que uma execução em primeiro plano; além disso podem surgir erros de epoll/stdin (`Operation not permitted`).
- Uso de **`timeout`** com execução em primeiro plano garante log completo até `N2: Connection ... completed` e `==== gNB started ===` nas corridas documentadas.
- Para N2 até ao AMF em IP de pod, `cu_cp.amf.bind_addr: 0.0.0.0` é necessário quando o RF ZMQ usa 127.0.0.1 (evitar SCTP bound apenas a loopback).

## Status

Método de referência para reproduzir a evidência N2/NG Setup descrita em `nasp_validation_06` e neste diretório.
