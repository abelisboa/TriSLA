#!/bin/bash
ssh -t porvir5g@ppgca.unisinos.br "
    ssh -t node006 '
        kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80 \
        > /dev/null 2>&1 &
        kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 \
        > /dev/null 2>&1 &
        kubectl -n monitoring port-forward svc/tempo 3100:3100 \
        > /dev/null 2>&1 &
        bash
    '
"
