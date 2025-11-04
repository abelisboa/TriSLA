# Túnel SSH para Prometheus
Write-Host " Iniciando túnel SSH..." -ForegroundColor Cyan
ssh -L 9090:nasp-prometheus.monitoring.svc.cluster.local:9090 `
    -J porvir5g@ppgca.unisinos.br porvir5g@node006 -N
