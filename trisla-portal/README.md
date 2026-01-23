# TriSLA Observability Portal

Complete observability portal for TriSLA, providing comprehensive monitoring and management capabilities.

## Overview

The TriSLA Observability Portal provides a unified interface for:
- Metrics, traces, and logs visualization
- SLA contract management (creation, status, violations, renegotiations)
- Natural Language Processing (NLP) + NEST templates for SLA creation
- Batch SLA requests
- Explainable AI (XAI) module
- Integration with Prometheus, Loki, Tempo, and OTEL Collector

## Project Structure



## Components

### Frontend
- **Framework**: Next.js 15
- **Styling**: Tailwind CSS + Shadcn/UI
- **Features**: Real-time dashboards, SLA management, XAI visualization

### Backend
- **Framework**: FastAPI (Python 3.11)
- **APIs**: RESTful endpoints for observability data
- **Integration**: Prometheus, Loki, Tempo, OpenTelemetry

## Deployment

See [Deployment Guide](../docs/DEPLOYMENT.md) for detailed instructions.

## Documentation

- [Architecture](../docs/ARCHITECTURE.md)
- [Installation](../docs/INSTALLATION.md)
- [Reproducibility](../docs/REPRODUCIBILITY.md)

## Version

This portal is part of TriSLA v3.9.3 (frozen scientific version).
