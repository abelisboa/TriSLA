# RAN (srsRAN gNB)

## Configuração canónica (ensaio N2 direto ao pod AMF)

- PLMN: 20893
- TAC: 1
- PCI: 1
- `cu_cp.amf.bind_addr: 0.0.0.0` (evita SCTP ligado só a loopback ao usar ZMQ em 127.0.0.1)

## RF (RFsim)

- Modo: ZMQ
- `tx_port`: tcp://127.0.0.1:2000
- `rx_port`: tcp://127.0.0.1:2001

## Integração

- Interface N2 (NGAP sobre SCTP) com AMF (IP do pod, sem NodePort no ensaio documentado).
- NG Setup validado (AMF: NGSetupRequest / NG-Setup response).

## Evidência primária

- `evidencias_gnb_real/nasp_validation_06/` (relatório, `logs/gnb.log`, `analysis/amf.txt`, nota de execução com `timeout` + Podman).
