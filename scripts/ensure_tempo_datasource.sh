#!/bin/bash
set -e

NAMESPACE="monitoring"

cat <<EOF | kubectl apply -n $NAMESPACE -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: trisla-tempo-datasource
  labels:
    grafana_datasource: "1"
data:
  tempo-datasource.yaml: |
    apiVersion: 1
    datasources:
      - name: Tempo
        type: tempo
        access: proxy
        url: http://trisla-tempo.trisla.svc.cluster.local:3200
        isDefault: false
        editable: true
EOF

echo "Datasource Tempo garantido."
