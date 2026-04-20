# Decision Engine (TriSLA)

The Decision Engine performs SLA admission control by combining real-time infrastructure signals, ML-NSMF outputs, and policy rules.

## Quick Links
- [Complete Guide](DECISION_ENGINE_COMPLETE_GUIDE.md)
- [Architecture Overview](../../ARCHITECTURE.md)
- [Deployment Guide](../../DEPLOYMENT.md)

## Purpose
The Decision Engine evaluates incoming SLA requests and produces deterministic decision outcomes (ACCEPT / REJECT / RENEGOTIATE) based on:
- Real-time infrastructure metrics (CPU, memory, disk, network)
- ML-NSMF risk predictions and confidence scores
- Policy rules and viability thresholds

## What It Does NOT Do
- Does not process semantic intent (delegated to SEM-CSMF)
- Does not perform ML predictions (delegated to ML-NSMF)
- Does not manage SLA lifecycle (delegated to SLA-Agent)
- Does not register on-chain (delegated to BC-NSSMF)

## Public Endpoints
-  — Submit SLA request for decision
-  — Decision by intent ID
-  — Health check
-  — Prometheus metrics
