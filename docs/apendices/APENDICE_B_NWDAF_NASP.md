# 📘 Apêndice B — Mapeamento NWDAF ↔ NASP

Descreve a equivalência semântica entre a função NWDAF (3GPP) e o ambiente NASP, 
mantendo compatibilidade para alimentar o ML-NSMF e o Decision Engine.

Endpoints principais:

- `/analytics/nsi-load`
- `/analytics/sla-risk`
- `/analytics/qos-sustain`

Eventos:

- `kafka://mobility.agg`
- `kafka://anomaly.event`

