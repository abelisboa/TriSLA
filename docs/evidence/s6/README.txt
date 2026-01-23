Grafana screenshots should be captured manually via:
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
Then access http://localhost:3000 and capture:
- TriSLA Overview dashboard
- SLO / Latency dashboard
- SLA-Agent Actions dashboard
