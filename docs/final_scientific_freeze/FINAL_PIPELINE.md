# Final Pipeline (Frozen)

1. SEM-CSMF: intent interpretation + SQLite persistence  
2. ML-NSMF: risk inference (when enabled)  
3. Decision Engine: preventive admission (score_mode, gates, feasibility, pressure)  
4. Portal: NASP instantiate **after** ACCEPT  
5. NASP: CRD persistence + reconciler (60s default)  
6. BC-NSSMF: immutable submit-time governance  
7. SLA-Agent: on-demand HTTP only (no continuous Kafka loop under frozen digest)

**Non-causal:** orchestration/reconciliation → DE feedback (ORCH freeze).
