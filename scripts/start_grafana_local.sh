#!/bin/bash

# 1. Conectar ao servidor ppgca
ssh -t porvir5g@ppgca.unisinos.br "
    # 2. Após logar, conectar ao node006
    ssh -t node006 '
        # 3. Fazer port-forward do Grafana para a máquina local
        kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
    '
"
