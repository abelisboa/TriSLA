# SLA-Agent Layer

The SLA-Agent implements lifecycle-level actions and monitoring hooks after an SLA request is processed.

## Quick Links
- [Complete Guide](SLA_AGENT_COMPLETE_GUIDE.md)
- [Architecture Overview](../../ARCHITECTURE.md)
- [Deployment Guide](../../DEPLOYMENT.md)

## Purpose
The SLA-Agent consumes decision outputs and orchestrates subsequent control-plane actions required by the platform.

## What It Does NOT Do
- Does not make admission decisions (delegated to Decision Engine)
- Does not process semantic intent (delegated to SEM-CSMF)
- Does not perform ML predictions (delegated to ML-NSMF)
