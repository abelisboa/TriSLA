# Core 5G (free5GC)

## Componentes observados no namespace `ns-1274485`

- AMF, SMF, UPF, NRF, NSSF, PCF, AUSF, UDM, UDR, WebUI, MongoDB, entre outros (ver lista completa em `CORE_PODS.txt`).

## Status (snapshot na geração desta documentação)

```
NAME                                        READY   STATUS      RESTARTS      AGE
amf-free5gc-amf-amf-0                       1/1     Running     0             122m
ausf-free5gc-ausf-ausf-fdfbdd45d-lphqv      1/1     Running     0             4h43m
nrf-free5gc-nrf-nrf-79874bb77d-fjhkq        1/1     Running     0             122m
nssf-free5gc-nssf-nssf-584d7588dd-kr2vw     1/1     Running     0             4h43m
pcf-free5gc-pcf-pcf-758685ff58-mv7xv        1/1     Running     0             4h43m
smf-free5gc-smf-smf-0                       1/1     Running     0             122m
udm-free5gc-udm-udm-db6cbb654-4xqzx         1/1     Running     0             4h44m
udr-free5gc-udr-udr-857b878cb8-f2d2w        1/1     Running     0             4h44m
upf-free5gc-upf-upf-0                       1/1     Running     0             18d
webui-free5gc-webui-webui-9f58548bc-fgcst   1/1     Running     2 (19d ago)   28d
mongodb-0                                   1/1     Running     2 (19d ago)   28d
...
```

## Função (escopo NASP / N2)

Gestão de mobilidade e sessão no plano de controlo; interface N2 (NGAP/SCTP) entre AMF e gNB.
